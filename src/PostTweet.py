import tweepy
import botSettings


class PostTweet(object):
    def __init__(self):
        super(PostTweet, self).__init__()
        k, s = botSettings.getConsumerKeys()
        auth = tweepy.OAuthHandler(k, s)
        k, s = botSettings.getAccesKeys()
        auth.set_access_token(k, s)
        self.api = tweepy.API(auth)

    def retweet(self, id):
        print('Retweeted tweet: https://twitter.com/statuses/%s' % id)
        if botSettings.postToTwitter:
            self.api.retweet(id)

    def postTweet(self, text):
        print(text)
        if botSettings.postToTwitter:
            self.api.update_status(status=text)
