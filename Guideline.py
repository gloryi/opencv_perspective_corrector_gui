from Utils import POI

class Guideline():
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
        applyDist = lambda _ : dist(x, y, _)
        poses = (self.p1, self.p2)
        closePoint, farPint = min(poses, key = applyDist), max(poses, key=applyDist)
        return closePoint, farPint

    def updateClosesetPoint(self, x, y):
        close, far = self.getClosestPoint(x, y)
        self.p1 = far
        self.p2 = POI(x, y)

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
        print("Guideline was activated")
        self.color = (255, 0, 255)

    def deactivate(self):
        self.color = (0, 0, 255)
        self.selectedPoint = None