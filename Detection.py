import numpy as np
import cv2
import time

from NetworkManager import NetworkManager
from ImageStitching import ImageStitcher

#gives color range to be detected
def getColorRange():
    #range of color
    #Current Color: Red
    colorLower1 = np.array([0, 120, 70], np.uint8)
    colorUpper1 = np.array([10, 255, 255], np.uint8)
    colorLower2 = np.array([170, 120, 70], np.uint8)
    colorUpper2 = np.array([180, 255, 255], np.uint8)
    return colorLower1, colorUpper1, colorLower2, colorUpper2

#apply filters and mask on frame for contouring
def filterFrame(frame):
    
    #apply blur
    kernel = np.ones((5,5), 'uint8')
    blurred = cv2.GaussianBlur(frame, (11,11), 0)
    blurred = cv2.erode(blurred, kernel, iterations = 5)
    blurred = cv2.dilate(blurred, kernel, iterations = 5)
    
    #apply mask on hsv image
    cLow1, cUp1, cLow2, cUp2 = getColorRange()
    frameHSV = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    colorMask1 = cv2.inRange(frameHSV, cLow1, cUp1)
    colorMask2 = cv2.inRange(frameHSV, cLow2, cUp2)
    colorMask = colorMask1 + colorMask2
    res = cv2.bitwise_and(frame, frame, mask = colorMask)
    
    #grayscale and return
    gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    
    return gray, res

#resize and mirror frames for more natural drum experience
def rescaleFrame(frame):
    frame = cv2.resize(frame, (0,0), fx = 1, fy = 1)
    frame = cv2.flip(frame, +1)
    return frame

#finds contours around the filtered frame
def contourFilteredFrame(frame):
    thresh = cv2.adaptiveThreshold(frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours
    
#draws a circle with a dot for detected objects
def drawContours(contours):
    minRad = 30
    maxRad = 200
    maxContours = 10
    contourList = []
    count = 0
    for contour in contours:
        count += 1
        ((x,y), radius) = cv2.minEnclosingCircle(contour)
        #remove contours that are too small
        if radius < minRad or radius > maxRad:
            continue
        contourList.append((x,y,radius))
        if count > maxContours:
            break
    return contourList


def return_coord(cap, cap2, sock, stitcher):
    _, frame = cap.read()
    _, frame2 = cap2.read()
    
    #frame = rescaleFrame(frame)
    #frame2 = rescaleFrame(frame2)
    filteredFrame, res = filterFrame(frame)
    filteredFrame2, res2 = filterFrame(frame2)
    contours = contourFilteredFrame(filteredFrame)
    contours2 = contourFilteredFrame(filteredFrame2)
    contourList = drawContours(contours)
    contourList2 = drawContours(contours2)
    for x,y,radius in contourList:
        cv2.circle(frame, (int(x), int(y)), int(radius), (0, 0, 255), 2)
        #cv2.circle(frame, (int(x), int(y)), 5, (0, 0, 255), -1)
        #sock.send_coord(str(int(x)) + str(int(y)))
        coord1 = (int(x), int(y))
    for x, y, radius in contourList2:
        cv2.circle(frame2, (int(x), int(y)), int(radius), (0, 0, 255), 2)
        #sock.send_coord(str(int(x)) + str(int(y)))
        coord2 = (int(x), int(y))
    #for error 'a bytes-like object is required, not'str''
    #b1= bytes(str(xPos) + str(yPos), encode='utf-8')
    #sock.sendto(b1,(UDP_IP,UDP_PORT))
    #sock.sendto(str(xPos) + str(yPos), (UDP_IP, UDP_PORT))
    stitched_image = stitcher.stitch(frame,frame2)
    #cv2.imshow("stitchedImage", stitched_image)
    cv2.imshow("1", frame)
    cv2.imshow("2", frame2)
    #cv2.imshow("combin", stitched_image)
    return coord1, coord2
            
                     
def main():
    #set up sockets
    sock = NetworkManager()
    #set up image stitching
    stitcher = ImageStitcher()
    #set up video
    cap = cv2.VideoCapture(0)
    cap2 = cv2.VideoCapture(2)
    #buffer to load video
    time.sleep(2.0)
    #main cv2 video loop
    while(True):
        #read frames
        coord1, coord2 = return_coord(cap, cap2, sock, stitcher)
        #if condition is met, break out of loop
        ch = cv2.waitKey(1)
        if ch & 0xFF == ord('q'):
            break
    cap.release()
    cap2.release()
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    main()