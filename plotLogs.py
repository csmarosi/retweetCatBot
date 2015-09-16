import sys
import json
import os.path
import heapq
from collections import defaultdict
import matplotlib.pyplot as plt


def loadFormattedRawData(fileName):
    result = None
    with open(fileName, 'r') as data:
        result = json.load(data)
    return result


def reformatStream(data):
    result = {}

    def copyKeys(fro, to, keys):
        for key in keys:
            to[key] = fro[key]
    for tweet in data:
        rt = tweet['retweeted_status']
        id = rt['id']
        if id not in result:
            result[id] = rt
        rId = result[id]
        copyKeys(rt, rId, ['favorite_count', 'retweet_count'])
        newData = {}
        copyKeys(rt, newData, ['favorite_count', 'retweet_count'])
        copyKeys(tweet, newData, ['created_at', 'id', 'user'])
        if 'rtData' in rId:
            rId['rtData'].append(newData)
        else:
            rId['rtData'] = [newData]
    return result


def createRearrangedTweets(inName, outName):
    result = None
    if not os.path.isfile(outName):
        d = loadFormattedRawData(inName)
        result = reformatStream(d)
        with open(outName, 'w') as f:
            json.dump(result, f,
                      sort_keys=True, indent=2, separators=(',', ': '))
    else:
        with open(outName, 'r') as data:
            result = json.load(data)
    return result


def plotDistribution(data):
    dataVector = []
    for i in data:
        dat = data[i]
        if 'rtData' not in dat:
            continue
        for j in dat['rtData']:
            dt = j['created_at'] - dat['created_at']
            rt = j['retweet_count']
            rtt = dat['retweet_count']
            # check that 'retweet_count' and others are numbers; WAT?
            try:
                dt > 0 and rt > 0 and rtt > 0
            except:
                print(j)
                continue
            dataVector.append((dt, rt, rtt, rt/rtt))
    x = [a[0] for a in dataVector]
    y = [a[1] for a in dataVector]
    fig = plt.figure(figsize=(25, 25))
    ax1 = fig.add_subplot(111)
    ax1.scatter(x, y, marker='.')
    plt.xlim(0, 24*3600)
    plt.savefig('retweetDistribution.png')


def main():
    inName = 'RetweetListener_offline.txt'
    outName = 'RetweetListener_forPlot.txt'
    if 3 == len(sys.argv):
        inName = sys.argv[1]
        outName = sys.argv[2]
    data = createRearrangedTweets(inName, outName)
    plotDistribution(data)
    magic(data)


def magic(data):
    words = defaultdict(int)
    for i in data:
        dat = data[i]
        for j in dat['text'].split(' '):
            word = j if 'http://t.co' in j else j.lower()
            words[word] += dat['retweet_count']
    topn = heapq.nlargest(2, data, key=lambda x: data[x]['retweet_count'])
    for i in topn:
        dat = data[i]
        dat.pop('rtData', None)
        s = json.dumps(dat, sort_keys=True, indent=2, separators=(',', ': '))
        print(s)
    topw = heapq.nlargest(9, words, key=lambda x: words[x])
    for w in topw:
        print(words[w], w)


if __name__ == '__main__':
    main()
