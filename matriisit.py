from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from PIL import Image
import tkinter
from tkinter import filedialog, messagebox
import math
import pygame
import pygame.gfxdraw
from pygame.locals import *
import json
import os
import modules.line

pygame.init()
root = tkinter.Tk()
root.withdraw()
root.wm_iconbitmap("./assets/icon.ico")

#AppData
AppDataPath = os.path.join(str(os.getenv('APPDATA')), "ArktPVC", "Matriisit")
ConfigPath = os.path.join(AppDataPath, "config.json")
if not os.path.isdir(AppDataPath):
    os.makedirs(AppDataPath, exist_ok=True)

def defaultConfigSerialization(config: dict) -> str:
    return json.dumps(config, indent=4)

def defaultSaveSerialization(save: List[List[int]]) -> str:
    return json.dumps(save, separators=(',', ':')) # Toimii, koska grid on vaan lista, jossa on listoja, joissa on numeroita

defaultConfig: Dict[str, int] = {
    "count": 80,
    "width": 10,
    "height": 10,
    "margin": 1,
    "useDrawPathPrediction": True,
    "displayDrawPreview": True
}
if not os.path.isfile(ConfigPath):
    with open(ConfigPath, "w", encoding="utf-8") as f:
        f.write(defaultConfigSerialization(defaultConfig))

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

def Lerp(a: float, b: float, t: float) -> float:
    """Linearly interpolates between a and b by t.

    The parameter t is clamped to the range [0, 1].
    """
    return a + (b - a) * max(min(t, 1.0), 0.0) # maxmin clamps value between 0 and 1

with open(ConfigPath, "r+", encoding="utf-8") as f:
    parsedConfig: Dict[str, int] = json.loads(f.read())
    for checkType in parsedConfig.values():
        if not isinstance(checkType, int):
            raise TypeError(f"Config value {checkType} is not an integer!")
    for defaultKey in defaultConfig.keys():
        if defaultKey not in parsedConfig:
            defaultValue = defaultConfig[defaultKey]
            parsedConfig[defaultKey] = defaultValue
            print(f"{defaultKey} not found in settings. Setting it to: {defaultValue}")
            f.seek(0) # Truncate does not work if pointer is not at the beginning of the file
            f.truncate() # Truncate clears the file of all text
            f.write(defaultConfigSerialization(parsedConfig)) # Writing all settings where default value for defaultKey was added
    count: int = parsedConfig["count"]
    width: int = parsedConfig["width"]
    height: int = parsedConfig["height"]
    margin: int = parsedConfig["margin"]
    path_prediction: bool = True if parsedConfig["useDrawPathPrediction"] else False
    draw_preview: bool = True if parsedConfig["displayDrawPreview"] else False

button_layer_height = 50

pygame.display.set_caption("Matriisit")
tmp_logo = pygame.image.load("./assets/logo_46.png")
tmp_logo.set_colorkey((0, 0, 0))
pygame.display.set_icon(tmp_logo)
del tmp_logo

size = ((width + margin) * count + margin, (height + margin) * count + margin + button_layer_height)
screen: pygame.Surface = pygame.display.set_mode(size)

font_size = 12
font = pygame.font.SysFont("Consolas", font_size, True, False)
left_pressed = False
right_pressed = False
color_index = 1

def generateGrid() -> List[List[int]]:
    return [[0 for _ in range(count)] for _ in range(count)]

def loadImageAsGrid() -> Optional[List[List[int]]]:
    imagePath = filedialog.askopenfilename(filetypes=(("Image file", "*.jpeg"), ("Image file", "*.jpg"), ("Image file", "*.png"), ("Image file", "*.tiff"), ("Image file", "*.bmp"), ("Image file", "*.jfif"), ("All files", "*.*")), title="Open Image File")
    if imagePath == None or len(imagePath) < 1:
        return None
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

grid: List[List[int]] = generateGrid()

running = True

clock = pygame.time.Clock()

DebugMode = False

save_index: int = 0
save_range = (0, 69) # Inclusive

lastPathPredPos: Optional[Tuple[int, int]] = None

def get_save_path(save_index: int) -> str:
    return os.path.join(AppDataPath, f"save{str(save_index) if save_index != 0 else ''}.penis")

def renderMatrixUnit(surface: pygame.Surface, row: int, column: int, color: Union[Tuple[int, int, int], Tuple[int, int, int, int]]):
    pygame.gfxdraw.box(surface, (column * width + margin * column + margin, row * height + margin * row + margin + button_layer_height, width, height), color)

class menu_button:
    def __init__(self, x: int, text: str, clickFunc: Callable[[], Any]) -> None:
        self.rect: pygame.Rect = pygame.Rect(x + 3, 3, 94, button_layer_height - 6)
        self.textSurf: pygame.Surface = font.render(text, True, WHITE)
        self.func = clickFunc

    def update(self, surface: pygame.Surface, mouse_pos: Tuple[int, int], mouse_pressed: bool, mouse_clicked: bool) -> None:
        collidepoint = self.rect.collidepoint(mouse_pos)
        pygame.gfxdraw.box(surface, self.rect, (128, 128, 128) if not collidepoint else ((160, 160, 160) if not mouse_pressed else (192, 192, 192)))
        surface.blit(self.textSurf, (self.rect.centerx - self.textSurf.get_width() // 2, (button_layer_height - font_size) // 2))

        if mouse_clicked and collidepoint:
            self.func()

class button_functions:
    @staticmethod
    def clear():
        global grid
        grid = generateGrid()
        print("tyhjennä")

    @staticmethod
    def stop():
        global running
        running = False
        print("lopeta")

    @staticmethod
    def save():
        global grid, save_index
        serialized = defaultSaveSerialization(grid)
        with open(get_save_path(save_index), "w", encoding="utf-8") as f:
            f.write(serialized)
        print("tallenna")

    @staticmethod
    def load():
        global save_index, grid
        loadPath = get_save_path(save_index)
        if os.path.isfile(loadPath):
            with open(loadPath, "r", encoding="utf-8") as f:
                serialized = f.read()
            try:
                tmp = json.loads(serialized)
                if len(tmp) != count:
                    messagebox.showwarning("Yhteensopivuus", f"Ladattavan tallennuksen matriisin koko ei ole yhteensopiva pelin matriisin koon kanssa.\n\nTallennuksen koko: {len(tmp)}\nPelin koko: {count}")
                    print(f"ladattavan tallennuksen matriisin koko ei ole yhteensopiva pelin matriisin koon kanssa.\ntallennuksen koko: {len(tmp)}, pelin koko: {count}")
                else:
                    grid = tmp
                    print("lataa")
            except json.decoder.JSONDecodeError:
                messagebox.showerror("Korruptoitunut tallennus", "Ladattava tallennus on korruptoitunut eikä sitä voida ladata.")
                print("tallennus korruptoitunut")
        else:
            grid = generateGrid()
            messagebox.showinfo("Ei ladattavaa", "Tämä tallennuspaikka on tyhjä.")
            print("ei ladattavaa")

    @staticmethod
    def previous_save():
        global save_index
        if save_index > save_range[0]:
            save_index -= 1

    @staticmethod
    def next_save():
        global save_index
        if save_index < save_range[1]:
            save_index += 1

clear_button = menu_button(0, "Tyhjennä", button_functions.clear)
stop_button = menu_button(100, "Lopeta", button_functions.stop)
save_button = menu_button(200, "Tallenna", button_functions.save)
load_button = menu_button(300, "Lataa", button_functions.load)
previous_save_button = menu_button(400, "<", button_functions.previous_save)
next_save_button = menu_button(600, ">", button_functions.next_save)

while running:
    left_clicked = False
    right_clicked = False
    keys_pressed: Dict[int, bool] = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
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
                    tmpimggrid = loadImageAsGrid()
                    if tmpimggrid != None:
                        grid = tmpimggrid

    player_position: Tuple[int, int] = pygame.mouse.get_pos()

    screen.fill((64, 64, 64))

    clear_button.update(screen, player_position, left_pressed, left_clicked)
    stop_button.update(screen, player_position, left_pressed, left_clicked)
    save_button.update(screen, player_position, left_pressed, left_clicked)
    load_button.update(screen, player_position, left_pressed, left_clicked)
    previous_save_button.update(screen, player_position, left_pressed, left_clicked)
    next_save_button.update(screen, player_position, left_pressed, left_clicked)

    save_slot_text: pygame.Surface = font.render(str(save_index), True, WHITE)
    screen.blit(save_slot_text, (previous_save_button.rect.right + (next_save_button.rect.left - previous_save_button.rect.right) // 2  - save_slot_text.get_width() // 2, button_layer_height // 2 - save_slot_text.get_height() // 2))
    # pygame.draw.rect(screen, COLOURS_LIST[color_index], (width * count + margin * count - 47, 3, 44, 44))
    pygame.gfxdraw.box(screen, (size[0] - 47, 3, 44, 44), COLOURS_LIST[color_index])

    x = player_position[0]
    y = player_position[1] - button_layer_height

    mouse_column: Optional[int] = None
    mouse_row: Optional[int] = None

    if y > 0:
        mouse_column = min(x // (width + margin), count - 1)
        mouse_row = min(y // (height + margin), count - 1)

        if (left_pressed or right_pressed) and pygame.mouse.get_focused():

            if path_prediction and lastPathPredPos != None:
                pathPredLine: modules.line.Line = modules.line.Line(lastPathPredPos, (mouse_row, mouse_column))

                pathPredDist = pathPredLine.Distance
                predStep: float = (1.0 / pathPredDist) if pathPredDist > 0 else 0
                if predStep > 0: # If rounding rounds to zero, the app wont freeze... And also the above if statement works nicely with this
                    predI: float = 0.0
                    while predI < 1.0:
                        predPos = pathPredLine.Lerp(min(predI, 1.0))
                        grid[round(predPos[0])][round(predPos[1])] = color_index if not right_pressed else 0
                        predI += predStep

            grid[mouse_row][mouse_column] = color_index if not right_pressed else 0

            lastPathPredPos = (mouse_row, mouse_column)
        else:
            lastPathPredPos = None
    else:
        lastPathPredPos = None

    if DebugMode:
        screen.blit(font.render(format(clock.get_fps(), ".3f"), True, WHITE, BLACK), (button_layer_height / 2 - font_size / 2, button_layer_height / 2 - font_size / 2))

    for column in range(count):
        for row in range(count):
            # pygame.draw.rect(screen, COLOURS_LIST[grid[row][column]], (column * width + margin * column + margin, row * height + margin * row + margin + button_layer_height, width, height))
            renderMatrixUnit(screen, row, column, COLOURS_LIST[grid[row][column]])

    if draw_preview and mouse_column != None and mouse_row != None:
        overlay_color = COLOURS_LIST[color_index]
        renderMatrixUnit(screen, mouse_row, mouse_column, (overlay_color[0], overlay_color[1], overlay_color[2], 64))

    pygame.display.flip()

    clock.tick()

pygame.quit()
print("loppuu")