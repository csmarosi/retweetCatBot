try:
    import apiKeys
    getConsumerKeys = apiKeys.getConsumerKeys
    getAccesKeys = apiKeys.getAccesKeys
except ImportError:

    def x(*args):
        return 'key', 'secret'

    getConsumerKeys = x
    getAccesKeys = x

tweetPerBracket = 5
bracketWidth = 3600 * 24

# TODO: this is an arbitrary value for a hyperparameter; get estimate for it!
minAge = 420
# from empirical data, update it from time to time!
avarageTweetPerSecond = 0.4
safetyFactor = 1.5
saveInterval = int(avarageTweetPerSecond * minAge / safetyFactor)

# Change these when actually retweeting
postToTwitter = False
minRetweetedIndex = 0.2
