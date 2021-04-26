import pygame
from pygame.locals import *
import numpy
import math
import pickle
pygame.init()
 

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (64, 64, 255)

COLOURS_LIST = (
    (255, 255, 255),
    (0, 255, 0),
    (255, 0, 0),
    (0, 0, 0),
    (64, 64, 255),
    (255, 0, 255),
    (255, 255, 0),
    (0, 255, 255),
    (128, 0, 0),
    (128, 128, 0),
    (128, 128, 128),
    (0, 128, 128),
    (0, 128, 0),
    (0, 0, 128)
)

count = 80
width = 10
height = 10
margin = 1
button_layer_height = 50
font_size = 12
#grid = [[0 for _ in range(count)] for _ in range(count)]
grid = numpy.zeros((count, count), dtype="byte")
font = pygame.font.SysFont("Consolas", font_size, True, False)
left_clicked = False
right_clicked = False
color_index = 1

size = ((width + margin) * count + margin, (height + margin) * count + margin + button_layer_height)
screen = pygame.display.set_mode(size)
 
pygame.display.set_caption("Matriisi")
 

done = False
 

clock = pygame.time.Clock()

moi_text = font.render("Tyhjennä", True, WHITE)
moi_x = 0
lopeta_text = font.render("Lopeta", True, WHITE)
lopeta_x = 100
save_text = font.render("Tallenna", True, WHITE)
save_x = 200

def menu_button(x: int, _text: pygame.Surface):
    button_rect = pygame.Rect(x + 3, 3, 94, button_layer_height - 6)
    pygame.draw.rect(screen, (128, 128, 128), button_rect)
    screen.blit(_text, (button_rect.centerx - _text.get_width() // 2, (button_layer_height - font_size) // 2))

while not done:
    for event in pygame.event.get():
        if event.type == QUIT:
            done = True
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                left_clicked = True
            elif event.button == 3:
                right_clicked = True
            elif event.button == 4:
                color_index += 1
                if color_index >= len(COLOURS_LIST):
                    color_index = 1
            elif event.button == 5:
                color_index -= 1
                if color_index < 1:
                    color_index = len(COLOURS_LIST) - 1
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                left_clicked = False
            elif event.button == 3:
                right_clicked = False
 
    
    player_position = pygame.mouse.get_pos()

    screen.fill((64, 64, 64))
    
    menu_button(moi_x, moi_text)
    menu_button(lopeta_x, lopeta_text)
    menu_button(save_x, save_text)
    pygame.draw.rect(screen, COLOURS_LIST[color_index], (width * count + margin * count - 47, 3, 44, 44))
    
    if left_clicked or right_clicked:
        x = player_position[0]
        y = player_position[1] - button_layer_height
        row = min(x // (width + margin), count - 1)
        column = min(y // (height + margin), count - 1)
        
        if y <= 0 and moi_x <= x <= moi_x + 100:
            grid = numpy.zeros((count, count), dtype="byte")
            print("tyhjennä")
        elif y <= 0 and lopeta_x <= x <= lopeta_x + 100:
            done = True
            print("lopeta")
        elif y <= 0 and save_x <= x <= save_x + 100:
            pass
        else:
            print(f"{row}, {column}")
            if not right_clicked:
                grid[column][row] = color_index
            else:
                grid[column][row] = 0
    
 
    for column in range(count):
        for row in range(count):
            pygame.draw.rect(screen, COLOURS_LIST[grid[row][column]], (column * width + margin * column + margin, row * height + margin * row + margin + button_layer_height, width, height))
            
    pygame.display.flip()
    
    print(clock.get_fps())
    
    clock.tick()
 
pygame.quit()