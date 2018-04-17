#!/usr/bin/env python3
# coding=utf-8

import re
import urllib

def get_curr_temp(page):
    # Match <span class=favoritTemp>2,8
    temp_pattern = '(-?[0-9]{1,2},[0-9])'
    temp = re.findall('<span class=favoritTemp>' + temp_pattern, page)

    return str(temp[0])
    
def degrees_to_cardinal_direction(winddir):
    if 11 < winddir <= 34:
        return 'NNO'
    elif 34 < winddir <= 56:
        return 'NO'
    elif 56 < winddir <= 79:
        return 'ONO'
    elif 79 < winddir <= 101:
        return 'O'
    elif 101 < winddir <= 124:
        return 'OSO'
    elif 124 < winddir <= 146:
        return 'SO'
    elif 146 < winddir <= 169:
        return 'SSO'
    elif 169 < winddir <= 191:
        return 'S'
    elif 191 < winddir <= 214:
        return 'SSV'
    elif 214 < winddir <= 236:
        return 'SV'
    elif 236 < winddir <= 259:
        return 'VSV'
    elif 259 < winddir <= 281:
        return 'V'
    elif 281 < winddir <= 304:
        return 'VNV'
    elif 304 < winddir <= 326:
        return 'NV'
    elif 326 < winddir <= 349:
        return 'NNV'
    else:
        return 'N'

def get_prognosis(page):
    # Get Min and Max temperatures
    temp_pattern = '\s?(-?[0-9]{1,2})'
    min_temps = re.findall('aria-label="Min temperatur">' + temp_pattern, page)
    max_temps = re.findall('aria-label="Max temperatur">' + temp_pattern, page)
    min_temp = str(min_temps[0])
    max_temp = str(max_temps[0])
    
    # Get prognosis text
    #prognosis = re.findall('aria-label="Prognos ([A-ZÅÄÖ a-zåäö]+)"', page)
    # funkar inte, konstigt...
    prognosis = re.findall('aria-label="Prognos (.+)"\s+data-qa-id=', page)
    prog = prognosis[0]

    # Get expected precipitation
    rains = re.findall('aria-label="Nederb.+rd">\s*([0-9,]{1,4})\smm\s*<\/p>',\
                       page)
    rain = str(rains[0])
    
    # Get wind speed
    # aria-label="Vind hastighet">
    winds = re.findall('aria-label="Vind hastighet">\s*([0-9]{1,3})\sm/s\s*<\/p>',\
                       page)
    wind = str(winds[0])
    
    # Get wind direction
    # aria-label="Vindriktning 0 grader"
    winddirs = re.findall('aria-label="Vindriktning\s([0-9]{1,3})\sgrader"',\
                          page)
    winddir = str(winddirs[0])
    cd = degrees_to_cardinal_direction(int(winddir))
    
    # The sun's ups and downs
    suns = re.findall('aria-label="Solens upp- och nerg.+ng">\s+([0-9]{2}:[0-9]{2})<br \/>\s+([0-9]{2}:[0-9]{2})', page)
    sun_up = str(suns[0][0])
    sun_down = str(suns[0][1])
    
    # Get date
    dates = re.findall('<time datetime="20([0-9]{2})-([0-9]{2})-([0-9]{2})T', page)
    date = dates[0][0]+dates[0][1]+dates[0][2]
    
    return (date, prog, sun_up, sun_down, min_temp, max_temp, wind, cd, rain)

def mean(numbers):
    integers = []
    for n in numbers:
        integers.append(int(n))
    return int(round(float(sum(integers)) / max(len(integers), 1), 0))

def get_temps_per_hour(page_string):
    time_pattern = 'data-qa-id="hour-day-hour" ' +\
                           'aria-label="Klockan">(.*):00\s?</time>'
    temp_pattern = '<td class="col -temp">\s*([-0-9]+).*\s*<\/td>'
    feel_pattern = '<td class="col -feelsLike">\s*([-0-9]+).*\s*<\/td>'
    res = re.findall(temp_pattern + '\s*' + feel_pattern, page_string)
    times = re.findall(time_pattern, page_string)
    t = []
    for tim in times:
        t.append(tim.replace(' ', ''))

    t_span = 6
    nr_of_spans = 3
    temp_per_hour = []
    for i in range(0, nr_of_spans):
        n = i * t_span
        span_time = str(t[n] + "-" + t[n + 6])
        span_temp = str(mean([res[n][0], res[n+1][0], res[n+2][0],
                              res[n+3][0], res[n+4][0], res[n+5][0]]))
        span_feel = str(mean([res[n][1], res[n+1][1], res[n+2][1],
                              res[n+3][1], res[n+4][1], res[n+5][1]]))
        temp_per_hour.append((span_time, span_temp, span_feel))
    return temp_per_hour