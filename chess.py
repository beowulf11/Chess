from figure import Queen, Rook, Bishop, Knight, Pawn, King
from random import choice
import time
import threading
'''
TODO:
 - Zmenit system ako sa figurky volaju a ako sa naraba z ich poziciami
 - End Game Checking e.i. Sachmat, Remiza, a mozno aj Sach nvm ?
 - Preusporiadaj metody v Chess
 - Treba prepisat vo figurkach check_king a king_checking_path aby vracali tuple int (self.y, self.x) !!!

 - Pawn raz skocil mimo pola pre AI ale v strede boardu

 - Implement BitBoard ?

REMAINDERS:
 - Nezabudni Pawn promotion riesit v tejto classe lebo ak sa AI dostane
   do take pozicie tak tam zostane len Pawn stat navzdy
 - Plus v board.py treba priradit este obrazok novej figurky po Pawn promotion

SPEED IMPROVEMENT:
 - Kebyze je AI moc pomale tak sus kazde kolo kazdej figurke vygenerovat allowed_moves a possible_moves
   pretoze tieto atributy sa vyuzivaju casto a nech ich netreba pre kazdy pohyb samostatne generovat.
   Zamyslies sa treba este raz pretoze to neni az take lahke. By trebalo pre kazdy pohyb pozries lebo niektore
   figurky si musia updatnut allowed_moves pretoze sa im bud objavia nove alebo niektore sa zablokuju

'''


class Chess:
    def __init__(self, ai, canvas, mode):
        self.player_map = [[0 for _ in range(8)] for _ in range(8)]

        self.canvas = canvas

        self.saving_pos_w_king = []
        self.saving_pos_b_king = []

        self.pawn_table = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                           5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0,
                           1.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 1.0,
                           0.5, 0.5, 1.0, 2.5, 2.5, 1.0, 0.5, 0.5,
                           0.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0, 0.0,
                           0.5, -0.5, -1.0, 0.0, 0.0, -1.0, -0.5, 0.5,
                           0.5, 1.0, 1.0, -2.0, -2.0, 1.0, 1.0, 0.5,
                           0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.knight_table = [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0,
                             -4.0, -2.0, 0.0, 0.0, 0.0, 0.0, -2.0, -4.0,
                             -3.0, 0.0, 1.0, 1.5, 1.5, 1.0, 0.0, -3.0,
                             -3.0, 0.5, 1.5, 2.0, 2.0, 1.5, 0.5, -3.0,
                             -3.0, 0.0, 1.5, 2.0, 2.0, 1.5, 0.0, -3.0,
                             -3.0, 0.5, 1.0, 1.5, 1.5, 1.0, 0.5, -3.0,
                             -4.0, -2.0, 0.0, 0.5, 0.5, 0.0, -2.0, -4.0,
                             -5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]
        self.bishop_table = [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0,
                             -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0,
                             -1.0, 0.0, 0.5, 1.0, 1.0, 0.5, 0.0, -1.0,
                             -1.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, -1.0,
                             -1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, -1.0,
                             -1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0,
                             -1.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, -1.0,
                             -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]
        self.rook_table = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                           0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5,
                           -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5,
                           -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5,
                           -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5,
                           -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5,
                           -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5,
                           0.0, 0.0, 0.0, 0.5, 0.5, 0.0, 0.0, 0.0]
        self.queen_table = [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0,
                            -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0,
                            -1.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0,
                            -0.5, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5,
                            0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5,
                            -1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0,
                            -1.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, -1.0,
                            -2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0]
        self.king_table = [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
                           -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
                           -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
                           -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
                           -2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0,
                           -1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0,
                           2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0,
                           2.0, 3.0, 1.0, 0.0, 0.0, 1.0, 3.0, 2.0]

        self.old = []

        self.king_w_elimation_positions = []
        self.king_b_elimation_positions = []

        self.pawn_en_pasant = 0

        self.ai = ai

        self.mode = mode

        self.pawn_promotion_move = 0
        self.pawn_to_promote = 0

        self.moved_byt_two_figure = 0

        self.end_game_message = 0

        self.selected_figure = 0
        self.selected_figure_moves = []

    def reset(self):
        self.saving_pos_w_king = []
        self.saving_pos_b_king = []
        self.old = []

        self.king_w_elimation_positions = []
        self.king_b_elimation_positions = []

        self.pawn_en_pasant = 0

        self.pawn_promotion_move = 0
        self.pawn_to_promote = 0

        self.moved_byt_two_figure = 0

        self.end_game_message = 0

        self.selected_figure = 0
        self.selected_figure_moves = []

    def generate_moves_for_human(self, pos):
        self.selected_figure = self.player_map[pos[0]][pos[1]]
        self.selected_figure_moves = self.generate_moves(self.player_map, figure=self.selected_figure)
        return self.selected_figure_moves

    def testing(self):
        '''ONLY FOR TESTING'''
        skin = '1'
        self.player_map = [
            [Rook(0, 0, 'B', skin, False), Knight(0, 1, 'B', skin), Bishop(0, 2, 'B', skin), Queen(0, 3, 'B', skin),
             King(0, 4, 'B', skin, False),
             Bishop(0, 5, 'B', skin), Knight(0, 6, 'B', skin), Rook(0, 7, 'B', skin, False)],
            [Pawn(1, 0, 'B', skin, False), Pawn(1, 1, 'B', skin, False), Pawn(1, 2, 'B', skin, False),
             Pawn(1, 3, 'B', skin, False),
             Pawn(1, 4, 'B', skin, False), Pawn(1, 5, 'B', skin, False), Pawn(1, 6, 'B', skin, False),
             Pawn(1, 7, 'B', skin, False)],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],git
            [0, 0, 0, 0, 0, 0, 0, 0],
            [Pawn(6, 0, 'W', skin, False), Pawn(6, 1, 'W', skin, False), Pawn(6, 2, 'W', skin, False),
             Pawn(6, 3, 'W', skin, False),
             Pawn(6, 4, 'W', skin, False), Pawn(6, 5, 'W', skin, False), Pawn(6, 6, 'W', skin, False),
             Pawn(6, 7, 'W', skin, False)],
            [Rook(7, 0, 'W', skin, False), Knight(7, 1, 'W', skin), Bishop(7, 2, 'W', skin), Queen(7, 3, 'W', skin),
             King(7, 4, 'W', skin, False),
             Bishop(7, 5, 'W', skin), Knight(7, 6, 'W', skin), Rook(7, 7, 'W', skin, False)]]

    def get_king_elimination_positions(self, color):
        '''
            Vrati pozicie figurok ktore mozu vyhodit krala farby color
        '''

        temp = []
        if color == 'W':
            for j in self.player_map:
                for i in j:
                    if i and i == 'B':
                        el = i.check_king(self.player_map, self.kings[1].poz)
                        if el:
                            temp.append(el)
        else:
            for j in self.player_map:
                for i in j:
                    if i and i == 'W':
                        el = i.check_king(self.player_map, self.kings[0].poz)
                        if el:
                            temp.append(el)
        return temp

    def find_king(self):
        for line in self.player_map:
            for figure in line:
                if figure == King and figure.color == 'B':
                    return True
        return False

    def ai_move(self, depth=3):
        print("Generating moves Alpha-Beta------")
        t = time.time()
        move, score = self.alpha_beta(self.player_map, depth, 1)
        if not move:
            move = choice(self.generate_moves(self.player_map, color='B'))
        print(f'{move}, time = {round(time.time()-t, 2)}')
        print('---------------------------------')
        return move

    def alpha_beta(self, board, depth=2, color=1, alpha=None, beta=None):
        '''
            Algoritmus na generovanie pohybov
        :param board: Hracia plocha pre ktoru sa generuju pohyby
        :param depth: Hlbka do kotrej ma algoritmus dojst
        :param color: Farba pre ktore generuje funkcia pohyby v danom pohybe (funkcia je rekurizvna, farby sa striedaju)
        :param alpha: Hodnota ktoru sa snazime maximalizovat
        :param beta:  Hodnotu ktoru sa snazime minimalizovat
        :return: Najlepsi pohyb pre ciernych (AI)
        '''
        if not depth:
            return 0, self.evaluate(board)
        if color:
            moves = self.generate_moves(board, 'B')
            best_move = 0
            score = 9999
            for move in moves:
                self.move_figure(move, board, True)
                minmax_s = self.alpha_beta(board, depth - 1, abs(color - 1), alpha=score)
                if beta is not None and minmax_s[1] < beta:
                    self.undo(board)
                    return best_move, minmax_s[1]
                if score > minmax_s[1]:
                    score = minmax_s[1]
                    best_move = move
                self.undo(board)
            return best_move, score
        else:
            moves = self.generate_moves(board, 'W')
            score = -9999
            for move in moves:
                self.move_figure(move, board, True)
                minmax_s = self.alpha_beta(board, depth - 1, abs(color - 1), beta=score)
                if alpha is not None and minmax_s[1] > alpha:
                    self.undo(board)
                    return 0, minmax_s[1]
                if score < minmax_s[1]:
                    score = minmax_s[1]
                self.undo(board)
            return 0, score

    def move_figure(self, move, pole=None, minmax=False):
        """
            Pohne z figurkou, prepise pole a updatne figurku
        :param move: YXyx, YX-yove, xove suradnice figurky, yx-yove, xove suradnice novej pozicie
        :param pole: hracie pole
        :return: None
        """

        if pole is None:
            pole = self.player_map

        elimineted_figure = 0
        elimineted_figure_type = 0
        y, x, new_pos_y, new_pos_x = move[0], move[1], move[2], move[3]
        figure = pole[y][x]

        figure_stats = 0  # Iba pre Rook, King, Pawn pretoze treba zaznamenavat ci sa uz pohli lebo to ovplivnuje ich dalsie mozne pohybi
        rook_el = 0

        figure_movement = []

        if figure == Pawn and not pole[new_pos_y][new_pos_x] and abs(x - new_pos_x) == 1 \
                and abs(y - new_pos_y) == 1:  # Mozny special case ked hybeme s Pawn (En Passant)
            elimineted_figure, pole[y][new_pos_x] = pole[y][new_pos_x], 0
            if elimineted_figure:
                elimineted_figure.image = None
            pole[new_pos_y][new_pos_x] = figure
            pole[y][x] = 0
        elif figure == King and abs(x - new_pos_x) == 2:
            pole[new_pos_y][new_pos_x], pole[y][x] = pole[y][x], 0
            if x > new_pos_x:
                rook_el, pole[y][x - 1], pole[y][0] = pole[y][0], pole[y][0], 0
                self.old.append(((y, 0, y, x - 1), rook_el.get_moving_stats(), 0, 0, 0))
                pole[y][x - 1].update_figure((y, x - 1))
                figure_movement.append((y, 0, y, x - 1))
            else:
                rook_el, pole[y][x + 1], pole[y][7] = pole[y][7], pole[y][7], 0
                self.old.append(((y, 7, y, x + 1), rook_el.get_moving_stats(), 0, 0, 0))
                pole[y][x + 1].update_figure((y, x + 1))
                figure_movement.append((y, 7, y, x + 1))
            rook_el = 1
        else:
            elimineted_figure, pole[new_pos_y][new_pos_x] = pole[new_pos_y][new_pos_x], figure
            if elimineted_figure:
                elimineted_figure.image = None

            pole[y][x] = 0

        if elimineted_figure:
            elimineted_figure_type = type(elimineted_figure)
            elimineted_figure = elimineted_figure.get_stats()

        figure_movement.append((y, x, new_pos_y, new_pos_x))
        figure_stats = figure.get_moving_stats()
        figure.update_figure(move[2:])

        self.pawn_promotion_move = 0

        if figure == Pawn and figure.y in (0, 7):
            self.pawn_promotion_move = (y, x, new_pos_y, new_pos_x)
            self.old.append((0, 1, elimineted_figure_type, elimineted_figure, 0))
            if minmax:
                self.pawn_to_promote = figure
                self.pawn_promotion(Queen)
        else:
            self.old.append((move, figure_stats, elimineted_figure_type, elimineted_figure, rook_el))

        return figure_movement

    def king_elimination_paths(self, king):
        '''
            Vrati cesty ktore vyhodia krala
        :param pole: hracie pole
        :param pos: kral
        :return: cesty
        '''

        paths = []

        for line in self.player_map:
            for figure in line:
                if figure == king.enemy:
                    path = figure.king_elimination_path(self.player_map, (king.y, king.x))
                    if path:
                        paths.append(path)

        return paths

    def end_round_update(self):
        '''
            Zavola vsetky potrebne funkcia na koniec kola
        :return:
        '''
        # TODO: Treba dopisat

        self.en_passant_update()

        figure = self.check_pawn_promotion()
        if figure:
            if self.ai and figure.color == 'B':
                self.pawn_promotion(choose_random_promotion())
            else:
                return figure

        self.update_king_elimination_positions()
        if not self.can_move_a_figure("W") or not self.can_move_a_figure("B"):
            if self.king_w_elimation_positions:
                return "white"
            elif self.king_b_elimation_positions:
                return "black"
            else:
                return "stailmate"

    def en_passant_update(self):
        figure = self.moved_byt_two_figure

        if figure:
            figure.moved_byt_two = False

        for line in self.player_map:
            for figure in line:
                if figure == Pawn and figure.moved_byt_two:
                    self.moved_byt_two_figure = figure

    def evaluate(self, pole=None):
        if pole is None:
            pole = self.player_map
        score = 0
        for line in pole:
            for figure in line:
                if figure:
                    if figure == 'B':
                        score -= self.figure_score(figure)
                    else:
                        score += self.figure_score(figure)

        return score

    def figure_score(self, figure):
        poz = figure.y * 8 + figure.x
        if figure == 'B':
            poz = -(figure.y * 8 + figure.x) - 1
        if figure == Pawn:
            return figure.score + self.pawn_table[poz]
        if figure == Rook:
            return figure.score + self.rook_table[poz]
        if figure == Bishop:
            return figure.score + self.bishop_table[poz]
        if figure == Knight:
            return figure.score + self.knight_table[poz]
        if figure == Queen:
            return figure.score + self.queen_table[poz]
        if figure == King:
            return figure.score + self.king_table[poz]

    def undo(self, pole=None):

        if pole is None:
            pole = self.player_map

        figure_move, figure_stats, elimineted_figure, elimineted_figure_stats, more_elimination = self.old.pop()
        self.moved_byt_two_figure = None

        if figure_move:
            pole[figure_move[0]][figure_move[1]], pole[figure_move[2]][figure_move[3]] = \
                pole[figure_move[2]][figure_move[3]], 0
            figure = pole[figure_move[0]][figure_move[1]]
            figure.y, figure.x = figure_move[0], figure_move[1]

        if figure_stats != 1:
            if figure == Pawn:
                figure.moved, figure.moved_byt_two = figure_stats
            else:
                figure.moved = figure_stats

        if elimineted_figure:
            figure = elimineted_figure(*elimineted_figure_stats)
            pole[figure.y][figure.x] = figure

        if more_elimination:
            self.undo()

    def pawn_promotion(self, new_figure_type):
        '''
            Promotne `figure` na `new_figure_type`
        :param pole: hracie pole
        :param figure: Pawn ktory ma byt promotnuti
        :param new_figure_type: Typ na ktory ma byt promotnuti
        :return:
        '''

        self.player_map[self.pawn_to_promote.y][self.pawn_to_promote.x] = new_figure_type(self.pawn_to_promote.y,
                                                                                          self.pawn_to_promote.x,
                                                                                          self.pawn_to_promote.color)
        y, x, *_ = self.pawn_promotion_move
        self.old.append((self.pawn_promotion_move, 1, Pawn, (y, x, *self.pawn_to_promote.get_stats()[2:]), 1))
        del self.pawn_to_promote

    def generate_moves(self, pole, color='W', figure_pos=None, figure=None):
        '''
            Vrati vygenerovane pohyby, bud pre `color` alebo danu figurku na
            `figure_pos`, ak je figurkyn kral v nebezpeci tak vrati iba take
            pohyby ktore zacharania krala
        :param pole: hracie pole
        :param color: farba pre ktoru sa vygeneruju pohyby
        :param figure_pos: pozicia figurky pre ktoru sa vygeneruju pohyby
        :param figure: figurka pre ktoru sa vygeneruju pohyby
        :return: pole pohybov
        '''

        if figure_pos is not None or figure is not None:
            if figure_pos is not None:
                figure = pole[figure_pos[0]][figure_pos[1]]
            # moves = self.filter_king_save_moves(
            #     [(figure.y, figure.x, *move) for move in figure.allowed_moves(self.player_map)])
            return [(figure.y, figure.x, *move) for move in figure.allowed_moves(self.player_map)]

        moves = []
        for line in pole:
            for figure in line:
                if figure == color:
                    for move in figure.allowed_moves(self.player_map):
                        moves.append((figure.y, figure.x, *move))

        return moves

    def filter_king_save_moves(self, moves):
        '''
            Funkcia prejde cez pohyby v `moves` a vrati tie ktore zachrania
            krala ak je v nebezpeci
        :param moves: Pole pozicii na ktore sa figurka/y moze pohnut
        :return: pozicie ktore zacharania krala
        '''

        if not moves:
            # print(moves, repr(moves), type(moves))
            return []

        figure = self.player_map[moves[0][0]][moves[0][1]]

        if figure == King:
            return moves

        if figure.color == 'W':
            king_save = self.king_w_elimation_positions
        else:
            king_save = self.king_b_elimation_positions

        if king_save:
            if len(king_save) > 1:
                return []
            moves = list(filter(lambda m: (m[2], m[3]) in king_save[0], moves))
        return moves

    def update_king_elimination_positions(self):
        w_k, b_k = 0, 0

        for line in self.player_map:
            for figure in line:
                if figure == King:
                    if figure.color == 'W':
                        w_k = figure
                    else:
                        b_k = figure
                    if w_k and b_k:
                        break

        self.king_b_elimation_positions = self.king_elimination_paths(b_k)
        self.king_w_elimation_positions = self.king_elimination_paths(w_k)

    def can_move_a_figure(self, color):
        '''
            Funkcia zisti ci hrac farby `color` ma figurku z ktorou sa
            moze pohnut ak nema vrati funkcia False == je remiza
        :param color:
        :return:
        '''
        if self.generate_moves(self.player_map, color):
            return True
        return False

    def check_pawn_promotion(self):
        '''
            Funkcia ktora povie ci je nejaka Pawn vhodny na promotion
        :return: Figurka (Pawn) na promotion
        '''

        self.pawn_to_promote = None

        for figure in self.player_map[0]:
            if figure == Pawn and figure.color == 'W':
                self.pawn_to_promote = figure
                break

        for figure in self.player_map[7]:
            if figure == Pawn and figure.color == 'B':
                self.pawn_to_promote = figure
                break
        return self.pawn_to_promote

    def ascii(self, pole=None):
        '''
            Prints an ascii representation of the Board and the the indexes of player_map for debugging
        :return:
        '''

        if pole is None:
            pole = self.player_map

        print('+' + '-' * 35 + '+')
        i = 0
        for line in pole:
            print(f'|{i}  ', end='')
            for figure in line:
                if figure:
                    print(figure, end='  ')
                else:
                    print('..', end='  ')
            print('|')
            i += 1
        print('|   ', end='')
        for i in range(8):
            print(f'0{i}', end='  ')
        print('|\n+' + '-' * 35 + '+')


def choose_random_promotion():
    return choice((Rook, Queen, Knight, Bishop))


if __name__ == '__main__':
    g = Chess()
    g.testing()

    g.player_map[7][5], g.player_map[7][6], g.player_map[6][5] = 0, 0, 0
    print()
    print(g.generate_moves(g.player_map, figure_pos=(6, 2)))

    g.move_figure((6, 2, 5, 2))

    print()
    print(g.generate_moves(g.player_map, figure_pos=(5, 2)))

    g.ascii()
