from time import strftime, gmtime
from heapq import heapify, heapreplace
import pykka
import botSettings
from . import ListenerBase as lb
from . import Persistence
from . import PostTweet
from . import TweetLogger

fileName = 'RetweetListener.txt'
persistenceFile = 'RetweetListener.pydat'
cutoff = 0.95


class RetweetListener(lb.ListenerBase, pykka.ThreadingActor):
    def __init__(self):
        super(RetweetListener, self).__init__()
        self.poster = PostTweet.PostTweet()
        self.tweetLogger = TweetLogger.TweetLogger()
        self.persistenceListener = Persistence.Persistence(persistenceFile)
        self.cumulativePerformance = {'achieved': 0, 'possible': 0}
        self.tweetLog = {}
        self.minRetweetedIndex = botSettings.minRetweetedIndex

    def onStart(self):
        d = self.persistenceListener.loadData()
        if d:
            (self.cumulativePerformance, self.minRetweetedIndex,
             self.tweetLog) = d

    def saveData(self):
        d = (self.cumulativePerformance, self.minRetweetedIndex, self.tweetLog)
        self.persistenceListener.saveData(d)

    def _logTweet(self, tweet):
        self.tweetLogger.logTweet(tweet, fileName)

    def _retweet(self, tweet, currentBracket):
        perf = self.actors['PerformanceListener']
        retweeted = perf.addReTweetedIfCan(tweet, currentBracket).get()
        if retweeted:
            tId = tweet['id']
            self.poster.retweet(tId)
        return retweeted

    def onChangeBracket(self, oldBracket):
        bestTweets = []
        for i in range(botSettings.tweetPerBracket):
            bestTweets.append((i, i))
        heapify(bestTweets)
        for tweetStat in self.tweetLog.values():
            if tweetStat['@day'] > bestTweets[0][0]:
                new = (tweetStat['@day'], tweetStat['@minAge'])
                heapreplace(bestTweets, new)
        self.minRetweetedIndex *= 0.6
        self.minRetweetedIndex += 0.4 * bestTweets[0][1] / botSettings.minAge
        self.tweetLog = {}
        print('current minRetweetedIndex: ', self.minRetweetedIndex)

    def _retweetCondtional(self, tweet, currentTime, cB):
        age = currentTime - self._getTweetTime(tweet)
        id = tweet['id']
        rtCount = tweet['retweet_count']
        if age > botSettings.minAge:
            if id not in self.tweetLog:
                self.tweetLog[id] = {'@minAge': rtCount, '@day': rtCount}
            else:
                self.tweetLog[id]['@day'] = rtCount
        retweetedIndex = rtCount / max(age, botSettings.minAge)
        if retweetedIndex > self.minRetweetedIndex:
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
        pStr = 'For time %d, captured %d retweet out of %d' % (pB, p[0], p[1])
        if botSettings.bracketWidth == 3600 * 24:
            n = strftime("%A", gmtime(pB))
            pStr = 'On %s, captured %d retweet out of %d' % (n, p[0], p[1])
        self.poster.postTweet(pStr)

        perf = self.cumulativePerformance
        perf['achieved'] += p[0]
        perf['possible'] += p[1]
        ratio = perf['achieved'] / perf['possible']
        self.saveData()
        print('Performance so far:', ratio, perf)
