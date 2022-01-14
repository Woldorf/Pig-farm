import pygame,time
class Pig(pygame.sprite.Sprite):
    def __init__(self,fontsize,SCREENWIDTH,SCREENHEIGHT,GameScreen,statList,logger):
        pygame.sprite.Sprite.__init__(self)
        self.logger = logger
        self.logger.debug('init:'+str(statList))
        self.GAMESCREEN = GameScreen
        self.FONTSIZE = fontsize
        self.SCREENWIDTH = SCREENWIDTH
        self.SCREENHEIGHT = SCREENHEIGHT
        #Sprite stuff
        self.size=30+int(statList['PIG-STARTINGSIZE'])
        self.spritesheet=pygame.image.load('sprites/pig/pigsheet.png').convert()
        temp = self.spritesheet.get_rect()
        self.w = int(temp.width/4)
        self.h = int(temp.h)
        spriteCords = [(0,0,self.w,self.h),(self.w,0,self.w,self.h),(self.w*2,0,self.w,self.h),(self.w*3,0,self.w,self.h)]
        self.spriteList = []
        for i in spriteCords:
            rect = pygame.Rect(i)
            s = pygame.Surface(rect.size).convert()
            s.blit(self.spritesheet, (0, 0), rect)
            s.set_colorkey((0,0,0))
            self.spriteList.append(s)
        self.sCount = 0
        self.image=pygame.transform.scale(self.spriteList[0],(self.w,self.h))
        self.rect=self.image.get_rect(center=(SCREENWIDTH/2,SCREENHEIGHT/2))
        self.mask=pygame.mask.from_surface(self.image)
        #These 2 are based off the original orientation of the sprite
        self.faceLeft = True
        self.faceRight = False
        #Base stat stuff
        self.x=self.rect.x
        self.y=self.rect.y
        self.minSpeed = 1 + int(statList['PIG-MINSPEED'])
        self.speed=5+int(statList['PIG-STARTINGSPEED'])
        self.speedLoss = .25
        self.superSpeed=2
        self.highHealth=20 + int(statList['PIG-STARTINGHEALTH'])
        self.health=self.highHealth
        self.highStamina=5
        self.stamina=self.highStamina
        self.staminaGain = 1
        #Stamina loss is just self.superSpeed
        self.weight=10 + int(statList['PIG-STARTINGWEIGHT'])
        #self.obj=pygame.draw.circle(GAMESCREEN,self.color,self.cords,self.size)
        self.age=0
        #Colors:
        self.staminaColor=(255,0,0)
        self.weightColor=(255,0,0)
        self.healthColor=(255,0,0)
        #Max stats
        self.MAXWEIGHT = 70 + int(statList['PIG-STARTINGHEALTH'])*1.5
        self.MAXHEALTH = 40 + int(statList['PIG-MAXHEALTH'])
        self.MAXSIZE = 60 + int(statList['PIG-MAXSTAMINA'])
        self.MAXSTAMINA = 15
    def drawSelf(self):
        self.GAMESCREEN.blit(self.image,self.rect)
    def drawStats(self):
        xGap = 10
        yGap = 20
        listODicts=[{'text':'Health:','leftcords':{'x':xGap,'y':yGap},'color':self.healthColor,'size':self.FONTSIZE}]
        listODicts.append({'text':'Stamina:','leftcords':{'x':xGap,'y':listODicts[-1]['leftcords']['y']+yGap},'color':self.staminaColor,'size':self.FONTSIZE})
        listODicts.append({'text':('Speed: '+str(self.speed)+' steps/second'),'leftcords':{'x':xGap,'y':listODicts[-1]['leftcords']['y']+yGap},'color':self.staminaColor,'size':self.FONTSIZE})
        listODicts.append({'text':('Weight: '+str(self.weight)+' heavies'),'leftcords':{'x':xGap,'y':listODicts[-1]['leftcords']['y']+yGap},'color':self.weightColor,'size':self.FONTSIZE})
        return listODicts
    def moveSelf(self):
        superSpeed = False
        if pygame.key.get_pressed()[pygame.K_SPACE] and self.stamina > 0:
            self.stamina -= .5
            superSpeed = True
        if (pygame.key.get_pressed()[pygame.K_LEFT] or pygame.key.get_pressed()[pygame.K_a]) and self.rect.left > 0:
            if superSpeed:
                self.x -= self.speed + self.superSpeed
            else:
                self.x -= self.speed
            if not self.faceLeft:
                for index,i in enumerate(self.spriteList):
                    self.spriteList[index]=pygame.transform.flip(i,True,False)
                self.faceLeft = not self.faceLeft
                self.faceRight = not self.faceRight
        if (pygame.key.get_pressed()[pygame.K_RIGHT] or pygame.key.get_pressed()[pygame.K_d]) and self.rect.right < self.SCREENWIDTH:
            if superSpeed:
                self.x += self.speed + self.superSpeed
            else:
                self.x += self.speed
            if not self.faceRight:
                for index,i in enumerate(self.spriteList):
                    self.spriteList[index]=pygame.transform.flip(i,True,False)
                self.faceLeft = not self.faceLeft
                self.faceRight = not self.faceRight
        if (pygame.key.get_pressed()[pygame.K_UP] or pygame.key.get_pressed()[pygame.K_w]) and self.rect.top > 0:
            if superSpeed:
                self.y -= self.speed + self.superSpeed
            else:
                self.y -= self.speed
        if (pygame.key.get_pressed()[pygame.K_DOWN] or pygame.key.get_pressed()[pygame.K_s]) and self.rect.bottom < self.SCREENHEIGHT:
            if superSpeed:
                self.y += self.speed + self.superSpeed
            else:
                self.y += self.speed
    def updateSelf(self):
        if int(time.time()) % 3 == 0:
            if self.stamina != self.highStamina:
                self.stamina += self.staminaGain
            if self.stamina > self.highStamina:
                self.stamina = self.highStamina
        self.sCount += 1
        if self.sCount >= len(self.spriteList):
            self.sCount = 0
        self.image=pygame.transform.scale(self.spriteList[self.sCount],(self.w,self.h))
        self.rect=self.image.get_rect(center=(self.x,self.y))
        self.mask=pygame.mask.from_surface(self.image)
    def continueRound(self):
        increase = 20
        self.sCount = 0
        self.weight = self.weight/2
        self.MAXWEIGHT += increase
        temp = self.spritesheet.get_rect()
        self.highStamina = self.highStamina/2
        self.stamina = self.highStamina
        self.highHealth = self.highHealth/2
        self.health = self.highHealth
        #self.w = int(temp.width/4)
        #self.h = int(temp.h)
        self.x = self.SCREENWIDTH/2
        self.y = self.SCREENHEIGHT/2
        self.rect = self.image.get_rect(center=(self.x,self.y))
        self.healthColor = (255,0,0)
        self.staminaColor = (255,0,0)
        self.weightColor = (255,0,0)
        self.logger.info(f'New round: (x,y)-({self.x},{self.y}), MS-{self.MAXSTAMINA}, MH-{self.MAXHEALTH}, MW-{self.MAXWEIGHT}, w:{self.weight}, s:{self.highStamina}')
    #def debug(self):
    #    self.logger.debug('')