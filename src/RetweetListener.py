from time import strftime, gmtime
import pykka
import botSettings
from . import ListenerBase as lb
from . import PostTweet
from . import TweetLogger


fileName = 'RetweetListener.txt'
cutoff = 0.95


class RetweetListener(lb.ListenerBase, pykka.ThreadingActor):

    def __init__(self):
        super(RetweetListener, self).__init__()
        self.poster = PostTweet.PostTweet()
        self.tweetLogger = TweetLogger.TweetLogger()
        self.cumPerf = (0, 0)

    def _logTweet(self, tweet):
        self.tweetLogger.logTweet(tweet, fileName)

    def _retweet(self, tweet, currentBracket):
        perf = self.actors['PerformanceListener']
        retweeted = perf.addReTweetedIfCan(tweet, currentBracket).get()
        if retweeted:
            tId = tweet['id']
            self.poster.retweet(tId)
        return retweeted

    def _retweetCondtional(self, tweet, currentTime, cB):
        bStat = float(currentTime - cB) / botSettings.bracketWidth
        followers = tweet['user']['followers_count']
        if followers > botSettings.followMax * (1 - bStat / cutoff):
            self._retweet(tweet, cB)

    def processFilteredTweet(self, tweet, currentTime, fullTweet):
        self._logTweet(fullTweet)
        cB = self.getBracket(currentTime)
        if cB == self.getTweetBracket(tweet):
            bStat = float(currentTime - cB) / botSettings.bracketWidth
            if bStat < cutoff:
                self._retweetCondtional(tweet, currentTime, cB)
            else:
                self._retweet(tweet, cB)

    def retweetPerformance(self, pB, p):
        (a, b) = self.cumPerf
        pStr = 'For time %d, captured %d retweet out of %d' % (pB, p[0], p[1])
        if botSettings.bracketWidth == 3600 * 24:
            n = strftime("%A", gmtime(pB))
            pStr = 'On %s, captured %d retweet out of %d' % (n, p[0], p[1])
        self.poster.postTweet(pStr)
        a += p[0]
        b += p[1]
        self.cumPerf = (a, b)
        print('Performance so far:', a/b, self.cumPerf)
