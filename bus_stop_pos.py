#!/usr/bin/env python3
# coding=utf-8

# Get bus position
def get_pos(dest, stop):    
    a = 'A'
    b = 'B'
    q = 'X'
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
        else:                           return q
    else:
        return q
