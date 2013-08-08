import dropbox
import webapp2
import cgi
from dateutil import parser

# Gets app key and secret from Dropbox
app_key = 'ehift129j568cs2'
app_secret = 'xtbohvv8u27c7wn'

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

    def get(self):
        authorize_url = flow.start()
        self.response.write('TenBox by Michael Vassilevsky<p></p>')
        self.response.write('Go to ' + authorize_url + ', click "Allow", and copy the authorization code')
        self.response.write(MAIN_PAGE_HTML)


class FilesPage(webapp2.RequestHandler):

    def post(self):
        self.response.write('<html><body>Most recently modified files:<pre>')
        code = cgi.escape(self.request.get('content'))
        access_token, user_id = flow.finish(code) # fails without correct authorization code, add error handling
        client = dropbox.client.DropboxClient(access_token)
        folder_metadata = client.metadata('/')
        files_and_folders = folder_metadata['contents']
        last_ten = []
        for meta in files_and_folders:
            if (meta['is_dir'] == False): # if it's not a folder
                last_ten.append(meta)
                sorted(last_ten, key = lambda l: parser.parse(l['modified']))
                if (len(last_ten) > 10):
                    last_ten.pop(0) # remove oldest element
        for elt in last_ten:
            to_print = elt['path'][1:] # removes slash from path
            self.response.write(to_print)
            self.response.write('<p></p>')
        self.response.write('</pre></body></html>')


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/files', FilesPage),
], debug=True)
