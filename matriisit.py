import pygame
from pygame.locals import *
import json
import os
pygame.init()

#AppData
AppDataPath = os.path.join(str(os.getenv('APPDATA')), "ArktPVC", "Matriisit")
if not os.path.isfile(AppDataPath):
    os.makedirs(AppDataPath, exist_ok=True)

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
font = pygame.font.SysFont("Consolas", font_size, True, False)
left_pressed = False
right_pressed = False
color_index = 1

def generateGrid():
    return [[0 for _ in range(count)] for _ in range(count)]

grid = generateGrid()

size = ((width + margin) * count + margin, (height + margin) * count + margin + button_layer_height)
screen: pygame.Surface = pygame.display.set_mode(size)

pygame.display.set_caption("Matriisit")

done = False

clock = pygame.time.Clock()

moi_text = font.render("Tyhjennä", True, WHITE)
moi_x = 0
lopeta_text = font.render("Lopeta", True, WHITE)
lopeta_x = 100
save_text = font.render("Tallenna", True, WHITE)
save_x = 200
load_text = font.render("Lataa", True, WHITE)
load_x = 300

DebugMode = False

def menu_button(x: int, _text: pygame.Surface):
    button_rect = pygame.Rect(x + 3, 3, 94, button_layer_height - 6)
    pygame.draw.rect(screen, (128, 128, 128), button_rect)
    screen.blit(_text, (button_rect.centerx - _text.get_width() // 2, (button_layer_height - font_size) // 2))

while not done:
    left_clicked = False
    right_clicked = False
    for event in pygame.event.get():
        if event.type == QUIT:
            done = True
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                left_pressed = True
            elif event.button == 3:
                right_pressed = True
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
                left_pressed = False
                left_clicked = True
            elif event.button == 3:
                right_pressed = False
                right_clicked = True
        elif event.type == KEYDOWN:
            if event.key == K_F3:
                DebugMode = not DebugMode


    player_position = pygame.mouse.get_pos()

    screen.fill((64, 64, 64))

    menu_button(moi_x, moi_text)
    menu_button(lopeta_x, lopeta_text)
    menu_button(save_x, save_text)
    menu_button(load_x, load_text)
    pygame.draw.rect(screen, COLOURS_LIST[color_index], (width * count + margin * count - 47, 3, 44, 44))

    x = player_position[0]
    y = player_position[1] - button_layer_height

    if y > 0:
        if left_pressed or right_pressed:
            row = min(x // (width + margin), count - 1)
            column = min(y // (height + margin), count - 1)

            if not right_pressed:
                grid[column][row] = color_index
            else:
                grid[column][row] = 0
    elif left_clicked:
        if moi_x <= x <= moi_x + 100:
            grid = generateGrid()
            print("tyhjennä")
        elif lopeta_x <= x <= lopeta_x + 100:
            done = True
            print("lopeta")
        elif save_x <= x <= save_x + 100:
            serialized = json.dumps(grid, separators=(',', ':')) # Toimii, koska grid on vaan lista, jossa on listoja, joissa on numeroita
            with open(os.path.join(AppDataPath, "save.penis"), "w", encoding="utf-8") as f:
                f.write(serialized)
            print("tallenna")
        elif load_x <= x <= load_x + 100:
            loadPath = os.path.join(AppDataPath, "save.penis")
            if os.path.isfile(loadPath):
                with open(loadPath, "r", encoding="utf-8") as f:
                    serialized = f.read()
                grid = json.loads(serialized)
                print("lataa")
            else: print("ei ladattavaa")

    if DebugMode:
        screen.blit(font.render(format(round(clock.get_fps(), 3), ".3f"), True, WHITE, BLACK), (button_layer_height / 2 - font_size / 2, button_layer_height / 2 - font_size / 2))

    ### Hidas ###
    # for column in range(count):
    #     for row in range(count):
    #         pygame.draw.rect(screen, COLOURS_LIST[grid[row][column]], (column * width + margin * column + margin, row * height + margin * row + margin + button_layer_height, width, height))

    # Tätä nopeempaa iteraatiota on kait likimahdotonta tehdä Pythonissa
    [pygame.draw.rect(screen, COLOURS_LIST[grid[row][column]], (column * width + margin * column + margin, row * height + margin * row + margin + button_layer_height, width, height)) for row in range(count) for column in range(count)]

    pygame.display.flip()

    clock.tick()

pygame.quit()
print("loppuu")