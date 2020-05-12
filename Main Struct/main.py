#! /usr/bin/env python3
import pygame as pg
from picamera import PiCamera
from picamera.array import PiRGBArray
import cv2 as cv

from constant import *
from color import *
from modbus import plc
import kb

##### control value #####
torch_speed_value_mm_per_min = 200
solder_speed_value_v = 2
gun_height_value = 0
v_value, a_value = 0, 0
######## iniaialize interface(pygame) ########
pg.init()
pg.font.init()

font = pg.font.SysFont('Noto Sans CJK', 40)
font_small = pg.font.SysFont('Noto Sans CJK', 24)

W, H = 370, 272
# WIN = pg.display.set_mode((W, H))
WIN = pg.display.set_mode((W, H), pg.FULLSCREEN)
### initialize modbus connect ###
plc_main = plc()
print(plc_main.connect())
if plc_main.is_connected:
    plc_main.write_value(TORCH_SPEED_VALUE, torch_speed_value_mm_per_min*2//3)
    plc_main.write_value(SOLDER_SPEED_VALUE, solder_speed_value_v*400)
    v_value = plc_main.read_value(GUN_VOLTAGE) / 200
    a_value = plc_main.read_value(GUN_AMP) / 400

### initialize keyboard ###
kb.init()
### initialize camera, including parameters ###
camera_resolution = (640, 480)
camera = PiCamera()
camera.resolution = camera_resolution
camera.brightness = 25
rawCapture = PiRGBArray(camera, size=camera_resolution)
####### functions #######


def draw_title(text: str, color=WHITE):
    text = font.render(text, True, color)

    width = text.get_width()
    x = (W - width)//2
    WIN.blit(text, (x, 120))


def print_text(text: str, position: int, line: bool = 0, color=YELLOW):
    if type(text) != str:
        print('Text type must be string.')
        return

    if not line:
        text = font.render(text, True, color)
        y = 210
    else:
        text = font_small.render(text, True, color)
        y = 240

    width = text.get_width()
    x = W//8 * (position*2 - 1) - width//2
    WIN.blit(text, (x, y))


def draw_main_screen():

    try:
        if plc_main.read_value(AUTO_MODE):
            draw_title('AUTO MODE')
        elif plc_main.read_value(MENUAL_MODE):
            draw_title('MANUAL MODE')

        v_value = plc_main.read_value(GUN_VOLTAGE) / 200
        a_value = plc_main.read_value(GUN_AMP) / 400

        WIN.fill(BLACK)
        print_text(str(torch_speed_value_mm_per_min * 1.5), 1)
        print_text('mm/min', 1, 1)
        print_text(str(solder_speed_value_v), 2)
        print_text('mm/min', 2, 1)
        print_text(str(gun_height_value), 3)
        print_text('mm', 3, 1)
        print_text(f'{str(v_value)}/{str(a_value)}', 4)
        print_text('V/A', 4, 1)

    except:
        pass


def set_val(id: int):
    if id == TORCH_SPEED_VALUE:
        default_val = torch_speed_value_mm_per_min
    elif id == SOLDER_SPEED_VALUE:
        default_val = solder_speed_value_v

    locked = False
    temp = ''
    while True:
        key = kb.scan()
        if key == '#':
            break
        elif key == '*':
            pass
        elif key != 0:
            if not locked:
                temp += key
                locked = key

        else:
            locked = False

        if id == TORCH_SPEED_VALUE:
            if int(temp) >= 2000:
                temp = '2000'
        elif id == SOLDER_SPEED_VALUE:
            if int(temp) >= 10:
                temp = '10'

    if temp != '':
        if id == TORCH_SPEED_VALUE:
            plc_main.write_value(id, int(temp)*2//3)
            torch_speed_value_mm_per_min = int(temp)
        elif id == SOLDER_SPEED_VALUE:
            plc_main.write_value(id, int(temp)*400)
            solder_speed_value_v = int(temp)
        return

    else:
        plc_main.write_value(id, default_val)
        return


def close():
    pg.quit()
    kb.close()
    plc_main.disconnect()
    exit()


#########　main loop #########
while True:
    # quit script
    for event in pg.event.get():
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            close()

    if not plc_main.is_connected:
        print(plc_main.connect())

    draw_main_screen()

    ############ plc buttons status #############
    # manual mode, at plc S4
    if plc_main.read_value(MENUAL_MODE):
        k = kb.scan()
        if k == '*':

            # read plc coil M13
            if plc_main.read_value(SET_GUN_SPEED):
                set_val(TORCH_SPEED_VALUE)

            # read plc coil M14
            elif plc_main.read_value(SET_SOLDER_SPEED):
                set_val(SOLDER_SPEED_VALUE)

    # automode
    elif plc_main.read_value(AUTO_MODE):
        if plc_main.read_value(AUTO_START):

            # camera detect
            for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
                image = frame.array
                cv.imshow('frame', image)

                rawCapture.truncate(0)

    pg.display.update()
    pg.time.delay(100)

close()