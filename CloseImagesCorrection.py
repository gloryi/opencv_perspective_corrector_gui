import cv2 as cv
import os
import pathlib
from copy import deepcopy
from collections import namedtuple

WORKDIR = os.path.join(os.getcwd(), "Test")

color = namedtuple('Color', 'r, g, b')

POI = namedtuple('POI', 'x, y')


class POI(POI):

    def __repr__(self):
        return f"{self.x},{self.y}"


class quadrant():
    def __init__(self, x1, y1, x2, y2, _color=color(255, 255, 255), name="defult quadrant", prev_focus=None):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self._color = _color
        self.name = name
        if not prev_focus:
            self.focal_point = POI(
                (self.x2 + self.x1) / 2, (self.y2 + self.y1) / 2)
            self.focal_point_relative = POI(
                self.focal_point.x / self.x2, self.focal_point.y / self.y2)
        else:
            self.focal_point_relative = prev_focus
            self.focal_point = POI((self.x2 - self.x1) * prev_focus.x + self.x1,
                                   (self.y2 - self.y1) * prev_focus.y + self.y1)

    def get_corners_clockwise(self):
        x1, x2, x3, x4 = self.x1, self.x2, self.x2, self.x1
        y1, y2, y3, y4 = self.y1, self.y1, self.y2, self.y2
        tl = [int(x1), int(y1)]
        tr = [int(x2), int(y2)]
        br = [int(x3), int(y3)]
        bl = [int(x4), int(y4)]
        return tl, tr, br, bl

    def get_name(self):
        return self.name

    def get_borders(self):
        tl, tr, br, bl = self.get_corners_clockwise()
        return [[tl, tr], [tr, br], [br, bl], [bl, tl]]

    def are_coords_inside(self, p):
        x, y = p
        xl, xh = min(self.x1, self.x2), max(self.x1, self.x2)
        yl, yh = min(self.y1, self.y2), max(self.y1, self.y2)

        if x > xl and x <= xh and y > yl and y <= yh:
            return True

        return False

    def get_poi(self):
        return self.focal_point

    def update_poi(self, x, y):
        self.focal_point = POI(x, y)
        self.focal_point_relative = POI(
            self.focal_point.x / self.x2, self.focal_point.y / self.y2)

    def get_poi_relative(self):
        return self.focal_point_relative


class zones_processor():
    def __init__(self):
        self.zones = []

    def register_zone(self, zone):
        self.zones.append(zone)

    def get_target_zone(self, x, y):
        target_zones = [_ for _ in self.zones if _.are_coords_inside((x, y))]
        if len(target_zones) != 1:
            return None
        else:
            return target_zones[0]

    def get_zones_special_points(self):
        return [_.get_poi() for _ in self.zones]

    def get_all_known_zones(self):
        return self.zones


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


def draw_markers(cv_image, processor, filename):
    global cached

    cv_image = deepcopy(cached)

    for zone in processor.get_all_known_zones():
        borders = zone.get_borders()
        for border in borders:
            cv.line(cv_image, border[0], border[1], zone._color, 5)

        poi = zone.get_poi()
        cv.circle(cv_image, (int(poi.x), int(poi.y)), 3, zone._color, 2)
        cv.line(cv_image, (int(poi.x), 0),
                (int(poi.x), cv_image.shape[0]), zone._color, 2)
        cv.line(cv_image, (0, int(poi.y)),
                (cv_image.shape[1], int(poi.y)), zone._color, 2)

    cv.imshow(filename, cv_image)


def prepare_callback(cv_image, filename, processor):

    def mouse_event_callback(event, x, y, flags, params):
        global cached

        if event == cv.EVENT_MBUTTONDOWN:
            print("Selected coords ", x, y)
            zone = processor.get_target_zone(x, y)
            if zone:
                print(f"Selected zone {zone.get_name()}")
                zone.update_poi(x, y)

            else:
                print("There is no appropriate zone found")

            draw_markers(cv_image, processor, filename)

        if event == cv.EVENT_RBUTTONDOWN:
            print(f"Switching point from {event_marker}\
                to {swith_to_next_label(event_marker)}")
            event_marker = swith_to_next_label(event_marker)

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

    processor = zones_processor()
    processor.register_zone(
        quadrant(0, 0, w / 2, h / 2, _color=color(255, 0, 255), name="Q2", prev_focus=relative_focus[0]))
    processor.register_zone(
        quadrant(w / 2, 0, w, h / 2, _color=color(0, 255, 255), name="Q1", prev_focus=relative_focus[1]))
    processor.register_zone(
        quadrant(0, h / 2, w / 2, h, _color=color(0, 0, 255), name="Q4", prev_focus=relative_focus[2]))
    processor.register_zone(
        quadrant(w / 2, h / 2, w, h, _color=color(255, 255, 0), name="Q3", prev_focus=relative_focus[3]))

    callback = prepare_callback(cv_image, image, processor)

    screen_res = 1920, 1080
    scale_width = screen_res[0] * 0.8 / cv_image.shape[1]
    scale_height = screen_res[1] * 0.8 / h
    scale = min(scale_width, scale_height)

    window_width = int(cv_image.shape[1] * scale)
    window_height = int(h * scale)

    cv.namedWindow(image, cv.WINDOW_NORMAL)
    cv.resizeWindow(image, window_width, window_height)

    draw_markers(cv_image, processor, image)

    cv.setMouseCallback(image, callback)

    cv.waitKey(0)

    registrator_func(image, processor)

    relative_focus = [_.get_poi_relative() for _ in processor.get_all_known_zones()]

    cv.destroyAllWindows()

registrator_func(None, None, close=True)
