import pygame as pg

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255 ,255, 0)

class interface:
    def __init__(self):
        pg.init()
        pg.font.init()

        self.font = pg.font.SysFont('Noto Sans CJK', 40)
        self.W, self.H = 370, 272
        WIN = pg.display.set_mode((self.W, self.H), pg.FULLSCREEN)

        self.e = self.W//8

    def draw(self, gun_speed:int, solder_speed:int, gun_height:int, v:int, a:int):
        _print_text(str(gun_speed), pos, )

    def _print_text(self, text:str, position:list, color = YELLOW):
        text = font.render(text, True, color)
        width = text.get_width()
        