import unittest
import botSettings
from ..src import RetweetListener as rl
from ..tst.commonTstUtil import createTweet, currentTime


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

    def test_internal_tweetLog_update(self):
        tweet = createTweet(1, 24)

        mA = botSettings.minAge
        self.o.processFilteredTweet(tweet, currentTime + mA + 1, None)
        tweet = createTweet(1, 42)
        self.o.processFilteredTweet(tweet, currentTime + mA + 2, None)
        self.assertEqual(self.o.tweetLog, {1: {'@day': 42, '@minAge': 24}})

    def test_internal_minRetweetedIndex_update(self):
        mA = botSettings.minAge

        for i in range(botSettings.tweetPerBracket + 1):
            tweet = createTweet(i, 24)
            self.o.processFilteredTweet(tweet, currentTime + mA + 1, None)

        mR = botSettings.minRetweetedIndex
        self.assertEqual(self.o.minRetweetedIndex, mR)

        self.o.onChangeBracket(None)
        # TODO: these magic constant should not be tested like this
        self.assertEqual(self.o.minRetweetedIndex, mR * 0.6 + 24 / mA * 0.4)
