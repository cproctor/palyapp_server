# Paly App

This is the server for a pilot mobile app to distribute Paly's journalism 
content over mobile. The pilot app's goals are to increase reader participation, 
feedback, and discussion. We will do this by:

- Developing a filtering/tagging system to help readers find content they care about,
- Providing a forum for discussion. Users must register, but can post anonymously or with their names attached
- Making reader comments a more significant part of the content
- Helping connect readers with journalists

## Installation

### Required libraries

- django (web framework)
- djangorestframework (extends django to provide REST functionality)
- drf-extensions (allows routing nested requests, such as a story's comments)
- beautifulsoup4 (parse html)
- feedparser (parse rss feeds)
- boto (interface with Amazon s3 to store images)
- django-storages (connect boto to django)
- requests (make http requests)
- pillow (image handling)
- pytz (time zone support)

## Next Steps

- Add a comments model
    - Allow user signup, so that users can create accounts (mapped to particular devices)
- Once concept is defined for the app, what social/interactive components will there be?

## MVP Goals

- Sync management task can pull updates from all publication feeds. 
- Stories, publications, comments, and categories available via REST interface.
