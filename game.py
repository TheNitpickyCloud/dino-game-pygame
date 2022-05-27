import pygame
import pygame_textinput
import random
import win32api
import sys
import csv

def getInfo(device):
    settings = win32api.EnumDisplaySettings(device.DeviceName, -1)
    l = []
    for varName in ['Color', 'BitsPerPel', 'DisplayFrequency']:
        l.append(getattr(settings, varName))

    return l[-1]

device = win32api.EnumDisplayDevices()
FPS = getInfo(device)

stage = 2
score = 0

pygame.init()
pygame.font.init()

clock = pygame.time.Clock()

# create the screen
screen = pygame.display.set_mode((1280, 720))

# title and icon
pygame.display.set_caption("dino game")
icon = pygame.image.load("assets/dino_logo.png")
pygame.display.set_icon(icon)

# score text
font = pygame.font.SysFont('Comic Sans MS', 32)
def displayScore(text):
    screen.blit(text, (1150, 30))

# Create TextInput-object
manager = pygame_textinput.TextInputManager(validator=lambda input: len(input) <= 10)
textinput = pygame_textinput.TextInputVisualizer(manager=manager, font_object=font)

# get initial score data
filename = "scores.csv"
scores = {}
header = ["name", "score"]

try:
    with open(filename, "r", encoding="utf8") as file:
        csvreader = csv.reader(file)
        _ = next(csvreader)
        for row in csvreader:
            if row != []:
                scores[row[0]] = row[1]
except:
    pass

def saveScore():
    prev = 0
    if str(manager.value) in scores:
        prev = int(scores[str(manager.value)])
    scores[str(manager.value)] = str(max(int(score), prev))
    scoreList = []

    for name_key in scores.keys():
        scoreList.append([name_key, scores[name_key]])

    with open(filename, "w", encoding="utf8") as file:
        csvwriter = csv.writer(file)
        csvwriter.writerow(header)
        csvwriter.writerows(scoreList)

def main():
    # player
    playerImg = [pygame.image.load("assets/dino-1.png").convert_alpha(), pygame.image.load("assets/dino-2.png").convert_alpha(), pygame.image.load("assets/dino-ducking-1.png").convert_alpha(), pygame.image.load("assets/dino-ducking-2.png").convert_alpha()]
    playerRect = playerImg[0].get_rect()
    playerMask = pygame.mask.from_surface(playerImg[0])
    playerX = 200
    playerY = 500
    jumpcount = 2
    jumping = False
    down = False
    playerRect.center = playerX+64, playerY+64
    curr = 0

    def player(x, y):
        nonlocal curr
        nonlocal playerMask
        nonlocal down
        nonlocal playerRect
        if down == False:
            if curr <= 15:
                screen.blit(playerImg[0], (x, y))
                playerMask = pygame.mask.from_surface(playerImg[0])
                curr += 1
            else:
                screen.blit(playerImg[1], (x, y))
                playerMask = pygame.mask.from_surface(playerImg[1])
                curr += 1
                if curr >= 30:
                    curr = 0
        else:
            if curr <= 15:
                screen.blit(playerImg[2], (x, y))
                playerMask = pygame.mask.from_surface(playerImg[2])
                curr += 1
            else:
                screen.blit(playerImg[3], (x, y))
                playerMask = pygame.mask.from_surface(playerImg[3])
                curr += 1
                if curr >= 30:
                    curr = 0

    # cactus
    cactusImg = [pygame.image.load("assets/cactus-1.png").convert_alpha(), pygame.image.load("assets/cactus-2.png").convert_alpha(), pygame.image.load("assets/cactus-3.png").convert_alpha()]
    cactusY = 500

    # bird
    birdImg = [pygame.image.load("assets/bird-1.png").convert_alpha(), pygame.image.load("assets/bird-2.png").convert_alpha()]
    birdY = [425, 360]

    # data common to obstacles
    obsMove = 0.5
    obsX = 1280
    obsY = cactusY
    currImg = cactusImg[0]
    currMask = pygame.mask.from_surface(currImg)
    currRect = currImg.get_rect()
    obsCurr = 0

    def obstacle(x, y):
        nonlocal cactusY
        nonlocal birdY
        nonlocal obsY
        nonlocal currImg
        nonlocal obsX
        nonlocal obsMove
        nonlocal currMask
        nonlocal obsCurr
        global score

        if x <= -64:
            if score >= 500:
                num = random.randint(0, 1)
                if num == 0:
                    obsX = 1280
                    currImg = cactusImg[random.randint(0, 2)]
                    obsY = cactusY
                    currMask = pygame.mask.from_surface(currImg)
                    obsMove += 0.05
                else:
                    obsX = 1280
                    currImg = birdImg[0]
                    obsY = birdY[random.randint(0, 1)]
                    currMask = pygame.mask.from_surface(currImg)
                    obsMove += 0.05
            else:
                obsX = 1280
                currImg = cactusImg[random.randint(0, 2)]
                obsY = cactusY
                currMask = pygame.mask.from_surface(currImg)
                obsMove += 0.05

        if obsY == birdY[0] or obsY == birdY[1]: # animate bird
            if obsCurr <= 15:
                screen.blit(currImg, (obsX, obsY))
                currMask = pygame.mask.from_surface(birdImg[0])
                currImg = birdImg[0]
                obsCurr += 1
            else:
                screen.blit(currImg, (obsX, obsY))
                currMask = pygame.mask.from_surface(birdImg[1])
                currImg = birdImg[1]
                obsCurr += 1
                if obsCurr >= 30:
                    obsCurr = 0
        else:
            screen.blit(currImg, (obsX, obsY))

    # cloud
    cloudImgs = [pygame.image.load("assets/cloud.png").convert_alpha(), pygame.image.load("assets/cloud.png").convert_alpha(), pygame.image.load("assets/cloud.png").convert_alpha(),
                pygame.image.load("assets/cloud.png").convert_alpha(), pygame.image.load("assets/cloud.png").convert_alpha(), pygame.image.load("assets/cloud.png").convert_alpha()]
    cloudXs = [random.randint(0, 1280), random.randint(0, 1280), random.randint(0, 1280), random.randint(0, 1280), random.randint(0, 1280), random.randint(0, 1280)]
    cloudYs = [random.randint(0, 320), random.randint(0, 320), random.randint(0, 320), random.randint(0, 320), random.randint(0, 320), random.randint(0, 320)]
    cloudMove = 0.1
    def cloud():
        for i in range(6):
            if cloudXs[i] <= -64:
                cloudXs[i] = 1280
            screen.blit(cloudImgs[i], (cloudXs[i], cloudYs[i]))

    # reset score
    global score
    score = 0

    # collision check
    def collide():
        xoffset = playerRect[0] - currRect[0]
        yoffset = playerRect[1] - currRect[1]

        leftmask = playerMask
        rightmask = currMask

        return leftmask.overlap(rightmask, (xoffset*1.2, yoffset*1.2))

    run = True
    while run:
        dt = clock.tick(FPS)

        # background and ground
        screen.fill((255, 255, 255))
        pygame.draw.line(screen, '#000000', (0, 628), (1280, 628), 1)

        # score display
        text = font.render(str(int(score)), True, '#000000', '#FFFFFF')
        displayScore(text)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                saveScore()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # jump
                    if not jumping:
                        pygame.mixer.music.load('assets/jump-sound.mp3')
                        pygame.mixer.music.play(0)
                        jumping = True
                if event.key == pygame.K_DOWN:
                    down = True
                    playerRect = playerRect.inflate(0, -20)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    down = False
                    playerY = cactusY
                    jumpcount = 2
                    playerRect = playerRect.inflate(0, 20)
        
        if jumping and not down:
            if jumpcount >= -2:
                playerY -= 0.5 * (jumpcount * abs(jumpcount)) * dt
                jumpcount -= 0.075
            else:
                playerY = cactusY
                jumpcount = 2
                jumping = False

        if down:
            jumping = False
            if playerY < cactusY:
                playerY = min(playerY+(2.5*dt), cactusY)
            else:
                playerY = cactusY
                jumpcount = 2
                #down = False

        obsX -= obsMove * dt
        obsMove = min(obsMove, 4)

        for i in range(6):
            cloudXs[i] -= cloudMove * dt

        cloud()
        player(playerX, playerY)
        obstacle(obsX, obsY)

        playerRect.center = playerX+64, playerY+64
        currRect.center = obsX+64, obsY+64

        if collide():
            pygame.mixer.music.load('assets/death-sound.mp3')
            pygame.mixer.music.play(0)
            global stage
            stage = 1
            break
            
        score += obsMove

        # pygame.draw.rect(screen, '#ff0000', playerRect, 1)
        # pygame.draw.rect(screen, '#ff0000', currRect, 1)

        pygame.display.update()

# gameloop
running = True
while running:
    dt = clock.tick(FPS)

    if stage == 0:
        main()

    elif stage == 1:
        # game over
        restartbuttonImg = pygame.image.load("assets/restart_button.png").convert_alpha()
        restartbuttonrect = restartbuttonImg.get_rect()
        restartbuttonrect.center = (540, 360)
        
        def restart_button():
            screen.blit(restartbuttonImg, (550-64, 360-64))

        restart_button()

        homebuttonImg = pygame.image.load("assets/home_button.png").convert_alpha()
        homebuttonrect = homebuttonImg.get_rect()
        homebuttonrect.center = (740, 360)
        
        def home_button():
            screen.blit(homebuttonImg, (730-64, 360-64))

        home_button()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                saveScore()
                sys.exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos  # gets mouse position

                # checks if mouse position is over the button

                if restartbuttonrect.collidepoint(mouse_pos):
                    saveScore()
                    stage = 0
                if homebuttonrect.collidepoint(mouse_pos):
                    saveScore()
                    stage = 2
    
    else:
        # login with id
        screen.fill((255, 255, 255))
        events = pygame.event.get()

        # name text display
        text = font.render("Name: ", True, '#000000', '#FFFFFF')
        screen.blit(text, (470, 280))

        # name input
        screen.blit(textinput.surface, (575, 280))
        textinput.update(events)
        
        # play button
        buttonImg = pygame.image.load("assets/play_button.png").convert_alpha()
        buttonrect = buttonImg.get_rect()
        buttonrect.center = (640, 400)
        
        def button():
            screen.blit(buttonImg, (640-64, 400-64))

        button()
        
        # Blit its surface onto the screen

        for event in events:
            if event.type == pygame.QUIT:
                running = False
                sys.exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos  # gets mouse position

                # checks if mouse position is over the button

                if buttonrect.collidepoint(mouse_pos) and manager.value != '':
                    stage = 0

        #pygame.draw.rect(screen, '#ff0000', buttonrect, 1)
        
    pygame.display.update()