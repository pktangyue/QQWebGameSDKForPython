from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView
from polls.models import Poll

urlpatterns = patterns('',
    url(r'^$','oauth_test.views.index'),
    url(r'^test_conn$','oauth_test.views.test_conn'),
    url(r'^callback$','oauth_test.views.callback'),
    url(r'^profile$','oauth_test.views.profile'),
    url(r'^friends$','oauth_test.views.friends'),
    url(r'^connect$','oauth_test.views.connect'),
    url(r'^weibo_display$','oauth_test.views.weibo_display'),
)
