import unittest
import botSettings
import RetweetListener as rl
import ListenerBase as lb


class TweetSpy(object):
    def __init__(self):
        self.rt = []
        self.pt = []

    def get(self):
        return True

    def addReTweetedIfCan(self, *args):
        return self

    def retweet(self, id):
        self.rt.append(id)

    def postTweet(self, text):
        self.pt.append(text)


def createTweet(id, followers):
    return {'id': id, 'user': {'followers_count': followers}}


class TestNormalWorking(unittest.TestCase):

    def setUp(self):
        def x(*args):
            pass
        rl.RetweetListener._logTweet = x
        self.o = rl.RetweetListener()
        self.o.actors = {}
        self.o.poster = TweetSpy()
        self.o.actors['PerformanceListener'] = TweetSpy()
        botSettings.bracketWidth = 3600 * 24
        botSettings.followMax = 123

    def test_printTime(self):
        botSettings.bracketWidth = 3600
        self.o.retweetPerformance(1435536000, (1, 2))
        self.assertEqual(
            self.o.poster.pt,
            ['For time 1435536000, captured 1 retweet out of 2'])

    def test_printDay(self):
        self.o.retweetPerformance(1435536000, (1, 2))
        self.assertEqual(
            self.o.poster.pt,
            ['On Monday, captured 1 retweet out of 2'])

    def test_postRetweet(self):
        def x(self, t):
            return 1435536000
        lb.ListenerBase._getTweetTime = x
        self.o.processFilteredTweet(createTweet(1, 123), 1435536000)
        self.o.processFilteredTweet(createTweet(2, 124), 1435536000)
        day = int(3600 * 24 * 0.95)
        self.o.processFilteredTweet(createTweet(3, 2), 1435536000 + day - 1)
        self.o.processFilteredTweet(createTweet(4, 0), 1435536000 + day - 1)
        self.o.processFilteredTweet(createTweet(5, -1), 1435536000 + day)
        self.assertEqual(self.o.poster.rt, [2, 3, 5])
