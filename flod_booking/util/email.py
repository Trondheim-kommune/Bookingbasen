#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

def format_week_day_for_email(week_day):    
    return {
        1: 'Mandag',
        2: 'Tirsdag',
        3: 'Onsdag',
        4: 'Torsdag',
        5: 'Fredag',
        6: u'Lørdag',
        7: u'Søndag'
    }[week_day]

def format_repeating_slot_for_email(slot):
    week_day =  format_week_day_for_email(slot.week_day)
    start_time = slot.start_time.strftime("%H:%M:%S")
    end_time = slot.end_time.strftime("%H:%M:%S")
    return week_day + "er: " + start_time + " - " + end_time

def format_slot_for_email(slot):
    week_day = format_week_day_for_email(int(slot.start_time.isoweekday()))
    date =  slot.start_time.strftime("%Y.%m.%d")
    start_time = slot.start_time.strftime("%H:%M:%S")
    end_time = slot.end_time.strftime("%H:%M:%S")
    return week_day + " " + date + ": " + start_time + " - " + end_time
