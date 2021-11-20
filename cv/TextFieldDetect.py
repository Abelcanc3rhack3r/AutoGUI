#detect rectangles in imaGE
import cv2


def detect_rectangles(image):
    #convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #find canny edges
    edged = cv2.Canny(gray, 30, 200)

    #find contours
    im2, cnts, hierarchy = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #sort contours
    (cnts, boundingBoxes) = sort_contours(cnts, method="top-to-bottom")

    #create array to store rectangles
    rects = []

    #loop over the contours
    for c in cnts:
        #approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        #if the approximated contour has 4 points its a rectangle
        if len(approx) == 4:
            rects.append(approx)

    #return the rectangles
    return rects

#sort contours
def sort_contours(cnts, method="left-to-right"):
    #initialize the reverse flag and sort index
    reverse = False
    i = 0

    #handle if we need to sort in reverse
    if method == "right-to-left" or method == "bottom-to-top":
        reverse = True

    #handle if we are sorting against the y-coordinate rather than
    #the x-coordinate of the bounding box
    if method == "top-to-bottom" or method == "bottom-to-top":
        i = 1

    #construct the list of bounding boxes and sort them from top to bottom
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes), key=lambda b:b[1][i], reverse=reverse))

    #return the list of sorted contours and bounding boxes
    return (cnts, boundingBoxes)

#draw rectangles on image
def draw_rectangles(image, rects):
    #loop over the rectangles
    for (x, y, w, h) in rects:
        #draw a rectangle given bbox coordinates
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    #return the image with rectangles
    return image

#main function
def main():
    #read in image
    image = cv2.imread("test_image.jpg")

    #detect rectangles
    rects = detect_rectangles(image)

    #draw rectangles
    image = draw_rectangles(image, rects)

    #show the output image
    cv2.imshow("Image", image)
    cv2.waitKey(0)

if __name__ == "__main__":
    main()