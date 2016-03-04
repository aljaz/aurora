from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from AuroraProject.settings import MEDIA_ROOT
admin.autodiscover()

import AuroraProject.views

urlpatterns = patterns('',
    # TODO: add home without course
    url(r'^$', 'AuroraProject.views.course_selection', name='course_selection'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': MEDIA_ROOT}),

    url(r'^comment/', include('Comments.urls', namespace='Comments')),

    url(r'result_users', 'AuroraProject.views.result_users', name='result_users'),
    url(r'result_elabs_nonfinal', 'AuroraProject.views.result_elabs_nonfinal', name='result_elabs_nonfinal'),
    url(r'result_elabs_final', 'AuroraProject.views.result_elabs_final', name='result_elabs_final'),
    url(r'result_reviews', 'AuroraProject.views.result_reviews', name='result_reviews'),

    url(r'^(?P<course_short_title>(gsi|hci))/', include(patterns('',
        url(r'^$', AuroraProject.views.home, name='home'),
        url(r'^challenge/', include('Challenge.urls', namespace='Challenge')),
        url(r'^elaboration/', include('Elaboration.urls', namespace='Elaboration')),
        url(r'^review/', include('Review.urls', namespace='Review')),
        url(r'^notifications/', include('Notification.urls', namespace='Notification')),
        url(r'^evaluation/', include('Evaluation.urls', namespace='Evaluation')),
        url(r'^statistics/', include('Statistics.urls', namespace='Statistics')),
        url(r'^slides/', include('Slides.urls', namespace='Slides')),
        url(r'', include('AuroraUser.urls', namespace='User')),
        ))),

    url(r'', include('FileUpload.urls')),

    url(r'^diskurs/', include('diskurs.urls', namespace="diskurs")),
)
