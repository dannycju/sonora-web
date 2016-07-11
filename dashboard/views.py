import os
import sys

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from mongoengine import *
import mongoengine_goodjson as gj
from bson.objectid import ObjectId
from tzlocal import get_localzone

from user.views import find_user
from bookmark.views import Folder, Bookmark, find_folders, find_bookmarks
from .stack_exchange_api import stack_exchange_api
from .scopus_api import scopus_api

def index(request):
    if "user_id" in request.session:
        user = find_user(request.session["user_id"])
        if user:
            # Fetch folders
            folders = find_folders(request.session["user_id"])
            # Fetch bookmarks without folder
            bookmarks = find_bookmarks(request.session["user_id"], no_folder=True)

            local_tz = get_localzone()
            timezone.activate(local_tz)

            return render(request,
                          "dashboard/dashboard.html",
                          {
                              "title": "Dashboard",
                              "user": user,
                              "folders": folders,
                              "bookmarks": bookmarks,
                          })
        else:
            return redirect("signup")

    return redirect("signin")


def view_folder(request, folder_id=None):
    if folder_id:
        if "user_id" in request.session:
            user = find_user(request.session["user_id"])
            if user:
                try:
                    folder = Folder.objects.get(id=ObjectId(folder_id), is_removed=False)
                except DoesNotExist:
                    return redirect("dashboard")

                bookmarks = Bookmark.objects(user=user.id,
                                             folders=[str(folder.id)],
                                             is_removed=False).order_by("-date_created")

                local_tz = get_localzone()
                # print(local_tz)
                timezone.activate(local_tz)
                # for x in range(len(bookmarks)):
                #     bookmarks[x].date_created = timezone.make_aware(bookmarks[x].date_created)

                return render(request,
                              "dashboard/folder.html",
                              {
                                  "title": folder.title,
                                  "user": user,
                                  "folder": folder,
                                  "bookmarks": bookmarks,
                              })

            else:
                return redirect("signup")
        else:
            return redirect("signin")

    return redirect("dashboard")


def related_questions(request):
    if "keywords" in request.GET:
        keywords = request.GET.get("keywords").split(",")

        question_sets = []
        for keyword in keywords:
            resp = stack_exchange_api("search",
                                      {
                                          "site": "stackoverflow",
                                          "intitle": keyword,
                                          "pagesize": 6,
                                          "page": 1,
                                          "sort": "relevance",
                                      })
            if resp:
                result = resp.json()
                question_sets.append({ "keyword": keyword, "items": result["items"] })

        html = ""
        if question_sets:
            for question_set in question_sets:
                h3 = ""
                for q in question_set["items"]:
                    h3 += """
                          <h3><a href="{link}" target="_blank">{title}</a></h3>""" \
                          .format(link=q["link"], title=q["title"])

                html += """
                        <div class="sc-keyword-container">
                            <b><span class="sc-keyword">Keyword:</span> {keyword}</b>
                        </div>
                        <div class="sc-set">
                            {h3}
                        </div>""".format(keyword=question_set["keyword"], h3=h3)

        return HttpResponse(html)

    return HttpResponse("")


def related_literatures(request):
    if "keywords" in request.GET:
        keywords = request.GET.get("keywords").split(",")

        sortby = "relevancy"
        if "sort" in request.GET:
            if request.GET.get("sort") == "cited":
                sortby += ",-citedby-count"
            elif request.GET.get("sort") == "recent":
                sortby += ",-coverDate"

        lit_sets = []
        for keyword in keywords:
            resp = scopus_api('search/scopus',
                              {
                                  'query': 'TITLE-ABS-KEY({})'.format(keyword),
                                  'field': 'identifier,doi,url,title,author,affiliation,description,publicationName,coverDate,coverDisplayDate,citedby-count',
                                  'count': 6,
                                  'start': 1,
                                  'sort': sortby,
                              })
            if resp:
                result = resp.json()
                lit_sets.append({
                                    "keyword": keyword,
                                    "entry": result["search-results"]["entry"]
                                })

        html = ""
        if lit_sets:
            for key_ls, lit_set in enumerate(lit_sets):
                div = ""
                authors = ""
                for key_lit, lit in enumerate(lit_set["entry"]):
                    if "author" in lit:
                        authors += ", ".join([au["authname"] for au in lit["author"]])
                        year_authors = "{year} - {authors}<br>" \
                                        .format(year=lit["prism:coverDate"][0:4],
                                                authors=authors)
                    else:
                        year_authors = """
                            <div style="display:inline-block;width:4em;">{year}</div>""" \
                            .format(year=lit["prism:coverDate"][0:4])

                    if "dc:description" in lit:
                        desc_toggle = """
                            <div style="display:inline-block;width:8.5em;">
                                <button class="link link-dotted-under" data-toggle="collapse"
                                 data-target="#lit-{key_ls}-{key_lit}"
                                 onclick="toggleShowAbstract(this);">Show Abstract</button>
                            </div>""" \
                            .format(key_ls=key_ls, key_lit=key_lit)

                        desc = """
                            <div id="lit-{key_ls}-{key_lit}" class="collapse">{description}
                            </div>""" \
                            .format(key_ls=key_ls,
                                    key_lit=key_lit,
                                    description=lit["dc:description"])
                    else:
                        desc_toggle = ""
                        desc = ""

                    if "prism:doi" in lit:
                        doi = "doi:" + lit["prism:doi"]
                    else:
                        doi = ""

                    div += """
                           <div>
                               <h3>
                                   <a href="http://dx.doi.org/{doi}"
                                    target="_blank"><b>{title}</b></a>
                               </h3>
                               <div class="details details-full">
                                   {year_authors}
                                   {desc_toggle}Cited by {cited}
                                   {desc}
                               </div>
                           </div>""" \
                           .format(doi=doi,
                                   title=lit["dc:title"],
                                   year_authors=year_authors,
                                   desc_toggle=desc_toggle,
                                   desc=desc,
                                   cited=lit["citedby-count"])

                html += """
                        <div class="sc-keyword-container">
                            <b><span class="sc-keyword">Keyword:</span> {keyword}</b>
                        </div>
                        <div class="sc-set">
                            {div}
                        </div>""".format(keyword=lit_set["keyword"], div=div)

        return HttpResponse(html)

    return HttpResponse("")


def related_researchers(request):
    if "keywords" in request.GET:
        keywords = request.GET.get("keywords").split(",")

        author_sets = []

        for keyword in keywords:
            resp = scopus_api('search/scopus',
                              {
                                  'query': 'TITLE-ABS-KEY({})'.format(keyword),
                                  'field': 'author,authid',
                                  'count': 6,
                                  'start': 1,
                                  'sort': 'relevancy,-citedby-count',
                              })
            if resp:
                result = resp.json()

                authors = []
                authnames = []  # Used for duplication checking

                for r in result['search-results']['entry']:
                    if r['author'][0]['authname'] not in authors:
                        authnames.append(r['author'][0]['authname'])
                        authors.append({
                                           'authname': r['author'][0]['authname'],
                                           'authid': r['author'][0]['authid'],
                                       })

                author_sets.append({
                                       "keyword": keyword,
                                       "authors": authors,
                                   })

        html = ""
        if author_sets:
            for author_set in author_sets:
                h3 = ""
                for au in author_set["authors"]:
                    h3 += """
                          <h3><a href="https://www.scopus.com/authid/detail.uri?authorId={authid}" target="_blank">{authname}</a></h3>""" \
                          .format(authid=au["authid"], authname=au["authname"])

                html += """
                        <div class="sc-keyword-container">
                            <b><span class="sc-keyword">Topic:</span> {keyword}</b>
                        </div>
                        <div class="sc-set">
                            {h3}
                        </div>""".format(keyword=author_set["keyword"], h3=h3)

        return HttpResponse(html)

    return HttpResponse("")
