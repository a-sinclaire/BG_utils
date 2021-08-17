import os
import pyautogui
from pynput import keyboard
import subprocess
import cv2
import pygame
from PIL import ImageGrab
from functools import partial

ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

from ctypes import windll  # windows only

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 0)
SetWindowPos = windll.user32.SetWindowPos


def rgb2hex(rgb):
    r = rgb[0]
    g = rgb[1]
    b = rgb[2]
    return '#%02x%02x%02x' % (r, g, b)


def copy2clip(txt):
    cmd = 'echo ' + txt.strip() + '|clip'
    return subprocess.check_call(cmd, shell=True)


class MyException(Exception):
    pass


def palette_swap(surf, old_c, new_c):
    img_copy = pygame.Surface(surf.get_size())
    img_copy.fill(new_c)
    surf.set_colorkey(old_c)
    img_copy.blit(surf, (0, 0))
    return img_copy


def on_activate_col_pick():
    print('<alt>+c pressed (COLOR PICK)')
    # Take A ScreenShot & Save to File
    myscreenshot = pyautogui.screenshot()
    myscreenshot.save(r'../Assets/screenshot.png')

    # Start pygame instance
    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont('Consolas', 30)
    pygame.mouse.set_visible(False)
    # pygame.mouse.set_cursor(pygame.cursors.broken_x)
    img = cv2.imread('../Assets/screenshot.png')
    width, height = img.shape[1], img.shape[0]
    # create main canvas
    screen = pygame.display.set_mode([width, height])

    # load img and create dark version
    pyimg = pygame.image.load('../Assets/screenshot.png').convert()
    dark = pygame.Surface(screen.get_size())
    dark.fill((0, 0, 0))
    dark.set_alpha(100)
    pyimg_dark = pyimg.copy()
    pyimg_dark.blit(dark, (0, 0))

    # radius of search circle and zoom level
    r = 100
    zoom = 4
    # create circular mask
    cropped_mask = pygame.Surface((r * zoom * 2, r * zoom * 2))
    cropped_mask.fill((0, 0, 0))
    pygame.draw.circle(cropped_mask, (255, 255, 255), (r * zoom, r * zoom), r)

    PICK_COLOR = True
    while PICK_COLOR:
        # draw BG (display screenshot)
        screen.blit(pyimg_dark, (0, 0))
        # get mouse_x mouse_y
        x, y = pygame.mouse.get_pos()
        # get color at mouse_x mouse_y
        color = pygame.Color(pygame.PixelArray(pyimg)[x, y])
        alpha, red, g, b = color
        rgb = [red, g, b]
        hex_val = (rgb2hex(rgb))

        # Create zoomed portion (copy of BG) #
        cropped = pygame.Surface((r * 2, r * 2))
        cropped.blit(pyimg, (0, 0), (x - r, y - r, r * zoom, r * zoom))
        # swap true black to something close so it isn't color_keyed out
        cropped = palette_swap(cropped, (0, 0, 0), (2, 2, 2))
        # zoom in and mask out circle
        cropped = pygame.transform.scale(cropped, (r * zoom * 2, r * zoom * 2))
        cropped.blit(cropped_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        # make all black pix transparent
        cropped.set_colorkey((0, 0, 0))
        # blit onto surface
        screen.blit(cropped, (x - r * zoom, y - r * zoom))

        # draw cross-hair
        crosshair = pygame.Surface((r*2, r*2))
        crosshair.fill((0, 0, 0))
        pygame.draw.circle(crosshair, (255, 255, 255), (r, r), r, 1)
        pygame.draw.line(crosshair, (255, 255, 255), (r, 0), (r, 2*r))
        pygame.draw.line(crosshair, (255, 255, 255), (0, r), (2*r, r))
        # draw color preview box
        pygame.draw.rect(crosshair, (255, 255, 255),
                         (round(r - r / 4) - 1, round(r + r / 4) - 1, round(r / 2) + 2, round(r / 2) + 2),
                         border_radius=round(r / 8))
        crosshair.set_colorkey((0, 0, 0))
        screen.blit(crosshair, (x-r, y-r))
        pygame.draw.rect(screen, rgb, (round(x - r / 4), round(y + r / 4), round(r / 2), round(r / 2)),
                         border_radius=round(r / 8))
        # draw hex text
        text = font.render(hex_val, False, (255, 255, 255))
        screen.blit(text, (x - round(text.get_width() / 2), y + r))

        # update display
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                print(hex_val)
                copy2clip(hex_val)
                PICK_COLOR = False
                pygame.quit()
    return


def on_activate_kill():
    print('<esc> pressed (QUIT)')
    pygame.quit()
    raise MyException("kill")


with keyboard.GlobalHotKeys({
    '<alt>+c': on_activate_col_pick,
    '<esc>': on_activate_kill}) as h:
    h.join()
