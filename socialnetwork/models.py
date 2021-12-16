from django.db import models
from django.contrib.auth.models import User


# Post Model
class Post(models.Model):
	text = models.CharField(max_length=200)
	user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
	fname = models.CharField(max_length=20)
	lname = models.CharField(max_length=20)
	date = models.DateTimeField()

	def __str__(self):
		return 'Post(id=' + str(self.id) + ')'


class Profile(models.Model):
	user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
	fname = models.CharField(max_length=20)
	lname = models.CharField(max_length=20)
	bio = models.CharField(max_length=200)
	following = models.ManyToManyField(User, related_name='following')
	picture = models.FileField(blank=True, upload_to='socialnetwork/static/img')
	content_type = models.CharField(max_length=50, blank=True)

	def __str__(self):
		return 'Profile(id=' + str(self.id) + ')'