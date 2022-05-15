import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import gym
from time import sleep

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
            if event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_q]:
                    break
        pygame.quit()

    def draw_score(self, player1_score, player2_score):
        self.player1_score, self.player2_score = player1_score, player2_score
        # Score.
        self.text_draw("PLAYER 1", 45 * 16 + 65, self.w_h // 2 - 90,
                       (100, 100, 100), 20)
        pygame.draw.circle(self.screen, COLOR_WHITE,
                           (45 * 16 + 5, self.w_h // 2 - 90), 45 // 5)
        self.text_draw(str(self.player1_score), 45 * 16 + 65, self.w_h // 2 - 30,
                       (100, 100, 100), 45)
        self.text_draw("PLAYER 2", 45 * 16 + 65, self.w_h // 2 + 20,
                       COLOR_BLACK, 20)
        pygame.draw.circle(self.screen, COLOR_BLACK,
                           (45 * 16 + 5, self.w_h // 2 + 20), 45//5)
        self.text_draw(str(self.player2_score), 45 * 16 + 65,
                       self.w_h // 2 + 80, COLOR_BLACK, 45)

    def interactive_button(self, x=45*16, y=45, w=125, h=45,
                           button_color=COLOR_BUTTON,
                           ac_button_color=COLOR_AC_BUTTON):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.button_color = button_color
        self.ac_button_color = ac_button_color

        # Draw buttons.
        pygame.draw.rect(self.screen, self.button_color, (self.x, self.y, w, h))
        pygame.draw.rect(self.screen, self.button_color, (self.x, self.y + 70, w, h))
        pygame.draw.rect(self.screen, self.button_color, (self.x, self.w_h - 90, w, h))
        # Draw text on buttons.
        self.text_draw("NEW GAME", self.x + 59, self.y + 25, (200, 0, 0), 20)
        self.text_draw("NEXT GAME", self.x + 62, self.y + 95, (0, 0, 180), 20)
        self.text_draw("QUIT", self.x + 56, self.w_h - 65, (200, 0, 200), 20)
        # To make interactive buttons.
        mouse = pygame.mouse.get_pos()
        # New game.
        if self.w + self.x > mouse[0] > self.x and \
                self.y + self.h > mouse[1] > self.y:
            pygame.draw.rect(self.screen, self.ac_button_color,
                             (self.x, self.y, self.w, self.h))
            self.text_draw("START", self.x+59, self.y + 25, COLOR_RED, 20)

        # Next game.
        if self.w + self.x > mouse[0] > self.x and \
                self.y + 70 + self.h > mouse[1] > self.y + 70:
            pygame.draw.rect(self.screen, self.ac_button_color,
                             (self.x, self.y + 70, self.w, self.h))
            self.text_draw("Next game", self.x + 62, self.y + 95, (0, 0, 225), 20)

        # Quit.
        if self.w + self.x > mouse[0] > self.x and \
                self.w_h - 90 + self.h > mouse[1] > self.w_h - 90:
            pygame.draw.rect(self.screen, self.ac_button_color,
                             (self.x, self.w_h - 90, self.w, self.h))
            self.text_draw("Quit", self.x + 56, self.w_h-65, (225, 0, 225), 20)
            if pygame.mouse.get_pressed()[0] == 1:
                pygame.quit()
                quit()

    def text_draw(self, text, x_pos, y_pos, font_color, font_size):
        self.text = text
        self.font_size = font_size
        self.font_color = font_color
        ff = pygame.font.Font(pygame.font.get_default_font(), self.font_size)
        TextSurf, TextRect = self.text_objects(self.text, ff, self.font_color)
        TextRect.center = (x_pos, y_pos)
        self.screen.blit(TextSurf, TextRect)

    def text_objects(self, text, font, font_color):
        textSurface = font.render(text, True, font_color)
        return textSurface, textSurface.get_rect()

    def play_get_pos(self):
        self.x_stone, self.y_stone = pygame.mouse.get_pos()

        return self.x_stone, self.y_stone

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

    def score(self, stone, color_name, player_score, play_order):
        self.stone, self.color_name, self.player_score = stone, color_name, player_score
        self.play_order = play_order
        self.result = None
        if len(self.stone[self.color_name]) >= 5:

            stone_sort = sorted(self.stone[self.color_name])

            for x, y in stone_sort:
                cnt = 0
                for i in range(1, 5):
                    if (x, y + 45 * i) in stone_sort:
                        cnt += 1
                        if cnt == 4:
                            self.player_score += 1
                            self.play_order = None
                            self.result = True
                            break

                    else: break

                cnt = 0
                for i in range(1, 5):
                    if (x + 45 * i, y) in stone_sort:
                        cnt += 1
                        if cnt == 4:
                            self.player_score += 1
                            self.play_order = None
                            self.result = True
                            break
                    else: break

                cnt = 0
                for i in range(1, 5):
                    if (x + 45 * i, y+45 * i) in stone_sort:
                        cnt += 1
                        if cnt == 4:
                            self.player_score += 1
                            self.play_order = None
                            self.result = True
                            break
                cnt = 0
                for i in range(1, 5):
                    if (x + 45 * i, y - 45 * i) in stone_sort:
                        cnt += 1
                        if cnt == 4:
                            self.player_score += 1
                            self.play_order = None
                            self.result = True
                            break

        if self.result:
            if self.color_name == "white":
                self.text_draw("WIN", 45 * 16 + 65, self.w_h // 2 - 120,
                               (100, 100, 100), 45)

            elif self.color_name == "black":
                self.text_draw("WIN", 45 * 16 + 65, self.w_h//2 + 120,
                               COLOR_BLACK, 45)

        return self.player_score, self.play_order

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
