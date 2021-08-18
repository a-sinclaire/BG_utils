from tkinter import ttk
import tkinter as tk
import os
import pyautogui
from pynput import keyboard
import subprocess
import cv2
import pygame
from PIL import ImageGrab
from functools import partial

if os.environ.get('USERNAME') != "wheez":
    ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 0)

LARGE_FONT = ("Verdana", 12)
NORM_FONT = ("Helvetica", 10)
SMALL_FONT = ("Helvetica", 8)


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
    # print('(COLOR PICK)')
    # return
    # Take A ScreenShot & Save to File
    my_screenshot = pyautogui.screenshot()
    my_screenshot.save(r'../Assets/screenshot.png')

    # Start pygame instance
    if not pygame.display.get_init():
        pygame.display.init()
    if not pygame.font.get_init():
        pygame.font.init()
    pygame.display.set_caption("color_pick")
    pygame.display.set_allow_screensaver(True)
    pygame.mouse.set_visible(False)
    font = pygame.font.SysFont('Consolas', 30)
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

    while True:
        if zoom < 1:
            zoom = 1
        # draw BG (display screenshot)
        screen.blit(pyimg_dark, (0, 0))
        # get mouse_x mouse_y
        x, y = pygame.mouse.get_pos()
        # get color at mouse_x mouse_y
        color = pygame.Color(pygame.PixelArray(pyimg)[x, y])
        alpha, red, g, b = color
        rgb = [red, g, b]
        hex_val = (rgb2hex(rgb))

        # create circular mask
        cropped_mask = pygame.Surface((r * zoom * 2, r * zoom * 2))
        cropped_mask.fill((0, 0, 0))
        pygame.draw.circle(cropped_mask, (255, 255, 255), (r * zoom, r * zoom), r)
        # Create zoomed portion (copy of BG) #
        cropped = pygame.Surface((r * 2, r * 2))
        cropped.blit(pyimg, (0, 0), (x - r, y - r, r * 2, r * 2))
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
        crosshair = pygame.Surface((r * 2, r * 2))
        crosshair.fill((0, 0, 0))
        pygame.draw.circle(crosshair, (255, 255, 255), (r, r), r, 1)
        pygame.draw.line(crosshair, (255, 255, 255), (r, 0), (r, 2 * r))
        pygame.draw.line(crosshair, (255, 255, 255), (0, r), (2 * r, r))
        # draw color preview box
        pygame.draw.rect(crosshair, (255, 255, 255),
                         (round(r - r / 4) - 1, round(r + r / 4) - 1, round(r / 2) + 2, round(r / 2) + 2),
                         border_radius=round(r / 8))
        crosshair.set_colorkey((0, 0, 0))
        screen.blit(crosshair, (x - r, y - r))
        pygame.draw.rect(screen, rgb, (round(x - r / 4), round(y + r / 4), round(r / 2), round(r / 2)),
                         border_radius=round(r / 8))

        # draw hex text
        text = font.render(hex_val, False, (255, 255, 255))
        if x < r - text.get_width() * .25:
            x_off = text.get_width() * .5 - x
        elif x > screen.get_width() - r + text.get_width() * .25:
            x_off = screen.get_width() - x - text.get_width() * .5
        else:
            x_off = 0
        if y > screen.get_height() - r - text.get_height():
            screen.blit(text, (x - round(text.get_width() / 2) + x_off, y - r - text.get_height()))
        else:
            screen.blit(text, (x - round(text.get_width() / 2) + x_off, y + r))

        # update display
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                copy2clip(hex_val)
                pygame.display.quit()
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    pygame.mouse.set_pos([x, y-1])
                if event.key == pygame.K_DOWN:
                    pygame.mouse.set_pos([x, y+1])
                if event.key == pygame.K_LEFT:
                    pygame.mouse.set_pos([x-1, y])
                if event.key == pygame.K_RIGHT:
                    pygame.mouse.set_pos([x+1, y])
                if event.key == pygame.K_LEFTBRACKET:
                    zoom -= 1
                if event.key == pygame.K_RIGHTBRACKET:
                    zoom += 1
                if event.key == pygame.K_ESCAPE:
                    pygame.display.quit()
                    pygame.quit()
                    return


def popupmsg(msg):
    popup = tk.Tk()
    popup.wm_title("msg box")
    label = ttk.Label(popup, text=msg, font=NORM_FONT)
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Okay", command=popup.destroy)
    B1.pack()
    popup.mainloop()


def on_activate_kill():
    # print('(QUIT)')
    popupmsg("Color Pick Thread has been Killed")
    pygame.quit()
    raise MyException("kill")


# for some reason i have to press the key combo twice (something with pygame)
# but also, i can just push one part of the key combo and it goes off?
# if the combo was <alt>+c for example i could get it to trigger (after the first time)
# by just pressing alt, or just pressing c. (also an issue with pygame)
# couldn't find a solution (other than remapping to uncommon keys)
# maybe in the future replace pygame with something else?
with keyboard.GlobalHotKeys(
        {'<f9>': on_activate_col_pick,
         '<scroll_lock>': on_activate_kill}) as h:
    h.join()
