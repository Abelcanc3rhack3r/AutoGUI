from datetime import time

import cv2

import pyautogui

import utils
import detectText
screenshot= cv2.imread("sample.png")

from pynput.mouse import Listener
from ..cv import elementDetect

def detect_pressed_btn(x,y):
    screenshot = pyautogui.screenshot()
    clip = utils.PILtoCV2(screenshot)
    rects = elementDetect.get_all_icons(screenshot)
def registerMouse():
    def on_move(x, y):
        pass
        #print('Pointer moved to {0}'.format(
            #(x, y)))

    def on_click(x, y, button, pressed):
        print('{0} at {1}'.format(
            'Pressed' if pressed else 'Released',
            (x, y)))
        detect_pressed_btn(x,y)
       #ROI(x,y)
        #if not pressed:
            # Stop listener
           # return False

    def on_scroll(x, y, dx, dy):
        print('Scrolled {0}'.format(
            (x, y)))
        detect_text(x,y)
        #ROI(x, y)

    # Collect events until released
    with Listener(
            on_move=on_move,
            on_click=on_click,
            on_scroll=on_scroll) as listener:
        listener.join()




def detectClickedText(x,y):
    screenshot = pyautogui.screenshot()
    clip = utils.PILtoCV2(screenshot)
    detectText.detectAllTextBoxes(clip)













def registerKeyboard():

    ptime=time.time()
    from pynput import keyboard

    def on_press(key):
        try:
            print('alphanumeric key {0} pressed'.format(
                key.char))
        except AttributeError:
            print('special key {0} pressed'.format(
                key))

    def on_release(key):
        print('{0} released'.format(
            key))
        if key == keyboard.Key.esc:
            # Stop listener
            return False

    # Collect events until released

    # ...or, in a non-blocking fashion:
    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)
    listener.start()

INIT=False
def init():
    registerKeyboard()
    registerMouse()
    INIT=True
def start_recording():
    if(not INIT):
        init()
