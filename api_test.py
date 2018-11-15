#!/usr/bin/env python3

import vasttrafik_api

jp = vasttrafik_api.JourneyPlanner(
    key='J7WW1diMol9n08iSjPY1tStuArsa',
    secret='z2Kkb6Poa7GrXK0DYbhIVcmFinga')

print(str(jp))
#print(jp.location_allstops())
sodermalmsgatan_id = jp.location_name('Södermalmsgatan, Göteborg')[0]['id']
print(sodermalmsgatan_id)

dep_board=jp.departureboard(stop_id=sodermalmsgatan_id, time_span=180, max_departures_per_line=2)
dep_board = sorted(sorted(dep_board, key = lambda x: x['track']), key = lambda x: x['sname'])
index=0
for i in dep_board:
    #print(i)
    print(i['sname'], i['direction'], i['rtTime'], i['track'])
    index = index + 1

print(index, "number of buses")
