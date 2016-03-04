from django.contrib import admin
from .models import Thread
from .models import Post
from .models import UserProfile

# Register your models here.
admin.site.register(Thread)
admin.site.register(Post)
admin.site.register(UserProfile)