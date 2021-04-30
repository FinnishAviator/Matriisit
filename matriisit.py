from typing import Dict, List, Tuple
from PIL import Image
import tkinter
from tkinter import filedialog
import math
import pygame
from pygame.locals import *
import json
import os

pygame.init()
root = tkinter.Tk()
root.withdraw()

#AppData
AppDataPath = os.path.join(str(os.getenv('APPDATA')), "ArktPVC", "Matriisit")
ConfigPath = os.path.join(AppDataPath, "config.json")
if not os.path.isdir(AppDataPath):
    os.makedirs(AppDataPath, exist_ok=True)
if not os.path.isfile(ConfigPath):
    with open(ConfigPath, "w") as f:
        f.write("""{
    \"count\": 80,
    \"width\": 10,
    \"height\": 10,
    \"margin\": 1
}""")

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

def closestColour(colour: Tuple[int, int, int]) -> Tuple[int, int, int]:
    def colour_diff(iterColour: Tuple[int, int, int]) -> float:
        return math.sqrt(abs(colour[0] - iterColour[0]) ** 2 + abs(colour[1] - iterColour[1]) ** 2 + abs(colour[2] - iterColour[2]) ** 2)

    return min(COLOURS_LIST, key=colour_diff)

with open(ConfigPath) as f:
    parsedConfig: Dict[str, int] = json.loads(f.read())
    for checkType in parsedConfig.values():
        if not isinstance(checkType, int):
            raise TypeError(f"Config value {checkType} is not an integer!")
    count: int = parsedConfig["count"]
    width: int = parsedConfig["width"]
    height: int = parsedConfig["height"]
    margin: int = parsedConfig["margin"]
button_layer_height = 50
font_size = 12
font = pygame.font.SysFont("Consolas", font_size, True, False)
left_pressed = False
right_pressed = False
color_index = 1

def generateGrid() -> List[List[int]]:
    return [[0 for _ in range(count)] for _ in range(count)]

def loadImageAsGrid() -> List[List[int]]:
    imagePath = filedialog.askopenfilename(filetypes=(("Image file", "*.jpeg"), ("Image file", "*.jpg"), ("Image file", "*.png"), ("Image file", "*.bmp"), ("Image file", "*.jfif"), ("All files", "*.*")), title="Open Image File")
    if imagePath == None or len(imagePath) < 1:
        return generateGrid()
    with Image.open(imagePath) as im:
        image = im.convert("RGB")

    cropSize = min(image.size[0], image.size[1])
    image = image.crop((image.size[0] // 2 - cropSize // 2, image.size[1] // 2 - cropSize // 2, image.size[0] // 2 + cropSize // 2, image.size[1] // 2 + cropSize // 2))
    image = image.resize((count, count))

    tmpGrid: List[List[int]] = []
    for y in range(count):
        tmpGrid.append([])
        for x in range(count):
            pxl = image.getpixel((x, y))
            if isinstance(pxl, int):
                print("Mitä vittua miks tää on intti?")
                return generateGrid()
            tmpGrid[y].append(COLOURS_LIST.index(closestColour((pxl[0], pxl[1], pxl[2]))))
    return tmpGrid

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
previous_slot_text = font.render("<", True, WHITE)
previous_slot_x = 400
next_slot_text = font.render(">", True, WHITE)
next_slot_x = 600

DebugMode = False

save_index = 0

def menu_button(x: int, _text: pygame.Surface):
    button_rect = pygame.Rect(x + 3, 3, 94, button_layer_height - 6)
    pygame.draw.rect(screen, (128, 128, 128), button_rect)
    screen.blit(_text, (button_rect.centerx - _text.get_width() // 2, (button_layer_height - font_size) // 2))

while not done:
    left_clicked = False
    right_clicked = False
    keys_pressed: Dict[int, bool] = pygame.key.get_pressed()
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
            elif event.key == K_o:
                if keys_pressed[K_LCTRL]:
                    grid = loadImageAsGrid()

    player_position = pygame.mouse.get_pos()

    screen.fill((64, 64, 64))

    menu_button(moi_x, moi_text)
    menu_button(lopeta_x, lopeta_text)
    menu_button(save_x, save_text)
    menu_button(load_x, load_text)
    menu_button(previous_slot_x, previous_slot_text)
    menu_button(next_slot_x, next_slot_text)
    save_slot_text: pygame.Surface = font.render(str(save_index), True, WHITE)
    screen.blit(save_slot_text, (previous_slot_x + (next_slot_x - (previous_slot_x + 50)) - save_slot_text.get_width() // 2, button_layer_height // 2 - save_slot_text.get_height() // 2))
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
            with open(os.path.join(AppDataPath, f"save{str(save_index) if save_index != 0 else ''}.penis"), "w", encoding="utf-8") as f:
                f.write(serialized)
            print("tallenna")
        elif load_x <= x <= load_x + 100:
            loadPath = os.path.join(AppDataPath, f"save{str(save_index) if save_index != 0 else ''}.penis")
            if os.path.isfile(loadPath):
                with open(loadPath, "r", encoding="utf-8") as f:
                    serialized = f.read()
                tmp = json.loads(serialized)
                if len(tmp) != count:
                    print(f"ladattavan tallennuksen matriisin koko ei ole yhteensopiva pelin matriisin koon kanssa.\ntallennuksen koko: {len(tmp)}, pelin koko: {count}")
                else:
                    grid = tmp
                    print("lataa")
            else: print("ei ladattavaa")
        elif previous_slot_x <= x <= previous_slot_x + 100:
            if save_index > 0:
                save_index -= 1
        elif next_slot_x <= x <= next_slot_x + 100:
            if save_index < 69:
                save_index += 1

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