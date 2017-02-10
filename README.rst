Right Now Media API documentation/discovery
===========================================

Data Model
----------

:Account:
  | ChurchId  ``int``
  | ChurchUserId  ``int``
  | IsOwner  ``bool``
  | ChurchName  
  | Role  
  | ChurchSubscriptionStatus  
  | SubscriptionTypeId  ``int``
  | SubscriptionClassId  ``int``
  | ImgUrl  
:AdBanner:
  | Height  ``int``
  | Width  ``int``
  | ImageUrl
:CastMetadata:
:Channel:
  | ChannelID  ``int``
  | Name  
  | ChannelTypeID  ``int``
  | IsCustom  ``bool``
  | Sequence  ``int``
  | Content  ``List<Content>`` *nullable*
:Content:
  | ContentID  ``int``
  | Title  
  | ContentTypeID  ``int``
  | Summary  
  | ImgUrl  
  | BannerURL  
  | Speaker  ``Speaker``  *nullable*
  | Publisher  ``Publisher``  *nullable*
  | Sessions  ``List<Session>``  *nullable*
  | Duration  ``int``
:Library:
  | LibraryID  ``int``
  | Name  
  | IsCustom  ``bool``
  | Channels  ``List<Channel>``  *nullable*
:LibraryAdvertisement:
  | AdvertisementID  ``int``
  | ContentID  ``int``
  | LinkUrl  
  | AdBanners    *nullable*
  | Content    *nullable*
:Publisher:
  | PublisherID  ``int``
  | Name  
  | Summary  
  | WebUrl  
  | ImgUrl  
:RecentlyWatchedSession:
  | ContentID  ``int``
  | LastWatchedOn  ``int``
  | LastPosition  ``int``
  | Content  ``Session``  *nullable*
  | ParentContent  ``Content``  *nullable*
  | IsCompleted  ``bool``
:SearchParameters:
:SearchResults:
  | BibleStudies  ``Channel``
  | KidsSeries  ``Channel``
:Series:
  | ContentID  ``int``
  | Summary  
  | Title  
  | InQueue  ``bool``
  | ImgUrl  
  | BannerUrl  
  | Publisher  ``Publisher``  *nullable*
  | Speaker  ``Speaker``  *nullable*
  | Supplements  ``List<Supplement>``  *nullable*
  | Sessions  ``List<Sessions>``  *nullable*
:Session:
  | Duration  ``int``
  | Title  
  | SessionID  ``int``
  | SeriesID  ``int``
  | ContentID  ``int``
  | Sequence  ``int``  *nullable*
  | Summary  
  | VimeoID  
  | ImgUrl  
  | ContentTypeID  ``int``
:SessionWithProgress:
:Settings:
  | KidsEnabled  ``bool``
:Show:
  | ShowID  ``int``
  | ContentID  ``int``
  | Title  
  | Publisher  
  | ImgUrl  
  | InQueue  ``bool``
  | Sessions  ``List<Sessions>``  *nullable*
:Speaker:
  | SpeakerID  ``int``
  | FirstName  
  | LastName  
  | Title  
  | Summary  
  | WebUrl  
  | ImgUrl  
:Supplement:
  | SupplementID  ``int``
  | Title  
  | Link  
  | Type  
  | Format  
:User:
  | FirstName  
  | LastName  
  | Email  
  | UserImageUrl  

API URLs
--------

With prefix of ``https://api.rightnow.org/api/media``:

::

"account/logo/" + i)
"authenticate");
"user")
"account")
"accounts")
"settings")
"search/all");
"content/recentlywatched/add")
"library/" + Integer.toString(i))
"library/" + Integer.toString(i) + "/ads")
"library/all")
"content/" + Integer.toString(i))
"library/default")
"content/series/" + Integer.toString(i) + "?preserveHTML=true")
"library/default/ads")
"series/session/" + Integer.toString(i))
"series/shows")
"show/session/" + Integer.toString(i))
"content/queue")
"session/" + Integer.toString(i) + "/hls")
"content/recentlywatched")
"session/" + Integer.toString(i) + "/googlecast")
"series/shows/" + Integer.toString(i))
"content/speaker/" + Integer.toString(i))
"library/custom/" + Integer.toString(i))
"library/custom/" + Integer.toString(i) + "/banner")
"content/queue/" + Integer.toString(i))
"content/queue/remove/" + Integer.toString(i))


HTTP Headers
~~~~~~~~~~~~

::

    Content-Type: application/json; charset=utf-8
    Accept: application/vnd.rnapi.v4+json   # probably 4
    Token: xyz # token was received when authenticating
    AccountIndex:  # One of the possible accounts (list received when authenticating. Assume index 0 for now)


TODO
~~~~

 * Speaker info
 * Publisher info
 * Download supplemental info?