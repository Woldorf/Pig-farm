#File to hold all the wolf data
import pygame,random
class Wolf(pygame.sprite.Sprite):
    def __init__(self,Gamescreen,SCREENWIDTH,SCREENHEIGHT): 
        pygame.sprite.Sprite.__init__(self)
        self.GAMESCREEN = Gamescreen
        gap = -100
        x = random.randrange(gap,0)
        x2 = random.randrange(SCREENWIDTH,SCREENWIDTH-gap)
        self.x = random.choice([x,x2])
        y = random.randrange(gap,0)
        y2 = random.randrange(SCREENHEIGHT,SCREENHEIGHT-gap)
        self.y = random.choice([y,y2])
        
        self.y = random.randint(10,20)
        self.engaged = False
        self.speed = 2
        self.damage = 2
        self.damageDelay = random.randint(1,10)
        self.engageDelay = random.randint(10,30)
        #Loading of the image:
        self.size = 30
        self.spriteList = []
        self.attackSprites = []
        self.sCount = 0
        self.spriteSheet=pygame.image.load('sprites/wolf/wolf.png').convert_alpha()
        rect = self.spriteSheet.get_rect()
        w = rect.w/7
        h = rect.h
        self.cords = [(0,0,w,h),(w,0,w,h),(w*2,0,w,h),(w*3,0,w,h)]
        cords2 = [(w*4,0,w,h),(w*5,0,w,h),(w*6,0,w,h)]
        for i in self.cords:
            rect = pygame.Rect(i)
            s = pygame.Surface(rect.size).convert()
            s.blit(self.spriteSheet, (0, 0), rect)
            s.set_colorkey((0,0,0))
            s = pygame.transform.scale(s,(w*2,h*2))
            self.spriteList.append(s)
        for i in cords2:
            rect = pygame.Rect(i)
            s = pygame.Surface(rect.size).convert()
            s.blit(self.spriteSheet, (0, 0), rect)
            s.set_colorkey((0,0,0))
            s = pygame.transform.scale(s,(w*2,h*2))
            self.attackSprites.append(s)

        self.image = self.spriteList[0]
        self.rect = self.image.get_rect()
        self.mask=pygame.mask.from_surface(self.image)
        self.mask.scale((self.rect.w,self.rect.h))
        #These are based off the original sprite:
        self.faceLeft = True
        self.faceRight = False
    def update(self,GAMESCREEN):
        if self.engaged:
            self.sCount += 1
            if self.sCount >= len(self.spriteList):
                self.sCount = 0
            self.rect.center = (self.x,self.y)
            GAMESCREEN.blit(self.spriteList[self.sCount],self.rect)
            self.mask = pygame.mask.from_surface(self.spriteList[self.sCount])
        if self.spriteList[self.sCount] == self.attackSprites[-1]:
            self.spriteList = []
            for i in self.cords:
                rect = pygame.Rect(i)
                s = pygame.Surface(rect.size).convert()
                s.blit(self.spriteSheet, (0, 0), rect)
                s.set_colorkey((0,0,0))
                s = pygame.transform.scale(s,(w*2,h*2))
                self.spriteList.append(s)
    def moveSelf(self,pig):
        if pig.x > self.x:
            self.x += self.speed
            if not self.faceRight:
                for index,i in enumerate(self.spriteList):
                    self.spriteList[index] = pygame.transform.flip(i,True,False)
                for index,i in enumerate(self.attackSprites):
                    self.attackSprites[index] = pygame.transform.flip(i,True,False)
                self.faceRight = not self.faceRight
                self.faceLeft = not self.faceLeft
        elif pig.x < self.x:
            self.x -= self.speed
            if not self.faceLeft:
                for index,i in enumerate(self.spriteList):
                    self.spriteList[index] = pygame.transform.flip(i,True,False)
                for index,i in enumerate(self.attackSprites):
                    self.attackSprites[index] = pygame.transform.flip(i,True,False)
                self.faceRight = not self.faceRight
                self.faceLeft = not self.faceLeft
        if pig.y > self.y:
            self.y += self.speed
        elif pig.y < self.y:
            self.y -= self.speed