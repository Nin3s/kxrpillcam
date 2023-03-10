''' 
This is the main program responsible for controlling the Payload Integrated Launch Log (P.I.L.L.)
The PILL is the experimental payload the NASA Student Launch Competition

The following code is proprietary to Knights Experimental Rocketry
'''

import cv2
import numpy as np
from datetime import datetime
import logging
import threading
from PIL import Image

#import adafruit_bno055
    #https://github.com/adafruit/Adafruit_CircuitPython_BNO055
#import adafruit_ds3231
    #https://docs.circuitpython.org/projects/ds3231/en/latest/
#import time
#import board
#from rtlsdr import RtlSdr
    #https://pypi.org/project/pyrtlsdr/
#import RPi.GPIO as GPIO
    #https://www.instructables.com/Servo-Motor-Control-With-Raspberry-Pi/





def runCamera():

# Various effects, global variables

    useGrayScale = False
    flipped = False
    useOverlay = False
    gifOverlay = False

# This is just used for naming the files
# In the future, we can use the timestamp as our file names
#img_counter = 0

    def applyFilters(frame):
        if useGrayScale:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if flipped:
            frame = cv2.flip(frame, -1)

        return frame

    def doGifOverlay(frame, now):
        gif = cv2.VideoCapture('bad_news.gif')

        frames = []
        while True:
            ret, gif_frame = gif.read()
            if not ret:
                break

            gif_frame = cv2.resize(gif_frame, (frame.shape[1], frame.shape[0]))
            overlay = cv2.addWeighted(gif_frame, 0.3, frame, 0.5, 0)

            # Check if other effects are on
            overlay = applyFilters(overlay)

            cv2.putText(overlay, now, (20, 40), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2, cv2.LINE_AA)
            frames.append(overlay)

        frames_pil = [Image.fromarray(f) for f in frames]
        frames_pil[0].save("opencv_gif.gif", save_all=True, append_images=frames_pil[1:], loop=0)

    def takePhoto(frame):
        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if gifOverlay:
            doGifOverlay(frame, curr_time)
        else:
            frame = applyFilters(frame)

            if useOverlay:
                overlay_img = cv2.imread('bad_news_img.png', cv2.COLOR_BGR2GRAY)

                overlay_img = cv2.resize(overlay_img, (640, 480))

                if useGrayScale: # convert to 2 channels, program will fail without it, see Color Channels in the README for more
                    gray_img = cv2.cvtColor(overlay_img, cv2.COLOR_BGR2GRAY)
                    frame = cv2.addWeighted(frame, 0.4, gray_img, 0.7, 0)
                else:
                    frame = cv2.addWeighted(frame, 0.7, overlay_img, 0.4, 0)

            cv2.putText(frame, curr_time, (20, 40), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.imshow("opencv_img.png", frame)
            cv2.imwrite("opencv_img.png", frame)

    camera = cv2.VideoCapture(0)

    while True:
        (grabbed, frame) = camera.read()
        frame = cv2.flip(frame, 1) # Mirrors camera output, feel free to remove if you feel like we should have the unmirrored version
        if not grabbed:
            break

        # Display output
        cv2.imshow("Camera", frame)

        k = cv2.waitKey(1)
        #img_name = "opencv_frame_{}.png".format(img_counter)
        
        if k == ord("q"):
            break
        elif k == ord(" "):
            new_frame = frame
            takePhoto(new_frame)
            #img_counter += 1
        # Toggles effects, print statements are for logging it in the console
        elif k == ord("1"):
            if not useGrayScale:
                useGrayScale = True
                print("Grayscale is on")
            else:
                useGrayScale = False
                print("Grayscale is off")
        elif k == ord("2"):
            if not flipped:
                flipped = True
                print("Output will be flipped 180 degrees")
            else:
                flipped = False
                print("Output will have original orientation")
        elif k == ord("3"): # gif overlay
            if not useOverlay:
                useOverlay = True
                gifOverlay = False
                print("Overlay active")
                print("Gif overlay inactive")
            else:
                useOverlay = False
                print("Overlay inactive")
        elif k == ord("4"): # static overlay (not needed, but here just in case we can't use gif overlay)
            if not gifOverlay:
                gifOverlay = True
                useOverlay = False
                print("Gif overlay active")
                print("Static overlay inactive")
            else:
                gifOverlay = False
                print("Gif overlay inactive")
        elif k == ord("5"):
            print("Clearing all active effects...\n")
            useGrayScale = False
            flipped = False
            useOverlay = False
            gifOverlay = False
            print("Cleared.")

#t1 = threading.Thread(target=runCamera, args=())
#t1.start()

runCamera()