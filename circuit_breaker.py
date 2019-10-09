import os
from functools import wraps
from dotenv import load_dotenv
from flask import Flask, abort, request
from twilio.rest import Client
from twilio.request_validator import RequestValidator


load_dotenv()


app = Flask(__name__)


def validate_twilio_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        validator = RequestValidator(os.getenv('TWILIO_AUTH_TOKEN'))
        request_valid = validator.validate(
            request.url,
            request.form,
            request.headers.get('X-TWILIO-SIGNATURE', ''))

        if request_valid:
            return f(*args, **kwargs)
        else:
            return f'Sorry! This is not a valid request'
    return decorated_function


@app.route('/circuit-breaker', methods=['GET'])
@validate_twilio_request
def suspend_account():
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    account = client.api.accounts(account_sid) \
                        .update(status='suspended')

    return f'{account.friendly_name} has been suspended'