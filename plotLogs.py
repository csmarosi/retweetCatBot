import sys
import json
from collections import defaultdict
from time import strftime, gmtime
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


def plotDistribution(data, inName):
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
            dataVector.append((dt, rt, rtt, rt / rtt))
    x = [a[0] for a in dataVector]
    y = [a[1] for a in dataVector]
    fig = plt.figure(figsize=(25, 25))
    ax1 = fig.add_subplot(111)
    ax1.scatter(x, y, marker='.')
    plt.xlim(0, 1200)
    plt.ylim(0, 2500)
    plt.savefig(inName.replace('.txt', '.png'))


def printRetweetsPerDay(data):
    retweets = defaultdict(int)
    retweetsSeen = defaultdict(int)
    mostRetweets = defaultdict(int)
    dailyBestTweet = {}
    secInDay = 60 * 60 * 24
    for origTweet in data:

        def updateDicts(firstCount, lastCount, key):
            increment = lastCount - firstCount
            retweets[key] += increment
            if increment > mostRetweets[key]:
                mostRetweets[key] = increment
                dailyBestTweet[key] = origTweet

        firstCount = None
        firstCountDay = None
        day = None
        lastCount = None
        for retweet in data[origTweet]['rtData']:
            day = int(retweet['created_at'] / secInDay)
            lastCount = retweet['retweet_count']
            if day != firstCountDay:
                if firstCountDay:
                    updateDicts(firstCount, lastCount, day - 1)
                firstCountDay = day
                firstCount = lastCount - 1
            retweetsSeen[day] += 1
        updateDicts(firstCount, lastCount, day)

    print('Day\t retweets\t retweetsSeen\t mostRetweets')
    for i in sorted(retweets.keys()):
        dayName = strftime("%A", gmtime(i * secInDay)).ljust(11)
        print('%s\t%d\t%d\t%d' % (dayName, retweets[i], retweetsSeen[i],
                                  mostRetweets[i]))
    return dailyBestTweet


def main():
    inName = 'RetweetListener_offline.txt'
    if 2 == len(sys.argv):
        inName = sys.argv[1]
    d = loadFormattedRawData(inName)
    data = reformatStream(d)
    dailyBestTweet = printRetweetsPerDay(data)
    topData = {}
    for i in dailyBestTweet.values():
        topData[i] = data[i]
    plotDistribution(topData, inName)


if __name__ == '__main__':
    main()
