import pygame, sys
import numpy as np
import os
import random
from os import path
import copy

#Constants
WIDTH=800
HEIGHT=WIDTH
LINE_WIDTH=15
BOARDS_ROWS=3
BOARDS_COLS=3
SQUARE_SIZE=WIDTH//BOARDS_COLS
SPACE=55
CROSS_WIDTH=25
c_radius=60
c_width=15
RADIUS = SQUARE_SIZE // 4
OFFSET = 50

#RGB
RED=(255,0,0)
GREEN=(0,255,0)
BLUE=(0,0,255)
BG_COLOR=(28,170,156)
LINE_COLOR=(23,145,135)
CIRCLE_COLOR=(239,231,200)
CROSS_COLOR=(66,66,66)

#initialize
pygame.init()
pygame.mixer.init()
screen=pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('TIC TAC TOE')
screen.fill(BG_COLOR)

font_name = pygame.font.match_font('arial')

def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, BLUE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def show_go_screen():
    screen.fill(BG_COLOR)
    draw_text(screen, "END!", 64, WIDTH / 2, HEIGHT / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False

#classes
class Board:

    def __init__(self):
        self.squares = np.zeros( (BOARDS_ROWS, BOARDS_COLS) )
        self.empty_sqrs = self.squares # [squares]
        self.marked_sqrs = 0

    def final_state(self, show=False):
        #승부 미정 0, P1 승 1, P2 승 2

        # 수직 승
        for col in range(BOARDS_COLS):
            if self.squares[0][col] == self.squares[1][col] == self.squares[2][col] != 0:
                if show:
                    color = CIRCLE_COLOR if self.squares[0][col] == 2 else CROSS_COLOR
                    iPos = (col * SQUARE_SIZE + SQUARE_SIZE // 2, 20)
                    fPos = (col * SQUARE_SIZE + SQUARE_SIZE // 2, HEIGHT - 20)
                    pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
                return self.squares[0][col]
            
        # 수평 승
        for row in range(BOARDS_ROWS):
            if self.squares[row][0] == self.squares[row][1] == self.squares[row][2] != 0:
                if show:
                    color = CIRCLE_COLOR if self.squares[row][0] == 2 else CROSS_COLOR
                    iPos = (20, row * SQUARE_SIZE + SQUARE_SIZE // 2)
                    fPos = (WIDTH - 20, row * SQUARE_SIZE + SQUARE_SIZE // 2)
                    pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
                return self.squares[row][0]

        # 대각선
        if self.squares[0][0] == self.squares[1][1] == self.squares[2][2] != 0:
            if show:
                color = CIRCLE_COLOR if self.squares[1][1] == 2 else CROSS_COLOR
                iPos = (20, 20)
                fPos = (WIDTH - 20, HEIGHT - 20)
                pygame.draw.line(screen, color, iPos, fPos, CROSS_WIDTH)
            return self.squares[1][1]
        
            # 대각선
        if self.squares[2][0] == self.squares[1][1] == self.squares[0][2] != 0:
            if show:
                color = CIRCLE_COLOR if self.squares[1][1] == 2 else CROSS_COLOR
                iPos = (20, HEIGHT - 20)
                fPos = (WIDTH - 20, 20)
                pygame.draw.line(screen, color, iPos, fPos, CROSS_WIDTH)
            return self.squares[1][1]
        
            # no win yet
        return 0

    def mark_sqr(self, row, col, player):
        self.squares[row][col] = player
        self.marked_sqrs += 1

    def empty_sqr(self, row, col):
        return self.squares[row][col] == 0

    def get_empty_sqrs(self):
        empty_sqrs = []
        for row in range(BOARDS_ROWS):
            for col in range(BOARDS_COLS):
                if self.empty_sqr(row, col):
                    empty_sqrs.append( (row, col) )
        
        return empty_sqrs
    
    def isfull(self):
        return self.marked_sqrs == 9

    def isempty(self):
        return self.marked_sqrs == 0

class AI:

    def __init__(self, level=1, player=2):
        self.level = level
        self.player = player

    # 랜덤 입력

    def rnd(self, board):
        empty_sqrs = board.get_empty_sqrs()
        idx = random.randrange(0, len(empty_sqrs))

        return empty_sqrs[idx] # (row, col)

    # 미니맥스

    def minimax(self, board, maximizing):
        
        # terminal case, 최종결과
        case = board.final_state()

        # player 1 wins +1
        if case == 1:
            return 1, None # eval, move

        # player 2 wins -1 
        if case == 2:
            return -1, None

        # draw 0
        elif board.isfull():
            return 0, None

        if maximizing:
            max_eval = -100
            best_move = None
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, 1)
                eval = self.minimax(temp_board, False)[0]
                if eval > max_eval:
                    max_eval = eval
                    best_move = (row, col)

            return max_eval, best_move

        elif not maximizing:
            min_eval = 100
            best_move = None
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, self.player)
                eval = self.minimax(temp_board, True)[0]
                if eval < min_eval:
                    min_eval = eval
                    best_move = (row, col)

            return min_eval, best_move

    # 메인

    def eval(self, main_board):
        if self.level == 0:
            # 무작위 선택
            eval = 'random'
            move = self.rnd(main_board)
        else:
            # 미니맥스 결정
            eval, move = self.minimax(main_board, False)

        print(f'AI has chosen to mark the square in pos {move} with an eval of: {eval}')

        return move # row, col

class Game:

    def __init__(self):
        self.board = Board()
        self.ai = AI()
        self.player = 1   #1-cross  #2-circles
        self.gamemode = 'ai' # pvp or ai
        self.running = True
        self.show_lines()

    # 그리기

    def show_lines(self):
        # bg
        screen.fill( BG_COLOR )

        # vertical
        pygame.draw.line(screen, LINE_COLOR, (SQUARE_SIZE, 0), (SQUARE_SIZE, HEIGHT), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (WIDTH - SQUARE_SIZE, 0), (WIDTH - SQUARE_SIZE, HEIGHT), LINE_WIDTH)

        # horizontal
        pygame.draw.line(screen, LINE_COLOR, (0, SQUARE_SIZE), (WIDTH, SQUARE_SIZE), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (0, HEIGHT - SQUARE_SIZE), (WIDTH, HEIGHT - SQUARE_SIZE), LINE_WIDTH)

    def draw_fig(self, row, col):
        if self.player == 1:
            # draw cross
            # desc line
            start_desc = (col * SQUARE_SIZE + OFFSET, row * SQUARE_SIZE + OFFSET)
            end_desc = (col * SQUARE_SIZE + SQUARE_SIZE - OFFSET, row * SQUARE_SIZE + SQUARE_SIZE - OFFSET)
            pygame.draw.line(screen, CROSS_COLOR, start_desc, end_desc, CROSS_WIDTH)
            # asc line
            start_asc = (col * SQUARE_SIZE + OFFSET, row * SQUARE_SIZE + SQUARE_SIZE - OFFSET)
            end_asc = (col * SQUARE_SIZE + SQUARE_SIZE - OFFSET, row * SQUARE_SIZE + OFFSET)
            pygame.draw.line(screen, CROSS_COLOR, start_asc, end_asc, CROSS_WIDTH)
        
        elif self.player == 2:
            # draw circle
            center = (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2)
            pygame.draw.circle(screen, CIRCLE_COLOR, center, RADIUS, c_width)

    # --- OTHER METHODS ---

    def make_move(self, row, col):
        self.board.mark_sqr(row, col, self.player)
        self.draw_fig(row, col)
        self.next_turn()

    def next_turn(self):
        self.player = self.player % 2 + 1

    def change_gamemode(self):
        self.gamemode = 'ai' #if self.gamemode == 'pvp' else 'pvp'

    def isover(self):
        return self.board.final_state(show=True) != 0 or self.board.isfull()

    def reset(self):
        self.__init__()

def main():

    # 오브젝트

    game = Game()
    board = game.board
    ai = game.ai

    # 메인루프

    while True:
        
        # pygame events
        for event in pygame.event.get():

            # quit event
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # keydown event
            if event.type == pygame.KEYDOWN:

                # 다시 시작, R이나 스페이스 버튼 누르면
                if event.key == pygame.K_r or pygame.K_SPACE:
                    game.reset()
                    board = game.board
                    ai = game.ai


            # click event
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                row = pos[1] // SQUARE_SIZE
                col = pos[0] // SQUARE_SIZE
                
                # human mark sqr
                if board.empty_sqr(row, col) and game.running:
                    game.make_move(row, col)

                    if game.isover():
                        game.running = False


        # AI initial call
        if game.gamemode == 'ai' and game.player == ai.player and game.running:

            # update the screen
            pygame.display.update()

            # eval
            row, col = ai.eval(board)
            game.make_move(row, col)

            if game.isover():
                game.running = False
            
        pygame.display.update()

main()


board=np.zeros((BOARDS_ROWS,BOARDS_COLS))

def draw_lines():
    # 1 horizontal
    pygame.draw.line(screen,LINE_COLOR,(0,SQUARE_SIZE),(WIDTH,SQUARE_SIZE),LINE_WIDTH)
    # 2 horizontal
    pygame.draw.line(screen,LINE_COLOR,(0,2*SQUARE_SIZE),(WIDTH,2*SQUARE_SIZE),LINE_WIDTH)

    # 1 vertical
    pygame.draw.line(screen,LINE_COLOR,(SQUARE_SIZE,0),((WIDTH)/3,HEIGHT),LINE_WIDTH)
    # 2 vertical
    pygame.draw.line(screen,LINE_COLOR,(2*SQUARE_SIZE,0),(2*SQUARE_SIZE,HEIGHT),LINE_WIDTH)
    
    #outline
    pygame.draw.line(screen,LINE_COLOR,(0,0),(WIDTH,0),LINE_WIDTH)
    pygame.draw.line(screen,LINE_COLOR,(0,0),(0,HEIGHT),LINE_WIDTH)
    pygame.draw.line(screen,LINE_COLOR,(0,HEIGHT),(WIDTH,HEIGHT),LINE_WIDTH)
    pygame.draw.line(screen,LINE_COLOR,(WIDTH,HEIGHT),(WIDTH,0),LINE_WIDTH)

def draw_figures():
    for row in range(BOARDS_ROWS):
        for col in range(BOARDS_COLS):
            if board[row][col]==1:
                pygame.draw.circle(screen,CIRCLE_COLOR,(int(col*SQUARE_SIZE+SQUARE_SIZE//2),int(row*SQUARE_SIZE+SQUARE_SIZE//2)),c_radius,c_width)
            elif board[row][col]==2:
                pygame.draw.line(screen,CROSS_COLOR, (col*SQUARE_SIZE+SPACE,row*SQUARE_SIZE+SQUARE_SIZE-SPACE),(col*SQUARE_SIZE+SQUARE_SIZE-SPACE,row*SQUARE_SIZE+SPACE),CROSS_WIDTH)
                pygame.draw.line(screen,CROSS_COLOR, (col*SQUARE_SIZE+SPACE,row*SQUARE_SIZE+SPACE),(col*SQUARE_SIZE+SQUARE_SIZE-SPACE,row*SQUARE_SIZE+SQUARE_SIZE-SPACE),CROSS_WIDTH)

def whoGoesFirst():
    if random.randint(0,1)==0:
        return 'computer'
    else:
        return 'player'

def mark_square(row,col,player):
    board[row][col]=player

def available_square(row,col):
    #return board[row][col]==0
    if board[row][col]==0:
        return True
    else:
        return False

def is_board_full():
    for row in range(BOARDS_ROWS):
        for col in range(BOARDS_COLS):
            if board[row][col]==0:
                return False
    
    return True

def check_win(player):
    #vertical win check
    for col in range(BOARDS_COLS):
        if board[0][col]==player and board[1][col]==player and board[2][col]==player:
            draw_vertical_winning_line(col,player)
            return True

    #horizontal win check
    for row in range(BOARDS_ROWS):
        if board[row][0]==player and board[row][1]==player and board[row][2]==player:
            draw_horizontal_winning_lines
            return True
    
    #asc diagonal win check
    if board[2][0]==player and board[1][1]==player and board[0][2]==player:
        draw_asc_diagonal(player)
        return True
    
    if board[0][0]==player and board[1][1]==player and board[2][2]==player:
        draw_desc_diagonal(player)
        return True
    
    return False

def draw_vertical_winning_line(col,player):
    posX=col*200+100
    if player==1:
        color=CIRCLE_COLOR
    elif player==2:
        color=CROSS_COLOR
    
    pygame.draw.line(screen,color,(posX,15),(posX,HEIGHT-15),15)

def draw_horizontal_winning_lines(row,player):
    posY=row*200+100
    if player==1:
        color=CIRCLE_COLOR
    elif player==2:
        color=CROSS_COLOR
    
    pygame.draw.line(screen,color,(15,posY),(WIDTH-15,posY),15)

def draw_asc_diagonal(player):
    if player==1:
        color=CIRCLE_COLOR
    elif player==2:
        color=CROSS_COLOR

    pygame.draw.line(screen,color,(15,HEIGHT-15),(WIDTH-15,15),15)

def draw_desc_diagonal(player):
    if player==1:
        color=CIRCLE_COLOR
    elif player==2:
        color=CROSS_COLOR

    pygame.draw.line(screen,color,(15,15),(WIDTH-15,HEIGHT-15),15)

def restart():
    screen.fill(BG_COLOR)
    draw_lines()
    player=1
    for row in range(BOARDS_ROWS):
        for col in range(BOARDS_COLS):
            board[row][col]=0

draw_lines()

player=1
game_over=False
