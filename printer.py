#!/usr/bin/env python3
# coding=utf-8

# Print Table

# Definition of column widths
widthFirstCol = 5
widthSeconCol = 23
widthThirdCol = 7
widthFourtCol = 7
widthFifthCol = 5
widthInTotal = widthFirstCol +\
               widthSeconCol +\
               widthThirdCol +\
               widthFourtCol +\
               widthFifthCol

# Print tuple elements with correct column width
def pr(val, colwidth):
    length = len(val)
    if length > colwidth-1:
        val = val[:colwidth-1]
        length = len(val)
    spacesToAdd = colwidth - length
    return val + (" " * spacesToAdd)

# Example:
# Hållplats: Södermalmsgatan     Time: 13:37
#
# #   Destination         Avgår  Nästa  Läge
# ------------------------------------------
# 25  Balltorp            Nu     14     A   
# 761 Lindome             7      ca 21  A   
# 25  Länsmansgården      6      17     B   
#
# Datum: 180320, Temp: -1,2 grader
# Prognos: Klart
# Mintemp: -4, Maxtemp: 5, Vind: 5 m/s N
# Nederbörd: 2 mm
# Soluppgång: 06:15, Solnedgång: 18:25
def print_table(stop, curr_time, line_tuple, date, curr_temp,\
                prognosis, min_t, max_t, wind, cd, rain,\
                sun_up, sun_down, temp_per_hour):
    bus_stop = "Hållplats: " + stop
    time     = "Kl: " + curr_time
    space1   = " " * (widthInTotal -\
                      len(bus_stop) -\
                      len(time))
    print("\n\n\n")
    print("{}{}{}".format(bus_stop, space1, time))
    print("")
    print("{}{}{}{}{}".format(
           pr("#", widthFirstCol),
           pr("Destination", widthSeconCol),
           pr("Avgår", widthThirdCol),
           pr("Nästa", widthFourtCol),
           pr("Läge", widthFifthCol)))
    print("-" * widthInTotal)
    for i in range(0, len(line_tuple)):
        print("{}{}{}{}{}".format(
               pr(line_tuple[i][0], widthFirstCol),
               pr(line_tuple[i][1], widthSeconCol),
               pr(line_tuple[i][2], widthThirdCol),
               pr(line_tuple[i][3], widthFourtCol),
               pr(line_tuple[i][4], widthFifthCol)))
    print("")
    degree_sign = u'\xb0'
    print("Datum: {}, Temp: {}{}C".format(date, curr_temp, degree_sign))
    print("Prognos: {}".format(prognosis))
    print("Mintemp: {}, Maxtemp: {}, Vind: {} m/s {}".format(min_t, max_t,
                                                             wind, cd))
    print("Nederbörd: {} mm".format(rain))
    print("Soluppgång: {}, Solnedgång: {}".format(sun_up, sun_down))
    print("[kl]  {}     {}     {}".format(temp_per_hour[0][0],
                                          temp_per_hour[1][0],
                                          temp_per_hour[2][0]))
    print("[°C]  {}({})     {}({})     {}({})".format(temp_per_hour[0][1],
                                                      temp_per_hour[0][2],
                                                      temp_per_hour[1][1],
                                                      temp_per_hour[1][2],
                                                      temp_per_hour[2][1],
                                                      temp_per_hour[2][2]))
