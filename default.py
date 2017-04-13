# -*- coding: utf-8 -*-
import sys
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import requests
import json
from urllib import urlencode
from urlparse import parse_qsl
from collections import defaultdict


def log(msg):
    xbmc.log("RNM PLUGIN:"+msg)

addon = xbmcaddon.Addon()

HEADERS = {'Content-type': 'application/json; charset=utf-8',
           'Connection': 'Keep-Alive',
           'Accept-Encoding': 'gzip',
           'Host': 'api.rightnow.org',
           'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1)',
           'Accept': 'application/vnd.rnapi.v4+json'}
base = 'https://api.rightnow.org/api/media/'
url_auth = base + 'authenticate'
url_library_all = base + 'library/all'
url_library = base + 'library/'  # + id
url_content = base + 'content/'  # + id
url_channel = base + "channel/"  # + id
url_sessions = base + 'content/series/'  # + id
url_play = base + '/session/'  # + id + '/hls'


_url = sys.argv[0]
_handle = int(sys.argv[1])

xbmcplugin.setContent(_handle, 'movies')


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
    libs = API(url_library_all)
    for lib in libs:
        item = xbmcgui.ListItem(label=lib['Name'])
        url = get_url(action='library', id=lib['LibraryID'])
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, item, is_folder)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_handle)


def list_library(lid):
    lib = API(url_library+lid)
    if lib is not None:
        for chan in lib['Channels']:
            name = chan['Name']
            chan_id = chan['ChannelID']
            is_folder = True
            url = get_url(action='channel', channel=chan_id)
            item = xbmcgui.ListItem(label=name)
            xbmcplugin.addDirectoryItem(_handle, url, item, is_folder)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_handle)


def list_channel(channelId):
    lib = API(url_channel + channelId)
    #log("Channel" + str(lib))
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
        xbmcplugin.addDirectoryItem(_handle, url, item, is_folder)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_handle)


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
        xbmcplugin.addDirectoryItem(_handle, url, item, is_folder)
    # If there are no sessions, the contentID is the sessionID
    for sessiond in content['Sessions']:
        _add_play_item(sessiond)
    if not content['Sessions']:
        _add_play_item(content)

    xbmcplugin.endOfDirectory(_handle)

def play_session(sessionId, title):
    # if this 404s, kodi 16.1 crashes with a segfault :-(
    url = API(url_play+sessionId+'/hls')
    item = xbmcgui.ListItem(label=title)
    xbmc.Player().play(url, listitem=item)
    #item = xbmcgui.ListItem(path=url)
    #xbmcplugin.setResolvedUrl(_handle, True, listitem=item)

def API(url, params=None, raw=False):
    """
    Send dict request to RNM and return the reply
    :param url: url
    :param params: dictionary of params (If this is set, will use POST, otherwise GET)
    :return: dictionary of results
    """
    global HEADERS
    if params is None:
        #log(url)
        #log(str(HEADERS))
        raw_reply = requests.get(url, headers=HEADERS)
    else:
        js = json.dumps(params)
        if 'Token' in HEADERS:
            del HEADERS['Token']
        raw_reply = requests.post(url, js, headers=HEADERS)
        if raw_reply.status_code == 401:
            error("401", "email or password incorrect")
    if raw_reply.status_code != 200:
        log('URL ' + url + ' returned status code ' + str(raw_reply.status_code) + ':' + raw_reply.content.decode())
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
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        # make sure we have an auth token
        if not ensure_token():
            return
        if params['action'] == 'library':
            list_library(params['id'])
        elif params['action'] == 'channel':
            list_channel(params['channel'])
        elif params['action'] == 'content':
            list_content(params['content'])
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
        list_libraries()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])