import re
from django.shortcuts import render
from django.core.mail import get_connection, EmailMessage

from common.constants import PASSWORD_LENGTH_SHOULD_BE_BETWEEN_8_TO_20, PASSWORD_MUST_HAVE_ONE_NUMBER, PASSWORD_MUST_HAVE_ONE_SMALLERCASE_LETTER, PASSWORD_MUST_HAVE_ONE_SPECIAL_CHARACTER, PASSWORD_MUST_HAVE_ONE_UPPERCASE_LETTER
from exceptions.generic import CustomBadRequest
# Create your views here.
def send_mail(email, msg):
    with get_connection() as connection:
        email_message = EmailMessage(
            subject="OTP verification for password change",
            body=msg,
            from_email="dhruvilphotos06@gmail.com",
            to=email,
            connection=connection,
        )
        email_message.send()

def validate_password(password):
    special_characters = r"[\$#@!\*]"
    print("open",password)
    print(len(password))
    if len(password) < 6:
        print("THIS")
        return CustomBadRequest(message=PASSWORD_LENGTH_SHOULD_BE_BETWEEN_8_TO_20)
    if len(password) > 20:
        return CustomBadRequest(message=PASSWORD_LENGTH_SHOULD_BE_BETWEEN_8_TO_20)
    if re.search('[0-9]', password) is None:
        return CustomBadRequest(message=PASSWORD_MUST_HAVE_ONE_NUMBER)
    if re.search('[a-z]', password) is None:
        return CustomBadRequest(message=PASSWORD_MUST_HAVE_ONE_SMALLERCASE_LETTER)
    if re.search('[A-Z]', password) is None:
        return CustomBadRequest(message=PASSWORD_MUST_HAVE_ONE_UPPERCASE_LETTER)
    if re.search(special_characters, password) is None:
        return CustomBadRequest(message=PASSWORD_MUST_HAVE_ONE_SPECIAL_CHARACTER)
    else:
        return True
    