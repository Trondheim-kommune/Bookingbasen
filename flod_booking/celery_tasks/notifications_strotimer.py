#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime
from celery_app import celery_app
from celery.utils.log import get_task_logger
from flask import render_template, request
from emails import send_email
from flod_common.session.utils import make_superuser_auth_cookie
from os.path import abspath, dirname
import requests
import json
import time
import datetime

logger = get_task_logger(__name__)

service_base_url = os.environ.get('BOOKING_URL', "http://localhost:1337")
service_version = os.environ.get('BOOKING_VERSION', 'v1')
strotime_notifications_uri = '%s/api/%s/applications/strotime/notifications' % (service_base_url, service_version)

@celery_app.task
def send_notifications_strotimer_task():   
    send_notifications_strotimer()

def send_notifications_strotimer():
    start_time = datetime.datetime.now() + datetime.timedelta(days=1)    
    end_time = datetime.datetime.now() + datetime.timedelta(days=1, hours=1)      
    data = {
        'start_time': start_time.strftime('%Y-%m-%dT%H:00:00'),
        'end_time': end_time.strftime('%Y-%m-%dT%H:00:00')
    }

    auth_token_cookie = make_superuser_auth_cookie()
    cookies = dict(request.cookies.items() + auth_token_cookie.items())

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    
    response = requests.post(strotime_notifications_uri, data=json.dumps(data), cookies=cookies, headers=headers)    
    if response.status_code == 201:        
        strotime_slots = json.loads(response.content)
        for strotime_slot in strotime_slots:
            email_address = strotime_slot['email_address']
            resource_name = strotime_slot['resource_name']
            person_name = strotime_slot['person_name']
    
            old_date_format = '%Y-%m-%dT%H:%M:%S'                            
            new_date_format = '%Y-%m-%d %H:%M:%S'                
            start_time = datetime.datetime.strptime(strotime_slot['start_time'], old_date_format)
            start_time = start_time.strftime(new_date_format)
            end_time = datetime.datetime.strptime(strotime_slot['end_time'], old_date_format)
            end_time = end_time.strftime(new_date_format)
            if start_time is not None and \
               end_time is not None and \
               email_address is not None and \
               resource_name is not None and \
               person_name is not None:    
                    logger.info("Email address: " + email_address)
                    logger.info("Resource name: " + resource_name)                        
                    logger.info("Person name: " + person_name)                        
                    logger.info("Start time: " + start_time)                        
                    logger.info("End time: " + end_time)                        

                    message = render_template("email_strotime_notification.txt", 
                                              start_time=start_time, 
                                              end_time=end_time, 
                                              resource_name=resource_name, 
                                              person_name=person_name)                    
                    if message is not None:                        
                        logger.info(message)                        
                        send_email(u'Påminnelse på strøtime',
                                   u'booking@trondheim.kommune.no',
                                   [email_address],
                                   message)
            else:
                logger.error("Missing required data.")
