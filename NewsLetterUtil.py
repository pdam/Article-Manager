#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import with_statement
__author__ = 'pdam.2010@gmail.com'



import os, sys, pickle, md5, threading
import atom
import  cPickle,gzip,ast,shelve
import getopt
import sys
import  os, re
import  simplejson
from datetime import datetime, date, time, timedelta
import time
from  ConfigParser  import ConfigParser
import  webbrowser
import argparse
import gdata
from  gdata import service 
import struct
import sys
import json
import tweepy
from  instapaper  import  Instapaper
from ConfigParser import SafeConfigParser
import urllib2

VERBOSE =1

contentPhp="""
<?php if(!isset($_POST[$articleList]) || (isset($_POST[$articleList]) && empty($_POST[$articleList])) || isset($_POST[$articleList]) && $_POST[$articleList]<0)
    { 
    
    for ($i=0;isset($_POST($articleList[$i]));$i++) {
       if  ( $_POST($articleList[$i]['selOpt']) == 'on' )  {
             $contents  =  $contents . '<tr><td>' .$_POST($articleList[$i]['date']) .'</td><td>' .$_POST($articleList[$i]['title']) . '</td><td>' . $_POST($articleList[$i]['body']) . '</td></tr>' ;
             
            }
       }
    

      echo  "$contents" ;
      require_once 'inc/MCAPI.class.php';
      require_once 'inc/config.inc.php'; //contains apikey

      $api = new MCAPI($apikey);

      $type = 'regular';

      $opts['newsletter_list'] = $_POST['list_id'] ;
      $opts['subject'] = $_POST['message_subject']  ;
      $opts['from_email'] = $_POST['from_email'];  
      $opts['from_name'] = $_POST['from_user'];

      $opts['tracking']=array('opens' => true, 'html_clicks' => true, 'text_clicks' => false);

      $opts['authenticate'] = true;
      //$opts['analytics'] = array('google'=>'my_google_analytics_key');
      $opts['title'] = 'Test Newsletter Title';

      $content = array('html_main'=> $contents . 'some pretty html content',
                       'html_sidecolumn' => 'sidecolumn.html',
                       'html_header' => 'header.html',
                       'html_footer' => 'footer.html' ,  // *|UNSUB|* message', 
                       'text' => $contents . ' *|UNSUB|*'
                      );
      //$opts['template_id'] = "270413";

      $retval = $api->campaignCreate($type, $opts, $content);

      if ($api->errorCode){
              echo "Unable to Create New Campaign!";
              echo "\n\tCode=".$api->errorCode;
              echo "\n\tMsg=".$api->errorMessage."\n";
      } 

      else {
              $cid  =  $retval ;
              echo "New Campaign ID:".$retval."\n";
              $retvalCamp = $api->campaignSendNow($cid);

      if ($api->errorCode){
              echo "Unable to Send  a  Campaign Immediately !";
              echo "\n\tCode=".$api->errorCode;
              echo "\n\tMsg=".$api->errorMessage."\n";
      } 
      else {
              $cid  =  $retval ;
              echo "Got status  ".$retval."\tSend campaign to List:".$list_id."\n";
              }
         }
}

?>
"""

time_fmt = "%Y-%m-%d %H:%M"

import urlparse
import oauth2 as oauth
import sys, getopt, urllib
import argparse
import sys
import urllib
from ConfigParser import SafeConfigParser




REQUEST_TOKEN_URL   = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL    = 'https://api.twitter.com/oauth/access_token'
AUTHORIZE_URL       = 'https://api.twitter.com/oauth/authorize'
UPDATE_URL          = 'http://api.twitter.com/1/statuses/update.json'


class   Twitter(object):

    def  __init__(self):
        self._config = SafeConfigParser()
        self._config.read('twitter.conf')    
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

     

class  BookMark(object):

    def  __init__( self, bookmark_id , description ,  title , url , category , hashval):
        self.bookmark_id =  bookmark_id     
        self.description = description
        self.title  =  title
        self.url =  url
        self.category = category
        self.hashval  =  hashval 
        
    def hasChanged(self , hashVal):
        return ( ( self.prev_hashval is not None ) and ( self.prev_hashval != hashVal ) )

    def mark(self,hashval):
        self.prev_hashval = self.hashval
        

                
class InstapaperError(Exception):
    pass

class Instapaper(object):
    def __init__(self, fileName , username='', password=''):
        self._username = username
        self.pickle  = pickle 
        self._password = password
        self.dumpFile =  "%s.pickle"%fileName
        try :
          file(self.dumpFile ,'rb') != None  
        except:
            print "Could not  find pickle  .Did  you  run the tool before?  Starting afresh ...."
            self.listBookMarks  =  self.listFolders()
        else : 
            self.listBookMarks = self.pickle.load( open( self.dumpFile, "rb" ) )     
        self.todo = []
        self.run()
        
        
    def AddWebBookMark(self, folder  , article_name , article_title , article_url  ,article_desc):
        """Invoke  Jmeter  passing the   right  arguments ."""
        article_name , article_title , article_url  ,article_desc   =   re.sub('\n' ,  '<BR/>' , article_name) ,re.sub('\n' ,  '<BR/>' ,article_title) , re.sub('\n' ,  '' ,article_url)  ,re.sub('\n' ,  '<BR/>' ,article_desc)
        cmd   =   "C:/java/apache-jmeter-2.6/bin/jmeter.bat -Jinsta_user=\"%s\" -Jinsta_password=\"%s\" -Jfname=\"%s\"  -Jarticle_name=\"%s\"  -Jarticle_title=\"%s\"  -Jarticle_url=\"%s\"  -Jarticle_desc=\"%s\"  -n  -t  InstaP.jmx -l  log_%s.jtl " %( self.insta_user  , self.insta_password , folder  , article_name , article_title , article_url  ,article_desc , time.strftime("%Y%m%d%H%M%S", time.localtime()) )
        print cmd
        os.system(cmd)

    def note(self, level, format, *args):
        if self.verbose > level:
            if args:
                format = format%args
            self.message(format)

    def message(self, format, *args):
        if args:
            format = format%args
        print format

    def __getstate__(self):
        return (self.roots, self.todo, self.done, self.bad)

    def __setstate__(self, state):
        self.reset()
        (self.listBookMarks, self.todo, self.done, self.bad) = state
        for root in self.listBookMarks:
            self.listBookMarks(root)
        for url in self.bad.keys():
            self.markerror(bookmark)

    def load_pickle( verbose=VERBOSE):
            if verbose > 0:
                print "Loading checkpoint from %s ..." % self.fileName
            f = open(self.fileName, "rb")
            c = pickle.load(f)
            f.close()
            if verbose > 0:
                print "Done."
                print "BookMarks:", "\n      ".join(c.listBookMarks)
            return c


    def run(self):
        while self.todo:
            self.round = self.round + 1
            self.note(0, "\nRound %d (%s)\n", self.round, self.status())
            listBookMarks = self.todo.keys()
            listBookMarks.sort()
            del listBookMarks[self.roundsize:]
            for bookmark in listBookMarks:
                self.doBookMark(bookmark)

    def status(self):
        return "%d total, %d to do, %d done, %d bad" % (
            len(self.todo)+len(self.done),
            len(self.todo), len(self.done),
            len(self.bad))

    def report(self):
        self.message("")
        if not self.todo: s = "Final"
        else: s = "Interim"
        self.message("%s Report (%s)", s, self.status())
        self.report_errors()



    def auth(self, username='', password=''):
        if username:
            return self._do_auth(username, password)
        if self._username:
            return self._do_auth(self._username, self._password)
        return False

    def _query(self, url=None, params=""):
        """ method to query a URL with the given parameters
            Parameters:
            url -> URL to query
            params -> dictionary with parameter values

            Returns: HTTP response code, headers
            If an exception occurred, headers fields are None
            """
        if url is None:
            raise NoUrlError("No URL was provided.")
        # return values
        headers = {'location': None, 'title': None}
        headerdata = urllib.urlencode(params)
        try:
            request = urllib2.Request(url, headerdata)
            response = urllib2.urlopen(request)
            status = response.read()
            info = response.info()
            try:
                headers['location'] = info['Content-Location']
            except KeyError:
                pass
            try:
                headers['title'] = info['X-Instapaper-Title']
            except KeyError:
                pass
            return (status, headers)
        except IOError as exception:
            return (exception.code, headers)
    def listFolders(self , rep='name' ):
        api = "https://www.instapaper.com/api/1/folders/list"
                
        params = {
            'username': self._username,
            'password': self._password,
        }
        params = urllib.urlencode(params)
        f = urllib.urlopen(api, params)
        status = f.getcode()
        if status == 201:
            return f.headers['Content-Location']
        elif status == 400:
            raise InstapaperError("bad request. probably missing a required parameter, such as url")
        elif status == 403:
            raise InstapaperError("invalid username or password")
        elif status == 500:
            raise InstapaperError("the service encountered an error")
        listF  =  simplejson.load(f)
        if  (  rep == 'name'  ):
                return [ f['title']   for    f in   listF  if  f['type']=='folder'   ]
        elif ( rep == 'id' ):
                return [ f['folder_id']   for    f in   listF  if  f['type']=='folder'   ]
        else :
            return [ ( f['folder_id'] , f['title'])   for    f in   listF  if  f['type']=='folder'   ]


    def getAllBookMarks(self):
        folder_idList   = [  x  for     x  in    self.listFolders(rep=None)  ]
        [ self.getBookmark( y[0] , y[1])  for  y  in  folder_idList ]
        return  self.listBookMarks
            

    def hasChanged( self, bookmark_id , hashval ):
        self.s = shelve.open('%s.she'%self.fileName  ,   'c')
        try:
           if ( self.s['bookmark']['bookmark_id'] == bookmark_id   and  self.s['bookmark']['hashval'] == hashval  ):
               status=False
           else :
               status= True 
        finally:
            self.s.close()
        return  status
       

    def getBookmark(self , folder_id ,  category): 
        """
            /api/1/bookmarks/list  Lists the user’s unread bookmarks, and can also synchronize reading positions.
        Input parameters:

            limit: Optional. A number between 1 and 500, default 25.
            folder_id: Optional. Possible values are unread (default), starred, archive, or a folder_id value from /api/1/folders/list.
            have: Optional. A concatenation of bookmark_id values that the client already has from the specified folder. See below.

             Output: One meta object, the current user, and between 0 and limit bookmarks.
            Each bookmark has    the    following  fields
            'hash'
            'description'
            'title'
            'url'
            'progress_timestamp'
            'bookmark_id'
            'time'
            'progress'
            'starred'
            'type'
            'private_source'
        """
        api = "https://www.instapaper.com/api/1/bookmarks/list"
        params = {
            'username': self._username,
            'password': self._password,
            'folder_id' :  folder_id}
        params = urllib.urlencode(params)
        request = urllib2.Request(api, params)
        outL =  json.loads(urllib2.urlopen(request).read(),'utf-8')
        for   x  in   outL :
               if  x.has_key('bookmark_id') : 
                        value = { 'bookmark_id'  :   x['bookmark_id'] ,  'hashval'  :   x['hash']  }
                        self.listBookMarks.append({ "bookmark_id": x['bookmark_id']  , "url"   : x['url']    ,  "title"  :  x['title']   ,  "description"  :   x['description']   , "hashval" :   x['hash'] ,    'category':   category  })



        
    
        
        
        
    def _query(self, url=None, params=""):
        """ method to query a URL with the given parameters
        Parameters:
        url -> URL to query
        params -> dictionary with parameter values

        Returns: HTTP response code, headers
        If an exception occurred, headers fields are None
        """
        if url is None:
            raise NoUrlError("No URL was provided.")
        # return values
        headers = {'location': None, 'title': None}
        headerdata = urllib.urlencode(params)
        try:
            request = urllib2.Request(url, headerdata)
            response = urllib2.urlopen(request)
            status = response.read()
            info = response.info()
            try:
                headers['location'] = info['Content-Location']
            except KeyError:
                pass
            try:
                headers['title'] = info['X-Instapaper-Title']
            except KeyError:
                pass
            return (status, headers)
        except IOError as exception:
            return (exception.code, headers)
    
    def report_errors(self):
        if not self.bad:
            self.message("\nNo errors")
            return
        self.message("\nError Report:")
        sources = self.errors.keys()
        sources.sort()
        for source in sources:
            triples = self.errors[source]
            self.message("")
            if len(triples) > 1:
                self.message("%d Errors in %s", len(triples), source)
            else:
                self.message("Error in %s", source)
            # Call self.format_url() instead of referring
            # to the URL directly, since the URLs in these
            # triples is now a (URL, bookmark_id) pair. The value
            # of the "source" variable comes from the list of
            # origins, and is a URL, not a pair.
            for url, rawlink, msg in triples:
                if rawlink != self.format_url(url): s = " (%s)" % rawlink
                else: s = ""
                self.message("  HREF %s%s\n    msg %s",
                             self.format_url(url), s, msg)

    def doBookMark(self, bookmarkDict):

        # All printing of URLs uses format_url(); argument changed to
        # bookmarkDict for clarity.
        if self.verbose > 1:
            if self.verbose > 2:
                self.show("Check ", self.format_url(bookmarkDict),
                          "  from", self.todo[bookmarkDict])
            else:
                self.message("Check %s", self.format_url(bookmarkDict))
        url, local_bookmark_id = bookmarkDict
        if local_bookmark_id and self.nonames:
            self.markdone(bookmarkDict)
            return
        try:
            bookmark = self.getBookMark(bookmarkDict)
        except ValueError, msg:
            msg = self.sanitize(msg)
            self.note(0, "Error parsing %s: %s",
                          self.format_url(bookmarkDict), msg)
            # Dont actually mark the URL as bad - it exists, just
            # we can't parse it!
            bookmark = None
        if bookmark:
            # Store the hash which corresponds to this bookmark.
            self.bookmark_table[bookmark_id] = hashval
            # If there is a bookmark_id in this bookmarkDict, and it's not
            # in the list of names for the page, call setbad(), since
            # it's a missing one.
            if local_bookmark_id and local_bookmark_id not in page.getnames():
                self.setbad(bookmarkDict, ("Missing name anchor `%s'" % local_bookmark_id))
            for bookmark_info in bookmark.getlinkinfos(bookmark_id):
                # getlinkinfos() now returns the bookmark_id as well,
                # and we store that bookmark_id here in the "todo" dictionary.
                title, url, description , hashval  ,  bookmark_id , category  = bookmark_info['title'],   bookmark_info['url'], bookmark_info['description'] , bookmark_info['hashval']  ,  bookmark_info['bookmark_id'] ,  bookmark_info['category']  
                self.newbookmark(title, url, description , hashval  ,  bookmark_id , category)
        else:
            # If no page has been created yet, we want to
            # record that fact.
            self.bookmark_table[bookmarkDict['bookmark_id']] = bookmarkDict['hashval']
        self.markdone(bookmarkDict)

    def newbookmark(self,title, url, description , hashval  ,  bookmark_id , category ):
        if self.done.has_key(bookmark_id):
            self.newdonelink(hashval, bookmark_id)
        else:
            self.newtodolink(hashval, bookmark_id)

    def newdonelink(self, url, bookmark_id):
        if bookmark_id not in self.done[url]:
            self.done[url].append(bookmark_id)

        # Call self.format_url(), since the URL here
        # is now a (URL, bookmark_id) pair.
        self.note(3, "  Done bookmark %s", self.format_url(url))

        # Make sure that if it's bad, that the bookmark_id gets added.
        if self.bad.has_key(url):
            source, rawlink = bookmark_id
            triple = url, rawlink, self.bad[url]
            self.seterror(source, triple)

    def newtodolink(self, url, bookmark_id):
        # Call self.format_url(), since the URL here
        # is now a (URL, bookmark_id) pair.
        if self.todo.has_key(url):
            if bookmark_id not in self.todo[url]:
                self.todo[url].append(bookmark_id)
            self.note(3, "  Seen todo bookmark %s", self.format_url(url))
        else:
            self.todo[url] = [bookmark_id]
            self.note(3, "  New todo bookmark %s", self.format_url(url))

    def format_url(self, url):
        bookmark, bookmark_id = url
        if bookmark_id: return bookmark + "#" + bookmark_id
        else: return bookmark

    def markdone(self, url):
        self.done[url] = self.todo[url]
        del self.todo[url]
        self.changed = 1

    def inroots(self, url):
        for bookmark in self.listBookMarks:
            if bookmark['bookmark_id'] == bookmark_id:
                return self.isallowed(bookmarrk, bookmark_id)
        return 0

    def isallowed(self, root, url):
        root = urlparse.urljoin(root, "/")
        return self.robots[root].can_fetch(AGENTNAME, url)

    def getBookMark(self, bookmark):
        # Incoming argument name is a (bookmark_id  , hashval ) pair.
        # The bookmark may have existed  in the bookmark_table variable.
        bookmark_id ,  hashval = bookmark['bookmark_id'] , bookmark['hashval'] 
        if self.bookmark_table.has_key(bookmark_id):
            return self.bookmark_table[bookmark_id]

        scheme, path = urllib.splittype(url)
        if scheme in ('mailto', 'news', 'javascript', 'telnet'):
            self.note(1, " Not checking %s URL" % scheme)
            return None
        isint = self.inroots(url)

        # Ensure that open_bookmark gets the URL pair to
        # print out its error message and record the error pair
        # correctly.
        if not isint:
            f = self.open_bookmark(bookmark)
            if f:
                self.safeclose(f)
            return None
        text, nurl = self.readhtml(bookmark)

        if nurl != url:
            self.note(1, " Redirected to %s", nurl)
            url = nurl
        if text:
            return BookMark(hashval, bookmark_id,  Instapaper=self)

    # These next three functions take (URL, bookmark_id) pairs as
    # arguments, so that open_bookmark() receives the appropriate tuple to
    # record error messages.
    def readhtml(self, bookmarkDict):
        url, bookmark_id = bookmarkDict
        text = None
        f, url = self.openhtml(bookmarkDict)
        if f:
            text = f.read()
            f.close()
        return text, url

    def openhtml(self, bookmarkDict):
        url, bookmark_id = bookmarkDict
        f = self.open_bookmark(bookmarkDict)
        if f:
            url = f.geturl()
            info = f.info()
            if not self.checkforhtml(info, url):
                self.safeclose(f)
                f = None
        return f, url

    def open_bookmark(self, bookmarkDict):
        url, bookmark_id = bookmarkDict
        try:
            return self.urlopener.open(url)
        except (OSError, IOError), msg:
            msg = self.sanitize(msg)
            self.note(0, "Error %s", msg)
            if self.verbose > 0:
                self.show(" HREF ", url, "  from", self.todo[bookmarkDict])
            self.setbad(bookmarkDict, msg)
            return None

    def checkforhtml(self, info, url):
        if info.has_key('content-type'):
            ctype = cgi.parse_header(info['content-type'])[0].lower()
            if ';' in ctype:
                # handle content-type: text/html; charset=iso8859-1 :
                ctype = ctype.split(';', 1)[0].strip()
        else:
            if url[-1:] == "/":
                return 1
            ctype, encoding = mimetypes.guess_type(url)
        if ctype == 'text/html':
            return 1
        else:
            self.note(1, " Not HTML, mime type %s", ctype)
            return 0

    def setgood(self, url):
        if self.bad.has_key(url):
            del self.bad[url]
            self.changed = 1
            self.note(0, "(Clear previously seen error)")

    def setbad(self, url, msg):
        if self.bad.has_key(url) and self.bad[url] == msg:
            self.note(0, "(Seen this error before)")
            return
        self.bad[url] = msg
        self.changed = 1
        self.markerror(url)

    def markerror(self, url):
        try:
            bookmark_ids = self.todo[url]
        except KeyError:
            bookmark_ids = self.done[url]
        for source, rawlink in bookmark_ids:
            triple = url, rawlink, self.bad[url]
            self.seterror(source, triple)

    def seterror(self, url, triple):
        try:
            # Because of the way the URLs are now processed, I need to
            # check to make sure the URL hasn't been entered in the
            # error list.  The first element of the triple here is a
            # (URL, bookmark_id) pair, but the URL key is not, since it's
            # from the list of bookmark_ids.
            if triple not in self.errors[url]:
                self.errors[url].append(triple)
        except KeyError:
            self.errors[url] = [triple]

    # The following used to be toplevel functions; they have been
    # changed into methods so they can be overridden in subclasses.

    def show(self, p1, bookmark, p2, bookmark_ids):
        self.message("%s %s", p1, bookmark)
        i = 0
        for source, rawlink in bookmark_ids:
            i = i+1
            if i == 2:
                p2 = ' '*len(p2)
            if rawlink != bookmark: s = " (%s)" % rawlink
            else: s = ""
            self.message("%s %s%s", p2, source, s)

    def sanitize(self, msg):
        if isinstance(IOError, ClassType) and isinstance(msg, IOError):
            # Do the other branch recursively
            msg.args = self.sanitize(msg.args)
        elif isinstance(msg, TupleType):
            if len(msg) >= 4 and msg[0] == 'http error' and \
               isinstance(msg[3], InstanceType):
                # Remove the Message instance -- it may contain
                # a file object which prevents pickling.
                msg = msg[:3] + msg[4:]
        return msg

    def safeclose(self, f):
        try:
            url = f.geturl()
        except AttributeError:
            pass
        else:
            f.close()

    def save_pickle(self, dumpfile):
        if not self.changed:
            self.note(0, "\nNo need to save checkpoint")
        elif not dumpfile:
            self.note(0, "No dumpfile, won't save checkpoint")
        else:
            self.note(0, "\nSaving checkpoint to %s ...", dumpfile)
            newfile = dumpfile + ".new"
            f = open(newfile, "wb")
            pickle.dump(self, f)
            f.close()
            try:
                os.unlink(dumpfile)
            except os.error:
                pass
            os.rename(newfile, dumpfile)
            self.note(0, "Done.")
            return 1
        
    def add(self, url, title='', selection='', auto_title=1):
        api = "https://www.instapaper.com/api/add"
        
        if not url:
            raise InstapaperError("required url")
        
        params = {
            'username': self._username,
            'password': self._password,
            'url': url,
            'title': title,
            'selection': selection,
            'auto-title': auto_title
        }
        params = urllib.urlencode(params)
        f = urllib.urlopen(api, params)
        
        status = f.getcode()
        if status == 201:
            return f.headers['Content-Location']
        elif status == 400:
            raise InstapaperError("bad request. probably missing a required parameter, such as url")
        elif status == 403:
            raise InstapaperError("invalid username or password")
        elif status == 500:
            raise InstapaperError("the service encountered an error")
    
    def _do_auth(self, username, password=''):
        api = 'https://www.instapaper.com/api/authenticate'
        params = urllib.urlencode({
            'username': username,
            'password': password,
        })
        f = urllib.urlopen(api, params)
        status = f.getcode()
        if status == 200:
            return True
        return False
            
   
class Blogger:

  def __init__(self, email, password):
    """Creates a GDataService and provides ClientLogin auth details to it.
    The email and password are required arguments for ClientLogin.  The
    'source' defined below is an arbitrary string, but should be used to
    reference your name or the name of your organization, the app name and
    version, with '-' between each of the three values."""

    # Authenticate using ClientLogin.
    self.service = service.GDataService(email, password)
    self.service.source = 'Blogger_Python_Sample-1.0'
    self.service.service = 'blogger'
    self.service.server = 'www.blogger.com'
    self.service.ProgrammaticLogin()

    # Get the blog ID for the first blog.
    feed = self.service.Get('/feeds/default/blogs')
    self_link = feed.entry[0].GetSelfLink()
    if self_link:
      self.blog_id = self_link.href.split('/')[-1]
    print  "Blog ID %s " % self.blog_id


  def PrintUserBlogTitles(self):
    """Prints a list of all the user's blogs."""

    # Request the feed.
    query = service.Query()
    query.feed = '/feeds/default/blogs'
    feed = self.service.Get(query.ToUri())

    # Print the results.
    print feed.title.text
    for entry in feed.entry:
      print "\t" + entry.title.text
    print

  def CreatePost(self, title, content, author_name, tags,is_draft):
    """This method creates a new post on a blog.  The new post can be stored as
    a draft or published based on the value of the is_draft parameter.  The
    method creates an GDataEntry for the new post using the title, content,
    author_name and is_draft parameters.  With is_draft, True saves the post as
    a draft, while False publishes the post.  Then it uses the given
    GDataService to insert the new post.  If the insertion is successful, the
    added post (GDataEntry) will be returned.
    """

    # Create the entry to insert.
    entry = gdata.GDataEntry()
    entry.author.append(atom.Author(atom.Name(text=author_name)))
    entry.title = atom.Title(title_type='xhtml', text=title)
    entry.content = atom.Content(content_type='html', text=content)
    for tag in tags :
      category = atom.Category(term=tag, scheme="http://www.blogger.com/atom/ns#")
      entry.category.append(category)

    if is_draft:
      control = atom.Control()
      control.draft = atom.Draft(text='yes')
      entry.control = control

    # Ask the service to insert the new entry.
    return self.service.Post(entry, 
      '/feeds/' + self.blog_id + '/posts/default')

  def PrintAllPosts(self):
    """This method displays the titles of all the posts in a blog.  First it
    requests the posts feed for the blogs and then it prints the results.
    """

    # Request the feed.
    feed = self.service.GetFeed('/feeds/' + self.blog_id + '/posts/default')

    # Print the results.
    print feed.title.text
    for entry in feed.entry:
      if not entry.title.text:
        print "\tNo Title"
      else:
        print "\t" + entry.title.text
    print

  def PrintPostsInLastWeek(self):
    """This method displays the title and modification time for any posts that
    have been created or updated in the period between the start_time and
    end_time parameters.  The method creates the query, submits it to the
    GDataService, and then displays the results.
  
    Note that while the start_time is inclusive, the end_time is exclusive, so
    specifying an end_time of '2007-07-01' will include those posts up until
    2007-6-30 11:59:59PM.
    The start_time specifies the beginning of the search period (inclusive),
    while end_time specifies the end of the search period (exclusive).
    """

    # Create query and submit a request.
    query = service.Query()
    query.feed = '/feeds/' + self.blog_id + '/posts/default'
    end_time =  datetime.strftime(datetime.now(), "%Y-%m-%d")
    start_time   =  datetime.strftime(datetime.now() + timedelta( days = -7 ), "%Y-%m-%d")    
    print  start_time  ,  end_time
    query.updated_min = start_time
    query.updated_max = end_time
    query.orderby = 'updated'
    feed = self.service.Get(query.ToUri())
    try: 
      import simplejson as json
    except:
      import json
    out  =  [ {'selected'   : False  ,    'updated_text'  :    entry.updated.text  or  ""  , 'updated_summary'  :    entry.summary.text   or  ""  ,
        'article_body'  :   entry.content.text or  ""  ,'article_title'  :    entry.article.text  or  ""  }
        for    entry  in   feed.entry   ]
    print json.dumps(out)


    
    html = html + template.render (templatepath + 'newsletter_start.html', {})
    html = html + template.render (templatepath + 'newsletter_js.html', {})               
    html = html + """<table width="500" class='out' border="1" data-dynamic="%s">""" % json.dumps(your_generated_data_dict)
    f =  open( 'c:/xampp/htdocs/newsletter.php'  , 'w')
    f.write(html)
    f.close()                
    

  def UpdatePostTitle(self, entry_to_update, new_title):
    """This method updates the title of the given post.  The GDataEntry object
    is updated with the new title, then a request is sent to the GDataService.
    If the insertion is successful, the updated post will be returned.

    Note that other characteristics of the post can also be modified by
    updating the values of the entry object before submitting the request.

    The entry_to_update is a GDatEntry containing the post to update.
    The new_title is the text to use for the post's new title.  Returns: a
    GDataEntry containing the newly-updated post.
    """
    
    # Set the new title in the Entry object
    entry_to_update.title = atom.Title('xhtml', new_title)
    
    # Grab the edit URI
    edit_uri = entry_to_update.GetEditLink().href  

    return self.service.Put(entry_to_update, edit_uri)

  def CreateComment(self, post_id, comment_text):
    """This method adds a comment to the specified post.  First the comment
    feed's URI is built using the given post ID.  Then a GDataEntry is created
    for the comment and submitted to the GDataService.  The post_id is the ID
    of the post on which to post comments.  The comment_text is the text of the
    comment to store.  Returns: an entry containing the newly-created comment

    NOTE: This functionality is not officially supported yet.
    """

    # Build the comment feed URI
    feed_uri = '/feeds/' + self.blog_id + '/' + post_id + '/comments/default'

    # Create a new entry for the comment and submit it to the GDataService
    entry = gdata.GDataEntry()
    entry.content = atom.Content(content_type='xhtml', text=comment_text)
    return self.service.Post(entry, feed_uri)

  def PrintAllComments(self, post_id):
    """This method displays all the comments for the given post.  First the
    comment feed's URI is built using the given post ID.  Then the method
    requests the comments feed and displays the results.  Takes the post_id
    of the post on which to view comments. 
    """

    # Build comment feed URI and request comments on the specified post
    feed_url = '/feeds/' + self.blog_id + '/comments/default'
    feed = self.service.Get(feed_url)

    # Display the results
    print feed.title.text
    for entry in feed.entry:
      print "\t" + entry.title.text
      print "\t" + entry.updated.text
    print

  def DeleteComment(self, post_id, comment_id):
    """This method removes the comment specified by the given edit_link_href, the
    URI for editing the comment.
    """
    
    feed_uri = '/feeds/' + self.blog_id + '/' + post_id + '/comments/default/' + comment_id
    self.service.Delete(feed_uri)

  def DeletePost(self, edit_link_href):
    """This method removes the post specified by the given edit_link_href, the
    URI for editing the post.
    """

    self.service.Delete(edit_link_href)
  
  def doBloggerActivity(self , article_title ,  article_desc  ,  article_author   , article_category ):
    """Runs each of the example methods defined above, demonstrating how to
    interface with the Blogger service.article_comment , article_title , article_desc  , article_category 
    """

    # Demonstrate retrieving a list of the user's blogs.
    self.PrintUserBlogTitles()
  
    # Demonstrate how to create a post  with   title, content, author_name, tags,is_draft
    #draft_post = self.CreatePost(article_title , article_desc  , article_author , ''  , True)
    #print "Successfully created draft post: \"" + draft_post.title.text + "\".\n"
  
    # Demonstrate how to publish a public post.
    #public_post = self.CreatePost(article_title , article_desc  , article_author , ''  , True)
    #print "Successfully created public post: \"" + public_post.title.text + "\".\n"
    
    print "Now listing all posts in last  week"
    #self.PrintPostsInLastWeek() 
    

  
def   markDirectoryAsProcessed(dirName):
  f =open (os.path.join(dirName , 'processed') , 'w')
  f.close()

  
# This file cache is thread-safe
class BookMarkCache:
    def __init__(self, fileName  , blg , twt ):
            self.fileName =  fileName 
            self.blogger  =  blg
            self.tweet  =  twt
            self.listBookMark =[]
            self.lock = threading.Lock()
                
    def get(self, bookmark_id, default=None):
        with self.lock:
            retval = default
            try:
                f = file(self.fileName, 'r')
                retval = pickle.load(f)
                f.close()                
            except IOError: pass
            return retval
    def __getitem__(self, bookmark):
        return self.get(key)
    def __setitem__(self, bookmark_id, hashval):
        with self.lock:
            f = open(self.fileName, 'wb')
            value ={'bookmark_id'  :   bookmark_id ,  'hashval'  :  hashval  }  
            pickle.dump(value.__dict__, f)
            f.close()
    def addToCache(self, bookmark):
        with self.lock:
            f = open(self.fileName, 'wb')
            pickle.dump({'selected'   : False  ,   'bookmark_id'  :    bookmark['bookmark_id']   ,   'category'  :    bookmark['category']  , 'hashval'  :    bookmark['hashval'] ,  'description'  :    bookmark['description']  ,
        'title'  :   bookmark['title']  , 'url'  :    bookmark['url'] }, f)
            f.close()


def main():
      blogger_email = ''
      blogger_password = ''
      insta_user = ''
      insta_password = ''
      mailchimp_user  = ''
      mailchimp_password  = ''
      postdir = '.'
      create_newsletter = True
      try:
        opts, args = getopt.getopt(sys.argv[1:], " ", ["blogger_email=","blogger_password=","insta_user=","insta_password=","mailchimp_user=","mailchimp_password=","postdir=","create_newsletter=" ])
      except getopt.error, msg:
        print ('python NewLetterUtil.py --blogger_email [blogger_email] --blogger_password [blogger_password] --insta_user [insta_user] --insta_password [insta_password]  --mailchimp_user [mailchimp_user]    --mailchimp_password [mailchimp_password]   --postdir  [postdir]  --create_newsletter [create_newsletter]')
        print ('Failed    to parse   arguments ' +   msg)
        sys.exit(2)
     
      # Process options
      for o, a in opts:
        if o == "--blogger_email":
          blogger_email = a
        elif o == "--blogger_password":
          blogger_password = a
        elif o == "--insta_user":
          insta_user = a
        elif o == "--insta_password":
          insta_password = a
        elif o == "--mailchimp_user":
          mailchimp_user = a
        elif o == "--mailchimp_password":
          mailchimp_password = a
        elif o == "--postdir":
          postdir = a
        elif o == "--create_newsletter":
          create_newsletter =  a 
        else :
          continue
      print  " Blogger Email  :  %s  \n  Blogger  Password  :  %s  \n Insta  User  :  %s \n  Insta password  %s \n   Mailchimp  User  :  %s  \n Mailchimp  password  : %s \nBlogger PostDir : %s\n   Create_NewsLetter : %s \n"  %(  blogger_email  , blogger_password  , insta_user ,    insta_password ,  mailchimp_user ,  mailchimp_password ,  postdir ,  create_newsletter   )
      if  blogger_email == '' or blogger_password == ''  or   insta_user == ''  or  insta_password == ''   or   mailchimp_user  == ''  or  mailchimp_password  == ''  or  postdir == '' :
            print ('python NewLetterUtil.py --blogger_email [blogger_email] --blogger_password  [blogger_password]   --insta_user  [insta_user] --insta_password [insta_password]  --mailchimp_user [mailchimp_user] --mailchimp_password [mailchimp_password]   --postdir  [postdir]  --create_newsletter [create_newsletter]  ')
            sys.exit(2)
      twt=  Twitter()
      blg = Blogger(blogger_email, blogger_password)
      cache = BookMarkCache("instapaper.pickle"  , blg ,  twt  )

      class BookMark:
          def __init__(self, bookmark_id,description ,url , title , category, hashval):
            self.bookmark_id = bookmark_id
            self.hashval = hashval
            self.description = description
            self.url= url
            self.title  = title
            self.category  = category
            blg.doBloggerActivity(  self.title.replace("\"", "")   ,self.description.replace("\"", "") + '  '  +   urllib.unquote_plus(self.url).replace("\"", "")  , 'Kabir   Seth' ,self.category   )
            twt.sendTweet(   self.title.replace("\"", "")    + '  ' +   self.description.replace("\"", "") + '  '  +   urllib.unquote_plus(self.url).replace("\"", "")) , 'Kabir   Seth' ,  self.category    
          def __str__(self):
            return 'BookMark ID  : %s, Bookmark Hashval :%s ,  desc :  %s    ,  url:  %s   ,Title   :  %s  , Category  :  %s   ' % (self.bookmark_id,  self.description , self.url , self.title , self.category, self.hashval)
          def __getitem__(self, bookmark_id):
              try  :
                  return[{ 'selected'   : False  ,   'bookmark_id'  :  entry['bookmark_id']   ,    'category'   :   entry['category']  , 'hashval' :  entry['hashval']   ,  'description' :   entry['description']  ,   'title'  :  entry['title'] ,  'url'  :   entry['url'] }  for    entry   in   cache.listBookMark  if  entry['bookmark_id']  ==  bookmark_id    ][0]
              except :
                   return None
      
      out =[]
      ip  = Instapaper('instapaper', insta_user ,insta_password)
      listBookMark = ip.getAllBookMarks()
      print  listBookMark
      print  len(listBookMark)
      try: 
          import simplejson as json
      except:
           import json
      out  =[{'selected'   : False  ,   'bookmark_id'  :    entry['bookmark_id']  or  ""  ,   'category'  :    entry['category']  or  ""  , 'hashval'  :    entry['hashval'] ,  'description'  :    entry['description']   or  ""  ,
        'title'  :   entry['title'] or  ""  , 'url'  :    entry['url']  or  ""  } for    entry  in   listBookMark  ]
      print listBookMark
      print json.dumps(out)
      templatepath ="c:/xampp/htdocs/newsletter"
      html = file('%s/preheader.htm'%templatepath, 'r').read()
      html = html +  file('%s/header.htm'%templatepath, 'r').read()               
      html = html + """<table width="500" class='out' border="1" data-dynamic="%s">""" % json.dumps(out)
      html = html + file('%s/footer.htm'%templatepath, 'r').read()
      
      f =  open( 'c:/xampp/htdocs/newsletter.html'  , 'w')
      f.write(html)
      f.close()
      print  "Boookmarks   are   %d  "%    len(listBookMark)
      for  bookmark   in  listBookMark :         
            bmk  = BookMark( bookmark['bookmark_id'] ,   bookmark['category'] ,   bookmark['hashval']  ,   bookmark['description'] ,   bookmark['title'] ,  bookmark['url'] )
            cache.addToCache(bmk)
            print  repr(bmk)
                            
      url = 'http://localhost/newsletter.php'
      webbrowser.open_new(url)

if __name__ == '__main__':
  main()

