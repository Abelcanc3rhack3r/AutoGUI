#parses the relative locator identifier (xpath)
from dataclasses import dataclass

import utils
import buttonRecognizer
#e.g "Copy", left of "Paste" and below "Toolbar"
KEYWORDS=["left of", "right of","below", "above"]
AXIAL_WEIGHT=1
DISTANCE_WEIGHT=1

def filter_orient(orient, boxd, tupes):
    filt=None
    if(orient=="l"):
        filt= [ tup for tup in tupes if tup[1].midX< boxd.midX]
    if (orient == "r"):
        filt = [tup for tup in tupes if tup[1].midX > boxd.midX]
    if (orient == "t"):
        filt = [tup for tup in tupes if tup[1].midY < boxd.midY]
    if (orient == "b"):
        filt = [tup for tup in tupes if tup[1].midY > boxd.midY]
    return filt
def score_name(name, box):
    #score = 1E6
    loss= utils.levenshtein(name, box.text)
    if(loss>buttonRecognizer.Rect.MIN_EDIT_DIST):
        loss= 1E6
    loss*=buttonRecognizer.Rect.NAME_LOSS

    return loss
def score_orient(orient, subject_box, query_box):
    score=1E6
    dx= abs(subject_box.midX-query_box.midX)
    dy = abs(subject_box.midY - query_box.midY)
    AL=buttonRecognizer.Rect.ALIGN_LOSS
    if (orient == "l"):
        score= AL*dy + dx
    if (orient == "r"):
        score= AL*dy + dx
    if (orient == "t"):
        score = AL * dx + dy
    if (orient == "b"):
        score = AL * dx + dy
    return score

import math
def axis_score(subject_box, query_box):
    dx = abs(subject_box.midX - query_box.midX)
    dy = abs(subject_box.midY - query_box.midY)
    angle1= abs(math.atan(dy/(dx+0.01))*(180/3.141))
    angle2 = abs(math.atan(dx / (dy+0.01)) * (180 / 3.141))
    #if(dx/dy)
    return max(angle1, angle2)
def total_score(subject_box, query_box):
    r= buttonRecognizer.Rect
    axial_loss= axis_score(subject_box, query_box)
    distance_loss= subject_box.distance(query_box)
    return AXIAL_WEIGHT*axial_loss+ DISTANCE_WEIGHT*distance_loss
def classify_orient(subject_box, query_box):
    dx = (subject_box.midX - query_box.midX)
    dy = (subject_box.midY - query_box.midY)

    if(abs(dx)>abs(dy)):
        #subject box is in same row as query box
        if(dx>0):
            return "right of"
        if (dx <= 0):
            return "left of"
    if (abs(dx) <=abs(dy)):
        # subject box is in same row as query box
        if (dy > 0):
            return "below"
        if (dy <= 0):
            return "above"



@dataclass
class ScoreObj:
    rect: buttonRecognizer.Rect
    name_loss:float =0
    pos_losses:float=0


def isName(name):
    return True


def parse(string, boxes, verbose=False):
    def find_kw(com):
        for kw in KEYWORDS:
            if(kw in com):
                return kw
        return None
    def find_kw_before(com):
        kws=[]
        com = string.find(com)
        for kw in KEYWORDS:
            ind= string.find(kw, 0, com)
            if(ind!=-1):
                kws.append((ind, kw))
        if(len(kws)>0):

            maxe= max(kws)[1]
            return maxe
        return None


    strb=string

    #for kw in KEYWORDS:
        #strb= strb.replace(kw, "[]")
    coms= strb.split(",")
    scores=[]
    for box in boxes:
        dataobj= ScoreObj(box)
        scores.append(dataobj)
    name = coms[0]
    name= name.strip()
    if(isName(name)):
        #score all the objects in the field for name
        for obj in scores:
            obj.name_loss= score_name(name,obj.rect)
            if(verbose):
                print("name loss for ", obj.rect.text, ":", obj.name_loss)

    for c in coms:
        assoc_kw= find_kw(c)
        if(assoc_kw is None):
            continue
        if(verbose):
            print("parse command ", assoc_kw, ":", c)
        subject_box_name = c.replace(assoc_kw, "").strip()
        subject_boxes = [(utils.levenshtein(box.text, subject_box_name)*buttonRecognizer.Rect.NAME_LOSS,box) for box in boxes]
        subject_boxes = [tup for tup in subject_boxes if tup[0] <= buttonRecognizer.Rect.MIN_EDIT_DIST*buttonRecognizer.Rect.NAME_LOSS]
        if("left" in assoc_kw):
            for obj in scores:
                rect = obj.rect
                rights= filter_orient("r", rect, subject_boxes)
                if(len(rights)==0):
                    obj.pos_losses=1E6
                    continue
                else:
                    orients = [score_orient("l", rect, right[1] )+right[0] for right in rights]
                    obj.pos_losses+= min(orients)
        if ("right" in assoc_kw):
            for obj in scores:
                rect = obj.rect
                lefts = filter_orient("l", rect, subject_boxes)
                if (len(lefts) == 0):
                    obj.pos_losses = 1E6
                    continue
                else:
                    orients = [score_orient("r", rect, left[1])+left[0] for left in lefts]
                    obj.pos_losses += min(orients)
        if ("above" in assoc_kw):
            for obj in scores:
                rect = obj.rect
                belows = filter_orient("b", rect, subject_boxes)
                if (len(belows) == 0):
                    obj.pos_losses = 1E6
                    continue
                else:
                    orients = [score_orient("t", rect, below[1])+below[0] for below in belows]
                    obj.pos_losses += min(orients)
        if ("below" in assoc_kw):
            for obj in scores:
                rect = obj.rect
                aboves = filter_orient("t", rect, subject_boxes)
                if (len(aboves) == 0):
                    obj.pos_losses = 1E6
                    continue
                else:
                    orients = [score_orient("b", rect, above[1]) +above[0] for above in aboves]
                    obj.pos_losses += min(orients)
    passed= [score for score in scores if score.pos_losses<1E6]
    if(len(passed)>0):
        most_likely = min(passed, key = lambda d: d.name_loss+ d.pos_losses)
        return most_likely.rect












