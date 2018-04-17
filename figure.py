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

    def king_in_danger(self, pole):
        for line in pole:
            for figure in line:
                if figure and str(figure)[:2] == f'{self.color}K':
                    if figure.save_position(pole, (figure.y, figure.x)):
                        pole[self.y][self.x] = 0
                        ohrozenie = not figure.save_position(pole, (figure.y, figure.x))
                        pole[self.y][self.x] = self
                        return ohrozenie
                    return False

    def update_shadow_map(self):
        '''
            Updatne mapu vsetkych moznych pohybov
        '''
        self.map_of_moves_shadowed = self.possible_moves()

    def allowed_moves(self, pole):
        '''
            Funkcia pomocou fukncie possible_moves urcite vsetky mozne pohybi a potom prefiltruje a zisti ktore pohyby
            su mozne na danej hracej ploche pre danu figurku
        :param pole: hracie pole
        :return: pole obsahujuce mozne pohyby k danemu polu
        '''
        if self.king_in_danger(pole):
            return self.allowed_moves_king(pole)
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
        return all_moves

    def allowed_moves_king(self, pole):
        '''
            Funkcia pomocou fukncie possible_moves urcite vsetky mozne pohybi a potom prefiltruje a zisti ktore pohyby
            su mozne na danej hracej ploche pre danu figurku
        :param pole:
        :return: dojrozmene pole obsahujuce mozne pohyby k danemu polu
        '''

        # TODO: Zisti co to real robi
        all_moves = []
        curr = self
        pole[self.y][self.x] = 0
        for i in pole:
            for j in i:
                if j and str(j)[:2] == f'{self.color}K':
                    king = j
        for move in self.possible_moves():
            for poz in move:
                if pole[poz[0]][poz[1]] and pole[poz[0]][poz[1]] == self.color:
                    break
                elif pole[poz[0]][poz[1]] and pole[poz[0]][poz[1]] == self.enemy:
                    if pole[poz[0]][poz[1]].name[1] != 'K':
                        curr_enemy = pole[poz[0]][poz[1]]
                        pole[poz[0]][poz[1]] = Pawn(poz[0], poz[1], self.color, skin=0)
                        if king.save_position(pole, king.poz):
                            all_moves.append(poz)
                        pole[poz[0]][poz[1]] = curr_enemy
                        break
                    break
                else:
                    pole[poz[0]][poz[1]] = Pawn(poz[0], poz[1], self.color, skin=0)
                    if king.save_position(pole, king.poz):
                        all_moves.append(poz)
                    pole[poz[0]][poz[1]] = 0
        pole[self.y][self.x] = curr
        return all_moves

    def update_figure(self, new_poz):
        self.y, self.x = new_poz[0], new_poz[1]
        self.update_shadow_map()

    def check_king(self, pole, s_pos):
        '''
            Skontroluje ci Queen, Rook alebo Bishop moze vyhodit krala
        '''
        for moves in self.map_of_moves_shadowed:
            for move in moves:
                if move == s_pos:
                    return [(self.y, self.x)]
                elif pole[move[0]][move[1]]:
                    break
        return []

    def king_elimination_path(self, pole, king_pos):
        for moves in self.map_of_moves_shadowed:
            for i, move in enumerate(moves):
                if move == king_pos:
                    return [(self.y, self.x)] + moves[:i]
                elif pole[move[0]][move[1]]:
                    break

        return []

    def king_checking_path(self, pole, s_pos):
        '''
            Vrati naspat cestu ktora vyhodi krala, plati pre Queen, Rook a Bishop
        '''

        for moves in self.map_of_moves_shadowed:  # Prejde cez vsetky mozne polia pohybov danej figurky
            for i, tile in enumerate(moves):  # Prejde cez dane pohyby
                if tile == s_pos:  # Ak sa policko ktore je mozne pre danu figurku rovna Kralovi moze ho vyhodit
                    return [(self.y, self.x)] + moves[:i]
                # Ak narazime na hociaku figurku tato cesta uz nemoze vyhodit krala
                elif pole[int(tile[0])][int(tile[1])]:
                    break

    def king_checking_paths(self, pole):
        for line in pole:
            for figure in line:
                if figure and figure.name[:2] == f'{self.color}K':
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

        self.map_of_moves_shadowed = self.possible_moves()

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
    def __init__(self, v_poz, h_poz, color, skin='', sliding='F'):
        super().__init__(v_poz, h_poz, color, skin)

        # Sliding hovori si sa moze robit King Sliding co zalezi natom ci sa figurka pohla
        self.name = color + 'R' + sliding

        self.create_skin()

        self.sliding = sliding

        self.map_of_moves_shadowed = self.possible_moves()

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
        if self.sliding == 'T':
            self.name = self.name[:2] + 'F'
            self.sliding = 'F'

    def get_stats(self):
        return super().get_stats() + tuple(self.sliding)


class Bishop(Figure):
    def __init__(self, v_poz, h_poz, color, skin=''):
        super().__init__(v_poz, h_poz, color, skin)

        self.name = color + 'B'

        self.create_skin()

        self.map_of_moves_shadowed = self.possible_moves()

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

        self.map_of_moves_shadowed = self.possible_moves()

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
        if self.king_in_danger(pole):
            return []
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

        return all_moves

    def check_king(self, pole, s_pos):
        '''
            Skontroluje ci Knight moze vyhodit krala
        '''
        for i in self.map_of_moves_shadowed:
            if i == s_pos:
                return [(self.y, self.x)]
        return []

    def king_checking_path(self, pole, s_pos):
        '''
            Vrati naspat cestu ktora vyhodi krala, co je iba policko figurky
        '''
        return [(self.y, self.x)]

    def king_elimination_path(self, pole, king_pos):
        for move in self.map_of_moves_shadowed:
            if move == king_pos:
                return [(self.y, self.x)]
        return []


class Pawn(Figure):
    def __init__(self, v_poz, h_poz, color, skin='', moved=True):
        super().__init__(v_poz, h_poz, color, skin)

        self.name = color + 'P'

        self.create_skin()

        self.moved = moved  # Attribut ktory hovori otom ci sa figurka pohla za hru

        self.moved_byt_two = False

        self.map_of_moves_shadowed = self.attacking_pos()

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
        if prvok and prvok != King:  # Ked je policko obsadene figurkou ktora neni Kral
            if prvok == self.enemy:  # Ked sa na policku nachadza nepriatel
                all_moves.append(pozs[2])

        # pozre vedla Pawn do prava ci sa vedla nech nachadza Pawn ktory sa pohol o 2 policka a moze sa spravi En passant
        elif not prvok and prvok1 and prvok1.color == self.enemy and prvok1 == Pawn and prvok1.moved_byt_two:
            all_moves.append(pozs[2])

        danger = self.king_checking_paths(pole)
        if len(danger) > 2:
            return []
        if len(danger) == 1:
            return [move for move in all_moves if move in all_moves]

        return all_moves

    def allowed_moves_king(self, pole):
        '''
            Funkcia pomocou fukncie possible_moves urci vsetky mozne pohybi a potom prefiltruje a zisti ktore pohyby
            su mozne na danej hracej ploche pre Pawn
        :return: pole obsahujuce mozne pohyby k danemu polu
        '''
        # curr = self
        # pole[self.y][self.x] = 0
        for line in pole:
            for figure in line:
                if figure and figure.name[:2] == f'{self.color}K':
                    king = figure
                    break

        print(self.king_checking_paths(king, pole))

        pozs = self.possible_moves()
        all_moves = []

        # prva pozicia je na lavo od Pawn
        try:
            prvok = pole[pozs[0][0]][pozs[0][1]]
            prvok1 = pole[self.y][self.x - 1]
        except:
            prvok = prvok1 = 0
        if prvok and prvok.name[1] != 'K':
            if prvok == self.enemy:
                curr_enemy = pole[prvok.y][prvok.x]
                pole[prvok.y][prvok.x] = Pawn(prvok.y, prvok.x, self.color, skin=0)
                if king.save_position(pole, king.poz):
                    all_moves.append(pozs[0])
                pole[prvok.y][prvok.x] = curr_enemy

        # pozre vedla Pawn do lava ci sa vedla nech nachadza Pawn ktory sa pohol o 2 policka a moze sa spravi En passant
        elif not prvok and prvok1 and prvok1.name == self.enemy + 'PT':
            curr_enemy = pole[prvok.y][prvok.x]
            pole[prvok.y][prvok.x] = Pawn(prvok.y, prvok.x, self.color, skin=0)
            if king.save_position(pole, king.poz):
                all_moves.append(pozs[0])
            pole[prvok.y][prvok.x] = curr_enemy

        # druha pozicia pred o 1 Pawn
        prvok = pole[pozs[1][0]][pozs[1][1]]
        if not prvok:
            curr_enemy = pole[pozs[1][0]][pozs[1][1]]
            pole[pozs[1][0]][pozs[1][1]] = Pawn(pozs[1][0], pozs[1][1], self.color, skin=0)
            if king.save_position(pole, king.poz):
                all_moves.append(pozs[1])
                # ked sa Pawn este nepohol ma moznost sa pohnut o dve policka dopredu
                if len(pozs) == 4:
                    prvok = pole[pozs[3][0]][pozs[3][1]]
                    if not prvok:
                        all_moves.append(pozs[3])
            pole[pozs[1][0]][pozs[1][1]] = curr_enemy

        # prva pozicia je na pravo od Pawn
        try:
            prvok = pole[pozs[2][0]][pozs[2][1]]
            prvok1 = pole[self.y][self.x + 1]
        except:
            prvok = prvok1 = 0
        if prvok and prvok.name[1] != 'K':
            if prvok == self.enemy:
                curr_enemy = pole[prvok.y][prvok.x]
                pole[prvok.y][prvok.x] = Pawn(prvok.y, prvok.x, self.color, skin=0)
                if king.save_position(pole, king.poz):
                    all_moves.append(pozs[2])
                pole[prvok.y][prvok.x] = curr_enemy

        # pozre vedla Pawn do prava ci sa vedla nech nachadza Pawn ktory sa pohol o 2 policka a moze sa spravi En passant
        elif not prvok and prvok1 and prvok1.name == self.enemy + 'PT':
            curr_enemy = pole[prvok.y][prvok.x]
            pole[prvok.y][prvok.x] = Pawn(prvok.y, prvok.x, self.color, skin=0)
            if king.save_position(pole, king.poz):
                all_moves.append(pozs[2])
            pole[prvok.y][prvok.x] = curr_enemy

        # pole[self.y][self.x] = curr
        return all_moves

    def update_figure(self, new_poz):
        """
            Updatne Pawn s novou poziciou, ak sa este pawn nepohol zaznamena to
        :param new_poz: nova pozicia Pawna
        """

        if abs(self.y - new_poz[0]):
            self.moved_byt_two = True
        self.y, self.x = new_poz[0], new_poz[1]
        self.moved = True
        self.map_of_moves_shadowed = self.attacking_pos()

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

    def king_checking_path(self, pole, s_pos):
        '''
            Vrati naspat cestu ktora vyhodi krala, co je iba policko figurky
        '''
        return [(self.y, self.x)]

    def king_elimination_path(self, pole, king_pos):
        for move in self.attacking_pos():
            if move == king_pos:
                return [(self.y, self.x)]
        return []


class King(Figure):
    def __init__(self, v_poz, h_poz, color, skin='', sliding='F'):
        super().__init__(v_poz, h_poz, color, skin)

        self.color = color

        self.name = color + 'K' + sliding

        self.create_skin()

        self.sliding = sliding

        self.map_of_moves_shadowed = self.possible_moves()

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
            Vrati mozne pohyby krala na zaklade pola + ked sa kral nepohol pozrie sa moze nastat castling
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
        if self.name[-1] == 'T' and self.save_position(pole, (self.y, self.x)):
            if (self.y, self.x + 1) in all_moves and self.save_position(pole, (self.y, self.x + 2)) and\
                    not pole[self.y][self.x + 2]:
                if pole[7][7] and pole[7][7].name == 'WRT' and self.color == 'W':
                    castle_moves.append((self.y, self.x + 2))
                elif pole[0][7] and pole[0][7].name == 'BRT' and self.color == 'B':
                    castle_moves.append((self.y, self.x + 2))
            elif (self.y, self.x - 1) in all_moves and self.save_position(pole, (self.y, self.x - 2)) and \
                    not pole[self.y][self.x - 2]:
                if pole[7][0] and pole[7][0].name == 'WRT' and self.color == 'W':
                    castle_moves.append((self.y, self.x - 2))
                elif pole[0][0] and pole[0][0].name == 'BRT' and self.color == 'B':
                    castle_moves.append((self.y, self.x - 2))

        return all_moves + castle_moves

    def update_figure(self, new_poz):
        """
            Updatne Krala s novou poziciou, ak sa este kral nepohol zaznamena to
        :param new_poz: nova pozicia Krala
        """
        super().update_figure(new_poz)
        if self.sliding == 'T':
            self.name = self.name[:2] + 'F'
            self.sliding = 'F'

    def check_king(self, pole, s_pos):
        '''
            Skontroluje ci Kral moze vyhodit krala, kral nikdy nemoze vyhodit krala
        '''
        return []

    def save_position(self, pole, pos):
        """
            Skontroluje ci je pozicia `pos` bezpecna pre Krala
        :param pole:
        :param pos:
        :return: True/False
        """
        for line in pole:
            for figure in line:
                if figure and figure == self.enemy:
                    if figure.check_king(pole, pos):
                        return False
        return True

    def king_checking_path(self, pole, s_pos):
        '''
            Vrati naspat cestu ktora vyhodi krala, kral nikdy nemoze vyhodit krala
        '''
        return []

    def king_elimination_path(self, pole, king_pos):
        return []

    def get_stats(self):
        return super().get_stats() + tuple(self.sliding)
