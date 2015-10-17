try:
    import apiKeys
    getConsumerKeys = apiKeys.getConsumerKeys
    getAccesKeys = apiKeys.getAccesKeys
except ImportError:

    def x(*args):
        return 'key', 'secret'

    getConsumerKeys = x
    getAccesKeys = x

saveInterval = 1777
tweetPerBracket = 5

# Change these when actually retweeting
bracketWidth = 3600 * 24
postToTwitter = False
minAge = 420
minRetweetedIndex = 0.2
