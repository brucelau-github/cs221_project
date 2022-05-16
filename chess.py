import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import gym
from time import sleep
import matplotlib.pyplot as plt
from PIL import Image

# Colors
COLOR_AC_BUTTON = (200, 200, 0)
COLOR_BLACK = (0, 0, 0)
COLOR_BOARD = (212, 87, 36)
COLOR_BUTTON = (255, 255, 0)
COLOR_GRAY = (100, 100, 100)
COLOR_GREEN = (0, 200, 0)
COLOR_RED = (255, 0, 0)
COLOR_WHITE = (255, 255, 255)

class Gomoku(gym.Env):
    def __init__(self, n=15):
        super().__init__()
        self.players = [1, -1]
        self.next_player = 1
        self.action_space = gym.spaces.Discrete(n*n)
        self.observation_space = gym.spaces.Discrete(n*n)
        self.board_size = n
        self.stone = {-1:[], 1:[]}
        self.score = {-1:0, 1:0}
        self.chess_board = [[0]*n for _ in range(n)]
        self.screen = None
        self.board_line_gap = 45

    def reset(self):
        """ reset the chess status """
        self.stone = {-1:[], 1:[]}
        self.score = {-1:0, 1:0}
        self.chess_board = [[0]*n for _ in range(n)]

    def step(self, action):
        """ place a piece on the board """
        m, n = action
        if self.chess_board[m][n] != 0:
            h_label, v_label = chr(ord('A') + m), str(n+1)
            raise ValueError(f"position {h_label}x{v_label} is occupied")
        observation, reward, done, info = self.chess_board, -1, False, {}
        player = self.next_player
        self.chess_board[m][n] = player
        self.stone[player].append(action)
        won = self.is_win(self.stone[player])
        if won: 
            reward = 5000
            done = True
        self.next_player *= -1
        self.score[player] += reward
        return (observation, reward, done, info)

    def is_win(self, stone):
        if len(stone) < 5:
            return False

        stone_sort = sorted(stone)
        for x, y in stone_sort:
            row, col, diag, adiag = [], [], [], []
            for i in range(1, 5):
                row.append((x, y+i))
                col.append((x+i, y))
                diag.append((x+i, y+i))
                adiag.append((x+i, y-i))
            stone_set = set(stone_sort)
            win = (stone_set.issuperset(set(row))
                   or stone_set.issuperset(set(col))
                   or stone_set.issuperset(set(diag))
                   or stone_set.issuperset(set(adiag)))
            if win: return True
        return False

    def print_info(self):
        print(self.stone)
        print(self.next_player)
        print(self.chess_board)

    def render(self):
        """ render a chess board """
        plt.figure()
        plt.imshow(pygame.surfarray.array3d(self.screen))
        plt.show()
        return None

    def draw_board(self):
        pygame.init()
        n, gap = self.board_size, self.board_line_gap
        self.screen = pygame.display.set_mode(((n+1)*gap, (n+1)*gap))
        self.screen.fill(COLOR_BOARD)
        h_label, v_label = ord('A'), 1
        h_line = pygame.Rect((gap, gap), ((n-1)*gap, 2)).move(0, -1)
        v_line = pygame.Rect((gap, gap), (2, (n-1)*gap)).move(-1, 0)
        for i in range(self.board_size):
            self.text_draw(chr(h_label+i), gap*(1 + i), gap-10, COLOR_BLACK, 10)
            self.text_draw(str(v_label+i), gap-10, gap*(1 + i), COLOR_BLACK, 10)
            pygame.draw.rect(self.screen, COLOR_BLACK, v_line.move(gap*i, 0))
            pygame.draw.rect(self.screen, COLOR_BLACK, h_line.move(0, gap*i))
        circle = pygame.draw.circle(self.screen, COLOR_BLACK, [gap * 8, gap * 8], 8)
        pygame.display.update()

    def draw_stone(self, m, n, player):
        if m == -1:
            return
        color = {-1: COLOR_BLACK, 1:COLOR_WHITE}
        gap = self.board_line_gap
        dirty = pygame.draw.circle(self.screen, color[player], [(m+1)*gap, (n+1)*gap], gap//2)
        pygame.display.update(dirty)

    def conv_mouse_pos(self, x, y):
        """ return a row, colum postion tuple """
        gap, N = self.board_line_gap, self.board_size
        m, n = x // gap - 1, y // gap - 1
        if x % gap > gap // 2:
            m += 1
        if y % gap > gap // 2:
            n += 1
        if 23 < x < N*gap and 23 < y < N*gap:
            return (m, n)
        return (-1, -1)

    def interactive_run(self):
        self.draw_board()
        while True:
            event = pygame.event.wait()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                m, n = self.conv_mouse_pos(x, y)
                if self.chess_board[m][n] == 0:
                    self.draw_stone(m, n, self.next_player)
                    s = self.step((m,n))
                    if s[2]: break
                self.render()
            if event.type == pygame.KEYDOWN and pygame.key.get_pressed()[pygame.K_q]:
                break
        msg = f"score: white {self.score[1]}, black {self.score[-1]}"
        text = self.text_draw(msg, 8*45, 8*45, COLOR_GREEN, 18)
        pygame.display.update(text)
        sleep(3)
        pygame.quit()

    def text_draw(self, text, x_pos, y_pos, font_color, font_size):
        font = pygame.font.Font(pygame.font.get_default_font(), font_size)
        text_img = font.render(text, True, font_color)
        text_rect = text_img.get_rect()
        text_rect.center = (x_pos, y_pos)
        self.screen.blit(text_img, text_rect)
        return text_rect

    def play_draw_stone(self, stone, play_order, color_name, stone_color, x_stone, y_stone):
        self.stone, self.play_order, self.color_name = stone, play_order, color_name
        self.stone_color, self.x_stone, self.y_stone = stone_color, x_stone, y_stone

        if (self.x_stone, self.y_stone) in self.stone["white"]:
            pass
        elif (self.x_stone, self.y_stone) in self.stone["black"]:
            pass
        else:
            pygame.draw.circle(self.screen, self.stone_color,
                               (self.x_stone, self.y_stone), 45//2)
            self.stone[self.color_name].append((self.x_stone, self.y_stone))
            if self.play_order: self.play_order = False
            else: self.play_order = True
        return self.stone, self.play_order

def test_is_win(game):
    tests = [
        [(0, 0)],
        [(0, 0),(1, 1),(2, 2),(3, 3),(4, 4),(5, 5)],
        [(0, 0),(1, 0),(2, 0),(3, 0),(4, 0),(5, 0)],
        [(0, 0),(0, 1),(0, 2),(0, 3),(0, 4),(0, 5)],
        [(5, 5),(6, 4),(7, 3),(8, 2),(9, 1),(10, 0)],
        [(11, 7), (11, 6), (11, 5), (11, 4), (11, 3), (0, 0)]
    ]
    for i in tests:
        print(game.is_win(i))
    memory1 = [(5, 5),(6, 4),(7, 3),(8, 2),(9, 1),(10, 0)]
    memory2 = [(0, 0),(1, 0),(2, 0),(3, 0),(4, 0),(5, 0)]
    for p1, p2 in zip(memory1, memory2):
        s = game.step(p1)
        print(f"reward:{s[1]}, done:{s[2]}")
        game.print_info()
        s = game.step(p2)
        # game.print_info()

def test_render_board(game):
    game.draw_board()
    game.draw_stone(10, 10, 1)
    sleep(20)
    pygame.event.set_allowed(pygame.MOUSEBUTTONDOWN)
    event = pygame.event.wait()

def test_conv_pos(game):
    tests = {
        (0, 0) : [(45, 45), (46, 46), (67, 67)],
        (-1, -1) : [(1, 1),(16*45, 16*45)],
        (1, 1) : [(80, 80),(90, 90), (90+22, 90+22)]
    }
    for k, v in tests.items():
        for t in v:
            got = game.conv_mouse_pos(t[0], t[1])
            assert got == k, f"convert {t} expect {k}, got {got}"
def test_run(game):
    game.interactive_run()

if __name__ == "__main__":
    game = Gomoku()
    test_run(game)
