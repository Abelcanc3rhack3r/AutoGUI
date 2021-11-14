import copy
import math
from dataclasses import dataclass
import numpy as np
from PIL import Image
import pytesseract
from pytesseract import Output

import cv2
#import utils
#logger
import time
MIN_CONF=0
# print(pytesseract.image_to_data(Image.open('planet.png')))
pytesseract.pytesseract.tesseract_cmd = r'..\Tesseract-OCR\tesseract'

@dataclass
class Neighbour:
        dx:int
        dy:int
        text:str
@dataclass
class Rect:

    ALIGN_LOSS = 10
    NAME_LOSS=1E5
    MERGE_TEXTBOX_XDIST=20
    MERGE_TEXTBOX_YDIST = 20
    MIN_EDIT_DIST = 1
    VICINITY_MARGIN= 30
    MIN_MSE=10
    MIN_PERCENT_AREA_SIMILAR=0.8
    rects= {}
    MIN_NEIGHBOURS=1
    MIN_DISTANCE=10
    x:int
    y:int
    width:int
    height:int
    text:str
    vicinity=None
    neighbours=[]
    def offset(self, x,y):
        self.x+=x
        self.y+=y
    @property
    def midX(self):
        return int(self.x + self.width/2)
    @property
    def midY(self):
        return int(self.y + self.height /2)

    def distance(self, rect):
        dx= self.x- rect.x
        dy = self.y- rect.y
        dist= math.sqrt(dx*dx+dy*dy)
        return dist
    @staticmethod
    def find_buttons_by_name(text, application=""):
        matches=[]
        for app in Rect.rects:
            for btn in Rect.rects[app]:
                ed=utils.levenshtein(btn.text, text)
                if(ed<=Rect.MIN_EDIT_DIST):
                    matches.append((ed, btn))
        matches.sort(key=lambda tup:tup[0])
        matchd= [ tup[1] for tup in matches]
        return matchd









    #group text boxes that are side by side onto one large button

    @staticmethod
    def is_beside(box1, box2):
        # both the top and the bottom of the buttons must be aligned to merge
        dy1= abs(box1.y-box2.y)
        dy2 = abs((box1.y+box1.height) - (box2.y+box2.height) )

        dx1= abs((box2.x ) -(box1.x+box1.width ))
        dx2 = abs((box1.x) - (box2.x + box2.width))
        dx=min(dx1,dx2)
        if(max(dy1,dy2)<=Rect.MERGE_TEXTBOX_YDIST and dx<= Rect.MERGE_TEXTBOX_XDIST):
            return True
        return False

    @staticmethod
    def is_beside_y(box1, box2):
        # both the left and the right of the buttons must be aligned to merge
        dx1 = abs(box1.x - box2.x)
        dx2 = abs((box1.x + box1.width) - (box2.x + box2.width))

        dy1 = abs((box2.y) - (box1.y + box1.height))
        dy2 = abs((box1.y) - (box2.y + box2.height))
        dy = min(dy1, dy2)
        if (max(dx1, dx2) <= Rect.MERGE_TEXTBOX_XDIST and dy <= Rect.MERGE_TEXTBOX_YDIST):
            return True
        return False

    @staticmethod
    def merge_textbox_y(box1, box2, image):
        l = min(box1.x, box2.x)
        t = min(box1.y, box2.y)
        r = max(box1.x + box1.width, box2.x + box2.width)
        b = max(box1.y + box1.height, box2.y + box2.height)
        if (box1.y <= box2.y):
            text = box1.text + " " + box2.text
        else:
            text = box2.text + " " + box1.text

        newbox = Rect(l, t, r - l, b - t, text)
        #newbox.vicinity = Rect.get_vicinity(newbox, image)
        return newbox
    @staticmethod
    def merge_textbox(box1, box2,image):
        l = min(box1.x, box2.x)
        t= min(box1.y, box2.y)
        r= max(box1.x+box1.width, box2.x+box2.width)
        b= max(box1.y+box1.height, box2.y+box2.height)
        if(box1.x<= box2.x):
            text= box1. text +" "+ box2.text
        else:
            text = box2.text + " " + box1.text

        newbox= Rect(l, t,r-l,b-t, text)
        #newbox.vicinity= Rect.get_vicinity(newbox,image)
        return newbox
    def get_vicinity(box, image, verbose=False):
        # cuts out the vicinity of the box, expected to be the same if the text is right
        margin = Rect.VICINITY_MARGIN
        vic = int(max(box.x - margin, 0)), int(max(box.y - margin, 0)), int(box.x + box.width + margin), int(
            box.y + box.height + margin)

        clip = image[vic[1]: vic[3], vic[0]:vic[2]]
        # box.vicinity= clip
        if (verbose):
            cv2.imshow("vicinity" + box.text, clip)
            cv2.waitKey(0)
        return clip

    @staticmethod
    def merge_all_textboxes(boxes,image,  verbose=False):
        addeds=[]
        def doubleiter(copiedlist):
            print("double iter round \n\n")
            for bx1 in copiedlist:
                for bx2 in copiedlist:
                    if(bx1==bx2):
                        continue
                    if(verbose and "Untitled" in bx1.text):
                        #bx2.draw_vicinity()

                        print(bx1.text , " is beside ", bx2.text, Rect.is_beside(bx1,bx2))
                    if(Rect.is_beside(bx1,bx2)):
                        merged_box= Rect.merge_textbox(bx1,bx2,image)
                        copiedlist.append(merged_box)
                        addeds.append(merged_box)
                        if(verbose):
                            print("merge ", bx1. text, " and ", bx2.text)
                        copiedlist.remove(bx1)
                        copiedlist.remove(bx2)
                        return True
                    elif (Rect.is_beside_y(bx1,bx2)):
                        merged_box= Rect.merge_textbox_y(bx1,bx2,image)
                        copiedlist.append(merged_box)
                        addeds.append(merged_box)
                        if(verbose):
                            print("merge ", bx1. text, " and ", bx2.text, "top")
                        copiedlist.remove(bx1)
                        copiedlist.remove(bx2)
                        return True
            return False
        #recursively loops through all boxes and merges textboxes that are near each other until there are none.
        copiedlist = copy.copy(boxes)
        copiedlist= [box for box in copiedlist if len(box.text)>0]
        while(doubleiter(copiedlist)):
            pass

        for bx in addeds:
            if(bx not in boxes):
                boxes.append(bx)
        if(verbose):

            for box in addeds:
                dbimg = image.copy()
                box.draw_box(dbimg)
                cv2.imshow("merged", dbimg)
                cv2.waitKey(0)
        return boxes










    @staticmethod
    def _distance(pt1, pt2):
        dx= pt1[0] - pt2[0]
        dy = pt1[1] - pt2[1]
        dist= math.sqrt(dx*dx+dy*dy)
        return dist
    @staticmethod
    def compare_neighbours(query, other, allRects, verbose=False):
        #see whether the neighbours of other are in the same vicninity as query
        for neigh in query.neighbours:
            neighposx, neighposy= neigh.dx+query.midX,neigh.dy+query.midY
            matchFound= False
            #loop through allRects and see if theres a RECT of similar text near the predicted location
            for rect in allRects:
                dist = Rect._distance((rect.x,rect.y), (neighposx, neighposy))
                if(dist< Rect.MIN_DISTANCE):
                    #compare the texts
                    if(utils.levenshtein(query.text, rect.text)<Rect.MIN_EDIT_DIST):
                        matchFound=True
                        if(verbose):
                            print("neighbour '",rect.text ,"' \n found in vicinity of '", query.text ,"'" )
            if(not matchFound):
                if (verbose):
                    print("neighbour '", rect.text, "' not  found in vicinity of '", query.text, "'")
                return False
        return True




    @staticmethod
    def init_boxes(boxes):
        for box in boxes:
            box.neighbours= box.get_neighbours()
        Rect.rects= boxes

    def draw_box(self, image, imshow=False, windowname=""):
        x=self.x
        y=self.y
        w=self.width
        h=self.height
        text= self.text
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 0, 255), 1)
        if(imshow):
            cv2.imshow(windowname,image)
            cv2.waitKey(0)


def get_text_boxes(screenshot, verbose=False, callerd=""):
    #pil_image= image.convert('RGB')
    #open_cv_image = np.array(pil_image)
    # Convert RGB to BGR
    #open_cv_image = open_cv_image[:, :, ::-1].copy()
    image=screenshot.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # threshold the gray using local thresholding
    #gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, 30)
    #edges = cv2.Canny(gray, 100, 200)
    ret, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    rects= []
    #cv2.imshow("thresholded image",gray)
    results = pytesseract.image_to_data(gray, output_type=Output.DICT)
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
                cv2.rectangle(image1, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(image1, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (0, 0, 255), 1)
                #print("found text:", text)
                #if (verbose and "and" in text):
                    #print(rects.index(rect),":",rect.text)
                    #rect.draw_vicinity()
    if(verbose):
        #pass
        #print("write",callerd+".jpg")
        #cv2.imwrite(callerd+".jpg", image1)
        cv2.imshow("Image", image1)
        cv2.waitKey(100)
    return rects


def scan_image(img, size=(50,200), stride=50):
    #get boxes of size (sizex,sizey) every stridex, stridey of image
    #returns list of boxes
    boxes = []
    all_rects= {}
    for x in range(0, img.shape[1], stride):
        for y in range(0, img.shape[0], stride):
            box=img[y:y+size[0], x:x+size[1]]
            boxes.append(box)
            rects=get_text_boxes(box,True)
            for rect in rects:
                rect.offset(x,y)
                print(f"{rect.text} found")
                all_rects[rect.text]= rect
        break
        #break
        #show the box
            #cv2.imshow('box', img[x:x+size[0], y:y+size[1]])
            #cv2.waitKey(0)
    for rect in all_rects.values():
        print(rect)
        rect.draw_box(img)

    cv2.imshow("textboxes", img)
    cv2.waitKey(0)
    all_rects1 = {}
    textboxes = Rect.merge_all_textboxes(list(all_rects.values()), img,verbose=True)
    for rect in textboxes:
        all_rects1[rect.text] = rect

    return all_rects
run_script="click Edit \n click Find"

def test():
    #logger.set_logfield("RUN")
    #ICON_LIBRARY["icon1"]= cv2.imread("test icon 2.png")
    img= cv2.imread("../scratch/google chrome.png")
    #boxes=get_text_boxes(img,verbose=True)
    scan_image(img)
    #Rect.merge_all_textboxes(boxes, img, verbose=True)
    #scan_image(img, (50,200),50)
    #get_mouse_loc_img(img, radius=50)
if(__name__ =="__main__"):
    test()




