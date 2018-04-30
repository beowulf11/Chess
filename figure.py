import tkinter


# TODO Naco je poz v str staci nech tam je x a y prepisat

class Figure:
    def __init__(self, v_poz, h_poz, color, skin):
        self.enemy = ['W', 'B'].pop(['W', 'B'].index(color) - 1)
        self.name = ''
        self.color = color
        self.skin = skin

        self.x = h_poz
        self.y = v_poz

        self.x_p = 0  # pixel pozicie na sachovnici
        self.y_p = 0  # pixel pozicie na sachovnici

        self.image_id = -1
        self.image = 0

        self.score = 0

    def create_skin(self):
        if self.skin:
            self.image = tkinter.PhotoImage(file=f'Images/{self.name[1].lower()}{self.color}{self.skin}.png')

    def allowed_moves(self, pole):
        '''
            Funkcia pomocou fukncie possible_moves urcite vsetky mozne pohybi a potom prefiltruje a zisti ktore pohyby
            su mozne na danej hracej ploche pre danu figurku
        :param pole: hracie pole
        :return: pole obsahujuce mozne pohyby k danemu polu
        '''
        all_moves = []
        for move in self.possible_moves():
            for poz in move:
                if pole[poz[0]][poz[1]] and pole[poz[0]][poz[1]] == self.color:
                    break
                elif pole[poz[0]][poz[1]] and pole[poz[0]][poz[1]] == self.enemy:
                    if pole[poz[0]][poz[1]] != King:
                        all_moves.append(poz)
                        break
                    break
                else:
                    all_moves.append(poz)
        return self.filter(pole, all_moves)

    def update_figure(self, new_poz):
        self.y, self.x = new_poz[0], new_poz[1]

    def check_king(self, pole, s_pos):
        '''
            Skontroluje ci Queen, Rook alebo Bishop moze vyhodit krala
        '''
        for moves in self.possible_moves():
            for move in moves:
                if move == s_pos:
                    return [(self.y, self.x)]
                elif pole[move[0]][move[1]]:
                    break
        return []

    def king_elimination_path(self, pole, king_pos):
        for moves in self.possible_moves():
            for i, move in enumerate(moves):
                if move == king_pos:
                    return [(self.y, self.x)] + moves[:i]
                elif pole[move[0]][move[1]]:
                    break

        return []

    def king_checking_paths(self, pole):
        for line in pole:
            for figure in line:
                if figure == self.color and figure == King:
                    king = figure
                    break

        paths = []
        current_figure, pole[self.y][self.x] = pole[self.y][self.x], 0
        for line in pole:
            for figure in line:
                if figure and figure.color == king.enemy:
                    path = figure.king_elimination_path(pole, (king.y, king.x))
                    if path:
                        paths.append(path)

        pole[self.y][self.x] = current_figure
        return paths

    def get_stats(self):
        return self.y, self.x, self.color, self.skin

    def get_stats_save(self):
        return self.get_stats()[:-1]

    def filter(self, pole, all_moves):
        pole[self.y][self.x] = 0
        danger = self.king_checking_paths(pole)
        pole[self.y][self.x] = self
        if len(danger) > 1:
            return []
        if len(danger) == 1:
            danger = danger[0]
            return [move for move in all_moves if move in danger]
        return all_moves

    def get_moving_stats(self):
        return 1

    def __eq__(self, other):
        if isinstance(other, str):
            return self.color == other
        return isinstance(self, other)

    def __ne__(self, other):
        if isinstance(other, str):
            return self.color != other
        return not isinstance(self, other)

    def __str__(self):
        return self.name[:2]

    __repr__ = __str__


class Queen(Figure):
    def __init__(self, v_poz, h_poz, color, skin=''):
        super().__init__(v_poz, h_poz, color, skin)

        self.name = color + 'Q'

        self.create_skin()

        self.score = 90

    def possible_moves(self):
        '''
            Fukcia urci vsetky mozne pozicie pre pohyb Queen
        :return: dvojrozmerne pole vsetkych moznych pohybov
        '''
        all_moves = []
        # volne pozicie hore

        moves = []
        for i in range(0, self.y):
            moves.insert(0, (i, self.x))
        if moves:
            all_moves.append(moves)

        # volne pozicie do prava
        moves = []
        for i in range(self.x + 1, 8):
            moves.append((self.y, i))
        if moves:
            all_moves.append(moves)

        # volne pozicie dole
        moves = []
        for i in range(self.y + 1, 8):
            moves.append((i, self.x))
        if moves:
            all_moves.append(moves)

        # volne pozicie do lava
        moves = []
        for i in range(0, self.x):
            moves.insert(0, (self.y, i))
        if moves:
            all_moves.append(moves)

        # volne pozicie do prava hore
        moves = []
        h, v = self.y - 1, self.x + 1
        while h >= 0 and v < 8:
            moves.append((h, v))
            h -= 1
            v += 1
        if moves:
            all_moves.append(moves)

        # volne pozicie do prava dole
        moves = []
        h, v = self.y + 1, self.x + 1
        while h < 8 and v < 8:
            moves.append((h, v))
            h += 1
            v += 1
        if moves:
            all_moves.append(moves)

        # volne pozicie do lava dole
        moves = []
        h, v = self.y + 1, self.x - 1
        while h < 8 and v >= 0:
            moves.append((h, v))
            h += 1
            v -= 1
        if moves:
            all_moves.append(moves)

        # volne pozicie do lava hore
        moves = []
        h, v = self.y - 1, self.x - 1
        while h >= 0 and v >= 0:
            moves.append((h, v))
            h -= 1
            v -= 1
        if moves:
            all_moves.append(moves)

        return all_moves


class Rook(Figure):
    def __init__(self, v_poz, h_poz, color, skin='', moved=True):
        super().__init__(v_poz, h_poz, color, skin)

        # Sliding hovori si sa moze robit King Sliding co zalezi natom ci sa figurka pohla
        self.name = color + 'R'

        self.create_skin()

        self.moved = moved

        self.score = 50

    def possible_moves(self):
        '''
            Fukcia urci vsetky mozne pozicie pre pohyb Rook
        :return: dvojrozmerne pole vsetkych moznych pohybov
        '''
        all_moves = []

        # volne pozicie hore
        moves = []
        for i in range(0, self.y):
            moves.insert(0, (i, self.x))
        if moves:
            all_moves.append(moves)

        # volne pozicie do prava
        moves = []
        for i in range(self.x + 1, 8):
            moves.append((self.y, i))
        if moves:
            all_moves.append(moves)

        # volne pozicie dole
        moves = []
        for i in range(self.y + 1, 8):
            moves.append((i, self.x))
        if moves:
            all_moves.append(moves)

        # volne pozicie do lava
        moves = []
        for i in range(0, self.x):
            moves.insert(0, (self.y, i))
        if moves:
            all_moves.append(moves)

        return all_moves

    def update_figure(self, new_poz):
        """
            Updatne Rook s novou poziciou, ak sa este Rook nepohol zaznamena to
        :param new_poz: nova pozicia Rook
        """
        super().update_figure(new_poz)
        if not self.moved:
            self.moved = True

    def get_stats(self):
        return super().get_stats() + ((self.moved,))

    def get_stats_save(self):
        return super().get_stats()[:-1] + ((self.moved,))

    def get_moving_stats(self):
        return self.moved


class Bishop(Figure):
    def __init__(self, v_poz, h_poz, color, skin=''):
        super().__init__(v_poz, h_poz, color, skin)

        self.name = color + 'B'

        self.create_skin()

        self.score = 30

    def possible_moves(self):
        '''
            Fukcia urci vsetky mozne pozicie pre pohyb Bishop
        :return: dvojrozmerne pole vsetkych moznych pohybov
        '''

        all_moves = []

        # volne pozicie do prava hore
        moves = []
        h, v = self.y - 1, self.x + 1
        while h >= 0 and v < 8:
            moves.append((h, v))
            h -= 1
            v += 1
        if moves:
            all_moves.append(moves)

        # volne pozicie do prava dole
        moves = []
        h, v = self.y + 1, self.x + 1
        while h < 8 and v < 8:
            moves.append((h, v))
            h += 1
            v += 1
        if moves:
            all_moves.append(moves)

        # volne pozicie do lava dole
        moves = []
        h, v = self.y + 1, self.x - 1
        while h < 8 and v >= 0:
            moves.append((h, v))
            h += 1
            v -= 1
        if moves:
            all_moves.append(moves)

        # volne pozicie do lava hore
        moves = []
        h, v = self.y - 1, self.x - 1
        while h >= 0 and v >= 0:
            moves.append((h, v))
            h -= 1
            v -= 1
        if moves:
            all_moves.append(moves)

        return all_moves


class Knight(Figure):
    def __init__(self, v_poz, h_poz, color, skin=''):
        super().__init__(v_poz, h_poz, color, skin)

        self.name = color + 'N'

        self.create_skin()

        self.score = 30

    def possible_moves(self):
        '''
            Fukcia urci vsetky mozne pozicie pre pohyb Knight
        :return: dvojrozmerne pole vsetkych moznych pohybov
        '''
        all_moves = []
        if self.y - 2 >= 0 and self.x + 1 <= 7:
            all_moves.append((self.y - 2, self.x + 1))

        if self.y - 1 >= 0 and self.x + 2 <= 7:
            all_moves.append((self.y - 1, self.x + 2))

        if self.y + 2 <= 7 and self.x + 1 <= 7:
            all_moves.append((self.y + 2, self.x + 1))

        if self.y + 1 <= 7 and self.x + 2 <= 7:
            all_moves.append((self.y + 1, self.x + 2))

        if self.y - 2 >= 0 and self.x - 1 >= 0:
            all_moves.append((self.y - 2, self.x - 1))

        if self.y - 1 >= 0 and self.x - 2 >= 0:
            all_moves.append((self.y - 1, self.x - 2))

        if self.y + 2 <= 7 and self.x - 1 >= 0:
            all_moves.append((self.y + 2, self.x - 1))

        if self.y + 1 <= 7 and self.x - 2 >= 0:
            all_moves.append((self.y + 1, self.x - 2))

        return all_moves

    def allowed_moves(self, pole):
        '''
            Funkcia pomocou fukncie possible_moves urci vsetky mozne pohybi a potom prefiltruje a zisti ktore pohyby
            su mozne na danej hracej ploche pre Knight
        :return: pole obsahujuce mozne pohyby k danemu polu
        '''
        all_moves = []
        for poz in self.possible_moves():
            # if poz[0] in range(8) and poz[1] in range(8):  # Ked je pozicia na hracej ploche
            if pole[poz[0]][poz[1]]:  # Ked sa na pozicii nachadza Figurka
                # Ked sa na pozicii nachadza vlastna figurka alebo Kral
                if pole[poz[0]][poz[1]] == self.color or pole[poz[0]][poz[1]] == King:
                    continue
                else:
                    all_moves.append(poz)
            else:
                all_moves.append(poz)

        return self.filter(pole, all_moves)

    def check_king(self, pole, s_pos):
        '''
            Skontroluje ci Knight moze vyhodit krala
        '''
        for i in self.possible_moves():
            if i == s_pos:
                return [(self.y, self.x)]
        return []

    def king_elimination_path(self, pole, king_pos):
        for move in self.possible_moves():
            if move == king_pos:
                return [(self.y, self.x)]
        return []


class Pawn(Figure):
    def __init__(self, v_poz, h_poz, color, skin='', moved=True, moved_byt_two=False):
        super().__init__(v_poz, h_poz, color, skin)

        self.name = color + 'P'

        self.create_skin()

        self.moved = moved  # Attribut ktory hovori otom ci sa figurka pohla za hru

        self.moved_byt_two = moved_byt_two

        self.score = 10

    def possible_moves(self):
        '''
            Fukcia urci vsetky mozne pozicie pre pohyb Pawn bez ohladu na ostatne figurky
        :return: pole vsetkych moznych pohybov
        '''

        moves = []

        # Pawn je Black
        if self.color == 'B':
            for y, x in ((1, -1), (1, 0), (1, 1)):
                moves.append((self.y + y, self.x + x))
            if not self.moved: # Ked sa Pawn este nepohol ma dodatocnu moznost skocit o 2 policka dopredi
                moves.append((self.y + 2, self.x))

        # Pawn je White
        else:
            for y, x in ((-1, -1), (-1, 0), (-1, 1)):
                moves.append((self.y + y, self.x + x))
            if not self.moved: # Ked sa Pawn este nepohol ma dodatocnu moznost skocit o 2 policka dopredi
                moves.append((self.y - 2, self.x))

        return moves

    def attacking_pos(self):
        """
            Funkcia podla farby figurky vrati pole pozicii ktore moze Pawn vyhodit
        :return:
        """

        # Pawn je Black
        if self.color == 'B':
            return [(self.y + 1, self.x - 1), (self.y + 1, self.x + 1)]

        # Pawn je White
        else:
            return [(self.y - 1, self.x - 1), (self.y - 1, self.x + 1)]

    def allowed_moves(self, pole):
        '''
            Funkcia pomocou fukncie possible_moves urci vsetky mozne pohybi a potom prefiltruje a zisti ktore pohyby
            su mozne na danej hracej ploche pre Pawn
        :return: pole obsahujuce mozne pohyby k danemu polu
        '''

        pozs = self.possible_moves()
        all_moves = []

        # prva pozicia je na lavo od Pawn
        try:
            prvok = pole[pozs[0][0]][pozs[0][1]]
            prvok1 = pole[self.y][self.x - 1]
        except:
            prvok = prvok1 = 0
        if pozs[0][0] not in range(0, 8) or pozs[0][1] not in range(0,8):
            prvok = prvok1 = 0
        if prvok and prvok != King:  # Ked je policko obsadene figurkou ktora neni Kral
            if prvok == self.enemy:  # Ked sa na policku nachadza nepriatel
                all_moves.append(pozs[0])

        # pozre vedla Pawn do lava ci sa vedla nech nachadza Pawn ktory sa pohol o 2 policka a moze sa spravi En passant
        elif not prvok and prvok1 and prvok1.color == self.enemy and prvok1 == Pawn and prvok1.moved_byt_two:
            all_moves.append(pozs[0])

        # druha pozicia, pred Pawn o 1
        prvok = pole[pozs[1][0]][pozs[1][1]]
        if not prvok:
            all_moves.append(pozs[1])
            # ked sa Pawn este nepohol ma moznost sa pohnut o dve policka dopredu
            if len(pozs) == 4:
                prvok = pole[pozs[3][0]][pozs[3][1]]
                if not prvok:
                    all_moves.append(pozs[3])

        # tretia pozicia je na pravo od Pawn
        try:
            prvok = pole[pozs[2][0]][pozs[2][1]]
            prvok1 = pole[self.y][self.x + 1]
        except:
            prvok = prvok1 = 0
        if pozs[2][0] not in range(0, 8) or pozs[2][1] not in range(0,8):
            prvok = prvok1 = 0
        if prvok and prvok != King:  # Ked je policko obsadene figurkou ktora neni Kral
            if prvok == self.enemy:  # Ked sa na policku nachadza nepriatel
                all_moves.append(pozs[2])

        # pozre vedla Pawn do prava ci sa vedla nech nachadza Pawn ktory sa pohol o 2 policka a moze sa spravi En passant
        elif not prvok and prvok1 and prvok1.color == self.enemy and prvok1 == Pawn and prvok1.moved_byt_two:
            all_moves.append(pozs[2])

        return self.filter(pole, all_moves)

    def update_figure(self, new_poz):
        """
            Updatne Pawn s novou poziciou, ak sa este pawn nepohol zaznamena to
        :param new_poz: nova pozicia Pawna
        """

        if abs(self.y - new_poz[0]) == 2:
            self.moved_byt_two = True
        self.y, self.x = new_poz[0], new_poz[1]
        self.moved = True

    def check_king(self, pole, s_pos):
        """
            Skontroluje ci Pawn moze vyhodit krala
        :param pole: Pole figurok
        :param s_pos: Pozicia Krala
        :return:
        """
        for i in self.attacking_pos():
            if i == s_pos:
                return [(self.y, self.x)]
        return []

    def king_elimination_path(self, pole, king_pos):
        for move in self.attacking_pos():
            if move == king_pos:
                return [(self.y, self.x)]
        return []

    def get_stats(self):
        return super().get_stats() + ((self.moved, self.moved_byt_two))

    def get_stats_save(self):
        return super().get_stats()[:-1] + ((self.moved, self.moved_byt_two))

    def get_moving_stats(self):
        return self.moved, self.moved_byt_two


class King(Figure):
    def __init__(self, v_poz, h_poz, color, skin='', moved=True):
        super().__init__(v_poz, h_poz, color, skin)

        self.color = color

        self.name = color + 'K'

        self.create_skin()

        self.moved = moved

        self.score = 900

    def possible_moves(self):
        """
        :return: Pole vsetkych moznych pohybov Krala bez ohladu na ostatne figurky
        """

        moves = []
        if self.y - 1 in range(0, 8):
            moves.append((self.y - 1, self.x))

        if self.y - 1 in range(0, 8) and self.x + 1 in range(0, 8):
            moves.append((self.y - 1, self.x + 1))

        if self.x + 1 in range(0, 8):
            moves.append((self.y, self.x + 1))

        if self.y + 1 in range(0, 8) and self.x + 1 in range(0, 8):
            moves.append((self.y + 1, self.x + 1))

        if self.y + 1 in range(0, 8):
            moves.append((self.y + 1, self.x))

        if self.y + 1 in range(0, 8) and self.x - 1 in range(0, 8):
            moves.append((self.y + 1, self.x - 1))

        if self.x - 1 in range(0, 8):
            moves.append((self.y, self.x - 1))

        if self.y - 1 in range(0, 8) and self.x - 1 in range(0, 8):
            moves.append((self.y - 1, self.x - 1))

        return moves

    def allowed_moves(self, pole):
        '''
            Vrati mozne pohyby krala na zaklade pola + ked sa kral nepohol
            pozrie sa moze nastat castling
        :param pole: pole figurok
        :return: Pole vsetkych moznych pohybov Krala z ohladom na ostatne figurky
        '''
        all_moves = []

        # Ulozi si poziciu Krala a nahradiho prazdnym polickom
        king = pole[self.y][self.x]
        pole[self.y][self.x] = 0

        for move in self.possible_moves():
            # Ked je policko obsadene figurkou s tou istou farbou ako je kral
            if pole[move[0]][move[1]] and pole[move[0]][move[1]] == self.color:
                continue
            # Bud je policko prazdne alebo sa na nom nachadza nepriatel, treba skontrolovat moznost pohybu
            elif self.save_position(pole, move):
                all_moves.append(move)

        # Vrati naspat krala na povodne policko
        pole[self.y][self.x] = king

        # Pozrie sa ci kral moze spravi castling
        castle_moves = []
        if not self.moved and self.save_position(pole, (self.y, self.x)):
            if (self.y, self.x + 1) in all_moves and self.save_position(pole, (self.y, self.x + 2)) and\
                    not pole[self.y][self.x + 2]:
                if pole[7][7] == Rook and pole[7][7] == self.color and not pole[7][7].moved:
                    castle_moves.append((self.y, self.x + 2))
                elif pole[0][7] == Rook and pole[0][7] == self.color and not pole[0][7].moved:
                    castle_moves.append((self.y, self.x + 2))
            elif (self.y, self.x - 1) in all_moves and self.save_position(pole, (self.y, self.x - 2)) and \
                    not pole[self.y][self.x - 2] and not pole[self.y][self.x - 3]:
                if pole[7][0] == Rook and pole[7][0] == self.color and not pole[7][0].moved:
                    castle_moves.append((self.y, self.x - 2))
                elif pole[0][0] == Rook and pole[0][0] == self.color and not pole[0][0].moved:
                    castle_moves.append((self.y, self.x - 2))

        return all_moves + castle_moves

    def update_figure(self, new_poz):
        """
            Updatne Krala s novou poziciou, ak sa este kral nepohol zaznamena to
        :param new_poz: nova pozicia Krala
        """
        super().update_figure(new_poz)
        if not self.moved:
            self.moved = True

    def check_king(self, pole, s_pos):
        '''
            Skontroluje ci Kral moze vyhodit krala
        '''
        for i in self.possible_moves():
            if i == s_pos:
                return [(self.y, self.x)]
        return []

    def save_position(self, pole, pos):
        """
            Skontroluje ci je pozicia `pos` bezpecna pre Krala
        :param pole:
        :param pos:
        :return: True/False
        """

        fig, pole[pos[0]][pos[1]] = pole[pos[0]][pos[1]], 0

        for line in pole:
            for figure in line:
                if figure and figure == self.enemy:
                    if figure.check_king(pole, pos):
                        pole[pos[0]][pos[1]] = fig
                        return False

        pole[pos[0]][pos[1]] = fig

        return True

    def king_elimination_path(self, pole, king_pos):
        for i in self.possible_moves():
            if i == king_pos:
                return [(self.y, self.x)]
        return []

    def get_stats(self):
        return super().get_stats() + ((self.moved,))

    def get_stats_save(self):
        return super().get_stats()[:-1] + ((self.moved,))

    def get_moving_stats(self):
        return self.moved
