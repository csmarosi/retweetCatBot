import time
import unittest
import botSettings
import PerformanceListener as pl

tweet = {
    "created_at": "Tue Jun 23 18:44:31 +0000 2015",
    "id": 613417367465373696,
    "retweet_count": 279,
}
RT = {'retweeted_status': tweet}


class TestNormalWorking(unittest.TestCase):
    def setUp(self):
        self.o = pl.PerformanceListener()
        self.now = int(time.time())
        self.tweetBracket = 1435085071 - 1435085071 % botSettings.bracketWidth

    def test_getTime(self):
        self.assertEqual(
            self.o._getTweetTime(tweet),
            1435085071)

    def test_getBracke(self):
        self.assertEqual(
            self.o.getTweetBracket(tweet),
            self.tweetBracket)

    def test_get2Bracke(self):
        self.assertEqual(
            self.o.getBracket(self.now),
            self.now - self.now % botSettings.bracketWidth)

    def test_dict(self):
        self.o.processFilteredTweet(tweet, self.now)
        self.assertEqual(
            self.o.perfCounters,
            {self.o.getBracket(self.now): {
                self.tweetBracket: {
                    613417367465373696: 279,
                    42: [(-279, 613417367465373696)],
                    }}})
