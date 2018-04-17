#!/usr/bin/env python3
# coding=utf-8

import re

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