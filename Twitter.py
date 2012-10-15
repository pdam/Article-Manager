#!/usr/bin/env python
import urlparse
import oauth2 as oauth
import sys, getopt, urllib
import argparse
import sys
import urllib
from ConfigParser import SafeConfigParser


consumer_key='RahR2y5xB2Sqs5bJEEaIbg'
consumer_secret='WS9WWIOaiXMHClXgkf9mVdBIphhSep98eloMzAmA'

REQUEST_TOKEN_URL   = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL    = 'https://api.twitter.com/oauth/access_token'
AUTHORIZE_URL       = 'https://api.twitter.com/oauth/authorize'
UPDATE_URL          = 'http://api.twitter.com/1/statuses/update.json'


class   Twitter(object):

    def  __init__(self):
        self._config = SafeConfigParser()
        self._config.read('c:/Users/pdam/Desktop/Kabir_Newsletter/twitter.conf')    
        self.consumer_key = self._config.get('twitter','consumer_keys')
        self.consumer_secret = self._config.get('twitter','consumer_secret')
        self.access_key = self._config.get('twitter','access_keys')
        self.access_secret = self._config.get('twitter','access_secret')
        self.request_token ={  'oauth_token'  : ''  ,  'oauth_token_secret' : ''  }
        self.access_token ={  'oauth_token'  : ''  ,  'oauth_token_secret' : ''  }
        
        

    def  doSetup(self ):
        print 'Running twitter setup...'
        consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
        print   consumer  
        client = oauth.Client(consumer)
        resp, content = client.request(REQUEST_TOKEN_URL, "GET")
        if resp['status'] != '200':
            raise Exception("Invalid response %s." % resp['status'])

        self.request_token = dict(urlparse.parse_qsl(content))
        print "Request Token:"
        print "    - oauth_token        = %s" % self.request_token['oauth_token']
        print "    - oauth_token_secret = %s" % self.request_token['oauth_token_secret']
        print

        # Step 2: Redirect to the provider. Since this is a CLI script we do not
        # redirect. In a web application you would redirect the user to the URL
        # below.

        print "Go to the following link in your browser:"
        print "%s?oauth_token=%s" % (AUTHORIZE_URL, self.request_token['oauth_token'])
        print
        # After the user has granted access to you, the consumer, the provider will
        # redirect you to whatever URL you have told them to redirect to. You can
        # usually define this in the oauth_callback argument as well.
        accepted = 'n'
        while accepted.lower() == 'n':
            accepted = raw_input('Have you authorized me? (y/n) ')
        oauth_verifier = raw_input('What is the PIN? ')

        # Step 3: Once the consumer has redirected the user back to the oauth_callback
        # URL you can request the access token the user has approved. You use the
        # request token to sign this request. After this is done you throw away the
        # request token and use the access token returned. You should store this
        # access token somewhere safe, like a database, for future use.
        token = oauth.Token(self.request_token['oauth_token'],
            self.request_token['oauth_token_secret'])
        token.set_verifier(oauth_verifier)
        client = oauth.Client(consumer, token)

        resp, content = client.request(ACCESS_TOKEN_URL, "POST")
        self.access_token = dict(urlparse.parse_qsl(content))

        print "Access Token:"
        print "    - oauth_token        = %s" % self.access_token['oauth_token']
        print "    - oauth_token_secret = %s" % self.access_token['oauth_token_secret']
        print
        print "You may now access protected resources using the access tokens above."


    def SendMsg(self, update):
        token = oauth.Token(key=self.access_key, secret=self.access_secret)
        consumer = oauth.Consumer(key=self.consumer_key, secret=self.consumer_secret)
        client = oauth.Client(consumer, token)
        request_uri = 'https://api.twitter.com/1/statuses/update.json'
        data = {'status': update[:140]}
        resp, content = client.request(request_uri, 'POST', urllib.urlencode(data))
        print reversed


    def  sendTweet(self, message ):
     if not self.consumer_key or not self.consumer_secret or not self.access_key or not self.access_secret:
         self.doSetup()
     else:
         self.SendMsg(message)

t = Twitter()
t.sendTweet(' twitter    API   sucks')


    
