import tkinter
from tkinter.filedialog import askdirectory
from pygame import *
import xml.etree.ElementTree as ET
import json
import os
import time as Time
import copy


def offset_editor():
    root = tkinter.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    init()

    screen = display.set_mode((0, 0), FULLSCREEN)

    if not display.Info().current_w / display.Info().current_h == 1920 / 1080:
        BG = transform.scale(image.load("assets" + os.path.sep + "Images" + os.path.sep + "menuBG.png"), (1920, 1080))
    else:
        BG = transform.scale(image.load("assets" + os.path.sep + "Images" + os.path.sep + "menuBG.png"),
                             (display.Info().current_w, display.Info().current_h))

    BGtype = 0

    Font30 = font.SysFont("Comic Sans MS", 30)

    temp = Font30.render("Click to open folder", 1, (0, 0, 0))
    temp1 = temp.get_rect()
    clickHitboxWidth = temp1.width + 5
    clickHitboxHeight = temp1.height

    folderPath = None
    character = None

    keyModifier = None

    currentAnimation = 4
    currentFrame = 0
    currentSize = [1, 1]
    offset = [[[0, 0]] for _ in range(5)]

    markerPos1 = [0, 0]
    markerPos2 = [0, 0]

    def drawMarkers():
        temp = Rect(0, 0, 20, 2)
        temp.center = markerPos1
        draw.rect(screen, (255, 0, 0), temp)
        temp = Rect(0, 0, 2, 20)
        temp.center = markerPos1
        draw.rect(screen, (255, 0, 0), temp)
        temp = Rect(0, 0, 20, 2)
        temp.center = markerPos2
        draw.rect(screen, (255, 0, 0), temp)
        temp = Rect(0, 0, 2, 20)
        temp.center = markerPos2
        draw.rect(screen, (255, 0, 0), temp)

    def getAttibuteRect(data):
        return Rect(float(data.attrib["x"]), float(data.attrib["y"]), float(data.attrib["width"]),
                    float(data.attrib["height"]))

    def getNfirstCharacters(text, n):
        result = ""
        if n < len(text):
            for k in range(n):
                result = "{0}{1}".format(result, text[k])
            return result
        else:
            return text

    def getNlastCharacters(text, n):
        result = ""
        for k in range(n):
            result = "{1}{0}".format(result, text[-k - 1])
        return result

    def getXmlData(folderPath):
        XMLpath = folderPath + os.path.sep + "character.xml"
        characterImage = image.load(folderPath + os.path.sep + "character.png").convert_alpha()
        XMLfile = ET.parse(XMLpath).getroot()
        result = [[] for k in range(5)]
        for data in XMLfile:
            name = data.attrib["name"]
            tempResult = ""
            for k in range(len(name)):
                if name[k] == "_":
                    tempResult = "{0}{1}".format(tempResult, " NOTE ")
                else:
                    tempResult = "{0}{1}".format(tempResult, name[k].upper())
            data.attrib["name"] = tempResult
        for data in XMLfile:
            name = data.attrib["name"]
            tempResult = ""
            temp = False
            for k in range(len(name)):
                if temp:
                    tempResult = "{0}{1}".format(tempResult, name[k])
                if name[k] == " ":
                    temp = True
            if tempResult == "":
                tempResult = name
            else:
                data.attrib["name"] = tempResult
        for data in XMLfile:
            name = data.attrib["name"]
            if getNfirstCharacters(name, 9) == "NOTE IDLE" or getNfirstCharacters(name, 4) == "IDLE":
                name = "idle dance{0}".format(getNlastCharacters(name, 4))
            data.attrib["name"] = name
        for data in XMLfile:
            name = data.attrib["name"]
            if getNfirstCharacters(name, 10) == "IDLE DANCE":
                data.attrib["name"] = name.lower()
        for data in XMLfile:
            name = data.attrib["name"]
            if getNfirstCharacters(name, 2) == "UP":
                name = "NOTE UP{0}".format(getNlastCharacters(name, 4))
            if getNfirstCharacters(name, 4) == "DOWN":
                name = "NOTE DOWN{0}".format(getNlastCharacters(name, 4))
            if getNfirstCharacters(name, 4) == "LEFT":
                name = "NOTE LEFT{0}".format(getNlastCharacters(name, 4))
            if getNfirstCharacters(name, 5) == "RIGHT":
                name = "NOTE RIGHT{0}".format(getNlastCharacters(name, 4))
            data.attrib["name"] = name
        for data in XMLfile:
            if getNfirstCharacters(data.attrib["name"], 9) == "NOTE LEFT" and len(data.attrib["name"]) == 13:
                result[0].append(characterImage.subsurface(getAttibuteRect(data)))
            if getNfirstCharacters(data.attrib["name"], 9) == "NOTE DOWN" and len(data.attrib["name"]) == 13:
                result[1].append(characterImage.subsurface(getAttibuteRect(data)))
            if getNfirstCharacters(data.attrib["name"], 7) == "NOTE UP" and len(data.attrib["name"]) == 11:
                result[2].append(characterImage.subsurface(getAttibuteRect(data)))
            if getNfirstCharacters(data.attrib["name"], 10) == "NOTE RIGHT" and len(data.attrib["name"]) == 14:
                result[3].append(characterImage.subsurface(getAttibuteRect(data)))
            if getNfirstCharacters(data.attrib["name"], 10) == "idle dance" and len(data.attrib["name"]) == 14:
                result[4].append(characterImage.subsurface(getAttibuteRect(data)))
        return result

    class Character:
        def __init__(self, name, characterNum):
            if name != "None":
                self.texture = getXmlData(name)
                try:
                    self.textureDirection = json.load(open(name + os.path.sep + "characterData.json"))[
                        "texture_direction"]
                except:
                    self.textureDirection = "Right"
                if self.textureDirection == "Left":
                    for k in range(5):
                        for x in range(len(self.texture[k])):
                            self.texture[k][x] = transform.flip(self.texture[k][x], True, False)
                    temp1 = self.texture[0]
                    self.texture[0] = self.texture[3]
                    self.texture[3] = temp1
                    for k in range(5):
                        for x in range(len(offset[k])):
                            for y in range(2):
                                offset[k][x][y] *= -1
            else:
                self.texture = [[Font30.render("", 1, (255, 255, 255))] for k in range(5)]

    def chooseDirectory(screen):
        display.toggle_fullscreen()
        folder_path = askdirectory(parent=root,
                                   initialdir="assets" + os.path.sep + "Images" + os.path.sep + "characters",
                                   title="Choose character file to start editing offsets")
        screen = display.set_mode((0, 0), FULLSCREEN)
        return folder_path

    def drawCharacter():
        temp = character.texture[currentAnimation][currentFrame]
        temp = transform.scale(temp, (int(temp.get_width() * currentSize[0]), int(temp.get_height() * currentSize[1])))
        temp1 = temp.get_rect()
        temp1.midbottom = (300 + (offset[currentAnimation][currentFrame][0] * currentSize[0]),
                           display.Info().current_h - 100 - (
                                   offset[currentAnimation][currentFrame][1] * currentSize[1]))
        screen.blit(temp, temp1)

    lastPressed = 0
    pressedList = []

    while True:
        for events in event.get():
            if events.type == QUIT or (events.type == KEYDOWN and events.key == K_ESCAPE):
                return None
            if events.type == MOUSEBUTTONDOWN and not (
                    display.Info().current_w - clickHitboxWidth < events.pos[0] < display.Info().current_w and 0 <
                    events.pos[1] < clickHitboxHeight):
                if events.button == 1:
                    markerPos1 = events.pos
                if events.button == 3:
                    markerPos2 = events.pos
            if events.type == KEYDOWN:
                if events.key == K_b:
                    BGtype += 1
                    BGtype %= 3
                if events.key == K_LSHIFT:
                    if keyModifier is None:
                        keyModifier = "Shift"
                if events.key == K_LCTRL:
                    if keyModifier is None:
                        keyModifier = "Control"
                if events.key == K_LALT:
                    if keyModifier is None:
                        keyModifier = "Alt"
                if keyModifier is None:
                    if events.key == K_UP:
                        offset[currentAnimation][currentFrame][1] += 1
                    if events.key == K_DOWN:
                        offset[currentAnimation][currentFrame][1] -= 1
                    if events.key == K_RIGHT:
                        offset[currentAnimation][currentFrame][0] += 1
                    if events.key == K_LEFT:
                        offset[currentAnimation][currentFrame][0] -= 1
                    if events.key == K_c and currentFrame < len(character.texture[currentAnimation]) - 1:
                        offset[currentAnimation][currentFrame + 1] = copy.copy(offset[currentAnimation][currentFrame])
                        currentFrame += 1
                if keyModifier == "Shift":
                    if events.key in [K_LEFT, K_DOWN, K_UP, K_RIGHT]:
                        pressedList.append(events.key)
                if keyModifier != "Shift":
                    pressedList = []
                if keyModifier == "Alt":
                    if events.key == K_UP:
                        currentSize[1] += 0.05
                    if events.key == K_DOWN and currentSize[1] > 0.05:
                        currentSize[1] -= 0.05
                    if events.key == K_RIGHT:
                        currentSize[0] += 0.05
                    if events.key == K_LEFT and currentSize[0] > 0.05:
                        currentSize[0] -= 0.05
                if keyModifier == "Control" and character is not None:
                    if events.key == K_UP and currentAnimation < 4:
                        currentAnimation += 1
                        currentFrame = 0
                    if events.key == K_DOWN and currentAnimation > 0:
                        currentAnimation -= 1
                        currentFrame = 0
                    if events.key == K_RIGHT and currentFrame < len(character.texture[currentAnimation]) - 1:
                        currentFrame += 1
                    if events.key == K_LEFT and currentFrame > 0:
                        currentFrame -= 1
                    if events.key == K_s:
                        if character.textureDirection == "Left":
                            temp = offset[0]
                            offset[0] = offset[3]
                            offset[3] = temp
                            for k in range(5):
                                for x in range(len(offset[k])):
                                    for y in range(2):
                                        offset[k][x][y] *= -1
                        json.dump({"offset": offset}, open(folderPath + os.path.sep + "offset.json", "w"))
                        print("Offset file saved!")
                        if character.textureDirection == "Left":
                            temp = offset[0]
                            offset[0] = offset[3]
                            offset[3] = temp
                            for k in range(5):
                                for x in range(len(offset[k])):
                                    for y in range(2):
                                        offset[k][x][y] *= -1
            if events.type == KEYUP:
                if events.key in [K_LSHIFT, K_LCTRL, K_LALT]:
                    keyModifier = None
                if keyModifier == "Shift" and events.key in pressedList:
                    pressedList.remove(events.key)
            if events.type == MOUSEBUTTONDOWN:
                if events.button == 1:
                    if display.Info().current_w - clickHitboxWidth < events.pos[0] < display.Info().current_w:
                        if 0 < events.pos[1] < clickHitboxHeight:
                            try:
                                folderPath = chooseDirectory(screen)
                                if folderPath is not None and folderPath != "":
                                    characterName = ""
                                    tempPos = 0
                                    for k in range(len(folderPath)):
                                        if folderPath[k] == "/" or folderPath[k] == os.path.sep:
                                            tempPos = k
                                    for k in range(tempPos + 1, len(folderPath)):
                                        characterName = "{0}{1}".format(characterName, folderPath[k])
                                    character = Character(folderPath, 1)
                                    currentAnimation = 4
                                    currentFrame = 0
                                    try:
                                        offset = json.load(open(folderPath + os.path.sep + "offset.json"))["offset"]
                                    except:
                                        offset = [[] for k in range(5)]
                                        for k in range(5):
                                            for x in range(len(character.texture[k])):
                                                offset[k].append([0, 0])
                            except:
                                print("An error occurred while loading the files")
        if keyModifier == "Shift":
            if Time.time() - lastPressed > 0.1:
                if K_UP in pressedList:
                    offset[currentAnimation][currentFrame][1] += 1
                    lastPressed = Time.time()
                if K_DOWN in pressedList:
                    offset[currentAnimation][currentFrame][1] -= 1
                    lastPressed = Time.time()
                if K_RIGHT in pressedList:
                    offset[currentAnimation][currentFrame][0] += 1
                    lastPressed = Time.time()
                if K_LEFT in pressedList:
                    offset[currentAnimation][currentFrame][0] -= 1
                    lastPressed = Time.time()
        screen.fill((0, 0, 0))
        if BGtype == 0:
            screen.blit(BG, (0, 0))
        elif BGtype == 1:
            screen.fill((0, 0, 0))
        elif BGtype == 2:
            screen.fill((255, 255, 255))
        if BGtype != 2:
            color = (255, 255, 255)
        else:
            color = (0, 0, 0)
        drawMarkers()
        screen.blit(Font30.render("Background type: " + ["Menu background", "Black", "White"][BGtype], 1, color),
                    (5, 0))
        temp = Font30.render("Click to open folder", 1, color)
        temp1 = temp.get_rect()
        temp1.topright = (display.Info().current_w - 5, 0)
        screen.blit(temp, temp1)
        temp = Font30.render(
            "Current size multiplier: {0} x {1}".format(round(currentSize[0], 2), round(currentSize[1], 2)), 1,
            (255, 255, 255))
        temp1 = temp.get_rect()
        temp1.bottomleft = (5, display.Info().current_h)
        screen.blit(temp, temp1)
        temp = Font30.render("Offset for this frame: x={0} y={1}".format(offset[currentAnimation][currentFrame][0],
                                                                         offset[currentAnimation][currentFrame][1]), 1,
                             (255, 255, 255))
        temp1 = temp.get_rect()
        temp1.bottomright = (display.Info().current_w - 5, display.Info().current_h)
        screen.blit(temp, temp1)
        temp = Font30.render("Current animation: {0}".format(["Left", "Down", "Up", "Right", "Idle"][currentAnimation]),
                             1,
                             (255, 255, 255))
        temp1 = temp.get_rect()
        temp1.topleft = (5, 30)
        screen.blit(temp, temp1)
        temp = Font30.render("Current frame: {0} / {1}".format(currentFrame + 1, len(
            character.texture[currentAnimation]) if character is not None else 1), 1, (255, 255, 255))
        temp1 = temp.get_rect()
        temp1.topleft = (5, 60)
        screen.blit(temp, temp1)
        if character is not None:
            drawCharacter()
        display.flip()
