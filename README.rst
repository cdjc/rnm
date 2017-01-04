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
