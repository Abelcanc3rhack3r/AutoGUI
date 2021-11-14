

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






