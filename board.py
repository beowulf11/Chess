import tkinter
import json
from figure import Queen, Rook, Bishop, Knight, Pawn, King
from random import randint, choice
import chess


class Board(tkinter.Frame):
    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.controller = controller
        self.canvas = tkinter.Canvas(self, width=700, height=700)
        self.canvas.pack()
        self.canvas_width = 700
        self.canvas_height = 700
        self.after_timer = 0
        self.dragging_enabled = False
        self.canvas.bind('<Escape>', self.esc_menu)
        self.canvas.bind("<Button-1>", self.on_press)
        self.end_game_message = ''
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<B1-Motion>", self.on_motion)
        self._drag_data = {'x': 0, 'y': 0, 'item': None}

        self.ai = True

        self.game = chess.Chess()

    def swap_frames(self, args=None):
        '''
            Vymeni frame hry za frame menu
        '''
        if self.end_game_message:
            self.canvas.delete(self.end_game_message[0])
            self.canvas.delete(self.end_game_message[1])
            del self.end_game_message
        self.controller.show_frames('Program')

    def set_up_game(self):
        '''
            Nastavi class na novu hru
        '''

        # Pokial hrac odklikol prec zo skoncenej hry tak treba zastavit casovac ktory prepina na menu
        if self.after_timer:
            self.canvas.after_cancel(self.after_timer)
        self.canvas.focus_set()

        with open('settings.txt', 'r') as file:
            settings = json.load(file)
            board_img = settings['background']
            self.hint_color = settings["hint"]

        self.canvas.delete('all')  # vymaze obrazky z predoslej hry
        self.board_img = tkinter.PhotoImage(file=f'Images/game_board_0{board_img}.png')

        self.selected_figure = 0
        self.possible_moves = []
        self.possible_moves_img = []
        self.background_id = self.canvas.create_image(self.board_img.width() // 2, self.board_img.height() // 2,
                                                      image=self.board_img)
        self.end_game_message = 0
        self.width_policka = 78.5
        self.posun_x = 35
        self.posun_y = 35
        self.choosing_menu = False
        self.choosing_fig = False
        self.next_turn = True
        self.turn_color = 1  # 0-cierny, 1-biely

        self.game.testing()
        self.create_figure_images()

    def game_loop(self, pozs):
        '''
            Pozre ci ma hrac vybratu figurku alebo si este jednu musi vybrat a podla vybery zavola funkcie
        :param pozs:
        '''
        if self.selected_figure:
            self.move_figure_human(self.selected_figure + pozs)

            if self.turn_color == 0 and self.ai:
                self.figure_move(self.game.ai_move())

        elif self.game.player_map[pozs[0]][pozs[1]]:  # figurka neni oznacena tak oznacime nejaku a vykreslime mozne pohyby
            self.select_figure(pozs[0], pozs[1])

    def select_figure(self, y, x):
        self.selected_figure = (y, x)
        self.possible_moves = self.game.generate_moves_for_human((y, x))
        # Pozriet ci sa nahodou nieco nevynechalo ale toto vsetko riesit v chess.py

        # if self.turn_color and self.selected_figure != King and self.king_w_elimation_positions:
        #     for x in self.selected_figure.allowed_moves(self.player_map):
        #         if x in self.saving_pos_w_king:
        #             self.possible_moves.append(x)
        # elif not self.turn_color and self.selected_figure != King and self.king_b_elimation_positions:
        #     for x in self.selected_figure.allowed_moves(self.player_map):
        #         if x in self.saving_pos_b_king:
        #             self.possible_moves.append(x)
        # elif self.selected_figure.name[1:] == 'KT':
        #     self.possible_moves = self.selected_figure.allowed_moves(
        #         self.player_map) + self.selected_figure.castling(self.player_map)
        # else:
        #     self.possible_moves = self.selected_figure.allowed_moves(self.player_map)
        self.draw_possible_moves(self.possible_moves)

    def moving_logic(self, pozs):
        if self.selected_figure.name[1:] == 'KT' and ''.join(str(x) for x in pozs) in self.selected_figure.castling(
                self.player_map):
            return 'kingSliding'
        else:
            return 'normal'

    def delete_possible_moves(self):
        '''
            Vymaze mozne pohybi
        '''

        for i in self.possible_moves_img:
            self.canvas.delete(i)

    def valid_click(self, pozs, turn_color=None):
        if self.selected_figure:
            return True
        if turn_color:
            if self.game.player_map[pozs[0]][pozs[1]] and self.game.player_map[pozs[0]][pozs[1]] == 'W':
                return True
            return False
        if turn_color == 0:
            if self.game.player_map[pozs[0]][pozs[1]] and self.game.player_map[pozs[0]][pozs[1]] == 'B':
                return True
            return False

    def on_release(self, args):
        # reset the drag information
        if self.dragging_enabled and self.selected_figure:
            pozs = self.get_location_from_pixels(args.x, args.y)
            self.selected_figure.x_p, self.selected_figure.y_p = self.canvas.coords(self._drag_data["item"])
            movement = self.moving_logic(pozs)
            if movement == 'kingSliding':
                self.king_sliding(self.selected_figure, pozs)
            elif movement == 'normal':
                if not self.figure_move(self.selected_figure, [str(i) for i in pozs]):
                    self.restore_location(self.selected_figure)
            self.selected_figure = 0
            self.delete_possible_moves()
            self._drag_data["item"] = None
            self._drag_data["x"] = 0
            self._drag_data["y"] = 0

    def on_motion(self, event):
        # compute how much the mouse has moved
        if self._drag_data["item"] != 1 and self.dragging_enabled and self.selected_figure:
            delta_x = event.x - self._drag_data["x"]
            delta_y = event.y - self._drag_data["y"]
            # move the object the appropriate amount
            self.canvas.move(self._drag_data["item"], delta_x, delta_y)
            # record the new position
            self._drag_data["x"] = event.x
            self._drag_data["y"] = event.y

    def on_press(self, args):
        '''
            Funkcia ktora sa zavola po kliknuti
        '''

        # Koniec hry
        if self.end_game_message:
            self.swap_frames()

        # Vyberanie figurky na Pawn Promotion
        elif self.choosing_fig:
            if 300 <= args.y <= 400:
                self.choosing_fig = False
                self.canvas.delete(self.select_figure_img[0])
                del (self.select_figure_img)
                for x in range(4):
                    if args.x in range(150 + 100 * x, 250 + 100 * x):
                        self.pawn_promotion(self.pawn_to_promote, [Queen, Rook, Bishop, Knight][x])
                self.next_turn = True

        # Vyber v menu (Continue, Save, Exit)
        elif self.choosing_menu:
            if 150 <= args.x <= 550 and 210 <= args.y <= 290:
                self.canvas.delete(self.select_menu[0])
                del self.select_menu
                self.choosing_menu = False
            elif 150 <= args.x <= 550 and 310 <= args.y <= 390:
                self.save()
            elif 150 <= args.x <= 550 and 410 <= args.y <= 490:
                self.swap_frames()

        # self.next_turn, Dovoli vybraniu dalsieho pohybu, zakaze ak je napr. program v animacii
        elif self.next_turn:
            pozs = self.get_location_from_pixels(args.x, args.y)
            # TODO: Spravit Klikanie aby fungovalo s chess.py
            if self.dragging_enabled:
                # Namiesto klikania sa taha
                if pozs:
                    if self.valid_click(pozs, self.turn_color):
                        self._drag_data["item"] = self.canvas.find_closest(args.x, args.y)[0]
                        self._drag_data["x"] = args.x
                        self._drag_data["y"] = args.y
                        if self._drag_data["item"] != 1:
                            self.select_figure(pozs[0], pozs[1])
                    elif self.valid_click(pozs, self.turn_color):
                        self._drag_data["item"] = self.canvas.find_closest(args.x, args.y)[0]
                        self._drag_data["x"] = args.x
                        self._drag_data["y"] = args.y
                        if self._drag_data["item"] != 1:
                            self.select_figure(pozs[0], pozs[1])
            else:
                if pozs:
                    self.delete_possible_moves()
                    if self.valid_click(pozs, self.turn_color):
                        self.game_loop(pozs)

    def get_location_from_pixels(self, m_x, m_y):
        '''
            Vrati poziciu na poli sachovnice z pixolovej pozicie
        '''
        for i in range(8):
            for j in range(8):
                if self.posun_x + j * self.width_policka <= m_x <= self.posun_x + j * self.width_policka + \
                        self.width_policka and self.posun_y + i * self.width_policka <= m_y <= self.posun_y + i * \
                        self.width_policka + self.width_policka:
                    return (i, j)
        return False

    def draw_possible_moves(self, zoz):
        '''
            Nakresli mozne pozicie pre pohyb na zaklade od par zoz a zaroven naplni zoznam possible_moves_img objektami
            ktore reprezentuju mozne pohybi
        '''
        self.possible_moves_img = []
        for i in zoz:
            s = self.get_pixels_middle_from_location(*i[2:])
            self.possible_moves_img.append(
                self.canvas.create_oval(s[1] - 10, s[0] - 10, s[1] + 10, s[0] + 10, fill=self.hint_color))

    def update_king_elimination_positions(self):
        '''
            Priradi kralom pozicie figurok ktore ich mozu vyhodit
        '''
        self.king_w_elimation_positions = self.get_king_elimination_positions('W')

        self.king_b_elimation_positions = self.get_king_elimination_positions('B')

    def get_king_elimination_positions(self, color):
        '''
            Vrati pozicie figurok ktore mozu vyhodit krala farby color
        '''
        temp = []
        if color == 'W':
            for j in self.player_map:
                for i in j:
                    if i and i == 'B':
                        el = i.check_king(self.player_map, (self.kings[1].y, self.kings[1].x))
                        if el:
                            temp.append(el)
        else:
            for j in self.player_map:
                for i in j:
                    if i and i == 'W':
                        el = i.check_king(self.player_map, (self.kings[0].y, self.kings[0].x))
                        if el:
                            temp.append(el)
        return temp

    def get_pixels_middle_from_location(self, y, x):
        '''
            Vrati stredne pixelove pozicie policka na pozici l_l
        '''

        return (self.posun_y + y * self.width_policka + self.width_policka // 2,
                self.posun_x + x * self.width_policka + self.width_policka // 2)

    def move_figure_to(self, fig=0, pix_x=0, pix_y=0):
        '''
            Animuje pohyb a zaroven na konci animacie dovoli priebehu dalsieho kola
        '''

        if fig.x_p != pix_x or fig.y_p != pix_y:
            if fig.x_p != pix_x:
                if fig.x_p > pix_x:
                    fig.x_p -= 0.5
                else:
                    fig.x_p += 0.5
            if fig.y_p != pix_y:
                if fig.y_p > pix_y:
                    fig.y_p -= 0.5
                else:
                    fig.y_p += 0.5
            self.canvas.coords(fig.image_id, fig.x_p, fig.y_p)
            # dokoncenie animacie povolenie dalsieho pohybu
            self.canvas.after(1, self.move_figure_to, fig, pix_x, pix_y)
        # elif fig.x_p == pix_x or fig.y_p == pix_y:
        #     self.en_passant_elimination()
        #     if not self.end_of_round():
        #         self.update_king_elimination_positions()
        #         end_game = self.checking_for_game_end()
        #         if end_game == 'white_lost':
        #             self.finished_game('Biely')
        #         elif end_game == 'black_lost':
        #             self.finished_game('Cierny')
        #         elif end_game == 'remiza':
        #             self.finished_game('Remiza')
            self.next_turn = True  # Zacina dalsie kolo

    def finished_game(self, looser):
        self.end_game_message = [self.canvas.create_rectangle(100, 300, 610, 400, fill='white'),
                                 self.canvas.create_text(350, 350, font=("Arial", 50),
                                                         text=f'{looser} prehrali')]
        self.after_timer = self.canvas.after(7000, self.swap_frames)

    def move_figure_human(self, movement):
        if movement in self.possible_moves:
            self.figure_move(movement)
            return True
        self.selected_figure, self.possible_moves = 0, 0
        return False

    def figure_move(self, movement):
        '''
            Zisiti ci sa figurka moze pohnut a ak ano tak zavola funkciu na pohyb a pripravi hru na dalsie kolo
        '''

        move = (movement[0], movement[1], movement[2], movement[3])
        figure_movement = self.game.move_figure(self.game.player_map, move)
        for move in figure_movement:
            figure = self.game.player_map[move[2]][move[3]]
            pix_y, pix_x = self.get_pixels_middle_from_location(move[2], move[3])
            self.move_figure_to(figure, pix_x, pix_y)
        self.figure_move_next_round(movement, movement) # wtf?
        self.selected_figure, self.possible_moves = 0, 0

    def figure_move_next_round(self, fig, new_pos):
        '''
            Pripravi hru na dalsie kolo
        '''
        self.next_turn = False  # Zacina animacia, zakaz dalsieho pohybu az do skoncenia animacie
        self.turn_color = abs(self.turn_color - 1)

    def restore_location(self, fig):
        self.next_turn = False
        pix_y, pix_x = self.get_pixels_middle_from_location(fig.y, fig.x)
        self.move_figure_to(fig, pix_x, pix_y)

    def saving_pos(self, attaking_pos):
        '''
            Vrati pozicie na ktore ked sa dostane figurka zachrani krala
        '''
        if len(attaking_pos) > 1:
            return []
        if attaking_pos:
            return attaking_pos[0]

    def can_move_a_figure(self, color):
        '''
            Funkcia zisti ci hrac farby color ma figurku z ktorou moze pohnut ak nema vrati funkcia False == je remiza
        :param color:
        :return:
        '''
        for i in self.player_map:
            for j in i:
                if j and j == color:
                    if j.allowed_moves(self.player_map):
                        return True
        return False

    def end_of_round(self):
        '''
            Funkcia sa zavola na konci kola a skontroluje ci su nejaky Pawns ktore sa pohli o 2 policka predosle kolo
            aby im mohlo zrusit moznost vyhodenia pomocou en passant. A pozrie sa ci sa Pawn nedostal cez celu
            sachovnicu a hrac si moze zvolit naco sa zmeni
        '''
        if self.pawn_en_pasant:
            self.pawn_en_pasant.name = self.pawn_en_pasant.name[:2] + 'F'
            self.pawn_en_pasant = 0

        for i in self.player_map:
            for j in i:
                if j and j.name[1:] == 'PT':
                    self.pawn_en_pasant = j
        return self.pawn_for_promotion()

    def checking_for_game_end(self):
        '''
            Funkcia skontroluje stav hry a pokial je Vyhra/Remiza ukonci hru s oznamenim
        '''
        if self.king_w_elimation_positions:
            sav_pos = self.saving_pos(self.king_w_elimation_positions)
            if sav_pos:
                self.saving_pos_w_king = self.player_map[int(sav_pos[0][0])][int(sav_pos[0][1])].king_checking_path(
                    self.player_map, self.kings[1].poz)
                self.can_be_moved_to('W', self.saving_pos_w_king)
                if not self.can_be_moved_to('W', self.saving_pos_w_king) and not self.kings[1].allowed_moves(
                        self.player_map):
                    return 'white_lost'
            elif not self.kings[1].allowed_moves(self.player_map):
                return 'white_lost'

        elif self.king_b_elimation_positions:
            sav_pos = self.saving_pos(self.king_b_elimation_positions)
            if sav_pos:
                self.saving_pos_b_king = self.player_map[int(sav_pos[0][0])][int(sav_pos[0][1])].king_checking_path(
                    self.player_map, self.kings[0].poz)
                if not self.can_be_moved_to('B', self.saving_pos_b_king) and not self.kings[0].allowed_moves(
                        self.player_map):
                    return 'black_lost'
            elif not self.kings[0].allowed_moves(self.player_map):
                return 'black_lost'

        elif not self.can_move_a_figure('W') or not self.can_move_a_figure('B'):
            return 'remiza'

    def pawn_promotion(self, pawn_promoted, promoted_to):
        '''
            Ked je nejaky panak ktory by mal byt premeneni na Queen tak ho premeni
        :param pawn_promoted:
        :return:
        '''
        px, py = int(pawn_promoted.poz[0]), int(pawn_promoted.poz[1])
        self.canvas.delete(pawn_promoted.image_id)
        self.player_map[px][py] = 0
        with open('settings.txt', 'r') as file:
            skin = json.load(file)['figures']
        self.player_map[px][py] = promoted_to(px, py, pawn_promoted.name[0], skin=skin)
        pawn_promoted = 0
        y, x = self.get_pixels_middle_from_location(self.player_map[px][py].poz)
        self.player_map[px][py].x_p, self.player_map[px][py].y_p = x, y
        self.player_map[px][py].image_id = self.canvas.create_image(
            self.get_pixels_middle_from_location(self.player_map[px][py].y, self.player_map[px][py].x),
            image=self.player_map[px][py].image)

    def can_be_moved_to(self, current_player, s_poz):
        '''

        :param current_player: Farba hraca ktoreho figurka sa budu skusat ci sa moze dostat na poz
        :param poz: Pozicia na ktore sa budu figurky snazit dostat
        '''
        for i in self.player_map:
            for j in i:
                if j and j == current_player:
                    if j.name[1] in 'QBR':
                        for poz in j.allowed_moves(self.player_map):
                            if poz in s_poz:
                                return True
                    else:
                        for poz in j.allowed_moves(self.player_map):
                            if poz in s_poz:
                                return True
        return False

    def choosing_figure(self, color, pawn):
        '''
            Zastavi hru a vytvori obrazovku na ktorej si je schopny hrac vybrat na aku postavicku sa zmeni Pawn
        '''
        self.pawn_to_promote = pawn
        self.choosing_fig = True
        with open('settings.txt', 'r') as file:
            skin = json.load(file)['figures']
        self.select_figure_img = [self.canvas.create_rectangle(150, 300, 550, 400, fill='white'),
                                  tkinter.PhotoImage(file='Images/q{}{}.png'.format(color, skin)),
                                  tkinter.PhotoImage(file='Images/r{}{}.png'.format(color, skin)),
                                  tkinter.PhotoImage(file='Images/b{}{}.png'.format(color, skin)),
                                  tkinter.PhotoImage(file='Images/k{}{}.png'.format(color, skin))]
        for k, i in enumerate(self.select_figure_img[1:]):
            self.canvas.create_image(100 * k + 200, 350, image=i)

    def esc_menu(self, args):
        '''
            Zastavi hru a vytvori obrazovku na ktorej sa hrac mozes rozhudnut pre: continue, save, exit
        '''
        if not self.choosing_fig and not self.end_game_message:
            if self.choosing_menu:
                self.canvas.delete(self.select_menu[0])
                del (self.select_menu)
                self.choosing_menu = False
            else:
                self.choosing_menu = True
                self.select_menu = [self.canvas.create_rectangle(100, 150, 600, 550, fill='white', width=2),
                                    tkinter.PhotoImage(file='Images/button_continue.png'),
                                    tkinter.PhotoImage(file='Images/button_save.png'),
                                    tkinter.PhotoImage(file='Images/button_exit.png')]
                for k, i in enumerate(self.select_menu[1:]):
                    self.canvas.create_image(350, 100 * (k + 1) + 150, image=i)

    def save(self):
        '''
            Ulozi konkretny stav hry do suboru game_save_normal a vypise notifikaciu o uspechu/neuspechu
        '''
        try:
            with open('game_save.txt', 'w') as file:
                file.write(str(self.turn_color) + '\n')
                for k in self.player_map:
                    for i in k:
                        if i:
                            if i.name[1] == 'P':
                                file.write(str(i)[:2] + str(i.moves)[0] + ' ' + i.poz + '\n')
                            else:
                                file.write(str(i) + ' ' + i.poz + '\n')
            self.save_nottif = []
            self.save_nottif.append(self.canvas.create_rectangle(250, 570, 450, 670, fill='white', width=2))
            self.save_nottif.append(self.canvas.create_text(350, 620, text='Saved', font=("Arial", 35)))
            self.canvas.after(1000, self.destroy_items, self.save_nottif)
        except:
            self.save_nottif = []
            self.save_nottif.append(self.canvas.create_rectangle(250, 570, 450, 670, fill='white', width=2))
            self.save_nottif.append(self.canvas.create_text(350, 620, text='Failed', font=("Arial", 35)))
            self.canvas.after(1000, self.destroy_items, self.save_nottif)

    def destroy_items(self, items):
        for i in items:
            self.canvas.delete(i)

    def load(self, args=0):
        try:
            with open('settings.txt', 'r') as file:
                json_file = json.load(file)
                skin = json_file['figures']
                if json_file['dragging'] == 'True':
                    self.dragging_enabled = True
                else:
                    self.dragging_enabled = False
            subor = open('game_save.txt', 'r')
            for i in range(8):
                for j in range(8):
                    self.player_map[i][j] = 0
            self.kings = [0, 0]
            self.turn_color = int(subor.readline())
            l = subor.readline()[:-1]
            while l:
                fig, poz = l.split()
                figure_c = self.figure_acronym(fig[1])
                if figure_c == King:
                    if fig[0] == 'B':
                        self.kings[0] = figure_c(poz[0], poz[1], fig[0], fig[2], skin)
                        self.player_map[int(poz[0])][int(poz[1])] = self.kings[0]
                    else:
                        self.kings[1] = figure_c(poz[0], poz[1], fig[0], fig[2], skin)
                        self.player_map[int(poz[0])][int(poz[1])] = self.kings[1]
                elif figure_c == Pawn or figure_c == Rook:
                    self.player_map[int(poz[0])][int(poz[1])] = figure_c(poz[0], poz[1], fig[0], fig[2], skin)
                else:
                    self.player_map[int(poz[0])][int(poz[1])] = figure_c(poz[0], poz[1], fig[0], skin)
                l = subor.readline()[:-1]
            subor.close()
            self.create_figure_images()
        except:
            self.swap_frames()

    def figure_acronym(self, acr):
        '''
            Vrati class Figurky podla stringu acronym
        '''
        return {'K': King, 'B': Bishop, 'N': Knight, 'P': Pawn, 'R': Rook, 'Q': Queen}.get(acr, 0)

    def random_positions_mirror(self):
        '''
            Hra v mode nahodne figurky ktore su zrkadlovo otocene pre druheho hraca
        '''
        self.player_map = [[0 for _ in range(8)] for _ in range(8)]
        with open('settings.txt', 'r') as file:
            json_file = json.load(file)
            skin = json_file['figures']
            if json_file['dragging'] == 'True':
                self.dragging_enabled = True
            else:
                self.dragging_enabled = False
        figures = [Queen, Rook, Rook, Bishop, Bishop, Knight, Knight, Pawn, Pawn, Pawn, Pawn, Pawn, Pawn, Pawn, Pawn]
        x = randint(0, 7)
        self.kings = [King(0, x, 'B', 'F', skin), King(7, abs(7 - x), 'W', 'F', skin)]
        for i in range(2):
            for j in range(8):
                if i == 0 and j == x:
                    continue
                fig = figures[randint(0, len(figures) - 1)]
                if fig == Pawn:
                    self.player_map[i][j] = fig(i, j, 'B', 'T', skin)
                    self.player_map[7 - i][abs(7 - j)] = fig(7 - i, abs(7 - j), 'W', 'T', skin)
                elif fig == Rook:
                    self.player_map[i][j] = fig(i, j, 'B', 'F', skin)
                    self.player_map[7 - i][abs(7 - j)] = fig(7 - i, abs(7 - j), 'W', 'F', skin)
                else:
                    self.player_map[i][j] = fig(i, j, 'B', skin)
                    self.player_map[7 - i][abs(7 - j)] = fig(7 - i, abs(7 - j), 'W', skin)
        self.player_map[0][x] = self.kings[0]
        self.player_map[7][abs(7 - x)] = self.kings[1]
        self.create_figure_images()
        self.update_king_elimination_positions()

    def random_positions_normal(self):
        '''
            Hra v mode random normal kde sa figurky z klasickeho sachu nahodne rozlozia
        '''
        self.player_map = [[0 for _ in range(8)] for _ in range(8)]
        with open('settings.txt', 'r') as file:
            json_file = json.load(file)
            skin = json_file['figures']
            if json_file['dragging'] == 'True':
                self.dragging_enabled = True
            else:
                self.dragging_enabled = False
        figures = [Queen, Rook, Rook, Bishop, Bishop, Knight, Knight, Pawn, Pawn, Pawn, Pawn, Pawn, Pawn, Pawn, Pawn]
        x = randint(0, 7)
        self.kings = [King(0, x, 'B', 'F', skin), King(7, x, 'W', 'F', skin)]
        for i in range(2):
            for j in range(8):
                if i == 0 and j == x:
                    continue
                fig = figures.pop(randint(0, len(figures) - 1))
                if fig == Pawn:
                    self.player_map[i][j] = fig(i, j, 'B', 'T', skin)
                    self.player_map[7 - i][j] = fig(7 - i, j, 'W', 'T', skin)
                elif fig == Rook:
                    self.player_map[i][j] = fig(i, j, 'B', 'F', skin)
                    self.player_map[7 - i][j] = fig(7 - i, j, 'W', 'F', skin)
                else:
                    self.player_map[i][j] = fig(i, j, 'B', skin)
                    self.player_map[7 - i][j] = fig(7 - i, j, 'W', skin)
        self.player_map[0][x] = self.kings[0]
        self.player_map[7][x] = self.kings[1]
        self.create_figure_images()
        self.update_king_elimination_positions()

    def random_positions_chaos(self):
        '''
            Hra v mode chaos kde sa pre kazdeho hraca nahodne vygeneruju figurky
        '''

        def random_pos():
            figures = [Queen, Rook, Bishop, Knight, Pawn]
            x = randint(0, 7)
            y = randint(0, 1)
            self.kings = [King(y, x, 'B', 'F', skin)]
            self.player_map[y][x] = self.kings[0]
            for i in range(2):
                for j in range(8):
                    if i == y and j == x:
                        continue
                    fig = figures[randint(0, len(figures) - 1)]
                    if fig == Pawn:
                        self.player_map[i][j] = fig(i, j, 'B', 'T', skin)
                    elif fig == Rook:
                        self.player_map[i][j] = fig(i, j, 'B', 'F', skin)
                    else:
                        self.player_map[i][j] = fig(i, j, 'B', skin)

            x = randint(0, 7)
            y = randint(0, 1)
            self.kings.append(King(7 - y, x, 'W', 'F', skin))
            self.player_map[7 - y][x] = self.kings[1]
            for i in range(2):
                for j in range(8):
                    if i == y and j == x:
                        continue
                    fig = figures[randint(0, len(figures) - 1)]
                    if fig == Pawn:
                        self.player_map[7 - i][j] = fig(7 - i, j, 'W', 'T', skin)
                    elif fig == Rook:
                        self.player_map[7 - i][j] = fig(7 - i, j, 'W', 'F', skin)
                    else:
                        self.player_map[7 - i][j] = fig(7 - i, j, 'W', skin)
            self.update_king_elimination_positions()

        self.player_map = [[0 for _ in range(8)] for _ in range(8)]
        with open('settings.txt', 'r') as file:
            json_file = json.load(file)
            skin = json_file['figures']
            if json_file['dragging'] == 'True':
                self.dragging_enabled = True
            else:
                self.dragging_enabled = False
        random_pos()
        while self.checking_for_game_end():
            random_pos()
        if self.king_w_elimation_positions:
            sav_pos = self.saving_pos(self.king_w_elimation_positions)
            if sav_pos:
                self.saving_pos_w_king = self.player_map[int(sav_pos[0][0])][int(sav_pos[0][1])].king_checking_path(
                    self.player_map, self.kings[1].poz)
        if self.king_b_elimation_positions:
            sav_pos = self.saving_pos(self.king_b_elimation_positions)
            if sav_pos:
                self.saving_pos_b_king = self.player_map[int(sav_pos[0][0])][int(sav_pos[0][1])].king_checking_path(
                    self.player_map, self.kings[0].poz)
        self.create_figure_images()

    def normal_positions(self):
        '''
            Hra v mode klasicky sach
        '''
        self.player_map = [[0 for _ in range(8)] for _ in range(8)]
        with open('settings.txt', 'r') as file:
            json_file = json.load(file)
            skin = json_file['figures']
            if json_file['dragging'] == 'True':
                self.dragging_enabled = True
            else:
                self.dragging_enabled = False
        self.kings = [King(0, 4, 'B', skin, 'T'), King(7, 4, 'W', skin, 'T')]
        self.player_map = [
            [Rook(0, 0, 'B', skin, 'T'), Knight(0, 1, 'B', skin), Bishop(0, 2, 'B', skin), Queen(0, 3, 'B', skin),
             self.kings[0],
             Bishop(0, 5, 'B', skin), Knight(0, 6, 'B', skin), Rook(0, 7, 'B', skin, 'T')],
            [Pawn(1, 0, 'B', 'F', skin), Pawn(1, 1, 'B', 'F', skin), Pawn(1, 2, 'B', 'F', skin),
             Pawn(1, 3, 'B', 'F', skin),
             Pawn(1, 4, 'B', 'F', skin), Pawn(1, 5, 'B', 'F', skin), Pawn(1, 6, 'B', 'F', skin),
             Pawn(1, 7, 'B', 'F', skin)],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [Pawn(6, 0, 'W', 'F', skin), Pawn(6, 1, 'W', 'F', skin), Pawn(6, 2, 'W', 'F', skin),
             Pawn(6, 3, 'W', 'F', skin),
             Pawn(6, 4, 'W', 'F', skin), Pawn(6, 5, 'W', 'F', skin), Pawn(6, 6, 'W', 'F', skin),
             Pawn(6, 7, 'W', 'F', skin)],
            [Rook(7, 0, 'W', 'T', skin), Knight(7, 1, 'W', skin), Bishop(7, 2, 'W', skin), Queen(7, 3, 'W', skin),
             self.kings[1],
             Bishop(7, 5, 'W', skin), Knight(7, 6, 'W', skin), Rook(7, 7, 'W', 'T', skin)]]
        self.update_king_elimination_positions()  # priradi polu polia figurok ktore mozu vyhodit krala
        self.create_figure_images()

    def create_figure_images(self):
        '''
            Priradi postavickam pixelove hodnoty na ktorych sa nachadzaju, id obrazka a vytvori obrazky figurok
        '''
        for i in range(8):
            for j in range(8):
                if self.game.player_map[i][j]:
                    y, x = self.get_pixels_middle_from_location(self.game.player_map[i][j].y,
                                                                self.game.player_map[i][j].x)
                    self.game.player_map[i][j].x_p, self.game.player_map[i][j].y_p = x, y
                    self.game.player_map[i][j].image_id = self.canvas.create_image((x, y),
                                                                                   image=self.game.player_map[i][
                                                                                       j].image)
