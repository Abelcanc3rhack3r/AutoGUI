import cv2
import imutils
import numpy as np

radius=25

MIN_AREA=25
# max ratio does not apply if area of child contour is less than MIN_AREA
MAX_RATIO=10
#area of the parent contour to the child contour , if the ratio is bigger than MAX_RATIO, then the child
#contour will be considered as icon
def crop_at_mouse(img, mousex, mousey, radius=50):
    t = max(0, mousey - radius)

    b = min(img.shape[0], mousey + radius)

    l = max(0, mousex - radius)

    r = min(img.shape[1], mousex + radius)
    mousex= mousex-l
    mousey=mousey-t
    return img[t:b, l:r],(mousex,mousey)
radius=50

def get_mouse_loc(event, x, y, flags, param):
    global mousex, mousey
    img=param["img"]
    if event == cv2.EVENT_LBUTTONDOWN:
        mousex, mousey = x, y
        print(mousex, mousey)
        c,mouse_pt=crop_at_mouse(img,mousex,mousey,radius)
        get_all_icons(c,mouse_pt)
        cv2.imshow("cropped",c)
        cv2.waitKey(0)



def get_mouse_loc_img(img, radius=50):
    global mousex, mousey
    cv2.namedWindow('image')
    cv2.setMouseCallback('image', get_mouse_loc,param={"img":img})
    while (1):
        cv2.imshow('image', img)
        k = cv2.waitKey(20) & 0xFF
        if k == 27:
            break
    cv2.destroyAllWindows()


def get_all_icons(img, mouse_point):
    img1 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img1 = cv2.Canny(img1, 50, 150)
    # find contours in image
    cnts,hierarchy = cv2.findContours(img1.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #cnts = imutils.grab_contours(cnts)


    # list all contours containing the mouse_point
    contours_list = []
    for c in cnts:
        if cv2.pointPolygonTest(c, mouse_point, False) >= 0:
            contours_list.append(c)

    # find the smallest contour in the list
    min_area = 1e6
    min_c=None
    for c in contours_list:
        if cv2.contourArea(c) < min_area:
            min_area = cv2.contourArea(c)
            min_c = c

    # draw the smallest contour
    imgc=img.copy()
    cv2.drawContours(imgc, [min_c], -1, (0, 255, 0), 2)
    cv2.imshow("smallest contour containing pt", imgc)
    cv2.waitKey(0)
    # find the index of min_c in cnts
    for i in range(len(cnts)):
        if cnts[i] == min_c:
            min_c_index = i

    while (True):

        hier_min_c = hierarchy[0][min_c_index]
        # get the parent of min_c
        parent_index = hier_min_c[3]
        if (parent_index == -1):
            break
        par = cnts[parent_index]
        # draw the parent contour
        image = img.copy()
        cv2.drawContours(image, [par], -1, (0, 255, 0), 2)
        cv2.imshow("parent contour", image)
        cv2.waitKey(0)
        # find the area of min_c
        min_area = cv2.contourArea(min_c)
        # find the area of parent contour
        parent_area = cv2.contourArea(par)
        # find the ratio of the area of parent to min_c, if bigger than MAX_RATIO, break
        if parent_area / min_area > MAX_RATIO and min_area > MIN_AREA:
            break
        # find the index of par in cnts
        for i in range(len(cnts)):
            if cnts[i] == par:
                par_index = i
        min_c_index = par_index


def test():
    img= cv2.imread("sample desktop2.png")
    get_mouse_loc_img(img, radius=50)
test()