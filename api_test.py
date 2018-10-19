#!/usr/bin/env python3

import vasttrafik

jp = vasttrafik.JournyPlanner(
    key='J7WW1diMol9n08iSjPY1tStuArsa',
    secret='z2Kkb6Poa7GrXK0DYbhIVcmFinga')

print(str(jp))
#print(jp.location_allstops())
sodermalmsgatan_id = jp.location_name('Södermalmsgatan, Göteborg')[0]['id']
print(sodermalmsgatan_id)

dep_board=jp.departureboard(sodermalmsgatan_id)
for i in dep_board:
    print(i)
    print(i['sname'], i['direction'], i['rtTime'], i['track'])

