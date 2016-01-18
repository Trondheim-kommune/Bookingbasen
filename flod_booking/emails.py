# -*- coding: utf-8 -*-

from flask.ext.mail import Message, Mail
from flask import current_app
import os

mail = Mail()

def init_email(app):
    mail.init_app(app)

def send_fake_email(subject, sender, recipients, text_body, html_body=None):
    subject = subject.encode('utf-8')
    recipients = str(recipients).encode('utf-8')
    sender = sender.encode('utf-8')
    text_body = text_body.encode('utf-8')

    email = """
        Subject: %s
        To: %s
        From: %s
        Body: %s
        """ % (subject,
                recipients,
                sender,
                text_body
                )

    print email

def make_msg(subject, sender, recipients, text_body, html_body=None):
    # make sure recipients list does not contain None, as this will result in email not being sent.
    recipients = [x for x in recipients if x is not None]
    msg = Message(subject, sender = sender, recipients = recipients)
    msg.body = text_body
    if html_body:
        msg.html = html_body
    return msg
        
def send_real_email(subject, sender, recipients, text_body, html_body=None):
    msg = make_msg(subject, sender, recipients, text_body, html_body)
    mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body=None):
    if current_app.debug:
        send_fake_email(subject,sender,recipients,text_body,html_body)
    else:
        send_real_email(subject,sender,recipients,text_body,html_body)

def send_email_with_attached_csv(subject, sender, recipients, text_body, attachment):
    if current_app.debug:
        send_fake_email(subject, sender, recipients,
                        text_body + "\n\nAttachment: " + attachment)
    else:
        msg = make_msg(subject, sender, recipients, text_body)
        msg.attach("erv_kode.csv", "text/csv", attachment)
        mail.send(msg)
