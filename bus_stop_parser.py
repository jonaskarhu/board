#!/usr/bin/env python3
# coding=utf-8

import re
import bus_stop_pos
import custom_exception

# Bus stop regex pattern, in one, two, or three words, accepting éæåäöÅÄÖ, e.g.:
# Östra Sjukhuset, Linnéplatsen, Jægerdorffsplatsen, Dr Fries Torg, SKF
busstop_pattern = '([A-ZÅÄÖa-zæéåäö\s]+)'

# Bus line number regex pattern, in one "word", e.g.:
# 6, 25, 761, RÖD, SVAR, 16X
# (need to be 5 chars in case of e.g. GRÖN, since Ö is of len 2)
bus_line_pattern = '([0-9A-ZÅÄÖ]{1,5})'

# Next departure pattern, e.g.:
# Nu, Kö, 2, 14, ca 10, --, Inställd
time_pattern = '([0-9\sA-ZÅÄÖa-zåäö-]+)'

def get_print_tuple(page):
    # Get Bus Stop
    stop_list = re.findall('hpl=' + busstop_pattern + ' \(', page)
    if len(stop_list) > 0:
        stop = stop_list[0]
    else:
        raise custom_exception.CustomException("Could not parse the bus stop.")

    full_list = re.findall(
        '[0-9A-F]{6}">'        + bus_line_pattern + '<\/td>' # line
        '<td>'                 + busstop_pattern  + '</td>'  # stop
        '<td class="s3">'      + time_pattern     + '</td>'  # time1
        '<td(?: class="s4")?>' + '[R\s]'          + '<\/td>' # R or space
        '<td class="s3">'      + time_pattern     + '</td>', # time2
        page)
    print_tuple = [(t + (bus_stop_pos.get_pos(t[1], stop),)) for t in full_list]

    # Get Time
    times = re.findall('([0-9]{1,2}:[0-9]{2}( )[A|P]{1}M)', page)
    time = times[0][0]
    ampm = time[len(time)-2:len(time)]
    time = time[:len(time)-3]
    [hrs, mins] = time.split(":")
    if ampm == 'AM' and hrs == '12':
        hrs = '00'
    elif ampm == 'PM' and hrs != '12':
        hrs = int(hrs); hrs += 12; hrs = str(hrs)
    if len(hrs) == 1: hrs = '0' + hrs
    curr_time = hrs + ":" + mins

    return (stop,
            curr_time,
            sorted(print_tuple, key = lambda x: x[4]))

