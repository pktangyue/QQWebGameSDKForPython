from oauth import oauth
from urllib2 import Request,urlopen,HTTPError
from urllib import urlencode,quote
from django.http import HttpResponse,HttpResponseRedirect

SERVER = 'http://openapi.sp0309.3g.qq.com/'
# oauth token urls
REQUEST_TOKEN_URL = SERVER + 'oauth/request_token'
ACCESS_TOKEN_URL  = SERVER + 'oauth/access_token'
AUTHORIZATION_URL = SERVER + 'oauth/authorize'
CALLBACK_URL = 'http://127.0.0.1:8000/oauth_test/callback'
# api urls
PROFILE_URL = SERVER + 'people/@me/@self'
FRIENDS_URL = SERVER + 'people/@me/@friends'
CONNECT_URL = SERVER + 'oauth/connect'
WEIBO_URL   = SERVER + 'weibo/display'
# key and secret
CONSUMER_KEY = 'GDdmIQH6jhtmLUypg82g'
CONSUMER_SECRET = 'MCD8BKwGdgPHvAuvgvz4EQpqDAtx89grbuNMRd7Eh98'

def escape(s):
    """Escape a URL including any /."""
    return quote(s, safe='~')

class QQ_OAuthClient(oauth.OAuthClient):
    def fetch_request_token(self, oauth_request):
        ret = self._excute(oauth_request)
        return oauth.OAuthToken.from_string(ret)

    def fetch_access_token(self, oauth_request):
        ret = self._excute(oauth_request)
        return oauth.OAuthToken.from_string(ret)

    def access_resource(self, oauth_request):
        return self._excute(oauth_request)

    def _excute(self, oauth_request):
        querystring = urlencode(oauth_request.get_nonoauth_parameters())
        if(oauth_request.http_method == 'GET'):
            request = Request(oauth_request.http_url+"?"+querystring, None, oauth_request.to_header())
        else:
            print "\n"
            print querystring
            print "\n"
            print oauth_request.http_url
            print "\n"
            print oauth_request.to_header()
            print "\n"
            print oauth_request.to_postdata()
            print "\n"
            print escape(oauth_request.get_normalized_http_method()),
            print "\n"
            print escape(oauth_request.get_normalized_http_url()),
            print "\n"
            #print escape(oauth_request.get_normalized_parameters()),
            print "\n"
            request = Request(oauth_request.http_url, querystring, oauth_request.to_header())
            #request = Request(oauth_request.http_url+"?"+querystring, None, oauth_request.to_header())
        try:
            response = urlopen(request)
            return response.read()
        except HTTPError,error:
            print error.read()
            print error.code
            return 'error'

client = QQ_OAuthClient(oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET), None)

def index(request):
    # get request token
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(client.consumer, callback=CALLBACK_URL, http_url=REQUEST_TOKEN_URL)
    oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), client.consumer, None)
    token = client.fetch_request_token(oauth_request)
    # save token to session
    request.session['token'] = token.to_string()
    # redirect to authorization url
    oauth_request = oauth.OAuthRequest.from_token_and_callback(token=token, http_url=AUTHORIZATION_URL)
    return HttpResponseRedirect(oauth_request.to_url())

def callback(request):
    # sad way to get the verifier
    verifier = request.GET['oauth_verifier']
    # get token from session
    token = oauth.OAuthToken.from_string(request.session['token'])
    # get access token
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(client.consumer, token=token, verifier=verifier, http_url=ACCESS_TOKEN_URL)
    oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), client.consumer, token)
    token = client.fetch_access_token(oauth_request)
    # save token to session
    request.session['token'] = token.to_string()
    return HttpResponse('success')

def test_conn(request):
    request = Request('http://oauth.tangyue.com/?aa=aa')
    response = urlopen(request)
    return HttpResponse(response.read())

def profile(request):
    # get token from session
    token = oauth.OAuthToken.from_string(request.session['token'])
    parameters = {'fields':'id,nickname,thumbnailUrl,gender,sqq,gamevip,yellow','format':'json'}
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(client.consumer, token=token,http_url=PROFILE_URL, parameters=parameters)
    oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), client.consumer, token)
    params = client.access_resource(oauth_request)
    return HttpResponse(params)

def friends(request):
    token = oauth.OAuthToken.from_string(request.session['token'])
    parameters = {}
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(client.consumer, token=token, http_url=FRIENDS_URL, parameters=parameters)
    oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), client.consumer, token)
    params = client.access_resource(oauth_request)
    return HttpResponse(params)

def connect(request):
    token = oauth.OAuthToken.from_string(request.session['token'])
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(client.consumer,token=token,http_url=CONNECT_URL)
    oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), client.consumer, token)
    params = client.access_resource(oauth_request)
    return HttpResponse(params)

def weibo_display(request):
    token = oauth.OAuthToken.from_string(request.session['token'])
    #parameters = {'content':'aa','goUrl':'http://www.baidu.com/','tt':0}
    parameters = {'content':'aa'}
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(client.consumer, token=token, http_url=WEIBO_URL,parameters=parameters, http_method='POST')
    oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(),client.consumer,token)
    params = client.access_resource(oauth_request)
    return HttpResponse(params)
