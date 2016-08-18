import tweepy
import time
import csv

class Bot:
    def __init__(self):
        self.CONSUMER_KEY = ''
        self.CONSUMER_KEY_SECRET = ''
        self.ACCESS_TOKEN = ''
        self.ACCESS_TOKEN_SECRET = ''
        self.api = self.authenticate()
        self.user_list = []

    def authenticate(self):
        auth = tweepy.OAuthHandler(self.CONSUMER_KEY, self.CONSUMER_KEY_SECRET)
        auth.set_access_token(self.ACCESS_TOKEN, self.ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)

        try:
            api.verify_credentials()
        except:
            print('Bot is not able to authenticate, check your keys and tokens')
        else:
            print('Bot has been authenticate')
            return api

    # Grab users followers

    def grab_users_followers(self, user):
        try:
            for page in tweepy.Cursor(self.api.followers_ids,user).pages():
                self.user_list.extend(page)
                time.sleep(5)
            print(len(self.user_list), 'users in the list')
        except:
            print('Failed to grab followers')

    # Follow all users in the list

    def mass_follow(self, users):
        for user in users:
            self.api.create_friendship(user)
            print('You are now following user ID: {}'.format(user))
            time.sleep(5)

    # Unfollow all friends

    def unfollow_all(self):
        for user in self.api.friends_ids():
            self.api.destroy_friendship(user)
            print('User ID: {} has been unfollowed'.format(user))
            time.sleep(5)

    # Unfollow all unfollowers

    def unfollow_unfollowers(self):
        for user in self.api.friends_ids():
            if user not in self.api.followers_ids():
                self.api.destroy_friendship(user)
                time.sleep(5)
                print('User ID: {} has been unfollowed'.format(user))
            else:
                print('Skipping user')

    # Get users all tweets and write a csv file

    def get_all_tweets(self, user):

        all_tweets = []
        new_tweets = self.api.user_timeline(screen_name = user, count = 200)

        all_tweets.extend(new_tweets)
        pointer_id = all_tweets[-1].id

        #Twitter only allows access to a users most recent 3200 tweet

        while True:
            if (len(new_tweets) > 0):
                new_tweets = self.api.user_timeline(screen_name = user, count = 200, max_id = pointer_id - 1)
                all_tweets.extend(new_tweets)
                pointer_id = all_tweets[-1].id
            else:
                break

        # Write the csv

        with open('{}_tweets.csv'.format(user), 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["id", "created_at", "text"])
            for tweet in all_tweets:
                writer.writerow([tweet.id_str, tweet.created_at, tweet.text])

        print(len(all_tweets))
        return all_tweets


    # Search a spesific keyword and decide how many

    # For Search, you have 180 requests per 15-minute window.
    # Since you can get 100-count per request,
    # In theory you can collect 180*100 = 18k tweets per 15 minutes.

    def search_tweets(self, word, max_tweets):
        searched_tweets = []
        last_id = -1
        max_tweets = max_tweets

        while len(searched_tweets) < max_tweets:
            count = max_tweets - len(searched_tweets)
            try:
                new_tweets = self.api.search(q=word, count=count, lang='tr', max_id=str(last_id - 1))
                if not new_tweets:
                    break
                searched_tweets.extend(new_tweets)
                last_id = new_tweets[-1].id
            except tweepy.TweepError as e:
                print('Error', str(e))
                break

        with open('{}_tweets.csv'.format(word), 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["id", "created_at", "text"])
            for tweet in searched_tweets:
                writer.writerow([tweet.id_str, tweet.created_at, tweet.text])

        return len(searched_tweets)


    # Remove all tweets
    # The authenticated user must be the author of the status to destroy.

    def remove_all_tweets(self, user):

        all_tweets = self.get_all_tweets(user)

        for tweet in all_tweets:
            self.api.destroy_status(tweet.id)

    def send_tweet(self, tweet):
        if len(tweet) < 140:
            self.api.update_status(tweet)
            print('Tweet is sended')
        else:
            print('Tweet is too long')


bot = Bot()

bot.grab_users_followers('username')

print(bot.user_list)

bot.mass_follow(bot.user_list)

bot.unfollow_all()

bot.unfollow_unfollowers()

bot.get_all_tweets('username')

bot.remove_all_tweets('authenticated user')

print(bot.search_tweets('#Rio2016', 10))
