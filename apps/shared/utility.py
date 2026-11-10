import re
from twilio.rest import Client
from rest_framework.exceptions import ValidationError


email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
phone_regex = re.compile(r'^\+?[1-9]\d{7,14}$')
username_regex = re.compile(r"^[a-zA-Z0-9_.-]+$")

def check_email_or_phone(email_or_phone):
    if re.fullmatch(phone_regex,email_or_phone):
        email_or_phone = 'phone'
    elif re.fullmatch(email_regex,email_or_phone):
        email_or_phone = 'email'
    else:
        raise ValidationError({
            'success':False,
            'message':'Invalid email or phone number'
        })
    return email_or_phone


def check_user_type(user_input):

    if re.fullmatch(email_regex, user_input):
        user_input = 'email'
    elif re.fullmatch(phone_regex, user_input):
        user_input = 'phone'
    elif re.fullmatch(username_regex, user_input):
        user_input = 'username'
    else:
        data = {
            'secces':False,
            'message':'Invalid username, phone number or email address'
            }
        raise ValidationError(data)
    return user_input