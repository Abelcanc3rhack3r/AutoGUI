i
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