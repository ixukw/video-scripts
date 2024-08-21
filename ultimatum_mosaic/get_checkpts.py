# This script is for ultimatum
# End goal: Given n checkpoints and m video files, compile into one video synced at each checkpoint.

import numpy as np
import cv2 as cv
#from matplotlib import pyplot as plt

THRESHOLD = 0.8
VIDEO_FILE = 'gilded_ulti_to50.mkv'
#                    0           1       2       3       4       5       6       7       8       9        10
image_file_names = ['begin.png','2.png','3.png','4.png','5.png','6.png','7.png','8.png','9.png','10.png','end.png']
images = []
for file in image_file_names:
    img = cv.imread(file, cv.IMREAD_GRAYSCALE)
    assert img is not None, 'Unable to read image ' + file
    images.append(img)

#w, h = grayimg.shape[::-1] # 105, 41
#frame_count = 0
image_index = 0
last_occurred_frame = -1

# [[(frame, position?),(), ..., ()], ...]
markers = []

cap = cv.VideoCapture(VIDEO_FILE, cv.CAP_FFMPEG, [cv.CAP_PROP_HW_ACCELERATION, cv.VIDEO_ACCELERATION_D3D11])
print(cap.get(cv.CAP_PROP_FRAME_COUNT), cap.get(cv.CAP_PROP_FPS), cap.get(cv.CAP_PROP_HW_ACCELERATION))

cap.set(cv.CAP_PROP_POS_FRAMES, 87800)

while cap.isOpened():
    ret, frame_color = cap.read()
    if not ret: # if frame is read correctly ret is True
        print("Can't receive frame (stream end?). Exiting ...", cap.get(cv.CAP_PROP_POS_FRAMES))
        break
    frame = cv.cvtColor(frame_color, cv.COLOR_BGR2GRAY) # apparently cv.cvtColor is high CPU util
    old_frame = frame
    # check for current index to find last occurrence
    if image_index != 0:
        frame = frame[530:590, 950:1000]
    res = cv.matchTemplate(frame, images[image_index], cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
    if res[max_loc[1], max_loc[0]] > THRESHOLD:
        if last_occurred_frame == -1:
            markers.append((cap.get(cv.CAP_PROP_POS_FRAMES), image_index, 'first')) # first image_index only
        last_occurred_frame = cap.get(cv.CAP_PROP_POS_FRAMES)
        print('index', image_index, 'on frame', last_occurred_frame)

    # if the current image hasn't been found, skip check for the next
    if last_occurred_frame == -1:
        continue

    # check next image for first occurrence
    if image_index == 9:
        frame = old_frame
    res = cv.matchTemplate(frame, images[image_index+1], cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)

    if res[max_loc[1], max_loc[0]] > THRESHOLD:
        frame_count = cap.get(cv.CAP_PROP_POS_FRAMES)
        print('first occurrence for index', image_index+1, 'at frame', frame_count)
        print('last occurrence for index', image_index, 'at frame', last_occurred_frame)
        #top_left = min_loc
        #w, h = images[image_index].shape[::-1]
        #bottom_right = (top_left[0] + w, top_left[1] + h)
        #cv.rectangle(frame, top_left, bottom_right, 255, 2)

        # zero duration crashes ffmpeg
        if (last_occurred_frame == frame_count):
            frame_count+=1

        markers.append((last_occurred_frame, image_index, 'last'))
        markers.append((frame_count, image_index+1, 'first'))
        last_occurred_frame = frame_count

        if image_index < len(image_file_names) - 2:
            image_index = image_index+1
        else:
            markers.append((frame_count+1, image_index+1, 'last')) # last image_index only
            image_index = 0
            last_occurred_frame = -1
            exit()
        print('now searching for',image_index)

    
    #cv.imshow('frame', grayvid)
    #if cv.waitKey(1) == ord('q'):
    #    break


with open('output.txt', 'w') as file:
    for x in markers:
        file.write(" ".join([str(i) for i in x]) + '\n')
#for i, [frameNum, res, frame] in enumerate(locs):
#    plt.subplot(len(locs), 2, i*2+1), plt.imshow(res, cmap = 'gray')
#    plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
#    plt.subplot(len(locs), 2, (i+1)*2), plt.imshow(frame, cmap = 'gray')
#    plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
#    plt.suptitle(frameCount)
#plt.show()

cap.release()
cv.destroyAllWindows()