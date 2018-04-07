import time
import os
#from cartographie.lecteurCarte import LecteurCarte
#from cartographie.chercheurChemin import ChercheurChemin
#from intelligence.robot import Robot
#from intelligence.lecteurRobot import LecteurRobot
#from intelligence.executeurObjectif import ExecuteurObjectif
import math
isRaspberry = "arm" in os.popen("uname -m").read()

if(isRaspberry):
    from picamera.array import PiRGBArray
    from picamera import PiCamera

import numpy as np
import cv2

camera = None
cameraBuffer = None
cameraImage = None
def initCamera():
    global isRaspberry
    global camera
    global cameraBuffer
    global cameraImage
    if(isRaspberry):
        camera = PiCamera()
        camera.resolution = (640, 480)
        cameraBuffer = PiRGBArray(camera, size=(640,480))
        time.sleep(0.1)
    else:
        camera = cv2.VideoCapture(0)

def readCameraImage():
    global isRaspberry
    global camera
    global cameraBuffer
    global cameraImage
    if (isRaspberry):
        cameraBuffer.truncate(0) #reset buffer
        camera.capture(cameraBuffer, format="bgr", resize=(640,480))
        cameraImage = cameraBuffer.array
    else:
        retVal, cameraImage = camera.read()


def angle_cos(p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )

def nothing(x):
    pass
cv2.namedWindow('bars')
cv2.createTrackbar('convex','bars',0,100,nothing)
cv2.createTrackbar('circle','bars',0,100,nothing)
cv2.createTrackbar('inertia','bars',0,100,nothing)

#cubeColorsHSV = {"yellow": [44, 100, 97, 10]}

cubeColorsHSV = {"yellow": [44, 100, 97, 10], #H,S,V,Range
              "green": [96, 61, 60, 20],
              "blue": [198, 100, 69, 20],
              "black": [240, 13, 6, 10],
              "orange": [19, 81, 82, 5]}

def filterColors(img):
    height, width, channels = img.shape
    imgBlur = cv2.medianBlur(img,5)
    imgBlur = cv2.blur(imgBlur, (7, 7))
    hsv = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2HSV)
    finalMask = np.zeros((height,width), np.uint8)
    kernel = np.ones((5, 5), np.uint8)
    for key in cubeColorsHSV:
        color = cubeColorsHSV[key]
        lower = np.array([max(0,color[0]/2-color[3]), 140, 50])
        upper = np.array([min(255,color[0]/2+color[3]), 255, 255])
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.erode(mask, kernel, iterations=2)
        finalMask = cv2.add(finalMask, mask)
    img = cv2.bitwise_and(img, img, mask=finalMask)
    return img, finalMask

def transformPointInArmReferential(point):
    xRatio = 255.0/640.0 # srcPoint are in a VGA referential
    yRatio = 255.0/480.0 # srcPoint are in a VGA referential
    srcPoints = np.float32([[132*xRatio, 327*yRatio]
                           , [410*xRatio, 260*yRatio]
                           , [391*xRatio, 420*yRatio]
                           , [207*xRatio, 464*yRatio]])
    dstPoints = np.float32([[0, 0], [100, 0], [100, 100], [0, 100]])
    M = cv2.getPerspectiveTransform(srcPoints, dstPoints)
    pt = np.array([[point[0],point[1]]], dtype = "float32")
    pt = np.array([pt])
    result = cv2.perspectiveTransform(pt, M)
    return [result[0][0][0],100-result[0][0][1]]

def previewArmCoordinates(img):
    xRatio = 255.0/640.0 # srcPoint are in a VGA referential
    yRatio = 255.0/480.0 # srcPoint are in a VGA referential
    srcPoints = np.float32([[132*xRatio, 327*yRatio], [410*xRatio, 260*yRatio], [391*xRatio, 420*yRatio], [207*xRatio, 464*yRatio]])
    imgPrev = img.copy()
    cv2.line(imgPrev, (srcPoints[0][0],srcPoints[0][1]), (srcPoints[1][0],srcPoints[1][1]), (0, 255, 0), 2)
    cv2.line(imgPrev, (srcPoints[1][0],srcPoints[1][1]), (srcPoints[2][0],srcPoints[2][1]), (0, 255, 0), 2)
    cv2.line(imgPrev, (srcPoints[2][0],srcPoints[2][1]), (srcPoints[3][0],srcPoints[3][1]), (0, 255, 0), 2)
    cv2.line(imgPrev, (srcPoints[3][0],srcPoints[3][1]), (srcPoints[0][0],srcPoints[0][1]), (0, 255, 0), 2)
    cv2.imshow("preview", imgPrev)
    dstPoints = np.float32([[0,0],[255,0],[255,255], [0,255]])
    #M = cv2.getPerspectiveTransform(srcPoints, dstPoints)
    #img = cv2.warpPerspective(img, M, (255,255))

def findCubesBlob(img, mask):
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=1)
    params = cv2.SimpleBlobDetector_Params()
    params.filterByColor = True
    params.blobColor = 255

    params.filterByArea = True
    params.minArea = 150

    params.filterByCircularity = True
    params.minCircularity = 0.25#float(cv2.getTrackbarPos('circle','bars'))/100.0

    params.filterByConvexity = True
    params.minConvexity = 0.25#float(cv2.getTrackbarPos('convex','bars'))/100.0

    params.filterByInertia = True
    params.minInertiaRatio = 0.01#float(cv2.getTrackbarPos('inertia','bars'))/100.0

    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(mask)
    im_with_keypoints = cv2.drawKeypoints(img, keypoints, np.array([]), (0, 0, 255),
                                          cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    cv2.imshow("Keypoints", im_with_keypoints)
    return img

def findCubes(img, mask, rawImage):
    cubeList = []
    draw = True
    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = contours[1]
    for c in cnts:
        rect = cv2.minAreaRect(c)
        area = rect[1][0] * rect[1][1]
        orientation = rect[2]
        #Reject small or large contours
        if area < 500 or area > 5000:
            continue

        #Find cube center
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        minY = 9999
        meanXLow = 0
        meanXHigh = 0
        for point in box:
            if point[1]<rect[0][1]: #High point
                meanXHigh += point[0]
            else:
                meanXLow += point[0]
            if minY > point[1]:
                minY = point[1]
        meanXLow /= 2
        meanXHigh /= 2
        cubeX = np.int0(rect[0][0])
        cubeY = np.int0(minY + max(rect[1][0],rect[1][1]) / 2)
        if rect[1][0]*1.3 < rect[1][1] or rect[1][1]*1.3 < rect[1][0]:
            cubeY = np.int0(minY + max(rect[1][0],rect[1][1]) / 2.7)
            cubeX = np.int0(meanXHigh * 0.6 + meanXLow * 0.4)
        grabPoint = (cubeX, cubeY)

        #find rotation
        rotation = 90-orientation

        #find color
        cubeColor = ""
        colorScore = 0
        for key in cubeColorsHSV:
            color = cubeColorsHSV[key]
            lower = np.array([max(0, color[0] / 2 - color[3]), 140, 50])
            upper = np.array([min(255, color[0] / 2 + color[3]), 255, 255])
            lookupSize = 30
            height, width, channels = rawImage.shape
            subImage = rawImage[max(0,grabPoint[1]-lookupSize/2)
                                :min(height, grabPoint[1]+lookupSize/2)
                                ,max(0,grabPoint[0]-lookupSize/2)
                                :min(width,grabPoint[0]+lookupSize/2)]
            subImage = cv2.medianBlur(subImage, 9)
            subImage = cv2.blur(subImage, (3, 3))
            hsv = cv2.cvtColor(subImage, cv2.COLOR_BGR2HSV)
            found = cv2.inRange(hsv, lower, upper)
            score = np.sum(found)
            #print score, key
            if score > colorScore:
                cubeColor = key
                colorScore = score

        cubeList.append({'position': grabPoint, 'rotation': rotation, 'color':cubeColor})

        # show the image
        if draw:
            orientationPoint = (
                np.int0(grabPoint[0] + 20 * math.cos((orientation - 90) * 3.1415 / 180.0))
                , np.int0(grabPoint[1] + 20 * math.sin((orientation - 90) * 3.1415 / 180.0))
            )
            cv2.drawContours(img, [box], -1, (0, 255, 0), 2)
            cv2.circle(img, grabPoint, 5, (0, 255, 0), 2)
            cv2.line(img, grabPoint, orientationPoint, (0, 255, 0), 2)
            cv2.putText(img, "{0} {1}".format(np.int0(rotation), cubeColor), (cubeX - 20, cubeY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.imshow("cubes", img)
    return cubeList

#
import random
def main():
    global isRaspberry
    global cameraImage
    initCamera()

    while True:
        readCameraImage()
        #cameraImage = cv2.imread("../../imageArea.jpg".format(random.randint(1, 4)))
        cameraImage = cv2.resize(cameraImage, (255, 255))
        previewArmCoordinates(cameraImage)
        startTotal = time.time()
        imgCubeColor, maskCubeColor = filterColors(cameraImage)
        cubes = findCubes(imgCubeColor, maskCubeColor, cameraImage)
        for c in cubes:
            armPosition = transformPointInArmReferential(c["position"])
            if armPosition[0] >= 0 and armPosition[0] <= 100 and armPosition[1] >= 0 and armPosition[1] <= 100:
                print "arm grab " + c["color"] + " at ", armPosition, c["rotation"]
        end = time.time()
        print "End:", end - startTotal
        cv2.imshow('final', cameraImage)
        if cv2.waitKey(500) == 27:
            break  # esc to quit
    cv2.destroyAllWindows()
    exit()

























    #Detection du rapsberry
    isRaspberry = "arm" in os.popen("uname -m").read()
    #isRaspberry = "arm" in os.uname()[4]

    if isRaspberry:  # raspberry
        screen = False
        robotConnected = True
        drawGraph = False and screen
    else:
        screen = True
        robotConnected = False
        drawGraph = True and screen

    fichierCarte = "cartes/carte_2017.xml"
    fichierObjectif = "objectifs/2017/objectifsPrincipalSolo.xml"
    fichierRobot = "robots/robotPrincipal2017.xml"

    fenetre = None

    # creation du robot
    print "Reading robot file"
    lecteurRobot = LecteurRobot(fichierRobot)
    robot = lecteurRobot.lire()
    # creation du lecteur de carte
    print "Reading map file"
    carte = LecteurCarte(fichierCarte, robot.largeur)
    listePointInteret = carte.lire()   # chargement de la carte

    # creation de l'afficihage de la carte
    if screen:
        print "Creating map view"
        from affichage.afficheurCarte import AfficheurCarte
        affichage = AfficheurCarte(fichierCarte, listePointInteret, 0.25, 300)
        fenetre = affichage.fenetre
        affichage.afficherCarte()  # affichage de la carte

    # creation du pathfinding
    print "Initializing pathfinding"
    chercher = ChercheurChemin(carte.getTaille(), carte.getHash(), listePointInteret, fenetre)
    if drawGraph:
        chercher.graph.dessiner(fenetre)

    if fenetre:
        fenetre.win.redraw()

    print "Initializing robot"
    simulation = robot.initialiser(chercher, listePointInteret, fenetre, not robotConnected)
    if simulation:
        print("ERROR: once again the program is in simulation mode! Some boards can't be detected.")
        print("Statring in 2s.")
        time.sleep(2)

    print "Creating IA"
    IA = ExecuteurObjectif(robot, fichierObjectif, fichierCarte, chercher, fenetre)  # creation de l'IA

    IA.afficherObjectifs()
    print "Running IA"
    IA.executerObjectifs()  # execution de l'IA

    print("End of the match, closing board connections")
    robot.closeConnections()

    # Pour tester le pathfinding, cliquez a deux endroits sur la carte
    if screen:
        while True:
            click1 = fenetre.win.getMouse()
            click2 = fenetre.win.getMouse()
            x1 = click1.getX() / fenetre.ratio - fenetre.offset
            y1 = click1.getY() / fenetre.ratio - fenetre.offset
            x2 = click2.getX() / fenetre.ratio - fenetre.offset
            y2 = click2.getY() / fenetre.ratio - fenetre.offset
            print "({} {}) ({}, {})" % (x1, y1, x2, y2)
            listMouvement = chercher.trouverChemin(x1, y1, x2, y2, listePointInteret)
            if listMouvement is None or len(listMouvement) == 0:
                print "WARNING Path Not Found"
            else:
                for ligne in listMouvement:
                    ligne.setCouleur("green")
                    ligne.dessiner(fenetre)
            fenetre.win.redraw()
    time.sleep(5)


if __name__ == "__main__":
    main()
