import os
from dotenv import load_dotenv
from twilio.rest import Client

CHIPOTLE_PROMO_CODE = 'BOGO'
CHIPOTLE_NUMBER = '+16786628359'

class TwilioClient: 
    def __init__(self):
        load_dotenv()

        self.account_sid = os.environ['TWILIO_ACCOUNT_SID']     
        self.auth_token = os.environ['TWILIO_AUTH_TOKEN']
        self.client = Client(self.account_sid, self.auth_token)

    def send_message(self, body, from_num, to_num):
        message = self.client.messages.create(body=body, from_=from_num, to=to_num)
               

def main():
    client = TwilioClient()
    client.send_message(CHIPTOLE_PROMO_CODE, '+13466372768', CHIPOTLE_NUMBER)


if __name__ == "__main__":
    main()
