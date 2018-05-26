import os
import numpy as np
import cv2
import math
import time
if "arm" in os.popen("uname -m").read():
    from picamera.array import PiRGBArray
    from picamera import PiCamera

class CubeDetector:

    def __init__(self):
        self.isRaspberry = "arm" in os.popen("uname -m").read()
        self.camera = None
        self.cameraBuffer = None
        self.cameraImage = None

        """self.cubeColorsHSV = {"yellow": [50, 100, 97, 15],  # H,S,V,Range
                             "green": [96, 61, 60, 25],
                             "blue": [198, 100, 69, 25],
                             #"black": [240, 13, 30, 10],
                             "orange": [10, 93, 96, 10]}"""
        self.cubeColorsHSV = {"yellow": [56, 89, 77, 10],  # H,S,V,Range
                              "green": [114, 61, 56, 10],
                              "blue": [207, 83, 66, 10],
                              "black": [185, 35, 22, 10],
                              "orange": [20, 66, 70, 15]}
        self.initCamera()

    def getCubeList(self,preview=False,fromFile=""):
        if fromFile != "":
            self.cameraImage = cv2.imread(fromFile)
        else:
            for i in range(0,2):
                self.readCameraImage()
        self.cameraImage = cv2.resize(self.cameraImage, (255, 255))
        cv2.imwrite("img_{}.jpg".format(time.time()), self.cameraImage)
        if preview:
            self.previewArmCoordinates(self.cameraImage)
        imgCubeColor, maskCubeColor = self.filterColors(self.cameraImage)
        cubes = self.findCubes(imgCubeColor, maskCubeColor, self.cameraImage, preview)
        for c in cubes:
            c["position"] = self.transformPointInArmReferential(c["position"])
        if preview:
            cv2.imshow('final', self.cameraImage)
        return cubes

    def initCamera(self):
        if self.isRaspberry:
            self.camera = PiCamera()
            self.camera.resolution = (640, 480)
            self.cameraBuffer = PiRGBArray(self.camera, size=(640, 480))
            time.sleep(0.1)
        else:
            self.camera = cv2.VideoCapture(0)

    def readCameraImage(self):
        if self.isRaspberry:
            self.cameraBuffer.truncate(0)  # reset buffer
            self.camera.capture(self.cameraBuffer, format="bgr", resize=(640, 480))
            self.cameraImage = self.cameraBuffer.array
        else:
            retVal, self.cameraImage = self.camera.read()

    def filterColors(self, img):
        height, width, channels = img.shape
        imgBlur = cv2.medianBlur(img, 5)
        imgBlur = cv2.blur(imgBlur, (7, 7))
        hsv = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2HSV)
        finalMask = np.zeros((height, width), np.uint8)
        kernel = np.ones((5, 5), np.uint8)
        for key in self.cubeColorsHSV:
            color = self.cubeColorsHSV[key]
            lower = np.array([max(0, color[0] / 2 - color[3]), 120, 2])
            upper = np.array([min(255, color[0] / 2 + color[3]), 255, 255])
            if key == "black":
                lower = np.array([0, 0, 0])
                upper = np.array([255, 255, 60])

            mask = cv2.inRange(hsv, lower, upper)
            mask = cv2.erode(mask, kernel, iterations=2)
            finalMask = cv2.add(finalMask, mask)
            #cv2.imshow(key, mask)
        img = cv2.bitwise_and(img, img, mask=finalMask)
        return img, finalMask

    def transformPointInArmReferential(self, point):
        xRatio = 255.0 / 640.0  # srcPoint are in a VGA referential
        yRatio = 255.0 / 480.0  # srcPoint are in a VGA referential
        srcPoints = np.float32([[132 * xRatio, 327 * yRatio]
                                   , [410 * xRatio, 260 * yRatio]
                                   , [391 * xRatio, 420 * yRatio]
                                   , [207 * xRatio, 464 * yRatio]])
        dstPoints = np.float32([[0, 0], [100, 0], [100, 100], [0, 100]])
        M = cv2.getPerspectiveTransform(srcPoints, dstPoints)
        pt = np.array([[point[0], point[1]]], dtype="float32")
        pt = np.array([pt])
        result = cv2.perspectiveTransform(pt, M)
        return [result[0][0][0], 100 - result[0][0][1] + 10]# +10 on Y helps -> yolo

    def previewArmCoordinates(self, img):
        xRatio = 255.0 / 640.0  # srcPoint are in a VGA referential
        yRatio = 255.0 / 480.0  # srcPoint are in a VGA referential
        srcPoints = np.float32(
            [[132 * xRatio, 327 * yRatio], [410 * xRatio, 260 * yRatio], [391 * xRatio, 420 * yRatio],
             [207 * xRatio, 464 * yRatio]])
        imgPrev = img.copy()
        cv2.line(imgPrev, (srcPoints[0][0], srcPoints[0][1]), (srcPoints[1][0], srcPoints[1][1]), (0, 255, 0), 2)
        cv2.line(imgPrev, (srcPoints[1][0], srcPoints[1][1]), (srcPoints[2][0], srcPoints[2][1]), (0, 255, 0), 2)
        cv2.line(imgPrev, (srcPoints[2][0], srcPoints[2][1]), (srcPoints[3][0], srcPoints[3][1]), (0, 255, 0), 2)
        cv2.line(imgPrev, (srcPoints[3][0], srcPoints[3][1]), (srcPoints[0][0], srcPoints[0][1]), (0, 255, 0), 2)
        cv2.imshow("preview", imgPrev)

    def findCubes(self, img, mask, rawImage, draw=False):
        cubeList = []
        contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = contours[1]
        for c in cnts:
            rect = cv2.minAreaRect(c)
            area = rect[1][0] * rect[1][1]
            orientation = rect[2]
            # Reject small or large contours
            if area < 500 or area > 5000:
                continue

            # Find cube center
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            minY = 9999
            meanXLow = 0
            meanXHigh = 0
            for point in box:
                if point[1] < rect[0][1]:  # High point
                    meanXHigh += point[0]
                else:
                    meanXLow += point[0]
                if minY > point[1]:
                    minY = point[1]
            meanXLow /= 2
            meanXHigh /= 2
            cubeX = np.int0(rect[0][0])
            cubeY = np.int0(minY + max(rect[1][0], rect[1][1]) / 2)
            if rect[1][0] * 1.3 < rect[1][1] or rect[1][1] * 1.3 < rect[1][0]:
                cubeY = np.int0(minY + max(rect[1][0], rect[1][1]) / 2.7)
                cubeX = np.int0(meanXHigh * 0.6 + meanXLow * 0.4)
            grabPoint = (cubeX, cubeY)

            # find rotation
            rotation = 90 - orientation

            # find color
            cubeColor = ""
            colorScore = 0
            for key in self.cubeColorsHSV:
                color = self.cubeColorsHSV[key]
                lower = np.array([max(0, color[0] / 2 - color[3]), 140, 50])
                upper = np.array([min(255, color[0] / 2 + color[3]), 255, 255])
                if key == "black":
                    lower = np.array([0, 0, 0])
                    upper = np.array([255, 255, 60])
                lookupSize = 30
                height, width, channels = rawImage.shape
                subImage = rawImage[max(0, grabPoint[1] - lookupSize / 2)
                :min(height, grabPoint[1] + lookupSize / 2)
                , max(0, grabPoint[0] - lookupSize / 2)
                           :min(width, grabPoint[0] + lookupSize / 2)]
                subImage = cv2.medianBlur(subImage, 9)
                subImage = cv2.blur(subImage, (3, 3))
                hsv = cv2.cvtColor(subImage, cv2.COLOR_BGR2HSV)
                found = cv2.inRange(hsv, lower, upper)
                score = np.sum(found)
                if score > colorScore:
                    cubeColor = key
                    colorScore = score

            cubeList.append({'position': grabPoint, 'rotation': rotation, 'color': cubeColor})

            # show the image
            if draw:
                orientationPoint = (
                    np.int0(grabPoint[0] + 20 * math.cos((orientation - 90) * 3.1415 / 180.0))
                    , np.int0(grabPoint[1] + 20 * math.sin((orientation - 90) * 3.1415 / 180.0))
                )
                cv2.drawContours(img, [box], -1, (0, 255, 0), 2)
                cv2.circle(img, grabPoint, 5, (0, 255, 0), 2)
                cv2.line(img, grabPoint, orientationPoint, (0, 255, 0), 2)
                cv2.putText(img, "{0} {1}".format(np.int0(rotation), cubeColor), (cubeX - 25, cubeY - 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                cv2.imshow("cubes", img)
        return cubeList



if __name__ == '__main__':
    detector = CubeDetector()
    cubeList = detector.getCubeList(True, "/Users/alexandrebrehmer/Desktop/imgCube/img_1525760757.49.jpg")
    selectedCube = None
    for cube in cubeList:
        if cube["position"][0] >= 0 and cube["position"][0] <= 100 and cube["position"][1] >= 0 and cube["position"][
            1] <= 100:
            selectedCube = cube
    if selectedCube:
        print "Getting", selectedCube["color"], "cube at", selectedCube["position"][0], selectedCube["position"][1], \
        selectedCube["rotation"]
    cv2.waitKey()