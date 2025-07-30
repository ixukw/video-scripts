# This script is for solitaire
# End goal: Given n checkpoints and m video files, compile into one video synced at each checkpoint.

import numpy as np
import cv2 as cv
import argparse
from tqdm import tqdm
from matplotlib import pyplot as plt
import os

THRESHOLD = 0.55
VIDEO_PREFIX = '/Users/inanxu/Movies/solitaires/'
VIDEO_FILES = [
    '52card_solitaire.mkv',
    'circuit_solitaire.mkv',
    'double_sided_solitaire.mkv',
    'lock_and_key_solitaire.mkv',
    'murder_mystery.mkv',
    'planet_solitaire.mkv',
    'river_solitaire.mkv',
    'tabula_rasa_solitaire.mkv',
    'time_travel_solitaire.mkv'
]
IMAGE_PREFIX = 'data/images/'
IMAGE_FILES = [
    'winstreak.png',
    'victory.png'
]
CHECKPOINT_PREFIX = 'data/checkpoints/'

# y1,x1,y2,x2
IMAGE_POS = [
    [0,350, 1400,-1],
    [450,600,600,1000]
]
def read_checkpoint_images(files):
    images = []
    for file in files:
        img = cv.imread(IMAGE_PREFIX + file, cv.IMREAD_GRAYSCALE)
        assert img is not None, 'Unable to read image ' + file
        images.append(img)
    return images

def check_image_in_frame(frame, image, pos=None):
    if pos:
        if pos[3] == -1:
            pos[3] = frame.shape[1]
        frame = frame[pos[0]:pos[1],pos[2]:pos[3]]
    res = cv.matchTemplate(frame, image, cv.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)

    plt.subplot(121),plt.imshow(res,cmap = 'gray')
    plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
    w,h = image.shape[::-1]
    r = (min_loc[0]+w, min_loc[1]+h)
    # print(min_loc, r,w,h,frame.shape)
    cv.rectangle(frame, min_loc, r, 255, 2)
    plt.subplot(122),plt.imshow(frame,cmap = 'gray')
    plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
    plt.plot(min_loc[0], min_loc[1],'bo')
    print(res[min_loc[1], min_loc[0]])
    plt.show()
    
    return res[min_loc[1], min_loc[0]] < THRESHOLD

def read_video(video, images, initial_frame=0):
    # a list where each index is a list of tuples of (frame, pos) for the corresponding checkpoint image index
    # [ [(frame, pos), ...,], ...]
    # but actually its just [(frame, image_index), ...] for some reason
    markers = []
    image_index = 1
    last_occurred_frame = -1

    cap = cv.VideoCapture(VIDEO_PREFIX + video)
    total_frames = cap.get(cv.CAP_PROP_FRAME_COUNT)
    print('%s: %s frames, %sfps, hw_accel?: %s' % (video, total_frames, cap.get(cv.CAP_PROP_FPS), cap.get(cv.CAP_PROP_HW_ACCELERATION)))

    # begin video file read at this frame count
    cap.set(cv.CAP_PROP_POS_FRAMES, initial_frame)
    with tqdm(total=total_frames-initial_frame) as pbar:
        while cap.isOpened():
            ret, _frame = cap.read()
            frame_number = cap.get(cv.CAP_PROP_POS_FRAMES)
            pbar.update(frame_number - pbar.n)
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...", cap.get(cv.CAP_PROP_POS_FRAMES))
                break
            
            if last_occurred_frame != -1 and frame_number < total_frames/2:
                cap.set(cv.CAP_PROP_POS_FRAMES, int(total_frames-400))
                print('fast forwarded')
                continue
            frame = cv.cvtColor(_frame, cv.COLOR_BGR2GRAY) # apparently cv.cvtColor is high CPU util

            
            if check_image_in_frame(frame, images[image_index],IMAGE_POS[image_index]):
                # if last_occurred_frame == -1:
                print('image %s (%s) at frame %s' % (image_index, IMAGE_FILES[image_index], frame_number))
                markers.append((frame_number, image_index))
                last_occurred_frame = frame_number

            # if the current image hasn't been found, skip check for the next
            if last_occurred_frame == -1:
                continue

            next_image_index = image_index+1
            if next_image_index < len(images):
                if check_image_in_frame(frame, images[next_image_index],IMAGE_POS[next_image_index]):
                    markers.append((frame_number+1, next_image_index)) # zero duration crashes ffmpeg
                    last_occurred_frame = frame_number+1
                    image_index+=1
                    print('next image %s (%s) at frame %s' % (next_image_index, IMAGE_FILES[next_image_index], frame_number))
        cap.release()
        cv.destroyAllWindows()
    return markers

def write_output(video, markers):
    with open(CHECKPOINT_PREFIX + video + '.txt', 'w') as file:
        for x in markers:
            file.write(",".join([str(i) for i in x]) + '\n')

def main():
    parser = argparse.ArgumentParser(
        prog='mosaic'
    )
    parser.add_argument('-v', '--verbose', action='store_true')

    args = parser.parse_args()

    images = read_checkpoint_images(IMAGE_FILES)
    for video in VIDEO_FILES:
        if not os.path.exists(CHECKPOINT_PREFIX + video + '.txt'):
            markers = read_video(video, images, 53958)
            write_output(video, markers)
        else:
            print('skipping %s since output exists' % (video))

if __name__ == "__main__":
    main()