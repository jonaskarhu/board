#!/usr/bin/env python3
# coding=utf-8

import argparse
import requests
import codecs
import bus_stop_parser
import weather_parser
import printer
import time
import sys
import traceback
import custom_exception
from urllib.parse import unquote_plus
import re
import os.path

def mean(numbers):
    integers = []
    for n in numbers:
        integers.append(int(n))
    return round(float(sum(integers)) / max(len(integers), 1), 1)

def replace_utf8_chars(s):
    return s.replace('%c3%a5','å')\
            .replace('%c3%a4','ä')\
            .replace('%c3%b6','ö')\
            .replace('%c3%85','Å')\
            .replace('%c3%84','Ä')\
            .replace('%c3%96','Ö')\
            .replace('%c3%a9','é')\
            .replace('%c3%a6','æ')\
            .replace('+',' ')

def get_page_as_string(url):
    page_obj = requests.get(url)
    unicode_str = page_obj.text
    return replace_utf8_chars(unicode_str)

def get_bus_stop_page(bus_stop):
    return get_bus_stop_page_help(bus_stop, 1, "")

def get_bus_stop_page_help(bus_stop, page_no, page_acc):
    # Get the page of the bus stop that is requested
    url = "http://wap.vasttrafik.se/MobileQuery.aspx?hpl=" +\
          bus_stop +\
          "+(Göteborg)&pg=" + str(page_no) + "&lang=sv"
    page = get_page_as_string(url)

    # Check if there is another page
    #page = unquote_plus(utf8string)
    res = re.findall('Fler avg', page)

    # Return or loop
    if res == []:
        # If there are no more pages, return the appended string
        return page_acc + page
    else:
        # If there is another page, recursively loop and append
        return get_bus_stop_page_help(bus_stop, page_no + 1, page_acc + page)

url_temp = "https://www.temperatur.nu/toltorpsdalen.html"
url_prognosis = "https://www.klart.se/se/västra-götalands-län/väder-göteborg/"

def get_logfile(no_of_errors_logged, no_of_errors_to_save):
    if no_of_errors_logged >= no_of_errors_to_save:
        error_log_to_remove = "error_" +\
                              str(no_of_errors_logged + 1
                                  - no_of_errors_to_save) +\
                              ".log"
        if os.path.exists(error_log_to_remove):
            os.remove(error_log_to_remove)
    return "error_" + str(no_of_errors_logged + 1) + ".log"

# Main start
def main(bus_stop):
    update_interval = 15 # sec
    backoff_factor = 1
    no_of_errors_logged = 0
    no_of_errors_to_save = 3
    while(1):
        # Ensure that html page can be fetched, otherwise
        # log the fault to an error.log file and
        # backoff for an increasing amount of time
        try:
            page = get_bus_stop_page(bus_stop)

            # Get bus information
            (stop,
             curr_time,
             print_tuple) = bus_stop_parser.get_print_tuple(page)

            # Get actual temperature
            weather_page = requests.get(url_temp)
            temp = weather_parser.get_curr_temp(weather_page.text)

            # Get weather prognosis
            prognosis_page = requests.get(url_prognosis)
            (date, prog,
             sun_up, sun_down,
             min_temp, max_temp,
             wind, cd, rain) = weather_parser.get_prognosis(
                                 prognosis_page.text)

            # Print board and sleep
            printer.print_table(stop, curr_time, print_tuple, date, temp,
                                prog, min_temp, max_temp, wind, cd, rain,
                                sun_up, sun_down)

            rain_url = 'https://www.klart.se/se/'\
                       'v%C3%A4stra-g%C3%B6talands-l%C3%A4n/'\
                       'v%C3%A4der-g%C3%B6teborg/timmar/'
            rain_page = get_page_as_string(rain_url)

            # Check if there is another page
            time_pattern = 'data-qa-id="hour-day-hour" ' +\
                           'aria-label="Klockan">(.*):00\s?</time>'
            temp_pattern = '<td class="col -temp">\s*([-0-9]+).*\s*<\/td>'
            feel_pattern = '<td class="col -feelsLike">\s*([-0-9]+).*\s*<\/td>'
            res = re.findall(temp_pattern +
                             '\s*' +
                             feel_pattern,
                             rain_page)
            times = re.findall(time_pattern,
                               rain_page)

            t = []
            for tim in times:
                t.append(tim.replace(' ', ''))
            degree_sign = u'\xb0'
            t_span = 6
            for i in range(0, 3):
                n = i * t_span
                print(u"{}-{}: Temp: {}{}C, Känns som: {}{}C".format(
                      t[n], t[n + 6],
                      str(mean([res[n][0], res[n+1][0], res[n+2][0],
                                res[n+3][0], res[n+4][0], res[n+5][0]])),
                      degree_sign,
                      str(mean([res[n][1], res[n+1][1], res[n+2][1],
                                res[n+3][1], res[n+4][1], res[n+5][1]])),
                      degree_sign))
            #break
            time.sleep(update_interval)
        except KeyboardInterrupt:
            break
        except:
            log_file_path = get_logfile(no_of_errors_logged,
                                        no_of_errors_to_save)
            log_file = open(log_file_path, "a")
            now = time.strftime("%Y-%m-%d %H:%M:%S UTC+1", time.gmtime())
            exception = "Unexpected exception:" + str(sys.exc_info())
            log_file.write("ERROR[" + now + "]:" +  exception + "\n")
            print("logged error to file:", log_file_path)
            log_file.write(traceback.format_exc())
            try:
                page
            except:
                pass
            else:
                log_file.write("Web page that caused the error:\n" +
                               page + "\n\n")
            log_file.close()
            no_of_errors_logged += 1

            time.sleep(update_interval * backoff_factor)
            if backoff_factor < 4:
                backoff_factor *= 2
            continue
        backoff_factor = 1

# Parse input
parser = argparse.ArgumentParser()
parser.add_argument("bus_stop")
args = parser.parse_args()

main(args.bus_stop)

