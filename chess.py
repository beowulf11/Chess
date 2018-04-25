from figure import Queen, Rook, Bishop, Knight, Pawn, King
from random import choice

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

'''


class Chess:
    def __init__(self, ai):
        self.player_map = [[0 for _ in range(8)] for _ in range(8)]

        self.saving_pos_w_king = []
        self.saving_pos_b_king = []

        self.pawn_table = [0, 0, 0, 0, 0, 0, 0, 0,
                           50, 50, 50, 50, 50, 50, 50, 50,
                           10, 10, 20, 30, 30, 20, 10, 10,
                           5, 5, 10, 25, 25, 10, 5, 5,
                           0, 0, 0, 20, 20, 0, 0, 0,
                           5, -5, -10, 0, 0, -10, -5, 5,
                           5, 10, 10, -20, -20, 10, 10, 5,
                           0, 0, 0, 0, 0, 0, 0, 0]
        self.knight_table = [-50, -40, -30, -30, -30, -30, -40, -50,
                             -40, -20, 0, 0, 0, 0, -20, -40,
                             -30, 0, 10, 15, 15, 10, 0, -30,
                             -30, 5, 15, 20, 20, 15, 5, -30,
                             -30, 0, 15, 20, 20, 15, 0, -30,
                             -30, 5, 10, 15, 15, 10, 5, -30,
                             -40, -20, 0, 5, 5, 0, -20, -40,
                             -50, -40, -30, -30, -30, -30, -40, -50, ]
        self.bishop_table = [-20, -10, -10, -10, -10, -10, -10, -20,
                             -10, 0, 0, 0, 0, 0, 0, -10,
                             -10, 0, 5, 10, 10, 5, 0, -10,
                             -10, 5, 5, 10, 10, 5, 5, -10,
                             -10, 0, 10, 10, 10, 10, 0, -10,
                             -10, 10, 10, 10, 10, 10, 10, -10,
                             -10, 5, 0, 0, 0, 0, 5, -10,
                             -20, -10, -10, -10, -10, -10, -10, -20, ]
        self.rook_table = [0, 0, 0, 0, 0, 0, 0, 0,
                           5, 10, 10, 10, 10, 10, 10, 5,
                           -5, 0, 0, 0, 0, 0, 0, -5,
                           -5, 0, 0, 0, 0, 0, 0, -5,
                           -5, 0, 0, 0, 0, 0, 0, -5,
                           -5, 0, 0, 0, 0, 0, 0, -5,
                           -5, 0, 0, 0, 0, 0, 0, -5,
                           0, 0, 0, 5, 5, 0, 0, 0]
        self.queen_table = [-20, -10, -10, -5, -5, -10, -10, -20,
                            -10, 0, 0, 0, 0, 0, 0, -10,
                            -10, 0, 5, 5, 5, 5, 0, -10,
                            -5, 0, 5, 5, 5, 5, 0, -5,
                            0, 0, 5, 5, 5, 5, 0, -5,
                            -10, 5, 5, 5, 5, 5, 0, -10,
                            -10, 0, 5, 0, 0, 0, 0, -10,
                            -20, -10, -10, -5, -5, -10, -10, -20]
        self.king_table = [-30, -40, -40, -50, -50, -40, -40, -30,
                           -30, -40, -40, -50, -50, -40, -40, -30,
                           -30, -40, -40, -50, -50, -40, -40, -30,
                           -30, -40, -40, -50, -50, -40, -40, -30,
                           -20, -30, -30, -40, -40, -30, -30, -20,
                           -10, -20, -20, -20, -20, -20, -20, -10,
                           20, 20, 0, 0, 0, 0, 20, 20,
                           20, 30, 10, 0, 0, 10, 30, 20]

        self.old = []

        self.king_w_elimation_positions = []
        self.king_b_elimation_positions = []

        self.pawn_en_pasant = 0

        self.ai = ai

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
        self.kings = [King(0, 4, 'B', skin, False), King(7, 4, 'W', skin, False)]
        self.player_map = [
            [Rook(0, 0, 'B', skin, False), Knight(0, 1, 'B', skin), Bishop(0, 2, 'B', skin), Queen(0, 3, 'B', skin),
             self.kings[0],
             Bishop(0, 5, 'B', skin), Knight(0, 6, 'B', skin), Rook(0, 7, 'B', skin, False)],
            [Pawn(1, 0, 'B', skin, False), Pawn(1, 1, 'B', skin, False), Pawn(1, 2, 'B', skin, False),
             Pawn(1, 3, 'B', skin, False),
             Pawn(1, 4, 'B', skin, False), Pawn(1, 5, 'B', skin, False), Pawn(1, 6, 'B', skin, False),
             Pawn(1, 7, 'B', skin, False)],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [Pawn(6, 0, 'W', skin, False), Pawn(6, 1, 'W', skin, False), Pawn(6, 2, 'W', skin, False),
             Pawn(6, 3, 'W', skin, False),
             Pawn(6, 4, 'W', skin, False), Pawn(6, 5, 'W', skin, False), Pawn(6, 6, 'W', skin, False),
             Pawn(6, 7, 'W', skin, False)],
            [Rook(7, 0, 'W', skin, False), Knight(7, 1, 'W', skin), Bishop(7, 2, 'W', skin), Queen(7, 3, 'W', skin),
             self.kings[1],
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

    def ai_move(self):
        moves = self.generate_moves(self.player_map, 'B')
        best_move = choice(moves)
        self.move_figure(best_move)
        score = self.evaluate()
        self.undo()
        for move in moves:
            # poz = move[2:]
            # if self.player_map[poz[0]][poz[1]] and self.player_map[poz[0]][poz[1]].color == 'W':
            # poz = move[:2]
            # if self.player_map[poz[0]][poz[1]] == Pawn:
            #     return move
            self.move_figure(move)
            if self.evaluate() < score:
                score = self.evaluate()
                best_move = move
            self.undo()
        return best_move

    def move_figure(self, move):
        """
            Pohne z figurkou, prepise pole a updatne figurku
        :param move: YXyx, YX-yove, xove suradnice figurky, yx-yove, xove suradnice novej pozicie
        :param pole: hracie pole
        :return: None
        """

        pole = self.player_map

        elimineted_figure = 0
        elimineted_figure_type = 0
        y, x, new_pos_y, new_pos_x = move[0], move[1], move[2], move[3]
        figure = pole[y][x]

        # print(move, pole[y][x])

        figure_stats = 0 # Iba pre Rook, King, Pawn pretoze treba zaznamenavat ci sa uz pohli lebo to ovplivnuje ich dalsie mozne pohybi
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

        if figure == Pawn and figure.y in (0, 7):
            self.pawn_promotion_move = (y, x, new_pos_y, new_pos_x)
            self.old.append((0, 1, elimineted_figure_type, elimineted_figure, 0))
        else:
            self.old.append((move, figure_stats, elimineted_figure_type, elimineted_figure, rook_el))

        return figure_movement

    def king_in_danger(self, pole, pos):
        '''
            Vrati ci je kral na pozicii `poz` v bezpeci
        :param pole: hracie pole
        :param pos: pozicia krala ktory ma byt skontrolovany
        :return: True/False
        '''

        king = pole[pos[0]][pos[1]]

        for line in pole:
            for figure in line:
                if figure and figure.color == king.enemy:
                    if figure.check_king(pole, (king.y, king.x)):
                        return True

        return False

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
                if figure and figure.color == king.enemy:
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

        if not self.can_move_a_figure("W") or not self.can_move_a_figure("B"):
            return "stailmate"

        self.update_king_elimination_positions()

    def en_passant_update(self):
        figure = self.moved_byt_two_figure

        if figure:
            figure.moved_byt_two = False

        for line in self.player_map:
            for figure in line:
                if figure == Pawn and figure.moved_byt_two:
                    self.moved_byt_two_figure = figure

    def evaluate(self):
        score = 0
        for line in self.player_map:
            for figure in line:
                if figure:
                    if figure.color == 'B':
                        score -= figure.score
                    else:
                        score += figure.score

        return score

    def undo(self):
        figure_move, figure_stats, elimineted_figure, elimineted_figure_stats, more_elimination = self.old.pop()
        self.moved_byt_two_figure = None

        if figure_move:
            self.player_map[figure_move[0]][figure_move[1]], self.player_map[figure_move[2]][figure_move[3]] = self.player_map[figure_move[2]][figure_move[3]], 0
            figure = self.player_map[figure_move[0]][figure_move[1]]
            figure.y, figure.x = figure_move[0], figure_move[1]

        if figure_stats != 1:
            if figure == Pawn:
                figure.moved, figure.moved_byt_two = figure_stats
            else:
                figure.moved = figure_stats

        if elimineted_figure:
            figure = elimineted_figure(*elimineted_figure_stats)
            self.player_map[figure.y][figure.x] = figure

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

        self.player_map[self.pawn_to_promote.y][self.pawn_to_promote.x] = new_figure_type(self.pawn_to_promote.y, self.pawn_to_promote.x, self.pawn_to_promote.color)
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
            return self.filter_king_save_moves([(figure.y, figure.x, *move) for move in figure.allowed_moves(self.player_map)])

        moves = []
        for line in pole:
            for figure in line:
                if figure == color:
                    if figure == King:
                        k_m = [(figure.y, figure.x, *move) for move in figure.allowed_moves(self.player_map)]
                    for move in figure.allowed_moves(self.player_map):
                        moves.append((figure.y, figure.x, *move))

        return self.filter_king_save_moves(moves) + k_m

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
            moves = list(filter(lambda m:(m[2], m[3]) in king_save[0],moves))
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
        for line in self.player_map:
            for figure in line:
                if figure and figure == color:
                    if figure.allowed_moves(self.player_map):
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

    def ascii(self):
        '''
            Prints an ascii representation of the Board and the the indexes of player_map for debugging
        :return:
        '''

        print('+' + '-' * 35 + '+')
        i = 0
        for line in self.player_map:
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
