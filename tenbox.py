"""
TenBox by Michael Vassilevsky

Accesses a user's Dropbox account, then displays up to 10 of the user's most
recently modified files.
"""

import dropbox
import webapp2
import cgi
from dateutil import parser

# app key and secret from Dropbox developer website
app_key = 'ehift129j568cs2'
app_secret = 'xtbohvv8u27c7wn'

# DropboxOAuth2FlowNoRedirect object, authorizes
flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)

MAIN_PAGE_HTML = """\
<html>
  <body>
  <p>Enter authorization code here:</p>
    <form action="/files" method="post">
      <div><textarea name="content" rows="1" cols="50"></textarea></div>
      <div><input type="submit" value="Authorize"></div>
    </form>
  </body>
</html>
"""


class MainPage(webapp2.RequestHandler):
    """The main page, used to link TenBox to a user's Dropbox account"""
    
    def get(self):
        """Generates the main page"""
        
        # generates an authorization URL using a DropboxOAuth2FlowNoRedirect object 
        authorize_url = flow.start()
        
        self.response.write('TenBox by Michael Vassilevsky<p></p>')
        self.response.write('Click ' + '<a href=' + authorize_url + ' target="_blank">here</a>' +
                            ', click "Allow", and copy the authorization code.')
        self.response.write(MAIN_PAGE_HTML)


class FilesPage(webapp2.RequestHandler):
    """The files page, which displays up to 10 of the most recently modfied files"""

    def post(self):
        """Generates the files page"""
        
        try:
            code = cgi.escape(self.request.get('content'))
        
            # gets access token, needed to make API requests
            access_token, user_id = flow.finish(code)
            
            self.response.write('<html><body>Most recently modified files:<pre>')
            
            client = dropbox.client.DropboxClient(access_token)
            folder_metadata = client.metadata('/') # gets metadata from the user's root folder
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
    ('/files', FilesPage),
], debug=True)
