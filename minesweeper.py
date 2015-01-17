""" 
    Minesweeper game
    Download it to scripts directory and import however you like.
    I believe there are no name conflicts.
    
    ------IMPORTANT-------
    you should put minesweeper.root.mainloop() (or root.mainloop())
    as a last line in your script in order to 
    
    Controls from within your script:
    
    click(v,h)      -for left click
    m_click(v,h)    -for middle (wheel) click
    r_click(v,h)    -for right click  
    retart()        -to restart the game
    pause()         -to pause the game
    open_field      -returns the open field
      
    Not able to press one cell, drag and release at other cell
    will still open the pressed cell.
"""

from Tkinter import *
from random import shuffle

# change here for different field size
ver = 10
hor = 10
mines = 10

sec = 0
minutes = 0
started = False
paused = False
is_lost = False
set_flags = 0

# list used to display No of set flags. Contains 1 element, 
# which is Tkinter Label object
flags_num = []

# list of placeholders for each cell
# will be filled with actual button objects in App class
button_list = [[' 'for i in range(hor)] for k in range(ver)]
# list used to display while paused
paused_list = button_list[:]
digit_colors = {'1':'#1e90ff', '2':'#2e8b57', 
                '3':'#996633', '4':'#00008b', 
                '5':'#8b0000', '6':'#00ffff', 
                '7':'#000000', '8':'#ffff00', 
                'M':'#ff0000', '*':'#ff0000',
                ' ':'#ffffff',} 

def field_builder(ver, hor, mines):
    # builds list of lists representing minefield
    long_line = list(mines * "*" + (ver * hor - mines) * "-")
    shuffle(long_line)
    field = [long_line[x * hor: x * hor + hor] for x in range(ver)]
    return field
    
def pointer_surroundings(v,h):
    # returns coordinates of surrounding cells for a given cell as a list
    return [[v + V,h + H] for V in [-1,0,1] for H in [-1,0,1]
     if 0 <= v + V < ver and 0 <= h+ H < hor]
    
def field_filler(field):
    # builds actual minefield filled with mine counts
    for V in range(ver):
        for H in range(hor):
            if field[V][H] != "*":
                surroundings = pointer_surroundings(V,H)
                mines = 0
                for i in surroundings:
                    if field[i[0]][i[1]] == "*":
                        mines +=1
                if mines == 0:
                    field[V][H] = ' '
                else:
                    field[V][H] = str(mines)
    return field        

def count_flags(v,h):
    # counts No of flags set in surrounding cells for a given cell
    surroundings = pointer_surroundings(v,h)
    flags = 0
    for i in surroundings:
        if open_field[i[0]][i[1]] == 'M' or open_field[i[0]][i[1]] == '*':
            flags +=1
    return str(flags)
    
def cascade(v,h):
    # cascade opener
    # made without recursion as it was more clear
    # returns list of cells to open
    cells_to_explore = pointer_surroundings(v,h)     
    cells_to_open = cells_to_explore[:]
    cells_explored = []
    while len(cells_to_explore) != 0:
        cell = cells_to_explore.pop()   
        current_surr = pointer_surroundings(cell[0], cell[1])
        if field[cell[0]][cell[1]] == ' ' and cell not in cells_explored: 
            for i in current_surr:
                cells_to_explore.append(i)
                cells_explored.append(cell)
                cells_to_open.append(i)
    # removes duplicate elements from cells_to_open
    unique = []
    for item in cells_to_open:
        if item not in unique:
            unique.append(item)
    return unique

def count_x(lst,x):
    # count x in list of lists
    res = 0
    for i in lst:
        res += i.count(x)
    return res
        
def restart():    
    # it is not called to build very first field
    # this function is called recursively if first open cell contains mine
    # from callbackBP1 function
    global field, filled_field, open_field, correct_mines, minutes, sec
    global started, set_flags, paused, is_lost
    paused = False
    is_lost = False
    started = False    
    set_flags = 0
    minutes = 0
    sec =0
    app.time.config(text = '0:00')
    flags_num[0].config(text = str(set_flags) + ' of ' + str(mines) + ' flags set')
    field = field_builder(ver, hor, mines)    
    filled_field = field_filler(field)    
    open_field = [['?'for i in range(hor)] for k in range(ver)]  
    correct_mines = [['?'for i in range(hor)] for k in range(ver)]  
    for arow in button_list:
        for acol in range(len(arow)):
            # set the background color to default # d9d9d9 after lost() 
            # (where the background colors of some cells were changed)
            arow[acol].config(text = ' ', relief = 'raised', bg = '#d9d9d9')
    app.advice_text.config(text = "Hit 'P' to pause, " +
                                     (hor- 10)*' ' + "'R' to restart",
                                     font=("Courier", 16, 'bold'),fg ='black')        
def pause():
    global paused
    if not paused:
        paused = True
        app.advice_text.config(text = 'P A U S E D', 
                              font = ('Courier', 16, 'bold'), 
                              fg = 'red')
        #cover all field with balnk cells
        for arow in button_list:
            for acol in range(len(arow)):
                arow[acol].config(text = ' ', relief = 'raised', bg = '#d9d9d9')
    else:
        paused = False
        app.tick()
        app.advice_text.config(text = "Hit 'P' to pause, " +
                                     (hor- 10)*' ' + "'R' to restart",
                                     font=("Courier", 16, 'bold'),fg ='black')
        for v in range(ver):
            for h in range(hor):
                if open_field[v][h] == '?':
                    button_list[v][h].config(text = ' ', relief = 'raised')
                elif open_field[v][h] == 'M':
                    button_list[v][h].config(text = open_field[v][h],
                                 relief = 'flat',
                                 fg = digit_colors[open_field[v][h]],
                                 bg = '#ffcc99')
                else:
                    button_list[v][h].config(text = open_field[v][h], 
                                 relief = 'flat',
                                 fg = digit_colors[open_field[v][h]]) 
                                
def lost(v,h):
    global paused, started, is_lost
    # will reuse paused to stop timer and reset it in restart()
    paused  = True
    is_lost = True
    started = False
    app.advice_text.config(text = "LOST: Press 'R' to restart",
                           font=("Courier", 16, 'bold'),fg ='red') 
    for vr in range(ver):
            for hr in range(hor):
                if field[vr][hr] == '*' and correct_mines[vr][hr] != 'Mine':
                    button_list[vr][hr].config(text = field[vr][hr], 
                                 relief = 'flat',
                                 bg = '#ff6600') 
                # likely not gonna happen, cause player will lose before
                elif field[vr][hr] in ' 12345678' and open_field[vr][hr] == 'M':
                    button_list[vr][hr].config(text = 'X', relief = 'flat',
                                 bg = 'red', fg = 'black') 
                elif field[vr][hr] == '*':
                    button_list[vr][hr].config(text = field[vr][hr], 
                                 relief = 'flat',
                                 fg = digit_colors[field[vr][hr]]) 
    button_list[v][h].config(relief = 'flat', bg = 'red')    
    
def win(v,h):
    if (count_x(open_field, 'M') + count_x(open_field, '?') == mines 
                                            and field[v][h] != '*'): 
        return True
    elif field[v][h] == '*': 
        return False

# builds first field of the game
field = field_builder(ver, hor, mines)    
filled_field = field_filler(field)    
open_field = [['?'for i in range(hor)] for k in range(ver)]  
# used to determine if set flags represent actual mines 
# if mine count equals number of set flags on a right click
# on a open cell containing number
correct_mines = [['?'for i in range(hor)] for k in range(ver)]  



class App:
        
    def __init__(self, master):
        
        self.frame = Frame(master)
        self.frame.bind_all("<Key>",self.keyevent)
        self.frame.pack()
        # change the limitations here
        if ver * hor < mines *2:
            self.frame.config( width=768, height=576)
            w = Label(self.frame, text="Not gonna happen\nToo many mines", 
                      font = ('Courier', 22, 'bold'), 
                      fg = 'red'
                      )
            w.place(relx=0.5, rely=0.5, anchor=CENTER)
        elif ver < 10 or hor < 10:
            self.frame.config( width=768, height=576)
            w = Label(self.frame, text="Not gonna happen\nToo small field", 
                      font = ('Courier', 22, 'bold'), 
                      fg = 'red'
                      )
            w.place(relx=0.5, rely=0.5, anchor=CENTER)
        elif mines < 10:
            self.frame.config( width=768, height=576)
            w = Label(self.frame, text="Not gonna happen\nNot enough mines", 
                      font = ('Courier', 22, 'bold'), 
                      fg = 'red'
                      )
            w.place(relx=0.5, rely=0.5, anchor=CENTER)                        
        else:
            # actual game begins
            for v in range(ver):
                for h in range(hor):
                    self.button = Button(
                        self.frame, 
                        text = ' ',
                        font = ("Courier", 16, 'bold'))
                    self.button.grid(row = v, column = h)
                    button_list[v][h] = self.button
                    self.button.bind("<ButtonPress-1>", 
                                     lambda event, v=v, h=h: callbackBP1(v,h))
                    self.button.bind("<ButtonRelease-1>", 
                                     lambda event, v=v, h=h: callbackBR1(v,h))
                    self.button.bind("<ButtonPress-2>", 
                                     lambda event, v=v, h=h: callbackBP2(v,h))
                    self.button.bind("<ButtonRelease-2>", 
                                     lambda event, v=v, h=h: callbackBR2(v,h))
                    self.button.bind("<Button-3>", 
                                     lambda event, v=v, h=h: callbackB3(v,h))
                                     
            self.separator = Frame(self.frame, height = 100, 
                             bd = 5, relief = 'raised')
            self.advice_text = Label(self.separator, text = "Hit 'P' to pause, "
                                     + (hor- 10)*' ' + "'R' to restart",
                                     font=("Courier", 16, 'bold'))
            self.advice_text.pack()
            self.separator.grid(row = ver, columnspan = hor, sticky = 'E' + 'W')
            self.flags = StringVar()
            self.flags.set(str(set_flags) + ' of ' + str(mines) + ' flags set') 
            self.flags_txt = Label(self.frame, text = self.flags.get(), 
                                               font = ("Courier", 16, 'bold'))
            flags_num.append(self.flags_txt) 
            self.flags_txt.grid(row = ver + 1, column = 0, columnspan = 8)      
            
            self.elapsed = '0:00'
            self.time = Label(self.frame, text = str(self.elapsed),
                                          font=("Courier", 16, 'bold'))
            self.time.grid(row = ver + 2, column = 0, columnspan = 4)
            self.restart_button = Button(self.frame, text = 'RESTART', 
                                         command = restart,
                                         font=("Courier", 16, 'bold'))
            self.restart_button.grid(row = ver + 2, column = hor - 3, 
                                     columnspan = 4)
            self.pause_button = Button(self.frame, text = ' PAUSE ', 
                                         command = pause,
                                         font=("Courier", 16, 'bold'))
            self.pause_button.grid(row = ver + 1, column = hor - 3, 
                                     columnspan = 4)          

    def tick(self):
        # timer used to update elapsed time
        # uses tkinter built in timer
        global sec, minutes

        self.time_to_display = '0:00'
        if sec < 10:
            self.time_to_display = str(minutes) + ':0' + str(sec)
        elif sec > 59:
            sec = 0
            minutes +=1
            self.time_to_display = str(minutes) + ':00'
        else:
            self.time_to_display = str(minutes) + ':' + str(sec)
        self.time.config(text = self.time_to_display)
        if started and not paused:
            sec += 1
            self.time.after(1000, self.tick)     
       
            
    def keyevent(self, event):
        if event.char == 'r':
            restart()
        elif event.char == 'p':
            pause()
        else:
            pass

def click(v,h):
    # left button click imitation
    callbackBP1(v,h)
    callbackBR1(v,h)
        
def m_click(v,h):
    # middle button click imitation
    callbackBP2(v,h)
    callbackBR2(v,h)

def r_click(v,h):
    # right click imitation
    # I suspect that in some cases it may misbehave, cannot reproduse myself though.
    # in that case change the name of that function, so it doesn`t begin with 'r'.
    # So it is not mixed up with keyboard 'r' press event for restart
    callbackB3(v,h)
        
def callbackBP1(v,h):
    # left button press
    # doesn`t do much, just highlights one or more cells
    global started, paused, is_lost
    if paused:
        return  
    if is_lost:
        #started is set to false to start timer
        started = False
        is_lost = False
    if not started and open_field[v][h] == '?':
        started = True
        is_lost = False
        # so the first click doesn`t reveal a mine
        if field[v][h] == '*':
            restart()
            started = False            
            callbackBP1(v,h)
            return
        app.tick() 
    if open_field[v][h] == '?':
        button_list[v][h].config(relief = 'flat')
    elif open_field[v][h] in '12345678':
        for cell in pointer_surroundings(v,h):
            button_list[cell[0]][cell[1]].config(relief = 'flat')
    else:
        pass
        
def callbackBR1(v,h):
    # left button release
    global started    
    if paused:
        return   
    if is_lost:
        return        
    # not to calculate cascade one more time
    if field[v][h] == ' ' and open_field[v][h] == ' ':
        return

    elif field[v][h] == ' ':
        # cascade opener
        for cell in cascade(v,h):
            if open_field[cell[0]][cell[1]] == 'M':
                button_list[cell[0]][cell[1]].config(text = 'M', relief = 'flat',
                         fg = digit_colors['M'], bg = '#d9d9d9') 
                open_field[cell[0]][cell[1]] = 'M'
            else:
                button_list[cell[0]][cell[1]].config(text = field[cell[0]][cell[1]],
                         relief = 'flat', bg = '#d9d9d9',
                         fg = digit_colors[field[cell[0]][cell[1]]]) 
                open_field[cell[0]][cell[1]] = field[cell[0]][cell[1]]                

    elif open_field[v][h] == 'M' and field[v][h] == '*':
        # if clicked in a correctly set flag
        return

    elif open_field[v][h] == '?':
        # if cell is not open yet
        button_list[v][h].config(text = field[v][h], relief = 'flat',
                                 fg = digit_colors[field[v][h]]) 
        open_field[v][h] = field[v][h]
        if field[v][h] == '*':
            lost(v,h)

    elif open_field[v][h] in '12345678' and open_field[v][h] == count_flags(v,h):
        # if number in cell equals to the number of flags in surroundings
        # if all flags are correct, reveals surroundings
        for cell in pointer_surroundings(v,h):
            if field[cell[0]][cell[1]] == ' ':
                # if there is empty cell in surroundings, reveals cascade
                for cell in cascade(v,h):
                    if open_field[cell[0]][cell[1]] == 'M':
                        button_list[cell[0]][cell[1]].config(text = 'M', 
                        relief = 'flat', fg = digit_colors['M'])  
                    else:
                        button_list[cell[0]][cell[1]].config(
                                   text = field[cell[0]][cell[1]], 
                                   relief = 'flat', 
                                   fg = digit_colors[field[cell[0]][cell[1]]]) 
                        open_field[cell[0]][cell[1]] = field[cell[0]][cell[1]]
            elif (field[cell[0]][cell[1]] == '*' and 
                              open_field[cell[0]][cell[1]] == 'M'):
                # leaves correct flags in place
                button_list[cell[0]][cell[1]].config(text = 'M' , relief = 'flat',
                                         fg = digit_colors['M'])    
                correct_mines[cell[0]][cell[1]] = 'Mine'                                     
            elif field[cell[0]][cell[1]] == '*' and open_field[cell[0]][cell[1]] != 'M':
                # if flag was set incorrectly, calls lost()
                button_list[cell[0]][cell[1]].config(text = 'X', relief = 'flat',
                                                 fg = '#ff0000')
                lost(v,h)
            else:
                button_list[cell[0]][cell[1]].config(text = field[cell[0]][cell[1]], 
                   relief = 'flat', fg = digit_colors[field[cell[0]][cell[1]]])             
                open_field[cell[0]][cell[1]] = field[cell[0]][cell[1]]

    else:
        # otherwise just unhighhlights
        for cell in pointer_surroundings(v,h):
            if correct_mines[cell[0]][cell[1]] != 'Mine' and open_field[cell[0]][cell[1]] == 'M':
                button_list[cell[0]][cell[1]].config(relief = 'raised')
            elif open_field[cell[0]][cell[1]] in '?':
                button_list[cell[0]][cell[1]].config(relief = 'raised')
    # checks if won
    if win(v,h):
        app.advice_text.config(text = "WIN: Press 'R' to restart",
                                     font=("Courier", 16, 'bold'),fg ='red')  
        started = False   
    elif win(v,h) == False: 
        # the last click uncovers a mine
        lost(v,h) 
    else:
        pass

             
def callbackBP2(v,h):
    # middle button press
    # highlights surroundings
    if paused:
        return   
    for cell in pointer_surroundings(v,h):
        button_list[cell[0]][cell[1]].config(relief = 'flat')

def callbackBR2(v,h):
    # middle button release
    # unhighlights surroundings
    if paused:
        return   
    for cell in pointer_surroundings(v,h):
        if open_field[cell[0]][cell[1]] == '?':
            button_list[cell[0]][cell[1]].config(relief = 'raised')
        elif (open_field[cell[0]][cell[1]] == 'M' 
                           and correct_mines[cell[0]][cell[1]] != 'Mine'):
            button_list[cell[0]][cell[1]].config(relief = 'raised')
        
def callbackB3(v,h):
    # right click
    # used to set and unset flags
    global set_flags
    if paused or not started:
        return
    elif not started:
        return
    elif open_field[v][h] == ' ':
        # not to set a flag if cell is open and empty
        return
    elif open_field[v][h] == 'M' and field[v][h] == '*':
        # correct flag unset
        button_list[v][h].config(text = ' ',  fg = digit_colors[' '], 
                                 relief = 'raised', bg = '#d9d9d9')            
        open_field[v][h] = '?'    
        correct_mines[v][h] ='?'      
        set_flags -= 1  
    elif open_field[v][h] == 'M':
        # incorrect flag unset
        button_list[v][h].config(text = ' ',  fg = digit_colors[' '], 
                                 bg = '#d9d9d9')            
        open_field[v][h] = '?'
        set_flags -= 1
    elif open_field[v][h] in '12345678* ':
        return
    else:
        button_list[v][h].config(text = 'M', fg = digit_colors['M'], bg = '#ffcc99')            
        open_field[v][h] = 'M'
        set_flags += 1
    flags_num[0].config(text = str(set_flags) + ' of ' + str(mines) + ' flags set')

root = Tk()
app = App(root)
#window is not resizable
root.resizable(width = False, height = False)
root.title('Minesweeper')

if __name__ == '__main__':
    root.mainloop()
