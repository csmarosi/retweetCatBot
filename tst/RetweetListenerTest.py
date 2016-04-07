import unittest
import botSettings
from ..src import RetweetListener as rl
from ..tst.commonTstUtil import createTweet, currentTime
import operator


class PerformanceListener(object):
    def __init__(self):
        self.rt = []
        self.tdict = {}
        self.tlist = []

    def addReTweetedIfCan(self, tweet, currentBracket):
        self.rt.append(tweet['id'])

    def getTopTweets(self, tweet):
        tdict = self.tdict
        tlist = self.tlist

        class G(object):
            def get(self):
                return tdict, tlist

        return G()


class TestNormalWorking(unittest.TestCase):
    def setUp(self):
        def x(*args):
            pass

        rl.RetweetListener._logTweet = x
        rl.persistenceFile = 'RetweetListenerTest.pydat'
        self.o = rl.RetweetListener()
        self.o.actors = {}
        self.perf = PerformanceListener()
        self.o.actors['PerformanceListener'] = self.perf

    def test_dataFileNotExist(self):
        self.o.onStart()

    def processFilteredTweet(self, tweet, currentTime):
        self.o.processFilteredTweet(tweet, currentTime,
                                    {'user': {'followers_count': 7}})
        self.perf.tdict[tweet['id']] = tweet['retweet_count']
        self.perf.tlist = sorted(self.perf.tdict.items(),
                                 key=operator.itemgetter(1),
                                 reverse=True)

    def test_postRetweet(self):
        mA = botSettings.minAge
        mR = botSettings.minRetweetedIndex

        tweet = createTweet(1, mR * mA + 1)
        self.processFilteredTweet(tweet, currentTime)

        tweet = createTweet(2, 3 * mA * mR)
        self.processFilteredTweet(tweet, currentTime + 3 * mA)

        tweet = createTweet(3, 3 * mA * mR + 1)
        self.processFilteredTweet(tweet, currentTime + 3 * mA)

        tweet = createTweet(4, 0)
        day = botSettings.bracketWidth
        self.processFilteredTweet(tweet, currentTime + day - 1)

        self.assertEqual(self.perf.rt, [1, 3, 4])

    def test_internal_tweetLog_update(self):
        tweet = createTweet(1, 24)

        mA = botSettings.minAge
        self.processFilteredTweet(tweet, currentTime + mA - 2)
        tweet = createTweet(1, 42)
        self.processFilteredTweet(tweet, currentTime + mA - 1)
        self.assertEqual(self.o.tweetLog, {1: {'retweet_count': 42}})

    def test_internal_minRetweetedIndex_update(self):
        mA = botSettings.minAge

        for i in range(botSettings.tweetPerBracket + 1):
            tweet = createTweet(i, 24)
            self.processFilteredTweet(tweet, currentTime + mA - 1)

        mR = botSettings.minRetweetedIndex
        self.assertEqual(self.o.minRetweetedIndex, mR)

        self.o.onChangeBracket(None)
        # TODO: these magic constant should not be tested like this
        self.assertEqual(self.o.minRetweetedIndex, mR * 0.6 + 24 / mA * 0.4)
