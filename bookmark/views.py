import re
import json
import requests
from bs4 import BeautifulSoup

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from mongoengine import *
import mongoengine_goodjson as gj
from bson.objectid import ObjectId

from user.views import find_user

class Bookmark(gj.Document):
    user = ObjectIdField(required=True)
    url = URLField(required=True)
    title = StringField(required=True)
    metadata = DictField(default={})
    folders = DynamicField(default=[])
    date_created = DateTimeField(default=timezone.now())
    date_updated = DateTimeField(default=timezone.now())
    is_removed = BooleanField(default=False)
    meta = {"collection": "bookmarks"}

class Folder(gj.Document):
    user = ObjectIdField(required=True)
    title = StringField(required=True)
    description = StringField(default="")
    keywords = DynamicField(default=[])
    date_created = DateTimeField(default=timezone.now())
    date_updated = DateTimeField(default=timezone.now())
    is_removed = BooleanField(default=False)
    meta = {"collection": "folders"}


@csrf_exempt
def new_bookmark_from_extension(request):
    # import time
    # time.sleep(1)
    # return JsonResponse({"message": "bookmard_saved"})

    # Make sure the request is in JSON format
    if re.match(r"^application/json\b", request.META["CONTENT_TYPE"], re.I):
        # Check if user has already signed in
        if "user_id" in request.session:
            user = find_user(request.session["user_id"])
            if user:
                request_content = json.loads(request.body.decode("utf-8"))

                bookmark = Bookmark.objects(user=user.id, url=request_content["url"]).first()
                if bookmark and not bookmark.is_removed:
                    return JsonResponse({"message": "bookmark_already_exist"})
                else:
                    title = request_content["title"]
                    if re.match(r"^https?://", title, re.I):
                        if "og_title" in request_content["metadata"]:
                            title = request_content["metadata"]["og_title"]
                        elif "twitter_title" in request_content["metadata"]:
                            title = request_content["metadata"]["twitter_title"]

                    new_bookmark = Bookmark(
                        user=ObjectId(request.session["user_id"]),
                        title=title,
                        url=request_content["url"],
                        metadata=request_content["metadata"]
                    )
                    new_bookmark.save()

                    if bookmark:
                        if bookmark.is_removed:
                            bookmark.delete()

                    # return HttpResponse(Bookmark.objects(url=request_content["url"]).to_json(indent=2))
                    return JsonResponse({"message": "bookmark_saved"})

            else:
                return JsonResponse({"message": "user_not_found"})
        else:
            return JsonResponse({"message": "sign_in_required"})

    return JsonResponse({"message": "bad_request"})


def fetch_details(url):
    if url:
        result = requests.get(url)
        if result.status_code != 200:
            return ''

        soup = BeautifulSoup(result.text, 'html.parser')

        details = {}
        details['title'] = soup.title.string

        metadata = {}
        for meta in soup.find_all('meta'):
            if meta.has_attr('content'):
                value = meta['content']
            elif meta.has_attr('value'):
                value = meta['value']
            else:
                value = ''

            if not value:
                continue

            if meta.has_attr('property'):
                attribute = meta['property']
            elif meta.has_attr('name'):
                attribute = meta['name']
            else:
                attribute = ''

            root = attribute.split(':', 1)[0]
            if root != 'description' and \
               root != 'keywords' and \
               root != 'twitter' and \
               root != 'og' and \
               root != 'fb' and \
               root != 'article' and \
               root != 'music' and \
               root != 'video' and \
               root != 'profile':
               continue;

            attribute = attribute.replace(':', '_')

            metadata[attribute] = value

        details['metadata'] = metadata
        return details

    return ''


def new_bookmark(request):
    if "user_id" in request.session:
        user = find_user(request.session["user_id"])
        if user:
            if request.method == 'POST':
                if request.POST.get('folders') != '':
                    folders = [request.POST.get('folders')]
                else:
                    folders = []

                url = (request.POST.get('url')).strip()

                bookmark = Bookmark.objects(user=user.id, url=url).first()
                if bookmark and not bookmark.is_removed:
                    pass
                    # return JsonResponse({"message": "bookmark_already_exist"})
                else:
                    details = fetch_details(url)

                    title = details["title"]
                    if re.match(r"^https?://", title, re.I):
                        if "og_title" in details["metadata"]:
                            title = details["metadata"]["og_title"]
                        elif "twitter_title" in details["metadata"]:
                            title = details["metadata"]["twitter_title"]

                    new_bookmark = Bookmark(
                        user=ObjectId(request.session["user_id"]),
                        folders=folders,
                        title=title,
                        url=url,
                        metadata=details["metadata"]
                    )

                    new_bookmark.save()

                    if bookmark:
                        if bookmark.is_removed:
                            bookmark.delete()

                if folders :
                    return redirect("viewfolder", folder_id=folders[0])

                return redirect("dashboard")

            else:
                folders = find_folders(request.session["user_id"])
                return render(request,
                              "bookmark/newbookmark.html",
                              {
                                  "title": "New Bookmark",
                                  "user": user,
                                  "folders": folders,
                              })

        else:
            redirect("signup")

    return redirect("dashboard")


def edit_bookmark(request, bookmark_id=None):
    if bookmark_id:
        if "user_id" in request.session:
            user = find_user(request.session["user_id"])
            if user:
                try:
                    bookmark = Bookmark.objects.get(id=ObjectId(bookmark_id))
                except DoesNotExist:
                    return redirect("dashboard")
                else:
                    if str(bookmark.user) == request.session["user_id"]:
                        if bookmark.folders:
                            redirect_target = "/folder/{}/".format(bookmark.folders[0])
                            original_folder_id = ObjectId(bookmark.folders[0])
                        else:
                            redirect_target = "/dashboard/"
                            original_folder_id = ""

                        folders = find_folders(request.session["user_id"])

                        return render(request,
                                      "bookmark/editbookmark.html",
                                      {
                                          "title": "Edit Bookmark",
                                          "user": user,
                                          "folders": folders,
                                          "bookmark": bookmark,
                                          "original_folder_id": original_folder_id,
                                          "redirect_target": redirect_target,
                                      })
            else:
                return redirect("signup")

    return redirect("dashboard")


def save_bookmark(request, bookmark_id=None):
    if bookmark_id:
        if "user_id" in request.session:
            user = find_user(request.session["user_id"])
            if user:
                try:
                    bookmark = Bookmark.objects.get(id=ObjectId(bookmark_id))
                except DoesNotExist:
                    return redirect("dashboard")
                else:
                    if str(bookmark.user) == request.session["user_id"]:
                        if request.POST.get('folders') == "":
                            folders = []
                        else:
                            folders = [request.POST.get('folders')]

                        title = (request.POST.get('title')).strip()
                        url = (request.POST.get('url')).strip()
                        description = (request.POST.get('description')).strip()

                        bookmark.update(folders=folders,
                                        title=title,
                                        url=url,
                                        metadata__description=description)

                        if folders:
                            return redirect("viewfolder",
                                            folder_id=folders[0])
                        else:
                            return redirect("dashboard")

                        return render(request,
                                      "bookmark/editbookmark.html",
                                      {
                                          "title": "Edit Bookmark",
                                          "user": user,
                                      })
            else:
                return redirect("signup")

    return redirect("dashboard")


def remove_bookmark(request, bookmark_id=None):
    # import time
    # time.sleep(5.25)
    # return JsonResponse({"message": "bookmark_removed"})

    if bookmark_id:
        if "user_id" in request.session:
            if find_user(request.session["user_id"]):
                try:
                    bookmark = Bookmark.objects.get(id=ObjectId(bookmark_id))
                except DoesNotExist:
                    return JsonResponse({"message": "bookmark_not_found"})
                else:
                    if str(bookmark.user) == request.session["user_id"]:
                        # bookmark.update(is_removed=True)
                        bookmark.delete()
                        return JsonResponse({"message": "bookmark_removed"})

                    return JsonResponse({"message": "operation_not_permitted"})

            else:
                return JsonResponse({"message": "user_not_found"})
        else:
            return JsonResponse({"message": "sign_in_required"})

    return JsonResponse({"message": "no_bookmark_specified"})


def new_folder(request):
    if "user_id" in request.session:
        user = find_user(request.session["user_id"])
        if user:
            return render(request,
                          "bookmark/editfolder.html",
                          {
                              "title": "New Folder",
                              "user": user,
                          })

    return redirect("signin")


def save_folder(request, folder_id=None):
    if request.method == 'POST':
        if "user_id" in request.session:
            user = find_user(request.session["user_id"])
            if user:
                if folder_id:
                    try:
                        folder = Folder.objects.get(id=ObjectId(folder_id))
                    except DoesNotExist:
                        return redirect("dashboard")
                    else:
                        title = (request.POST.get('title')).strip()
                        description = (request.POST.get('description')).strip()

                        keywords = []
                        keywords_str = (request.POST.get('keywords')).strip()
                        if keywords_str != "":
                            keywords = keywords_str.split(",")
                            keywords = [keyword.strip() for keyword in keywords]

                        folder.update(user=user.id,
                                      title=title,
                                      description=description,
                                      keywords=keywords)

                        return redirect("viewfolder",
                                        folder_id=folder_id)

                else:
                    title = (request.POST.get('title')).strip()
                    already_exist = Folder.objects(user=user.id, title=title)
                    if not already_exist:
                        description = (request.POST.get('description')).strip()

                        keywords = []
                        keywords_str = (request.POST.get('keywords')).strip()
                        if keywords_str != "":
                            keywords = keywords_str.split(",")
                            keywords = [keyword.strip() for keyword in keywords]

                        folder = Folder(user=user.id,
                                        title=title,
                                        description=description,
                                        keywords=keywords)
                        folder.save()
                        return redirect("dashboard")

                    else:
                        return redirect("dashboard")

            else:
                redirect("signup")

    return redirect("dashboard")


def edit_folder(request, folder_id=None):
    if folder_id:
        if "user_id" in request.session:
            user = find_user(request.session["user_id"])
            if user:
                try:
                    folder = Folder.objects.get(id=ObjectId(folder_id))
                except DoesNotExist:
                    return redirect("dashboard")
                else:
                    if str(folder.user) == request.session["user_id"]:
                        return render(request,
                                      "bookmark/editfolder.html",
                                      {
                                          "title": "New Folder",
                                          "user": user,
                                          "folder": folder,
                                      })

    return redirect("dashboard")


def remove_folder(request, folder_id=None):
    # import time
    # time.sleep(5.25)
    # return JsonResponse({"message": "folder_removed"})

    if not folder_id:
        return JsonResponse({"message": "no_folder_specified"})

    if "user_id" not in request.session:
        return JsonResponse({"message": "sign_in_required"})

    if not find_user(request.session["user_id"]):
        return JsonResponse({"message": "user_not_found"})

    try:
        folder = Folder.objects.get(id=ObjectId(folder_id))
    except DoesNotExist:
        return JsonResponse({"message": "folder_not_found"})
    else:
        if str(folder.user) != request.session["user_id"]:
            return JsonResponse({"message": "operation_not_permitted"})

        bookmarks = Bookmark.objects(user=ObjectId(request.session["user_id"]),
                                     folders=[str(folder.id)],
                                     is_removed=False).delete()
        folder.delete()
        return JsonResponse({"message": "folder_removed"})


def find_bookmarks(user_id, no_folder=False):
    if no_folder:
        bookmarks = Bookmark.objects(user=ObjectId(user_id),
                                     folders=[],
                                     is_removed=False).order_by("-date_created")
    else:
        bookmarks = Bookmark.objects(user=ObjectId(user_id),
                                     is_removed=False).order_by("-date_created")

    return bookmarks


def find_folders(user_id):
    folders = Folder.objects(user=ObjectId(user_id),
                             is_removed=False).order_by("title")
    return folders
