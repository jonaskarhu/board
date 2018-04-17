#!/usr/bin/env python3
# coding=utf-8

# Parse cli input
import argparse

# Import other modules
import page_getter
import bus_stop_parser
import weather_parser
import printer
import custom_exception

# Misc system imports
import time
import sys
import traceback
import os.path

def get_logfile(no_of_errors_logged, no_of_errors_to_save):
    if no_of_errors_logged >= no_of_errors_to_save:
        error_log_to_remove = "error_" +\
                              str(no_of_errors_logged + 1
                                  - no_of_errors_to_save) +\
                              ".log"
        if os.path.exists(error_log_to_remove):
            os.remove(error_log_to_remove)
    return "error_" + str(no_of_errors_logged + 1) + ".log"

# urls
url_temp = "https://www.temperatur.nu/toltorpsdalen.html"
url_prognosis = "https://www.klart.se/se/västra-götalands-län/väder-göteborg/"
url_hr_by_hr = "https://www.klart.se/se/v%C3%A4stra-g%C3%B6talands-l%C3%A4n/"\
               "v%C3%A4der-g%C3%B6teborg/timmar/"

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
            # Get bus information
            bus_stop_page = page_getter.get_bus_stop_page(bus_stop)
            (stop,
             curr_time,
             print_tuple) = bus_stop_parser.get_print_tuple(bus_stop_page)

            # Get actual temperature
            weather_page = page_getter.get_page_as_string(url_temp)
            temp = weather_parser.get_curr_temp(weather_page)

            # Get weather prognosis
            prognosis_page = page_getter.get_page_as_string(url_prognosis)
            (date, prog,
             sun_up, sun_down,
             min_temp, max_temp,
             wind, cd, rain) = weather_parser.get_prognosis(prognosis_page)

            # Get hour by hour temperature prognosis
            hr_by_hr_page = page_getter.get_page_as_string(url_hr_by_hr)
            temp_per_hour = weather_parser.get_temps_per_hour(hr_by_hr_page)

            # Print board and sleep
            printer.print_table(stop, curr_time, print_tuple, date, temp,
                                prog, min_temp, max_temp, wind, cd, rain,
                                sun_up, sun_down, temp_per_hour)
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
                bus_stop_page
            except:
                pass
            else:
                log_file.write("Web page that caused the error:\n" +
                               bus_stop_page + "\n\n")
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

