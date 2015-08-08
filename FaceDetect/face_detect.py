import dlib
import cv2
import sys
import numpy as np
import os

def getTranslationMatrix2d(dx, dy):
    """
    Returns a numpy affine transformation matrix for a 2D translation of
    (dx, dy)
    """
    return np.matrix([[1, 0, dx], [0, 1, dy], [0, 0, 1]])

def rotateImage(image, angle):
    """
    Rotates the given image about it's centre
    """
    image_size = (image.shape[1], image.shape[0])
    image_center = tuple(np.array(image_size) / 2)

    rot_mat = np.vstack([cv2.getRotationMatrix2D(image_center, angle, 1.0), [0, 0, 1]])
    trans_mat = np.identity(3)

    w2 = image_size[0] * 0.5
    h2 = image_size[1] * 0.5

    rot_mat_notranslate = np.matrix(rot_mat[0:2, 0:2])

    tl = (np.array([-w2, h2]) * rot_mat_notranslate).A[0]
    tr = (np.array([w2, h2]) * rot_mat_notranslate).A[0]
    bl = (np.array([-w2, -h2]) * rot_mat_notranslate).A[0]
    br = (np.array([w2, -h2]) * rot_mat_notranslate).A[0]

    x_coords = [pt[0] for pt in [tl, tr, bl, br]]
    x_pos = [x for x in x_coords if x > 0]
    x_neg = [x for x in x_coords if x < 0]

    y_coords = [pt[1] for pt in [tl, tr, bl, br]]
    y_pos = [y for y in y_coords if y > 0]
    y_neg = [y for y in y_coords if y < 0]

    right_bound = max(x_pos)
    left_bound = min(x_neg)
    top_bound = max(y_pos)
    bot_bound = min(y_neg)

    new_w = int(abs(right_bound - left_bound))
    new_h = int(abs(top_bound - bot_bound))
    new_image_size = (new_w, new_h)

    new_midx = new_w * 0.5
    new_midy = new_h * 0.5

    dx = int(new_midx - w2)
    dy = int(new_midy - h2)

    trans_mat = getTranslationMatrix2d(dx, dy)
    affine_mat = (np.matrix(trans_mat) * np.matrix(rot_mat))[0:2, :]
    result = cv2.warpAffine(image, affine_mat, new_image_size, flags=cv2.INTER_LINEAR)

    return result

# Get user supplied values
        
def findFace(img):
    
    detector = dlib.get_frontal_face_detector()
    
    orgImg = img
    gray = orgGray = cv2.cvtColor(orgImg, cv2.COLOR_BGR2GRAY)
    
    angles = (0, 5, -5, 10, -10, 15, -15, 30, -30, 45, -45, 70, -70, 90, -90)
    
    for i in range(0, len(angles)):
        dets = detector(gray, 1)
    
        if len(dets)==1:
            break
        
        nextIndex = i+1
        if nextIndex<len(angles):
            #cv2.imshow("Faces found", gray)
            #cv2.waitKey(0)
            gray = rotateImage(orgGray, angles[nextIndex])
    
    if len(dets)==1:
        img = rotateImage(orgImg, angles[i])
        for k, d in enumerate(dets):
            #cv2.rectangle(img, (d.left(), d.top()), (d.right(), d.bottom()), (0, 255, 0), 2)
            img = img[max(d.top(),0):d.bottom(),max(d.left(),0):d.right()]
        
        img = cv2.resize(img, (128,128))
        
        return img
        #cv2.imwrite(outputDir + imgName, img)
        #cv2.imshow("Faces found", img)
        #cv2.waitKey(0)

    return None
        
def loadImageSaveFace(directory, imgName, outputDir):
    
    imagePath = directory + imgName
    
    if not os.path.isfile(imagePath):
        return None

    faceImg = findFace(cv2.imread(imagePath))
    if faceImg is not None:
        cv2.imwrite(outputDir + imgName, faceImg)

if __name__ == "__main__":

    #imgDir = "../TinderTrainingData/women/"
    #foundLocation = "../FoundFaces/"
    #imgDir = "../UserTrainingData/"
    #foundLocation = "../UserFoundFaces/"
    imgDir = "../AutoLabeledData/"
    foundLocation = "../AutoLabeledData/Faces/"
    #imgName = sys.argv[1]
    cascPath = sys.argv[2]
    #imagePath = imgDir + imgName
    
    files = [f for f in os.listdir(imgDir) if f[-3:] == "jpg"]
    #for filename in not_found:
    for filename in files:
        #findFace(imgDir, filename, cascPath)
        loadImageSaveFace(imgDir, filename, foundLocation)
