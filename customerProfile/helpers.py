from distutils import config
import re



from common.exceptions import CustomBadRequest
from common.messages import PASSWORD_LENGTH_SHOULD_BE_BETWEEN_8_TO_20, \
    PASSWORD_MUST_HAVE_ONE_NUMBER, PASSWORD_MUST_HAVE_ONE_SMALLERCASE_LETTER, PASSWORD_MUST_HAVE_ONE_UPPERCASE_LETTER, \
    PASSWORD_MUST_HAVE_ONE_SPECIAL_CHARACTER
from django.core import mail


def validate_password(password):
    specialCharacters = r"[\$#@!\*]"
    if len(password) < 6:
        return CustomBadRequest(message=PASSWORD_LENGTH_SHOULD_BE_BETWEEN_8_TO_20)
    if len(password) > 20:
        return CustomBadRequest(message=PASSWORD_LENGTH_SHOULD_BE_BETWEEN_8_TO_20)
    elif re.search('[0-9]', password) is None:
        return CustomBadRequest(message=PASSWORD_MUST_HAVE_ONE_NUMBER)
    elif re.search('[a-z]', password) is None:
        return CustomBadRequest(message=PASSWORD_MUST_HAVE_ONE_SMALLERCASE_LETTER)
    elif re.search('[A-Z]', password) is None:
        return CustomBadRequest(message=PASSWORD_MUST_HAVE_ONE_UPPERCASE_LETTER)
    elif re.search(specialCharacters, password) is None:
        return CustomBadRequest(message=PASSWORD_MUST_HAVE_ONE_SPECIAL_CHARACTER)
    else:
        return True

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = config('dhruvilphotos06@gmail.com')
# EMAIL_HOST_PASSWORD = config('Dna@182601')
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_USE_SSL = False
def send_mail(email, msg):
    with mail.get_connection() as connection:
        mail.EmailMessage(
            "OTP verification for password change",
            msg,
            "dhruvilphotos06@gmail.com",
            email,
            connection=connection,
        ).send()