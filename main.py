import os
from dotenv import load_dotenv
from twilio.rest import Client
import requests
import json
import ast

TEST_TWITTER_HANDLE = 'certifiedaf'

CHIPOTLE_TWITTER_HANDLE = 'chiptoleTweets'
CHIPOTLE_PROMO_CODE = 'BOGO'
CHIPOTLE_NUMBER = '+16786628359'

TWITTER_API_BASE_URL = 'https://api.twitter.com/2'
TWITTER_API_STREAM_PARAM = '/tweets/search/stream'
TWITTER_API_RULES_PARAM = '/rules'

def pprint_json(calling_function, response):
    print(("--- CALLING FUNCTION: {function} ---").format(function=calling_function))
    result = ast.literal_eval(str(response.json()))
    print(json.dumps(result, indent=4))


class TwilioClient: 
    def __init__(self):
        load_dotenv()
        self.account_sid = os.environ['TWILIO_ACCOUNT_SID']     
        self.auth_token = os.environ['TWILIO_AUTH_TOKEN']
        self.client = Client(self.account_sid, self.auth_token)

    def send_message(self, body, from_num, to_num):
        message = self.client.messages.create(body=body, from_=from_num, to=to_num)


class TwitterDataStream:
    def __init__(self):
        load_dotenv()
        self.session = requests.Session()
        self.bearer_token = os.environ['TWITTER_BEARER_TOKEN'] 
        self.headers = {"Content-Type": "application/json", "Authorization": "Bearer {token}".format(token=self.bearer_token)} 

    def add_or_delete_rule(self, body):
        response = requests.post(
            TWITTER_API_BASE_URL + TWITTER_API_STREAM_PARAM + TWITTER_API_RULES_PARAM, 
            headers=self.headers,
            json=body)
        pprint_json("add_or_delete_rule", response)

    def get_rules(self):
        response = requests.get(
            TWITTER_API_BASE_URL + TWITTER_API_STREAM_PARAM + TWITTER_API_RULES_PARAM, 
            headers=self.headers)
        pprint_json("get_rules", response)

    def get_tweet_stream(self):
        print("Opening HTTP Connection...")
        with self.session.request(
            url=TWITTER_API_BASE_URL + TWITTER_API_STREAM_PARAM + '?tweet.fields=text', 
            headers=self.headers, 
            stream=True,
            method='GET'
        ) as resp:
            print("--STATUS CODE-- {code}".format(code=resp.status_code))
            if resp.status_code != 200:
                print("error -- oops")
            
            # print out buffer
            for line in resp.iter_lines():
                if line:
                    print(line)




def main():
    twitter_data_stream = TwitterDataStream()
    client = TwilioClient()
    client.send_message(CHIPTOLE_PROMO_CODE, '+13466372768', CHIPOTLE_NUMBER)

    # TESTING: ADDING STREAM RULE -- filtering by tweets from @certifiedaf
    body = {"add": [{"value": "from:{handle}", "tag": "tweets from @{handle}".format(TEST_TWITTER_HANDLE)}]}
    twitter_data_stream.add_or_delete_rule(body)

    # ADDING STREAM RULE -- filtering by tweets from @chiptoleTweets
    body = {"add": [{"value": "from:{handle}", "tag": "tweets from @{handle}".format(CHIPOTLE_TWITTER_HANDLE)}]}
    twitter_data_stream.add_or_delete_rule(body)

    # GET CURRENT STREAM RULE 
    # ex. 'data': [{'id': '1594927913228443649', 'value': 'from:ChipotleTweets'}], 'meta': {'sent': '2022-11-22T05:40:53.281Z', 'result_count': 1}}
    twitter_data_stream.get_rules()

    # # DELETE STREAM RULE 
    # body = {'delete': {'ids': ['1594932432863727617']}}
    # twitter_data_stream.add_or_delete_rule(body)
    twitter_data_stream.get_tweet_stream()

if __name__ == "__main__":
    main()



