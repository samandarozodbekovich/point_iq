from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


@shared_task
def send_registration_email(email, code):
    html_content = render_to_string(
        'authentication/activate_account.html',
        {'code': code},
    )
    msg = EmailMessage(
        subject='Activate your account',
        body=html_content,
        to=[email],
    )
    msg.content_subtype = 'html'
    msg.send()
    print('Code is send to your email address')