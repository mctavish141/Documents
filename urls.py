from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'News.views.home', name='home'),
    # url(r'^News/', include('News.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    url(r'^$', 'News.views.index'),
    url(r'^users/$', 'News.views.users'),
    url(r'^add-article/$', 'News.views.addArticle'),
    url(r'^home/$', 'News.views.home'),
    url(r'^articles/(\d+)/$', 'News.views.showArticle'),
    url(r'^register/$', 'News.views.register'),
    url(r'^edit-article/(\d+)/$', 'News.views.editArticle'),
    url(r'^remove-article/(\d+)/$', 'News.views.removeArticle'),
    url(r'^articles/(\d+)/manage-comments/$', 'News.views.manageComments'),
    url(r'^search-articles/$', 'News.views.searchArticles'),
    url(r'^users/(?P<userLogin>.+)/$', 'News.views.showUser', name='userLogin'),
    url(r'^remove-user/(?P<userLogin>.+)/$', 'News.views.removeUser', name='userLogin'),
    url(r'^users-removed/$', 'News.views.usersRemoved'),
    url(r'^statistics/$', 'News.views.statistics'),
    url(r'^backup/$', 'News.views.backupDatabase'),
    url(r'^restore/$', 'News.views.restoreDatabase'),
    url(r'^remove-user-comments/(?P<userLogin>.+)/$', 'News.views.removeUserComments', name='userLogin'),
    url(r'^testing/$', 'News.views.testing'),
)
