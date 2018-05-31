import tkinter
import json
from figure import Queen, Rook, Bishop, Knight, Pawn, King
from random import randint, choice
from time import sleep
import chess
import threading


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
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<B1-Motion>", self.on_motion)
        self._drag_data = {'x': 0, 'y': 0, 'item': None}

        self.end_game_message = ''
        self.width_policka = 78.5
        self.posun_x = 35
        self.posun_y = 35
        self.ai = True

    def swap_frames(self, args=None):
        '''
            Vymeni frame hry za frame menu
        '''
        if self.end_game_message:
            self.canvas.delete(self.end_game_message[0])
            self.canvas.delete(self.end_game_message[1])
            del self.end_game_message
        self.controller.show_frames('Program')

    def set_up_game(self, mode='n'):
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
            if settings["ai"] == "False":
                self.ai = False
            else:
                self.ai = True
            if settings['dragging'] == 'True':
                self.dragging_enabled = True
            else:
                self.dragging_enabled = False

        self.canvas.delete('all')  # vymaze obrazky z predoslej hry
        self.board_img = tkinter.PhotoImage(file=f'Images/game_board_0{board_img}.png')

        self.selected_figure = 0
        self.possible_moves = []
        self.possible_moves_img = []
        self.background_id = self.canvas.create_image(self.board_img.width() // 2, self.board_img.height() // 2,
                                                      image=self.board_img)
        self.end_game_message = 0
        self.choosing_menu = False
        self.choosing_fig = False
        self.turn_color = 1  # 0-cierny, 1-biely

        self.game = chess.Chess(self.ai, self.canvas, mode)

        self.create_figure_images()

    def game_loop(self, pozs):
        '''
            Pozre ci ma hrac vybratu figurku alebo si este jednu musi vybrat a podla vybery zavola funkcie
        :param pozs:
        '''
        if self.selected_figure:
            self.move_figure_human(self.selected_figure + pozs)

        elif self.game.player_map[pozs[0]][pozs[1]]:  # figurka neni oznacena tak oznacime nejaku a vykreslime mozne pohyby
            self.select_figure(pozs[0], pozs[1])

    def select_figure(self, y, x):
        self.selected_figure = (y, x)
        self.possible_moves = self.game.generate_moves_for_human((y, x))
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
            self.delete_possible_moves()
            if not self.move_figure_human(self.selected_figure + pozs):
                self.restore_location(self._drag_data["item"])
            self.selected_figure = 0
            self._drag_data["item"] = None
            self._drag_data["x"] = 0
            self._drag_data["y"] = 0

    def on_motion(self, event):
        # compute how much the mouse has moved
        if isinstance(self._drag_data["item"], (Queen, Rook, Bishop, Knight, Pawn, King)) and self.dragging_enabled and self.selected_figure:
            delta_x = event.x - self._drag_data["x"]
            delta_y = event.y - self._drag_data["y"]
            # move the object the appropriate amount
            self.canvas.move(self._drag_data["item"].image_id, delta_x, delta_y)
            # record the new position
            self._drag_data["item"].x_p = event.x
            self._drag_data["item"].y_p = event.y
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
                        self.game.pawn_promotion([Queen, Rook, Bishop, Knight][x])
                        self.pawn_promotion()
                        self.end_game()

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

        else :
            pozs = self.get_location_from_pixels(args.x, args.y)
            # TODO: Spravit Klikanie aby fungovalo s chess.py
            if self.dragging_enabled:
                # Namiesto klikania sa taha
                if pozs:
                    if self.valid_click(pozs, self.turn_color):
                        poz = self.get_location_from_pixels(args.x, args.y)
                        self._drag_data["item"] = self.game.player_map[poz[0]][poz[1]]
                        self._drag_data["x"] = args.x
                        self._drag_data["y"] = args.y
                        if isinstance(self._drag_data["item"], (Queen, Rook, Bishop, Knight, Pawn, King)):
                            self.select_figure(poz[0], poz[1])
                    elif self.valid_click(pozs, self.turn_color):
                        poz = self.get_location_from_pixels(args.x, args.y)
                        self._drag_data["item"] = self.game.player_map[poz[0]][poz[1]]
                        self._drag_data["x"] = args.x
                        self._drag_data["y"] = args.y
                        if isinstance(self._drag_data["item"], (Queen, Rook, Bishop, Knight, Pawn, King)):
                            self.select_figure(poz[0], poz[1])
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

    def get_pixels_middle_from_location(self, y, x):
        '''
            Vrati stredne pixelove pozicie policka na pozici l_l
        '''

        return (self.posun_y + y * self.width_policka + self.width_policka // 2,
                self.posun_x + x * self.width_policka + self.width_policka // 2)

    def move_figure_human(self, movement):
        if movement in self.possible_moves:
            self.figure_move(movement)
            return True
        self.selected_figure, self.possible_moves = 0, 0
        return False

    def end_game(self):
        answer = self.game.end_round_update()
        if answer == Pawn:
            self.choosing_figure(answer)
        elif answer in {'black', 'white'}:
            self.finished_game(answer)
        elif answer == 'stailmate':
            self.finished_game(answer)
        else:
            self.turn_color = abs(self.turn_color - 1)
            if self.turn_color == 0 and self.ai:
                f_m = self.game.ai_move(3)
                self.create_figure_images()
                self.game.player_map[f_m[0]][f_m[1]].y_p, self.game.player_map[f_m[0]][f_m[1]].x_p = self.get_pixels_middle_from_location(*f_m[:2])
                self.figure_move(f_m)

    def figure_move(self, movement):
        '''
            Zisiti ci sa figurka moze pohnut a ak ano tak zavola funkciu na pohyb a pripravi hru na dalsie kolo
        '''
        move = (movement[0], movement[1], movement[2], movement[3])
        figure_movement = self.game.move_figure(move)
        for move in figure_movement:
            figure = self.game.player_map[move[2]][move[3]]
            pix_y, pix_x = self.get_pixels_middle_from_location(move[2], move[3])
            print("Moving figure...")
            self.move_figure_to(figure, pix_x, pix_y)

        self.selected_figure, self.possible_moves = 0, 0
        self.end_game()

    def move_figure_to(self, fig=0, pix_x=0, pix_y=0, speed=1):
        '''
            Animuje pohyb a zaroven na konci animacie dovoli priebehu dalsieho kola
        '''
        while fig.x_p != pix_x or fig.y_p != pix_y:
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
            self.canvas.update()
            sleep(0.001/speed)
            # self.canvas.after(1, self.move_figure_to, fig, pix_x, pix_y)

    def finished_game(self, looser):
        self.end_game_message = [self.canvas.create_rectangle(100, 300, 610, 400, fill='white'),
                                 self.canvas.create_text(350, 350, font=("Arial", 50),
                                                         text=f'{looser} prehrali')]

    def restore_location(self, fig):
        pix_y, pix_x = self.get_pixels_middle_from_location(fig.y, fig.x)
        self.move_figure_to(fig, pix_x, pix_y, 10)

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

    def pawn_promotion(self):
        '''
            Vytvori obrazok a nastavi poziciu pre figurku ktora bola vymenena za Pawn ktory bol promotnuti
        :param pawn_promoted:
        :return:
        '''
        self.canvas.delete(self.pawn_to_promote.image_id)
        self.create_figure_images()
        self.pawn_to_promote = None

    def can_be_moved_to(self, current_player, s_poz):
        '''

        :param current_player: Farba hraca ktoreho figurka sa budu skusat ci sa moze dostat na poz
        :param poz: Pozicia na ktore sa budu figurky snazit dostat
        '''
        for i in self.player_map:
            for j in i:
                if j == current_player:
                    if j.name[1] in 'QBR':
                        for poz in j.allowed_moves(self.player_map):
                            if poz in s_poz:
                                return True
                    else:
                        for poz in j.allowed_moves(self.player_map):
                            if poz in s_poz:
                                return True
        return False

    def choosing_figure(self, pawn):
        '''
            Zastavi hru a vytvori obrazovku na ktorej si je schopny hrac vybrat na aku postavicku sa zmeni Pawn
        '''
        self.pawn_to_promote = pawn
        color = pawn.color
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
                file.write(self.game.mode + '\n')
                for k in self.game.player_map:
                    for i in k:
                        if i:
                            stats = i.get_stats_save()
                            file.write(str(i)[1] + ' ')
                            for stat in stats:
                                file.write(str(stat) + ' ')
                            file.write('\n')
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
        '''
            Odstany graficke objekty z canvas
        :param items: objekty ktore sa maju odstranit
        :return:
        '''
        for i in items:
            self.canvas.delete(i)

    def load(self, args=0):
        '''
            Nacita hru zo suboru game_save.txt
        :param args:
        :return:
        '''
        def convert_stats(stats, skin):
            '''
                Upravi statistiky a prida skin do nich
            :param stats: Premeni string pole na spravne premenne pre stats figurky
            :param skin: Skin ktory sa ma pridat do statistik
            :return:
            '''
            conv_stats = []
            skin_inserted = False
            for stat in stats:
                if stat == 'False':
                    if not skin_inserted:
                        conv_stats.append(skin)
                        skin_inserted = True
                    conv_stats.append(False)
                elif stat == 'True':
                    if not skin_inserted:
                        conv_stats.append(skin)
                        skin_inserted = True
                    conv_stats.append(True)
                elif stat != 'B' and stat != 'W':
                    conv_stats.append(int(stat))
                else:
                    conv_stats.append(stat)
            return conv_stats

        try:
            print("Loading...")
            with open('settings.txt', 'r') as file:
                json_file = json.load(file)
                skin = json_file['figures']
                if json_file['dragging'] == 'True':
                    self.dragging_enabled = True
                else:
                    self.dragging_enabled = False
            with open('game_save.txt', 'r') as subor:
                for i in range(8):
                    for j in range(8):
                        self.game.player_map[i][j] = 0
                self.turn_color = int(subor.readline())
                if self.ai:
                    self.turn_color = 1
                self.game.mode = subor.readline()[:-1]
                l = subor.readline()[:-1]
                while l:
                    fig, *stats = l.split()
                    stats = convert_stats(stats, skin)
                    self.game.player_map[stats[0]][stats[1]] = self.figure_acronym(fig)(*stats)
                    l = subor.readline()[:-1]
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
        print("Generating positions...")
        self.player_map = [[0 for _ in range(8)] for _ in range(8)]
        with open('settings.txt', 'r') as file:
            json_file = json.load(file)
            skin = json_file['figures']

        figures = [Queen, Rook, Rook, Bishop, Bishop, Knight, Knight, Pawn, Pawn, Pawn, Pawn, Pawn, Pawn, Pawn, Pawn]
        x = randint(0, 7)
        self.game.player_map[0][x] = King(0, x, 'B', skin, True)
        self.game.player_map[7][abs(7 - x)] = King(7, abs(7 - x), 'W', skin, True)
        for i in range(2):
            for j in range(8):
                if self.game.player_map[i][j]:
                    continue
                fig = figures[randint(0, len(figures) - 1)]
                if fig == Pawn or fig == Rook:
                    self.game.player_map[i][j] = fig(i, j, 'B', skin, True)
                    self.game.player_map[7 - i][abs(7 - j)] = fig(7 - i, abs(7 - j), 'W', skin, True)
                else:
                    self.game.player_map[i][j] = fig(i, j, 'B', skin)
                    self.game.player_map[7 - i][abs(7 - j)] = fig(7 - i, abs(7 - j), 'W', skin)
        self.create_figure_images()

    def random_positions_normal(self):
        '''
            Hra v mode random normal kde sa figurky z klasickeho sachu nahodne rozlozia
        '''
        print("Generating positions...")
        self.player_map = [[0 for _ in range(8)] for _ in range(8)]
        with open('settings.txt', 'r') as file:
            json_file = json.load(file)
            skin = json_file['figures']

        figures_w = [Queen, Rook, Rook, Bishop, Bishop, Knight, Knight, Pawn, Pawn, Pawn, Pawn, Pawn, Pawn, Pawn, Pawn]
        figures_b = [Queen, Rook, Rook, Bishop, Bishop, Knight, Knight, Pawn, Pawn, Pawn, Pawn, Pawn, Pawn, Pawn, Pawn]
        x = randint(0, 7)
        self.game.player_map[0][x] = King(0, x, 'B', skin, False)
        x = randint(0, 7)
        self.game.player_map[7][x] = King(7, x, 'W', skin, False)
        for i in range(2):
            for j in range(8):
                if self.game.player_map[i][j]:
                    continue
                fig = figures_w.pop(randint(0, len(figures_w) - 1))
                if fig == Pawn or fig == Rook:
                    self.game.player_map[i][j] = fig(i, j, 'B', skin, True)
                else:
                    self.game.player_map[i][j] = fig(i, j, 'B', skin)
        for i in range(6, 8):
            for j in range(8):
                if self.game.player_map[i][j]:
                    continue
                fig = figures_b.pop(randint(0, len(figures_b) - 1))
                if fig == Pawn or fig == Rook:
                    self.game.player_map[i][j] = fig(i, j, 'W', skin, True)
                else:
                    self.game.player_map[i][j] = fig(i, j, 'W', skin)
        self.create_figure_images()

    def random_positions_chaos(self):
        '''
            Hra v mode chaos kde sa pre kazdeho hraca nahodne vygeneruju figurky
        '''

        def random_pos():
            figures = [Queen, Rook, Bishop, Knight, Pawn]
            x = randint(0, 7)
            y = randint(0, 1)
            self.game.player_map[y][x] = King(y, x, 'B', skin, True)
            for i in range(2):
                for j in range(8):
                    if i == y and j == x:
                        continue
                    fig = figures[randint(0, len(figures) - 1)]
                    if fig == Pawn  or fig == Rook:
                        self.game.player_map[i][j] = fig(i, j, 'B', skin, True)
                    else:
                        self.game.player_map[i][j] = fig(i, j, 'B', skin)

            x = randint(0, 7)
            y = randint(0, 1)
            self.game.player_map[7 - y][x] = King(7 - y, x, 'W', skin, False)
            for i in range(2):
                for j in range(8):
                    if i == y and j == x:
                        continue
                    fig = figures[randint(0, len(figures) - 1)]
                    if fig == Pawn or fig == Rook:
                        self.game.player_map[7 - i][j] = fig(7 - i, j, 'W', skin, True)
                    else:
                        self.game.player_map[7 - i][j] = fig(7 - i, j, 'W', skin)

        print("Generating positions...")
        self.game.player_map = [[0 for _ in range(8)] for _ in range(8)]
        with open('settings.txt', 'r') as file:
            json_file = json.load(file)
            skin = json_file['figures']

        random_pos()
        while not self.game.generate_moves(self.game.player_map, color='W') or not self.game.generate_moves(self.game.player_map, color='B'):
            random_pos()
        self.create_figure_images()

    def normal_positions(self):
        '''
            Hra v mode klasicky sach
        '''
        print("Preparing board...")
        self.player_map = [[0 for _ in range(8)] for _ in range(8)]
        with open('settings.txt', 'r') as file:
            json_file = json.load(file)
            skin = json_file['figures']

        self.game.player_map = [
            [Rook(0, 0, 'B', skin, False), Knight(0, 1, 'B', skin), Bishop(0, 2, 'B', skin), Queen(0, 3, 'B', skin),
             King(0, 4, 'B', skin, False),
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
             King(7, 4, 'W', skin, False),
             Bishop(7, 5, 'W', skin), Knight(7, 6, 'W', skin), Rook(7, 7, 'W', skin, False)]]

        self.create_figure_images()

    def create_figure_images(self):
        '''
            Priradi postavickam pixelove hodnoty na ktorych sa nachadzaju, id obrazka a vytvori obrazky figurok
        '''
        skin = 0
        for line in self.game.player_map:
            for figure in line:
                if figure and figure.skin:
                    skin = figure.skin

        for line in self.game.player_map:
            for figure in line:
                if figure and figure.image_id == -1:
                    if not figure.skin:
                        figure.skin = skin
                        figure.create_skin()
                    y, x = self.get_pixels_middle_from_location(figure.y, figure.x)
                    figure.x_p, figure.y_p = x, y
                    figure.image_id = self.canvas.create_image((x, y), image=figure.image)
