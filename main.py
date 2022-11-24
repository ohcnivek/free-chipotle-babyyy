import os
from dotenv import load_dotenv
from twilio.rest import Client
import requests
import json
import ast
import typing

### Add your twitter handle + your own phone number + your twilio number here.
TEST_TWITTER_HANDLE = 'certifiedaf' 
TEST_NUMBER = '+16786628359'
TWILIO_NUMBER = '+13466372768'
###

CHIPOTLE_TWITTER_HANDLE = 'ChipotleTweets'
CHIPOTLE_NUMBER = '+1888222'

TWITTER_API_BASE_URL = 'https://api.twitter.com/2'
TWITTER_API_STREAM_PARAM = '/tweets/search/stream'
TWITTER_API_RULES_PARAM = '/rules'


class Logger:
    def info_json(class_:str, function_:str, response: requests.Response):
        print('-- {class_} : {function_}() -- '.format(class_=class_, function_=function_))
        result = ast.literal_eval(str(response.json()))
        print(json.dumps(result, indent=4))
    
    
    def info(class_:str, function_:str, message:str):
        print('-- {class_} : {function_}() -- {message}'.format(class_=class_, function_=function_, message=message))
        
        
    def got_effed(exception_):
        print(exception_)

class TwilioClient: 
    def __init__(self):
        load_dotenv()
        self.account_sid = os.environ['TWILIO_ACCOUNT_SID']     
        self.auth_token = os.environ['TWILIO_AUTH_TOKEN']
        self.client = Client(self.account_sid, self.auth_token)

    def send_message(self, body, from_num:str, to_num:str):
        message = self.client.messages.create(body=body, from_=from_num, to=to_num)
        Logger.info('TwilioClient', 'send_message', 'Successfully sent message, "{body}" ,  to to {to_num} from {from_num}'.format(body=body, to_num=to_num, from_num=from_num))
        
    def send_batch_messages(self, batch:typing.List[str], from_num:str, to_num:str):
        Logger.info('TwilioClient', 'send_batch_messages','Sending batch message to {to_num} from {from_num}'.format(to_num=to_num, from_num=from_num))
        for message in batch:
            try:
                self.send_message(message, from_num, to_num)
            except Exception as e:
                Logger.info('TwilioClient', 'send_batch_messages', 'Something went wrong sending {message}'.format(message=message))
                Logger.got_effed(e)
                        

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
        Logger.info_json('TwitterDataStream',"add_or_delete_rule", response)


    def get_rules(self):
        response = requests.get(
            TWITTER_API_BASE_URL + TWITTER_API_STREAM_PARAM + TWITTER_API_RULES_PARAM, 
            headers=self.headers)
        Logger.info_json('TwitterDataStream',"get_rules", response)


    def digest_tweet_stream(self, twilio_client):
        Logger.info('TwitterDataStream', 'digest_tweet_stream', 'Opening HTTP Connection...')
        with self.session.request(
            url=TWITTER_API_BASE_URL + TWITTER_API_STREAM_PARAM + '?tweet.fields=text', 
            headers=self.headers, 
            stream=True,
            method='GET'
        ) as resp:
            Logger.info('TwitterDataStream', 'digest_tweet_stream', "STATUS CODE -- {code}".format(code=resp.status_code))
            if resp.status_code != 200:
                Logger.info('TwitterDataStream', 'digest_tweet_stream', "shit hit the fan")
                            
            for line_as_byte in resp.iter_lines():
                if not line_as_byte:
                    continue;
                line_as_str = line_as_byte.decode()
                try:
                    line_json= json.loads(line_as_str)
                    tweet_body_text=line_json['data']['text']
                    candidates = Parser.generate_candidates(tweet_body_text)
                    if (candidates):
                        # COMENT OUT LINE BELOW WHILE TESTING
                        # twilio_client.send_batch_messages(candidates, TWILIO_NUMBER, CHIPOTLE_NUMBER)
                        
                        # COMMENT OUT LINE BELOW AFTER TESTING
                        twilio_client.send_batch_messages(candidates, TWILIO_NUMBER, TEST_NUMBER)
                except Exception as e: 
                    Logger.info('TwitterDataStream', 'digest_tweet_stream', "shit hit the fan pt.2" )
                    Logger.got_effed(e)
                    continue
                
                
class Parser:
    def generate_candidates(tweet_as_str: str)-> typing.List[str]:
        text_list = tweet_as_str.split(' ')
        candidates = []

        for word in text_list:
            word_contains_num = Parser._contains_number(word)
            word_contains_char = Parser._contains_char(word)
            
            # probably an emoji or something
            if (not word_contains_char and not word_contains_num):
                continue
            
            # contains both char & number
            if (word_contains_num and word_contains_char):
                candidates.append(word)
                continue
                
            # contains only char -- only consider if all upper case 
            if (word_contains_char):
                if (word.isupper()):
                    candidates.append(word)

            # contains only numbers -- odd, but add as candidate
            if (word_contains_num):
                if (word.isdigit()):
                    candidates.append(word)

        return candidates


    def _contains_number(word:str)-> bool:
        return any(char.isdigit() for char in word)
    
    
    def _contains_char(word:str)-> bool:
        return any(char.isalpha() for char in word)
    
    
    def _get_index_of_first_num(word:str)-> int:
        for index, char in enumerate(word):
            if char.isdigit():
                return index
        return -1 

def main():
    twitter_data_stream = TwitterDataStream()
    twilio_client = TwilioClient()

    ## TESTING: ADDING STREAM RULE -- filtering by tweets from @YOUR-OWN_TWITTER-HANDLE
    # body = {"add": [{"value": "from:{handle}", "tag": "tweets from @{handle}".format(TEST_TWITTER_HANDLE)}]}
    # twitter_data_stream.add_or_delete_rule(body)
    
    ## DELETE TEST STREAM RULE (can use id from .get_rules() response)
    # body = {'delete': {'ids': ['1594932432863727617']}}
    # twitter_data_stream.add_or_delete_rule(body)

    ## ADDING STREAM RULE -- filtering by tweets from @chiptoleTweets
    # body = {"add": [{"value": "from:{handle}", "tag": "tweets from @{handle}".format(CHIPOTLE_TWITTER_HANDLE)}]}
    # twitter_data_stream.add_or_delete_rule(body)

    # GET CURRENT STREAM RULES
    twitter_data_stream.get_rules()
    twitter_data_stream.digest_tweet_stream(twilio_client)

if __name__ == "__main__":
    main()



