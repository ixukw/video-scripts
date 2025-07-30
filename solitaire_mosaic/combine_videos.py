# 

import ffmpeg
import os.path
from datetime import timedelta
VIDEO_PREFIX = '/Users/inanxu/Movies/solitaires/'
VIDEO_FILES = [
    '52card_solitaire.mkv',
    # 'black.mkv',
    'circuit_solitaire.mkv',
    'double_sided_solitaire.mkv',
    'lock_and_key_solitaire.mkv',
    'murder_mystery.mkv',
    'planet_solitaire.mkv',
    'river_solitaire.mkv',
    'tabula_rasa_solitaire.mkv',
    # 'black.mkv'
    'time_travel_solitaire.mkv'
]
CHECKPOINT_PREFIX = 'data/checkpoints/'
CHECKPOINTS_FILES = [x + '.txt' for x in VIDEO_FILES]

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
checkpoints = {'0':[],'1':[],'2':[]}
for j, file in enumerate(CHECKPOINTS_FILES):
    with open(CHECKPOINT_PREFIX + file, 'r') as f:
        lines = [x.split(' ') for x in f.read().splitlines()]
        checkpoints['0'].append([
            0,
            lines[0][0],
            1,
            VIDEO_FILES[j]
        ])
        checkpoints['1'].append([
            lines[0][0],
            lines[1][0],
            1,
            VIDEO_FILES[j]
        ])
        checkpoints['2'].append([
            lines[1][0],
            str(float(lines[1][0])+180),
            1,
            VIDEO_FILES[j]
        ])
        # frame_start, frame_end, speed, origin_file

# calculate framerate modifications
for k, v in checkpoints.items():
    durations = [float(b) - float(a) for (a, b, _, _) in v]
    avg = sum(durations) / len(durations)
    for i, x in enumerate(v):
        x[2] = avg/durations[i]
print(checkpoints)
# exit()
# ffmpeg
IN_FILES = {file: VIDEO_PREFIX + i for i in VIDEO_FILES}
stack_videos = []
queue = []

if not os.path.exists('tmp'):
    os.mkdir('tmp')
for k, v in checkpoints.items():
    videos = []
    for i, (start, end, speed, file) in enumerate(v):
        name = 'tmp/' + k + '_' + file[:-4] + '_' + str(i) + '.mkv'

        if not os.path.isfile(name):
            print('starting video',name)
            if len(queue) >= 1:
                for p in queue:
                    print('waiting',p)
                    p.wait()
                queue = []
            time = str(timedelta(seconds=(float(start) / 60)))
            #print('COMPARISON', start, time)
            input = ffmpeg.input(VIDEO_PREFIX + file, ss=time)
            process = (
                input
                .trim(start_frame=0, end_frame=str(float(end)-float(start)))
                .setpts('(PTS-STARTPTS)')
                # .filter('scale',width=640,height=-1)
                #.filter('minterpolate',mi_mode='mci',mc_mode='aobmc',vsbmc=1,fps=60)
                .output(name, qp=0)
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
    
    # videos.pop(47)

    name = 'tmp/stack_' + k + '.mkv'
    if not os.path.isfile(name):
        (
            ffmpeg
            .filter([ffmpeg.input(v).crop(x=0, y=0, width=1920-302,height=1080)
                     .filter('scale',width=540,height=-1)
                     .setpts('PTS*'+str(speed)) for (v, speed) in videos], 'xstack', fill='black', inputs=48, grid='3x3')#layout=generateLayout(6,8))
            .output(name, qp=0)
            # .global_args('-hwaccel','auto')
            #.global_args('-loglevel','verbose')
            #.run(capture_stderr=True, capture_stdout=True)
            .run()
        ) 
    print('created file', name)
    stack_videos.append(name)

(
    ffmpeg
    .filter([ffmpeg.input(x) for x in stack_videos], 'concat', n=len(stack_videos))
    # .filter('scale',w=1920,h=-1)
    .output('tmp/stack_n.mkv', qp=0, pix_fmt='yuv420p')
    .run()
)
# you need to use yuv420p for the video to work in most editors
exit()