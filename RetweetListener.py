import json
import pykka
import botSettings
import ListenerBase as lb
import PostTweet


fileName = 'RetweetListener.txt'


class RetweetListener(lb.ListenerBase, pykka.ThreadingActor):

    def __init__(self):
        super(RetweetListener, self).__init__()
        self.poster = PostTweet.PostTweet()

    def pprint(self, tweet):
        d = json.dumps(tweet, sort_keys=True, indent=4, separators=(',', ': '))
        with open(fileName, 'a') as f:
            f.write(d)

    def _retweet(self, tweet, currentBracket):
        perf = self.actors['PerformanceListener']
        if perf.addReTweetedIfCan(tweet, currentBracket).get():
            tId = tweet['id']
            self.poster.retweet(tId)

    def processFilteredTweet(self, tweet, currentTime):
        self.pprint(tweet)
        cB = self.getBracket(currentTime)
        if cB == self.getTweetBracket(tweet):
            bStat = float(currentTime - cB) / botSettings.bracketWidth
            if bStat < 0.9:
                followers = tweet['user']['followers_count']
                if followers * bStat > botSettings.followMax:
                    self._retweet(tweet, cB)
            else:
                self._retweet(tweet, cB)

    def retweetPerformance(self, pB, p):
        pStr = 'For time %d, captured %d retweet out of %d' % (pB, p[0], p[1])
        self.poster.postTweet(pStr)
