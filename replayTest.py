#!/usr/bin/env python3

import sys
import json
from src import DistributorListener as dl
from pykka import ActorRegistry


def startSystem():
    distributorListener = dl.DistributorListener.start().proxy()
    distributorListener.onStart()
    return distributorListener


def main():
    inName = 'RetweetListener_offline.txt'
    if 2 == len(sys.argv):
        inName = sys.argv[1]
    tweetStream = None
    with open(inName, 'r') as data:
        tweetStream = json.load(data)

    mediaIsPresent = {'media': True}
    flushCounter = 0
    distributorListener = startSystem()
    for tweet in tweetStream:
        tweet['retweeted_status']['entities'] = mediaIsPresent
        distributorListener.processTweet(tweet)
        flushCounter += 1
        if 0 == flushCounter % 40123:
            distributorListener.flush().get()
            sys.stdout.flush()
        if 0 == flushCounter % 47123:
            distributorListener.flush().get()
            print('crash!')
            distributorListener = startSystem()
            sys.stdout.flush()
    distributorListener.flush().get()
    distributorListener.stop()
    for i in ActorRegistry.get_all():
        i.stop()


if __name__ == '__main__':
    main()
