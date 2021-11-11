import cv2
import imutils
import numpy as np

radius=25

MIN_AREA=25
# max ratio does not apply if area of child contour is less than MIN_AREA
MAX_RATIO=10000
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

ICON_LIBRARY={}
def get_mouse_loc(event, x, y, flags, param):
    global mousex, mousey
    img=param["img"]
    if event == cv2.EVENT_LBUTTONDOWN:
        mousex, mousey = x, y
        print(mousex, mousey)
        c,mouse_pt=crop_at_mouse(img,mousex,mousey,radius)
        large_image=c
        midx = int(radius / 2)
        midy = int(radius / 2)
        matched_image=None
        # loop through all bitmaps in ICON_LIBRARY
        for k, small_image in ICON_LIBRARY.items():
            method = cv2.TM_SQDIFF_NORMED
            result = cv2.matchTemplate(small_image, large_image, method)
            # We want the minimum squared difference
            mn, _, mnLoc, _ = cv2.minMaxLoc(result)

            # Draw the rectangle:
            # Extract the coordinates of our best match
            MPx, MPy = mnLoc
            # Step 2: Get the size of the template. This is the same size as the match.
            trows, tcols = small_image.shape[:2]
            # Step 3: Draw the rectangle on large_image
            rect = (MPx, MPy, MPx + tcols, MPy + trows)
            # check if midx and midy are in rect
            if MPx < midx < MPx + tcols and MPy < midy < MPy + trows:
                print("mouse is in icon")
                cv2.rectangle(large_image, (MPx, MPy), (MPx + tcols, MPy + trows), (0, 0, 255), 2)
                # Display the original image with the rectangle around the match.
                cv2.imshow('output', large_image)
                cv2.waitKey(0)
        clicked_icon=get_all_icons(c,mouse_pt)
        if(clicked_icon is not None):
            cv2.imshow("you clicjed on an icon",clicked_icon)
            cv2.waitKey(0)
        #give a name to the clicked icon
            name="icon"+ len(ICON_LIBRARY)
            ICON_LIBRARY[name]=clicked_icon
            cv2.destroyWindow("you clicjed on an icon")




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


def get_all_icons(img, mouse_point, verbose=False):
    img1 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img1 = cv2.GaussianBlur(img1, (0, 0), 3)
    img1 = cv2.Canny(img1, 1, 10)

    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))
    img1 = cv2.morphologyEx(img1, cv2.MORPH_DILATE, kernel)

    # find contours in image
    cnts, hierarchy = cv2.findContours(img1.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # cnts = imutils.grab_contours(cnts)
    # cv2.drawContours(img, cnts, -1, (0, 255, 0), 1)
    if (verbose):
        cv2.imshow("edges", img1)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

    # list all contours containing the mouse_point
    contours_list = []
    for c in cnts:
        if cv2.pointPolygonTest(c, mouse_point, False) >= 0:
            contours_list.append(c)
    if (len(contours_list) == 0):
        return None
    # find the smallest contour in the list
    min_area = 1e6
    min_c = None
    for c in contours_list:
        if cv2.contourArea(c) < min_area:
            min_area = cv2.contourArea(c)
            min_c = c

    # draw the smallest contour
    if (verbose):
        imgc = img.copy()

        cv2.drawContours(imgc, [min_c], -1, (0, 255, 0), 2)
        cv2.imshow("smallest contour containing pt", imgc)
    # find the index of min_c in cnts
    for i in range(len(cnts)):
        if np.array_equal(cnts[i], min_c):
            min_c_index = i
    # x=0
    for ii in range(0, 100):

        hier_min_c = hierarchy[0][min_c_index]
        # get the parent of min_c
        parent_index = hier_min_c[3]
        if (parent_index == -1):
            print("no more parents")
            par = hier_min_c
            break
        par = cnts[parent_index]
        # draw the parent contour
        if (verbose):
            image = img.copy()
            cv2.drawContours(image, [par], -1, (0, 255, 0), 2)
            # cv2.destroyALlWindows
            cv2.imshow("parent contour", image)
            # cv2.waitKey(0)
        # find the area of min_c
        min_area = cv2.contourArea(min_c)
        # find the area of parent contour
        parent_area = cv2.contourArea(par)
        # find the ratio of the area of parent to min_c, if bigger than MAX_RATIO, break
        print("area ratio", parent_area / min_area, MAX_RATIO)
        if parent_area / min_area > MAX_RATIO and min_area > MIN_AREA:
            break
        # find the index of par in cnts
        for i in range(len(cnts)):
            if np.array_equal(cnts[i], par):
                par_index = i
        min_c_index = par_index
    # get the bounding box of par
    bb = cv2.boundingRect(par)
    # draw the bounding box
    if (verbose):
        img_bb = img.copy()
        cv2.rectangle(img_bb, (bb[0], bb[1]), (bb[0] + bb[2], bb[1] + bb[3]), (0, 255, 0), 2)
        cv2.imshow("bounding box", img_bb)
    # cv2.waitKey(0)
    # crop the bounding box
    img_crop = img[bb[1]:bb[1] + bb[3], bb[0]:bb[0] + bb[2]]
    if (verbose):
        cv2.imshow("cropped image", img_crop)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return img_crop

def test():
    ICON_LIBRARY["icon1"]= cv2.imread("test icon.png")
    img= cv2.imread("sample desktop2.png")
    get_mouse_loc_img(img, radius=50)
test()