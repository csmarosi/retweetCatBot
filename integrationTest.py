from heapq import heappush
import random
import botSettings
import ListenerBase as lb
import DistributorListener as distL
import PerformanceListener as pl
import RetweetListener as rt
from time import sleep


def createListeners():
    pl.fileName = 'perfCountersTest.pydat'
    rt.fileName = 'RetweetListenerTest.txt'
    botSettings.tweetPerBracket = 2

    def x(self):
        return 1 * botSettings.bracketWidth
    distL.DistributorListener._getCurrentTime = x

    dl = distL.DistributorListener.start().proxy()
    listeners = dl.actors.get().copy()
    listeners['DistributorListener'] = dl
    return listeners


def testCreation():
    old = createListeners()
    assert set(old.keys()) == {'PerformanceListener', 'RetweetListener',
                               'DistributorListener'}
    old['DistributorListener'].stop()


def checkTimeMachine(listeners, number):
    def x(self):
        return (number + 1) * botSettings.bracketWidth - 1
    distL.DistributorListener._getCurrentTime = x
    listeners['DistributorListener'].onChangeBracketInternal(x(42)).get()

    def x(self, t):
        return t['created_at']
    lb.ListenerBase._getTweetTime = x


def createTweet(time, id, rt):
    return {'retweeted_status':
            {"created_at": botSettings.bracketWidth * time,
             "id": id,
             "entities": {"media": None},
             "retweet_count": rt,
             "user": {"followers_count": 42}}}


def sendTweet(l, tweet, soft=False):
    if soft:
        l['DistributorListener'].processTweet(tweet)
    else:
        # get(): Tweets must arrive when I ask for counters
        l['DistributorListener'].processTweet(tweet).get()
        now = distL.DistributorListener._getCurrentTime(42)
        # get(): Force all RT messages to be sent
        l['RetweetListener'].processFilteredTweet(
            createTweet(0, 4242, 1)['retweeted_status'], now).get()


def createAndSendTweet(listeners, now, rtInc):
    checkTimeMachine(listeners, now)
    for i in range(25):
        tt = i % 5
        if tt < now + 1:
            sendTweet(listeners, createTweet(tt, i, i + rtInc))


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
    listeners = createListeners()
    bW = botSettings.bracketWidth
    perf = listeners['PerformanceListener']

    createAndSendTweet(listeners, 1, 0)
    assert 0 not in perf.perfCounters.get()
    assert bW in perf.perfCounters.get()
    assert 0 in perf.perfCounters.get()[bW]
    assert bW in perf.perfCounters.get()[bW]
    assert perf.perfCounters.get()[bW] == expectedCounters(1, 0)
    assert perf.retweeted.get()[bW] == {'rtC': 7, 'rtId': [1, 6]}
    assert perf.performance.get() == {}

    createAndSendTweet(listeners, 2, 1)
    assert perf.perfCounters.get()[2 * bW] == expectedCounters(2, 1)
    assert perf.retweeted.get()[2 * bW] == {'rtC': 11, 'rtId': [2, 7]}
    assert perf.performance.get() == {0: (0, 15 + 20)}
    assert perf.retweeted.get()[bW] == {'rtC': 7, 'rtId': [1, 6]}  # no change

    createAndSendTweet(listeners, 3, 2)
    assert perf.perfCounters.get()[3 * bW] == expectedCounters(3, 2)
    assert perf.retweeted.get()[3 * bW] == {'rtC': 15, 'rtId': [3, 8]}
    assert perf.performance.get() == {0: (0, 35), bW: (2, (21 + 16 + 2))}

    createAndSendTweet(listeners, 4, 3)
    assert perf.perfCounters.get()[4 * bW] == expectedCounters(4, 3)
    assert perf.retweeted.get()[4 * bW] == {'rtC': 19, 'rtId': [4, 9]}
    assert perf.performance.get() == {
        0: (0, 35),
        bW: (2,  (21 + 16 + 2 * 1)),
        2 * bW: (2, (22 + 17 + 2 * 2))}

    listeners['DistributorListener'].stop()


def testPerformanceCalculationFewTweets():
    listeners = createListeners()
    bW = botSettings.bracketWidth
    perf = listeners['PerformanceListener']

    createAndSendTweet(listeners, 1, 0)
    checkTimeMachine(listeners, 2)
    sendTweet(listeners, createTweet(1, 6, 17))
    sendTweet(listeners, createTweet(2, 21, 1))
    sendTweet(listeners, createTweet(2, 22, 2))
    sendTweet(listeners, createTweet(2, 23, 3))
    assert perf.performance.get() == {0: (0, 35)}

    checkTimeMachine(listeners, 3)
    sendTweet(listeners, createTweet(2, 21, 2))
    sendTweet(listeners, createTweet(2, 22, 4))

    sendTweet(listeners, createTweet(3, 31, 0))
    sendTweet(listeners, createTweet(3, 31, 1))  # cannot retweet again
# Test reloading: Send non-retweetable; otherwise it is saved after a retweet
    sendTweet(listeners, createTweet(3, 31, 41))  # forgotten tweet
    sendTweet(listeners, createTweet(2, 22, 42))
    listeners['DistributorListener'].onStart().get()
    sendTweet(listeners, createTweet(3, 32, 0))
    sendTweet(listeners, createTweet(3, 33, 3))

    sendTweet(listeners, createTweet(3, 32, 2))
    assert perf.performance.get()[bW] == (11, (21 + 17))

    checkTimeMachine(listeners, 4)
    sendTweet(listeners, createTweet(4, 81, 1))
    assert perf.performance.get()[2 * bW] == ((1 + 2), (3 + 4))

    checkTimeMachine(listeners, 5)
    sendTweet(listeners, createTweet(4, 81, 2))
    sendTweet(listeners, createTweet(5, 612776279041945600, 1))
    assert perf.performance.get()[3 * bW] == (2, 5)

    checkTimeMachine(listeners, 6)
    assert perf.performance.get()[4 * bW] == (1, 2)
    assert perf.perfCounters.get() == {
        4 * bW: {4 * bW: {42: [(-1, 81)], 81: 1}},
        5 * bW: {4 * bW: {42: [(-2, 81)], 81: 2},
                 5 * bW: {42: [(-1, 612776279041945600)],
                          612776279041945600: 1}}}

    checkTimeMachine(listeners, 7)
    assert perf.perfCounters.get() == {
        5 * bW: {4 * bW: {42: [(-2, 81)], 81: 2},
                 5 * bW: {42: [(-1, 612776279041945600)],
                          612776279041945600: 1}}}

    checkTimeMachine(listeners, 8)
    assert perf.performance.get()[6 * bW] == (0, 0)
    assert perf.perfCounters.get() == {}
    listeners['DistributorListener'].stop()


def testHeavyLoad():
    def x(*args):
        pass
    # IO is boring and paid gradually
    pl.PerformanceListener.saveData = x
    rt.RetweetListener._logTweet = x
    listeners = createListeners()
    createAndSendTweet(listeners, 1, 0)
    checkTimeMachine(listeners, 2)
    # TODO: this takes a long-long time!
    hundred = 1  # stream API gives ~3 cat per sec, so this tests a daily load
    for i in range(3*24*36*hundred):
        id = random.randint(101, 612776279041945600)
        retweet = random.randint(1, 987)
        sendTweet(listeners, createTweet(1, id, retweet), soft=True)
    listeners['DistributorListener'].stop()


def test_exceptionsAreSwallowed_andNoOneCares():
    listeners = createListeners()
    createAndSendTweet(listeners, 1, 0)
    checkTimeMachine(listeners, 2)

    def x(*args):
        if 2 == random.randint(1, 6):
            raise Exception()
    rt.RetweetListener._logTweet = x
    idSet = {42}
    for i in range(198):
        id = random.randint(101, 612776279041945600)
        idSet.add(id)
        retweet = random.randint(1, 154)
        sendTweet(listeners, createTweet(2, id, retweet), soft=True)
    sleep(0.1)  # TODO: find out the way to do proper synchronization!

    def x(*args):
        pass
    rt.RetweetListener._logTweet = x
    createAndSendTweet(listeners, 3, 2)
    perfCounters = listeners['PerformanceListener'].perfCounters.get()
    bW = botSettings.bracketWidth
    assert set(perfCounters.keys()) == {bW, 2*bW, 3*bW}
    assert set(perfCounters[2*bW][2*bW].keys()) == idSet
    # TODO: check what was retweeted
    listeners['DistributorListener'].stop()
