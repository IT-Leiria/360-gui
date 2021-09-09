import cv2
import numpy as np
from PyQt5.QtGui import QImage, QPainter  
from qimage2ndarray import array2qimage

from timeit import default_timer as timer

def qImage2CvMat(image):
        start = timer()
        image = image.convertToFormat(4)
        end = timer()
        print("Converted format: {}".format(end - start))
        width = image.width()
        height = image.height()
        start = timer()
        ptr = image.bits()
        end = timer()
        print("Copied bits: {}".format(end - start))
        ptr.setsize(image.byteCount())
        start = timer()
        arr = np.array(ptr).reshape(height, width, 4)
        end = timer()
        print("Reshaped: {}".format(end - start))
        return cv2.cvtColor(arr, cv2.COLOR_BGRA2GRAY)

'''
    https://learnopencv.com/how-to-convert-your-opencv-c-code-into-a-python-module/
    https://github.com/spmallick/learnopencv/tree/master/pymodule

    https://www.reddit.com/r/opencv/comments/bs8iu3/question_developing_own_contrib_module_with/
    https://docs.opencv.org/master/d2/de6/tutorial_py_setup_in_ubuntu.html
    https://docs.opencv.org/3.4.1/da/d49/tutorial_py_bindings_basics.html
'''
class Tracker(object):
    def __init__(self, model):
        self.model = model
 
    def template_match(self, img):
        # Apply template Matching
        if self.model.tracked_image and self.model.tracking_activated.value:

            w = self.model.tracked_image.width()
            h = self.model.tracked_image.height()

            start = timer()
            converted_img = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)
            #converted_img = qImage2CvMat(img)
            end = timer()

            print("Converted both in: {}".format(end - start))
            gray = qImage2CvMat(self.model.tracked_image)


            try:
                start = timer()
                scale_percent = 5 # percent of original size
                width = int(converted_img.shape[1] * scale_percent / 100)
                height = int(converted_img.shape[0] * scale_percent / 100)
                dim = (width, height)
                resized_img = cv2.resize(converted_img, dim, interpolation = cv2.INTER_AREA)

                width = int(gray.shape[1] * scale_percent / 100)
                height = int(gray.shape[0] * scale_percent / 100)
                dim = (width, height)
                resized_tracked = cv2.resize(gray, dim, interpolation = cv2.INTER_AREA)

                res = cv2.matchTemplate(resized_img, resized_tracked, cv2.TM_CCOEFF_NORMED)
                end = timer()
                print("Matched in: {}".format(end - start))
            except:
                raise

            start = timer()
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            end = timer()
            print("MinMaxLoc in: {}".format(end - start))
            if max_loc is not None:
                #cv2.rectangle(img, max_loc, bottom_right, (0,0,255), 2)
                print("Max_val: {}".format(max_val))
                return int(max_loc[0] / (scale_percent / 100)), int(max_loc[1] / (scale_percent / 100)), w, h
            else:
                return -1, -1, -1, -1
        else:
            return -1, -1, -1, -1