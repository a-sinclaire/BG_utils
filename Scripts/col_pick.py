import os
import pyautogui
from pynput import keyboard
import subprocess
import cv2
import pygame
from PIL import ImageGrab
from functools import partial
ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

from ctypes import windll  #windows only
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 0)
SetWindowPos = windll.user32.SetWindowPos


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
    print('<cmd>+<shift>+c pressed')
    # Take A ScreenShot & Save to File
    myscreenshot = pyautogui.screenshot()
    myscreenshot.save(r'D:/_Files/Programming/Python/BG_utils/Assets/screenshot.png')

    # Display screenshot
    pygame.init()
    pygame.font.init()
    myfont = pygame.font.SysFont('Consolas', 30)
    pygame.mouse.set_visible(False)
    img = cv2.imread('D:/_Files/Programming/Python/BG_utils/Assets/screenshot.png')
    width, height = img.shape[1], img.shape[0]
    screen = pygame.display.set_mode([width, height])
    # force on top
    # SetWindowPos(pygame.display.get_wm_info()["window"], 0, 0, 0, 0, 0, 2 | 1)
    pyimg = pygame.image.load('D:/_Files/Programming/Python/BG_utils/Assets/screenshot.png').convert()

    r = 80
    zoom = 3
    cropped_mask = pygame.Surface((r * zoom*2, r * zoom*2))
    cropped_mask.fill((0, 0, 0))
    pygame.draw.circle(cropped_mask, (255, 255, 255), (r*zoom, r*zoom), r)

    PICK_COLOR = True
    while PICK_COLOR:
        # draw BG
        screen.blit(pyimg, (0, 0))

        # draw crosshair
        x, y = pygame.mouse.get_pos()
        cropped = pygame.Surface((r*2, r*2))
        cropped.blit(screen, (0, 0), (x-r, y-r, r*zoom, r*zoom))
        cropped = pygame.transform.scale(cropped, (r*zoom*2, r*zoom*2))
        cropped.blit(cropped_mask, (0, 0), special_flags=pygame.BLEND_MULT)
        cropped.set_colorkey((0, 0, 0))

        screen.blit(cropped, (x-r*zoom, y-r*zoom))
        pygame.draw.circle(screen, (255, 255, 255), (x, y), r, 1)
        pygame.draw.line(screen, (255, 255, 255), (x, y+r), (x, y-r))
        pygame.draw.line(screen, (255, 255, 255), (x+r, y), (x-r, y))
        color = pygame.Color(pygame.PixelArray(pyimg)[x, y])
        alpha, red, g, b = color
        rgb = [red, g, b]
        hex_val = (rgb2hex(rgb))
        pygame.draw.rect(screen, (red, g, b), (round(x-r/4), round(y+r/4), round(r/2), round(r/2)), border_radius=round(r/8))
        text = myfont.render(hex_val, False, (255, 255, 255))
        screen.blit(text, (x-round(text.get_width()/2), y+r))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                print(hex_val)
                copy2clip(hex_val)
                PICK_COLOR = False
                pygame.quit()
    return


def on_activate_kill():
    print('<ctrl>+<shift>+<esc> pressed')
    pygame.quit()
    raise MyException("kill")


with keyboard.GlobalHotKeys({
    '<cmd>+<shift>+c': on_activate_col_pick,
    '<ctrl>+<shift>+<esc>': on_activate_kill}) as h:
    h.join()
