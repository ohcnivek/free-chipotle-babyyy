import os
from dotenv import load_dotenv
from twilio.rest import Client
import requests
import json
import ast
import typing

load_dotenv()

### DO NOT INCLUDE @ IN HANDLE
TEST_TWITTER_HANDLE = os.environ['TEST_TWITTER_HANDLE']
TEST_NUMBER =  os.environ['TEST_NUMBER']

CHIPOTLE_TWITTER_HANDLE = 'ChipotleTweets'
CHIPOTLE_NUMBER = '+1888222'

TWILIO_NUMBER =  os.environ['TWILIO_NUMBER']

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
        self.account_sid = os.environ['TWILIO_ACCOUNT_SID']     
        self.auth_token = os.environ['TWILIO_AUTH_TOKEN']
        self.client = Client(self.account_sid, self.auth_token)


    def send_message(self, body:str, from_num:str, to_num:str):
        '''
            Send an sms message via Twilio.
            Parameters:
                - body: str
                    body of message
                - from_num:str
                    number to send message from (your Twilio number)
                - to_num:str 
                    number to send message to (Chipotle's number)
        '''
        message = self.client.messages.create(body=body, from_=from_num, to=to_num)
        Logger.info('TwilioClient', 'send_message', 'Successfully sent message, "{body}" ,  to to {to_num} from {from_num}'.format(body=body, to_num=to_num, from_num=from_num))
        
        
    def send_batch_of_messages(self, batch:typing.List[str], from_num:str, to_num:str):
        '''
            Send series of sms messages via Twilio.
            Parameters:
                - batch: List[str]
                    each word in this batch will get sent as an individual message.
                - from_num:str
                    number to send message from (your Twilio number)
                - to_num:str 
                    number to send message to (Chipotle's number)
        '''
        Logger.info('TwilioClient', 'send_batch_of_messages','Sending batch message to {to_num} from {from_num}'.format(to_num=to_num, from_num=from_num))
        for message in batch:
            try:
                self.send_message(message, from_num, to_num)
            except Exception as e:
                Logger.info('TwilioClient', 'send_batch_of_messages', 'Something went wrong sending {message}'.format(message=message))
                Logger.got_effed(e)
                        

class TwitterDataStream:
    def __init__(self):
        self.session = requests.Session()
        self.bearer_token = os.environ['TWITTER_BEARER_TOKEN'] 
        self.headers = {"Content-Type": "application/json", "Authorization": "Bearer {token}".format(token=self.bearer_token)} 


    def add_or_delete_rule(self, body: typing.Dict[str, object]):
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
                        # twilio_client.send_batch_of_messages(candidates, TWILIO_NUMBER, CHIPOTLE_NUMBER)
                        
                        # COMMENT OUT LINE BELOW AFTER TESTING
                        twilio_client.send_batch_of_messages(candidates, TWILIO_NUMBER, TEST_NUMBER)
                except Exception as e: 
                    Logger.info('TwitterDataStream', 'digest_tweet_stream', "shit hit the fan pt.2" )
                    Logger.got_effed(e)
                    continue
    
    """
        Static methods.
    """
    def generate_rule_json(action_type:str, *args, **kwargs):
        '''
            Generate the body (json) to pass to Twitter's add_rule() API. 

            Parameters:
                - action_type: str
                    type of action - add, delete

                --- optional ---
                - rule_types: List[str] 
                    type of rule to add: currently only supports 'from'
                
                - twitter_handle: str 
                    must pass if generating for 'from' rule.

                - ids: List[str]
                        must pass if generating body for delete.
        '''
        body = {}

        if action_type == "delete":
            ids = kwargs.get('ids', None)
            if not ids:
                raise "Need to pass in ids to generate a delete body."
            body['delete'] = {'ids': ids}
            return body
        
        rule_types = kwargs.get('rule_types', None)
        if not rule_types:
            raise "Need to pass rule_type to generate an add body."

        for rule in rule_types:
            if (rule == "from"):
                twitter_handle = kwargs.get('twitter_handle', None)
                if not twitter_handle:
                    raise "Need to pass in twitter handle to generate add body for from: rule."
                rule_value_and_tag = TwitterDataStream._gen_from_rule_value_and_tag(twitter_handle)
                body['add'] = [rule_value_and_tag]

            # add future action types here

        return body

    def _gen_from_rule_value_and_tag(twitter_handle:str):
        return {"value": "from:{twitter_handle}".format(twitter_handle=twitter_handle), "tag": "tweets from @{twitter_handle}".format(twitter_handle=twitter_handle)}

                
                
class Parser:
    def generate_candidates(tweet_as_str: str)-> typing.List[str]:
        '''
            Returns possible words in tweet that could be a promo code.

            Parameters:
                - tweet_as_str: str 
                    tweet text body as a string 
        '''
        text_list = tweet_as_str.split(' ')
        candidates = []

        for word in text_list:
            word_contains_num = Parser._contains_number(word)
            word_contains_char = Parser._contains_char(word)
            
            # probably an emoji or something? idk
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


def main():
    twitter_data_stream = TwitterDataStream()
    twilio_client = TwilioClient()

    ### TESTING: ADDING TEST STREAM RULE -- filtering by tweets from @YOUR-OWN_TWITTER-HANDLE
    # body = twitter_data_stream.generate_rule_json("add", rule_types=['from'], twitter_handle=TEST_TWITTER_HANDLE) 
    # twitter_data_stream.add_or_delete_rule(body)
    
    ### DELETE TEST STREAM RULE (can use id from .get_rules() response)
    # body = TwitterDataStream.generate_rule_json("delete", ids=['1595914775271284738']) 
    # twitter_data_stream.add_or_delete_rule(body)

    ### ADDING STREAM RULE -- filtering by tweets from @chiptoleTweets
    # body = twitter_data_stream.generate_rule_json("add", rule_types=['from'], twitter_handle=CHIPOTLE_TWITTER_HANDLE)
    # twitter_data_stream.add_or_delete_rule(body)

    ### GET CURRENT STREAM RULES + START STREAMIN!!!
    twitter_data_stream.get_rules()
    twitter_data_stream.digest_tweet_stream(twilio_client)

if __name__ == "__main__":
    main()



