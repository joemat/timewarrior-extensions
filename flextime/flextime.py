#!/usr/bin/env python3

###############################################################################
#
# Copyright 2020, Jörg Matysiak
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# https://www.opensource.org/licenses/mit-license.php
#
###############################################################################

import datetime
import json

import sys
from dateutil import tz

FLEXTIME_MARKER_TAG = "flextime"
VACATION_MARKER_TAG = "vacation"
DEFAULT_WORKING_HOURS_PER_DAY = 8
DEFAULT_VACATION_DAYS_PER_YEAR = 20
DEFAULT_FLEXTIME_START_HOURS = 0

DATEFORMAT = "%Y%m%dT%H%M%SZ"

def format_seconds(seconds):
    """Convert seconds to a formatted string

    Convert seconds: 3661
    To formatted: "   1:01:01"
    """

    # ensure to show negative time frames correctly
    hour_factor = 1
    if seconds < 0 :
        hour_factor = -1
        seconds = - seconds

    hours = seconds // 3600
    minutes = seconds % 3600 // 60
    seconds = seconds % 60
    return "{:4d}:{:02d}:{:02d}".format(hour_factor * hours, minutes, seconds)


def has_tag(object, wantedTag):
    if "tags" not in object or object["tags"] == []:
        return False
    else:
        for tag in object["tags"]:
            if tag == wantedTag:
                return True
    return False

def calc_days(body):
    totals = dict()
    vaccation = 0;
    j = json.loads(body)
    for object in j:
        start = datetime.datetime.strptime(object["start"], DATEFORMAT)

        if "end" in object:
            end = datetime.datetime.strptime(object["end"], DATEFORMAT)
        else:
            end = datetime.datetime.utcnow()

        tracked = end - start

        day = start.strftime("%Y-%m-%d")

        if has_tag(object, FLEXTIME_MARKER_TAG):
            # add flextime with 0 tracked time => expected is counted, no working time added
            tracked = datetime.timedelta(seconds=0)

        if (has_tag(object, VACATION_MARKER_TAG)):
            # for vaccation don't add an entry in the totals array, only increase vaccation count
            # THIS WORKS ONLY FOR COMPLETE DAYS OF VACCATION!!!
            # TODO make this work for 1/2 days
            vaccation += 1
            continue;

        if day in totals:
            totals[day] += tracked
        else:
            totals[day] = tracked


    return totals, vaccation

def get_header(start, end):
    return [
        "",
        "Flextime for {:%Y-%m-%d %H:%M:%S} - {:%Y-%m-%d %H:%M:%S}".format(start, end),
        ""
    ]

def append_table_header(output, color_config, max_width):
    if color_config == "on":
        output.append("[4m{:{width}}[0m [4m{:>10}[0m [4m{:>10}[0m [4m{:>10}[0m".format("Day", "Total", "Expected", "Diff", width=max_width))
    else:
        output.append("{:{width}} {:>10} {:>10} {:>10}".format("Day", "Total", "Expected", "Diff", width=max_width))
        output.append("{} {} {} {}".format("-" * max_width, "----------", "----------", "----------"))

def append_totals_header(output, color_config, max_width):
    if color_config == "on":
        output.append("{} {} {} {}".format(" " * max_width, "[4m          [0m", "[4m          [0m", "[4m          [0m"))
    else:
        output.append("{} {} {} {}".format(" " * max_width, "----------", "----------", "----------"))

def underline(output, color_config):
    if color_config == "on":
        output.append("{}".format("[4m          [0m"))
    else:
        output.append("{}".format("----------"))


def read_input(input_stream):
    header = 1
    configuration = dict()
    body = ""
    for line in input_stream:
        if header:
            if line == "\n":
                header = 0
            else:
                fields = line.strip().split(": ", 2)
                if len(fields) == 2:
                    configuration[fields[0]] = fields[1]

                else:
                    configuration[fields[0]] = ""
                    print(fields[0])
        else:
            body += line
    return configuration, body



def from_config_or_default(configuration,name, default):
    if name in configuration:
        return configuration[name]
    return default


def calcFlexTime(input_stream):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    configuration, body = read_input(input_stream)

    working_hours_per_day = int(from_config_or_default(configuration, "flextime.hours_per_day", DEFAULT_WORKING_HOURS_PER_DAY))
    working_secs_per_day = working_hours_per_day * 60 * 60

    vacation_total = int(from_config_or_default(configuration, "flextime.vacation_days_per_year", DEFAULT_VACATION_DAYS_PER_YEAR))

    flextime_start_hours = float(from_config_or_default(configuration, "flextime.start_hours", DEFAULT_FLEXTIME_START_HOURS))
    flextime_baseline = int(flextime_start_hours * 60 * 60)

    # Sum the seconds tracked by day.
    totals, vaccation = calc_days(body)

    date_width = 10 # length of day string
 
    if "temp.report.start" not in configuration:
        return ["There is no data in the database"]

    start_utc = datetime.datetime.strptime(configuration["temp.report.start"], DATEFORMAT)
    start_utc = start_utc.replace(tzinfo=from_zone)
    start = start_utc.astimezone(to_zone)

    if "temp.report.end" in configuration:
        end_utc = datetime.datetime.strptime(configuration["temp.report.end"], DATEFORMAT)
        end_utc = end_utc.replace(tzinfo=from_zone)
        end = end_utc.astimezone(to_zone)
    else:
        end = datetime.datetime.now()

    
    output = get_header(start, end)
    
    color_config = configuration["color"]
    append_table_header(output, color_config, date_width)

    working_secs_total = 0
    expected_secs_total = 0
    for day in sorted(totals):
        seconds = int(totals[day].total_seconds())
        formatted = format_seconds(seconds)
        working_secs_total += seconds
        expected_secs_total += working_secs_per_day
        output.append("{:{width}} {:10} {:10} {:10}".format(day, formatted, format_seconds(working_secs_per_day), format_seconds(seconds - working_secs_per_day), width=date_width))

    append_totals_header(output, color_config, date_width)
   
    flextime_current = working_secs_total - expected_secs_total
    output.append("{:{width}} {:10} {:10} {:10}".format("Total", format_seconds(working_secs_total), format_seconds(expected_secs_total), format_seconds(flextime_current), width=date_width))
    output.append("")
    output.append("Flextime:")
    underline(output, color_config)
    output.append("{:{width}} {:10} ".format("Baseline", format_seconds(flextime_baseline), width=date_width))
    output.append("{:{width}} {:10} ".format("In period", format_seconds(flextime_current), width=date_width))
    output.append("{:{width}} {:10} ".format("Sum", format_seconds(flextime_baseline + flextime_current), width=date_width))

    output.append("")

    output.append("Vacation:")
    underline(output,color_config)
    output.append("{:{width}} {:10} ".format("Total (this year)", vacation_total, width=20))
    output.append("{:{width}} {:10} ".format("Taken in period", vaccation, width=20))
    output.append("{:{width}} {:10}*".format("Left*", vacation_total - vaccation, width=20))
    output.append("")
    output.append("*Left also includes vacation taken in periods that are not shown in this report.")
    
    output.append("")

    return output


if __name__ == "__main__":
    for line in calcFlexTime(sys.stdin):
        print(line)
