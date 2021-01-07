'''
Sudoku game!
Built using tkinter
includes backtracking solving algorithm
generates a random board according to user's difficulty selection
'''

# imports
import sys
import random
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import ImageTk, Image

# declare some constants
MAX_ITERATIONS=15000
NOT_FOUND=(-1, -1)

# to add in future:
# add button solve for cell


class Sudoku:
    
    # initialise game
    def __init__(self):
        self.bo = [[0 for i in range(9)] for i in range(9)] # 9x9 board with zeros
        self.bo_solved = []                                 # board to store solution
        self.count = 0                                      # count for solving algorithm
        self.level=0                                        # difficulty
        self.welcome_win()                                  # start game by showing welcome window
        self.random_fill()                                  # fill the board with random numbers
        self.changed = []                                   # list of cells changed by user
        self.play = True                                    # indicates playing in progress
        self.disable_changes = False                        # flag to disable changes if finished
    
    # initialise GUI and run tkinter mainloop
    def initUI(self):
        
        root = tk.Tk()
        root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file='icon.png')) # program bottom bar icon
        root.title("Sudoku")
        
        # window size parameters
        window_height = 500
        window_width = 550
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.geometry("{}x{}+{}+{}".format(window_width, window_height, int((screen_width / 2) - (window_width / 2)),
                                           int((screen_height / 2) - (window_height / 2))))
        
        # frame1 - board components
        frame1 = tk.Frame(root)
        frame1.pack(side=tk.TOP)
        board = [[tk.Label(frame1, text=self.bo[i][j] if self.bo[i][j] != 0 else " ",
                           width=5, height=2, borderwidth=1, relief="solid", font="Arial", bg="white")
                  for j in range(9)] for i in range(9)]
        s = ttk.Style()
        s.configure('TSeparator', background='#b52a2a')
        
        for i in range(9):
            for j in range(9):
                board[i][j].grid(row=i, column=j)
                board[i][j].bind('<Enter>', self.cell_foucs)
                board[i][j].bind('<Leave>', self.cell_leave)
                board[i][j].bind('<Key>', self.add)
                # board[i][j].bind('<Control-Key-1>', self.note)
                if i>0 and i%3==0:
                    ttk.Separator(frame1, orient="vertical").grid(row=i, column=j, sticky=tk.N + tk.E + tk.W)
                if j>0 and j%3==0:
                    ttk.Separator(frame1, orient="horizontal").grid(row=i, column=j, sticky=tk.N + tk.S + tk.W)

        
        # closing functions

        def close():
            self.play = False
            root.destroy()
        
        def play_again():
            ans = messagebox.askquestion("Sudoku", "Are you sure?")
            if ans == "yes":
                root.destroy()
        
        # frame2 - "new game" and "solve" button
        
        frame2 = tk.Frame(root)
        frame2.pack(side=tk.BOTTOM, anchor=tk.S, fill=tk.BOTH)
        frame2.columnconfigure(0, weight=1)
        frame2.columnconfigure(1, weight=1)
        reset_btn = tk.Button(frame2, text="New Game", command=play_again, padx=10, pady=5, font=("Fixedsys","16"))
        reset_btn.grid(row=1,column=0,sticky="nsew")
        solve_btn = tk.Button(frame2, text="Solve", padx=10, pady=5,font=("Fixedsys","16"))
        solve_btn.bind("<Button>", lambda event: self.show_sol(board))
        solve_btn.grid(row=1,column=1,sticky="nsew")
        
        '''
        def mark_num(event):
            print("in mark num")
            num=int(event.widget['text'])
            color=""
            for i in range(9):
                for j in range(9):
                    if self.bo[i][j]==num:
                        print("found num in ",i,j)
                        color = "#ffe1ad" if event.widget["relief"] == "raised" else prev_colors[i][j]
                        board[i][j].config(bg=color)
            if color == "#ffe1ad":
                event.widget.config(relief="sunken")
            else:
                event.widget.config(relief="solid")
        
        numbers=[]
        prev_colors=[[cell["bg"] for cell in row] for row in board]
        for i in range(9):
            numbers.append(tk.Button(frame2, text=i+1, padx=3, pady=3,font="Arial"))
            numbers[i].grid(row=0,column=i)
            numbers[i].bind('<Button>',mark_num)
        '''
        
        root.protocol("WM_DELETE_WINDOW", close)
        root.focus_force()
        root.mainloop()
    
    # show solution of board
    def show_sol(self, b):
        for i in range(9):
            for j in range(9):
                b[i][j].config(text=self.bo_solved[i][j],
                               bg="#ededed" if self.bo[i][j] == 0 or (i, j) in self.changed else "white")
        self.disable_changes=True

    # some GUI cells functions
    
    def cell_foucs(self, event):
        event.widget.focus_set()
        event.widget.config(bg="#ffd2cf")
    
    def cell_leave(self, event):
        info = event.widget.grid_info()
        (i, j) = (info["row"], info["column"])
        if not (i, j) in self.changed:
            event.widget.config(bg="white")
        else:
            event.widget.config(bg="#ededed")
    
    # check if putting number 'num' in cell 'row,col' is legal
    def legal(self, row, col, num):
        if num in self.bo[row] or self.bo[row][col] != 0 or num < 1 or num > 9:
            return False
        column = [self.bo[i][col] for i in range(9)]
        if num in column:
            return False
        box_index = (row // 3) * 3 + col // 3
        for i in range(9):
            for j in range(9):
                if box_index == ((i // 3) * 3 + j // 3) and not (i == row and j == col) and self.bo[i][j] == num:
                    return False
        return True
    
    # fill board randomly
    def random_fill(self):
        i = 0
        while i < 10:
            j = random.randint(0, 8)
            k = random.randint(0, 8)
            num = random.randint(1, 9)
            if not self.legal(j, k, num):
                continue
            i += 1
            self.bo[j][k] = num
            
        # validate board. if not valid, fill again from the start
        if not self.solve():
            self.bo = [[0 for i in range(9)] for i in range(9)]
            self.count = 0
            self.random_fill()
        # if valid, delete some of the numbers according to difficulty selected
        else:
            self.bo_solved = [i[:] for i in self.bo] # store solution in bo_solved
            i = 30 if self.level==0 else (45 if self.level==1 else 60)
            while i > 0:
                j = random.randint(0, 8)
                k = random.randint(0, 8)
                if self.bo[j][k] == 0:
                    continue
                self.bo[j][k] = 0
                i -= 1
    
    # solving algorithm
    def solve(self):
        self.count += 1
        if self.count > MAX_ITERATIONS:
            return False
        (i, j) = self.find_empty()
        if (i, j) == NOT_FOUND: # if not found an empty cell - solving done
            return True
        # try each number between 1-9 in cell, if false positioning,
        # recursion goes back to the cell and tries the next number
        for k in range(1, 10):
            if self.legal(i, j, k):
                self.bo[i][j] = k
                # recursion step with k
                if self.solve():
                    return True
                self.bo[i][j] = 0
        return False
    
    def find_empty(self):
        for i in range(9):
            for j in range(9):
                if self.bo[i][j] == 0:
                    return (i, j)
        return NOT_FOUND
    
    def add(self, event):
        info = event.widget.grid_info()
        (i, j) = (info["row"], info["column"])
        ans = event.char
        if (not ans.isdigit() and ans != '\x08') or self.disable_changes:
            return
        if ans == '\x08':
            if (i, j) in self.changed:
                self.bo[i][j] = 0
                event.widget.config(text=" ", bg="white")
                self.changed.remove((i, j))
        elif self.bo[i][j] == 0 or (i, j) in self.changed:
            ans = int(ans)
            temp = self.bo[i][j]
            self.bo[i][j] = 0
            if self.legal(i, j, ans):
                self.bo[i][j] = ans
                if (i, j) not in self.changed:
                    self.changed.append((i, j))
                event.widget.config(text=self.bo[i][j], bg="#ededed")
            else:
                prev_color = event.widget["bg"]
                self.bo[i][j] = temp
                event.widget.config(bg="red")
                event.widget.after(300, lambda: event.widget.config(bg=prev_color))
        (i, j) = self.find_empty()
        if (i, j) == NOT_FOUND:
            messagebox.showinfo("", "you are done!")
    
    def print_board(self):
        for i in self.bo:
            print(i)
    
    # initialises welcome window
    def welcome_win(self):
        root = tk.Tk()
        root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file='icon.png'))
        root.title("Sudoku")
        window_height = 150
        window_width = 300
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.geometry("{}x{}+{}+{}".format(window_width, window_height, int((screen_width / 2) - (window_width / 2)),
                                           int((screen_height / 2) - (window_height / 2))))
        
        frame = tk.Frame(root)
        
        logo = Image.open('start.png')
        logo = logo.resize((260, 70), Image.ANTIALIAS)
        image=ImageTk.PhotoImage(logo)
        img_lbl = tk.Label(frame, image=image)
        img_lbl.grid(row=0,column=0,columnspan=3)
        
        level_lbl=tk.Label(frame,text="Select Difficulty:",font=("Fixedsys","14"))
        level_lbl.grid(row=1,column=0,columnspan=3)
        
        def set_level(event):
            self.level=event.widget.grid_info()["column"]
            root.destroy()
        
        easy_btn=tk.Button(frame,text="Beginner")
        easy_btn.grid(row=3,column=0)
        inter_btn=tk.Button(frame,text="Intermediate")
        inter_btn.grid(row=3, column=1)
        mas_btn=tk.Button(frame,text="Master")
        mas_btn.grid(row=3, column=2)
        easy_btn.bind("<Button>", set_level)
        inter_btn.bind("<Button>", set_level)
        mas_btn.bind("<Button>", set_level)
        frame.pack()
        root.protocol("WM_DELETE_WINDOW", lambda : sys.exit())
        root.mainloop()

def main():
    while True:
        game = Sudoku()
        game.initUI()
        if not game.play:
            break

if __name__ == '__main__':
    main()
