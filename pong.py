from machine import Pin, I2C
import ssd1306
from time import sleep_ms
from random import randint


CLOCK = 10

SCREENW = 128
SCREENH = 64

PADDLEW = 4
PADDLEH = 16

# Movement speed multipliers
MOVESPEEDX = 1
MOVESPEEDY = 1

# Initial positions
PADDLELX = 5
PADDLELY = 25
PADDLERX = SCREENW - PADDLEW - 5
PADDLERY = 25
BALLX = int(SCREENW / 2)
BALLY = int(SCREENH / 2)

RANDOM = (-1, 1)


class drawnObject:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.ulCorner = (self.x, self.y)
        self.urCorner = (self.x + self.w, self.y)
        self.blCorner = (self.x, self.y + self.h)
        self.brCorner = (self.x + self.w, self.y + self.h)
    
    def update(self):
        self.ulCorner = (self.x, self.y)
        self.urCorner = (self.x + self.w, self.y)
        self.blCorner = (self.x, self.y + self.h)
        self.brCorner = (self.x + self.w, self.y + self.h)
        
    def moveToPos(self, x, y):
        self.x = x
        self.y = y
        self.update()
        oled.rect(self.x, self.y, self.w, self.h, 1, True)


class Paddle(drawnObject):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
    
    def spawn(self):
        oled.rect(self.x, self.y, self.w, self.h, 1, True)
    
    def move(self, moveY):
        self.y += moveY * MOVESPEEDY
        if self.y <= 0:
            self.y = 0
        if self.y >= SCREENH - self.h:
            self.y = SCREENH - self.h
        self.update()
        oled.rect(self.x, self.y, self.w, self.h, 1, True)


class Ball(drawnObject):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.noHit = True
        self.moveX = -1
        self.moveY = 0
    
    def move(self):
        self.x += self.moveX * MOVESPEEDX
        self.y += self.moveY * MOVESPEEDY
        self.update()
        oled.rect(self.x, self.y, self.w, self.h, 1, True)

    def collision(self):
        if (0 <= self.ulCorner[0] <= paddleL.urCorner[0]
            and self.ulCorner[1] in range(paddleL.urCorner[1], paddleL.brCorner[1] + 1)):
            return "L"
        elif (SCREENW >= self.urCorner[0] >= paddleR.ulCorner[0]
              and self.urCorner[1] in range(paddleR.ulCorner[1], paddleR.blCorner[1] + 1)):
            return "R"
        elif self.urCorner[1] == 0:
            return "C"
        elif self.brCorner[1] == SCREENH:
            return "F"
        elif self.ulCorner[0] == 0:
            return "LW"
        elif self.urCorner[0] == SCREENW:
            return "RW"
        else:
            return False
        
    def check(self):
        if self.collision() == "L":
            self.moveX = 1
            self.moveY = RANDOM[randint(0, 1)]
        elif self.collision() == "R":
            self.moveX = -1
            self.moveY = RANDOM[randint(0, 1)]
        elif self.collision() == "C":
            self.moveY = 1
        elif self.collision() == "F":
            self.moveY = -1
        elif self.collision() == "LW":
            self.moveToPos(BALLX, BALLY)
            paddleL.moveToPos(PADDLELX, PADDLELY)
            paddleR.moveToPos(PADDLERX, PADDLERY)
        elif self.collision() == "RW":
            self.moveToPos(BALLX, BALLY)
            paddleL.moveToPos(PADDLELX, PADDLELY)
            paddleR.moveToPos(PADDLERX, PADDLERY)
        self.move()


def userInput(paddle, btn, moveY):
    if btn.value() == 0:
        paddle.move(moveY)
    else:
        paddle.move(0)
        

def cpuInput(paddle, ball):
    if paddle.ulCorner[1] > ball.brCorner[1]:
        paddle.move(-1)
    elif paddle.blCorner[1] < ball.urCorner[1]:
        paddle.move(1)


btnU = Pin(7, Pin.IN, Pin.PULL_UP)
btnD = Pin(9, Pin.IN, Pin.PULL_UP)

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

oled.fill(0)
paddleL = Paddle(PADDLELX, PADDLELY, PADDLEW, PADDLEH)
paddleR = Paddle(PADDLERX, PADDLELY, PADDLEW, PADDLEH)
ball = Ball(BALLX, BALLY, 2, 2)


while True:
    oled.fill(0)
    paddleR.move(0) # Spawns right paddle
    userInput(paddleL, btnU, -1)
    userInput(paddleL, btnD, 1)
    cpuInput(paddleR, ball)
    ball.check()
    oled.show()
    sleep_ms(CLOCK)