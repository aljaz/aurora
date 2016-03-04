from django.conf import settings
from django.db import models
from django.db.models.aggregates import Sum
from django.contrib.auth.models import User

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars')


class Post(models.Model):
    content = models.TextField('content')
    #post_nr_in_thread_by_user = models.IntegerField('sequenced number for a user post inside one thread')
    parent_post = models.ForeignKey('self', null=True, blank=True)
    user = models.ForeignKey(AUTH_USER_MODEL)
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return_string = str(self.id) + ' - ' + self.content[0:50];

        if len(self.content) > 50:
            return_string += '...'

        return return_string

    @property
    def sum_votes(self):
        sum = self.postvote_set.aggregate(Sum('value'))
        if sum.get('value__sum'):
            return sum.get('value__sum')
        else:
            return 0


class Thread(models.Model):
    title = models.TextField(max_length=512)
    first_post = models.ForeignKey(Post)
    user = models.ForeignKey(AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)


class Favorite(models.Model):
    post = models.ForeignKey(Post)
    user = models.ForeignKey(AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)


class PostVote(models.Model):
    post = models.ForeignKey(Post)
    user = models.ForeignKey(AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    value = models.IntegerField()