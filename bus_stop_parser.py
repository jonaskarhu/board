#!/usr/bin/env python3
# coding=utf-8

import re
import bus_stop_pos
import custom_exception

def natural_key(string_):
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

def remove_duplicates(buses):
    number_of_matches = 0
    count_list = []
    for b in buses:
        count_list.append([b, 0])
    for b1 in count_list:
        for b2 in count_list:
            if (b1[0][0] == b2[0][0]) and (b1[0][1] == b2[0][1]) and (b1[0][4] == b2[0][4]):
                b1[1] = b1[1] + 1
                number_of_matches = number_of_matches + 1

    have_duplicates = False
    if number_of_matches > len(buses):
        have_duplicates = True

    if have_duplicates:
        new_buses = []
        print("Duplicates found, remove them...")
        for b1 in count_list:
            for b2 in count_list:
                if (b1[0][0] == b2[0][0]) and (b1[0][1] == b2[0][1]) and (b1[0][4] == b2[0][4]):
                    if (b1[0][2] == b2[0][2]) and (b1[0][3] == b2[0][3]) and b1[0] not in new_buses and b1[1] == 1:
                        new_buses.append(b1[0])
                        print("adding bus without change:", b1[0])
                    elif b1[0] != b2[0]:
                        ## combine times for duplicates
                        list_of_times = [b1[0][2], b1[0][3], b2[0][2], b2[0][3]]
                        print("Times before sort:", list_of_times)
                        list_of_times = sorted(list_of_times, key=natural_key)
                        if '--' in list_of_times and len(list_of_times) > 2:
                            list_of_times.remove('--')
                            if '--' in list_of_times and len(list_of_times) > 2:
                                list_of_times.remove('--')
                        ## TODO: handle "ca" time
                        ca_list = []
                        list_of_times_temp = []
                        index = 0
                        for t in list_of_times:
                            if t[:2] == 'ca':
                                list_of_times_temp.append(t[3:])
                                ca_list.append(index)
                            else:
                                list_of_times_temp.append(t)
                            index = index + 1
                        if len(ca_list) > 0:
                            list_of_times_temp_sorted = sorted(list_of_times_temp, key=natural_key)
                            for i in ca_list:
                                j = 0
                                for t in list_of_times_temp_sorted:
                                    if t == list_of_times_temp[i]:
                                        list_of_times_temp_sorted[j] = 'ca ' + list_of_times_temp[i]
                                    j = j + 1
                            list_of_times = list_of_times_temp_sorted
                        if 'Nu' in list_of_times:
                            list_of_times.remove('Nu')
                            list_of_times.insert(0, 'Nu')
                            if 'Nu' in list_of_times[1:]:
                                list_of_times.insert(0, 'Nu')
                        print("Times after sort:", list_of_times)
                        new_bus = (b1[0][0], b1[0][1], list_of_times[0], list_of_times[1], b1[0][4])
                        if new_bus not in new_buses:
                            ## only add unique buses
                            new_buses.append(new_bus)
                            print("adding bus WITHOUT duplicate:", b1[0])
        return new_buses
    else:
        print("No duplicates found, return original!")
        return buses

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
    print_tuple = [(t + (bus_stop_pos.get_pos(stop, t[0], t[1]),)) for t in full_list]

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

    buses = remove_duplicates(sorted(print_tuple, key = lambda x: x[4]))

    return (stop,
            curr_time,
            buses)

