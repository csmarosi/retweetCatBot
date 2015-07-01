from time import strftime, gmtime
import json
import pykka
import botSettings
import ListenerBase as lb
import PostTweet


fileName = 'RetweetListener.txt'
cutoff = 0.95


class RetweetListener(lb.ListenerBase, pykka.ThreadingActor):

    def __init__(self):
        super(RetweetListener, self).__init__()
        self.poster = PostTweet.PostTweet()

    def _logTweet(self, tweet):
        d = json.dumps(tweet, sort_keys=True, indent=4, separators=(',', ': '))
        with open(fileName, 'a') as f:
            f.write(d)

    def _retweet(self, tweet, currentBracket):
        perf = self.actors['PerformanceListener']
        if perf.addReTweetedIfCan(tweet, currentBracket).get():
            tId = tweet['id']
            self.poster.retweet(tId)

    def _retweetCondtional(self, tweet, currentTime, cB):
        bStat = float(currentTime - cB) / botSettings.bracketWidth
        followers = tweet['user']['followers_count']
        if followers > botSettings.followMax * (1 - bStat / cutoff):
            self._retweet(tweet, cB)

    def processFilteredTweet(self, tweet, currentTime):
        self._logTweet(tweet)
        cB = self.getBracket(currentTime)
        if cB == self.getTweetBracket(tweet):
            bStat = float(currentTime - cB) / botSettings.bracketWidth
            if bStat < cutoff:
                self._retweetCondtional(tweet, currentTime, cB)
            else:
                self._retweet(tweet, cB)

    def retweetPerformance(self, pB, p):
        pStr = 'For time %d, captured %d retweet out of %d' % (pB, p[0], p[1])
        if botSettings.bracketWidth == 3600 * 24:
            n = strftime("%A", gmtime(pB))
            pStr = 'On %s, captured %d retweet out of %d' % (n, p[0], p[1])
        self.poster.postTweet(pStr)
