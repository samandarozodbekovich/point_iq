from celery import shared_task
from django.core.mail import EmailMessage
from django.core.management import call_command


@shared_task
def flush_expired_tokens():
    call_command('flushexpiredtokens')


@shared_task
def send_registration_email(phone_number, code):
    subject = "Activate your account"
    body = f"<p>Sizning tasdiqlash kodingiz: <b>{code}</b></p>"

    # to‘g‘ri ko‘rinish
    msg = EmailMessage(
        subject=subject,
        body=body,
        from_email="webmaster@localhost",
        to=[phone_number],
    )
    msg.content_subtype = "html"
    msg.send()
