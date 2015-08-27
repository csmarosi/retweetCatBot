from heapq import heappush
import random
import botSettings
import DistributorListener as distL
import PerformanceListener as pl
import RetweetListener as rt


class TweetSender(object):

    def __init__(self):
        pl.fileName = 'perfCountersTest.pydat'
        rt.fileName = 'RetweetListenerTest.txt'
        botSettings.tweetPerBracket = 2
        self._lastEvent = botSettings.bracketWidth

        dl = distL.DistributorListener.start().proxy()
        self.listeners = dl.actors.get().copy()
        self.listeners['DistributorListener'] = dl

    def _addEvent(self, event):
        if event > self._lastEvent:
            self._lastEvent = event

    def checkTimeMachine(self, number):
        x = (number + 1) * botSettings.bracketWidth - 1
        self._addEvent(x)
        self.listeners['DistributorListener'].onChangeBracketInternal(x)
        self.listeners['DistributorListener'].flush().get()

    def _createTweet(self, time, id, rt):
        user = {"followers_count": 42, 'screen_name': 'lo'}
        created_at = botSettings.bracketWidth * (time + 1) - 1
        self._addEvent(created_at)
        return {'id': 42,
                "created_at": self._lastEvent,
                'retweeted_status': {
                    "created_at": created_at,
                    "id": id,
                    "entities": {"media": None},
                    'text': 'Blah',
                    'favorite_count': rt,
                    "retweet_count": rt,
                    "user": user},
                "user": user}

    def sendTweet(self, time, id, rt, soft=False):
        tweet = self._createTweet(time, id, rt)
        self.listeners['DistributorListener'].processTweet(tweet)
        if not soft:
            self.listeners['DistributorListener'].flush().get()

    def createAndSendTweet(self, now, rtInc):
        self.checkTimeMachine(now)
        for i in range(25):
            tt = i % 5
            if tt < now + 1:
                self.sendTweet(tt, i, i + rtInc)


def testCreation():
    old = TweetSender().listeners
    assert set(old.keys()) == {'PerformanceListener', 'RetweetListener',
                               'DistributorListener'}
    old['DistributorListener'].stop()


def expectedCounters(time, rtInc):
    bW = botSettings.bracketWidth
    result = {}
    for j in range(max(0, time - 2), time + 1):
        result[j * bW] = {42: []}
        for i in range(25):
            if j == i % 5:
                result[j * bW][i] = i + rtInc
                heappush(result[j * bW][42], (-i - rtInc, i))
    return result


def testPerformanceCalculationManyTweets():
    tweetSender = TweetSender()
    bW = botSettings.bracketWidth
    perf = tweetSender.listeners['PerformanceListener']

    tweetSender.createAndSendTweet(1, 0)
    assert 0 not in perf.perfCounters.get()
    assert bW in perf.perfCounters.get()
    assert 0 in perf.perfCounters.get()[bW]
    assert bW in perf.perfCounters.get()[bW]
    assert perf.perfCounters.get()[bW] == expectedCounters(1, 0)
    assert perf.retweeted.get()[bW] == {'rtC': 7, 'rtId': [1, 6]}
    assert perf.performance.get() == {}

    tweetSender.createAndSendTweet(2, 1)
    assert perf.perfCounters.get()[2 * bW] == expectedCounters(2, 1)
    assert perf.retweeted.get()[2 * bW] == {'rtC': 11, 'rtId': [2, 7]}
    assert perf.performance.get() == {0: (0, 15 + 20)}
    assert perf.retweeted.get()[bW] == {'rtC': 7, 'rtId': [1, 6]}  # no change

    tweetSender.createAndSendTweet(3, 2)
    assert perf.perfCounters.get()[3 * bW] == expectedCounters(3, 2)
    assert perf.retweeted.get()[3 * bW] == {'rtC': 15, 'rtId': [3, 8]}
    assert perf.performance.get() == {0: (0, 35), bW: (2, (21 + 16 + 2))}

    tweetSender.createAndSendTweet(4, 3)
    assert perf.perfCounters.get()[4 * bW] == expectedCounters(4, 3)
    assert perf.retweeted.get()[4 * bW] == {'rtC': 19, 'rtId': [4, 9]}
    assert perf.performance.get() == {
        0: (0, 35),
        bW: (2,  (21 + 16 + 2 * 1)),
        2 * bW: (2, (22 + 17 + 2 * 2))}

    tweetSender.listeners['DistributorListener'].stop()


def testPerformanceCalculationFewTweets():
    tweetSender = TweetSender()
    bW = botSettings.bracketWidth
    perf = tweetSender.listeners['PerformanceListener']

    tweetSender.createAndSendTweet(1, 0)
    tweetSender.checkTimeMachine(2)
    tweetSender.sendTweet(1, 6, 17)
    tweetSender.sendTweet(2, 21, 1)
    tweetSender.sendTweet(2, 22, 2)
    tweetSender.sendTweet(2, 23, 3)
    assert perf.performance.get() == {0: (0, 35)}

    tweetSender.checkTimeMachine(3)
    tweetSender.sendTweet(2, 21, 2)
    tweetSender.sendTweet(2, 22, 4)

    tweetSender.sendTweet(3, 31, 0)
    tweetSender.sendTweet(3, 31, 1)  # no retweet again
# Test reloading: Send non-retweetable; otherwise it is saved after a retweet
    tweetSender.sendTweet(3, 31, 41)  # forgotten tweet
    tweetSender.sendTweet(2, 22, 42)
    tweetSender.listeners['DistributorListener'].onStart().get()
    tweetSender.sendTweet(3, 32, 0)
    tweetSender.sendTweet(3, 33, 3)

    tweetSender.sendTweet(3, 32, 2)
    assert perf.performance.get()[bW] == (11, (21 + 17))

    tweetSender.checkTimeMachine(4)
    tweetSender.sendTweet(4, 81, 1)
    assert perf.performance.get()[2 * bW] == ((1 + 2), (3 + 4))

    tweetSender.checkTimeMachine(5)
    tweetSender.sendTweet(4, 81, 2)
    tweetSender.sendTweet(5, 612776279041945600, 1)
    assert perf.performance.get()[3 * bW] == (2, 5)

    tweetSender.checkTimeMachine(6)
    assert perf.performance.get()[4 * bW] == (1, 2)
    assert perf.perfCounters.get() == {
        4 * bW: {4 * bW: {42: [(-1, 81)], 81: 1}},
        5 * bW: {4 * bW: {42: [(-2, 81)], 81: 2},
                 5 * bW: {42: [(-1, 612776279041945600)],
                          612776279041945600: 1}}}

    tweetSender.checkTimeMachine(7)
    assert perf.perfCounters.get() == {
        5 * bW: {4 * bW: {42: [(-2, 81)], 81: 2},
                 5 * bW: {42: [(-1, 612776279041945600)],
                          612776279041945600: 1}}}

    tweetSender.checkTimeMachine(8)
    assert perf.performance.get()[6 * bW] == (0, 0)
    assert perf.perfCounters.get() == {}
    tweetSender.listeners['DistributorListener'].stop()


def test_exceptionsAreSwallowed_andNoOneCares():
    tweetSender = TweetSender()
    tweetSender.createAndSendTweet(1, 0)
    tweetSender.checkTimeMachine(2)

    def x(*args):
        if 2 == random.randint(1, 6):
            raise Exception()
    rt.RetweetListener._logTweet = x
    idSet = {42}
    for i in range(198):
        id = random.randint(101, 612776279041945600)
        idSet.add(id)
        retweet = random.randint(1, 154)
        tweetSender.sendTweet(2, id, retweet, soft=True)
    print(tweetSender.listeners['DistributorListener'].flush().get())

    def x(*args):
        pass
    rt.RetweetListener._logTweet = x
    tweetSender.createAndSendTweet(3, 2)
    perfCounters = \
        tweetSender.listeners['PerformanceListener'].perfCounters.get()
    bW = botSettings.bracketWidth
    assert set(perfCounters.keys()) == {bW, 2*bW, 3*bW}
    assert set(perfCounters[2*bW][2*bW].keys()) == idSet
    # TODO: check what was retweeted
    tweetSender.listeners['DistributorListener'].stop()
