from django.shortcuts import render, redirect, reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

# Django transaction system so we can use @transaction.atomic
from django.db import transaction

from socialnetwork.forms import LoginForm, RegistrationForm


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
	return redirect(reverse('global_stream'))

@login_required
def global_stream_action(request):

	context = {}

	if request.method == 'GET':
		return render(request, 'socialnetwork/global_stream.html', context)
	return render(request, 'socialnetwork/global_stream.html', context)


@login_required
def follower_stream_action(request):

	context = {}

	if request.method == 'GET':
		return render(request, 'socialnetwork/follower_stream.html', context)
	render(request, 'socialnetwork/follower_stream.html', context)

@login_required
def profile_page_action(request):

	context = {}

	if request.method == 'GET':
		return render(request, 'socialnetwork/user_profile.html', context)

	return render(request, 'socialnetwork/user_profile.html', context)


@login_required
def update_profile(request):
	context = {}

	if request.method == 'POST':
		print(request.POST)
		print("profile updated")
		context['bio_text'] = request.POST['bio_text']
		return render(request, 'socialnetwork/user_profile.html', context)

	render(request, 'socialnetwork/user_profile.html', context)


@login_required
def goto_profile(request, name):
	context = {}
	if request.method == 'GET':
		context['name'] = name
		return render(request, 'socialnetwork/profile.html', context)
	context['name'] = name
	return render(request, 'socialnetwork/profile.html', context)

@login_required
def update_follow(request):
	context = {}
	if request.method == 'GET':
		return render(request, 'socialnetwork/profile.html', context)

	return render(request, 'socialnetwork/profile.html', context)

