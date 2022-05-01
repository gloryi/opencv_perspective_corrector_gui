from collections import namedtuple
import csv
import cv2 as cv
import numpy as np
import os


class POI():
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"{self.x}, {self.y}"

    def add(self, other_poi):
        return POI(self.x + other_poi.x, self.y + other_poi.y)

    def divide(self, divider):
        return POI(self.x / divider, self.y / divider)

    def __call__(self):
        return [self.x, self.y]


class meta_perspective():
    def __init__(self, p1, p2, p3, p4):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4

    def __repr__(self):
        return f"{self.p1}, {self.p2}, {self.p3}, {self.p4}"

    def __add__(self, other_meta):
        return meta_perspective(self.p1.add(other_meta.p1),
                                self.p2.add(other_meta.p2),
                                self.p3.add(other_meta.p3),
                                self.p4.add(other_meta.p4))

    def divide(self, divider):
        return meta_perspective(self.p1.divide(divider),
                                self.p2.divide(divider),
                                self.p3.divide(divider),
                                self.p4.divide(divider))

    def as_array(self):
        return np.asarray([self.p1(), self.p2(), self.p3(), self.p1()])


def default_parser(data):
    filename, x1, y1, x2, y2, x3, y3, x4, y4 = data
    p1 = POI(float(x1), float(y1))
    p2 = POI(float(x2), float(y2))
    p3 = POI(float(x3), float(y3))
    p4 = POI(float(x4), float(y4))
    return filename, meta_perspective(p1, p2, p3, p4)


def file_reader(filepath):
    with open(filepath) as images_perspective_log:
        reader = csv.reader(images_perspective_log)
        for line in reader:
            yield line


class meta_image():
    def __init__(self, initial_data, parser_func):
        self.initial_data = initial_data
        self.parser_func = parser_func
        self.image_path, self.perspective = self.parser_func(self.initial_data)
        self.image = None
        self.h = None
        self.w = None
        self.H = None

    def __repr__(self):
        return f"{self.image_path}: {self.perspective}"

    def get_perspective_mat(self, target_meta):
        H, _ = cv.findHomography(self.perspective.as_array(),
                                 target_meta.as_array())
        self.H = H

    def read_image_dimentions(self):
        img = cv.imread(self.image_path)
        print(img.shape)
        self.h, self.w, _ = img.shape
        del img

    def read_image(self):
        img = cv.imread(self.image_path)
        return img

    def apply_perspective(self, target_meta):
        img = self.read_image()
        # corrected = cv.warpPerspective(img, perspective_mat, (img1.shape[1], img1.shape[0]))

    def calculate_corrected_size(self):
        if self.perspective is None or self.h is None or self.w is None:
            raise Exception("Image paramters are not defined")
        ...



def average_perspective(meta_perspectives):
    total_meta = meta_perspectives[0]
    for meta in meta_perspectives[1:]:
        total_meta += meta
    return total_meta.divide(len(meta_perspectives))


test_files_directory = os.path.join(os.getcwd(),"Test/correction_log.log")

meta_images = []

reader = file_reader(test_files_directory)
for line in reader:
    meta_images.append(meta_image(line, default_parser))
    print(meta_images[-1])
    meta_images[-1].read_image_dimentions()
    print(meta_images[-1].h)
    print(meta_images[-1].w)

central_meta = average_perspective([_.perspective for _ in meta_images])
