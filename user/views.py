from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from mongoengine import *
from bson.objectid import ObjectId
import bcrypt

class User(DynamicDocument):
    username = StringField(unique=True, required=True)
    password = StringField(required=True)
    email = EmailField(required=True)
    firstname = StringField(default="")
    lastname = StringField(default="")
    biodata = StringField(default="")
    topics = DynamicField(default=[])
    date_created = DateTimeField(default=timezone.now())
    date_updated = DateTimeField(default=timezone.now())
    is_deleted = BooleanField(default=False)
    meta = {"collection": "users"}

def hash_pw_str(password, hashed=""):
    if hashed:
        return ( bcrypt.hashpw(password.encode("utf-8"), hashed.encode("utf-8")) ).decode("utf-8")
    else:
        return ( bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()) ).decode("utf-8")

def signup(request):
    if request.method == 'POST':
        # Check email attribute for sign up submission
        if request.POST.__contains__('email'):
            username = (request.POST.get('username')).strip()
            password = (request.POST.get('password')).strip()
            email = (request.POST.get('email')).strip()

            user = User(username=username, password=hash_pw_str(password), email=email)

            try:
                user.save()
            except NotUniqueError:
                return render(request,
                              "user/signup.html",
                              {
                                  "title": "Username Has Already Been Taken",
                                  "username": username,
                                  "email": email,
                                  "username_error_msg":
                                      """Email has already been taken.
                                      Please try other email."""
                              })
            else:
                request.session["user_id"] = str(user.id)
                return redirect("completeprofile")

        # For sign up page requested through sign in page
        else:
            username = (request.POST.get('username')).strip()
            return render(request,
                          "user/signup.html",
                          {
                              "title": "Sign Up for Sonora",
                              "username": username
                          })

    else:
        return render(request,
                      "user/signup.html",
                      {"title": "Sign Up for Sonora"})

def find_user(user_id):
    try:
        user = User.objects.get(id=ObjectId(user_id))
    except DoesNotExist:
        return None
    else:
        return user

def find_user_by_username(username):
    try:
        user = User.objects.get(username=username)
    except DoesNotExist:
        return None
    else:
        return user

def signin(request):
    if "signed_out" in request.session:
        try:
            del request.session['signed_out']
        except KeyError:
            pass

        return render(request,
                      "user/signin.html",
                      {
                          "title": "Sign In to Sonora",
                          "message": "You have been signed out."
                      })

    # Attempt to sign user in
    if request.method == 'POST':
        username = (request.POST.get('username')).strip()
        password = (request.POST.get('password')).strip()

        try:
            user = User.objects.get(username=username)
        except DoesNotExist:
            return render(request,
                          "user/signin.html",
                          {
                              "title": "Account Not Found",
                              "username": username,
                              "username_error_msg":
                                  """No user found with this username.
                                  Click "Sign up now" link below
                                  if you want to create an user."""
                          })
        except MultipleObjectsReturned:
            # TODO: log error
            pass
        else:
            if hash_pw_str(password, user.password) == user.password:
                request.session["user_id"] = str(user.id)
                return redirect("dashboard")
            else:
                return render(request,
                              "user/signin.html",
                              {
                                  "title": "Username and Password Do Not Match",
                                  "username": username,
                                  "password_error_msg":
                                      """Username and password do not match."""
                                      # user.password + " (" + hash_pw_str(password, user.password) + ")"
                              })

    elif "user_id" in request.session:
        user = find_user(request.session["user_id"])
        if user:
            # If user already signed in, redirect to dashboard
            return redirect("dashboard")

    return render(request,
                  "user/signin.html",
                  {"title": "Sign In to Sonora"})


# @csrf_exempt
# def signin_from_extension(request):
#     # Check if user has already signed in
#     if "user_id" in request.session:
#         if find_user(request.session["user_id"]):
#             return JsonResponse({"signed_in": True})
#     return JsonResponse({"signed_in": False})

def signout(request):
    try:
        del request.session['user_id']
    except KeyError:
        pass

    request.session['signed_out'] = ""

    return redirect("signin")

def completeprofile(request):
    if "user_id" in request.session:
        user = find_user(request.session["user_id"])
        if user:
            heading = """Hello, {}! Your profle has been created.
                      You could take a moment to complete
                      your profile.""".format(user.username)

            return render(request,
                          "user/editprofile.html",
                          {
                              "title": "Edit Profile",
                              "heading": heading
                          })

    return redirect("signin")

def editprofile(request):
    if "user_id" in request.session:
        user = find_user(request.session["user_id"])
        if user:
            return render(request,
                          "user/editprofile.html",
                          {
                              "title": "Edit Profile",
                              "heading": "Edit Profile",
                              "firstname": user.firstname,
                              "lastname": user.lastname,
                              "biodata": user.biodata,
                              "topics": user.topics,
                          })

    return redirect("signin")

def saveprofile(request):
    if request.method == 'POST':
        if "user_id" in request.session:
            user = find_user(request.session["user_id"])
            if user:
                firstname = (request.POST.get('firstname')).strip()
                lastname = (request.POST.get('lastname')).strip()
                biodata = (request.POST.get('biodata')).strip()

                topics = []
                topics_str = (request.POST.get('topics')).strip()
                if topics_str != "":
                    topics = topics_str.split(",")
                    topics = [topic.strip() for topic in topics]

                user.update(firstname=firstname,
                            lastname=lastname,
                            biodata=biodata,
                            topics=topics)

                request.session["profile_saved"] = ""

                return redirect("viewprofile", username=user.username)

    return redirect("signin")

def viewprofile(request, username):
    if username:
        user = find_user_by_username(username)
        if user:
            if "user_id" in request.session:
                if request.session["user_id"] == str(user.id):
                    if "profile_saved" in request.session:
                        try:
                            del request.session['profile_saved']
                        except KeyError:
                            pass

                        message = "Your profile has been saved."
                    else:
                        message = ""

                    return render(request,
                                  "user/viewprofile.html",
                                  {
                                      "title": "Profile Information",
                                      "username": username,
                                      "firstname": user.firstname,
                                      "lastname": user.lastname,
                                      "biodata": user.biodata,
                                      "topics": user.topics,
                                      "message": message,
                                      "edit": True,
                                  })

            return render(request,
                          "user/viewprofile.html",
                          {
                              "title": "Profile Information",
                              "firstname": user.firstname,
                              "lastname": user.lastname,
                              "biodata": user.biodata,
                              "topics": user.topics,
                              "edit": False,
                          })
        else:
            return HttpResponse("User not found")

    return redirect("signin")

