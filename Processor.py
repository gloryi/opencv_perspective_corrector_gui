from collections import namedtuple
import csv

POI = namedtuple('POI', 'x, y')

class POI(POI):
    def __repr__(self):
        return f"{self.x},{self.y}"


class meta_perspective():
    def __init__(p1, p2, p3, p4):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4


def default_parser(data):
    filename, x1, y1, x2, y2, x3, y3, x4, y4 = data
    p1, p2, p3, p4 = POI(float(x1),float(y1))

def file_reader(filepath):
    with open(filepath) as images_perspective_log:
    reader = csv.reader(images_perspective_log)
        for line in reader:
            yield line


class meta_image():
    def __init__(initial_data, parser_func):
        self.initial_data = initial_data
        self.parser_func = parser_func
        self.image_path, self.perspective = self.parser_func(self.initial_data)
