import pykka
import botSettings
from . import ListenerBase as lb
from . import Persistence

fileName = 'perfCounters.pydat'


class PerformanceListener(lb.ListenerBase, pykka.ThreadingActor):
    def __init__(self):
        super(PerformanceListener, self).__init__()
        self.persistenceListener = Persistence.Persistence(fileName)
        self.perfCounters = {}
        self.retweeted = {}
        self.performance = {}

    def _createRetweetedDict(self, cB):
        if cB not in self.retweeted:
            self.retweeted[cB] = {'rtC': 0, 'rtId': []}

    def _updateCounters(self, observation, tweetTime, counters):
        if observation in self.perfCounters:
            c1 = self.perfCounters[observation]
            if tweetTime in c1:
                c = c1[tweetTime]
                counters.update(c)

    def _calculateResult(self, oldBracket):
        cB = oldBracket
        lastBracket = cB - botSettings.bracketWidth
        counters = {}
        self._updateCounters(lastBracket, lastBracket, counters)
        self._updateCounters(cB, lastBracket, counters)
        topData = sorted(
            [v for _, v in counters.items() if type(v) == int],
            reverse=True)
        topNum = min(botSettings.tweetPerBracket, len(topData))
        topScore = sum(topData[:topNum])
        self._createRetweetedDict(lastBracket)
        retweeted = self.retweeted[lastBracket]['rtId']
        yourScore = 0 - self.retweeted[lastBracket]['rtC']
        for i in retweeted:
            yourScore += counters[i]
        self.performance[lastBracket] = (yourScore, topScore)
        return lastBracket, self.performance[lastBracket]

    def _createPerfCounterDict(self, cB, tB):
        if cB not in self.perfCounters:
            self.perfCounters[cB] = {}
        cC = self.perfCounters[cB]
        if tB not in cC:
            cC[tB] = {}

    def _prunePerfCounterDict(self, cB):
        keys = list(self.perfCounters.keys())
        for key in keys:
            if key + botSettings.bracketWidth < cB:
                del self.perfCounters[key]

    def onStart(self):
        d = self.persistenceListener.loadData()
        if d:
            (self.perfCounters, self.retweeted, self.performance) = d

    def saveData(self):
        d = (self.perfCounters, self.retweeted, self.performance)
        self.persistenceListener.saveData(d)

    def onStop(self):
        self.saveData()
        self.stop()

    def addReTweetedIfCan(self, tweet, currentBracket):
        self._createRetweetedDict(currentBracket)
        rt = self.retweeted[currentBracket]
        isAlreadyRetweeted = tweet['id'] in rt['rtId']
        hasSpace = len(rt['rtId']) < botSettings.tweetPerBracket
        if hasSpace and not isAlreadyRetweeted:
            rt['rtC'] += tweet['retweet_count']
            rt['rtId'] += [tweet['id']]
            self.saveData()
            return True
        else:
            return False

    def onChangeBracket(self, oldBracket):
        b, p = self._calculateResult(oldBracket)
        self.actors['RetweetListener'].retweetPerformance(b, p)
        self._prunePerfCounterDict(oldBracket)

    def processFilteredTweet(self, tweet, currentTime, fullTweet):
        cB = self.getBracket(currentTime)
        tB = self.getTweetBracket(tweet)
        tId = tweet['id']
        tC = tweet['retweet_count']
        self._createPerfCounterDict(cB, tB)
        currentCounter = self.perfCounters[cB][tB]
        currentCounter[tId] = tC
