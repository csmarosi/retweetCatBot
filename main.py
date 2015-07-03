#!/usr/bin/env python3

import sys
import traceback
import json
import tweepy
import botSettings
import DistributorListener as dl


class MagicListener(tweepy.StreamListener):

    def __init__(self):
        super().__init__()
        self.distributorListener = dl.DistributorListener.start().proxy()
        self.distributorListener.onStart()

    def on_data(self, data):
        try:
            decoded = json.loads(data)
            self.distributorListener.processTweet(decoded)
        except:
            print('There were an error during MagicListener.on_data()')
            traceback.print_exc(file=sys.stdout)
        return True

    def on_error(self, status):
        self.distributorListener.stop()
        print(status)

    def on_exception(self, exception):
        self.distributorListener.stop()


def main():
    k, s = botSettings.getConsumerKeys()
    auth = tweepy.OAuthHandler(k, s)
    k, s = botSettings.getAccesKeys()
    auth.set_access_token(k, s)

    l = MagicListener()
    stream = tweepy.Stream(auth, l)
# TODO: yes, it is hard-coded because YAGNI; stream.sample()
    stream.filter(track=['cat'], languages=['en'])


if __name__ == '__main__':
    main()
