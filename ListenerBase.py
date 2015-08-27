import time
import calendar
import botSettings


class ListenerBase(object):

    def __init__(self):
        super(ListenerBase, self).__init__()

    def _bracketTime(self, time):
        return time - time % botSettings.bracketWidth

    def _getTweetTime(self, tweet):
        tweetTime = tweet['created_at']
        # TODO: ideally the time should be rewritten to int at the beginning
        if isinstance(tweetTime, int):
            return tweetTime
        tS = time.strptime(tweetTime, "%a %b %d %H:%M:%S +0000 %Y")
        return int(calendar.timegm(tS))

    def getBracket(self, currentTime):
        return self._bracketTime(currentTime)

    def getTweetBracket(self, tweet):
        return self._bracketTime(self._getTweetTime(tweet))

    def onChangeBracket(self, oldBracket):
        pass

    def onStart(self):
        pass

    def onStop(self):
        self.stop()
        pass

    def saveData(self):
        pass
