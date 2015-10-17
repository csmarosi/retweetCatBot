import pykka
import botSettings
from . import ListenerBase as lb
from . import PerformanceListener as pl
from . import RetweetListener as rl


class DistributorListener(lb.ListenerBase, pykka.ThreadingActor):
    def __init__(self):
        super(DistributorListener, self).__init__()
        self.actors = {}
        self._counter = 0
        self.actors['PerformanceListener'] = \
            pl.PerformanceListener.start().proxy()
        self.actors['RetweetListener'] = \
            rl.RetweetListener.start().proxy()
        for _, v in self.actors.items():
            v.actors = self.actors
        self._currentBracket = None

    def flush(self):
        result = super(DistributorListener, self).flush()
        for _, v in self.actors.items():
            result += v.flush().get()
        return result

    def _sendTweetTo(self, tweet, currentTime, fullTweet):
        for _, v in self.actors.items():
            v.processFilteredTweet(tweet, currentTime, fullTweet)

    def _sendSave(self):
        for _, v in self.actors.items():
            v.saveData()

    def onStart(self):
        for _, v in self.actors.items():
            v.onStart()

    def on_stop(self):
        for _, v in self.actors.items():
            v.onStop()

    def onChangeBracketInternal(self, currentTime):
        if self._currentBracket is None:
            self._currentBracket = self.getBracket(currentTime)
            return
        cB = self.getBracket(currentTime)
        if self._currentBracket < cB:
            for _, v in self.actors.items():
                v.onChangeBracket(self._currentBracket).get()
            self._currentBracket = cB

    def processTweet(self, tweet):
        currentTime = self._getTweetTime(tweet)
        self.onChangeBracketInternal(currentTime)
        if 0 == self._counter % botSettings.saveInterval:
            self._sendSave()
        self._counter += 1
        if 'retweeted_status' in tweet:
            rt = tweet['retweeted_status']
            if 'entities' in rt and 'media' in rt['entities']:
                dT = self.getBracket(currentTime) - self.getTweetBracket(rt)
                if dT / botSettings.bracketWidth < 3:
                    self._sendTweetTo(rt, currentTime, tweet)
