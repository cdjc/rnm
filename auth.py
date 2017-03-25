#!/usr/bin/env python
import sys
import time
import requests
import json

try:
    import xbmc
    log = xbmc.log
except:
    def log(msg):
        print >> sys.stderr,msg


base = 'https://api.rightnow.org/api/media/'

url_auth = base + 'authenticate'
url_library_all = base + 'library/all'
url_library = base + 'library/'  # + id
url_user = base + 'user'
url_account = base + 'account'
url_accounts = base + 'accounts'
url_settings = base + 'settings'
url_content = base + 'content/'  # + id

HEADERS = {'Content-type': 'application/json; charset=utf-8',
           'Connection' : 'Keep-Alive',
           'Accept-Encoding' : 'gzip',
           'AccountIndex' : '4199486',
           'Host' : 'api.rightnow.org',
           'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1)',
           'Accept': 'application/vnd.rnapi.v4+json'}

token = None

def POST(url, params=None, raw=False):
    """
    Send dict request to RNM and return the reply
    :param url: url
    :param params: dictionary of params
    :return: dictionary of results
    """
    if token and 'token' not in HEADERS:
        HEADERS['Token'] = token
        #HEADERS['AccountIndex'] = '0'
    if params is None:
        raw_reply = requests.get(url, headers=HEADERS)
    else:
        js = json.dumps(params)
        raw_reply = requests.post(url, js, headers=HEADERS)
    if raw_reply.status_code != 200:
        print('URL', url, 'returned status code', raw_reply.status_code, 'with content:', raw_reply.content.decode())
        for k in sorted(raw_reply.headers):
            print(k,":",raw_reply.headers[k])
        return None
    if raw:
        return raw_reply
    reply = json.loads(raw_reply.content.decode('utf-8'))
    if 'Message' in reply:
        log('Message: ' + reply['Message'])
    return reply


class Model:
    """
    Base class for models. deserialize a class from a dictionary
    """

    def create(self, data):
        #print('------------>', self.__class__.__name__)
        if data is None:  # we had an error :-(
            #print('<<<<<no data<', self.__class__.__name__)
            return
        for key, value in data.items():
            if hasattr(self, key):
                #print('Processing', key)
                attr_type = getattr(self, key)
                if value is None:
                    setattr(self, key, None)
                    continue
                # type is either a simple type, a subtype of Model, or a list of types.
                is_list = type(attr_type) == list
                is_model = type(attr_type) == type and issubclass(attr_type, Model)
                is_simple = not is_list and not is_model
                if is_simple:
                    #print(' simple', attr_type, value)
                    setattr(self, key, attr_type(value))
                elif is_model:
                    #print(' ** model', attr_type)
                    empty_value = attr_type()
                    full_value = empty_value.create(value)
                    setattr(self, key, full_value)
                else:  # is_list
                    if type(value) != list:
                        log('Expected a list for key ' + key + ' in model ' + self.__name__)
                        continue
                    list_type = attr_type[0]
                    #is_model_list = type(list_type) == type and issubclass(list_type, Model)
                    is_model_list = issubclass(list_type, Model)
                    list_value = []
                    for raw_value in value:
                        if not is_model_list:
                            list_value.append(list_type(raw_value))
                        else:
                            empty_value = list_type()
                            full_value = empty_value.create(raw_value)
                            list_value.append(full_value)
                    setattr(self, key, list_value)
        #print('<<<<<<<<<<<<<', self.__class__.__name__)

        return self


class Account(Model):
    ChurchId = int
    ChurchUserId = int
    IsOwner = bool
    ChurchName = str
    Role = str
    ChurchSubscriptionStatus = str
    SubscriptionTypeId = int
    SubscriptionClassId = int
    ImgUrl = str
    IsRegistered = bool
    IsSpecialOffer = bool


class TopLevel(Model):
    token = str
    IsNorthAmerican = bool
    ExpiresOn = int  # seconds since 1970
    accounts = [Account]
    churchUserId = str


class Publisher(Model):
    pass  # TODO: fill this in


class Speaker(Model):
    Summary = str
    FirstName = str
    LastName = str
    SpeakerID = int
    ImgUrl = str  # nullable
    WebUrl = str


class Session(Model):
    Duration = int
    Title = str
    SessionID = int
    SeriesID = int
    ContentID = int
    Sequence = int
    Summary = str
    VimeoID = str
    ImgUrl = str
    ContentTypeID = int


class Content(Model):
    BannerUrl = str
    ContentID = int
    ContentSourceID = int
    ContentTypeID = int
    Duration = int
    ExternalContentID = str  # Not sure. This can be None
    ImgUrl = str
    Publisher = Publisher
    Speaker = Speaker
    Summary = str
    Title = str
    Sessions = [Session]


class Channel(Model):
    Name = str
    ChannelID = int
    ChannelTypeID = int
    IsCustom = bool
    Content = [Content]
    Sequence = int


class Library(Model):
    """
    Library list with empty channels: url_library_all
    Single Library with populated channels: url_library + LibraryID
    """
    LibraryID = int
    Channels = [Channel]
    IsCustom = bool
    Name = str


class Data:
    top_level = None
    libraries = []

    def __init__(self):
        pass

    def authenticate(self, user, pswd):
        self.top_level = TopLevel()
        reply = POST(url_auth, {'username': user, 'password': pswd})
        print(reply)
        if reply is None:
            return
        self.top_level.create(reply)
        global token
        token = self.top_level.token

    def library_all(self):
        self.libraries = []
        reply = POST(url_library_all)
        if reply is None:
            return
        for raw_lib in reply:
            new_lib = Library()
            new_lib.create(raw_lib)
            self.libraries.append(new_lib)

    def library(self, id):
        liblist = [lib for lib in self.libraries if lib.LibraryID == id]
        library = Library()
        reply = POST(url_library + str(id))
        if reply is None:
            return
        library.create(reply)
        if len(liblist) == 0:
            self.libraries.append(library)
        else:
            self.libraries = [x if x.LibraryID != id else library for x in self.libraries] # Yuk, but works

    def recently_watched_add(self, content_id):
        dct = {'ContentID' : content_id,
               'LastWatchedOn' : int(time.time()),
               'LastPosition' : 0}


D = Data()
user,pswd = [x.strip() for x in open('DO_NOT_COMMIT')]
D.authenticate(user,pswd)