#!/usr/bin/env python3
# coding=utf-8

## GUI lib
import tkinter as tk
from PIL import Image, ImageTk

## Import other modules
import page_getter
import bus_stop_parser

## Misc system imports
import time
import sys
import traceback
import os.path

## Fonts and Colors (RGB)
background_grey        = "#3C4550"
lighter_grey           = "#626971"
text_color_off_white   = "#F0F8FA"
text_color_ferrari_red = "#FF2800"
text_font = 'DejaVu Sans'
text_size = 25
screen_res = '1400x900'

## Global settings
update_interval = 15000 # milliseconds
border_width    = 0 # set to 2 to debug
the_bus_stop    = 'Södermalmsgatan'

## Fault handling
backoff_factor = 1
no_of_errors_logged = 0
no_of_errors_to_save = 3

def getLogfile(no_of_errors_logged, no_of_errors_to_save):
    if no_of_errors_logged >= no_of_errors_to_save:
        error_log_to_remove = "error_" +\
                              str(no_of_errors_logged + 1
                                  - no_of_errors_to_save) +\
                              ".log"
        if os.path.exists(error_log_to_remove):
            os.remove(error_log_to_remove)
    return "error_" + str(no_of_errors_logged + 1) + ".log"

def getColAttr(col):
    # returns (col_width, col_weight)
    if   col == 0: return(0, 0)
    elif col == 1: return(30, 40)
    elif col == 2: return(6, 1)
    elif col == 3: return(6, 1)
    elif col == 4: return(5, 1)

def createPhotoImage(path):
    try:
        img = Image.open(path)
    except FileNotFoundError:
        img = Image.open('unknown.png')
    img.thumbnail((text_size*4.6, 10000), Image.ANTIALIAS)
    return ImageTk.PhotoImage(img)

class Mainframe(tk.Frame):
    # Mainframe contains the widgets
    # More advanced programs may have multiple frames
    # or possibly a grid of subframes

    def __init__(self, master, *args, **kwargs):
        # *args packs positional arguments into tuple args
        # **kwargs packs keyword arguments into dict kwargs
        
        # initialise base class
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.master = master
        self.Start()
        # in this case the * an ** operators unpack the parameters

    def Start(self):
        # Create the top frame, including bus stop and time, and an empty line
        self.BusStop = tk.StringVar()
        self.CurrTime = tk.StringVar()
        self.ErrorIndicator = tk.StringVar()
        self.NrOfErrorsLogged = tk.StringVar()

        self.TopFrame = tk.Frame(self,
                                 bg = background_grey,
                                 borderwidth = border_width,
                                 relief = "solid",)
        self.TopFrame.pack(fill='x')

        self.TopFrame.grid_columnconfigure(0, weight=1)
        self.TopFrame.grid_rowconfigure(2, weight=1)

        n = 0
        for l in range(2):
            if n == 0:
                text0 = self.BusStop
                text1 = self.CurrTime
                text_color = text_color_off_white
            else:
                text0 = self.ErrorIndicator
                text1 = self.NrOfErrorsLogged
                text_color = text_color_ferrari_red
            aLabel1 = tk.Label(self.TopFrame,
                               font = (text_font, text_size, 'bold'),
                               anchor = 'w',
                               bg = background_grey,
                               borderwidth = border_width,
                               relief = "solid",
                               foreground = text_color,
                               textvariable = text0)
            aLabel2 = tk.Label(self.TopFrame,
                               font = (text_font, text_size, 'bold'),
                               anchor = 'w',
                               bg = background_grey,
                               borderwidth = border_width,
                               relief="solid",
                               foreground = text_color,
                               textvariable = text1)
            aLabel1.grid(row=n, column=0, sticky="w")
            aLabel2.grid(row=n, column=1, sticky="e")
            n += 1

        # Get the print_tuple for the first time to determine how many lines
        # are needed, i.e. how many line frames to create
        (bus_stop, curr_time, print_tuple) = self.getPrintTupleForGui(the_bus_stop)
        self.NrOfDests = len(print_tuple) - 1

        # Create all lines and columns
        vars = []
        line = 0
        for i in range(len(print_tuple)): # lenght of print_tuple, i.e. nr of
                                          # departures incl. head line
            if line%2 == 0:
                bg_color = background_grey
            else:
                bg_color = lighter_grey

            self.LineFrame = tk.Frame(self,
                                      bg = bg_color,
                                      borderwidth = border_width,
                                      relief = "solid")
            self.LineFrame.pack(fill='x')

            row_tuple = ()
            for col in range(len(print_tuple[0])): # nr of rows, or length of
                                                   # row tuple, i.e.
                                                   # # dest next nextnext (pos)
                if col == 0:
                    # special case for having the image of the bus line
                    img = Image.open('unknown.png')
                    img.thumbnail((text_size*4.6, 10000), Image.ANTIALIAS)
                    self.img = ImageTk.PhotoImage(img)
                    self.imgLabel = tk.Label(self.LineFrame,
                                             borderwidth = border_width,
                                             relief = "solid",
                                             image = self.img,
                                             bg = bg_color)
                    self.imgLabel.grid(row=0, column=col, sticky="w",
                                       padx=(text_size*0.25, text_size*0.25),
                                       pady=(text_size*0.25, text_size*0.25))
                    self.imgLabel.image = self.img
                    self.LineFrame.grid_columnconfigure(col, weight = 0)
                    row_tuple += (self.imgLabel,)
                else:
                    var = tk.StringVar()
                    (col_width, col_weight) = getColAttr(col)
                    self.Col = tk.Label(self.LineFrame,
                                        font = (text_font, text_size, 'bold'),
                                        anchor = 'w',
                                        borderwidth = border_width,
                                        relief = "solid",
                                        bg = bg_color,
                                        width = int(round(col_width)),
                                        foreground = text_color_off_white,
                                        textvariable = var)
                    self.Col.grid(row=0, column=col, sticky="w")
                    self.LineFrame.grid_columnconfigure(col, weight = col_weight)
                    row_tuple += (var,)
            line += 1
            vars.append(row_tuple)
        self.vars = vars

        # Set update interval and go in to the Update loop
        self.TimerInterval = update_interval
        self.Update()

    # Update widget field with new values in a print_tuple that looks like this:
    # print_tuple = [('#', 'Destination', 'Avgår', 'Nästa', 'Läge')
                   # ('25', 'Balltorp', '8', '18', 'A'),
                   # ('52', 'Skogome', '3', '13', 'A'),
                   # ...]
    def UpdateFields(self, print_tuple):
        line = 0
        for tup in print_tuple:
            col = 0
            for elem in tup:
                if col == 0:
                    self.img = createPhotoImage(elem + '.png')
                    self.vars[line][col].configure(image = self.img)
                    self.vars[line][col].image = self.img
                elif col == 1:
                    self.vars[line][col].set(' ' + elem)
                else:
                    self.vars[line][col].set(elem)
                col += 1
            line += 1

    # Loop that fetches all fields that continuously shall be updated
    def Update(self):
        result = self.getPrintTupleForGui(the_bus_stop)
        if result == None:
            # If there is an exception, 'None' will be returned and it needs to
            # be handled, just pass since the exception will callback here
            pass
        else:
            (bus_stop, curr_time, print_tuple) = result
            no_of_dests = len(print_tuple) - 1
            if self.NrOfDests != no_of_dests:
                #print(self.NrOfDests, "!=", no_of_dests, "-> Restart!")
                self.Destroy()
                self.after(1, self.Start)
            else:
                self.BusStop.set('Hållplats: ' + bus_stop)
                self.CurrTime.set('Kl: ' + curr_time)
                self.UpdateFields(print_tuple)
                self.after(self.TimerInterval, self.Update)

    def Destroy(self):
        for widget in self.winfo_children():
            widget.destroy()

    def getPrintTupleForGui(self, bus_stop):
        global no_of_errors_logged
        global backoff_factor
        global test
        try:
            bus_stop_page = page_getter.get_bus_stop_page(bus_stop)
            (stop,
             curr_time,
             print_tuple_in) = bus_stop_parser.get_print_tuple(bus_stop_page)
            print_tuple_temp = [('#', 'Destination', 'Avgår', 'Nästa', 'Läge')] +\
                               print_tuple_in
            if bus_stop != 'Södermalmsgatan':
                print_tuple = []
                for t in print_tuple_temp: print_tuple.append(t[0:4])
            else:                          print_tuple = print_tuple_temp
            backoff_factor = 1
            self.ErrorIndicator.set('') # indicate up and running again
            return (stop, curr_time, print_tuple)
        except KeyboardInterrupt:
            raise
        except:
            prev_error_ind = str(self.ErrorIndicator.get())
            new_error_ind = prev_error_ind + '!'
            self.ErrorIndicator.set(new_error_ind) # indicate error handling
                                                   # ongoing
            log_file_path = getLogfile(no_of_errors_logged,
                                       no_of_errors_to_save)
            log_file = open(log_file_path, "a")
            now = time.strftime("%Y-%m-%d %H:%M:%S UTC+1", time.gmtime())
            exception = "Unexpected exception:" + str(sys.exc_info())
            log_file.write("ERROR[" + now + "]:" +  exception + "\n")
            print("logged error to file:", log_file_path)
            log_file.write(traceback.format_exc())
            try:
                bus_stop_page
            except:
                pass
            else:
                log_file.write("Web page that caused the error:\n" +
                               bus_stop_page + "\n\n")
            log_file.close()
            no_of_errors_logged += 1
            self.NrOfErrorsLogged.set(no_of_errors_logged)
            backoff_time = backoff_factor * update_interval
            if backoff_factor < 4:
                backoff_factor *= 2
            self.after(backoff_time, self.Update)

class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.title('Board')
        #self.attributes('-fullscreen', True)
        self.geometry(screen_res)
        self.configure(background = background_grey,
                       borderwidth = border_width,
                       relief = "solid")

        Mainframe(self).pack(fill='x', padx = 1*text_size, pady = 1*text_size)

        self.mainloop()

App()