#!/usr/bin/env python
# -*- coding: utf-8 -*-


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
    week_day = format_week_day_for_email(slot.week_day)
    start_time = slot.start_time.strftime("%H:%M:%S")
    end_time = slot.end_time.strftime("%H:%M:%S")
    return week_day + "er: " + start_time + " - " + end_time


def format_slot_for_email(slot):
    week_day = format_week_day_for_email(int(slot.start_time.isoweekday()))
    date = slot.start_time.strftime("%Y.%m.%d")
    start_time = slot.start_time.strftime("%H:%M:%S")
    end_time = slot.end_time.strftime("%H:%M:%S")
    return week_day + " " + date + ": " + start_time + " - " + end_time


def format_application_status_for_email(application_status):
    return {
        'Granted': 'godkjent',
        'Denied': 'avvist',
        'Processing': 'under behandling'
    }[application_status]


def format_slots_for_email(slots, application_type):
    formatted_slots = []
    for slot in slots:
        if application_type == "repeating":
            formatted_slots.append(format_repeating_slot_for_email(slot))
        else:
            formatted_slots.append(format_slot_for_email(slot))
    return formatted_slots
