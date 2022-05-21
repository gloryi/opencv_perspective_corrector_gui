import os
import cv2 as cv
from copy import deepcopy

from Utils import color, POI, iterate_images
from Config import *
from Guideline import Guideline
from GridProcessor import GridProcessor



# process mouse event on image

def prepare_registrator(correction_points_path):
    correction_log = open(correction_points_path, 'w')

    def register_points(img_name, processor, close=False):
        if close:
            correction_log.close()
        else:
            print(",".join([str(_) for _ in [img_name, *processor.getCrossPoints()]]))
            correction_log.write(",".join(
                [str(_) for _ in [img_name, *processor.getCrossPoints()]]) + "\n")
    return register_points


class point_lable:
    FIRST = "first"
    SECOND = "second"
    THIRD = "third"


def get_ind_of_lable_type(label):
    return 0 if label == point_lable.THIRD\
        else 1 if label == point_lable.FIRST\
        else 2


def swith_to_next_label(label):
    return point_lable.FIRST if label == point_lable.THIRD\
        else point_lable.SECOND if label == point_lable.FIRST\
        else point_lable.THIRD


def map_lable_to_col(label):
    colors = [(255, 255, 255), (0, 255, 0), (0, 0, 255)]
    return colors[get_ind_of_lable_type(label)]


cached = None


def drawLines(cv_image, processor, filename):
    global cached

    cv_image = deepcopy(cached)

    for color_switch, guideline in enumerate(processor.getGuidelines()):

        #w, h = cv_image.shape[1], cv_image.shape[0]
        farPoint1 = guideline.getPointOfDist(4000)
        farPoint2 = guideline.getPointOfDist(-4000)
        

        #firstPoint = guideline.p1
 
        cv.line(cv_image, (int(farPoint1.x), int(farPoint1.y)),
                (int(farPoint2.x), int(farPoint2.y)), guideline.getColor() , 2)

        if (guideline.isActivated()):
            sp = guideline.getSelected()
            cv.circle(cv_image, (int(sp.x), int(sp.y)), 3, (255, 255, 0), 3)



        p1, p2 = guideline.p1, guideline.p2

        switchColor = lambda switch,target: 255 if switch%2 == target else 0

        cv.circle(cv_image, (int(p1.x), int(p1.y)), 500, (switchColor(color_switch,0), switchColor(color_switch,1), switchColor(color_switch,0)), 3)
        cv.circle(cv_image, (int(p2.x), int(p2.y)), 500, (switchColor(color_switch,0), switchColor(color_switch,1), switchColor(color_switch,0)), 3)



    for g1 in processor.getGuidelines():
        for g2 in processor.getGuidelines():
            if g1 == g2:
                continue
            inters = g1.findCrossPoint(g2)
            if inters is None:
                continue
            cv.circle(cv_image, (int(inters.x), int(inters.y)), 3, (0, 255, 0), 3)

    cv.imshow(filename, cv_image)


def prepare_callback(cv_image, filename, processor):

    def mouse_event_callback(event, x, y, flags, params):
        global cached

        if event == cv.EVENT_MBUTTONDOWN:
            print("Selected coords ", x, y)

            #targetGuideline = min(processor.getGuidelines(), key = lambda _ : _.distance(x,y))

            targetGuideline, *others = sorted(processor.getGuidelines(), key = lambda _ : _.distance(x,y))

            targetGuideline.activate()

            #
            closestPoint = targetGuideline.updateClosesetPoint(x,y)
            #targetGuideline.updateClosest()

            for otherLine in others:
                otherLine.deactivate()

            drawLines(cv_image, processor, filename)

    return mouse_event_callback





registrator_func = prepare_registrator(
    os.path.join(WORKDIR, "correction_log.log"))

images_iterator = iterate_images()

relative_focus = [None]*4


processor =  GridProcessor()
g1 = Guideline(POI(50,   0), POI(50, 1500), clapToTop   = True)
g2 = Guideline(POI(2000,  0), POI(2000, 1500), clapToTop  = True)
g3 = Guideline(POI(0,   50), POI(1500, 50) , clapToLeft = True)
g4 = Guideline(POI(0,  2000), POI(1500, 2000), clapToLeft = True)
processor.registerGuideline(g1)
processor.registerGuideline(g2)
processor.registerGuideline(g3)
processor.registerGuideline(g4)



for image in images_iterator:
    cv_image = cv.imread(image)
    cached = deepcopy(cv_image)

    w, h = cv_image.shape[1], cv_image.shape[0]


    callback = prepare_callback(cv_image, image, processor)

    screen_res = 1920, 1080
    scale_width = screen_res[0] * 0.8 / cv_image.shape[1]
    scale_height = screen_res[1] * 0.8 / h
    scale = min(scale_width, scale_height)

    window_width = int(cv_image.shape[1] * scale)
    window_height = int(h * scale)

    processor.xBorder, processor.yBorder = w, h

    cv.namedWindow(image, cv.WINDOW_NORMAL)
    cv.resizeWindow(image, window_width, window_height)

    drawLines(cv_image, processor, image)

    cv.setMouseCallback(image, callback)

    cv.waitKey(0)

    registrator_func(image, processor)

    #relative_focus = [_.get_poi_relative() for _ in processor.get_all_known_zones()]

    cv.destroyAllWindows()

registrator_func(None, None, close=True)
