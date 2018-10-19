#!/usr/bin/env python3
# coding=utf-8

import vasttrafik
import secrets
import datetime

def get_time_to_departure(absolute_time):
    departure_hour = int(absolute_time[:2])
    departure_minute = int(absolute_time[3:])
    now = datetime.datetime.now()
    # TODO: Handle midnight more reasonably ;-)
    if 0 <= departure_hour <= 5 and 18 <= now.hour <= 23:
        departure_hour = 24
    time_to_departure = 60*(departure_hour - now.hour) + departure_minute - now.minute
    return time_to_departure

def get_print_tuple():
    jp = vasttrafik.JournyPlanner(
        key=secrets.get_key(),
        secret=secrets.get_secret())

    sodermalmsgatan_id = jp.location_name('Södermalmsgatan, Göteborg')[0]['id']
    departure_board = jp.departureboard(sodermalmsgatan_id)
    #raw=[]
    buses={}
    for d in departure_board:
        is_realtime = False
        try:
            time = get_time_to_departure(d['rtTime'])
            is_realtime = True
        except KeyError:
            time = get_time_to_departure(d['time'])
        except:
            raise
        #raw.append((d['sname'], d['direction'], time, d['track'], is_realtime))
        bus_no = d['sname']
        destination = d['direction']
        bus = bus_no + ' ' + destination
        position = d['track']

        if bus not in buses:
            # First unique bus
            buses[bus] = {'next':{'time':time, 'isrt':is_realtime},
                          'nextnext':{'time':'', 'isrt':''},
                          'position':position}
        else:
            # Not unique bus, determine which times to keep
            if buses[bus]['nextnext']['time'] == '':
                if time > buses[bus]['next']['time']:
                    buses[bus]['nextnext']['time'] = time
                    buses[bus]['nextnext']['isrt'] = is_realtime
                elif time < buses[bus]['next']['time']:
                    buses[bus]['nextnext']['time'] = buses[bus]['next']['time']
                    buses[bus]['nextnext']['isrt'] = buses[bus]['next']['isrt']
                    buses[bus]['next']['time'] = time
                    buses[bus]['next']['isrt'] = is_realtime
                else:
                    if buses[bus]['next']['isrt']:
                        buses[bus]['nextnext']['time'] = time
                        buses[bus]['nextnext']['isrt'] = is_realtime
                    elif is_realtime:
                        buses[bus]['nextnext']['time'] = buses[bus]['next']['time']
                        buses[bus]['nextnext']['isrt'] = buses[bus]['next']['isrt']
                        buses[bus]['next']['time'] = time
                        buses[bus]['next']['isrt'] = is_realtime
                    else:
                        buses[bus]['nextnext']['time'] = time
                        buses[bus]['nextnext']['isrt'] = is_realtime

    tuple_list=[]
    for bus in buses:
        if buses[bus]['next']['time'] < 1:
            buses[bus]['next']['time'] = 'Nu'
        if not buses[bus]['next']['isrt']:
            buses[bus]['next']['time'] = 'ca ' + str(buses[bus]['next']['time'])
        if buses[bus]['nextnext']['time'] != '':
            if buses[bus]['nextnext']['time'] < 1:
                buses[bus]['nextnext']['time'] = 'Nu'
            if not buses[bus]['nextnext']['isrt']:
                buses[bus]['nextnext']['time'] = 'ca ' + str(buses[bus]['nextnext']['time'])

        line = bus[:bus.index(' ')]
        dest = bus[bus.index(' ')+1:]
        next = buses[bus]['next']['time']
        nextnext = buses[bus]['nextnext']['time']
        pos = buses[bus]['position']
        tuple_list.append((line, dest, next, nextnext, pos))

    print_tuple = sorted(sorted(tuple_list, key = lambda x: x[0]), key = lambda x: x[4])
    head = ('#', 'Destination', 'Avgår', 'Nästa', 'Läge')
    print_tuple.insert(0, head)
    now = datetime.datetime.now()
    hour = str(now.hour)
    min = str(now.minute)
    if len(hour) < 2:
        hour = str.insert(0, '0')
    if len(min) < 2:
        min = str.insert(0, '0')
    #print("RAW:")
    #for r in raw:
    #    print(r)
    #print("OUTPUT:")
    #for p in print_tuple:
    #    print(p)
    return('Södermalmsgatan', hour + ":" + min, print_tuple)
