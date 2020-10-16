# A flextime extension for timewarrior

## Installation

* copy `flextime.py` to `~/.timewarrior/extensions`
* optional: use `timew config [parameter] [value]` to set these parameters to configure the extension

    * `flextime.hours_per_day` working hours per day (default: 8)
    * `flextime.start_hours` start value of your flex time (default: 0)
    * `flextime.vacation_days_per_year` no. of your vacation days per week (default: 20)

## Usage

Show flex time report

```
timew report flextime :week

Flextime for 2020-10-12 00:00:00 - 2020-10-19 00:00:00

Day             Total   Expected       Diff
---------- ---------- ---------- ----------
2020-10-12    7:15:00    8:00:00   -1:15:00
2020-10-13    8:15:00    8:00:00    0:15:00
2020-10-14    9:15:00    8:00:00    1:15:00
2020-10-15    9:15:00    8:00:00    1:15:00
2020-10-16    8:56:46    8:00:00    0:56:46
           ---------- ---------- ----------
Total        42:56:46   40:00:00    2:56:46

Flextime:
----------
Baseline      9:18:00 
In period     2:56:46 
Sum          12:14:46 

Vacation:
----------
Total (this year)            30 
Taken in period               4 
Left*                        26*

*Left also includes vacation taken in periods that are not shown in this report.
```

Note: in this example the flextime baseline was set 9:18h and vacation days per year was set to `30`.

## Magic tags

* time ranges tagged with `flextime` do not increase tracked working time
   * if you have a whole day off add a time range marked with `flextime` to tell timew that this is a working day even though no time is tracked
* time ranges tagged with `vacation` decrease the vacation counter but do not have any effect on flex time

```
$ timew summary 20201201T000000 - 20201231T000000

Wk  Date       Day Tags       Start      End    Time    Total
W52 2020-12-21 Mon foo      7:30:00 16:00:00 8:30:00  8:30:00
W52 2020-12-22 Tue bar      7:30:00 15:30:00 8:00:00  8:00:00
W52 2020-12-23 Wed flextime 7:30:00  9:00:00 1:30:00  1:30:00
W52 2020-12-24 Thu vacation 9:00:00  9:00:00 0:00:00  0:00:00
W53 2020-12-28 Mon vacation 9:00:00  9:00:00 0:00:00  0:00:00
W53 2020-12-29 Tue vacation 9:00:00  9:00:00 0:00:00  0:00:00
W53 2020-12-30 Wed vacation 9:00:00  9:00:00 0:00:00  0:00:00
                                                             
                                                     18:00:00


$ timew report flextime 20201201T000000 - 20201231T000000
temp.report.tags:

Flextime for 2020-12-01 00:00:00 - 2020-12-31 00:00:00

Day             Total   Expected       Diff
---------- ---------- ---------- ----------
2020-12-21    8:30:00    8:00:00    0:30:00
2020-12-22    8:00:00    8:00:00    0:00:00
2020-12-23    0:00:00    8:00:00   -8:00:00
           ---------- ---------- ----------
Total        16:30:00   24:00:00   -8:30:00

Flextime:
----------
Baseline      9:18:00 
In period    -8:30:00 
Sum           1:48:00 

Vacation:
----------
Total (this year)            30 
Taken in period               4 
Left*                        26*

*Left also includes vacation taken in periods that are not shown in this report.
```
    