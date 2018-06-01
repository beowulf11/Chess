import tkinter
from board import Board
import json


class ProgramMain(tkinter.Tk):
    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)
        self.title('Chess - Denis Capkovic')
        self.container = tkinter.Frame(self)
        self.container.pack(side="top", fill="both", expand=False)
        self.frames = {}

        frame = Program(self.container, self)
        self.frames['Program'] = frame
        frame.grid(row=0, column=0)

        frame = Board(self.container, self)
        frame.place(width=700, height=700)
        self.frames['Board'] = frame
        frame.grid(row=0, column=0)

        frame = Play(self.container, self)
        self.frames['Play'] = frame
        frame.grid(row=0, column=0)

        frame = PlayRandom(self.container, self)
        self.frames['PlayRandom'] = frame
        frame.grid(row=0, column=0)

        frame = Settings(self.container, self)
        self.frames['Settings'] = frame
        frame.grid(row=0, column=0)

        self.show_frames('Program')

    def show_frames(self, cont, mode='normal'):
        if cont == 'Board':
            self.maxsize(width=700, height=700)
            frame = self.frames[cont]
            if mode == 'load':
                frame.set_up_game()
                frame.load()
            elif mode == 'random_normal':
                frame.set_up_game('rn')
                frame.random_positions_normal()
            elif mode == 'random_zrkadlo':
                frame.set_up_game('rz')
                frame.random_positions_mirror()
            elif mode == 'random_chaos':
                frame.set_up_game('rc')
                frame.random_positions_chaos()
            else:
                frame.set_up_game()
                frame.normal_positions()
            frame.place(width=700, height=700)
        elif cont == 'Play':
            frame = self.frames[cont]
            self.maxsize(width=900, height=700)
        elif cont == 'PlayRandom':
            frame = self.frames[cont]
        elif cont == 'Settings':
            frame = self.frames[cont]
            frame.refresh()
        else:
            frame = self.frames[cont]
            self.maxsize(width=900, height=700)
        frame.tkraise()

    def close(self):
        self.destroy()


class Program(tkinter.Frame):
    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.controller = controller
        self.canvas = tkinter.Canvas(self, width=900, height=700)
        self.canvas.pack()
        self.image = []
        self.nacitaj_obrazku()
        self.vytvor_menu()
        self.bind_obrazovku()

    def nacitaj_obrazku(self):
        '''
            Nacita obrazky ktore sa vyuziju v menu
        '''
        self.image = [tkinter.PhotoImage(file='Images/menu_background.png'),
                      tkinter.PhotoImage(file='Images/button_start.png'),
                      tkinter.PhotoImage(file='Images/button_settings.png'),
                      tkinter.PhotoImage(file='Images/button_exit.png')]

    def vytvor_menu(self):
        '''
        Funkcia vytvori pozadie, play_button, settings_button a exi_button
        '''
        self.canvas.create_image(450, 350, image=self.image[0])
        self.canvas.create_image(450, 250, image=self.image[1])
        self.canvas.create_image(450, 350, image=self.image[2])
        self.canvas.create_image(450, 450, image=self.image[3])

    def bind_obrazovku(self):
        '''
            Prida bind na obrazovku ktora po kliknuti zavola fukciu self.kliknutia
        '''
        self.canvas.bind('<Button-1>', self.kliknutie)

    def kliknutie(self, args):
        '''
            Funkcia zisti ake tlacidlo bolo kliknute
        '''
        if 250 <= args.x <= 660 and 210 <= args.y <= 290:
            self.controller.show_frames('Play')
        if 250 <= args.x <= 660 and 310 <= args.y <= 390:
            self.controller.show_frames('Settings')
        if 250 <= args.x <= 660 and 410 <= args.y <= 490:
            self.controller.close()


class Settings(tkinter.Frame):
    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.controller = controller
        self.canvas = tkinter.Canvas(self, width=900, height=700)
        self.canvas.pack()
        self.image = []
        self.hint_images = []
        self.colors = ['#e74c3c', '#8e44ad', '#f39c12', '#1abc9c']
        self.nacitaj_obrazku()
        self.vytvor_menu()
        self.hints = []
        self.sel_back, self.sel_fig = 0, 0
        self.canvas.bind('<Button-1>', self.kliknutie)

    def refresh(self):
        for i in range(4):
            self.canvas.itemconfig(i + 2, image=self.image[i + 1])
            self.canvas.itemconfig(i + 6, image=self.image[i + 5])
            self.canvas.itemconfig(self.hint_images[i], image=self.image[-4])
        with open('settings.txt', 'r') as file:
            self.settings_selected = json.load(file)
        self.sel_back, self.sel_fig = int(self.settings_selected["background"]), int(self.settings_selected["figures"])
        self.sel_hint = self.colors.index(self.settings_selected['hint'])
        self.sel_dragging = self.settings_selected['dragging']
        self.sel_ai = self.settings_selected['ai']
        self.canvas.itemconfig(self.hint_images[self.sel_hint], image=self.image[-3])
        self.canvas.itemconfig(self.sel_back + 2, image=self.image[int(self.sel_back) + 9])
        self.canvas.itemconfig(self.sel_fig + 6, image=self.image[int(self.sel_fig) + 13])
        if self.sel_dragging == 'True':
            self.canvas.itemconfig(19, image=self.image[19])
        elif self.sel_dragging == 'False':
            self.canvas.itemconfig(19, image=self.image[18])
        if self.sel_ai == True:
            self.canvas.itemconfig(21, image=self.image[19])
        else:
            self.canvas.itemconfig(21, image=self.image[18])

    def save(self):
        self.settings_selected["background"] = self.sel_back
        self.settings_selected["figures"] = self.sel_fig
        self.settings_selected["hint"] = self.colors[self.sel_hint]
        self.settings_selected["dragging"] = self.sel_dragging
        self.settings_selected["ai"] = self.sel_ai
        with open('settings.txt', 'w') as file:
            json.dump(self.settings_selected, file)
        self.controller.show_frames('Program')

    def kliknutie(self, args):
        '''
            Funkcia zisti ake tlacidlo bolo kliknute
        '''
        if 250 <= args.x <= 660 and 610 <= args.y <= 690:
            self.controller.show_frames('Program')
        elif 250 <= args.x <= 560 and 510 <= args.y <= 690:
            self.save()
        if 348 <= args.x <= 392 and 28 <= args.y <= 72:
            if self.sel_dragging == 'True':
                self.canvas.itemconfig(19, image=self.image[18])
                self.sel_dragging = 'False'
            else:
                self.canvas.itemconfig(19, image=self.image[19])
                self.sel_dragging = 'True'
        if 688 <= args.x <= 732 and 28 <= args.y <= 72:
            if self.sel_ai == True:
                self.canvas.itemconfig(21, image=self.image[18])
                self.sel_ai = False
            else:
                self.canvas.itemconfig(21, image=self.image[19])
                self.sel_ai = True
        if 100 <= args.y <= 200:
            for i in range(4):
                if 125 + (i + 1) * 50 + i * 100 <= args.x <= 225 + (i + 1) * 50 + i * 100:
                    self.canvas.itemconfig(self.sel_back + 2, image=self.image[int(self.sel_back) + 1])
                    self.sel_back = i
                    self.canvas.itemconfig(self.sel_back + 2, image=self.image[int(self.sel_back) + 9])
                    return
        if 240 <= args.y <= 340:
            for i in range(4):
                if 125 + (i + 1) * 50 + i * 100 <= args.x <= 225 + (i + 1) * 50 + i * 100:
                    self.canvas.itemconfig(self.sel_fig + 6, image=self.image[int(self.sel_fig) + 5])
                    self.sel_fig = i
                    self.canvas.itemconfig(self.sel_fig + 6, image=self.image[int(self.sel_fig) + 13])
                    return
        if 380 <= args.y <= 480:
            for i in range(4):
                if 125 + (i + 1) * 50 + i * 100 <= args.x <= 225 + (i + 1) * 50 + i * 100:
                    self.canvas.itemconfig(self.hint_images[self.sel_hint], image=self.image[-4])
                    self.sel_hint = i
                    self.canvas.itemconfig(self.hint_images[self.sel_hint], image=self.image[-3])
                    return

    def nacitaj_obrazku(self):
        '''
            Nacita obrazky ktore sa vyuziju v menu
        '''
        self.image = [tkinter.PhotoImage(file='Images/menu_background.png'),
                      tkinter.PhotoImage(file='Images/game_board_00s.png'),
                      tkinter.PhotoImage(file='Images/game_board_01s.png'),
                      tkinter.PhotoImage(file='Images/game_board_02s.png'),
                      tkinter.PhotoImage(file='Images/game_board_03s.png'),
                      tkinter.PhotoImage(file='Images/figure_0.png'),
                      tkinter.PhotoImage(file='Images/figure_1.png'),
                      tkinter.PhotoImage(file='Images/figure_2.png'),
                      tkinter.PhotoImage(file='Images/figure_3.png'),
                      tkinter.PhotoImage(file='Images/game_board_00sS.png'),
                      tkinter.PhotoImage(file='Images/game_board_01sS.png'),
                      tkinter.PhotoImage(file='Images/game_board_02sS.png'),
                      tkinter.PhotoImage(file='Images/game_board_03sS.png'),
                      tkinter.PhotoImage(file='Images/figure_0S.png'),
                      tkinter.PhotoImage(file='Images/figure_1S.png'),
                      tkinter.PhotoImage(file='Images/figure_2S.png'),
                      tkinter.PhotoImage(file='Images/figure_3S.png'),
                      tkinter.PhotoImage(file='Images/button_dragging.png'),
                      tkinter.PhotoImage(file='Images/false.png'),
                      tkinter.PhotoImage(file='Images/true.png'),
                      tkinter.PhotoImage(file='Images/button_ai.png'),
                      tkinter.PhotoImage(file='Images/hint_unselected.png'),
                      tkinter.PhotoImage(file='Images/hint_selected.png'),
                      tkinter.PhotoImage(file='Images/button_save.png'),
                      tkinter.PhotoImage(file='Images/button_back.png')]

    def vytvor_menu(self):
        '''
            Funkcia vytvori pozadie, normal, random, load, exit
        '''
        self.canvas.create_image(450, 350, image=self.image[0])
        self.canvas.create_image(225, 150, image=self.image[1])
        self.canvas.create_image(375, 150, image=self.image[2])
        self.canvas.create_image(525, 150, image=self.image[3])
        self.canvas.create_image(675, 150, image=self.image[4])
        self.canvas.create_image(225, 290, image=self.image[5])
        self.canvas.create_image(375, 290, image=self.image[6])
        self.canvas.create_image(525, 290, image=self.image[7])
        self.canvas.create_image(675, 290, image=self.image[8])
        self.hint_images.append(self.canvas.create_image(225, 430, image=self.image[-4]))
        self.canvas.create_oval(215, 420, 235, 440, fill=self.colors[0]),
        self.hint_images.append(self.canvas.create_image(375, 430, image=self.image[-4]))
        self.canvas.create_oval(365, 420, 385, 440, fill=self.colors[1]),
        self.hint_images.append(self.canvas.create_image(525, 430, image=self.image[-4]))
        self.canvas.create_oval(515, 420, 535, 440, fill=self.colors[2]),
        self.hint_images.append(self.canvas.create_image(675, 430, image=self.image[-4]))
        self.canvas.create_oval(665, 420, 685, 440, fill=self.colors[3]),
        self.canvas.create_image(279, 50, image=self.image[17])
        self.canvas.create_image(370, 50, image=self.image[18])
        self.canvas.create_image(620, 50, image=self.image[20])
        self.canvas.create_image(710, 50, image=self.image[18])
        self.canvas.create_image(450, 550, image=self.image[-2])
        self.canvas.create_image(450, 650, image=self.image[-1])


class Play(tkinter.Frame):
    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.controller = controller
        self.canvas = tkinter.Canvas(self, width=900, height=700)
        self.canvas.pack()
        self.image = []
        self.nacitaj_obrazku()
        self.vytvor_menu()
        self.hints = []
        self.canvas.bind('<Button-1>', self.kliknutie)
        self.canvas.bind('<Motion>', self.hint)

    def hint(self, args):
        hover_item = self.clicked_item(args)
        if hover_item == 'normal':
            self.create_hint('normal')
        elif hover_item == 'random':
            self.create_hint('random')
        elif hover_item == 'load':
            self.create_hint('load')
        else:
            for i in self.hints:
                self.canvas.delete(i)
            self.hints = []

    def create_hint(self, mode):
        if not self.hints:
            self.hints = [self.canvas.create_rectangle(255, 415, 645, 485, fill='white', width=10, outline='#2b3d4f')]
            if mode == 'normal':
                self.hints.append(self.canvas.create_text(450, 450, text='Klasicky sach', font=("Arial", 20)))
            if mode == 'random':
                self.hints.append(self.canvas.create_text(450, 450, text='Vyber nahodneho sachu', font=("Arial", 20)))
            if mode == 'load':
                self.hints.append(self.canvas.create_text(450, 450,
                                                          text='Pokusi sa nacitat hru ak neni ziadna\n'
                                                               'hra ulozena zacina sa klasicka hra',
                                                          font=("Arial", 15)))

    def clicked_item(self, args):
        if 250 <= args.x <= 660 and 110 <= args.y <= 190:
            return 'normal'
        if 250 <= args.x <= 660 and 210 <= args.y <= 290:
            return 'random'
        if 250 <= args.x <= 660 and 310 <= args.y <= 390:
            return 'load'
        if 250 <= args.x <= 660 and 510 <= args.y <= 590:
            return 'Program'

    def kliknutie(self, args):
        '''
            Funkcia zisti ake tlacidlo bolo kliknute
        '''
        clk_item = self.clicked_item(args)
        if clk_item == 'normal':
            self.controller.show_frames('Board', 'normal')
        if clk_item == 'random':
            self.controller.show_frames('PlayRandom')
        if clk_item == 'load':
            self.controller.show_frames('Board', 'load')
        if clk_item == 'Program':
            self.controller.show_frames('Program')

    def nacitaj_obrazku(self):
        '''
            Nacita obrazky ktore sa vyuziju v menu
        '''
        self.image = [tkinter.PhotoImage(file='Images/menu_background.png'),
                      tkinter.PhotoImage(file='Images/button_normal.png'),
                      tkinter.PhotoImage(file='Images/button_random.png'),
                      tkinter.PhotoImage(file='Images/button_load.png'),
                      tkinter.PhotoImage(file='Images/button_back.png')]

    def vytvor_menu(self):
        '''
            Funkcia vytvori pozadie, normal, random, load, exit
        '''
        self.canvas.create_image(450, 350, image=self.image[0])
        self.canvas.create_image(450, 150, image=self.image[1])
        self.canvas.create_image(450, 250, image=self.image[2])
        self.canvas.create_image(450, 350, image=self.image[3])
        self.canvas.create_image(450, 550, image=self.image[4])


class PlayRandom(tkinter.Frame):
    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.controller = controller
        self.canvas = tkinter.Canvas(self, width=900, height=700)
        self.canvas.pack()
        self.image = []
        self.nacitaj_obrazku()
        self.vytvor_menu()
        self.hints = []
        self.canvas.bind('<Button-1>', self.kliknutie)
        self.canvas.bind('<Motion>', self.hint)

    def hint(self, args):
        hover_item = self.clicked_item(args)
        if hover_item == 'random_normal':
            self.create_hint('random_normal')
        elif hover_item == 'random_zrkadlo':
            self.create_hint('random_zrkadlo')
        elif hover_item == 'random_chaos':
            self.create_hint('random_chaos')
        else:
            for i in self.hints:
                self.canvas.delete(i)
            self.hints = []

    def create_hint(self, mode):
        if not self.hints:
            self.hints = [self.canvas.create_rectangle(255, 415, 645, 485, fill='white', width=10, outline='#2b3d4f')]
            if mode == 'random_normal':
                self.hints.append(self.canvas.create_text(450, 450, text='Klasicky sach ale figurky\n'
                                                                         'su nahodne rozostavene',
                                                          font=("Arial", 15)))
            if mode == 'random_zrkadlo':
                self.hints.append(self.canvas.create_text(450, 450,
                                                          text='Pole sa zaplni nahodnymi figurkami, nepriatel\ndostane'
                                                               'take iste rozlozenie zrkadlovo otocnene',
                                                          font=("Arial", 13)))
            if mode == 'random_chaos':
                self.hints.append(self.canvas.create_text(450, 450,
                                                          text='Kazdy hrac dostane nahodny pocet\n'
                                                               'nahodne vygenerovanych figurok',
                                                          font=("Arial", 15)))

    def clicked_item(self, args):
        if 250 <= args.x <= 660 and 110 <= args.y <= 190:
            return 'random_normal'
        if 250 <= args.x <= 660 and 210 <= args.y <= 290:
            return 'random_zrkadlo'
        if 250 <= args.x <= 660 and 310 <= args.y <= 390:
            return 'random_chaos'
        if 250 <= args.x <= 660 and 510 <= args.y <= 590:
            return 'Back'

    def kliknutie(self, args):
        '''
            Funkcia zisti ake tlacidlo bolo kliknute
        '''
        clk_item = self.clicked_item(args)
        if clk_item == 'random_normal':
            self.controller.show_frames('Board', 'random_normal')
        if clk_item == 'random_zrkadlo':
            self.controller.show_frames('Board', 'random_zrkadlo')
        if clk_item == 'random_chaos':
            self.controller.show_frames('Board', 'random_chaos')
        if clk_item == 'Back':
            self.controller.show_frames('Play')

    def nacitaj_obrazku(self):
        '''
            Nacita obrazky ktore sa vyuziju v menu
        '''
        self.image = [tkinter.PhotoImage(file='Images/menu_background.png'),
                      tkinter.PhotoImage(file='Images/button_normal.png'),
                      tkinter.PhotoImage(file='Images/button_zrkadlo.png'),
                      tkinter.PhotoImage(file='Images/button_chaos.png'),
                      tkinter.PhotoImage(file='Images/button_back.png')]

    def vytvor_menu(self):
        '''
            Funkcia vytvori pozadie, normal, random, load, exit
        '''
        self.canvas.create_image(450, 350, image=self.image[0])
        self.canvas.create_image(450, 150, image=self.image[1])
        self.canvas.create_image(450, 250, image=self.image[2])
        self.canvas.create_image(450, 350, image=self.image[3])
        self.canvas.create_image(450, 550, image=self.image[4])


app = ProgramMain()
app.mainloop()
