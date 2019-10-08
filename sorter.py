#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Scans a dir for files with exif data and moves the files to a new dir based
upon the exif data foud.  If no exif data is found in a file, no action is taken
upon the file
"""


import sys,os,subprocess
from pathlib import Path
import datetime
import argparse


foo="""
Date Created                    : 2016:11:22 20:00:23
File Modification Date/Time     : 2011:09:16 13:32:56-05:00
Date/Time Original              : 2011:08:25 21:02:57
GPS Date Stamp                  : 2011:11:24
GPS Date/Time                   : 2011:11:24 20:26:01Z
Modify Date                     : 2005:03:15 16:42:41
"""
def get_ymd(fn, args):
    ymd = "unknown"
    ro = subprocess.run(["exiftool", "-CreateDate", fn], capture_output=True)
    create_date = ro.stdout[34:53].decode('ascii')
    if len(create_date) == 0:
        ro = subprocess.run(["exiftool", fn], capture_output=True)
        try:
            for line in ro.stdout.decode('ascii').splitlines():
                if line.find("Date Created") != -1:
                    print(line)
                    create_date = line[34:53]
                    break
                if line.find("GPS Date/Time") != -1:
                    print(line)
                    create_date = line[34:53]
                    break
        except Exception as e:
            print("Error looking for other date {}".format(e))
        if len(create_date):
            if args.debug:
                print("Setting date to {}".format(create_date))
            subprocess.run(["exiftool", "-CreateDate={}".format(create_date), fn])
    if len(create_date):
        try:
            dt = datetime.datetime.strptime(create_date, "%Y:%m:%d")
            ymd = dt.strftime("%Y/%m/%d")
        except:
            print("Error parsing time:{}".format(create_date))
    if args.debug:
        print("{:12} {}".format(ymd, fn))
    return ymd


def process_dir(path, files, args):
    ds = os.stat(path)

    for fn in files:
        ffn = os.path.join(path, fn)
        fs = os.stat(ffn)
        ymd = get_ymd(ffn, args)
        dest_dir = os.path.join(args.dest, ymd)
        if args.copy or args.move:
            os.makedirs(dest_dir, exist_ok=True)
            if args.copy:
                subprocess.run(["cp", "-pn", ffn, dest_dir])
            else:
                subprocess.run(["mv", "-n", ffn, dest_dir])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__)

    parser.add_argument("-d", default=0, dest="debug", action="count",
        help="Increase the level of debug output.")

    parser.add_argument("-c", "--copy", default=False, action="store_true",
        help="Copy files to dest.")
    
    parser.add_argument("-m", "--move", default=False, action="store_true",
        help="Move files to dest.")
    
    parser.add_argument("--dest", required=True,
        help="Root dir to move files to.")
    
    parser.add_argument('dirs', metavar='dir', type=str, nargs='+',
        help='Directories to process.')

    args = parser.parse_args()
    if args.debug>1:
        print(args)

    # Walk all files starting at the directory root given
    for path in args.dirs:
        print("Scanning {}/".format(path))
        for path, dirs, files in os.walk(path):
            files.sort()
            process_dir(path, files, args)
