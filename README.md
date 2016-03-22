# retweetCatBot
Retweeting popular cats; at least that is the cover story.

This project tries to identify the tweets that gets the most retweets.
Add cat pictures (and the supposed health benefits of watching them) to this,
 and you get the most awesome project.

### Performance metric
Given a time interval `t`, `n` number of retweet to identify,
 and a deterministic (simple) filter on the Twitter stream,
 find the `n` tweets created in `t` that will have
 the top `retweet_count` at the end of `t+1`.
The score of a particular algorithm is the number of new retweets on
 the (at most `n`) tweets identified
 between the identification and the end of `t+1`.
Tweets must identified during `t`.
It is fairly trivial determine the sum of retweets at `t+1` (the perfect score).

The non-trivial task is the race against the retweets, i.e. identify them
 before the retweets happen.

### Twitter streaming API
The stream API gives only ~3 cats per seconds, which is less that the current
 rate limits on the search API.
The building blocks here are messages however.
Streaming is a natural fit for this usage, could be upgraded to the firehose,
 and a great way to learn about message-passing interfaces.


## Dependencies
The project is tested with `python3`.
`tweepy` is used to interact with the Twitter API and
 `pykka` for message passing.
All the code is tested in
[this Docker container](https://github.com/csmarosi/dockerFiles/blob/master/dev_python3/Dockerfile).


## Licence
AGPL, though it may be changed later.
