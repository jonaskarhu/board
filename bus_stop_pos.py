#!/usr/bin/env python3
# coding=utf-8

# Get bus position
def get_pos(stop, no, dest):
    a = 'A'
    b = 'B'
    c = 'C'
    d = 'D'
    e = 'E'
    f = 'F'
    k = 'K'
    m = 'M'
    n = 'N'
    x = 'X'
    if stop == 'Södermalmsgatan':
        if   dest == 'Balltorp':        return a
        elif dest == 'Skogome':         return a
        elif dest == 'Lindome':         return a
        elif dest == 'Mölndal':         return a
        elif dest == 'Mölndal centrum': return a
        elif dest == 'Mölndal station': return a
        elif dest == 'Länsmansgården':  return b
        elif dest == 'Linnéplatsen':    return b
        elif dest == 'Heden':           return b
        else:                           return x
    # elif stop == 'Brunnsparken':
        # if   dest == 'Östra Sjukhuset': return d # 1
        # elif dest == 'Tynnered':        return e # 1
        # elif dest == 'Högsbotorp':      return e # 2
        # elif dest == 'Mölndal':
            # if   no == '2':             return f # 2
            # elif no == '4':             return e # 4
        # elif dest == 'Marklandsgatan':
            # if   no == '3':             return c # 3
            # elif no == '16':            return e
        # elif dest == 'Kålltorp':        return d # 3
        # elif dest == 'Angered':         return f # 4
        # elif dest == 'Bergsjön':        return f # 7, 11
        # elif dest == 'Saltholmen':
            # if   no == '11':            return c
            # elif no == '114':           return k
        # elif dest == 'Länsmansgården':
            # if   no == '6':             return d
            # elif no == '5':             return b
            # elif no == '25':            return n
        # elif dest == 'Linnéplatsen':    return a
        # elif dest == 'Skogome':         return n
        # elif dest == 'Balltorp':        return m
        # elif dest == 'Eketrägatan':     return d
        # elif dest == 'Guldheden':       return a
        # elif dest == 'Biskopsgården':   return b
        # else:                           return x
    else:
        return x
