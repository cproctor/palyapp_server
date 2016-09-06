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


What's next? I need a way for new users to register, and I need to create comments tagged to users. 
- Restrict Stories and Publications to readonly. 
- Restrict comment reads to authenticated users. 
- Restrict comment edits to comment owner.

- Tagging policy?

- Add profile objects 
    - student id


I need to get a little fancy with the comments:
    - When comments are created, the author should be taken from the Request.
        - This seems like I will need some customization in the ViewSet. It needs an appropriate 
          permission, and the create action needs to be overwitten to take the value from request.
    - When a serialized representation is made for a comment, it should only contain an author
      if the comment was made non-anonymous. 

    - Add routes for users' comments and for storys' comments


What exactly do I want from the comments?
    When creating a comment, just work.

