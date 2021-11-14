import re

import pyautogui
from AutoGUI.cv import elementDetect
from AutoGUI.cv import textRecognizer



TEXTBOXES= {}
ICONS={}

def click(screenshot,btnToClick):
    for btnName, btn in elementDetect.ICON_LIBRARY.items():
        if(btnName == btnToClick):
            rect= elementDetect.icon_on_screen(screenshot, btn)
            if(rect):
                print("rect detected on screen")




def loop():
    global ICONS
    global TEXTBOXES


    screenshot= pyautogui.screenshot()

    for btnName, btn in elementDetect.ICON_LIBRARY.items():
        rect = elementDetect.icon_on_screen(screenshot, btn)
        if (rect):
            ICONS[btnName]=btn
    #detect all the textboxes in image
    TEXTBOXES = textRecognizer.scan_image(screenshot)


coms = ["click", "type"]


def execute(script):
    # split script into lines
    lines = script.split('\n')
    # remove comments
    lines = [line for line in lines if not line.startswith('#')]
    # remove empty lines
    lines = [line for line in lines if line]
    # remove leading and trailing whitespace
    lines = [line.strip() for line in lines]

    for line in lines:
        loop()
        for com in coms:
            if (com in line):
                # extract the string in brackets

                if (com == "click"):
                    string = re.search(r'\((.*?)\)', line).group(1)
                    print("execuuted:",string)
                    click(string)
                if (com == "type"):
                    string = re.search(r'\((.*?)\)', line).group(1)
                    print("executed:",string)
                    type(string)





def click(btn_name):
    def contains(text, lis):
        # return the element in lis that contains text
        for item in lis:
            if (text in item):
                return item
        return None
    try:
        #pyautogui click
        ele=contains(btn_name,TEXTBOXES.keys())
        if (ele is not None):
                midx,midy = TEXTBOXES[ele].midX, TEXTBOXES[ele].midY
                pyautogui.click(midx,midy)
        ele = contains(btn_name, ICONS.keys())
        if (ele is not None):
            midx, midy = ICONS[ele].midX, ICONS[ele].midY
            pyautogui.click(midx, midy)
    except:
        print("button not found")


def type(string):
    pyautogui.typewrite(string)



def test():
    script="click (Google)"
    execute(script)

if __name__ == '__main__':
    test()


'''
def loop_buttons(screen_buttons):
        for box in screen_buttons:
            btext = box.text
            #match = utils.levenshtein(btext, text)
            match=""
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
'''