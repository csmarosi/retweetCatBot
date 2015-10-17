import unittest
import botSettings
from ..src import DistributorListener as dl
from ..src import PostTweet


class tweepyApiSpy(object):
    def retweet(self, id):
        self.id = id

    def update_status(self, status):
        self.text = status


class TotalCoverage(unittest.TestCase):
    def setUp(self):
        def x(self, *args):
            pass

        dl.DistributorListener._getTweetTime = x
        dl.DistributorListener.__init__ = x
        dl.DistributorListener.onChangeBracketInternal = x
        dl.DistributorListener._sendSave = x
        dl.DistributorListener._bracketTime = lambda x, y: 42

    def test_DistributorListener_considersImages(self):
        o = dl.DistributorListener()
        o._counter = 0
        o.sendTweetTo = 0

        def sendTweetToStub(self, *args):
            o.sendTweetTo += 1

        o._sendTweetTo = sendTweetToStub
        o.processTweet({})
        o.processTweet({'retweeted_status': {}})
        o.processTweet({'retweeted_status': {'entities': {}}})
        self.assertEqual(o.sendTweetTo, 0)
        o.processTweet({'retweeted_status': {'entities': {'media': None}}})
        self.assertEqual(o.sendTweetTo, 1)

    def test_PostTweet(self):
        botSettings.postToTwitter = True
        o = PostTweet.PostTweet()
        spy = tweepyApiSpy()
        o.api = spy
        o.retweet(42)
        self.assertEqual(42, spy.id)
        o.postTweet('Buttercup')
        self.assertEqual('Buttercup', spy.text)
