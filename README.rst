Right Now Media API documentation/discovery
===========================================

Data Model
----------

:Account:
  ChurchId  
  ChurchUserId  
  IsOwner  
  ChurchName  
  Role  
  ChurchSubscriptionStatus  
  SubscriptionTypeId  
  SubscriptionClassId  
  ImgUrl  
:AdBanner:
  Height  
  Width  
  ImageUrl  
CastMetadata:
:Channel:
  ChannelID  
  Name  
  ChannelTypeID  
  IsCustom  
  Sequence  
  Content  *nullable*  
:Content:
  ContentID  
  Title  
  ContentTypeID  
  Summary  
  ImgUrl  
  BannerURL  
  Speaker    *nullable*
  Publisher    *nullable*
  Sessions    *nullable*
  Duration  
:Library:
  LibraryID  
  Name  
  IsCustom  
  Channels    *nullable*
:LibraryAdvertisement:
  AdvertisementID  
  ContentID  
  LinkUrl  
  AdBanners    *nullable*
  Content    *nullable*
:Publisher:
  PublisherID  
  Name  
  Summary  
  WebUrl  
  ImgUrl  
:RecentlyWatchedSession:
  ContentID  
  LastWatchedOn  
  LastPosition  
  Content    *nullable*
  ParentContent    *nullable*
  IsCompleted  
:SearchParameters:
:SearchResults:
  BibleStudies  
  KidsSeries  
:Series:
  ContentID  
  Summary  
  Title  
  InQueue  
  ImgUrl  
  BannerUrl  
  Publisher    *nullable*
  Speaker    *nullable*
  Supplements    *nullable*
  Sessions    *nullable*
:Session:
  Duration  
  Title  
  SessionID  
  SeriesID  
  ContentID  
  Sequence    *nullable*
  Summary  
  VimeoID  
  ImgUrl  
  ContentTypeID  
:SessionWithProgress:
:Settings:
  KidsEnabled  
:Show:
  ShowID  
  ContentID  
  Title  
  Publisher  
  ImgUrl  
  InQueue  
  Sessions    *nullable*
:Speaker:
  SpeakerID  
  FirstName  
  LastName  
  Title  
  Summary  
  WebUrl  
  ImgUrl  
:Supplement:
  SupplementID  
  Title  
  Link  
  Type  
  Format  
:User:
  FirstName  
  LastName  
  Email  
  UserImageUrl  
