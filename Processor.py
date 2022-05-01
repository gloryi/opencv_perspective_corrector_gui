from collections import namedtuple
import csv
import cv2 as cv
import numpy as np
import os
from scipy import linalg


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
        return np.asarray([self.p1(), self.p2(), self.p3(), self.p4()])


def default_parser(data):
    filename, x1, y1, x2, y2, x3, y3, x4, y4 = data
    p1 = POI(float(x1), float(y1))
    p2 = POI(float(x2), float(y2))
    p3 = POI(float(x3), float(y3))
    p4 = POI(float(x4), float(y4))
    return filename, meta_perspective(p1, p2, p3, p4)


def file_reader(image_path):
    with open(image_path) as images_perspective_log:
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
        self.homographyMatrix = None
        self.homographyMatrixReversed = None
        self.homographyMatrixInverted = None
        self.homographyMatrixReversedInverted = None

    def __repr__(self):
        return f"{self.image_path}: {self.perspective}"

    def _calculate_perspective_mat(self, target_meta):
        H, _ = cv.findHomography(self.perspective.as_array(),
                                 target_meta.as_array())
        # print(f"Homography Matrix are\n{H}")
        HRev, _ = cv.findHomography(target_meta.as_array(),
                                    self.perspective.as_array())
        # print(f"Homography Matrix Reversed are \n{HRev}")

        self.homographyMatrix = H
        self.homographyMatrixReversed = HRev
        self.homographyMatrixInverted = linalg.inv(self.homographyMatrix)
        self.homographyMatrixReversedInverted = linalg.inv(
            self.homographyMatrixReversed)

    def _read_image_dimentions(self):
        img = cv.imread(self.image_path)
        # print(img.shape)
        self.h, self.w, _ = img.shape
        del img

    def _read_image(self):
        img = cv.imread(self.image_path)
        return img

    def _apply_perspective(self, target_meta, target_shape):
        image_original = self._read_image()
        target_shape = target_shape if target_shape is not None else [
            self.h, self.w]
        image_corrected = cv.warpPerspective(
            image_original, self.homographyMatrix, (target_shape[1], target_shape[0]))
        return image_corrected

    def apply_translation(self, target_meta, target_shape):
        if self.h is None or self.w is None or self.homographyMatrix is None:
            self._read_image_dimentions()
            self._calculate_perspective_mat(target_meta)
        image_translated = self._apply_perspective(target_meta, target_shape)

        out_image_path = self._get_prefixed_image_path("00_TRANS_")

        self._dump_image(image_translated, out_image_path)

    def _dump_image(self, mat, image_path):
        cv.imwrite(image_path, mat)

    def _get_prefixed_image_path(self, prefix):
        base_image_path = os.path.basename(self.image_path)
        return self.image_path.replace(base_image_path, prefix + base_image_path)


    def perspective_warp(image, transform):
        h, w = image.shape[:2]
        corners_bef = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
        corners_aft = cv2.perspectiveTransform(corners_bef, transform)
        xmin = math.floor(corners_aft[:, 0, 0].min())
        ymin = math.floor(corners_aft[:, 0, 1].min())
        xmax = math.ceil(corners_aft[:, 0, 0].max())
        ymax = math.ceil(corners_aft[:, 0, 1].max())
        x_adj = math.floor(xmin - corners_aft[0, 0, 0])
        y_adj = math.floor(ymin - corners_aft[0, 0, 1])
        translate = np.eye(3)
        translate[0, 2] = -xmin
        translate[1, 2] = -ymin
        corrected_transform = np.matmul(translate, transform)
        return cv2.warpPerspective(image, corrected_transform, (math.ceil(xmax - xmin), math.ceil(ymax - ymin))), x_adj, y_adj



    def calculate_corrected_size(self):
        if self.homographyMatrix is None or \
                self.homographyMatrixReversed is None or \
                self.h is None or \
                self.w is None:
            raise Exception("Image paramters are not defined")
        h_corner = np.asarray([self.h, 0.0, 1.0])
        w_corner = np.asarray([0.0, self.w, 1.0])

        print("*" * 10 + "\n" + self.image_path)
        # h, w corners with forward homography matrix applied
        h_corner_translated = np.dot(h_corner, self.homographyMatrix)
        w_corner_translated = np.dot(w_corner, self.homographyMatrix)
        print("Forward homography matrix applied\n")
        print(h_corner_translated)
        print(w_corner_translated)
        # h, w corners with reversed homography matrix applied
        h_corner_translated = np.dot(h_corner, self.homographyMatrixReversed)
        w_corner_translated = np.dot(w_corner, self.homographyMatrixReversed)
        print("Reversed homography matrix applied\n")
        print(h_corner_translated)
        print(w_corner_translated)
        # h, w corners with inverted homography matrix applied
        h_corner_translated = np.dot(h_corner, self.homographyMatrixInverted)
        w_corner_translated = np.dot(w_corner, self.homographyMatrixInverted)
        print("Inverted homography matrix applied\n")
        print(h_corner_translated)
        print(w_corner_translated)
        # h, w corners with reversed inverted homography matrix applied
        h_corner_translated = np.dot(
            h_corner, self.homographyMatrixReversedInverted)
        w_corner_translated = np.dot(
            w_corner, self.homographyMatrixReversedInverted)
        print("Reversed and inverted homography matrix applied\n")
        print(h_corner_translated)
        print(w_corner_translated)
        print("*" * 10)


def average_perspective(meta_perspectives):
    total_meta = meta_perspectives[0]
    for meta in meta_perspectives[1:]:
        total_meta += meta
    return total_meta.divide(len(meta_perspectives))


test_files_directory = os.path.join(os.getcwd(), "Test/correction_log.log")

meta_images = []

reader = file_reader(test_files_directory)

LAST_ADDED = -1

for line in reader:
    meta_images.append(meta_image(line, default_parser))
    print(meta_images[LAST_ADDED])
    meta_images[LAST_ADDED]._read_image_dimentions()
    # print(meta_images[LAST_ADDED].h)
    # print(meta_images[LAST_ADDED].w)

central_meta = average_perspective([_.perspective for _ in meta_images])
print(central_meta)

for meta_image in meta_images:
    #meta_image.apply_translation(central_meta, None)
    meta_image._calculate_perspective_mat(central_meta)
    meta_image.calculate_corrected_size()
