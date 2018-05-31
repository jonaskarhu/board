#!/usr/bin/env python3
# coding=utf-8

## GUI lib
import tkinter as tk
from PIL import Image, ImageTk
import tkinter.font as tkfont

## Import other modules
import page_getter
import bus_stop_parser
import weather_parser

## Misc system imports
import time
import datetime
import sys
import traceback
import os.path
import re
import math

## Fonts and Colors (RGB)
background_grey        = "#3C4550"
lighter_grey           = "#626971"
text_color_off_white   = "#F0F8FA"
text_color_ferrari_red = "#FF2800"
text_color_red_night   = "#971600"
background_grey_night  = "#000000"
lighter_grey_night     = "#202020"
text_color_night       = "#A4A4A4"
text_font              = 'DejaVu Sans'
text_size              = 23
text_size_weather      = 18
screen_res             = '1400x900'

## Global settings
update_interval      = 15000  # milliseconds
night_mode_interval  = 60000  # milliseconds
weather_interval     = 30000#300000 # milliseconds
border_width         = 0 # set to 2 to debug
border_width_weather = 0 # set to 2 to debug
the_bus_stop         = 'Södermalmsgatan'
forecast_hours       = 10

## Fault handling
backoff_factor       = 1
no_of_errors_logged  = 0
no_of_errors_to_save = 3
log_errors           = False

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

def getColAttrWeather():
    # returns (col_width, col_weight)
    return(10, 20)

def createPhotoImage(path):
    try:
        img = Image.open(path)
    except FileNotFoundError:
        img = Image.open('bus_images/unknown.png')
    img.thumbnail((text_size*4.6, 10000), Image.ANTIALIAS)
    return ImageTk.PhotoImage(img)

def mapWsymb2ToPng(wsymb):
    if   wsymb == 1:  return 'clear'
    elif wsymb == 2:  return 'mostlysunny'
    elif wsymb == 3:  return 'mostlycloudy'
    elif wsymb == 4:  return 'mostlycloudy'
    elif wsymb == 5:  return 'cloudy'
    elif wsymb == 6:  return 'cloudy'
    elif wsymb == 7:  return 'fog'
    elif wsymb == 8:  return 'chancerain'
    elif wsymb == 9:  return 'rain'
    elif wsymb == 10: return 'rain'
    elif wsymb == 11: return 'tstorms'
    elif wsymb == 12: return 'chancesleet'
    elif wsymb == 13: return 'sleet'
    elif wsymb == 14: return 'sleet'
    elif wsymb == 15: return 'chanceflurries'
    elif wsymb == 16: return 'flurries'
    elif wsymb == 17: return 'flurries'
    elif wsymb == 18: return 'chancerain'
    elif wsymb == 19: return 'rain'
    elif wsymb == 20: return 'rain'
    elif wsymb == 21: return 'tstorms'
    elif wsymb == 22: return 'chancesleet'
    elif wsymb == 23: return 'sleet'
    elif wsymb == 24: return 'sleet'
    elif wsymb == 25: return 'chancesnow'
    elif wsymb == 26: return 'snow'
    elif wsymb == 27: return 'snow'
    else:             return 'unknown'

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
        self.CurrTemp = tk.StringVar()
        self.ErrorIndicator = tk.StringVar()
        self.NrOfErrorsLogged = tk.StringVar()

        dark_frames = []
        dark_labels = []
        light_frames = []
        light_labels = []
        red_labels = []

        self.TopFrame = tk.Frame(self,
                                 bg = background_grey,
                                 borderwidth = border_width,
                                 relief = "solid",)
        self.TopFrame.pack(fill='x')

        self.TopFrame.grid_columnconfigure(0, weight=1)
        self.TopFrame.grid_columnconfigure(1, weight=1)
        self.TopFrame.grid_columnconfigure(2, weight=1)
        self.TopFrame.grid_rowconfigure(2, weight=1)
        dark_frames.append(self.TopFrame)

        n = 0
        for l in range(2):
            if n == 0:
                text0 = self.BusStop
                text1 = self.CurrTime
                text2 = self.CurrTemp
                text_color = text_color_off_white
            else:
                text0 = self.ErrorIndicator
                text1 = ""
                text2 = self.NrOfErrorsLogged
                text_color = text_color_ferrari_red
            aLabel1 = tk.Label(self.TopFrame,
                               font = (text_font, text_size, 'bold'),
                               anchor = 'w',
                               bg = background_grey,
                               borderwidth = border_width,
                               relief = "solid",
                               foreground = text_color,
                               width = 35,
                               textvariable = text0)
            aLabel2 = tk.Label(self.TopFrame,
                               font = (text_font, text_size, 'bold'),
                               anchor = 'center',
                               bg = background_grey,
                               borderwidth = border_width,
                               relief="solid",
                               foreground = text_color,
                               width = 35,
                               textvariable = text1)
            aLabel3 = tk.Label(self.TopFrame,
                               font = (text_font, text_size, 'bold'),
                               anchor = 'e',
                               bg = background_grey,
                               borderwidth = border_width,
                               relief="solid",
                               foreground = text_color,
                               width = 35,
                               textvariable = text2)
            aLabel1.grid(row=n, column=0, sticky='w')
            aLabel2.grid(row=n, column=1)
            aLabel3.grid(row=n, column=2, sticky='e')
            if n == 0:
                dark_labels.append(aLabel1)
                dark_labels.append(aLabel2)
                dark_labels.append(aLabel3)
            else:
                red_labels.append(aLabel1)
                red_labels.append(aLabel2)
                red_labels.append(aLabel3)
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
            if line%2 == 0: bg_color = background_grey
            else:           bg_color = lighter_grey

            self.LineFrame = tk.Frame(self,
                                      bg = bg_color,
                                      borderwidth = border_width,
                                      relief = "solid")
            self.LineFrame.pack(fill='x')

            if line%2 == 0: dark_frames.append(self.LineFrame)
            else:           light_frames.append(self.LineFrame)

            row_tuple = ()
            for col in range(len(print_tuple[0])): # nr of cols, or length of
                                                   # one row in tuple, i.e.
                                                   # # dest next nextnext (pos)
                if col == 0:
                    # special case for having the image of the bus line
                    img = Image.open('bus_images/unknown.png')
                    img.thumbnail((text_size*4.6, 10000), Image.ANTIALIAS)
                    self.img = ImageTk.PhotoImage(img)
                    self.imgLabel = tk.Label(self.LineFrame,
                                             borderwidth = border_width,
                                             relief = "solid",
                                             image = self.img,
                                             bg = bg_color)
                    self.imgLabel.grid(row=0, column=col, sticky="w",
                                       padx=(text_size*0.40, text_size*0.40),
                                       pady=(text_size*0.25, text_size*0.25))
                    self.imgLabel.image = self.img
                    self.LineFrame.grid_columnconfigure(col, weight = 0)
                    row_tuple += (self.imgLabel,)
                    if line%2 == 0: dark_labels.append(self.imgLabel)
                    else:           light_labels.append(self.imgLabel)
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
                    if line%2 == 0: dark_labels.append(self.Col)
                    else:           light_labels.append(self.Col)
            line += 1
            vars.append(row_tuple)
        self.vars = vars

        # Weather forecast
        self.sun_up = tk.StringVar()
        self.sun_down = tk.StringVar()
        for i in range(3):
            if i == 1:
                # Weather Headline
                display = "Prognos (SMHI)"#, Soltider: ↑04:32 ↓21:48"
                self.WeatherFrame = tk.Frame(self,
                                             bg = background_grey,
                                             borderwidth = border_width_weather,
                                             relief = "solid")
                self.WeatherFrame.pack(fill='x')
                dark_frames.append(self.WeatherFrame)
                
                # Prognos (SMHI)
                self.Head = tk.Label(self.WeatherFrame,
                                     font = (text_font, text_size_weather, 'bold'),
                                     anchor = 'w',
                                     borderwidth = border_width_weather,
                                     relief = "solid",
                                     bg = background_grey,
                                     foreground = text_color_off_white,
                                     text = display)
                # Small sun icon
                sun_1 = Image.open('weather_icons/clear.png')
                sun_1.thumbnail((text_size_weather*2.6, 10000), Image.ANTIALIAS)
                self.sun_1 = ImageTk.PhotoImage(sun_1)
                self.sun_1Label = tk.Label(self.WeatherFrame,
                                           borderwidth = border_width_weather,
                                           relief = "solid",
                                           anchor = 'e',
                                           image = self.sun_1,
                                           bg = background_grey)
                self.sun_1Label.image = self.sun_1
                # Sun Up Time
                self.SunUp = tk.Label(self.WeatherFrame,
                                      font = (text_font, text_size_weather, 'bold'),
                                      anchor = 'e',
                                      borderwidth = border_width_weather,
                                      relief = "solid",
                                      bg = background_grey,
                                      foreground = text_color_off_white,
                                      textvariable = self.sun_up)
                # Small sun icon
                sun_2 = Image.open('weather_icons/clear.png')
                sun_2.thumbnail((text_size_weather*2.6, 10000), Image.ANTIALIAS)
                self.sun_2 = ImageTk.PhotoImage(sun_2)
                self.sun_2Label = tk.Label(self.WeatherFrame,
                                           borderwidth = border_width_weather,
                                           relief = "solid",
                                           anchor = 'e',
                                           image = self.sun_2,
                                           bg = background_grey)
                self.sun_2Label.image = self.sun_2
                # Sun Down Time
                self.SunDown = tk.Label(self.WeatherFrame,
                                        font = (text_font, text_size_weather, 'bold'),
                                        anchor = 'e',
                                        borderwidth = border_width_weather,
                                        relief = "solid",
                                        bg = background_grey,
                                        foreground = text_color_off_white,
                                        textvariable = self.sun_down)
                self.Head.grid(       row=0, column=0, sticky="w")
                self.sun_1Label.grid( row=0, column=1, sticky="e",
                                      padx=(1*text_size, 0))
                self.SunUp.grid(      row=0, column=2, sticky="e")
                self.sun_2Label.grid( row=0, column=3, sticky="e",
                                      padx=(1*text_size, 0))
                self.SunDown.grid(    row=0, column=4, sticky="e")
                self.WeatherFrame.grid_columnconfigure(0, weight=100)
                self.WeatherFrame.grid_columnconfigure(1, weight=0)
                self.WeatherFrame.grid_columnconfigure(2, weight=0)
                self.WeatherFrame.grid_columnconfigure(3, weight=0)
                self.WeatherFrame.grid_columnconfigure(4, weight=0)
                dark_labels.append(self.Head)
                dark_labels.append(self.sun_1Label)
                dark_labels.append(self.SunUp)
                dark_labels.append(self.sun_2Label)
                dark_labels.append(self.SunDown)
            else:
                # i == 0, i == 2 => empty lines
                display = ""
                self.WeatherFrame = tk.Frame(self,
                                             bg = background_grey,
                                             borderwidth = border_width_weather,
                                             relief = "solid")
                self.WeatherFrame.pack(fill='x')
                dark_frames.append(self.WeatherFrame)
                self.Col = tk.Label(self.WeatherFrame,
                                    font = (text_font, text_size_weather, 'bold'),
                                    anchor = 'w',
                                    borderwidth = border_width_weather,
                                    relief = "solid",
                                    bg = background_grey,
                                    foreground = text_color_off_white,
                                    text = display)
                self.Col.grid(row=0, column=0, sticky="w")
                dark_labels.append(self.Col)

        # Hack to get the image label the same width as the text labels
        font = tkfont.Font(family = text_font, size = text_size_weather, weight = 'bold')
        char_width = font.measure('0')

        smhi_tuple = self.GetWeather()
        wvars = []
        for row in range(len(smhi_tuple[0])-1):
            self.WeatherFrame = tk.Frame(self,
                                         bg = background_grey,
                                         borderwidth = border_width_weather,
                                         relief = "solid")
            self.WeatherFrame.pack(fill='x')
            dark_frames.append(self.WeatherFrame)
            wrow_tuple = ()
            for col in range(len(smhi_tuple)):
                (col_width, col_weight) = getColAttrWeather()
                if (row == 1):
                    img = Image.open('weather_icons/unknown.png')
                    img.thumbnail((text_size_weather*4.6, 10000), Image.ANTIALIAS)
                    self.img = ImageTk.PhotoImage(img)
                    self.imgLabel = tk.Label(self.WeatherFrame,
                                             borderwidth = border_width_weather,
                                             relief = "solid",
                                             anchor = 'center',
                                             image = self.img,
                                             width = char_width*int(round(col_width)),
                                             bg = background_grey)
                    self.imgLabel.grid(row=0, column=col, sticky="w")
                    self.imgLabel.image = self.img
                    self.WeatherFrame.grid_columnconfigure(col, weight = col_weight)
                    wrow_tuple += (self.imgLabel,)
                    dark_labels.append(self.imgLabel)
                else:
                    var = tk.StringVar()
                    self.Col = tk.Label(self.WeatherFrame,
                                        font = (text_font, text_size_weather, 'bold'),
                                        anchor = 'center',
                                        borderwidth = border_width_weather,
                                        relief = "solid",
                                        bg = background_grey,
                                        width = int(round(col_width)),
                                        foreground = text_color_off_white,
                                        textvariable = var)

                    self.Col.grid(row=0, column=col, sticky="w")
                    self.WeatherFrame.grid_columnconfigure(col,
                                                           weight = col_weight)
                    wrow_tuple += (var,)
                    dark_labels.append(self.Col)
            wvars.append(wrow_tuple)
        self.wvars = wvars

        self.dark_frames = dark_frames
        self.dark_labels = dark_labels
        self.light_frames = light_frames
        self.light_labels = light_labels
        self.red_labels = red_labels
        self.night_mode = False
        self.daytime = True

        # Set update interval and go in to the Update loop
        self.TimerInterval = update_interval
        self.WeatherInterval = weather_interval
        self.WeatherDelay = 0
        self.NightModeInterval = night_mode_interval
        self.NightModeDelay = 0

        self.Update()

    def GetWeather(self):
        global forecast_hours
        try:
            json_content = page_getter.get_smhi_weather()
            now = datetime.datetime.now()
            this_hour = now.hour
            smhi_tuple = []
            found_first = False
            for item in json_content['timeSeries']:
                prognosis_time = item['validTime']
                prognosis_hr = int(re.findall('T([0-9]{2}):', prognosis_time)[0])
                if (len(smhi_tuple) < forecast_hours) and\
                   ((prognosis_hr > this_hour) or\
                    ((this_hour == 23) and (prognosis_hr == 0)) or\
                    found_first):
                    found_first = True
                    for para in item['parameters']:
                        if para['name'] == 'Wsymb2':
                            wsymb = para['values'][0]
                        elif para['name'] == 't':
                            temp = para['values'][0]
                        elif para['name'] == 'pmean':
                            rain = para['values'][0]
                        elif para['name'] == 'ws':
                            wind = int(round(para['values'][0]))
                        elif para['name'] == 'gust':
                            gust = int(round(para['values'][0]))
                    if 0 < rain < 1:
                        pass
                    else:
                        rain = int(round(rain))
                    smhi_tuple.append((str(prognosis_hr), mapWsymb2ToPng(wsymb),
                                       str(temp), str(rain), str(wind), str(gust)))
                elif len(smhi_tuple) == forecast_hours:
                    return smhi_tuple
        except KeyboardInterrupt:
            raise
        except:
            self.after(1000, self.GetWeather())

    # Update widget field with new values in a print_tuple that looks like this:
    # print_tuple = [('#', 'Destination', 'Avgår', 'Nästa', 'Läge')
                   # ('25', 'Balltorp', '8', '18', 'A'),
                   # ('52', 'Skogome', '3', '13', 'A'),
                   # ...]
    def UpdateFields(self, print_tuple):
        line = 0
        for tup in print_tuple:
            col = 0
            prev_elem = ''
            for elem in tup:
                if col == 0:
                    self.img = createPhotoImage('bus_images/' + elem + '.png')
                    self.vars[line][col].configure(image = self.img)
                    self.vars[line][col].image = self.img
                elif col == 1:
                    if (elem == 'Extrabuss') and (prev_elem == '25'):
                        elem = elem + ' Linnéplatsen'
                    self.vars[line][col].set(elem)
                else:
                    self.vars[line][col].set(elem)
                col += 1
                prev_elem = elem
            line += 1

    def UpdateWeather(self, smhi_tuple):
        # Each row in smhi_tuple represents one displayed weather column
        # Each row in self.wvars contains the labels for one displayed row
        line = 0
        for tup in smhi_tuple:
            col = 0
            wind = ''
            for elem in tup:
                if col == 0:
                    if len(elem) < 2:
                        elem = '0' + elem
                    self.wvars[col][line].set('kl ' + elem)
                elif col == 1:
                    self.img = createPhotoImage('weather_icons/' + elem + '.png')
                    self.wvars[col][line].configure(image = self.img)
                    self.wvars[col][line].image = self.img
                    pass
                elif col == 2:
                    self.wvars[col][line].set(elem + '°C')
                elif col == 3:
                    self.wvars[col][line].set(elem + ' mm')
                elif col == 4:
                    wind = elem
                elif col == 5:
                    self.wvars[col-1][line].set(wind + '(' + elem + ') m/s')

                col += 1
            line += 1

    def NightMode(self):
        daytime = self.DayTime()
        if (not daytime) and (not self.night_mode):
            # Enable Night Mode
            self.master.config(background = background_grey_night)
            for frame in self.dark_frames:
                frame.config(bg = background_grey_night)
            for label in self.dark_labels:
                label.config(bg = background_grey_night,
                             foreground = text_color_night)
            for frame in self.light_frames:
                frame.config(bg = lighter_grey_night)
            for label in self.light_labels:
                label.config(bg = lighter_grey_night,
                             foreground = text_color_night)
            for label in self.red_labels:
                label.config(bg = background_grey_night,
                             foreground = text_color_red_night)
            self.night_mode = True
        elif daytime and self.night_mode:
            # Disable Night Mode
            self.master.config(background = background_grey)
            for frame in self.dark_frames:
                frame.config(bg = background_grey)
            for label in self.dark_labels:
                label.config(bg = background_grey,
                             foreground = text_color_off_white)
            for frame in self.light_frames:
                frame.config(bg = lighter_grey)
            for label in self.light_labels:
                label.config(bg = lighter_grey,
                             foreground = text_color_off_white)
            for label in self.red_labels:
                label.config(bg = background_grey,
                             foreground = text_color_ferrari_red)
            self.night_mode = False
        else:
            pass

    def DayTime(self):
        url_prognosis = "https://www.klart.se/se/västra-götalands-län/väder-göteborg/"
        try:
            prognosis_page = page_getter.get_page_as_string(url_prognosis)
            if prognosis_page == None:
                return self.daytime
            else:
                (date, prog, sun_up, sun_down, min_temp, max_temp,
                 wind, cd, rain) = weather_parser.get_prognosis(prognosis_page)

                now = datetime.datetime.now()
                this_hour = str(now.hour)
                this_minute = str(now.minute)
                if len(this_hour) == 1: this_hour = '0' + this_hour
                if len(this_minute) == 1: this_minute = '0' + this_minute
                time = this_hour + ':' + this_minute
                self.sun_up.set('↑' + sun_up)
                self.sun_down.set('↓' + sun_down)

                if (time < sun_down < sun_up) or (sun_down < sun_up <= time):
                    # sun down is after midnight
                    self.daytime = True
                    return True
                elif (sun_up <= time < sun_down):
                    # sun down is before midnight
                    self.daytime = True
                    return True
                else:
                    self.daytime = False
                    return False
        except KeyboardInterrupt:
            raise
        except:
            return self.daytime

    # Loop that fetches all fields that continuously shall be updated
    def Update(self):
        global no_of_errors_logged
        global log_errors
        self.ErrorIndicator.set('!')
        self.update_idletasks()

        # Update Weather (less often than the bus info)
        delay_factor = math.ceil(self.WeatherInterval/self.TimerInterval)
        if (delay_factor <= self.WeatherDelay) or self.WeatherDelay == 0:
            try:
                # Update Temperature
                temperature = self.GetCurrentTemp()
                if temperature == None:
                    # TODO: Raise some kind of flag in case we don't get curr temp
                    pass
                else:
                    self.CurrentTemp = temperature
            except KeyboardInterrupt:
                raise
            except:
                self.HandleException(temperature)

            try:
                # Update Weather Forecast
                smhi_tuple = self.GetWeather()
                if smhi_tuple == None:
                    # TODO: Raise some kind of flag in case we don't get forecast
                    pass
                else:
                    self.UpdateWeather(smhi_tuple)
                self.WeatherDelay = 1
            except KeyboardInterrupt:
                raise
            except:
                self.HandleException(smhi_tuple)
        else:
            self.WeatherDelay += 1

        # Update Night Mode
        night_delay = math.ceil(self.NightModeInterval/self.TimerInterval)
        if (night_delay <= self.NightModeDelay) or self.NightModeDelay == 0:
            self.NightMode()
            self.NightModeDelay = 1
        else:
            self.NightModeDelay += 1

        # Update Bus times
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
                self.CurrTemp.set('Temp: ' + self.CurrentTemp + '°C')
                self.ErrorIndicator.set('')
                if (no_of_errors_logged > 0) and log_errors:
                    self.NrOfErrorsLogged.set(str(no_of_errors_logged))
                self.UpdateFields(print_tuple)
                self.after(self.TimerInterval, self.Update)

    def Destroy(self):
        for widget in self.winfo_children():
            widget.destroy()

    def GetCurrentTemp(self):
        try:
            url_temp = "https://www.temperatur.nu/toltorpsdalen.html"
            weather_page = page_getter.get_page_as_string(url_temp)
            temp = weather_parser.get_curr_temp(weather_page)
            return temp
        except KeyboardInterrupt:
            raise
        except:
            self.HandleException(weather_page)

    def getPrintTupleForGui(self, bus_stop):
        global backoff_factor
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
            return (stop, curr_time, print_tuple)
        except KeyboardInterrupt:
            raise
        except:
            self.HandleException(bus_stop_page)
            backoff_time = backoff_factor * update_interval
            if backoff_factor < 4:
                backoff_factor *= 2
            self.after(backoff_time, self.Update)

    def HandleException(self, error_page):
        global no_of_errors_logged
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
            error_page
        except:
            pass
        else:
            log_file.write("Web page that caused the error:\n" +
                           error_page + "\n\n")
        log_file.close()
        no_of_errors_logged += 1

class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.title('Board')
        self.attributes('-fullscreen', True)
        self.geometry(screen_res)
        self.configure(background = background_grey,
                       borderwidth = border_width,
                       relief = "solid")

        Mainframe(self).pack(fill='x', padx = 1*text_size, pady = 1*text_size)

        self.mainloop()

App()
