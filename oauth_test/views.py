import httplib
from urllib2 import Request,urlopen
import time
import oauth.oauth as oauth
from pprint import pprint
from inspect import getmembers
from django.http import HttpResponse,HttpResponseRedirect
from urllib import urlencode

#SERVER = 'openapi.3g.qq.com'
SERVER = 'openapi.sp0309.3g.qq.com'
#SERVER = 'api.t.sina.com.cn'
#SERVER = 'dev.g.qq.com'
PORT = 80

# fake urls for the test server (matches ones in server.py)
REQUEST_TOKEN_URL = 'http://openapi.sp0309.3g.qq.com/oauth/request_token'
ACCESS_TOKEN_URL  = 'http://openapi.sp0309.3g.qq.com/oauth/access_token'
AUTHORIZATION_URL = 'http://openapi.sp0309.3g.qq.com/oauth/authorize'
RESOURCE_URL = 'http://openapi.sp0309.3g.qq.com/people/@me/@self'
#REQUEST_TOKEN_URL = 'http://openapi.3g.qq.com/oauth/request_token'
#ACCESS_TOKEN_URL  = 'http://openapi.3g.qq.com/oauth/access_token'
#AUTHORIZATION_URL = 'http://openapi.3g.qq.com/oauth/authorize'
#RESOURCE_URL = 'http://openapi.3g.qq.com/people/@me/@self'
#REQUEST_TOKEN_URL = 'http://api.t.sina.com.cn/oauth/request_token'
#ACCESS_TOKEN_URL  = 'http://api.t.sina.com.cn/oauth/access_token'
#AUTHORIZATION_URL = 'http://api.t.sina.com.cn/oauth/authorize'
#RESOURCE_URL = 'http://openapi.3g.qq.com/people/@me/@self'
CALLBACK_URL = 'http://127.0.0.1:8000/oauth_test/callback'

# key and secret granted by the service provider for this consumer application - same as the MockOAuthDataStore
CONSUMER_KEY = 'GDdmIQH6jhtmLUypg82g'
CONSUMER_SECRET = 'MCD8BKwGdgPHvAuvgvz4EQpqDAtx89grbuNMRd7Eh98'

def index(request):
    # setup
    print '** OAuth Python Library Example **'
    client = SimpleOAuthClient(SERVER, PORT, REQUEST_TOKEN_URL, ACCESS_TOKEN_URL, AUTHORIZATION_URL)
    consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
    signature_method_plaintext = oauth.OAuthSignatureMethod_PLAINTEXT()
    signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()

    # get request token
    print '* Obtain a request token ...'
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, callback=CALLBACK_URL, http_url=client.request_token_url)
    oauth_request.sign_request(signature_method_hmac_sha1, consumer, None)
    print 'REQUEST (via headers)'
    print 'parameters: %s' % str(oauth_request.to_header())
    print urlencode(oauth_request.parameters)
    token = client.fetch_request_token(oauth_request)
    request.session['token'] = token.to_string()
    print 'GOT'
    print 'key: %s' % str(token.key)
    print 'secret: %s' % str(token.secret)
    print 'callback confirmed? %s' % str(token.callback_confirmed)

    print '* Authorize the request token ...'
    oauth_request = oauth.OAuthRequest.from_token_and_callback(token=token, http_url=client.authorization_url)
    print 'REQUEST (via url query string)'
    print 'parameters: %s' % str(oauth_request.parameters)
    return HttpResponseRedirect(oauth_request.to_url())

def callback(request):

    client = SimpleOAuthClient(SERVER, PORT, REQUEST_TOKEN_URL, ACCESS_TOKEN_URL, AUTHORIZATION_URL)
    consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
    signature_method_plaintext = oauth.OAuthSignatureMethod_PLAINTEXT()
    signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()
    # sad way to get the verifier
    import urlparse, cgi
    verifier = request.GET['oauth_verifier']
    print request.session['token']
    token = oauth.OAuthToken.from_string(request.session['token'])
    print 'verifier: %s' % verifier

    # get access token
    print '* Obtain an access token ...'
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, token=token, verifier=verifier, http_url=client.access_token_url)
    oauth_request.sign_request(signature_method_hmac_sha1, consumer, token)
    print 'REQUEST (via headers)'
    print 'parameters: %s' % str(oauth_request.parameters)
    token = client.fetch_access_token(oauth_request)
    print 'GOT'
    print 'key: %s' % str(token.key)
    print 'secret: %s' % str(token.secret)
    request.session['token'] = token.to_string()
    return HttpResponse('success')

def profile(request):
    client = SimpleOAuthClient(SERVER, PORT, REQUEST_TOKEN_URL, ACCESS_TOKEN_URL, AUTHORIZATION_URL)
    consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
    signature_method_plaintext = oauth.OAuthSignatureMethod_PLAINTEXT()
    signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()
    # access some protected resources
    print request.session['token']
    token = oauth.OAuthToken.from_string(request.session['token'])
    print '* Access protected resources ...'
    parameters = {'fields':'id'}
    #oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, token=token,http_url=RESOURCE_URL)
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, token=token,http_url=RESOURCE_URL,parameters=parameters)
    oauth_request.sign_request(signature_method_hmac_sha1, consumer, token)
    print 'REQUEST (via post body)'
    print 'parameters: %s' % str(oauth_request.parameters)
    params = client.access_resource(oauth_request)
    print 'GOT'
    print 'non-oauth parameters: %s' % params
    return HttpResponse(params)

def test_conn(request):
    headers = {'Content-Type' :'application/x-www-form-urlencoded'}
    request = Request('http://oauth.tangyue.com/index.php?aa=aa',None)
    request.get_method = lambda: 'GET'
    response = urlopen(request)
    ret = response.read()
    return HttpResponse(ret)


# example client using httplib with headers
class SimpleOAuthClient(oauth.OAuthClient):

    def __init__(self, server, port=httplib.HTTP_PORT, request_token_url='', access_token_url='', authorization_url=''):
        self.server = server
        self.port = port
        self.request_token_url = request_token_url
        self.access_token_url = access_token_url
        self.authorization_url = authorization_url
        self.connection = httplib.HTTPConnection(self.server, self.port, True ,10 )

    def fetch_request_token(self, oauth_request):
        # via headers
        # -> OAuthToken
        print self.request_token_url
        request = Request(self.request_token_url,None,oauth_request.to_header())
        print request.get_header('Authorization')
        response = urlopen(request)
        print response.getcode()
        ret = response.read()
        print ret
        return oauth.OAuthToken.from_string(ret)

    def fetch_access_token(self, oauth_request):
        # via headers
        # -> OAuthToken
        request = Request(self.access_token_url,None,oauth_request.to_header())
        response = urlopen(request)
        print response.getcode()
        ret = response.read()
        print ret
        return oauth.OAuthToken.from_string(ret)

    def authorize_token(self, oauth_request):
        # via url
        # -> typically just some okay response
        print oauth_request.to_url()
        request = Request(oauth_request.to_url())
        response = urlopen(request)
        print response.geturl()
        print response.getcode()
        ret  = response.read()
        return ret

    def access_resource(self, oauth_request):
        # via post body
        # -> some protected resources
        headers = {'Content-Type' :'application/x-www-form-urlencoded'}

        print oauth_request.to_url()
        print "\n\n"
        print oauth_request.to_postdata()
        print "\n\n"
        print oauth_request.to_header()
        print "\n\n"
        #print escape(oauth_request.get_normalized_http_method())
        #print "\n\n"
        #print escape(oauth_request.get_normalized_http_url())
        #print "\n\n"
        #print escape(oauth_request.get_normalized_parameters())
        #print "\n\n"
        request = Request(RESOURCE_URL+"?fields=id",None,oauth_request.to_header())
        #request = Request(oauth_request.to_url(),oauth_request.to_postdata(),oauth_request.to_header())
        print request.get_method()
        response = urlopen(request)
        print response.geturl()
        print response.getcode()
        ret = response.read()
        return ret

def escape(s):
    """Escape a URL including any /."""
    import urllib
    return urllib.quote(s, safe='~')
