# -*- coding: utf-8 -*-
import sys
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import requests
import json
import pickle
from urllib import urlencode
from urlparse import parse_qsl
from urlparse import urlparse as parse_url
from collections import defaultdict
from HTMLParser import HTMLParser
import re
import os.path

path = xbmcaddon.Addon().getAddonInfo('path').decode('utf-8') + "/"

class SessionRequests():
    session = requests.Session()
    cookie = None
    def getSession(self):
        return self.session

    def setSession(self,ses):
        self.session = ses

    def setCookie(self,cookieJar):
        self.session.cookies = cookieJar

    def getCookie(self):
        return self.cookie

    def readCookie(self):
        object = pickle.load(open(path + "cookies","rb"))
        self.session.cookies.update(object)

    def saveCookie(self):
        object=self.session.cookies.copy()
        pickle.dump(object, open(path + "cookies", "wb"))

    def makeRequest(self,url, params=None, raw=False, headers = None):
        if params is None:
        #log(url)
        #log(str(HEADERS))
            raw_reply = self.session.get(str(url), headers=headers,cookies = self.session.cookies)
        else:
            if raw:
                raw_reply = self.session.post(url, params, headers)
            else:
                js = json.dumps(params)
                if 'Token' in headers:
                    del headers['Token']
                raw_reply = self.session.post(url, js, headers=headers)
            if raw_reply.status_code == 401:
                error("401", "email or password incorrect")
        if not (raw_reply.status_code == 200 or raw_reply.status_code == 302):
            log('URL ' + url + ' returned status code ' + str(raw_reply.status_code) + ':' + raw_reply.content.encode('utf-8').strip())
            for k in sorted(raw_reply.headers):
                log(k + ":" + raw_reply.headers[k])
            return None
        if raw:
            return raw_reply
        try:
            reply = json.loads(raw_reply.content.decode('utf-8'))
        except ValueError, e:
            log('Json decode error '+ str(e) )
            log('Content is: '+raw_reply)
            return None

        if 'Message' in reply:
            log('Message: ' + reply['Message'])
        return reply

class SearchHTMLScraper(HTMLParser):
    RESET = 3
    TITLE_FOUND = 1
    RESULT_FOUND = 2
    FOUND_URL = 3
    RESULT_LOOKING = 0
    text_found = RESULT_LOOKING

    def __init__(self,handle):
        HTMLParser.__init__(self)
        self._handle = handle
        self.options = []

    def handle_starttag(self, tag, attrs):
        stringAttributes = json.dumps(attrs)
        if str(tag).strip() == "h1":
            if "LibraryChannelTitle" in stringAttributes:
                self.text_found=self.TITLE_FOUND
        if str(tag).strip() == "a":
            if "content-wrapper" in stringAttributes:
                for name,value in attrs:
                    if name == "href":
                        self.item_result={}
                        self.item_result['result'] = {}
                        self.item_result['result']['url'] = value

        if str(tag).strip() == "div":
            if "content-title" in stringAttributes:
                self.text_found=self.RESULT_FOUND
        if str(tag).strip() == "hr":
            if self.text_found == self.RESULT_LOOKING and "ChannelSeparator" in stringAttributes:
                self.text_found = self.RESET

    def get_menu_options(self):
        return self.options

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):

        if self.text_found == self.TITLE_FOUND:
            self.item = {}
            self.item['title'] = data
            self.item['results'] = [ ]
            self.text_found = self.RESULT_LOOKING

        if self.text_found == self.RESULT_FOUND:
            self.text_found = self.RESULT_LOOKING
            self.item_result['result']['title'] = data
            self.item['results'].append(self.item_result)
            self.item_result = None

        if self.text_found == self.RESET:
            self.options.append(self.item)
            self.item = None
            self.text_found = self.RESULT_LOOKING


def log(msg):
    xbmc.log("RNM PLUGIN:"+msg,xbmc.LOGINFO)

addon = xbmcaddon.Addon()
sessionInstance = SessionRequests()

HEADERS = {'Content-type': 'application/json; charset=utf-8',
           'Connection': 'Keep-Alive',
           'Accept-Encoding': 'gzip',
           'Host': 'api.rightnow.org',
           'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1)',
           'Accept': 'application/vnd.rnapi.v4+json'}

HEADERSFORWEB = {

    'User-Agent' :  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Connection': 'Close',
    'Host' :'www.rightnowmedia.org',
    'Accept-Encoding' : 'gzip,deflate,br',
    'Accept' :'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

url_web_base = 'https://www.rightnowmedia.org'
url_web_login = url_web_base + '/Account/Login'
base = 'https://api.rightnow.org/api/media/'
url_auth = base + 'authenticate'
url_library_all = base + 'library/all'
url_library = base + 'library/'  # + ['custom/'] + id      # use 'custom' for custom libraries only
url_content = base + 'content/'  # + id
url_channel = base + "channel/"  # + id
url_sessions = base + 'content/series/'  # + id
url_play = base + '/session/'  # + id + '/hls'


_url = sys.argv[0]
_kodihandle = int(sys.argv[1])

xbmcplugin.setContent(_kodihandle, 'movies')


def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.
    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_url, urlencode(kwargs))


def list_libraries():
    url = get_url(action='search')
    item = xbmcgui.ListItem(label="Search Videos")
    xbmcplugin.addDirectoryItem(_kodihandle, url, item, False)
    libs = API(url_library_all)
    for lib in libs:
        item = xbmcgui.ListItem(label=lib['Name'])
        url = get_url(action='library', id=lib['LibraryID'], iscustom=lib['IsCustom'])
        is_folder = True
        xbmcplugin.addDirectoryItem(_kodihandle, url, item, is_folder)
    xbmcplugin.addSortMethod(_kodihandle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_kodihandle)


def list_library(lid, is_custom):
    custom_string = '' if is_custom=='False' else 'custom/'
    lib = API(url_library+custom_string+lid)
    if lib is not None:
        for chan in lib['Channels']:
            name = chan['Name']
            chan_id = chan['ChannelID']
            is_folder = True
            url = get_url(action='channel', channel=chan_id)
            item = xbmcgui.ListItem(label=name)
            xbmcplugin.addDirectoryItem(_kodihandle, url, item, is_folder)
    xbmcplugin.addSortMethod(_kodihandle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_kodihandle)


def list_channel(channelId):
    lib = API(url_channel + channelId)
    #log("Channel" + str(lib))
    if lib is not None:
        for content in lib['Content']:
            name = content['Title']
            contentId = content['ContentID']
            item = xbmcgui.ListItem(label=name)
            art = {}
            if 'ImgUrl' in content:
                art['thumb'] = content['ImgUrl']
            if 'BannerURL' in content:
                art['banner'] = content['BannerURL']

            item.setArt(art)

            info = {}
            if 'Summary' in content:
                info['plot'] = content['Summary']
            if 'Publisher' in content and type(content['Publisher']) is dict and 'Name' in content['Publisher']:
                info['studio'] = content['Publisher']['Name']
            if 'Speaker' in content:
                speaker = content['Speaker']
                if type(speaker) is dict and 'FirstName' in speaker and 'LastName' in speaker:
                    info['artist'] = [speaker['FirstName'] + ' ' + speaker['LastName']]

            item.setInfo('video', info)
            is_folder = True
            url = get_url(action='content', content=contentId)
            xbmcplugin.addDirectoryItem(_kodihandle, url, item, is_folder)
    xbmcplugin.addSortMethod(_kodihandle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_kodihandle)


def searchDialogProcess(options):
    select_options = []
    if len(options) > 0:
        for i in range(0,len(options)):
            select_options.append(options[i]['title'])
        item_selected = xbmcgui.Dialog().select("Search results",list = select_options)
        select_options = []
        for i in range(len(options[item_selected]['results'])):
            select_options.append(options[item_selected]['results'][i]['result']['title'])
        result_selected = xbmcgui.Dialog().select("Search results",list = select_options)
        content_id = re.search(".+/([0-9]+)",options[item_selected]['results'][result_selected]['result']['url']).group(1)
        play_web_session(url_web_base + options[item_selected]['results'][result_selected]['result']['url'],int(content_id))
    else:
        xbmcgui.Dialog().ok("Status","Sorry no search results found")

def search(string,_handle):
    global sessionInstance
    sessionInstance.readCookie()
    global HEADERSFORWEB
    HEADERSFORWEB['Referer'] = url_web_base + "/Search?q=" + string
    dom = sessionInstance.makeRequest(url_web_base + "/Search?q=" + string,None,True,HEADERSFORWEB)
    parser = SearchHTMLScraper(_handle)
    parser.feed(dom.text.encode("utf8"))
    searchDialogProcess(parser.get_menu_options())


def search_content():
    global _kodihandle
    search_str = ""
    keyboard = xbmc.Keyboard(search_str,'Search')

    keyboard.doModal()
    if (keyboard.isConfirmed() == False):
        return
    search_str = keyboard.getText()   #.replace(' ','+')  # sometimes you need to replace spaces with + or %20
    if len(search_str) == 0:
        return
    else:
        search(search_str, _kodihandle)


def list_content(contentId):
    content = API(url_sessions+contentId)
    def _add_play_item(d):
        session = defaultdict(lambda: '', d)
        sessionId = session['SessionID']
        if sessionId == '':
            sessionId = session['ContentID']

        name = session['Title']
        type_id = session['ContentTypeID']
        if type_id in (2, 3, 9):  # See the APIDOC.rst for a guess at the meaning.
            name = '[web only] ' + name
        summary = session['Summary']
        duration = session['Duration']
        thumb = session['ImgUrl']

        item = xbmcgui.ListItem(label=name)
        item.setArt({'thumb' : thumb})

        info = {'plot' : summary, 'duration' : duration}
        item.setInfo('video', info)
        is_folder = False
        url = get_url(action='play', session=sessionId, title=name.encode('utf-8'))
        xbmcplugin.addDirectoryItem(_kodihandle, url, item, is_folder)
    # If there are no sessions, the contentID is the sessionID
    for sessiond in content['Sessions']:
        _add_play_item(sessiond)
    if not content['Sessions']:
        _add_play_item(content)

    xbmcplugin.endOfDirectory(_kodihandle)

# Play the url via the web url not api

def play_web_session(url_from_search, content_id_from_search):
    HEADERSFORPLAYER =  {
        'User-Agent' :  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:52.0) Gecko/20100101 Firefox/52.0',
        'Accept-Encoding' : 'gzip,deflate,br',
        "x-requested-with":"XMLHttpRequest",
        "Connection":"keep-alive",
        "Accept":"*/*",
        'Host' :'www.rightnowmedia.org',
        'Referer' : url_from_search,
    }
    sessionInstance.readCookie()
    url_response = sessionInstance.makeRequest(url_from_search + "#1", None, True, HEADERSFORPLAYER)
    returnReg = re.search(".+session-contentId=\"([0-9]+)\"",url_response.text)
    if returnReg is None:
        returnReg = re.search(".+var contentId = ([0-9]+);.*",url_response.text)
    if returnReg is None:
        xbmcgui.Dialog().ok("Status","Could not load video, link was missing")
    else:
        content_id = returnReg.group(1)
        url = sessionInstance.makeRequest("https://www.rightnowmedia.org/Media/Player",{"contentId": str(content_id),'showPoster' : 'false' },True,HEADERSFORPLAYER)
        videolink = re.search("source src=\"(.+?)\"",url.text).group(1)
        xbmc.Player().play(videolink)

def play_session(sessionId, title):
    # if this 404s, kodi 16.1 crashes with a segfault :-(
    url = API(url_play+sessionId+'/hls')
    item = xbmcgui.ListItem(label=title)
    xbmc.Player().play(url, listitem=item)
    #item = xbmcgui.ListItem(path=url)
    #xbmcplugin.setResolvedUrl(_handle, True, listitem=item)


def API(url, params=None, raw=False, headers = HEADERS):
    """
    Send dict request to RNM and return the reply
    :param url: url
    :param params: dictionary of params (If this is set, will use POST, otherwise GET)
    :return: dictionary of results
    """
    if params is None:
        #log(url)
        #log(str(HEADERS))
        raw_reply = requests.get(str(url), headers=headers)
    else:
        if raw:
            raw_reply = requests.post(url, params, headers=headers)
        else:
            js = json.dumps(params)
            if 'Token' in headers:
                del headers['Token']
            raw_reply = requests.post(url, js, headers=headers)
        if raw_reply.status_code == 401:
            error("401", "email or password incorrect")
    if not (raw_reply.status_code == 200 or raw_reply.status_code == 302):
        log('URL ' + url + ' returned status code ' + str(raw_reply.status_code) + ':' + raw_reply.content.encode('utf-8').strip())
        for k in sorted(raw_reply.headers):
            log(k + ":" + raw_reply.headers[k])
        return None
    if raw:
        return raw_reply
    try:
        reply = json.loads(raw_reply.content.decode('utf-8'))
    except ValueError, e:
        log('Json decode error '+ str(e) )
        log('Content is: '+raw_reply.content.decode('utf-8'))
        return None

    if 'Message' in reply:
        log('Message: ' + reply['Message'])
    return reply

def setTokenHeader(token, account_id):
    HEADERS['Token'] = token
    HEADERS['AccountIndex'] = account_id

def ensure_token():
    global HEADERS
    token = addon.getSetting('token')
    account_id = addon.getSetting('church_id')
    if token and account_id:
        #log('Found token: ' + token)
        setTokenHeader(token, account_id)
        return True
    return authenticate()

# grab the verificatoin token to prevent cross side scripting

def parseLoginValidationResponse(page):
    result = re.search('<input name=\"__RequestVerificationToken\" type=\"hidden\" value=\"(.*?)\"\ />',page.encode('utf-8').strip())
    return result.group(1)

# Authenticate for logging intot he UI via FireFox Webinterface

def authenticate_web():
    global HEADERSFORWEB
    user = addon.getSetting('email')
    #log('***USER*** '+user)
    if not user:
        error("Email address required", "Set the email in this plugin's settings")
        return False
    pswd = addon.getSetting('password')
    #log('***PASS*** '+pswd)
    if not pswd:
        error("Password required", "Set the password in this plugin's settings")
        return False
    getRawLoginPageResponse = sessionInstance.makeRequest(url_web_login,None,True,HEADERSFORWEB)
    verificationKey = str(parseLoginValidationResponse(getRawLoginPageResponse.text))
    object = { "UserName" : user,
                "Password" : pswd,
               "__RequestVerificationToken" :verificationKey,
               "RememberMe" :"false"
    }
    cookies = {
        ".AspNetCore.Antiforgery.s7eEODgMd7s":verificationKey
    }

    cookieJar =  None
    cookieJar = requests.utils.add_dict_to_cookiejar(cookieJar,cookies)
    sessionInstance.setCookie(cookieJar)
    reply =  sessionInstance.makeRequest(url_web_login,object,True,HEADERSFORWEB)
    sessionInstance.saveCookie()
    if reply is None:
        return False
    return True

def authenticate():

    global HEADERS
    user = addon.getSetting('email')
    #log('***USER*** '+user)
    if not user:
        error("Email address required", "Set the email in this plugin's settings")
        return False
    pswd = addon.getSetting('password')
    #log('***PASS*** '+pswd)
    if not pswd:
        error("Password required", "Set the password in this plugin's settings")
        return False
    reply = API(url_auth, {'username': user, 'password': pswd})
    if reply is None:
        return False
    token = reply['token']
    #log('new auth token:'+token)
    addon.setSetting('token',token)
    account_id = str(reply['accounts'][0]['ChurchId'])
    addon.setSetting('church_id', account_id)
    setTokenHeader(token, account_id)
    return True

def error(title, msg):
    dialog = xbmcgui.Dialog()
    dialog.notification(title, msg, icon=xbmcgui.NOTIFICATION_ERROR)

def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring
    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    log(paramstring)
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        # make sure we have an auth token
        if not ensure_token():
            return
        if params['action'] == 'library':
            list_library(params['id'], params['iscustom'])
        elif params['action'] == 'channel':
            list_channel(params['channel'])
        elif params['action'] == 'content':
            list_content(params['content'])
        elif params['action'] == 'search':
            search_content()
        elif params['action'] == 'search_items':
            search_content(params['search'])
        elif params['action'] == 'play':
            play_session(params['session'], params['title'])
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        if not authenticate(): # force new authenticate
            return
        if not authenticate_web():
            return
        list_libraries()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
