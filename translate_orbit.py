#! /bin/python3

"""Reads satellite data from http://celestrak.com/NORAD/elements/, spits out an ssc formatted text, suitable for Celestia"""

# translate_orbit is based on Grant Hutchinson's excel spreadsheet: https://www.classe.cornell.edu/~seb/celestia/hutchison/spreadsheets.html

from math import floor
from urllib.request import urlopen
import urllib
import sys
import argparse

# Maps from a category name to an URI containing the text file
categories = {}
URI_BASE = "http://celestrak.com/NORAD/elements/"

def __get_categories():
    """Reads the base URL and extracts the categories."""
    startmarker = '<a href=\"'
    f = urllib.request.urlopen(URI_BASE)
    myfile = str(f.read())
    start = 0
    while(start >= 0):
        start = myfile.find(startmarker,start)
        if start >= 0:
            start = start+len(startmarker)
            end = myfile.find("\">",start)
            link = myfile[start:end]
            # Ignore links with unwanted symbols
            if link.find(" ") < 0 and link.find("@") < 0 and link.find("#") < 0:
                # Ignore links we know are useless
                if not link == "master.php":
                    # Ignore anything with a slash that isn't a satscat link:
                    if not (link.find("satcat") < 0 and link.find("/")>=0):
                        name = link.replace(".txt","")
                        name = name.replace(".php","")
                        name = name.replace("/satcat/","")
                        categories[name]=URI_BASE+link


def list_categories():
    """List all available categories"""
    if(len(categories)==0):
        __get_categories()
    for cat in categories:
        print(cat)

def list_spacecraft(category):
    """List all spacecraft in a given category."""
    if(len(categories)==0):
        __get_categories()
    link = categories[category]
    f = urllib.request.urlopen(link)
    linecount = 0
    for line in f:
        line = line.decode('utf-8').strip()
        # Every third line is a spacecraft
        if linecount%3 == 0:
            print(line)
        linecount = linecount + 1

def __get_tle(category,spacecraft):
    """Return the two-line element set for the given category and spacecraft"""
    if(len(categories)==0):
        __get_categories()
    link = categories[category]
    f = urllib.request.urlopen(link)
    linecount = 0
    found = False
    res1 = None
    res2 = None
    for line in f:
        line = line.decode('utf-8').strip()
        # Every third line is a spacecraft
        if linecount%3 == 0 and line == spacecraft:
            found = True
        elif found and res1 is None:
            res1 = line
        elif found and res1 is not None and res2 is None:
            res2 = line
            break
    return res1,res2


def calculate_epoch(line1):
    epoch_year = float(line1[18:20].strip())
    if epoch_year <= 56:
        epoch_year = 2000+epoch_year
    else:
        epoch_year = 1900+epoch_year
    epoch_day = float(line1[20:32].strip())
    return 1721424.5 - floor((epoch_year - 1) / 100) + floor((epoch_year - 1) / 400) + floor(365.25 * (epoch_year - 1)) + epoch_day

def calculate_period(line2):
    return 1.0/float(line2[52:64])


def caluculate_semimajor_axis(line2):
    return pow(pow(calculate_period(line2),2)*75371000000000,0.33333333333333333)


def calculate_eccentricity(line2):
    return float('0.'+line2[26:33].strip())


def calculate_inclination(line2):
    return float(line2[8:16].strip())


def calculate_ascending_node(line2):
    return float(line2[17:25].strip())


def calculate_arg_of_pericenter(line2):
    return float(line2[34:42].strip())


def calculate_mean_anomaly(line2):
    return float(line2[43:51].strip())


def calculate_roation_offset(line1,line2):
    epoch_day = float(line1[20:32].strip())
    period = calculate_period(line2)
    daydiff = 2451545-epoch_day
    tmp = calculate_arg_of_pericenter(line2) + calculate_mean_anomaly(line2)
    return (tmp +360 * (((daydiff / period - floor(daydiff / period))))) % 360


def do_translate(category, spacecraft, mesh=None, radius = None, orientation = None):
    """Reads in the category, finds the spacecraft, and does translation"""
    line1,line2 = __get_tle(category,spacecraft)
    print("# Generated by orbit_translate python module version 1.0")
    print("# Based on data from http://celestrak.com/NORAD/elements/")
    print("")
    print('"'+spacecraft+'" "Sol/Earth" {')
    print('  Class "spacecraft"')
    if mesh is not None:
        print('  Mesh "'+mesh +'"')
    if radius is not None:
        print('  Radius ' + str(radius))
    print('  EllipticalOrbit{')
    print('    Epoch ' + str(calculate_epoch(line1)))
    print('    Period ' + str(calculate_period(line2)))
    print('    SemiMajorAxis ' + str(caluculate_semimajor_axis(line2)))
    print('    Eccentricity ' + str(calculate_eccentricity(line2)))
    print('    Inclination ' + str(calculate_inclination(line2)))
    print('    AscendingNode ' + str(calculate_ascending_node(line2)))
    print('    ArgOfPericenter ' + str(calculate_arg_of_pericenter(line2)))
    print('    MeanAnomaly ' + str(calculate_mean_anomaly(line2)))
    print('  }')
    print('  Obliquity ' + str(calculate_inclination(line2)))
    print('  EquatorAscendingNode '+ str(calculate_ascending_node(line2)))
    print('  RotationOffset ' + str(calculate_roation_offset(line1,line2)))
    if orientation is not None:
        print('  Orientation '+orientation.replace('\"',''))
    print('}')

parser = argparse.ArgumentParser(description="A program to generate Celestia-compatible ssc from ELT scraped from the internet. Run without parameters to list available categories.")
parser.add_argument("-c",help="the category we want to use. If no -s argument is given, list all spacecraft in that category.")
parser.add_argument("-s",help="the spacecraft we want to use. Requires use of -c argument.")
parser.add_argument("-m",help="Optional: the mesh to use")
parser.add_argument("-r",help="Optional, numeric: the radius of the object in kilometres.")
parser.add_argument("-o",help="Optional: the orientation to use, format: \"[ a b c d ]\", where a is in degrees, b, c and d are the components of the rotation axis." )
parsed_args = parser.parse_args()

if parsed_args.c is None and parsed_args.s is None:
    print("Available categories:")
    list_categories()
elif parsed_args.c is not None and parsed_args.s is None:
    print('Available spacecraft in "'+parsed_args.c+'":')
    list_spacecraft(parsed_args.c)
elif parsed_args.c is not None and parsed_args.s is not None:
    do_translate(parsed_args.c,parsed_args.s,parsed_args.m,parsed_args.r,parsed_args.o)
elif parsed_args.c is None and parsed_args.s is not None:
    print("You must specify the category using the -c switch. To list available categories, run program without any arguments. Use -h switch for help.")

