import pykka
import botSettings
from . import ListenerBase as lb
from . import Persistence
from . import TweetLogger

fileName = 'RetweetListener.txt'
persistenceFile = 'RetweetListener.pydat'
cutoff = 0.95


class RetweetListener(lb.ListenerBase, pykka.ThreadingActor):
    def __init__(self):
        super(RetweetListener, self).__init__()
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
        perf.addReTweetedIfCan(tweet, currentBracket)

    def onChangeBracket(self, oldBracket):
        perf = self.actors['PerformanceListener']
        # Note: this is not consistent with the perfocmance metric,
        # but the difference should be small enough in practice
        counters, topData = perf.getTopTweets(oldBracket).get()
        try:
            nTh = min(botSettings.tweetPerBracket - 1, len(topData))
            nThBest = self.tweetLog[topData[nTh][0]]['retweet_count']
            self.tweetLog = {}
        except:
            print('TODO: This should not happen in production.')
            return
        self.minRetweetedIndex *= 0.6
        self.minRetweetedIndex += 0.4 * nThBest / botSettings.minAge

    def _retweetCondtional(self, tweet, currentTime, cB):
        id = tweet['id']
        if id not in self.tweetLog:
            self.tweetLog[id] = {}
        age = currentTime - self._getTweetTime(tweet)
        if age < botSettings.minAge:
            tLid = self.tweetLog[id]
            tLid['retweet_count'] = tweet['retweet_count']
        retweetedIndex = tweet['retweet_count'] / max(age, botSettings.minAge)
        bStat = float(currentTime - cB) / botSettings.bracketWidth
        if retweetedIndex > self.minRetweetedIndex or bStat > cutoff:
            self._retweet(tweet, cB)

    def processFilteredTweet(self, tweet, currentTime, fullTweet):
        self._logTweet(fullTweet)
        cB = self.getBracket(currentTime)
        if cB == self.getTweetBracket(tweet):
            self._retweetCondtional(tweet, currentTime, cB)
