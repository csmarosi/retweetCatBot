#!/usr/bin/env python3

import sys
import argparse
import json
from src import DistributorListener as dl
from pykka import ActorRegistry


def startSystem():
    distributorListener = dl.DistributorListener.start().proxy()
    distributorListener.onStart()
    return distributorListener


def procesTweetStream(tweetStream, flushCounter, distributorListener):
    mediaIsPresent = {'media': True}
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
    return flushCounter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputFiles',
                        nargs='+',
                        help='One or more reparsed log files [reParseLog.py]')
    args = parser.parse_args()

    flushCounter = 0
    distributorListener = startSystem()
    for inputFile in args.inputFiles:
        with open(inputFile, 'r') as data:
            print('Playing:', inputFile)
            jsonData = json.load(data)
            flushCounter = procesTweetStream(jsonData, flushCounter,
                                             distributorListener)
    distributorListener.flush().get()
    distributorListener.stop()
    for i in ActorRegistry.get_all():
        i.stop()


if __name__ == '__main__':
    main()
