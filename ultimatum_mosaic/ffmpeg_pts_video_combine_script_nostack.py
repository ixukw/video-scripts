# this currently doesn't work
# need to only invoke one run() call but ffmpeg-python is stupid

import ffmpeg
import os.path

VIDEO_FILES = ['gilded_ulti_1to11.mkv', 'gilded_ulti_12to20.mkv', 'gilded_ulti_21to24.mkv', 'gilded_ulti_25to.mkv','gilded_ulti_to50.mkv']
CHECKPOINTS_FILES = ['output1to11.txt','output12to20.txt','output21to24.txt','output25to.txt','outputto50.txt']

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
                checkpoints[segment_name] = {}
            if VIDEO_FILES[j] not in checkpoints[segment_name]:
                checkpoints[segment_name][VIDEO_FILES[j]] = []
            # {file: [frame_start, frame_end, speed]}
            checkpoints[segment_name][VIDEO_FILES[j]].append([lines[i][0], lines[i+1][0] if lines[i][1] != '10' else str(float(lines[i][0])+60), 1]) 

# calculate framerate modifications
#print(checkpoints)

for pt, v in checkpoints.items():
    durations = []
    for file, g in v.items():
        for [a,b,_] in g:
            durations.append(float(b)-float(a))
    #print(durations)
    #durations = [float(b) - float(a) for f, g in v.items() for [a,b,_] in g]
    avg = sum(durations) / len(durations)
    for i, (file, g) in enumerate(v.items()):
        for j, k in enumerate(g):
            checkpoints[pt][file][j][2] = avg/(float(k[1]) - float(k[0]))
print(checkpoints)

# ffmpeg

IN_FILES = {file: i for i in VIDEO_FILES}
#IN_FILES = {file: ffmpeg.input(file) if i%2==0 else ffmpeg.input(file, hwaccel='cuda') for i, file in enumerate(VIDEO_FILES)}

#queue = []
for k, v in checkpoints.items():
    #videos = []
    processes = []
    count = 0
    for i, (file, data) in enumerate(v.items()):
        process = ffmpeg.input(file)#.filter_multi_output('split', ''.join(['[out'+str(i)+']' for i in range(len(data)-1)]))
        videos = []
        need_execute = False
        for j, (start, end, speed) in enumerate(data):
            name = 'tmp/' + k + '_' + file[:-4] + '_' + str(count) + '.mkv'
            print('starting video',name)

            if not os.path.isfile(name):
                #input = ffmpeg.input(file)# if len(queue)>0 else ffmpeg.input(file, hwaccel='cuda')
                process.trim(start_frame=start, end_frame=end).setpts('(PTS-STARTPTS)')
                need_execute = True
                #.filter('scale',width=585,height=-1)
                #.filter('minterpolate',mi_mode='mci',mc_mode='aobmc',vsbmc=1,fps=60)
                #.output(name, vcodec='h264_nvenc', qp=0)
                #.output(name)
                #.global_args('-hwaccel','cuda')
                #.run_async()
            #)
            #queue.append(process)
            #process.run_async()
                videos.append(name)
            count += 1
        #videos.append((name, speed))
        if need_execute:
            print('attempting',process)
            print(videos)
            ffmpeg.output(process, videos, vcodec='h264_nvenc', qp=0).run()
    #for p in queue:
    #    print('waiting for',p)
    #    p.wait()
    #queue = []
    #for x in videos:
    #    x.wait()
    #    print('done video', x)
    #print('created',len(videos),'clips for segment',k)
    
    continue
    name = 'tmp/stack_' + k + '.mkv'
    if not os.path.isfile(name):
        (
            ffmpeg
            #.filter(videos,'xstack', fill='black', inputs=len(v), layout='0_0|0_h0|0_h0+h1|0_h0+h1+h2|0_h0+h1+h2+h3|0_h0+h1+h2+h3+h4|0_h0+h1+h2+h3+h4+h5|w0_0|w0_h0|w0_h0+h1|w0_h0+h1+h2|w0_h0+h1+h2+h3|w0_h0+h1+h2+h3+h4|w0_h0+h1+h2+h3+h4+h5|w0+w7_0|w0+w7_h0|w0+w7_h0+h1|w0+w7_h0+h1+h2|w0+w7_h0+h1+h2+h3|w0+w7_h0+h1+h2+h3+h4|w0+w7_h0+h1+h2+h3+h4+h5|w0+w7+w14_0|w0+w7+w14_h0|w0+w7+w14_h0+h1|w0+w7+w14_h0+h1+h2|w0+w7+w14_h0+h1+h2+h3|w0+w7+w14_h0+h1+h2+h3+h4|w0+w7+w14_h0+h1+h2+h3+h4+h5|w0+w7+w14+w21_0|w0+w7+w14+w21_h0|w0+w7+w14+w21_h0+h1|w0+w7+w14+w21_h0+h1+h2|w0+w7+w14+w21_h0+h1+h2+h3|w0+w7+w14+w21_h0+h1+h2+h3+h4|w0+w7+w14+w21_h0+h1+h2+h3+h4+h5|w0+w7+w14+w21+w28_0|w0+w7+w14+w21+w28_h0|w0+w7+w14+w21+w28_h0+h1|w0+w7+w14+w21+w28_h0+h1+h2|w0+w7+w14+w21+w28_h0+h1+h2+h3|w0+w7+w14+w21+w28_h0+h1+h2+h3+h4|w0+w7+w14+w21+w28_h0+h1+h2+h3+h4+h5|w0+w7+w14+w21+w28+w35_0|w0+w7+w14+w21+w28+w35_h0|w0+w7+w14+w21+w28+w35_h0+h1|w0+w7+w14+w21+w28+w35_h0+h1+h2|w0+w7+w14+w21+w28+w35_h0+h1+h2+h3|w0+w7+w14+w21+w28+w35_h0+h1+h2+h3+h4|w0+w7+w14+w21+w28+w35_h0+h1+h2+h3+h4+h5')
            .filter([ffmpeg.input(v, hwaccel='cuda').filter('scale',width=585,height=-1).setpts('PTS*'+str(speed)) for (v, speed) in videos], 'xstack', fill='black', inputs=len(v), layout='0_0|0_h0|0_h0+h1|0_h0+h1+h2|0_h0+h1+h2+h3|0_h0+h1+h2+h3+h4|0_h0+h1+h2+h3+h4+h5|w0_0|w0_h0|w0_h0+h1|w0_h0+h1+h2|w0_h0+h1+h2+h3|w0_h0+h1+h2+h3+h4|w0_h0+h1+h2+h3+h4+h5|w0+w7_0|w0+w7_h0|w0+w7_h0+h1|w0+w7_h0+h1+h2|w0+w7_h0+h1+h2+h3|w0+w7_h0+h1+h2+h3+h4|w0+w7_h0+h1+h2+h3+h4+h5|w0+w7+w14_0|w0+w7+w14_h0|w0+w7+w14_h0+h1|w0+w7+w14_h0+h1+h2|w0+w7+w14_h0+h1+h2+h3|w0+w7+w14_h0+h1+h2+h3+h4|w0+w7+w14_h0+h1+h2+h3+h4+h5|w0+w7+w14+w21_0|w0+w7+w14+w21_h0|w0+w7+w14+w21_h0+h1|w0+w7+w14+w21_h0+h1+h2|w0+w7+w14+w21_h0+h1+h2+h3|w0+w7+w14+w21_h0+h1+h2+h3+h4|w0+w7+w14+w21_h0+h1+h2+h3+h4+h5|w0+w7+w14+w21+w28_0|w0+w7+w14+w21+w28_h0|w0+w7+w14+w21+w28_h0+h1|w0+w7+w14+w21+w28_h0+h1+h2|w0+w7+w14+w21+w28_h0+h1+h2+h3|w0+w7+w14+w21+w28_h0+h1+h2+h3+h4|w0+w7+w14+w21+w28_h0+h1+h2+h3+h4+h5|w0+w7+w14+w21+w28+w35_0|w0+w7+w14+w21+w28+w35_h0|w0+w7+w14+w21+w28+w35_h0+h1|w0+w7+w14+w21+w28+w35_h0+h1+h2|w0+w7+w14+w21+w28+w35_h0+h1+h2+h3|w0+w7+w14+w21+w28+w35_h0+h1+h2+h3+h4|w0+w7+w14+w21+w28+w35_h0+h1+h2+h3+h4+h5')
            .output(name, vcodec='h264_nvenc', qp=0)
            .global_args('-hwaccel','cuda')
            .run()
        )
    print('created file', name)
exit()
inputs = ['tmp/stack'+str(i)+j+'.mkv' for i in range(10) for j in range(2)]
print(inputs)

(
    ffmpeg
    .filter([ffmpeg.input(x, hwaccel='nvdec') for x in inputs], 'concat', n=len(inputs))
    .output('tmp/combined.mkv')
    .run()
)


#def genLayout(n):
#    out=''
#    for i in range(n):
#        for j in range(n):
#            ''.join(['w'+x for x in range(j)])
exit()