#! /usr/bin/env python3

import pygame as pg
from time import sleep

from constant import *
from modbus import plc
import kb

####### color map #######
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255 ,255, 0)
##### control value #####
gun_speed_value = 0
solder_speed_value = 0
gun_height_value = 0
v_value, a_value = 0, 0
#########################

######## iniaialize interface(pygame) ########
pg.init()
pg.font.init()

font = pg.font.SysFont('Noto Sans CJK', 40)
font_small = pg.font.SysFont('Noto Sans CJK', 24)

W, H = 370, 272
WIN = pg.display.set_mode((W, H))
# WIN = pg.display.set_mode((W, H), pg.FULLSCREEN)

### initialize modbus connect and keyboard ###
plc_main = plc()
plc.connect()
kb.init()

####### functions #######
def print_text(text:str, position:int, line:bool = 0, color = YELLOW):
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

def set_val(id:int):
    if id == GUN_SPEED_VALUE:
        address = 10
        default_val = gun_speed_value
    elif id == SOLDER_SPEED_VALUE:
        address = 12
        default_val = solder_speed_value
    
    locked = False
    temp = ''
    while True:
        key = kb.scan()
        if key == '#': break
        elif key == '*': pass
        elif key != 0:
            if not locked:
                temp += key
                locked = key

        else: locked = False

        if temp != '' and int(temp) >= 2000: temp = '2000'
        WIN.fill(BLACK)
        print_text(str(temp), 1, color=RED)
    
    plc.write_value(id, int(temp))
    return (temp if temp != '' else default_val)

def draw_main_screen():
    WIN.fill(BLACK)

    gun_speed_value = plc_main.read_value(GUN_SPEED_VALUE)
    solder_speed_value = plc_main.read_value(SOLDER_SPEED_VALUE)
    v_value = plc_main.read_value(GUN_VOLTAGE)
    a_value = plc_main.read_value(GUN_AMP)

    print_text(str(gun_speed_value), 1)
    print_text('mm/min', 1, 1)
    print_text(str(solder_speed_value), 2)
    print_text('mm/min', 2, 1)
    print_text(str(gun_height_value), 3)
    print_text('mm', 3, 1)
    print_text(f'{str(v_value)}/{str(a_value)}', 4)
    print_text('V/A', 4, 1)

#########　main loop #########
run = True
while run:
    for event in pg.event.get():
        # quit script
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE): run = False

        # auto mode, at plc S5
    if plc_main.read_value(0xB000+5):
        pass

        # manual mode, at plc S4
    elif plc_main.read_value(0xB000+4):
        k = kb.scan()
        if k == '*':

            # read plc coil M13
            if plc_main.read_value(0x2000+13):
                set_val(GUN_SPEED_VALUE)

            # read plc coil M14
            elif plc_main.read_value(0x2000+14):
                set_val(SOLDER_SPEED_VALUE)
            else: pass

    draw_main_screen()

    pg.display.update()
    pg.time.delay(200)

pg.quit()
kb.close()
# plc_main.disconnect()