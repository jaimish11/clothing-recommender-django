from django.test import TestCase
from recommender.models import Item

class ItemModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Item.objects.create(item_type = 'jeans')

    def test_item_type_label(self):
        item = Item.objects.get(id=1)
        field_label = item._meta.get_field('item_type').verbose_name
        self.assertEquals(field_label, 'item type')

    def test_color_label(self):
        item=Item.objects.get(id=1)
        field_label = item._meta.get_field('color').verbose_name
        self.assertEquals(field_label, 'color')

    def test_image_url_length(self):
        item = Item.objects.get(id=1)
        max_length = item._meta.get_field('image_URL').max_length
        self.assertEquals(max_length, 1000)

    def test_get_absolute_url(self):
        item = Item.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEquals(item.get_absolute_url(), '/recommender/item/1')