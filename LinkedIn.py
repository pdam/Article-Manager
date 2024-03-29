import httplib2
import time, os, simplejson

# Fill the keys and secrets you retrieved after registering your app
consumer_key      =   'abcd123456'
consumer_secret  =   'efgh987654'
user_token           =   'abcd1234-efgh987-9988'
user_secret          =   '9876abcd-123asdf-1122'

# Use your API key and secret to instantiate consumer object
consumer = oauth.Consumer(consumer_key, consumer_secret)

# Use your developer token and secret to instantiate access token object
access_token = oauth.Token(
			key=user_token,
			secret=user_secret)

client = oauth.Client(consumer, access_token)

# Make call to LinkedIn to retrieve your own profile
resp,content = client.request("http://api.linkedin.com/v1/people/~", "GET", {})

# By default, the LinkedIn API responses are in XML format. If you prefer JSON, simply specify the format in your call
resp,content = client.request("http://api.linkedin.com/v1/people/~?format=json", "GET", {})




