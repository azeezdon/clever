from django.db import models
from tinymce import HTMLField
from blog.utils import unique_slug_generator
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from mptt.models import MPTTModel, TreeForeignKey
from django.urls import reverse
from django.db.models.signals import pre_save
from django.utils import timezone
from taggit.managers import TaggableManager
from meta.models import ModelMeta


# Create your models here.


class Post(ModelMeta, models.Model):
    class NewManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(status='published')

    options = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    title = models.CharField(max_length=100)
    overview = models.TextField()
    publish = models.DateTimeField(default=timezone.now)

    # comment_count =models.IntegerField(default=0)
    # view_count =models.IntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=250, blank=True, unique_for_date='publish')
    thumbnail = models.ImageField()
    content = HTMLField('content')
    status = models.CharField(max_length=10, choices=options, default='draft')
    objects = models.Manager()  # default manager
    newmanager = NewManager()  # custom manager
    tags = TaggableManager()

    #   comments = GenericRelation(Comment)

    def get_absolute_url(self):
        return reverse('post_detail', args=[self.slug])

    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title


def slug_generator(sender, instance, *args, **kwargs):
    """ Generate unique slug """
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(slug_generator, sender=Post)


class Comment(MPTTModel):
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    name = models.CharField(max_length=50)
    content = models.TextField()
    publish = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    status = models.BooleanField(default=True)

    class MPTTMeta:
        order_insertion_by = ['publish']

    class Meta:
        ordering = ['tree_id', 'lft']

    def __str__(self):
        return 'Comment {} by {}'.format(self.content, self.name)
