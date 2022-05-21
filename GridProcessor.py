class GridProcessor():
    def __init__(self):
        self.guidelines = []
        self.xBorder = 0
        self.yBorder = 0

    def registerGuideline(self, guideline):
        self.guidelines.append(guideline)

    def getClosestGuideline(self, x, y):
        targetGuideline = min(self.guidelines, key = lambda gl: gl.distance(x,y) )
        return targetGuideline

    def getGuidelines(self):
        return self.guidelines

    def getCrossPoints(self):
        intersections = []
        for i in range(len(self.getGuidelines())):
            for j in range(i,len(self.getGuidelines())):
                g1, g2 = self.guidelines[i], self.guidelines[j]
                if g1 == g2:
                    continue
                inters = g1.findCrossPoint(g2)
                if inters is None:
                    continue
                if inters.x < 0 or inters.y <0:
                    continue
                if inters.x > self.xBorder or inters.y > self.yBorder:
                    continue
                intersections.append(inters)
        return intersections
                #cv.circle(cv_image, (int(inters.x), int(inters.y)), 3, (0, 255, 0), 3)
