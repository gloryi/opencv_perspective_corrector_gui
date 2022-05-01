class GridProcessor():
    def __init__(self):
        self.guidelines = []

    def registerGuideline(self, guideline):
        self.guidelines.append(guideline)

    def getClosestGuideline(self, x, y):
        targetGuideline = min(self.guidelines, key = lambda gl: gl.distance(x,y) )
        return targetGuideline

    def getGuidelines(self):
        return self.guidelines

    def getCrossPoints(self):
        intersections = []
        for g1 in self.getGuidelines():
            for g2 in self.getGuidelines():
                if g1 == g2:
                    continue
                inters = g1.findCrossPoint(g2)
                if inters is None:
                    continue
                intersections.append(inters)
        return intersections
                #cv.circle(cv_image, (int(inters.x), int(inters.y)), 3, (0, 255, 0), 3)
