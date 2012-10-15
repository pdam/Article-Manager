#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'pdam.2010@gmail.com'



import atom
import getopt
import sys
import  os, re
import simplejson
from datetime import datetime, date, time, timedelta
import time
from  ConfigParser  import ConfigParser
import  webbrowser
import argparse
import gdata
from  gdata import service 
import struct
import sys
import tweepy
from ConfigParser import SafeConfigParser




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

consumer_key='jj0v13SvciKXLZsTIw3Lw'
consumer_secret='F4fB5QS9D6QnYf123Gg3QolYIE6ldmUxzbeq0JktU'

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



class InstapaperError(Exception):
    pass


from cPickle import dumps

#base class for monitoring changes
class ChangesMonitor:
    _cm_last_dump = None
    def is_chaged(self):
        prev_dump = self._cm_last_dump
        self._cm_last_dump = None
        cur_dump = dumps(self, -1)
        self._cm_last_dump = cur_dump
        return ( ( prev_dump is not None ) and ( prev_dump != cur_dump ) )



class Instapaper(object):
    def __init__(self, username='', password=''):
        self._username = username
        self._password = password
        self.listBookMarks =[]
    
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
        [ self.getBookmark(y) for    y  in  folder_idList ]
        print  self.listBookMarks
            
        
    def getBookmark(self , folder_id , limit=None):
        
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
        
        The “have” parameter:

        This is a comma-separated list of bookmark_id values that the client already has in its local bookmark data, and shouldn’t be re-sent. Any IDs sent in the have parameter that would not have appeared in the list within the given limit are returned in a delete_ids parameter on the meta object.

        The have parameter can just be a list of the bookmark_id values, e.g.:

        12345,12346,12347

        …in which case Instapaper won’t include those bookmarks in the output.

        But it can also do more. Each bookmark returned by the API has a hash value, which is computed from its URL, title, description, and reading progress. If you join the hash value you have for an article with its article ID using a colon, e.g.:

        12345:OjMuzFp6,12346:0n4ONgYs,12347:YXo82wTR

        …then Instapaper will omit those bookmarks from the output, but only if the hashes haven’t changed. So you can use this method to selectively be informed of updates to article metadata without otherwise re-downloading the entire list on each update.

        Finally, you can optionally append two more fields to each ID with colons to indicate how far the user has read each article, as a floating-point value between 0.0 and 1.0 to indicate progress and the Unix timestamp value of the time that the progress was recorded, e.g.:

        12345:OjMuzFp6:0.5:1288584076

        This would indicate that the bookmark with bookmark_id=12345 and hash=OjMuzFp6 was read to 0.5 progress, or 50% of its length, at timestamp 1288584076 (2010-11-01 12:01:16am EST). If the server’s information is less recent than this, it will update the bookmark and return it in the output with a new hash value.

        """
        api = "https://www.instapaper.com/api/1/bookmarks/list"
        params = {
            'username': self._username,
            'password': self._password,
            'folder_id' :  folder_id}
        if  limit  is not None :
            params.append({'limit' :  limit})
        params = urllib.urlencode(params)
        
        status = f.getcode()
        if status == 201:
            return f.headers['Content-Location']
        elif status == 400:
            raise InstapaperError("bad request. probably missing a required parameter, such as url")
        elif status == 403:
            raise InstapaperError("invalid username or password")
        elif status == 500:
            raise InstapaperError("the service encountered an error")
        con = ""
        print   folder_id
        try:
            self.bookMarkList =  simplejson.load(f , 'utf-8')
            [  self.listBookMarks.append( ( b['hash'] , b['description'] , b['title'] , b['url'] , b['bookmark_id']) )   for   b   in   bookMarkList   if  b.has_key('hash')]
        except simplejson.decoder.JSONDecodeError:
            print  'Faced  JSONDecodeError   with  %s' % f
        

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

                   <td><input type="text" name="<?php echo "articleList[%d]['title']"; ?>" value="%s"  /></td>

                   <td><input type="text" name="<?php echo "articleList[%d]['body']"; ?>"  value="%s"  /></td>

                   </tr>

                   </table>"""%( count  ,  count  ,  article_update  , count , article_title ,  count ,  article_body )   
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
  
  def doBloggerActivity(self , article_title ,  article_desc  ,  article_comment   , article_category ):
    """Runs each of the example methods defined above, demonstrating how to
    interface with the Blogger service.article_comment , article_title , article_desc  , article_category 
    """

    # Demonstrate retrieving a list of the user's blogs.
    self.PrintUserBlogTitles()
  
    # Demonstrate how to create a post  with   title, content, author_name, tags,is_draft
    #draft_post = self.CreatePost(article_title , article_desc  , article_category , article_category  , True)
    #print "Successfully created draft post: \"" + draft_post.title.text + "\".\n"
  
    # Demonstrate how to publish a public post.
    #public_post = self.CreatePost(article_title , article_desc  , article_category , article_category  , True)
    #print "Successfully created public post: \"" + public_post.title.text + "\".\n"
    
    print "Now listing all posts in last  week"
    self.PrintPostsInLastWeek() 
    

  

class InstaPaper:

  def __init__(self, email, password):
    self.insta_user  =   email
    self.insta_password = password


  def AddWebBookMark(self, folder  , article_name , article_title , article_url  ,article_desc):
    """Invoke  Jmeter  passing the   right  arguments ."""
    article_name , article_title , article_url  ,article_desc   =   re.sub('\n' ,  '<BR/>' , article_name) ,re.sub('\n' ,  '<BR/>' ,article_title) , re.sub('\n' ,  '' ,article_url)  ,re.sub('\n' ,  '<BR/>' ,article_desc)
    cmd   =   "C:/java/apache-jmeter-2.6/bin/jmeter.bat -Jinsta_user=\"%s\" -Jinsta_password=\"%s\" -Jfname=\"%s\"  -Jarticle_name=\"%s\"  -Jarticle_title=\"%s\"  -Jarticle_url=\"%s\"  -Jarticle_desc=\"%s\"  -n  -t  InstaP.jmx -l  log_%s.jtl " %( self.insta_user  , self.insta_password , folder  , article_name , article_title , article_url  ,article_desc , time.strftime("%Y%m%d%H%M%S", time.localtime()) )
    print cmd
    os.system(cmd)
    
    
def   markDirectoryAsProcessed(dirName):
  f =open (os.path.join(dirName , 'processed') , 'w')
  f.close()

  
def main():
  """The main function runs the Blogger application with the provided
  username and password values.  Authentication credentials are required.
  NOTE:  It is recommended that you run this sample using a test account."""
  blogger_email = ''
  blogger_password = ''
  insta_user = ''
  insta_password = ''
  mailchimp_user  = ''
  mailchimp_password  = ''
  postdir = '.'
  create_newsletter = True
  # parse command line options
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
  ip  = InstaPaper(insta_user , insta_password)
  for root, dirs, files in os.walk(postdir, topdown=False):
      for name in dirs:
          for  x  in os.listdir(os.path.join(root, name)) :
              print  'Processing %s'% os.path.join(root , name , x)
              if  x[:-9]=='processed':
                   break
              if  os.path.exists(os.path.join( root , name,'article.txt')) :
                   article_desc  =  unicode(file(os.path.join( root , name, 'article.txt')).read() , 'utf-8' , errors='ignore')
              if  os.path.exists(os.path.join( root , name,'metadata.txt')) :  
                   cfg  =   ConfigParser()
                   cfg.read(os.path.join( root , name,'metadata.txt'))
                   article_category  = unicode(cfg.get('blogger','article_category'), 'utf-8' , errors='ignore')
                   article_name  =    unicode(cfg.get('blogger','article_name'), 'utf-8' , errors='ignore')
                   article_title =     unicode(cfg.get('blogger','article_title'), 'utf-8' , errors='ignore')
                   article_url  = unicode(cfg.get('insta','article_url'), 'utf-8' , errors='ignore')
                   article_comment =  unicode(cfg.get('blogger','article_comment'), 'utf-8' , errors='ignore')

          blg.doBloggerActivity(  article_title  , article_desc , article_comment , article_category)
          twt.sendTweet(unicode(file(os.path.join( root , name, 'article.txt')).read() , 'utf-8' , errors='ignore'))
          ip.AddWebBookMark(name  , article_name , article_title , article_url  ,article_desc)     
          markDirectoryAsProcessed(os.path.join( root , name))
          url = 'http://localhost/newsletter.php'
          webbrowser.open_new(url)
          


if __name__ == '__main__':
  main()

