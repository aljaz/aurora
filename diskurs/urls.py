from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^(?P<thread_id>[0-9]+)/newpost/$', views.new_post, name='new_post'),
    url(r'^(?P<thread_id>[0-9]+)/upvote/(?P<post_id>[0-9]+)/$', views.upvote_post, name='upvote_post'),
    url(r'^(?P<thread_id>[0-9]+)/downvote/(?P<post_id>[0-9]+)/$', views.downvote_post, name='downvote_post'),
    url(r'^(?P<thread_id>[0-9]+)/delete/(?P<post_id>[0-9]+)/$', views.delete_post, name='delete_post'),
    # ex: /diskurs/5/
    url(r'^(?P<thread_id>[0-9]+)/$', views.thread, name='thread'),
    url(r'^(?P<thread_id>[0-9]+)/post/(?P<post_id>[0-9]+)/$', views.thread_post, name='thread_post'),
]