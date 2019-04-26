from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
	
class Item(models.Model):
	
	item_type = models.CharField(max_length = 200, null = True, blank = True)
	price = models.CharField(max_length = 200, null = True, blank = True)
	color = models.CharField(max_length = 200, null = True, blank = True)
	image_URL = models.CharField(max_length = 1000, null = True, blank = True)
	fit = models.CharField(max_length = 200, null = True, blank = True)
	occasion = models.CharField(max_length = 200, null = True, blank = True)
	brand = models.CharField(max_length = 200, null = True, blank = True)
	pattern = models.CharField(max_length = 200, null = True, blank = True)
	fabric = models.CharField(max_length = 200, null = True, blank = True)
	gender = models.CharField(max_length = 1, null = True, blank = True)
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
