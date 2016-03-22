import unittest
import botSettings
from ..src import RetweetListener as rl

currentTime = 1435536000


class TweetSpy(object):
    def __init__(self):
        self.rt = []
        self.pt = []
        self.getResult = True

    def get(self):
        return self.getResult

    def addReTweetedIfCan(self, *args):
        return self

    def retweet(self, id):
        self.rt.append(id)

    def postTweet(self, text):
        self.pt.append(text)


def createTweet(id, rtCount):
    return {
        'id': id,
        'created_at': currentTime,
        'retweet_count': rtCount,
        'user': {'followers_count': 0}
    }


class TestNormalWorking(unittest.TestCase):
    def setUp(self):
        def x(*args):
            pass

        rl.RetweetListener._logTweet = x
        rl.persistenceFile = 'RetweetListenerTest.pydat'
        self.o = rl.RetweetListener()
        self.o.actors = {}
        self.o.poster = TweetSpy()
        self.o.actors['PerformanceListener'] = self.o.poster

    def test_dataFileNotExist(self):
        self.o.onStart()

    def test_printTime(self):
        botSettings.bracketWidth = 3600
        self.o.retweetPerformance(currentTime, (1, 2))
        self.assertEqual(self.o.poster.pt,
                         ['For time 1435536000, captured 1 retweet out of 2'])

    def test_printDay(self):
        self.o.retweetPerformance(currentTime, (1, 2))
        self.assertEqual(self.o.poster.pt,
                         ['On Monday, captured 1 retweet out of 2'])

    def test_postRetweet(self):
        mA = botSettings.minAge
        mR = botSettings.minRetweetedIndex

        tweet = createTweet(1, mR * mA + 1)
        self.o.processFilteredTweet(tweet, currentTime, None)

        tweet = createTweet(2, 3 * mA * mR)
        self.o.processFilteredTweet(tweet, currentTime + 3 * mA, None)

        tweet = createTweet(3, 3 * mA * mR + 1)
        self.o.processFilteredTweet(tweet, currentTime + 3 * mA, None)

        tweet = createTweet(4, 0)
        day = botSettings.bracketWidth
        self.o.processFilteredTweet(tweet, currentTime + day - 1, None)

        self.o.poster.getResult = False
        tweet = createTweet(5, 2 * mA * mR)
        self.o.processFilteredTweet(tweet, currentTime + mA + 1, None)
        self.assertEqual(self.o.poster.rt, [1, 3, 4])
