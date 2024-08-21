# 

import ffmpeg
import os.path
from datetime import timedelta
VIDEO_FILES = ['gilded_ulti_1to11.mkv', 'gilded_ulti_12to20.mkv', 'gilded_ulti_21to24.mkv', 'gilded_ulti_25to.mkv','gilded_ulti_to50.mkv']
CHECKPOINTS_FILES = ['output1to11.txt','output12to20.txt','output21to24.txt','output25to.txt','outputto50.txt']

def generateLayout(row, col):
    layout = ''
    for c in range(col):
        for r in range(row):
            row_part = ''.join([f'h{i}+' for i in range(r)])[:-1] if r > 0 else '0'
            col_part = ''.join([f'w{i*col}+' for i in range(c)])[:-1] if c > 0 else '0'
            layout += f'|{col_part}_{row_part}'
    print(layout[1:])
    return layout[1:]

# read checkpoints
checkpoints = {}
for j, file in enumerate(CHECKPOINTS_FILES):
    with open(file, 'r') as f:
        lines = [x.split(' ') for x in f.read().splitlines()]
        for i in range(len(lines)-1):
            segment_name = lines[i][1] + lines[i][2]
            if lines[i][1] != '10':
                segment_name += '_' + lines[i+1][1] + lines[i+1][2]
            if segment_name not in checkpoints:
                checkpoints[segment_name] = []
            checkpoints[segment_name].append([lines[i][0], lines[i+1][0] if lines[i][1] != '10' else str(float(lines[i][0])+300), 1, VIDEO_FILES[j]]) # frame_start, frame_end, speed, origin_file
checkpoints.pop('10last')

# calculate framerate modifications
for k, v in checkpoints.items():
    durations = [float(b) - float(a) for (a, b, _, _) in v]
    avg = sum(durations) / len(durations)
    for i, x in enumerate(v):
        x[2] = avg/durations[i]
        
# ffmpeg

IN_FILES = {file: i for i in VIDEO_FILES}

stack_videos = []
queue = []
for k, v in checkpoints.items():
    videos = []
    for i, (start, end, speed, file) in enumerate(v):
        name = 'tmp/' + k + '_' + file[:-4] + '_' + str(i) + '.mkv'

        if not os.path.isfile(name):
            print('starting video',name)
            if len(queue) >= 2:
                for p in queue:
                    print('waiting',p)
                    p.wait()
                queue = []
            time = str(timedelta(seconds=(float(start) / 60)))
            #print('COMPARISON', start, time)
            input = ffmpeg.input(file, ss=time)
            process = (
                input
                .trim(start_frame=0, end_frame=str(float(end)-float(start)))
                .setpts('(PTS-STARTPTS)')
                #.filter('scale',width=585,height=-1)
                #.filter('minterpolate',mi_mode='mci',mc_mode='aobmc',vsbmc=1,fps=60)
                .output(name, vcodec='h264_nvenc', qp=0)
                #.output(name)
                #.global_args('-hwaccel','cuda')
                .run_async()
            )
            queue.append(process)
        videos.append((name, speed))
        
    for p in queue:
        print('waiting for',p)
        p.wait()
    queue = []
    #print('created',len(videos),'clips for segment',k)
    
    videos.pop(47)

    name = 'tmp/stack_' + k + '.mkv'
    if not os.path.isfile(name):
        (
            ffmpeg
            .filter([ffmpeg.input(v, hwaccel='cuda').crop(x=410, y=100, width=1100,height=855).filter('scale',width=480,height=360).setpts('PTS*'+str(speed)) for (v, speed) in videos], 'xstack', fill='black', inputs=48, grid='8x6')#layout=generateLayout(6,8))
            .output(name, vcodec='h264_nvenc', qp=0)
            #.global_args('-hwaccel','cuda')
            #.global_args('-loglevel','verbose')
            #.run(capture_stderr=True, capture_stdout=True)
            .run()
        ) 
    print('created file', name)
    stack_videos.append(name)

(
    ffmpeg
    .filter([ffmpeg.input(x) for x in stack_videos], 'concat', n=len(stack_videos))
    .filter('scale',w=3840,h=2160)
    .output('tmp/xstack_combined.mkv', pix_fmt='yuv420p', qp=0, vcodec='h264_nvenc')
    .run()
)
exit()