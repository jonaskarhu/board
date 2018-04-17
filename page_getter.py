#!/usr/bin/env python3
# coding=utf-8

import requests
import re

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
    # url hardcoded here so it can be modified easily
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