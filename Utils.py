import pathlib
from collections import namedtuple
import os
from Config import WORKDIR

color = namedtuple('Color', 'r, g, b')

POI = namedtuple('POI', 'x, y')


class POI(POI):

    def __repr__(self):
        return f"{self.x},{self.y}"

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