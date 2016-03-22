import time
import unittest
import botSettings
from ..src import PerformanceListener as pl
from ..tst.commonTstUtil import createTweet


class TestNormalWorking(unittest.TestCase):
    def setUp(self):
        pl.fileName = 'perfCountersTest.pydat'
        self.o = pl.PerformanceListener()
        self.now = int(time.time())
        self.tweetBracket = 1435085071 - 1435085071 % botSettings.bracketWidth

    def test_dataFileNotExist(self):
        self.o.onStart()
        self.assertEqual({}, self.o.perfCounters)

    def test_getTime(self):
        tweet = createTweet(created_at="Tue Jun 23 18:44:31 +0000 2015")
        self.assertEqual(self.o._getTweetTime(tweet), 1435085071)

    def test_getBracke(self):
        tweet = createTweet(created_at="Tue Jun 23 18:44:31 +0000 2015")
        self.assertEqual(self.o.getTweetBracket(tweet), self.tweetBracket)

    def test_get2Bracke(self):
        self.assertEqual(
            self.o.getBracket(self.now),
            self.now - self.now % botSettings.bracketWidth)

    def test_dict(self):
        tweet = createTweet(id=613417367465373696,
                            rtCount=279,
                            created_at="Tue Jun 23 18:44:31 +0000 2015")
        self.o.processFilteredTweet(tweet, self.tweetBracket, None)
        self.o.addReTweetedIfCan(tweet, self.tweetBracket)
        self.o.processFilteredTweet(tweet, self.tweetBracket, None)

        tweet = createTweet(id=613417367465373696,
                            rtCount=297,
                            created_at="Tue Jun 23 18:44:31 +0000 2015")
        currentBracket = botSettings.bracketWidth + self.o.getBracket(
            self.tweetBracket)
        self.o.processFilteredTweet(tweet, currentBracket, None)
        self.o.processFilteredTweet(tweet, currentBracket, None)
        self.assertEqual(self.o.perfCounters,
                         {self.tweetBracket: {self.tweetBracket:
                                              {613417367465373696: 279, }},
                          currentBracket: {self.tweetBracket:
                                           {613417367465373696: 297, }}})
        self.assertEqual(
            self.o._calculateResult(currentBracket), (self.tweetBracket,
                                                      (18, 297)))
