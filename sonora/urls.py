"""sonora URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

from user import views as user_views
from bookmark import views as bookmark_views
from dashboard import views as dashboard_views

urlpatterns = [
    # url(r'^admin/', admin.site.urls),

    url(r'^signup/$', user_views.signup, name='signup'),
    url(r'^signin/$', user_views.signin, name='signin'),
    url(r'^signout/$', user_views.signout, name='signout'),
    url(r'^profile/(?P<username>[\w-]+)/$', user_views.viewprofile, name='viewprofile'),
    url(r'^editprofile/$', user_views.editprofile, name='editprofile'),
    url(r'^completeprofile/$', user_views.completeprofile, name='completeprofile'),
    url(r'^saveprofile/$', user_views.saveprofile, name='saveprofile'),

    url(r'^dashboard/$', dashboard_views.index, name='dashboard'),
    url(r'^related_researchers/$', dashboard_views.related_researchers),
    url(r'^related_questions/$', dashboard_views.related_questions),
    url(r'^related_literatures/$', dashboard_views.related_literatures),
    url(r'^folder/(?P<folder_id>[\w]+)/$', dashboard_views.view_folder, name='viewfolder'),

    url(r'^newbookmarkfromextension/$', bookmark_views.new_bookmark_from_extension, name='newbookmarkfromextension'),
    url(r'^newbookmark/$', bookmark_views.new_bookmark, name='newbookmark'),
    url(r'^editbookmark/(?P<bookmark_id>[\w]+)/$', bookmark_views.edit_bookmark, name='editbookmark'),
    url(r'^savebookmark/(?P<bookmark_id>[\w]+)/$', bookmark_views.save_bookmark, name='savebookmark'),
    url(r'^removebookmark/(?P<bookmark_id>[\w]+)/$', bookmark_views.remove_bookmark, name='removebookmark'),

    url(r'^newfolder/$', bookmark_views.new_folder, name='newfolder'),
    url(r'^savefolder/$', bookmark_views.save_folder, name='savefolder'),
    url(r'^savefolder/(?P<folder_id>[\w]+)/$', bookmark_views.save_folder, name='savefolder'),
    url(r'^editfolder/(?P<folder_id>[\w]+)/$', bookmark_views.edit_folder, name='editfolder'),
    url(r'^removefolder/(?P<folder_id>[\w]+)/$', bookmark_views.remove_folder, name='removefolder'),
]
