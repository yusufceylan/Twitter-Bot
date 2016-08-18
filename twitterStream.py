import tweepy
import csv

CONSUMER_KEY = ''
CONSUMER_KEY_SECRET = ''
ACCESS_TOKEN = ''
ACCESS_TOKEN_SECRET = ''

# Listening and tracking a word in real-time

class Listener(tweepy.StreamListener):

    def __init__(self, limit = 0):
        super().__init__()
        self.limit = limit
        self.tweet_count = 0

    def on_status(self, status):
        if (self.tweet_count < self.limit):
            try:
                print(status.text)
                with open('TwitDB.csv', 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow([status.id, status.created_at, status.text])
                self.tweet_count += 1
                return True
            except BaseException as e:
                print('Failed on data', str(e))
        else:
            twitterStream.disconnect()


    def on_error(self, status):
        print(status)


Listener = Listener(limit=10)
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_KEY_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

twitterStream = tweepy.Stream(auth, Listener)
twitterStream.filter(track=['python'], languages=['tr'])
