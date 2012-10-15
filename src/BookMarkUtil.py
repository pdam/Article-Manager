#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import with_statement

import csv, shutil
import sys, pickle,unicodedata
import atom
import urllib
import tweepy.oauth
import time
from ConfigParser import SafeConfigParser
from oauth2 import Consumer, Client, Token
sys.path.append(".")
import cgi
import mimetypes
import getopt
import  os, re
import  simplejson
from urlparse import urlparse
from datetime import datetime, timedelta
import  webbrowser
import gdata
from  gdata import service 
import json
from  instapaper  import  Instapaper
import urllib2
__author__ = 'pdam.2010@gmail.com'
__version__ ='0.0.1'




# Extract real version number if necessary
if __version__[0] == '$':
    _v = __version__.split()
    if len(_v) == 3:
        __version__ = _v[1]


# Tunable parameters
DEFROOT = "file:/c\\xampp\\htdocs"   # Default root URL
CHECKEXT = 1                            # Check external references (1 deep)
VERBOSE = 1                             # Verbosity level (0-3)
MAXPAGE = 150000                        # Ignore files bigger than this
ROUNDSIZE = 50                          # Number of links processed per round
DUMPFILE = "@instapaper.pickle"         # Pickled checkpoint
AGENTNAME = "pdam"                      # Agent name for robots.txt parser
NONAMES = 0                             # Force name anchor checking
TWITTER_REQUEST_TOKEN_URL   = 'https://api.twitter.com/oauth/request_token'
TWITTER_ACCESS_TOKEN_URL    = 'https://api.twitter.com/oauth/access_token'
TWITTER_AUTHORIZE_URL       = 'https://api.twitter.com/oauth/authorize'
TWITTER_UPDATE_URL          = 'http://api.twitter.com/1/statuses/update.json'
TWITTER_CONFIG =   'twitter.conf'
checkext = CHECKEXT
verbose = VERBOSE
maxpage = MAXPAGE
roundsize = ROUNDSIZE
dumpfile = DUMPFILE
restart = 0
norun = 0
extra_roots = []
nonames = NONAMES

class PersistentDict(dict):
    ''' Persistent dictionary with an API compatible with shelve and anydbm.

    The dict is kept in memory, so the dictionary operations run as fast as
    a regular dictionary.

    Write to disk is delayed until close or sync (similar to gdbm's fast mode).

    Input file format is automatically discovered.
    Output file format is selectable between pickle, json, and csv.
    All three serialization formats are backed by fast C implementations.'''

    def __init__(self, filename ,flag='c', mode=None, format='pickle', *args, **kwds):
        self.flag = flag                    # r=readonly, c=create, or n=new
        self.mode = mode                    # None or an octal triple like 0644
        self.format = format                # 'csv', 'json', or 'pickle'
        self.filename = filename
        if flag != 'n' and os.access(filename, os.R_OK):
            fileobj = open(filename, 'rb' if format=='pickle' else 'r')
            with fileobj:
                self.load(fileobj)
        dict.__init__(self, *args, **kwds)

    def sync(self):
        'Write dict to disk'
        if self.flag == 'r':
            return
        filename = self.filename
        tempname = filename + '.tmp'
        fileobj = open(tempname, 'wb' if self.format=='pickle' else 'w')
        try:
            self.dump(fileobj)
        except Exception:
            os.remove(tempname)
            raise
        finally:
            fileobj.close()
        shutil.move(tempname, self.filename)    # atomic commit
        if self.mode is not None:
            os.chmod(self.filename, self.mode)

    def close(self):
        self.sync()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()

    def dump(self, fileobj):
        if self.format == 'csv':
            csv.writer(fileobj).writerows(self.items())
        elif self.format == 'json':
            json.dump(self, fileobj, separators=(',', ':'))
        elif self.format == 'pickle':
            pickle.dump(dict(self), fileobj, 2)
        else:
            raise NotImplementedError('Unknown format: ' + repr(self.format))

    def load(self, fileobj):
        # try formats from most restrictive to least restrictive
        for loader in (pickle.load, json.load, csv.reader):
            fileobj.seek(0)
            try:
                return self.update(loader(fileobj))
            except Exception:
                pass
        raise ValueError('File not in a supported format')
    

"""
Utilities  included

Report printed:

When done, it reports  no of   messages  that   were created  for  Blogger or  Twitter
.  When  interrupted, it reports for the pages that it has created  .

In verbose mode, additional messages are printed during the
information gathering phase.  By default, it prints a summary of its
work status every 50 Articles (adjustable with the -r option), and it
reports errors as they are encountered.  Use the -q option to disable
this output.

Checkpoint feature:

Whether interrupted or not, it dumps its state (a Python pickle) to a
checkpoint file and the -R option allows it to restart from the
checkpoint (assuming that the pages on the subweb that were already
processed haven't changed).  Even when it has run till completion, -R
can still be useful -- it will print the reports again, and -Rq prints
the errors only.  In this case, the checkpoint file is not written
again.  The checkpoint file can be set with the -d option.

The checkpoint file is written as a Python pickle.  Remember that
Python's pickle module is currently quite slow.  Give it the time it
needs to load and save the checkpoint file.  When interrupted while
writing the checkpoint file, the old checkpoint file is not
overwritten, but all work done in the current run is lost.

Usage: BookMarkUtil.py [option] ... [rooturl] ...

Options:

-R        -- restart from checkpoint file
-d file   -- checkpoint filename (default %(DUMPFILE)s)
-n        -- reports only, no checking (use with -R)
-q        -- quiet operation (also suppresses external links report)
-r number -- number of links processed per round (default %(ROUNDSIZE)d)
-t root   -- specify root dir which should be treated as internal (can repeat)
-v        -- verbose operation; repeating -v will increase verbosity
-blogger_email --  Username   used   in www.blogger.com
-blogger_password  -- Password   used   in www.blogger.com
-insta_user  -- Username  used   with InstaPapeer   API
-insta_password -- Password  used   with InstaPaper   API
-mailchimp_user --  Username   used   to  create  a mailchimp  newsletter
-mailchimp_password -- Password  used   with InstaPaper   API
-create_newsletter   -- Generate  the  HTML for  creaing  a newsletter 



"""



contentPhp="""
<?php if(!isset($_POST[$articleList]) || (isset($_POST[$articleList]) && empty($_POST[$articleList])) || isset($_POST[$articleList]) && $_POST[$articleList]<0)
    { 
    
    for ($i=0;isset($_POST($articleList[$i]));$i++) {
       if  ( $_POST[$articleList[$i]['selOpt']] == 'on' )  {
             $contents  =  $contents . '<tr><td>' .$_POST[$articleList[$i]['date']] .'</td><td>' .$_POST[$articleList[$i]['title']] . '</td><td>' . $_POST[$articleList[$i]['body']] . '</td></tr>' ;
             
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




class   Twitter(object):
    
    def  __init__(self):
        self._config = SafeConfigParser()
        self._config.read(TWITTER_CONFIG)    
        self.consumer_key = self._config.get('twitter','consumer_keys')
        self.consumer_secret = self._config.get('twitter','consumer_secret')
        self.access_key = self._config.get('twitter','access_keys')
        self.access_secret = self._config.get('twitter','access_secret')
        self.request_token ={  'oauth_token'  : ''  ,  'oauth_token_secret' : ''  }
        self.access_token ={  'oauth_token'  : ''  ,  'oauth_token_secret' : ''  }
       
    
    def  doSetup(self ):
        print 'Running twitter setup...'
        consumer = Consumer(self.consumer_key, self.consumer_secret)
        print   consumer  
        client = Client(consumer)
        resp, content = client.request(TWITTER_REQUEST_TOKEN_URL, "GET")
        if resp['status'] != '200':
            raise Exception("Invalid response %s." % resp['status'])

        self.request_token = dict(urlparse(content))
        print "Request Token:"
        print "    - oauth_token        = %s" % self.request_token['oauth_token']
        print "    - oauth_token_secret = %s" % self.request_token['oauth_token_secret']
        print

        # Step 2: Redirect to the provider. Since this is a CLI script we do not
        # redirect. In a web application you would redirect the user to the URL
        # below.

        print "Go to the following link in your browser:"
        print "%s?oauth_token=%s" % (TWITTER_AUTHORIZE_URL, self.request_token['oauth_token'])
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
        token = Token(self.request_token['oauth_token'],
            self.request_token['oauth_token_secret'])
        token.set_verifier(oauth_verifier)
        client = Client(consumer, token)

        resp, content = client.request(TWITTER_ACCESS_TOKEN_URL, "POST")
        self.access_token = dict(urlparse(content))

        print "Access Token:"
        print "    - oauth_token        = %s" % self.access_token['oauth_token']
        print "    - oauth_token_secret = %s" % self.access_token['oauth_token_secret']
        print
        print "You may now access protected resources using the access tokens above."





    def SendMsg(self, update):
        token = Token(key=self.access_key, secret=self.access_secret)
        consumer =Consumer(key=self.consumer_key, secret=self.consumer_secret)
        client = Client(consumer, token)
        request_uri = 'https://api.twitter.com/1/statuses/update.json'
        data = {u'status': unicodedata.normalize('NFKD', update[:140]).encode('ASCII', 'ignore')}
        resp= client.request(request_uri, 'POST', urllib.urlencode(data))[0]
        print resp.content 
        print resp.status


    def  sendTweet(self, message ):
        if not self.consumer_key or not self.consumer_secret or not self.access_key or not self.access_secret:
            self.doSetup()
        else:
            self.SendMsg(message)

     

                
class InstapaperError(Exception):
    pass

class Instapaper(object):
    def __init__(self, fileName , username, password):
        self._username = username
        self.fileName =  fileName
        self._password = password
        self.listBookMarks =[]
        self.verbose = 0
        self.roundsize =  50
        self.changed  =0  
        
        
    def AddWebBookMark(self, folder  , article_name , article_title , article_url  ,article_desc):
        """Invoke  Jmeter  passing the   right  arguments ."""
        article_name , article_title , article_url  ,article_desc   =   re.sub('\n' ,  '<BR/>' , article_name) ,re.sub('\n' ,  '<BR/>' ,article_title) , re.sub('\n' ,  '' ,article_url)  ,re.sub('\n' ,  '<BR/>' ,article_desc)
        cmd   =   "C:/java/apache-jmeter-2.6/bin/jmeter.bat -Jinsta_user=\"%s\" -Jinsta_password=\"%s\" -Jfname=\"%s\"  -Jarticle_name=\"%s\"  -Jarticle_title=\"%s\"  -Jarticle_url=\"%s\"  -Jarticle_desc=\"%s\"  -n  -t  InstaP.jmx -l  log_%s.jtl " %( self.insta_user  , self.insta_password , folder  , article_name , article_title , article_url  ,article_desc , time.strftime("%Y%m%d%H%M%S", time.localtime()) )
        print cmd
        os.system(cmd)


    def auth(self):
        if self._username is  None:
            return self._do_auth(self._username, self._password)
        if self._password  is  None:
            return self._do_auth(self._username, self._password)
        return False


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
        print self.listBookMarks
        return  self.listBookMarks
            

        
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
        self.listChangedBookMarks=[]
        params = {
            'username': self._username,
            'password': self._password,
            'folder_id' :  folder_id}
        params = urllib.urlencode(params)
        request = urllib2.Request(api, params)
        outL =  json.loads(urllib2.urlopen(request).read(),'utf-8')
        for   x  in   outL :
            if  x.has_key('hash') : 
                self.listChangedBookMarks.append({ "bookmark_id": x['bookmark_id']  , "url"   : x['url']    ,  "title"  :  x['title']   ,  "description"  :   x['description']   , "hashval" :   x['hash'] ,    'category':   category  })

        print  self.listChangedBookMarks
    

    
    def __getstate__(self):
        return (self.roots, self.todo, self.done, self.bad, self.round)

    def __setstate__(self, state):
        self.reset()
        (self.listBookMarks, self.todo, self.done, self.bad, self.round) = state
        for root in self.listBookMarks:
            self.addrobot(root)
            
    def load_pickle(self, dumpfile, verbose=VERBOSE):
            if verbose > 0:
                print "Loading checkpoint from %s ..." % dumpfile
            f = open(dumpfile, "rb")
            c = pickle.load(f)
            f.close()
            if verbose > 0:
                print "Done."
                print "BookMarks:", "\n      ".join(c.listBookMarks)
            return c


    def run(self):
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
        print("")   
        

    def doBookMark(self, bookmarkDict):

        # All printing of URLs uses format_url(); argument changed to
        # bookmarkDict for clarity.
        if self.verbose > 1:
            if self.verbose > 2:
                self.show("Check ", self.format_url(bookmarkDict),
                          "  from", self.todo[bookmarkDict])
            else:
                print("Check %s", self.format_url(bookmarkDict))
        url, local_bookmark_id = bookmarkDict
        if local_bookmark_id and self.nonames:
            self.markdone(bookmarkDict)
            return
        try:
            bookmark = self.getBookMark(bookmarkDict)
        except ValueError, msg:
            msg = self.sanitize(msg)
            print(0, "Error parsing %s: %s",
                          self.format_url(bookmarkDict), msg)
            # Dont actually mark the URL as bad - it exists, just
            # we can't parse it!
            bookmark = None
        if bookmark:
            # Store the hash which corresponds to this bookmark.
            self.bookmark_table[BookMark.bookmark_id] = bookmark.hash
            for bookmark_info in bookmark.getlinkinfos(BookMark.bookmark_id):
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
        print(3, "  Done bookmark %s", self.format_url(url))

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
            print(3, "  Seen todo bookmark %s", self.format_url(url))
        else:
            self.todo[url] = [bookmark_id]
            print(3, "  New todo bookmark %s", self.format_url(url))

    def format_url(self, url):
        bookmark, bookmark_id = url
        if bookmark_id: return bookmark + "#" + bookmark_id
        else: return bookmark

    def markdone(self, url):
        self.done[url] = self.todo[url]
        del self.todo[url]

    def inroots(self, url):
        for bookmark in self.listBookMarks:
            if bookmark['bookmark_id'] == BookMark.bookmark_id:
                return self.isallowed(bookmark, BookMark.bookmark_id)
        return 0

    def isallowed(self, root, url):
        root = urllib2.urlparse(root, "/")
        return self.robots[root].can_fetch(AGENTNAME, url)

    def getBookMark(self, bookmark):
        # Incoming argument name is a (bookmark_id  , hashval ) pair.
        # The bookmark may have existed  in the bookmark_table variable.
        bookmark_id ,  hashval = bookmark['bookmark_id'] , bookmark['hashval'] 
        if self.bookmark_table.has_key(bookmark_id):
            return self.bookmark_table[bookmark_id]

        scheme= urllib.splittype(url)[0]
        if scheme in ('mailto', 'news', 'javascript', 'telnet'):
            print(1, " Not checking %s URL" % scheme)
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
            print(1, " Redirected to %s", nurl)
        if text:
            return BookMark(hashval, bookmark_id,  Instapaper=self.instapaper)

    # These next three functions take (URL, bookmark_id) pairs as
    # arguments, so that open_bookmark() receives the appropriate tuple to
    # record error messages.
    def readhtml(self, bookmarkDict):
        text = None
        f, url = self.openhtml(bookmarkDict)
        if f:
            text = f.read()
            f.close()
        return text, url

    def openhtml(self, bookmarkDict):
        url = bookmarkDict(0)
        f = self.open_bookmark(bookmarkDict)
        if f:
            url = f.geturl()
            info = f.info()
            if not self.checkforhtml(info, url):
                self.safeclose(f)
                f = None
        return f, url

    def open_bookmark(self, bookmarkDict):
        url, = bookmarkDict(0)
        try:
            return self.urlopener.open(url)
        except (OSError, IOError), msg:
            msg = self.sanitize(msg)
            print(0, "Error %s", msg)
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
            ctype = mimetypes.guess_type(url)[0]
        if ctype == 'text/html':
            return 1
        else:
            print(1, " Not HTML, mime type %s", ctype)
            return 0

    def setgood(self, url):
        if self.bad.has_key(url):
            del self.bad[url]
            self.changed = 1
            print(0, "(Clear previously seen error)")

    def setbad(self, url, msg):
        if self.bad.has_key(url) and self.bad[url] == msg:
            print(0, "(Seen this error before)")
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
        print("%s %s", p1, bookmark)
        i = 0
        for source, rawlink in bookmark_ids:
            i = i+1
            if i == 2:
                p2 = ' '*len(p2)
            if rawlink != bookmark: s = " (%s)" % rawlink
            else: s = ""
            print("%s %s%s", p2, source, s)

    def sanitize(self, msg):
        if isinstance(IOError, type.ClassType) and isinstance(msg, IOError):
            # Do the other branch recursively
            msg.args = self.sanitize(msg.args)
        elif isinstance(msg, type.TupleType):
            if len(msg) >= 4 and msg[0] == 'http error' and \
               isinstance(msg[3], type.InstanceType):
                # Remove the Message instance -- it may contain
                # a file object which prevents pickling.
                msg = msg[:3] + msg[4:]
        return msg

    def safeclose(self, f):
        try:
            f.geturl()
        except AttributeError:
            pass
        else:
            f.close()

    def save_pickle(self, dumpfile):
        if not self.changed:
            print(0, "\nNo need to save checkpoint")
        elif not dumpfile:
            print(0, "No dumpfile, won't save checkpoint")
        else:
            print(0, "\nSaving checkpoint to %s ...", dumpfile)
            newfile = dumpfile
            f = open(newfile, "wb")
            pickle.dump(self, f)
            f.close()
            try:
                os.unlink(dumpfile)
            except os.error:
                pass
            os.rename(newfile, dumpfile)
            print(0, "Done.")
            return 1
    
        
    def _query(self, url=None, params=""):
        """ method to query a URL with the given parameters
        Parameters:
        url -> URL to query
        params -> dictionary with parameter values

        Returns: HTTP response code, headers
        If an exception occurred, headers fields are None
        """
        if url is None:
            raise Exception("No URL was provided.")
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
            
   
class Blogger(object):
    
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
        query = service.Query()
        query.feed = '/feeds/default/blogs'
        feed = self.service.Get(query.ToUri())
    
        # Print the results.
        print feed.title.text
        for entry in feed.entry:
            print "\t" + entry.title.text

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
        fd =  open( 'c:/xampp/htdocs/template.html'  , 'r')
        content   = fd.read()
        fContent =""
        fd.close()
        rowContent =""
        count =0
        for entry in feed.entry:
            count+=1 
            try :
                article_update =entry.updated.text
            except:
                article_update =   ""
            try :
                article_summary =entry.summary.text
            except:
                article_summary =   ""
    
            try :
                article_body =  entry.content.text
            except:
                article_body =   ""
            
            try :
                article_title = entry.title.text
            except:
                article_title =   "" 
                
            rowContent  += """<table>
                       <tr>
                       <td><input type="checkbox" name="articleList[%d]['selOpt']" value="on" /></td>
    
                       <td><input type="text" name="<?php echo "articleList[%d]['date']"; ?>" value="%s" /></td>
    
                       <td><input type="text" name="<?php echo "articleList[%d]['summary']"; ?>" value="%s" /></td>
                       
                       <td><input type="text" name="<?php echo "articleList[%d]['title']"; ?>" value="%s"  /></td>
    
                       <td><input type="text" name="<?php echo "articleList[%d]['body']"; ?>"  value="%s"  /></td>
    
                       </tr>
    
                       </table>"""%( count  ,  count  ,  article_update  ,  count  ,  article_summary  , count , article_title ,  count ,  article_body )   
        fContent += content % (  rowContent , contentPhp)
        print  fContent 
        f =  open( 'c:/xampp/htdocs/newsletter.php'  , 'w')
        f.write(fContent)
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
        self.PrintPostsInLastWeek() 
    
class BookMark(object):
    def __init__(self, bookmark):
        self.bookmark_id = bookmark['bookmark_id']
        self.hash = bookmark['hashval']
        self.description = bookmark['description']
        self.url= bookmark['url']
        self.title  = bookmark['title']
        self.category  = bookmark['category']
        if  self.bookmark_id !=  None: 
            ip.blg.doBloggerActivity(  bookmark['title']  , bookmark['description']  ,  urllib.unquote_plus(bookmark['url']) ,   bookmark['category'] )
            ip.twt.sendTweet(  u'%s  %s  %s' %  (bookmark['title'] ,  bookmark['description']  ,  bookmark['url'] ) )   

    def __str__(self):
        return 'BookMark ID  : %s, Bookmark Hash :%s ' % (self.bookmark_id, self.hash)


    


# This file cache is thread-safe
class BookMarkCache(object):
    def get(self, bookmark_id, default=None):
        with self.lock:
            with open('instapaper.pickle', 'rb') as f:
                try:
                    print f.read()
                    return f.read()
                except IOError:
                        "print  %r  "% repr(f)
                else :
                    print  f.read()
                    
    def __getitem__(self, bookmark_id):
        return self.get(bookmark_id)
    def __setitem__(self, bookmark_id, hashval):
        with PersistentDict('instapaper.pickle'  , 'hashval'  , format='pickle') as d:
            print(d, 'start')
            d   =  {  'bookmark_id' :bookmark_id   ,  'hash' : hashval  }
            print(d, 'updated')

             
        with open('instapaper.pickle', 'rb') as f:
            print(f.read())
        
                   
    def __init__(self, instapaper=None, fileName='instapaper.pickle' , verbose=VERBOSE):
        self.fileName  = fileName
        self.verbose = verbose
        self.instapaper = instapaper
        try :
            with open('instapaper.pickle', 'rb') as f:
                print(f.read())        
        except:
            f =  open('instapaper.pickle', 'wb') 
        finally:
            f.close()
            
            
        
    def note(self, level, msg, *args):
        if self.Instapaper:
            apply(self.Instapaper.note, (level, msg) + args)
        else:
            if self.verbose >= level:
                if args:
                    msg = msg%args
                print msg

    # Method to retrieve names.
    def getnames(self):
        if self.parser:
            return self.parser.names
        else:
            return []





 



    



time_fmt = "%Y-%m-%d %H:%M"

verbose =10

try:
    opts, args = getopt.getopt(sys.argv[1:], "Rdqv", ["blogger_email=","blogger_password=","insta_user=","insta_password=","mailchimp_user=","mailchimp_password=","create_newsletter=" ])
except getopt.error, msg:
    sys.stdout = sys.stderr
    print msg
    sys.exit(2)

for o, a in opts:
    if o == '--R':
        restart = 1
    if o == '--d':
        dumpfile = a
    if o == '--q':
        verbose = 0
    if o == '--v':
        verbose = verbose + 1
    if o == "--blogger_email":
        blogger_email = a
    if o == "--blogger_password":
        blogger_password = a
    if o == "--insta_user":
        insta_user = a
    if o == "--insta_password":
        insta_password = a
    if o == "--mailchimp_user":
        mailchimp_user = a
    if o == "--mailchimp_password":
        mailchimp_password = a
    if o == "--create_newsletter":
        create_newsletter =  a 



if verbose > 0:
    print AGENTNAME, "version", __version__
    print  " Blogger Email  :  %s  \n  Blogger  Password  :  %s  \n Insta  User  :  %s \n  Insta password  %s \n   Mailchimp  User  :  %s  \n Mailchimp  password  : %s \n   Create_NewsLetter : %s \n"  %(  blogger_email  , blogger_password  , insta_user ,    insta_password ,  mailchimp_user ,  mailchimp_password ,   create_newsletter   )



if  blogger_email == '' or blogger_password == ''  or   insta_user == ''  or  insta_password == ''   or   mailchimp_user  == ''  or  mailchimp_password  == '' :
    print ('python NewLetterUtil.py --blogger_email [blogger_email] --blogger_password  [blogger_password]   --insta_user  [insta_user] --insta_password [insta_password]  --mailchimp_user [mailchimp_user] --mailchimp_password [mailchimp_password]   --postdir  [postdir]  --create_newsletter [create_newsletter]  ')
    sys.exit(2)

dumpFile="instapaper.pickle";
ip = Instapaper(dumpfile , insta_user,insta_password)
cache = BookMarkCache(dumpFile)
bookMarkList =  ip.getAllBookMarks()
print bookMarkList
for b in bookMarkList  :
    bmk  = BookMark(b)
    cache[bmk] = { 'bookmark_id'  :  b['bookmark_id'] ,  'hashval'  :   b['hashval']  }
    entry = cache.get(b['bookmark_id'])
    ip.run()
    ip.save_pickle('instapaper.pickle')
url = 'http://localhost/newsletter.php'





webbrowser.open_new(url)










