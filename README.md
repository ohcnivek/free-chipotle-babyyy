# free-chipotle-babyyy

I love two things in life — Chipotle & Twitter.

Recently (like 3 days ago), @ChipotleTweets started doing giveaways of FREE entrées with each USMNT goal on Twitter 💸

<blockquote class="twitter-tweet" data-theme="light"><p lang="en" dir="ltr">⚽️🌯⚽️　 ⚽️🌯⚽️<br> 🌯　　 🌯 🌯　　 🌯<br>⚽️ free chipotle ⚽️<br> 🌯 with every 🌯<br>　 ⚽️ <a href="https://twitter.com/hashtag/USMNT?src=hash&amp;ref_src=twsrc%5Etfw">#USMNT</a> ⚽️<br>　　 🌯　goal　 🌯<br>　 ⚽️ ⚽️<br>　　　　 🌯<br><br>Rules » <a href="https://t.co/ZXQoqg6VdJ">https://t.co/ZXQoqg6VdJ</a></p>&mdash; U.S. Men&#39;s National Soccer Team (@USMNT) <a href="https://twitter.com/USMNT/status/1593288245189611520?ref_src=twsrc%5Etfw">November 17, 2022</a></blockquote>

But then... this happend:

<blockquote class="twitter-tweet" data-conversation="none" data-theme="light"><p lang="en" dir="ltr">I literally texted the second the code came out and didn&#39;t get it. How is that possible!?!?</p>&mdash; Josh Kitchen (@JoshuaKitchen4) <a href="https://twitter.com/JoshuaKitchen4/status/1594778716638355456?ref_src=twsrc%5Etfw">November 21, 2022</a></blockquote>

I mean... how crappy is that??

So I wrote this small script to help us who aren't as swifty on the keyboard (or prefers to not turn on notifications for Twitter lol).

## Getting Started

1. Clone repo: `git clone https://github.com/ohcnivek/free-chipotle-babyyy.git`

2. Create a .env file w/ the following + populate w/ approporiate values from Twilio + Twitter developer accounts (both are free to set up). Make sure to not add @ for the twitter handle.

```
TWILIO_ACCOUNT_SID=XXX
TWILIO_AUTH_TOKEN=XXX
TWILIO_NUMBER = '+1XXXXXXXXXX'

TWITTER_API_KEY=XXX
TWITTER_API_KEY_SECRET=XXX
TWITTER_BEARER_TOKEN=XXX

TEST_TWITTER_HANDLE = 'XXXXXXXX'
TEST_NUMBER = '+1XXXXXXXXXX'
```

3. 🎊 Congrats - You're set up to test!

## Testing

### Background

#### Twitter API

This script uses Twilio + Twitter's developer API. To get set up, you'll need a general understanding of how streams work (specifically for Twitter in our case).

Long story short, imagine this stream is a real-time firehose of data (tweets) from Twitter that is feeding into our app. Now without any filters that would be way too many tweets for us to consume & do anything useful.

So, we add filters -- in our case, we filter on the condition that it's a tweet from @ChipotleTweets.

Now obviously, since we can't test using @ChipotleTweets, we can instead filter using our own twitter account (`TEST_TWITTER_HANDLE` in `.env + main.py`) for now.

To add these filters (aka rules), use `twitter_data_stream.add_or_delete_rule(body)`. I've included some examples in `main.py` to help get set up.

Check out more about Twitter's filtered stream [here!](https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/introduction)

### Heuristic for finding promo code in the tweet

I just looked for words in the tweet that's either all caps or just numbers of even better both lol :)

Once you successfuly:

1. Add rule to filter by tweets from your twitter account
2. Call `twitter_data_stream.get_rules()` and vaildate that the rules has been succesfully added

The output should look something like this after validating with `twitter_data_stream.get_rules()`:

```
 $ python main.py
-- TwitterDataStream : get_rules() --
{
    "data": [
        {
            "id": "1596320693007925249",
            "value": "from:certifiedaf",
            "tag": "tweets from @certifiedaf"
        },
        {
            "id": "1596320697701355521",
            "value": "from:ChipotleTweets",
            "tag": "tweets from @ChipotleTweets"
        },
        {
            "id": "1596320705859276805",
            "value": "from:USMNT",
            "tag": "tweets from @USMNT"
        }
    ],
    "meta": {
        "sent": "2022-11-26T03:02:13.968Z",
        "result_count": 3
    }
}
-- TwitterDataStream : digest_tweet_stream() -- Opening HTTP Connection...
-- TwitterDataStream : digest_tweet_stream() -- STATUS CODE -- 200
```

3. Then, tweet from your account the following:
   "data PROMO2019"

It's important that you include the word 'data' or 'text' to your tweet when testing (the script uses these words to evaulate if the tweet is a promotion tweet).

4. Now, once you tweet from your account, you should get a message to your number (or whatever number you put down as `TEST_NUMBER` in `main.py`).

Updated output:

```
$ python main.py
-- TwitterDataStream : get_rules() --
{
    "data": [
        {
            "id": "1596320693007925249",
            "value": "from:certifiedaf",
            "tag": "tweets from @certifiedaf"
        },
        {
            "id": "1596320697701355521",
            "value": "from:ChipotleTweets",
            "tag": "tweets from @ChipotleTweets"
        },
        {
            "id": "1596320705859276805",
            "value": "from:USMNT",
            "tag": "tweets from @USMNT"
        }
    ],
    "meta": {
        "sent": "2022-11-26T03:02:13.968Z",
        "result_count": 3
    }
}
-- TwitterDataStream : digest_tweet_stream() -- Opening HTTP Connection...
-- TwitterDataStream : digest_tweet_stream() -- STATUS CODE -- 200
-- TwilioClient : start_message_job() -- Start message job to send a message to +16786628359 from +13466372768
-- TwilioClient : send_message() -- Successfully sent message, "
Hey there! Text PROMO2019 to 888222 ASAP for your free chipotle!" , to +1YOUR_NUMBER from +1YOUR_TWILIO_NUMBER
```

And you're good to go. You can also add some additional numbers to send reminders to if you want to spread the joy -- checkout the `main()` function for how to do that.

## During the game:

Just keep an eye for texts to your phone! The codes go out fast, so make sure you have your phone close by.

## Disclaimer

Don't abuse this script. This was for fun & I have no gurantee that this will work. I just love Chipotle & Twitter & thought it would be a fun lil script to spin up. Gift some potle to your loved ones this holiday szn :)
