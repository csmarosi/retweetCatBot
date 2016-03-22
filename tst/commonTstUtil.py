currentTime = 1435536000


def createTweet(id=613417367465373696, rtCount=42, created_at=currentTime):
    user = {"followers_count": 42, 'screen_name': 'lo'}
    return {
        "created_at": created_at,
        "id": id,
        "entities": {"media": None},
        'text': 'Blah',
        'favorite_count': rtCount,
        "retweet_count": rtCount,
        "user": user
    }
