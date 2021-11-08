import cv2
import pyautogui
from pytesseract import pytesseract, Output
import numpy as np

import rect
import utils
from ..gui import buttonRecognizer





BTN_NUM=0
def get_all_icons(img, BTN_NUM=0):
    img1 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img1 = cv2.Canny(img1, 50, 150)
    contours, hierarchy = cv2.findContours(img1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # get contours that are smaller than 0.05 of the image size

    contours = [c for c in contours if cv2.contourArea(c) < 1 * img.shape[0] * img.shape[1]]
    # loop through contours, get bounding box and draw rectangle
    icons = []
    db = img.copy()
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        MIN_SIZE=20
        # add icon to list if icon is larger than MIN SIZE pixels

        if w > MIN_SIZE and h > MIN_SIZE:
            name= f"Button{BTN_NUM}"
            BTN_NUM+=1
            rec=buttonRecognizer.Rect(bitmap= crop, x=x,y=y, width=w, height= h, name= name)
            crop=img[y:y + h, x:x + w]
            icons.append(rec)
            # show the icon and the bounding box
            cv2.rectangle(db, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.imshow("icons", db)
    cv2.waitKey(0)
    return icons
#from windowDetector import image_in_image
library=[]
def similar_button(but1, but2):
    # if image2 is bigger than image1, call image_in_image(image1, image2), else call image_in_image(image2, image1)
    image1, image2= but1.bitmap, but2.bitmap
    try:
        if image1.size < image2.size:
            return image_in_image(image1, image2)
        else:
            return image_in_image(image2, image1)
    except:
        return False
    return False
def add_button_to_library(button):
    similar= [not similar_button(ele, button) for ele in library ]
    if(all(similar)):
        library.append(button)

def detect_icon(clip):
    kernel = np.ones((2, 2), np.uint8)
    gray = cv2.cvtColor(clip, cv2.COLOR_BGR2GRAY)
    # gray = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(gray, 30, 200)
    edged = cv2.dilate(edged, kernel, iterations=1)
    cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    print(cnts)
    # print(cnts[1][0])
    # return
    if (len(cnts[0]) > 0):
        largestcnts= sorted(cnts[0],key=lambda cnt: cv2.contourArea(cnt))
        x, y, w, h = cv2.boundingRect(largestcnts)
        MIN_SIZE = 20
        # add icon to list if icon is larger than MIN SIZE pixels

        if w > MIN_SIZE and h > MIN_SIZE:
            name = f"Button{BTN_NUM}"
            BTN_NUM += 1
            rec = buttonRecognizer.Rect(bitmap=crop, x=x, y=y, width=w, height=h, name=name)
            crop = img[y:y + h, x:x + w]
            icons.append(rec)
            # show the icon and the bounding box
            cv2.rectangle(db, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return None
def ROI(x,y):
    # find the region around the mouse when clicked, detect contours and
    #find the largest self contained contour in the region
    rwidth=50
    rheight=50
    dx=int(rwidth/2)
    dy= int(rheight/2)
    sx= max(0, x-dx)
    sy= max(0, y-dy)
    ex= min(x+dx,  pyautogui.size()[0])
    ey=min(y+dy, pyautogui.size()[1])
    screenshot=pyautogui.screenshot(region=(sx, sy, ex-sx, ey-sy))
    clip= utils.PILtoCV2(screenshot)
    kernel = np.ones((2, 2), np.uint8)
    gray = cv2.dilate(clip, kernel, iterations=1)
    #cv2.imshow("clip", clip)
    #cv2.waitKey(0)

    return detect_icon(clip)

def get_text_boxes(screenshot, verbose=False, callerd=""):
    MIN_CONF=0.9
    #pil_image= image.convert('RGB')
    #open_cv_image = np.array(pil_image)
    # Convert RGB to BGR
    #open_cv_image = open_cv_image[:, :, ::-1].copy()
    image=screenshot.copy()
    #image=open_cv_image
    rects= []
    results = pytesseract.image_to_data(screenshot, output_type=Output.DICT)
    print(results)
    image1 = image
    for i in range(0, len(results["text"])):
        # extract the bounding box coordinates of the text region from
        # the current result
        x = results["left"][i]
        y = results["top"][i]
        w = results["width"][i]
        h = results["height"][i]
        # extract the OCR text itself along with the confidence of the
        # text localization
        text = results["text"][i]
        conf = float(results["conf"][i])
        if conf > MIN_CONF and len(text)>0:
            # display the confidence and text to our terminal
           # print("Confidence: {}".format(conf))
           # print("Text: {}".format(text))
           # print("")
            # strip out non-ASCII text so we can draw the text on the image
            # using OpenCV, then draw a bounding box around the text along
            # with the text itself
            text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
            rect=Rect(x,y,w,h,text)
            #rect.vicinity = get_vicinity(rect, screenshot, False)
            rects.append(rect)
        # show the output image

            if(verbose and len(text)>0):
                rect.draw_box(image1,False)
                #cv2.rectangle(image1, (x, y), (x + w, y + h), (0, 255, 0), 2)
                #cv2.putText(image1, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                #0.5, (0, 0, 255), 1)
                print("found text:", text)
                #if (verbose and "and" in text):
                    #print(rects.index(rect),":",rect.text)
                    #rect.draw_vicinity()
    if(verbose):
        print("write",callerd+".jpg")
        #cv2.imwrite(callerd+".jpg", image1)
        cv2.imshow("Image", image1)
        cv2.waitKey(0)
    return rects


def detect_labelled_textboxes(image):
    MIN_TEXTBOX_WIDTH=50
    MIN_TEXTBOX_HEIGHT=50
    def detect_rects(img):
        # convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # apply gaussian blur
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        # apply canny edge detection
        edges = cv2.Canny(blur, 50, 150, apertureSize=3)
        # find contours
        contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        childless_rects = []
        for cnt in contours:
            # loop over contours and add contour to a list if it doesnt have any children
            #if hierarchy[0, cnt, 2] == -1:

                # check if contour is approximately a rect
                epsilon = 0.1 * cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True)
                if len(approx) == 4:

                    # check if the bounding rect of the contour is bigger than 50 x 50
                    br=cv2.boundingRect(approx)
                    if br[2] > MIN_TEXTBOX_WIDTH and br[3] > MIN_TEXTBOX_HEIGHT:
                        cv2.drawContours(img, [cnt], 0, (0, 255, 0), 2)
                        rect = Rect(x=br[0],y=br[1], width=br[2], height=br[3])
                        childless_rects.append(rect)
        return childless_rects


    def expand(rect):
        (x, y, w, h) = rect.x, rect.y, rect.width, rect.height
        margin = 25
        m = margin
        return (x - m, y - m, w + m, h + m)

    textboxes= get_text_boxes(image)
    exp_





if(__name__ =="__main__"):
    pytesseract.tesseract_cmd = r'.\Tesseract-OCR\tesseract'
    screenshot = cv2.imread("./images/icons.png")
    get_all_icons(screenshot)