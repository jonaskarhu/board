#!/usr/bin/env python3
# coding=utf-8
import json
import requests
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning

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

def get_temperatur_nu_temp():
    temperatur_nu_endpoint = 'http://api.temperatur.nu/tnu_1.17.php'
    params = {
        'lat' : '57.677739',
        'lon' : '11.971323',
        'cli' : 'karhu_app'
    }
    response = requests.get(temperatur_nu_endpoint, params=params)
    #response = '{"full_exec_time":0.01783299446105957,"title":"Temperatur.nu API 1.17","client":"unsigned","stations":[{"title":"Göteborg/Högsbo","id":"hogsbo","temp":"15.3","dist":"2.5"}]}'
    json_obj = json.loads(response.text)
    temp = '-'
    try:
        for station in json_obj['stations']:
            try:
                temp = str(station['temp']).replace('.', ',')
                break
            except:
                pass
    except:
        pass
    return temp

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

def get_smhi_weather():
    base_url = 'https://opendata-download-metfcst.smhi.se/'
    api = 'api/category/pmp3g/version/2/'   # API version
    geo = 'geotype/point/'                  # Point or Grid
    lon = 'lon/11.934536/';                 # Longitude
    lat = 'lat/57.690638/';                 # Latitude
    fmt = 'data.json';                      # Response Format (json, xml, csv)
    url = base_url+api+geo+lon+lat+fmt

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    # verify=False since SMHI's API does not have correct ssl settings
    res = requests.get(url, verify=False)
    return res.json()
