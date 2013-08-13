"""
TenBox by Michael Vassilevsky

Accesses a user's Dropbox account, then displays up to 10 of the user's most
recently modified files.
"""

import webapp2
import cgi
import urllib2
from dropbox import client, rest, session
from dateutil import parser

# app key and secret from Dropbox developer website
app_key = 'ehift129j568cs2'
app_secret = 'xtbohvv8u27c7wn'
access_type = 'dropbox'

sess = session.DropboxSession(app_key, app_secret, access_type)
request_token = sess.obtain_request_token()

class MainPage(webapp2.RequestHandler):
    """The main page, used to link TenBox to a user's Dropbox account"""
    
    def get(self):
        """Generates the main page"""
        
        url = sess.build_authorize_url(request_token, 'http://localhost:8080/files') # replace with address for version on appspot
        self.redirect(url)

class FilesPage(webapp2.RequestHandler):
    """The files page, which displays up to 10 of the most recently modfied files"""

    def get(self):
        """Generates the files page"""
        
        try:
            self.response.write('<html><body>Most recently modified files:<pre>')
            access_token = sess.obtain_access_token(request_token)
            dr_client = client.DropboxClient(sess)
            folder_metadata = dr_client.metadata('/') # gets metadata from the user's root folder
            files_and_folders = folder_metadata['contents']
            last_ten = []
            for meta in files_and_folders:
                if (meta['is_dir'] == False): # if not a folder
                    last_ten.append(meta)
                    
                    # parses and sorts files by date modified
                    sorted(last_ten, key = lambda l: parser.parse(l['modified']))
                    
                    # removes oldest file from list, if the list has more than ten elements
                    if (len(last_ten) > 10):
                        last_ten.pop(0)
                        
            for elt in last_ten:
                to_print = elt['path'][1:] # removes slash from path
                self.response.write(to_print)
                self.response.write('<p></p>')
                
            self.response.write('</pre></body></html>')
        except:
            self.response.write('<html><body>Incorrect authorization code, please try again.</body></html')


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/files', FilesPage)
], debug=True)
