import json
from . import ListenerBase as lb


class TweetLogger(lb.ListenerBase):
    def compactTweet(self, tweet):
        def copyKeys(fro, to, keys):
            for key in keys:
                to[key] = fro[key]

        def copyUser(fro, to):
            to['user'] = {}
            userCopy = ['followers_count', 'screen_name']
            copyKeys(fro['user'], to['user'], userCopy)

        result = {}
        copyKeys(tweet, result, ['id'])
        result['created_at'] = self._getTweetTime(tweet)
        copyUser(tweet, result)

        rt = tweet['retweeted_status']
        result_rt = {}
        result['retweeted_status'] = result_rt
        copyKeys(rt, result_rt, ['text', 'favorite_count', 'retweet_count',
                                 'id'])
        copyUser(rt, result_rt)

        result_rt['created_at'] = self._getTweetTime(rt)

        return result

    def logTweet(self, tweet, fileName):
        compactTweet = self.compactTweet(tweet)  # yapf workaround
        d = json.dumps(compactTweet,
                       sort_keys=True,
                       indent=2,
                       separators=(',', ': '))
        with open(fileName, 'a') as f:
            f.write(d)
