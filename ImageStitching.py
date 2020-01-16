import cv2
import numpy as np

class ImageStitcher():
    def __init__(self):
        self.stitcher = cv2.Stitcher_create()
    def stitch(self, image1, image2):
        (status, stitched) = self.stitcher.stitch([image1, image2])
        # if the status is '0', then OpenCV successfully performed image
        # stitching
        if status == 0:
            # write the output stitched image to disk
            return stitched
        # otherwise the stitching failed, likely due to not enough keypoints)
        # being detected
        else:
            print("[INFO] image stitching failed ({})".format(status))
        