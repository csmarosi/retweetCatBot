#!/usr/bin/env python3

import sys
import json
from src import DistributorListener as dl


def main():
    inName = 'RetweetListener_offline.txt'
    if 2 == len(sys.argv):
        inName = sys.argv[1]
    tweetStream = None
    with open(inName, 'r') as data:
        tweetStream = json.load(data)

    distributorListener = dl.DistributorListener.start().proxy()
    distributorListener.onStart()
    mediaIsPresent = {'media': True}
    flushCounter = 0
    for tweet in tweetStream:
        tweet['retweeted_status']['entities'] = mediaIsPresent
        distributorListener.processTweet(tweet)
        flushCounter += 1
        if flushCounter > 40123:
            distributorListener.flush().get()
            sys.stdout.flush()
            flushCounter = 0
    distributorListener.flush().get()
    distributorListener.stop()


if __name__ == '__main__':
    main()
