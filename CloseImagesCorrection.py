import cv2 as cv
import os
import pathlib
from copy import deepcopy
from collections import namedtuple

WORKDIR = os.path.join(os.getcwd(), "Test")

color = namedtuple('Color', 'r, g, b')

#POI = namedtuple('POI', 'x, y')


class POI(POI):

    def __repr__(self):
        return f"{self.x},{self.y}"



class guideline():
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        # TODO Unify processing of this parameter
        self.selectedPoint = None
        self.color = (0, 0, 255)

    def distance(self, x, y):
        # ToDo - unificate method
        dist = lambda x1, y1, x2, y2 : ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        return min(dist(x, y, self.p1.x, self.p1.y), dist(x, y, self.p2.x, self.p2.y))

    def getColor(self):
        return self.color

    def getClosestPoint(self, x, y):
        dist = lambda x, y, p : ((x - p.x) ** 2 + (y - p.y) ** 2) ** 0.5
        closestPoint = min([self.p1, self.p2], key = lambda _ : dist(x, y, _))
        return closestPoint

    def updateClosesetPoint(self, x, y):
        closest = self.getClosestPoint(x, y)
        closest = POI(x, y)

    def selectPoint(self, point):
        self.selectedPoint = point

    def getSelected(self):
        return self.selectedPoint

    def findCrossPoint(self, otherGuideline):
        x1, x2, x3, x4 = self.p1.x, self.p2.x, otherGuideline.p1.x, otherGuideline.p2.x
        y1, y2, y3, y4 = self.p1.y, self.p2.y, otherGuideline.p1.y, otherGuideline.p2.y

        x1y2 = x1*y2
        y1x2 = y1*x2

        x3y4 = x3*y4
        y3x4 = y3*x4

        D = (x1 - x2)*(y3 - y4) - (y1-y2)*(x3 - x4)

        if D == 0:
            return None

        Cx = (x1y2 - y1x2)*(x3 - x4) - (x1 - x2)*(x3y4 - y3x4)
        Cx /= D

        Cy = (x1y2 - y1x2)*(y3 - y4) - (y1 - y2)*(x3y4 - y3x4)
        Cy /= D

        return POI(Cx, Cy)

    def getPointOfDist(self, dist):
        baseVec = [self.p2.x - self.p1.x, self.p2.y - self.p1.y]
        baseVecL = (baseVec[0]**2 + baseVec[1]**2)**0.5
        baseVec[0] = baseVec[0]/baseVecL*dist
        baseVec[1] = baseVec[1]/baseVecL*dist

        return POI(self.p1.x + baseVec[0], self.p1.y + baseVec[1])

    def isActivated(self):
        return not self.selectedPoint is None

    def activate(self):
        print("guideline was activated")
        self.color = (255, 0, 255)

    def deactivate(self):
        self.color = (0, 0, 255)
        self.selectedPoint = None




class gridProcessor():
    def __init__(self):
        self.guidelines = []

    def registerGuideline(self, guideline):
        self.guidelines.append(guideline)

    def getClosestGuideline(self, x, y):
        targetGuideline = min(self.guidelines, key = lambda gl: gl.distance(x,y) )
        return targetGuideline

    def getGuidelines(self):
        return self.guidelines


# process mouse event on image

def prepare_registrator(correction_points_path):
    correction_log = open(correction_points_path, 'w')

    def register_points(img_name, processor, close=False):
        if close:
            correction_log.close()
        else:
            print(",".join([str(_) for _ in [img_name, *processor.get_zones_special_points()]]))
            correction_log.write(",".join(
                [str(_) for _ in [img_name, *processor.get_zones_special_points()]]) + "\n")
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

    for guideline in processor.getGuidelines():

        #w, h = cv_image.shape[1], cv_image.shape[0]
        farPoint = guideline.getPointOfDist(4000)
        #farPoint = POI(min(w, farPoint.x), min(h, farPoint.y))
        

        firstPoint = guideline.p1
 
        cv.line(cv_image, (int(firstPoint.x), int(firstPoint.y)),
                (int(farPoint.x), int(farPoint.y)), guideline.getColor() , 2)

        if (guideline.isActivated()):
            sp = guideline.getSelected()
            cv.circle(cv_image, (int(sp.x), int(sp.y)), 3, (255, 255, 0), 2)



        p1, p2 = guideline.p1, guideline.p2

        cv.circle(cv_image, (int(p1.x), int(p1.y)), 3, (255, 0, 0), 2)
        cv.circle(cv_image, (int(p2.x), int(p2.y)), 3, (255, 0, 0), 2)



    for g1 in processor.getGuidelines():
        for g2 in processor.getGuidelines():
            if g1 == g2:
                continue
            inters = g1.findCrossPoint(g2)
            if inters is None:
                continue
            cv.circle(cv_image, (int(inters.x), int(inters.y)), 3, (0, 255, 0), 2)

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



            #zone = processor.get_target_zone(x, y)
            #if zone:
            #    print(f"Selected zone {zone.get_name()}")
            #    zone.update_poi(x, y)

            #else:
            #    print("There is no appropriate zone found")

            #draw_markers(cv_image, processor, filename)

        # if event == cv.EVENT_RBUTTONDOWN:
            #print(f"Switching point from {event_marker}\
            #    to {swith_to_next_label(event_marker)}")
            #event_marker = swith_to_next_label(event_marker)

            drawLines(cv_image, processor, filename)

    return mouse_event_callback


# TODO ADD SKIP OR PROCESSING OF MISSING
def iterate_images():
    images_list = []
    for _r, _d, _f in os.walk(WORKDIR):
        for f in _f:
            # print(f)
            if pathlib.Path(f).suffix == ".jpg":
                images_list.append(os.path.join(_r, f))
    # print(images_list)
    for image in images_list:
        yield image
        # break


registrator_func = prepare_registrator(
    os.path.join(WORKDIR, "correction_log.log"))

images_iterator = iterate_images()

relative_focus = [None]*4

for image in images_iterator:
    cv_image = cv.imread(image)
    cached = deepcopy(cv_image)

    w, h = cv_image.shape[1], cv_image.shape[0]

    # processor = zones_processor()
    #processor.register_zone(
    #    quadrant(0, 0, w / 2, h * 0.25, _color=color(255, 0, 255), name="Q2", prev_focus=relative_focus[0]))
    #processor.register_zone(
    #    quadrant(w / 2, 0, w, h * 0.25, _color=color(0, 255, 255), name="Q1", prev_focus=relative_focus[1]))
    #processor.register_zone(
    #    quadrant(0, h * 0.25, w / 2, h, _color=color(0, 0, 255), name="Q4", prev_focus=relative_focus[2]))
    #processor.register_zone(
    #    quadrant(w / 2, h * 0.25, w, h, _color=color(255, 255, 0), name="Q3", prev_focus=relative_focus[3]))



    processor =  gridProcessor()
    g1 = guideline(POI(100,   0), POI(100, 1500) )
    g2 = guideline(POI(1000,  0), POI(1000, 1500))
    g3 = guideline(POI(0,   100), POI(1500, 100) )
    g4 = guideline(POI(0,  1000), POI(1500, 1000))
    processor.registerGuideline(g1)
    processor.registerGuideline(g2)
    processor.registerGuideline(g3)
    processor.registerGuideline(g4)


    callback = prepare_callback(cv_image, image, processor)

    screen_res = 1920, 1080
    scale_width = screen_res[0] * 0.8 / cv_image.shape[1]
    scale_height = screen_res[1] * 0.8 / h
    scale = min(scale_width, scale_height)

    window_width = int(cv_image.shape[1] * scale)
    window_height = int(h * scale)

    cv.namedWindow(image, cv.WINDOW_NORMAL)
    cv.resizeWindow(image, window_width, window_height)

    drawLines(cv_image, processor, image)

    cv.setMouseCallback(image, callback)

    cv.waitKey(0)

    registrator_func(image, processor)

    relative_focus = [_.get_poi_relative() for _ in processor.get_all_known_zones()]

    cv.destroyAllWindows()

registrator_func(None, None, close=True)
