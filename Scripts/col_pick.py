import os
import pyautogui
from pynput import keyboard
import subprocess
import cv2
import pygame
from PIL import ImageGrab
from functools import partial
ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)
PICK_COLOR = False


os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 0)


def rgb2hex(rgb):
    r = rgb[0]
    g = rgb[1]
    b = rgb[2]
    return '#%02x%02x%02x' % (r, g, b)


def copy2clip(txt):
    cmd = 'echo '+txt.strip()+'|clip'
    return subprocess.check_call(cmd, shell=True)


class MyException(Exception):
    pass


def on_activate_col_pick():
    global PICK_COLOR, screen, pyimg
    print('<cmd>+<shift>+c pressed')
    # Take A ScreenShot & Save to File
    myscreenshot = pyautogui.screenshot()
    myscreenshot.save(r'D:/_Files/Programming/Python/BG_utils/Assets/screenshot.png')

    # Display screenshot
    pygame.init()
    pygame.mouse.set_visible(False)
    img = cv2.imread('D:/_Files/Programming/Python/BG_utils/Assets/screenshot.png')
    width, height = img.shape[1], img.shape[0]
    screen = pygame.display.set_mode([width, height], pygame.NOFRAME, pygame.SHOWN)
    pyimg = pygame.image.load('D:/_Files/Programming/Python/BG_utils/Assets/screenshot.png').convert()

    PICK_COLOR = True
    while PICK_COLOR:
        # draw BG
        screen.blit(pyimg, (0, 0))

        # draw crosshair
        x, y = pygame.mouse.get_pos()
        r = 50
        pygame.draw.circle(screen, (255, 255, 255), (x, y), r, 1)  # debug
        pygame.draw.line(screen, (255, 255, 255), (x, y+r), (x, y-r))
        pygame.draw.line(screen, (255, 255, 255), (x+r, y), (x-r, y))
        color = pygame.Color(pygame.PixelArray(pyimg)[x, y])
        alpha, red, g, b = color
        pygame.draw.rect(screen, (red, g, b), (round(x-r/4), round(y-r/4), round(r/2), round(r/2)), border_radius=round(r/4))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                rgb = [red, g, b]
                hex_val = (rgb2hex(rgb))
                print(hex_val)
                copy2clip(hex_val)
                PICK_COLOR = False
                pygame.quit()


def on_activate_kill():
    print('<ctrl>+<shift>+<esc> pressed')
    pygame.quit()
    raise MyException("kill")


with keyboard.GlobalHotKeys({
    '<cmd>+<shift>+c': on_activate_col_pick,
    '<ctrl>+<shift>+<esc>': on_activate_kill}) as h:
    h.join()
