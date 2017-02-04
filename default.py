import sys
import xbmc
import xbmcgui
import xbmcplugin
import auth
from urllib import urlencode
from urlparse import parse_qsl
from collections import defaultdict

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
    libs = auth.POST(auth.url_library_all)
    for lib in libs:
        item = xbmcgui.ListItem(label = lib['Name'])
        url = get_url(action='library', id=lib['LibraryID'])
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, item, is_folder)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_handle)

def list_library(id):
    lib = auth.POST(auth.url_library+id)
    for chan in lib['Channels']:
        name = chan['Name']
        chan_id = chan['ChannelID']
        is_folder = True
        url = get_url(action='channel',library=id,channel=chan_id)
        item = xbmcgui.ListItem(label = name)
        xbmcplugin.addDirectoryItem(_handle, url, item, is_folder)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_handle)

def list_channel(libraryId, channelId):
    lib = auth.POST(auth.url_library + libraryId)
    for chan in lib['Channels']:
        chan_id = chan['ChannelID']
        if chan_id == int(channelId):
            for content in chan['Content']:
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
    content = auth.POST(auth.url_content+'series/'+contentId)
    for sessiond in content['Sessions']:
        session = defaultdict(lambda: '', sessiond)
        sessionId = session['SessionID']
        name = session['Title']
        summary = session['Summary']
        duration = session['Duration']
        thumb = session['ImgUrl']

        item = xbmcgui.ListItem(label=name)
        item.setArt({'thumb' : thumb})

        info = {'plot' : summary, 'duration' : duration}
        item.setInfo('video', info)
        is_folder = False
        url = get_url(action='play', session=sessionId)
        xbmcplugin.addDirectoryItem(_handle, url, item, is_folder)
    xbmcplugin.endOfDirectory(_handle)

def play_session(sessionId):
    # if this 404s, kodi 16.1 crashes with a segfault :-(
    url = auth.POST(auth.base+'session/'+sessionId+"/hls")
    xbmc.Player().play(url)
    #item = xbmcgui.ListItem(path=url)
    #xbmcplugin.setResolvedUrl(_handle, True, listitem=item)


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
        if params['action'] == 'library':
            list_library(params['id'])
        elif params['action'] == 'channel':
            list_channel(params['library'],params['channel'])
        elif params['action'] == 'content':
            list_content(params['content'])
        elif params['action'] == 'play':
            play_session(params['session'])
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_libraries()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])