#!/usr/bin/env python3
# coding=utf-8

import vasttrafik_api
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
    jp = vasttrafik_api.JourneyPlanner(
        key=secrets.get_key(),
        secret=secrets.get_secret())
    try:
        sodermalmsgatan = 'Södermalmsgatan, Göteborg'
        stops = jp.location_name(sodermalmsgatan)
        for stop in stops:
            if stop['name'] == sodermalmsgatan:
                sodermalmsgatan_id = stop['id']
    except KeyboardInterrupt:
        raise
    except KeyError:
        sodermalmsgatan_id = '9021014006630000'
    #raise ValueError('test')
    departure_board = jp.departureboard(sodermalmsgatan_id, time_span=99,
                                        max_departures_per_line=3)
    #raw=[]
    buses={}
    for d in departure_board:
        is_realtime = False
        try:
            time = get_time_to_departure(d['rtTime']) # type(time): int
            is_realtime = True
        except KeyError:
            time = get_time_to_departure(d['time'])   # type(time): int
        except:
            raise
        #raw.append((d['sname'], d['direction'], time, d['track'], is_realtime))
        bus_no = d['sname']
        destination = d['direction']
        bus = bus_no + ' ' + destination
        position = d['track']

        if bus not in buses:
            # First unique bus
            buses[bus] = {'next1':{'time':time, 'isrt':is_realtime},
                          'next2':{'time':'', 'isrt':''},
                          'next3':{'time':'', 'isrt':''},
                          'position':position}
        elif buses[bus]['next2']['time'] == '':
            # Second occurence of the same bus, should be the nextnext time
            buses[bus]['next2']['time'] = time
            buses[bus]['next2']['isrt'] = is_realtime
        elif buses[bus]['next3']['time'] == '':
            # Third occurence of the same bus, should be the nextnextnext time
            buses[bus]['next3']['time'] = time
            buses[bus]['next3']['isrt'] = is_realtime
        else:
            # Should never get here.
            pass
        # Sorting not needed since they arrive in order from the API,
        # but save this sorting algorithm if I notice that the API
        # doesn't behave all the time.
        #else:
            # Not unique bus, determine which times to keep
            #if buses[bus]['next2']['time'] == '':
            #    if time > buses[bus]['next1']['time']:
            #        buses[bus]['next2']['time'] = time
            #        buses[bus]['next2']['isrt'] = is_realtime
            #    elif time < buses[bus]['next1']['time']:
            #        buses[bus]['next2']['time'] = buses[bus]['next1']['time']
            #        buses[bus]['next2']['isrt'] = buses[bus]['next1']['isrt']
            #        buses[bus]['next1']['time'] = time
            #        buses[bus]['next1']['isrt'] = is_realtime
            #    else:
            #        if buses[bus]['next1']['isrt']:
            #            buses[bus]['next2']['time'] = time
            #            buses[bus]['next2']['isrt'] = is_realtime
            #        elif is_realtime:
            #            buses[bus]['next2']['time'] = buses[bus]['next1']['time']
            #            buses[bus]['next2']['isrt'] = buses[bus]['next1']['isrt']
            #            buses[bus]['next1']['time'] = time
            #            buses[bus]['next1']['isrt'] = is_realtime
            #        else:
            #            buses[bus]['next2']['time'] = time
            #            buses[bus]['next2']['isrt'] = is_realtime

    tuple_list=[]
    for bus in buses:
        # Next
        if buses[bus]['next1']['time'] < 1:
            buses[bus]['next1']['time'] = 'Nu'
        if not buses[bus]['next1']['isrt']:
            buses[bus]['next1']['time'] = 'ca ' + str(buses[bus]['next1']['time'])
        if not isinstance(buses[bus]['next1']['time'], str):
            buses[bus]['next1']['time'] = str(buses[bus]['next1']['time'])

        # Nextnext
        if buses[bus]['next2']['time'] != '':
            if buses[bus]['next2']['time'] < 1:
                buses[bus]['next2']['time'] = 'Nu'
            if not buses[bus]['next2']['isrt']:
                buses[bus]['next2']['time'] = 'ca ' + str(buses[bus]['next2']['time'])
            if not isinstance(buses[bus]['next2']['time'], str):
                buses[bus]['next2']['time'] = str(buses[bus]['next2']['time'])

        # Nextnextnext
        if buses[bus]['next3']['time'] != '':
            if buses[bus]['next3']['time'] < 1:
                buses[bus]['next3']['time'] = 'Nu'
            if not buses[bus]['next3']['isrt']:
                buses[bus]['next3']['time'] = 'ca ' + str(buses[bus]['next3']['time'])
            if not isinstance(buses[bus]['next3']['time'], str):
                buses[bus]['next3']['time'] = str(buses[bus]['next3']['time'])

        line = bus[:bus.index(' ')]
        dest = bus[bus.index(' ')+1:]
        next = buses[bus]['next1']['time']
        nextnext = buses[bus]['next2']['time']
        nextnextnext = buses[bus]['next3']['time']
        pos = buses[bus]['position']
        tuple_list.append((line, dest, next, nextnext, nextnextnext, pos))

    print_tuple = sorted(sorted(tuple_list, key = lambda x: x[0]), key = lambda x: x[5])
    head = ('#', 'Destination', 'Avgår', 'Nästa', 'Sedan', 'Läge')
    print_tuple.insert(0, head)
    now = datetime.datetime.now()
    hour = str(now.hour)
    min = str(now.minute)
    if len(hour) < 2:
        hour = '0' + hour
    if len(min) < 2:
        min = '0' + min
    #print("RAW:")
    #for r in raw:
    #    print(r)
    #print("OUTPUT:")
    #for p in print_tuple:
    #    print(p)
    return('Södermalmsgatan', hour + ":" + min, print_tuple)
