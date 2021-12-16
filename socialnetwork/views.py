from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db import models
from django.utils import timezone
from django.http import HttpResponse, Http404

# Django transaction system so we can use @transaction.atomic
from django.db import transaction

from socialnetwork.forms import *
from socialnetwork.models import *



# Create your views here.
def login_action(request):
	context = {}

	#display the registration form on a GET request
	if request.method == 'GET':
		context['form'] = LoginForm()
		return render(request, 'socialnetwork/login.html', context)

	form = LoginForm(request.POST)
	context['form'] = form



	# validate the form
	if not form.is_valid():
		return render(request, 'socialnetwork/login.html', context)

	new_user = authenticate(username=form.cleaned_data['username'],
							password=form.cleaned_data['password'])

	login(request, new_user)

	return redirect(reverse('global_stream'))

def logout_action(request):
    logout(request)
    return redirect(reverse('login'))

@transaction.atomic
def register_action(request):
	context = {}

	if request.method == 'GET':
		context['form'] = RegistrationForm()
		return render(request, 'socialnetwork/register.html', context)

	form = RegistrationForm(request.POST)
	context['form'] = form

	if not form.is_valid():
		return render(request, 'socialnetwork/register.html', context)

	new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])

	new_user.save()

	new_user = authenticate(username=form.cleaned_data['username'], 
							password=form.cleaned_data['password'])

	login(request, new_user)
	new_profile = Profile(user=request.user, 
						  fname=request.POST['first_name'], 
						  lname=request.POST['last_name'], 
						  picture=None)
	new_profile.save()
	return redirect(reverse('global_stream'))

@login_required
def global_stream_action(request):
	user = Profile.objects.get(user=request.user)
	posts = Post.objects.all().order_by("-date")
	context = {'profile': user, 'posts': posts}
	return render(request, 'socialnetwork/global_stream.html', context)


@login_required
def follower_stream_action(request):
	user = Profile.objects.get(user=request.user)
	followers = list(user.following.all())
	posts = []
	for followed in followers:
		for post in Post.objects.filter(user=followed):
			posts.append(post)

	context = {'profile': user, 'posts': posts}
	return render(request, 'socialnetwork/follower_stream.html', context)

@login_required
def profile_page_action(request):
	context = {}
	c_user = Profile.objects.get(user=request.user)
	following = list(c_user.following.all())
	context['c_user'] = c_user
	context['following'] = following
	context['form']  = ItemForm()
	return render(request, 'socialnetwork/user_profile.html', context)


@login_required
def update_profile(request):
	context = {}
	c_user = Profile.objects.get(user=request.user)
	context['c_user'] = c_user
	context['form']  = ItemForm()

	if request.method == 'POST':
		return render(request, 'socialnetwork/user_profile.html', context)

	return render(request, 'socialnetwork/user_profile.html', context)


@login_required
def goto_profile(request, user):
	context = {}
	p_user = User.objects.get(username=user)
	profile = Profile.objects.get(user=p_user)
	c_user = Profile.objects.get(user=request.user)
	following = list(c_user.following.all())

	if (profile.user == c_user.user): 
		return redirect(reverse('user_profile_page'))

	name = profile.fname + ' ' + profile.lname
	context['c_user'] = c_user
	context['profile'] = profile
	context['following'] = following
	if (profile.user in following):
		context['following'] = True
	else:
		context['following'] = False

	context['name'] = name
	return render(request, 'socialnetwork/profile.html', context)

@login_required
def update_follow(request, user):
	context = {}
	p_user = User.objects.get(username=user)
	f_user = Profile.objects.get(user=p_user)
	c_user = Profile.objects.get(user=request.user)
	following = list(c_user.following.all())
	context['c_user'] = c_user
	context['profile'] = user
	context['following'] = following

	if (f_user.user in following):
		c_user.following.remove(f_user.user)
		c_user.save()
		context['following'] = False
	elif (f_user.user not in following):
		c_user.following.add(f_user.user) 
		c_user.save()
		context['following'] = True

	return goto_profile(request, user)

@login_required
def create_post(request):
	errors = []
	if 'post_input' not in request.POST or not request.POST['post_input']:
		errors.append('You cannot make a blank post')
	else:
		post = Post(text=request.POST['post_input'], 
				    user=request.user, 
				    fname=request.user.first_name, 
				    lname=request.user.last_name,
				    date=timezone.now())
		post.save()
	posts = Post.objects.all().order_by("-date")
	profile = Profile.objects.get(user=request.user)
	context = {'posts': posts, 'errors': errors, 'profile':profile}
	return render(request, 'socialnetwork/global_stream.html', context)

@login_required
def add_propic(request):
	context = {}
	c_user = Profile.objects.get(user=request.user)
	following = list(c_user.following.all())
	context['c_user'] = c_user
	context['following'] = following
	form = ItemForm(request.POST, request.FILES, instance=c_user)
	c_user.bio = request.POST['bio_text']
	if not form.is_valid():
		context['form'] = form

	else:
	    # Must copy content_type into a new model field because the model
	    # FileField will not store this in the database.  (The uploaded file
	    # is actually a different object than what's return from a DB read.)
	    pic = form.cleaned_data['picture']
	    c_user.content_type = form.cleaned_data['picture'].content_type
	    form.save()
	    c_user.picture = pic
	    context['form'] = ItemForm()
	c_user.save()
	context['name'] = c_user.fname + ' ' + c_user.lname
	return render(request, 'socialnetwork/user_profile.html', context)

def get_photo(request, id):
	item = get_object_or_404(Profile, id=id)

	# Maybe we don't need this check as form validation requires a picture be uploaded.
	# But someone could have delete the picture leaving the DB with a bad references.
	if not item.picture:
	    raise Http404

	return HttpResponse(item.picture, content_type=item.content_type)


