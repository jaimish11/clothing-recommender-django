from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import uuid

class Preferences(models.Model):
	user = models.OneToOneField(User, null = True, blank = True, on_delete = models.CASCADE)
	preferences = models.CharField(max_length = 3000, null = True, blank = True)
	
'''class Liked(models.Model):
	user = models.OneToOneField(User, primary_key = True, default = uuid.uuid4, on_delete = models.CASCADE)
	liked_items = models.ManyToManyField('Item', blank = True, related_name = 'item_likes')

	def get_like_url(self):
		return reverse('like-toggle', args = [str(self.user.id)])
'''
class Item(models.Model):
	#id = models.UUIDField(primary_key = True, default = uuid.uuid4, help_text = 'Unique ID for this particular item')
	item_type = models.CharField(max_length = 200, null = True, blank = True)
	price = models.CharField(max_length = 200, null = True, blank = True)
	color = models.CharField(max_length = 200, null = True, blank = True)
	image_URL = models.CharField(max_length = 1000, null = True, blank = True)
	fit = models.CharField(max_length = 200, null = True, blank = True)
	occasion = models.CharField(max_length = 200, null = True, blank = True)
	brand = models.CharField(max_length = 200, null = True, blank = True)
	pattern = models.CharField(max_length = 200, null = True, blank = True)
	fabric = models.CharField(max_length = 200, null = True, blank = True)
	length = models.CharField(max_length = 200, null = True, blank = True)
	likes = models.ManyToManyField(User, blank = True, related_name = 'item_likes')

	def get_absolute_url(self):
		"""Returns the url to access a detail record for this item"""
		return reverse('item-detail', args = [str(self.id)])

	def get_total_likes(self):
		return self.likes.count()

	def get_items(self):
		return reverse('items')

	def get_random_liked_url(self):
		return reverse('index')
