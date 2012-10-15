
import ConfigParser
import getopt
import os
import sys
import twitter


USAGE = '''Usage: tweet [options] message


OAuth settings

Your application's OAuth settings. Keep the "Consumer secret" a secret. This key should never be human-readable in your application.
Access level 	Read, write, and direct messages
About the application permission model
Consumer key 	jj0v13SvciKXLZsTIw3Lw
Consumer secret 	F4fB5QS9D6QnYf123Gg3QolYIE6ldmUxzbeq0JktU
Request token URL 	https://api.twitter.com/oauth/request_token
Authorize URL 	https://api.twitter.com/oauth/authorize
Access token URL 	https://api.twitter.com/oauth/access_token
Callback URL 	None
Your access token

Use the access token string as your "oauth_token" and the access token secret as your "oauth_token_secret" to sign requests with your own Twitter account. Do not share your oauth_token_secret with anyone.
Access token 	51805153-mv1eUtMXMvl2zRi6yeuvrULYjGeAF88mIOvPGvkY2
Access token secret 	LymCYLsC0RTaINOZO66b1ONUoLtiGJNPrmBcI9ZW610
Access level 	Read, write, and direct messages



  This script posts a message to Twitter.

  Options:

    -h --help : print this help
    --consumer-key : the twitter consumer key
    --consumer-secret : the twitter consumer secret
    --access-key : the twitter access token key
    --access-secret : the twitter access token secret
    --encoding : the character set encoding used in input strings, e.g. "utf-8". [optional]

  Documentation:

  If either of the command line flags are not present, the environment
  variables TWEETUSERNAME and TWEETPASSWORD will then be checked for your
  consumer_key or consumer_secret, respectively.

  If neither the command line flags nor the enviroment variables are
  present, the .tweetrc file, if it exists, can be used to set the
  default consumer_key and consumer_secret.  The file should contain the
  following three lines, replacing *consumer_key* with your consumer key, and
  *consumer_secret* with your consumer secret:

  A skeletal .tweetrc file:

    [Tweet]
    consumer_key: *consumer_key*
    consumer_secret: *consumer_password*
    access_key: *access_key*
    access_secret: *access_password*

'''

def PrintUsageAndExit():
  print USAGE
  sys.exit(2)

def GetConsumerKeyEnv():
  return os.environ.get("TWEETUSERNAME", None)

def GetConsumerSecretEnv():
  return os.environ.get("TWEETPASSWORD", None)

def GetAccessKeyEnv():
  return os.environ.get("TWEETACCESSKEY", None)

def GetAccessSecretEnv():
  return os.environ.get("TWEETACCESSSECRET", None)

class TweetRc(object):
  def __init__(self):
    self._config = None

  def GetConsumerKey(self):
    return self._GetOption('consumer_key')

  def GetConsumerSecret(self):
    return self._GetOption('consumer_secret')

  def GetAccessKey(self):
    return self._GetOption('access_key')

  def GetAccessSecret(self):
    return self._GetOption('access_secret')

  def _GetOption(self, option):
    try:
      return self._GetConfig().get('Tweet', option)
    except:
      return None

  def _GetConfig(self):
    if not self._config:
      self._config = ConfigParser.ConfigParser()
      self._config.read('c:/Users/pdam/Desktop/Kabir_Newsletter/.tweet.rc')
    return self._config

def main():
  try:
    shortflags = 'h'
    longflags = ['help', 'consumer-key=', 'consumer-secret=', 
                 'access-key=', 'access-secret=', 'encoding=']
    opts, args = getopt.gnu_getopt(sys.argv[1:], shortflags, longflags)
  except getopt.GetoptError:
    PrintUsageAndExit()
  consumer_keyflag = None
  consumer_secretflag = None
  access_keyflag = None
  access_secretflag = None
  encoding = None
  for o, a in opts:
    if o in ("-h", "--help"):
      PrintUsageAndExit()
    if o in ("--consumer-key"):
      consumer_keyflag = a
    if o in ("--consumer-secret"):
      consumer_secretflag = a
    if o in ("--access-key"):
      access_keyflag = a
    if o in ("--access-secret"):
      access_secretflag = a
    if o in ("--encoding"):
      encoding = a
  message = ' '.join(args)
  if not message:
    PrintUsageAndExit()
  rc = TweetRc()
  consumer_key = consumer_keyflag or GetConsumerKeyEnv() or rc.GetConsumerKey()
  consumer_secret = consumer_secretflag or GetConsumerSecretEnv() or rc.GetConsumerSecret()
  access_key = access_keyflag or GetAccessKeyEnv() or rc.GetAccessKey()
  access_secret = access_secretflag or GetAccessSecretEnv() or rc.GetAccessSecret()
  if not consumer_key or not consumer_secret or not access_key or not access_secret:
    PrintUsageAndExit()
  api = twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret,
                    access_token_key=access_key, access_token_secret=access_secret,
                    input_encoding=encoding)
  try:
    status = api.PostUpdate(message)
  except UnicodeDecodeError:
    print "Your message could not be encoded.  Perhaps it contains non-ASCII characters? "
    print "Try explicitly specifying the encoding with the --encoding flag"
  print "%s just posted: %s" % (status.user.name, status.text)

if __name__ == "__main__":
  main()
