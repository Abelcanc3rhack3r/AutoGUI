import copy
import math
from dataclasses import dataclass
import numpy as np
from PIL import Image
import pytesseract
from pytesseract import Output
import pyautogui
import cv2
import utils
import time
MIN_CONF=0
# print(pytesseract.image_to_data(Image.open('planet.png')))
pytesseract.pytesseract.tesseract_cmd = r'.\Tesseract-OCR\tesseract'
screenshot = cv2.imread("sample.png")
current_application="google sheets"
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
        newbox.vicinity= get_vicinity(newbox,image)
        return newbox

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
    def draw_vicinity(self):
        cv2.imshow(self.text, self.vicinity)
        cv2.waitKey(0)
        cv2.destroyAllWindows()




        def get_neighbours(orient, boxes):


            filterboxes= None
            if(orient == "l"):
                filterboxes= [box for box in boxes if box.x<self.x]

                def dist(box):
                    dx= abs(box.midX-self.midX)
                    dy = abs(box.midY-self.midY)
                    loss= dx+ dy*ALIGN_LOSS
                    return loss
            if (orient == "r"):
                filterboxes = [box for box in boxes if box.x > self.x]
                def dist(box):
                    dx= abs(box.midX-self.midX)
                    dy = abs(box.midY-self.midY)
                    loss= dx+ dy*ALIGN_LOSS
                    return loss
            if (orient == "t"):
                filterboxes = [box for box in boxes if box.y < self.y]
                def dist(box):
                    dx= abs(box.midX-self.midX)
                    dy = abs(box.midY-self.midY)
                    loss= dy+ dx*ALIGN_LOSS
                    return loss
            if (orient == "b"):
                filterboxes = [box for box in boxes if box.y > self.y]
                def dist(box):
                    dx= abs(box.midX-self.midX)
                    dy = abs(box.midY-self.midY)
                    loss= dy+ dx*ALIGN_LOSS
                    return loss
            filterboxes.sort(key = dist)













    #def get_neighbours(self, verbose=False):





            #get top, bottom , left and right texts and get their approx location relative to element
            #TOP
            # get closest neighbours



def get_vicinity(box, image, verbose=False):
    #cuts out the vicinity of the box, expected to be the same if the text is right
    margin= Rect.VICINITY_MARGIN
    vic= int(max(box.x-margin,0 )), int(max(box.y-margin ,0)), int(box.x+box.width+ margin), int(box.y+box.height+margin)


    clip= image[vic[1]: vic[3], vic[0]:vic[2]]
    #box.vicinity= clip
    if(verbose):
        cv2.imshow("vicinity"+ box.text, clip)
        cv2.waitKey(0)
    return clip


def match_vicinity(query, subject):
    #def pad_row()
    #matches the vicinity of the query box with the subject box to confirm its the same button
    #  if more than X% of the vicinity of the box has an MSE of less than Y
    #pad query if query is larger than subject
    qv= query.vicinity
    sv=subject.vicinity
    if(qv.shape[0]< sv.shape[0] or qv.shape[1]< sv.shape[1]):
        #qv= np.pad(qv, (0,sv.shape[0]-qv.shape[0],0,sv.shape[1]-qv.shape[1]))
        #pad row
        qv =cv2.copyMakeBorder(qv,0,(sv.shape[0]- qv.shape[0]), 0, (sv.shape[1]- qv.shape[1]),cv2.BORDER_CONSTANT)

       # z= np.zeros((qv.shape[1],))
       # s= (z,)*(sv.shape[0]-qv.shape[0])
      #  qv= np.vstack((qv,)+s)
        #pad cols
      #  z = np.zeros((qv.shape[0],))
      #  s = (z,) * (sv.shape[1] - qv.shape[1])
      #  qv = np.hstack((qv,) + s)

    elif (qv.shape[0] > sv.shape[0] or qv.shape[1] > sv.shape[1]):
        #sv= np.pad(sv, (qv.shape[0]-sv.shape[0],qv.shape[1]-sv.shape[1]))
        sv = cv2.copyMakeBorder(sv, 0, (qv.shape[0] - sv.shape[0]), 0, (qv.shape[1] - sv.shape[1]),cv2.BORDER_CONSTANT)
    mse_conv= utils.mse(qv, sv)
    filt= mse_conv [0]<= Rect.MIN_MSE
    h, w = subject.vicinity.shape[:2]
    area_prop= np.sum(filt)/ (h*w)
    return area_prop> Rect.MIN_PERCENT_AREA_SIMILAR
def take_screenshot():
    im1 = pyautogui.screenshot()
    cvim= utils.PILtoCV2(im1)
    cvim= cvim[:,0:300]
    return cvim


def change_focus_click(x,y):
    print("click1")
    pyautogui.click(x, y)
    time.sleep(5)
    print("click2")
    pyautogui.click(x, y)




def click_button(text, verbose=False):
    def loop_buttons(screen_buttons):
        for box in screen_buttons:
            btext = box.text
            match = utils.levenshtein(btext, text)
            #if (verbose):
                #print("match button text: btext:", btext, " to query:", text)
            if (match <= Rect.MIN_EDIT_DIST):
                matching_buttons.append((match, box))
        matching_buttons.sort(key=lambda tup: tup[0])
        if (len(matching_buttons) > 1):

            # if there exists a button with the same text in the application registry,
            # then click the button which has a registry item that is most similar to it
            regs = Rect.find_buttons_by_name(text)
            if (verbose):
                print("matching regs:", [box.text for box in regs])
            for edit, mbox in matching_buttons:
                if (verbose):
                    print(" button", mbox.text, "matches command text:", text)
                vicinity = get_vicinity(mbox, image, False)
                for reg in regs:
                    if (match_vicinity(mbox, reg)):
                        if (verbose):
                            print(mbox.text, "matches the vicinity of ", reg.text, "click on it")
                            print("click:", mbox.midX, mbox.midY)
                        return mbox
            else:
                # ask the user for more info on which button to click
                pass
                # TODO
        elif (len(matching_buttons) == 1):

            mbox = matching_buttons[0][1]
            if (verbose):
                print("only one button,", mbox.text, " matches the text description")
                #mbox.draw_box(imshow=True)
            return mbox
        return None
    #returns the screen coordinates of the button containing text
    image= take_screenshot()
    matching_buttons=[]
    screen_buttons= get_text_boxes(image,verbose=True,callerd="find "+text)
    button=loop_buttons(screen_buttons)
    if(not button):
        expanded_buttons=  Rect.merge_all_textboxes(screen_buttons,image)
        button=loop_buttons(expanded_buttons)
    if(button):

        change_focus_click(button.midX, button.midY)

        return button









def get_text_boxes(screenshot, verbose=False, callerd=""):
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
            rect.vicinity = get_vicinity(rect, screenshot, False)
            rects.append(rect)
        # show the output image

            if(verbose and len(text)>0):
                cv2.rectangle(image1, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(image1, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (0, 0, 255), 1)
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


def parse_command (command):
    #CLICK <BUTTON NAME>
    if ("click " in command):
        clickstr= command.replace("click","")
        clickstr=clickstr.strip()
        click_button(clickstr, True)

run_script="click Edit \n click Find"

def test_loop():
    #screenshot=take_screenshot()
    Rect.rects[current_application] = get_text_boxes(screenshot, False)
    #print("StRA")
    #Rect.merge_all_textboxes(Rect.rects[current_application],image=screenshot,verbose=True)
    #parse_command("click Untitled spreadsheet")
    coms=run_script.split("\n")
    for com in coms:
        parse_command(com)
#test_loop()




def template_matching_OCR(img, verbose=False):
    # matches all the characters in theimage using template matching
    boxes = pytesseract.image_to_boxes(img)
    hImg, wImg, _ = img.shape
    chrs=[]
    for b in boxes.splitlines():
        b = b.split(' ')

        x, y, w, h = int(b[1]), int(b[2]), int(b[3]), int(b[4])
        if(True):
            #print(b)
            cv2.rectangle(img, (x, hImg - y), (w, hImg - h), (50, 50, 255), 1)
            cv2.putText(img, b[0], (x, hImg - y + 13), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (50, 205, 50), 1)


        print(x,hImg-h,w-x,(hImg - y)-(hImg - h))
        chrs.append(Rect(x,hImg-h,w-x,(hImg - y)-(hImg - h),b[0]))
    #if(verbose):
    cv2.imshow('Detected text', img)
    cv2.waitKey(0)
    #join chrs box into words

    def get_overlapping(x1, x2, y1, y2):
        if(x2> y1 and x1< y2):
            return x2- y1
        if (y2 > x1 and y1 < x2):
            return y2 - x1
        return 0

        return abs(max(x1, y1) - min(x2, y2))
    def is_adjacent(box1, box2,image=None):
        #two charboxes are adjacent if the x distance between 2 is less than x% of their sum width
        #also, if their y ranges overlap
        pwidth=2
        pheight=0.9
        dx= min(abs(box1.x+box1.width- box2.x), abs(box2.x+box2.width- box1.x))
        #print("merge ", box1.text, box2.text)

        if(image is not None):
            box1.draw_box(image=image, windowname="merge")
            box2.draw_box(image=image, windowname="merge")
            cv2.imshow("merge",image)
            cv2.waitKey(0)
        #print()
        awidth = (box1.width+box2.width)/(len(box1.text)+len(box2.text))
        aheight= min(box1.height, box2.height)
        yoverlap= get_overlapping(box1.y, box1.y+box1.height, box2.y, box2.y+box2.height)
        #print(dx, "<", awidth * pwidth, yoverlap, ">=", pheight * aheight)
        if(dx<= awidth*pwidth and yoverlap >=pheight*aheight) :
            return True
        return False
    def merge_boxes(box1, box2):
        newx= min(box1.x, box2.x)
        newy= min(box1.y, box2.y)
        newx2 = max(box2.x+box2.width, box1.x+box1.width)
        newy2 = max(box2.y + box2.height, box1.y + box1.height)
        neww, newh= newx2- newx, newy2-newy
        if(box1.x<=box2.x):
            text = box1.text+box2.text
        else:
            text=box2.text+box1.text
        return Rect(newx, newy, neww, newh, text= text)
    dimage=screenshot
    def merge_all_boxes(boxes, verbose=False,image=None):
        image= np.copy(dimage)
        for b1 in boxes:
            for b2 in boxes:
                if(b1!=b2):
                    if(is_adjacent(b1,b2, None)):
                        newb= merge_boxes(b1, b2)
                        boxes.remove(b1)
                        boxes.remove(b2)
                        boxes.append(newb)
                        #if(verbose):
                            #print("merged ", b1.text, b2.text, "->", newb.text)
                            #b1.draw_box(image=image, windowname="merge" )
                            #b2.draw_box(image=image, windowname="merge" ,imshow=True)
                            #newb.draw_box(image=image, windowname="merge",imshow=True)
                        merge_all_boxes(boxes, verbose)
                        return
        return

    merge_all_boxes(chrs, verbose=True, image=screenshot)
    if(verbose):
        for chr in chrs:
            chr.draw_box(image=screenshot, windowname="merge",imshow=False)
            #cv2.imshow("merge", screenshot)
            #cv2.waitKey(0)
#get_text_boxes(screenshot, verbose=True)
#template_matching_OCR(screenshot,verbose=True)
import extractChars

#rects=get_text_boxes(screenshot, verbose=False, callerd="")
#extractChars.extract_chars(screenshot, rects)