import time
import pykka
import botSettings
import ListenerBase as lb
import PerformanceListener as pl
import RetweetListener as rl


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
        self._currentBracket = self.getBracket(self._getCurrentTime())

    def _getCurrentTime(self):
        return int(time.time())

    def _sendTweetTo(self, method, tweet, currentTime):
        for _, v in self.actors.items():
            if 'processTweet' == method:
                v.processTweet(tweet)
            elif 'processFilteredTweet' == method:
                v.processFilteredTweet(tweet, currentTime)

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
        cB = self.getBracket(currentTime)
        if self._currentBracket != cB:
            for _, v in self.actors.items():
                # TODO: get is needed for testing
                v.onChangeBracket(self._currentBracket).get()
            self._currentBracket = cB

    def processTweet(self, tweet):
        currentTime = self._getCurrentTime()
        self.onChangeBracketInternal(currentTime)
        if 0 == self._counter % botSettings.saveInterval:
            self._sendSave()
        self._counter += 1
        self._sendTweetTo('processTweet', tweet, currentTime)
        if 'retweeted_status' in tweet:
            rt = tweet['retweeted_status']
            if 'entities' in rt and 'media' in rt['entities']:
                dT = self.getBracket(currentTime) - self.getTweetBracket(rt)
                if dT / botSettings.bracketWidth < 3:
                    self._sendTweetTo('processFilteredTweet', rt, currentTime)
