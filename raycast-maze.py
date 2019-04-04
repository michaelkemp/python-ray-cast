import pygame, base64, math, random, sys
pygame.init()

TURN = math.pi/64
STEP = 4
RES = 320
VANG = math.pi/6
PLAYERDISTANCE = (RES/2)/math.tan(VANG)
FOV = []
VANG = math.pi/6
i = -VANG
while (i < VANG):
    FOV.append(i)
    i+=(VANG*2)/RES

WIDE = 64
HIGH = 128

pygame.display.set_caption("Raycast Maze")
CLOCK = pygame.time.Clock()

## ############################## WALLS ##############################
SPRITEBLOCK = pygame.image.load("walls.png")
ROWWLL = [None] * 64
COLWLL = [None] * 64
ROWBGN = [None] * 64
COLBGN = [None] * 64
ROWEND = [None] * 64
COLEND = [None] * 64
for i in range(64):
    ROWWLL[i] = pygame.Surface((1,64))
    COLWLL[i] = pygame.Surface((1,64))
    ROWBGN[i] = pygame.Surface((1,64))
    COLBGN[i] = pygame.Surface((1,64))
    ROWEND[i] = pygame.Surface((1,64))
    COLEND[i] = pygame.Surface((1,64))
    ROWWLL[i].blit(SPRITEBLOCK, [0,0], ( 0+i,  0, 1, 64))
    COLWLL[i].blit(SPRITEBLOCK, [0,0], (64+i,  0, 1, 64))
    ROWBGN[i].blit(SPRITEBLOCK, [0,0], ( 0+i, 64, 1, 64))
    COLBGN[i].blit(SPRITEBLOCK, [0,0], (64+i, 64, 1, 64))
    ROWEND[i].blit(SPRITEBLOCK, [0,0], ( 0+i,128, 1, 64))
    COLEND[i].blit(SPRITEBLOCK, [0,0], (64+i,128, 1, 64))
## ############################## WALLS ##############################


## #########################################################################################
## ############################# START : PRIM'S MAZE ALGORITHM #############################
## #########################################################################################

def removeWalls(x, y, maze, frontier, rows, cols):
    N,E,S,W,IN,FRONTIER = 1,2,4,8,16,32
    ins = []

    #add to possible wall removal if IS IN MAZE and DOES HAVE WALL
    if (x > 0) and ((maze[x-1][y] & IN) == IN) and ((maze[x][y] & W) == W):
        ins.append([x-1,y,E,W])
    if (x < cols-1) and ((maze[x+1][y] & IN) == IN) and ((maze[x][y] & E) == E):
        ins.append([x+1,y,W,E])
    if (y > 0) and ((maze[x][y-1] & IN) == IN) and ((maze[x][y] & N) == N):
        ins.append([x,y-1,S,N])
    if (y < rows-1) and ((maze[x][y+1] & IN) == IN) and ((maze[x][y] & S) == S):
        ins.append([x,y+1,N,S])

    #if there is a wall to remove - Select Random Room and Remove Walls adjoining cells
    if (len(ins) > 0):
        deWall = random.choice(ins)
        thisX = x
        thisY = y
        thisW = deWall[3]
        thatX = deWall[0]
        thatY = deWall[1]
        thatW = deWall[2]
        maze[thisX][thisY] = maze[thisX][thisY] & ~thisW
        maze[thatX][thatY] = maze[thatX][thatY] & ~thatW


def addToMaze(x, y, maze, frontier, rows, cols):
    N,E,S,W,IN,FRONTIER = 1,2,4,8,16,32

    maze[x][y] = maze[x][y] & ~FRONTIER #remove from frontier
    maze[x][y] = maze[x][y] | IN #add to maze
    removeWalls(x, y, maze, frontier, rows, cols) #remove walls
    makeFrontier(x,y,maze,frontier, rows, cols) #make new frontier

def makeFrontier(x,y,maze,frontier, rows, cols):
    N,E,S,W,IN,FRONTIER = 1,2,4,8,16,32

    if (x > 0) and ((maze[x-1][y] & IN) != IN):
        if (maze[x-1][y] & FRONTIER) != FRONTIER:
            maze[x-1][y] = maze[x-1][y] | FRONTIER
            frontier.append([x-1,y])
    if (x < cols-1) and ((maze[x+1][y] & IN) != IN):
        if (maze[x+1][y] & FRONTIER) != FRONTIER:
            maze[x+1][y] = maze[x+1][y] | FRONTIER
            frontier.append([x+1,y])
    if (y > 0) and ((maze[x][y-1] & IN) != IN):
        if (maze[x][y-1] & FRONTIER) != FRONTIER:
            maze[x][y-1] = maze[x][y-1] | FRONTIER
            frontier.append([x,y-1])
    if (y < rows-1) and ((maze[x][y+1] & IN) != IN):
        if (maze[x][y+1] & FRONTIER) != FRONTIER:
            maze[x][y+1] = maze[x][y+1] | FRONTIER
            frontier.append([x,y+1])

def makeMaze(rows,cols):
    N,E,S,W,IN,FRONTIER = 1,2,4,8,16,32

    MAZEROWS = rows
    MAZECOLS = cols
    frontier = []
    maze = [[(N|E|S|W) for y in range(MAZEROWS)] for x in range(MAZECOLS)] #create maze with all walls

    addToMaze(0, 0, maze, frontier, MAZEROWS, MAZECOLS)
    while (len(frontier) > 0):
        random.shuffle(frontier)
        tmp = frontier.pop()
        addToMaze(tmp[0], tmp[1], maze, frontier, MAZEROWS, MAZECOLS)

    return maze

## #######################################################################################
## ############################# END : PRIM'S MAZE ALGORITHM #############################
## #######################################################################################



## ############################# START : TURN MAZE INTO GAMEBOARD #############################

def gameBoard(maze):
    N,E,S,W,IN,FRONTIER = 1,2,4,8,16,32

    PATHWIDTH = 2

    MCOLS = len(maze)
    MROWS = len(maze[0])

    COLP = (MCOLS*PATHWIDTH)+1
    ROWP = (MROWS*PATHWIDTH)+1
    game = [[0 for y in range(ROWP)] for x in range(COLP)] #create empty gameboard

    for y in range(MROWS):
        for x in range(MCOLS):
            if (maze[x][y] & N):
                for i in range(PATHWIDTH+1):
                    game[(x*PATHWIDTH)+i][y*PATHWIDTH] = 1
            if (maze[x][y] & W):
                for i in range(PATHWIDTH+1):
                    game[x*PATHWIDTH][(y*PATHWIDTH)+i] = 1

    for y in range(ROWP):
        game[COLP-1][y] = 1
    for x in range(COLP):
        game[x][ROWP-1] = 1

    return game

## ############################# END : TURN MAZE INTO GAMEBOARD #############################



def makeBackground(ROWS,COLS):
    BACKGROUND = pygame.Surface((COLS*WIDE,ROWS*WIDE))
    #Whole Background
    BACKGROUND.fill((128,128,128))
    #Just the Ceiling
    pygame.draw.rect(BACKGROUND, (192,192,192), [0,0, COLS*WIDE, ROWS*WIDE/2], 0)
    return BACKGROUND

def makeMap(gameboard):
    COLS = len(gameboard)
    ROWS = len(gameboard[0])
    MAP = pygame.Surface((COLS,ROWS))
    MAP.fill((192,192,192))
    for y in range(ROWS):
        for x in range(COLS):
            if(int(gameboard[y][x]) == 1):
                pygame.draw.rect(MAP, (0,0,0), [x,y, 1, 1], 0)
    return MAP


## #######################################################################################
## ################################# START : RAY-CASTING #################################
## #######################################################################################

def canGo(x,y,gameboard):
    COLS = len(gameboard)
    ROWS = len(gameboard[0])

    dx = math.floor(x/WIDE)
    dy = math.floor(y/WIDE)
    if (dx > 0) and (dx < COLS) and (dy > 0) and (dy < ROWS):
        if (int(gameboard[dy][dx]) == 0):
            return True
    return False


def castRay(raydir,posX,posY,playdir,gameboard):
    COLS = len(gameboard)
    ROWS = len(gameboard[0])

    rays = []
    rise = math.sin(raydir)
    run = math.cos(raydir)
    if (abs(run) > 0.001):
        slope = rise/run
    else:
        slope = 10000

    if (raydir > (3*math.pi/2)):
        colRange = [math.ceil(posX/WIDE),COLS, 1] #low to high
        rowRange = [math.floor(posY/WIDE),0,-1]   #high to low
        colHit = 0
        rowHit = -1
    elif (raydir > (math.pi)):
        colRange = [math.floor(posX/WIDE),0,-1]   #high to low
        rowRange = [math.floor(posY/WIDE),0,-1]   #high to low
        colHit = -1
        rowHit = -1
    elif (raydir > (math.pi/2)):
        colRange = [math.floor(posX/WIDE),0,-1]   #high to low
        rowRange = [math.ceil(posY/WIDE),ROWS, 1] #low to high
        colHit = -1
        rowHit = 0
    else:
        colRange = [math.ceil(posX/WIDE),COLS, 1] #low to high
        rowRange = [math.ceil(posY/WIDE),ROWS, 1] #low to high
        colHit = 0
        rowHit = 0

    hitR = False
    if (abs(slope) > 0.0001):    
        for y in range(rowRange[0],rowRange[1],rowRange[2]):
            if (hitR): break
            rowY = y * WIDE
            rowX = (rowY - posY + (slope * posX)) / slope
            if (rowX >= 0) and (rowX < ROWS*WIDE):
                hitY = math.floor(rowY/WIDE)+rowHit
                hitX = math.floor(rowX/WIDE)
                if (int(gameboard[hitY][hitX]) == 1):
                    distance = math.sqrt(math.pow(posX-rowX,2) + math.pow(posY-rowY,2))
                    distance = 1 + (distance * math.cos(raydir-playdir))
                    along = round(rowX)%WIDE
                    rays.append([rowX,rowY,distance,"row",along,hitX,hitY])
                    hitR = True

    hitC = False
    if (abs(slope) < 10000):
        for x in range(colRange[0],colRange[1],colRange[2]):
            if (hitC): break
            colX = (x * WIDE)
            colY = (slope * (colX - posX)) + posY
            if (colY > 0) and (colY < COLS*WIDE):
                hitY = math.floor(colY/WIDE)
                hitX = math.floor(colX/WIDE)+colHit
                if (int(gameboard[hitY][hitX]) == 1):
                    distance = math.sqrt(math.pow(posX-colX,2) + math.pow(posY-colY,2))
                    distance = 1 + (distance * math.cos(raydir-playdir))
                    along = round(colY)%WIDE
                    rays.append([colX,colY,distance,"col",along,hitX,hitY])
                    hitC = True

    if (len(rays) == 0):
        return False
    if (len(rays) == 1):
        return rays[0]
    else:
        if (rays[0][2] < rays[1][2]):
            return rays[0]
        else:
            return rays[1]

## #######################################################################################
## ################################## END : RAY-CASTING ##################################
## #######################################################################################


def main():

    MAPSIZE = 12
    maze = makeMaze(MAPSIZE,MAPSIZE)
    gameboard = gameBoard(maze)

    COLS = len(gameboard)
    ROWS = len(gameboard[0])
    SCREEN = pygame.display.set_mode((RES*2,RES*2))

    position = [round((1*WIDE)+(WIDE/2)),round((1*WIDE)+(WIDE/2))]
    direction = 3*math.pi/2

    BACKGROUND = makeBackground(ROWS,COLS)
    MAP = makeMap(gameboard)
    MAPPOS = pygame.Surface((COLS,ROWS))
    showMap = False

    while True:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
            direction -= TURN
            if (direction < 0): direction += 2*math.pi
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction += TURN
            if (direction > 2*math.pi): direction -= 2*math.pi
        if keys[pygame.K_UP]    or keys[pygame.K_w]:
            tmpX = position[0] + (STEP * math.cos(direction))
            tmpY = position[1] + (STEP * math.sin(direction))
            if (canGo(tmpX,tmpY,gameboard)):
                position[0] = tmpX
                position[1] = tmpY
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]:
            tmpX = position[0] - (STEP * math.cos(direction))
            tmpY = position[1] - (STEP * math.sin(direction))
            if (canGo(tmpX,tmpY,gameboard)):
                position[0] = tmpX
                position[1] = tmpY

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    showMap = not showMap

        SCREEN.fill((0,0,0))
        SCREEN.blit(pygame.transform.scale(BACKGROUND,(RES*2,RES*2)),(0,0))

        bar = 0
        for i in FOV:
            rayDir = direction+i
            if (rayDir < 0): rayDir += 2*math.pi
            if (rayDir > 2*math.pi): rayDir -= 2*math.pi
            myRay = castRay(rayDir,position[0],position[1],direction,gameboard)
            if (myRay != False):
                dist = myRay[2]
                height = round(PLAYERDISTANCE * HIGH/dist)
                top = round((640 - height)/2)
                if (myRay[3] == "row"):
                    if ((myRay[5] == 1) and (myRay[6] == 0)):
                        SCREEN.blit(pygame.transform.scale(ROWBGN[myRay[4]],(2,height)), [bar,top, 2, height])
                    elif ((myRay[5] == (MAPSIZE*2)-1) and (myRay[6] == (MAPSIZE*2))):
                        SCREEN.blit(pygame.transform.scale(ROWEND[myRay[4]],(2,height)), [bar,top, 2, height])
                    else:
                        SCREEN.blit(pygame.transform.scale(ROWWLL[myRay[4]],(2,height)), [bar,top, 2, height])

                else:
                    if ((myRay[5] == 0) and (myRay[6] == 1)):
                        SCREEN.blit(pygame.transform.scale(COLBGN[myRay[4]],(2,height)), [bar,top, 2, height])
                    elif ((myRay[5] == (MAPSIZE*2)) and (myRay[6] == (MAPSIZE*2)-1)):
                        SCREEN.blit(pygame.transform.scale(COLEND[myRay[4]],(2,height)), [bar,top, 2, height])
                    else:
                        SCREEN.blit(pygame.transform.scale(COLWLL[myRay[4]],(2,height)), [bar,top, 2, height])
            bar += 2

        if (showMap):
            MAPPOS.blit(MAP,(0,0))
            pygame.draw.rect(MAPPOS, (0,255,0), [math.floor(position[0]/WIDE),math.floor(position[1]/WIDE), 1, 1], 0)
            SCREEN.blit(pygame.transform.scale(MAPPOS,(COLS*4,ROWS*4)),(0,0))
            pygame.draw.circle(SCREEN, (0,0,0), [RES,20], 20, 1)
            cenX = RES
            cenY = 20
            edgX = cenX + (18 * math.cos(direction))
            edgY = cenY + (18 * math.sin(direction))
            pygame.draw.line(SCREEN, (0,255,0), [cenX,cenY], [edgX,edgY], 1)

        pygame.display.update()

        CLOCK.tick(30)

def terminate():
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
