#!/usr/bin/python
"""
Made and produced by Kurced Keyboard Studios, all rights reserved.
Feel free to edit sound volumes located on lines 66-67.
"""
#Working on:
#Researching screen and researching itself

import random,pygame,time,sys,logging
from pygame.locals import *
#Home brewed libraries:
from wolf import Wolf as WOLF
from pig import Pig as PIG

#library initalizing and whatnot
SEED = random.randrange(sys.maxsize)
random.seed(SEED)
logging.basicConfig(filename='work.log',filemode='w',format='%(name)s @ [%(asctime)s] - %(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M %p')
logging.root.setLevel(level=logging.DEBUG)
logger=logging.getLogger('Butler')
piglogger = logger.getChild('Pig')
pygame.init()
pygame.mixer.init()
pygame.display.set_caption('Pig')
flags = pygame.SCALED# | pygame.FULLSCREEN
GAMESCREEN = pygame.display.set_mode((600,600),flags=flags)

SCREENWIDTH=pygame.display.Info().current_w
SCREENHEIGHT=pygame.display.Info().current_h
TPS = 10
TPSCLOCK = pygame.time.Clock()
MAPWIDTH = SCREENWIDTH #2000
MAPHEIGHT = SCREENHEIGHT #2000

#Do a quick debug help:
debuglist = {'SCREENDATA':[SCREENWIDTH,SCREENHEIGHT],'MAPDATA':[MAPWIDTH,MAPHEIGHT],'GAMESCREENDATA':GAMESCREEN,'PYGAMEFLAGS':flags}
logger.debug('Everything inialized:')
for i in debuglist:
    logger.info(str(i)+' - '+str(debuglist[i]))

#Make the background data:
mapSheet = pygame.image.load('sprites/map/map.png').convert_alpha()

FONTSIZE = 18
#Colors:
#             R    G    B
GRAY      = (100, 100, 100)
NAVYBLUE  = (  0,   0, 150)
WHITE     = (255, 255, 255)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
BLUE      = (  0,   0, 255)
YELLOW    = (255, 255,   0)
ORANGE    = (255, 128,   0)
PURPLE    = (255,   0, 255)
CYAN      = (  0, 255, 255)
BLACK     = (  0,   0,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)

MAXWOLVES = 3
WOLFDELAY = 10
CAMERASLACK = 30

class TEXT:
    def __init__(self,dict=None,**kwargs):
        if dict != None:
            kwargs = dict
        self.text=kwargs['text']
        self.color = kwargs['color']
        self.size = kwargs['size']
        self.words = pygame.font.Font("freesansbold.ttf",self.size).render(self.text,True,self.color)
        self.rect = self.words.get_rect()
        try:
            self.x = kwargs['leftcords']['x']
            self.y = kwargs['leftcords']['y']
            self.rect.topleft = (self.x,self.y)
        except:
            #The error here is annoying but it checks if there's a leftcords part of kwargs because I frequently position stuff based off the top left corner
            try:
                self.x=kwargs['rightcords']['x']
                self.y=kwargs['rightcords']['y']
                self.rect.topright = (self.x,self.y)
            except:
                self.x = kwargs['x']
                self.y = kwargs['y']
                self.rect.center = (self.x,self.y)

    def drawSelf(self):
        self.words = pygame.font.Font("freesansbold.ttf",self.size).render(self.text,True,self.color)
        GAMESCREEN.blit(self.words,self.rect)

class FOOD(pygame.sprite.Sprite):
    def __init__(self,pig,shop):
        pygame.sprite.Sprite.__init__(self)
        pGap = 50 #Closest the food can be generated to the pig
        bGap = 20 #Closest to the world border the food can generate
        xF = False
        yF = False
        while not xF:
            x = random.randrange(bGap,MAPWIDTH-bGap)
            if (x <= pig.x - pGap or x >= pig.x + pGap) and x > shop.rect.right:
                xF = True
        while not yF:
            y = random.randrange(bGap,MAPHEIGHT-bGap)
            if (y <= pig.y - pGap or y >= pig.y + pGap ) and y > shop.rect.bottom:
                yF = True

        self.color = YELLOW
        self.size = 30
        self.cords = (x,y)

        originalImage=pygame.image.load('sprites/slop.png').convert_alpha()
        self.image=pygame.transform.scale(originalImage,(self.size,self.size))
        self.rect=self.image.get_rect(center=(self.cords))
        self.mask=pygame.mask.from_surface(self.image)
        self.mask.scale((self.rect.height,self.rect.width))

        self.healthGain = 3
        self.weightGain = 3
        self.staminaGain = .5
    def update(self):
        GAMESCREEN.blit(self.image,self.rect)

class BUTCHERSHOP(pygame.sprite.Sprite):
    def __init__(self):
        rect1 = pygame.Rect(0,0,20,30)
        rect2 = pygame.Rect(mapSheet.get_rect().w/2,0,20,30)
        self.dayimage = pygame.Surface(rect1.size).convert()
        self.nightimage = pygame.Surface(rect2.size).convert()
        self.dayimage.blit(mapSheet,(0,0),rect1)
        #self.nightimage.blit(mapSheet,(0,0),rect2)
        self.dayimage = pygame.transform.scale(self.dayimage,(120,170))
        self.mask = pygame.mask.from_surface(self.dayimage)
        self.rect = self.dayimage.get_rect()

class BACKGROUND:
    def __init__(self):
        r = mapSheet.get_rect()
        rect1 = pygame.Rect(0,0,r.w/2,r.h)
        rect2 = pygame.Rect(r.w/2,0,r.w/2,r.h)
        self.dayimage = pygame.Surface(rect1.size).convert()
        self.nightimage = pygame.Surface(rect2.size).convert()
        self.dayimage.blit(mapSheet,(0,0),rect1)
        self.nightimage.blit(mapSheet,(0,0),rect2)
        self.dayimage = pygame.transform.scale(self.dayimage,(SCREENWIDTH,SCREENHEIGHT))
        self.nightimage = pygame.transform.scale(self.nightimage,(SCREENWIDTH,SCREENHEIGHT))
    def drawSelf(self,time):
        if time == 'day':
            GAMESCREEN.blit(self.dayimage,(0,0))
        else:
            GAMESCREEN.blit(self.nightimage,(0,0))

class SYSTEM:
    def __init__(self):
        self.background = BACKGROUND()
        self.butcherShop  = BUTCHERSHOP()
        temp = readFile('data/money.txt')
        self.cash = int(float(temp['CASH']))
        self.earnings = 0
    def draw(self,time):
        self.background.drawSelf(time)

def readFile(file):
    with open(file,'r') as File:
        fileLines = File.readlines()
    for index,i in enumerate(fileLines):
        fileLines[index]=i.replace('\n','')
    returnData = {}
    for index,i in enumerate(fileLines):
        if index%2 == 0 or index == 0:
            data = fileLines[index+1]
            returnData[i.replace('--','')] = data
    return returnData

def writeFile(dict,file):
    with open(file,'w') as File:
        for i in dict:
            line = '--'+str(i.upper())+'\n'
            line2 = str(dict[i])+'\n'
            File.writelines([line,line2])

def terminate(pig=None):
    #if pig != None:
    #    pig.debug()
    logger.debug('No errors. Exiting game safely')
    logger.info('Seed:'+str(SEED))
    pygame.quit()
    sys.exit()

def makeWolves(wolfList):
    while len(wolfList) < MAXWOLVES:
        wolfList.add(WOLF(GAMESCREEN,SCREENHEIGHT,SCREENHEIGHT))
    return wolfList

def makeFood(FoodGroup,pig,systemData):
    #Max food - 5
    while len(FoodGroup) < 5:
        #Generate the actual food objects:
        temp = FOOD(pig,systemData.butcherShop)
        FoodGroup.add(temp)
    return FoodGroup

def makeCredits(masterList,listToAdd):
    headerColor = ORANGE
    nameColor = CYAN
    headerSize = 40
    nameSize = 40
    headerToNameGap = 30
    nameToHeaderGap = 60
    nameToNameGap = 30
    for index,i in enumerate(listToAdd):
        if index == 0:
            masterList.append(TEXT(text=i,x=SCREENWIDTH/2,y=masterList[-1].rect.bottom+nameToHeaderGap,color=headerColor,size=headerSize))
        elif index == 1:
            masterList.append(TEXT(text=i,x=SCREENWIDTH/2,y=masterList[-1].rect.bottom+headerToNameGap,color=nameColor,size=nameSize))
        else:
            masterList.append(TEXT(text=i,x=SCREENWIDTH/2,y=masterList[-1].rect.bottom+nameToNameGap,color=nameColor,size=nameSize))
    return masterList

def startScreen(systemData):
    yGap = 30
    optionList = []
    selectedOption = 0
    xGap=20
    yGap=30
    tempList = ['RESEARCH','SETTINGS','QUIT','CREDITS']
    optionList.append(TEXT(text='START GAME',x=SCREENWIDTH/2,y=SCREENHEIGHT/2,color=BLUE,size=FONTSIZE))
    for index,i in enumerate(tempList):
        if index == 0:
            optionList.append(TEXT(text=i,leftcords={'x':xGap,'y':yGap},color=BLUE,size=FONTSIZE))
        else:
            optionList.append(TEXT(text=i,leftcords={'x':xGap,'y':optionList[-1].rect.bottom+yGap},color=BLUE,size=FONTSIZE))
    enter = False
    while not enter:
        systemData.background.drawSelf('night')

        for index,i in enumerate(optionList):
            if index == selectedOption:
                i.color = RED
            else:
                i.color = BLUE
            i.drawSelf()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_RETURN or event.key == K_SPACE:
                    enter = not enter
                elif event.key == K_ESCAPE:
                    terminate() 
                elif event.key == K_TAB or event.key == K_s or event.key == K_DOWN:
                    selectedOption += 1
                    if selectedOption >= len(optionList):
                        selectedOption = 0  
                elif event.key == K_w or event.key == K_UP:
                    selectedOption -= 1
                    if selectedOption < 0:
                        selectedOption = len(optionList)-1
    if optionList[selectedOption].text == 'START GAME':
        game(PIG(FONTSIZE,SCREENWIDTH,SCREENHEIGHT,GAMESCREEN,readFile('data/stats.txt'),piglogger),systemData)
    elif optionList[selectedOption].text == 'QUIT':
        terminate()
    elif optionList[selectedOption].text == 'CREDITS':
        creditsScreen(systemData)
    elif optionList[selectedOption].text == 'RESEARCH':
        researchScreen(systemData)
    #elif optionList[selectedOption].text == 'SETTINGS':
    #    settingsScreen(pig)

"""def settingScreen(pig):
    imageList=[]
    settings = pygame.image.load("Images/SettingsButton.png")
    imageList.append({"img":settings,"cords":(SCREENWIDTH-30,SCREENHEIGHT-30)})
    start = pygame.image.load("Images/StartButton.png")
    imageList.append({"img":start,"cords":(SCREENHEIGHT/2,SCREENHEIGHT/2)})
    while True:
        GAMESCREEN.fill(GREEN)
        pig.drawSelf()
        for i in imageList:
            r = i["img"].get_rect()
            r.center = i["cords"]
            GAMESCREEN.blit(i,r)"""

def pauseScreen():
    spacer = 20
    paused = TEXT(text="PAUSED - \"P\" TO RETURN",x=SCREENWIDTH/2,y=SCREENHEIGHT/2,color=RED,size=FONTSIZE)
    quit = TEXT(text="QUIT GAME - \"Q\"", x=SCREENWIDTH/2,y=paused.rect.bottom + spacer,color=RED,size=FONTSIZE)
    paused.drawSelf()
    quit.drawSelf()

def midRound(pig,systemData):
    if pig.health <= 0:
        systemData.earnings = 0
    else:
        systemData.earnings += round(pig.weight/(pig.health/pig.speed),2)*5

    yGap = 30
    ToDraw = []
    options = []
    ToDraw.append(TEXT(text=('Wallet: '+str(round(systemData.cash,2))+'$'),x=SCREENWIDTH/4,y=SCREENHEIGHT/3,color=BLACK,size=FONTSIZE))
    ToDraw.append(TEXT(text=('Estimated Earnings: '+str(round(float(int(systemData.earnings)),2))+'$'),x=ToDraw[-1].rect.right+(SCREENWIDTH/4),y=SCREENHEIGHT/3,color=BLACK,size=FONTSIZE))
    ToDraw.append(TEXT(text=('Rounds Survived: '+str(pig.age)),x=SCREENWIDTH/2,y=ToDraw[-1].rect.bottom + yGap,color=BLACK,size=FONTSIZE))
    options.append(TEXT(text='CONTINUE',x=SCREENWIDTH/2,y=ToDraw[-1].rect.bottom+yGap,color=BLACK,size=FONTSIZE))
    options.append(TEXT(text='CASH OUT',x=SCREENWIDTH/2,y=options[-1].rect.bottom+yGap,color=BLACK,size=FONTSIZE))
    gameOver = False
    selectedOption = 0
    while True:
        systemData.draw('night')

        for index,i in enumerate(options):
            if selectedOption == index:
                i.color = RED
            else:
                i.color = BLACK
            i.drawSelf()

        for i in ToDraw:
            i.drawSelf()

        TPSCLOCK.tick(TPS)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate(pig)
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate(pig)
                elif event.key == K_SPACE or event.key == K_RETURN:
                    if options[selectedOption].text == 'CONTINUE':
                        gameOver = False
                        return pig,gameOver,systemData
                    else:
                        gameOver = True
                        systemData.cash += systemData.earnings
                        writeFile({'cash':round(systemData.cash,2),'highscore':pig.age},'data/money.txt')
                        return pig, gameOver,systemData
                elif event.key == K_TAB or event.key == K_s or event.key == K_DOWN:
                    selectedOption += 1
                    if selectedOption >= len(options):
                        selectedOption = 0
                elif event.key == K_w or event.key == K_UP:
                    selectedOption -= 1
                    if selectedOption < 0:
                        selectedOption = len(options)-1

def creditsScreen(systemData):
    masterList = []
    scrollSpeed = 3
    headerColor = ORANGE
    headerSize = 40
    headerToNameGap = 30
    localTPS = 40

    masterList.append(TEXT(text='CREDITS',x=SCREENWIDTH/2,y=SCREENHEIGHT,color=headerColor,size=headerSize+10))
    masterList.append(TEXT(text='Pig - Kurced Studios',x=SCREENWIDTH/2,y=masterList[-1].rect.bottom+headerToNameGap,color=headerColor,size=headerSize+10))    
    
    masterList = makeCredits(masterList,['DEVELOPERS','Woldorf'])
    masterList = makeCredits(masterList,['CONTRIBUTERS','Woldorf','Quantavious'])
    masterList = makeCredits(masterList,['ARTISTS','Quantavious'])
    masterList = makeCredits(masterList,['ALPHA TESTERS','Woldorf','Quantavious'])
    masterList = makeCredits(masterList,['ESCAPE TO EXIT'])
    
    #Other types of things to display;
    #Special Thanks
    #Donators

    while True:
        systemData.draw('night')
        for i in masterList:
            if i == masterList[-1] and masterList[-1].rect.y <= SCREENHEIGHT/2:
                i.rect.y = SCREENHEIGHT/2
            i.rect.y -= scrollSpeed
            i.drawSelf()

        TPSCLOCK.tick(localTPS)
        pygame.display.flip()

        for i in pygame.event.get():
            if i.type == QUIT:
                terminate()
            elif i.type == KEYDOWN and i.key == K_ESCAPE:
                return

def game(pig,systemData):
    pig.age += 1 #Basically round count
    FoodGroup = pygame.sprite.Group()
    wolfGroup = pygame.sprite.Group()
    FoodGroup=makeFood(FoodGroup,pig,systemData)
    paused = False
    roundOver = False
    while True:
        systemData.draw('day')
        pig.drawSelf()
        tempList=[]
        for i in pig.drawStats():
            tempList.append(TEXT(dict=i))
            tempList[-1].drawSelf()
            xGap = 5
            rectInflation = 10
            if i['text'] == 'Health:':
                color = BLUE
                if pig.highHealth==pig.MAXHEALTH:
                    color = ORANGE
                pygame.draw.rect(GAMESCREEN,RED,pygame.Rect(tempList[-1].rect.right+xGap,tempList[-1].rect.top,pig.highHealth*rectInflation,tempList[-1].rect.height))
                pygame.draw.rect(GAMESCREEN,color,pygame.Rect(tempList[-1].rect.right+xGap,tempList[-1].rect.top,pig.health*rectInflation,tempList[-1].rect.height))
            elif i['text'] == 'Stamina:':
                color = BLUE
                if pig.highStamina==pig.MAXSTAMINA:
                    color = ORANGE
                pygame.draw.rect(GAMESCREEN,RED,pygame.Rect(tempList[-1].rect.right+xGap,tempList[-1].rect.top,pig.highStamina*rectInflation,tempList[-1].rect.height))
                pygame.draw.rect(GAMESCREEN,color,pygame.Rect(tempList[-1].rect.right+xGap,tempList[-1].rect.top,pig.stamina*rectInflation,tempList[-1].rect.height))
        FoodGroup=makeFood(FoodGroup,pig,systemData)
        FoodGroup.update()
        wolfGroup=makeWolves(wolfGroup)
        wolfGroup.update(GAMESCREEN)

        if paused:
            pauseScreen()
        
        TPSCLOCK.tick(TPS)
        pygame.display.flip()

        for i in pygame.event.get():
            if i.type == QUIT:
                terminate(pig)

        if pygame.key.get_pressed()[pygame.K_p]:
            if paused:
                logger.info('PAUSED@'+str(time.asctime()))
            else:
                logger.info('UNPAUSED@'+str(time.asctime()))
            paused = not paused
        elif pygame.key.get_pressed()[pygame.K_ESCAPE]:
            terminate(pig)

        if not paused:
            if pig.weight >= 30 and int(time.time())%WOLFDELAY == 0:
                for w in wolfGroup:
                    if not w.engaged:
                        if random.randint(10,30) == w.engageDelay:
                            w.engaged = True
            pig.updateSelf()
            pig.moveSelf()
            #Wolf collision
            for w in wolfGroup:
      
                if w.engaged:
                    w.moveSelf(pig)
                    if isinstance(pygame.sprite.collide_mask(w,pig),tuple):
                        if int(time.time()) % w.damageDelay == 0:
                            errorPlace = 0 
                            for index,i in enumerate(w.attackSprites):
                                if w.sCount + index >= len(w.spriteList):
                                    errorPlace = w.sCount + index
                                w.spriteList[(w.sCount + index)-errorPlace] = i
                            pig.health -= w.damage
                            w.damageDelay = random.randrange(1,10)
                        if pig.health < 0:
                            roundOver=True
                            pig,gameOver,systemData = midRound(pig,systemData)
            #Butcher shop collision
            if isinstance(pygame.sprite.collide_mask(pig,systemData.butcherShop),tuple):
                pig,gameOver,systemData = midRound(pig,systemData)
                roundOver = True
        #Food colision 
        for food in FoodGroup:  
            if isinstance(pygame.sprite.collide_mask(food,pig),tuple):
                pig.health += food.healthGain
                pig.weight += food.weightGain
                pig.size += food.weightGain
                pig.h += 1
                pig.w += 1
                pig.highStamina += food.staminaGain
                pig.highHealth += food.weightGain/2
                if pig.health > pig.highHealth:
                    pig.health = pig.highHealth
                if pig.highHealth > pig.MAXHEALTH:
                    pig.highHealth = pig.MAXHEALTH
                    pig.healthColor = ORANGE
                if pig.weight >= pig.MAXWEIGHT:
                    pig.weight = pig.MAXWEIGHT
                    pig.weightColor = ORANGE
                if pig.size > pig.MAXSIZE:
                    pig.size = pig.MAXSIZE
                if pig.highStamina >= pig.MAXSTAMINA:
                    pig.highStamina = pig.MAXSTAMINA
                    pig.speedColor = ORANGE
                if pig.speed > pig.minSpeed:
                    pig.speed -= pig.speedLoss
                elif pig.speed == pig.minSpeed:
                    pig.stamina += pig.staminaGain
                FoodGroup.remove(food)
        if roundOver:
            if gameOver:
                return
            else:
                pig.continueRound()
                FoodGroup.empty()
                wolfGroup.empty()
                roundOver = False

def researchScreen(systemData):
    xGap=30
    yGap=50
    color = CYAN
    maxUpgrades = 5
    upgradeSize = 10
    upgradeColorLocked = DARKGRAY
    upgradeColorUnLocked = ORANGE
    upgradeColorPurchased = GREEN

    statList=readFile('data/stats.txt')
    priceList=readFile('data/prices.txt')
    textList = [TEXT(text='RESEARCH',color=ORANGE,size=FONTSIZE*2,x=SCREENWIDTH/2,y=SCREENHEIGHT/12)]
    optionList = ['Starting Health','Starting Speed','Starting Weight','Max Stamina','Minimum Speed'] #Needs to be in the order of the stats.txt file
    for i in optionList:
        if i == optionList[0]:
            textList.append(TEXT(text=i,color=color,size=FONTSIZE,leftcords={'x':xGap,'y':SCREENHEIGHT/6}))
        else:
            textList.append(TEXT(text=i,color=color,size=FONTSIZE,leftcords={'x':xGap,'y':textList[-1].rect.bottom+yGap}))

    for index,i in enumerate(priceList):
        if i.startswith('PIG'):
            if int(statList[i]) == 0:
                temp = int(list(priceList.values())[index])
            else:
                temp = int(statList[i]) * int(list(priceList.values())[index])

            if temp == int(list(priceList.values())[0]):
                textList.append(TEXT(text=(str(temp)+'$'),color=color,size=FONTSIZE,rightcords={'x':SCREENWIDTH-xGap,'y':textList[1].rect.top}))
            else:
                textList.append(TEXT(text=(str(temp)+'$'),color=color,size=FONTSIZE,rightcords={'x':SCREENWIDTH-xGap,'y':textList[-1].rect.bottom+yGap}))  

    textList.append(TEXT(text=('DOUGH IN WALLET: '+str(round(systemData.cash,2))+'$'),color = CYAN,size=FONTSIZE,x=SCREENWIDTH/2,y=textList[-1].rect.bottom+ yGap*2))
    textList.append(TEXT(text='',color=CYAN,size=FONTSIZE,x=SCREENWIDTH/2,y=textList[-1].rect.bottom+yGap))

    selectedOption = 0
    while True:
        systemData.draw('night')
        for i in textList:
            i.drawSelf()

        circleCenterX = textList[0].rect.right+xGap
        circleCenterY = textList[0].rect.centery

        for index,i in enumerate(statList):
            placement = 0
            if textList[index+1].text.find('$')==-1:
                circleCenterX = textList[index+1].rect.right+xGap
                circleCenterY = textList[index+1].rect.centery
                while placement < maxUpgrades:
                    upCount = int(statList[i])
                    if placement < upCount:
                        color = upgradeColorPurchased
                    elif placement == upCount:
                        if index == selectedOption:
                            color = WHITE
                        else:
                            color = upgradeColorUnLocked
                    elif placement > upCount:
                        color = upgradeColorLocked
                    pygame.draw.circle(GAMESCREEN,color,(circleCenterX,circleCenterY),upgradeSize)
                    placement+=1
                    circleCenterX += xGap
                circleCenterY += yGap

        pygame.display.flip()

        for i in pygame.event.get():
            if i.type == QUIT:
                terminate()
            elif i.type == KEYDOWN:
                if i.key == K_ESCAPE:
                    writeFile(statList,'data/stats.txt')
                    return
                elif i.key == K_TAB or i.key == K_DOWN or i.key == K_s:
                    selectedOption += 1
                    if selectedOption >= len(optionList):
                        selectedOption = 0
                elif i.key == K_w or i.key == K_UP:
                    selectedOption -= 1
                    if selectedOption < 0:
                        selectedOption = len(optionList)-1

#Main while loop:
while True:
    #Game only breaks by using the terminate() function
    logger.info('Pig initlialized, entering the starting screen')
    systemData = SYSTEM()
    startScreen(systemData)