from emails import send_email, send_email_with_attached_csv
from celery_app import celery_app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@celery_app.task
def send_email_task(subject, sender, recipients, text_body, html_body=None):    
    send_email(subject, sender, recipients, text_body, html_body)

@celery_app.task
def send_email_with_csv_task(subject, sender, recipients, text_body, attachment):
    send_email_with_attached_csv(subject, sender, recipients, text_body, attachment)
