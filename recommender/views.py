from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from recommender.forms import LoginForm
from recommender.models import Item, Preferences
from django.views import generic
from django.views.generic import RedirectView
from django.db.models import Max, Count
from django.db import connection
from django.http import HttpResponseRedirect, JsonResponse
from django.template.loader import render_to_string
from collections import defaultdict
from django.urls import reverse
from threading import Thread
import queue
import time
import json
from django.contrib import messages


def index(request):
	random_items = Item.objects.order_by('?').only('image_URL')[:21]
	context = {

		'index_active_page': 'active',
		'random_items': random_items,
	}
	return render(request, 'index.html', context)

def PreferenceFilterView(request):
	item_ids = []
	user_prefs = []
	ids = request.GET.get('ids')
	prefs = request.GET.get('filters')
	ids = ids.replace('[', '')
	ids = ids.replace(']', '')
	ids = ids.replace("'", '')
	ids = ids.replace(' ', '')
	prefs = prefs.replace('[', '')
	prefs = prefs.replace(']', '')
	prefs = prefs.replace('"', '')
	item_ids.append(ids.split(","))
	user_prefs.append(prefs.split(","))
	item_ids = tuple(item_ids)
	user_prefs = tuple(user_prefs)
	#print('items')
	items = []
	for i in Item.objects.filter(id__in = item_ids[0]).filter(item_type__in = user_prefs[0]).only('image_URL').values('image_URL'):
		items.append(i['image_URL'])
	#print(items)
	context = {
		'items': items,
	}
	if request.is_ajax():
		html = render_to_string('recommender/filter_section.html', context, request = request)
		return JsonResponse({'form': html})



@login_required
def RecommendedListView(request):
	model = Item
	template_name = 'recommender/recommended.html'
	paginate_by = 10
	context = {
		'recommended_active_page': 'active'
	}
	return render(request, template_name, context)

	
	def calculate_dice_coe(random_items, pks, liked_index_list, upl, column_mapping, pref, queue):
		desc_coe_list = []
		dice_coe = defaultdict(int)
		top_val_1 = []
		for i,pk in zip(range(len(random_items)),pks):
				if pk in liked_index_list:
					continue

				for j in range(0,8):

					if random_items[i][j] in 'N/A' and upl[j] in 'N/A': 
						continue
					elif random_items[i][j] in upl[j]:
						#print(random_items[i][j])
						#print(upl[j])
						if column_mapping[pref] == j:
							top_val_1.append(2)
							#print(top_val_1)
						else:
							top_val_1.append(0.5)
							#print(top_val_1)
							

				top = sum(top_val_1)
				bottom = 11
				dice_coe[str(pk)] = round((2*top)/bottom,3)
				top_val_1.clear()
				#print(dice_coe)

		desc_coe_dict = sorted(dice_coe, key = dice_coe.get, reverse = True)
		for value in desc_coe_dict:
			#print(dice_coe[value])
			#print(value)
			desc_coe_list.append(value)

		#print(desc_coe_list[:11])
		desc_coe_list1 = desc_coe_list[:11]
		#print(desc_coe_list1)
		rec = tuple([int(i) for i in desc_coe_list1])
		urls = []
		ids = []
		item = []
		#urls = Item.objects.raw('SELECT image_URL FROM recommender_item WHERE id in %s',[rec])
		for u in Item.objects.filter(id__in = rec).only('id', 'image_URL').values('id', 'image_URL'):
			urls.append(u['image_URL'])
			ids.append(u['id'])
			

		for u in Item.objects.filter(id__in = rec).only('item_type').values('item_type'):
			item.append(u['item_type'])
		
		data_rec = zip(urls,ids)
		context = {
			'rec': data_rec,
			'type': item,
			'ids': ids,
		}
		queue.put(context)
		
	
	def get_sim(pref, liked_index_list, user_preference_list):
		pk_list = []
		pks = []
		random_items = []
		context = {}
		upl = user_preference_list.copy()
		print(upl)
		#print(pref)
		column_mapping = {'item_type': 0, 'color': 1, 'fit': 2, 'occasion': 3, 'brand': 4, 'pattern': 5, 'fabric':6, 'length': 7}
		lastkey = Item.objects.only('id').order_by('-id').first()
		#print(lastkey.id)
		firstkey = Item.objects.only('id').order_by('id').first()
		#print(firstkey.id)
		start_time1 = time.time()
		for pk in Item.objects.only('id').values('id'):
			if pk['id'] in liked_index_list:
				continue
			else:
				pks.append(pk['id'])
		#print(time.time() - start_time1)
		#print(len(pks))
		start_time2 = time.time()
		item_queue = queue.Queue()

		def retrieve_items(fk, lk, liked_index_list, item_queue):
			for i in range(fk,lk):
				if i in liked_index_list:
					continue
				random_item = Item.objects.only('item_type', 'color', 'fit', 'occasion', 'brand', 'pattern', 'fabric', 'length').filter(id=i).values_list('item_type', 'color', 'fit', 'occasion', 'brand', 'pattern', 'fabric', 'length').first()		
				random_items.append(random_item)
			item_queue.put(random_items)

		thread = Thread(target = retrieve_items, args = (int(firstkey.id), int(lastkey.id), liked_index_list, item_queue))
		thread.start()
		thread.join()
		random_items = item_queue.get()
		#print('Time for retrieving tuples')
		#print(time.time() - start_time2)
		try:
			queued_req1 = queue.Queue()
			start_time3 = time.time()
			thread1 = Thread(target = calculate_dice_coe, args = (random_items, pks, liked_index_list, upl, column_mapping, pref, queued_req1,))	
			thread1.start()	
			thread1.join()
			context = queued_req1.get()
			#print(time.time() - start_time3)
			#print(context)
			return context
		except:
			print('Exception occured')
			traceback.print_exc()
		finally:
			connection.close()

	def get_preference_list(liked_index_list, pref):
		def item_sql(liked_index_list):
			str11 = 'SELECT id,max(mycount),item_type FROM (SELECT id,item_type, COUNT(item_type) mycount FROM recommender_item where id in ('
			str12 = ','.join(map(str,liked_index_list))
			str13 = ') GROUP BY item_type)'
			q2 = str11 + str12 + str13
			count = Item.objects.raw(q2)
			return count
		def color_sql(liked_index_list):
			str11 = 'SELECT id,max(mycount),color FROM (SELECT id,color, COUNT(color) mycount FROM recommender_item where id in ('
			str12 = ','.join(map(str,liked_index_list))
			str13 = ') GROUP BY color)'
			q2 = str11 + str12 + str13
			count = Item.objects.raw(q2)
			return count
		def fit_sql(liked_index_list):
			str11 = 'SELECT id,max(mycount),fit FROM (SELECT id,fit, COUNT(fit) mycount FROM recommender_item where id in ('
			str12 = ','.join(map(str,liked_index_list))
			str13 = ') GROUP BY fit)'
			q2 = str11 + str12 + str13
			count = Item.objects.raw(q2)
			return count
		def occasion_sql(liked_index_list):
			str11 = 'SELECT id,max(mycount),occasion FROM (SELECT id,occasion, COUNT(occasion) mycount FROM recommender_item where id in ('
			str12 = ','.join(map(str,liked_index_list))
			str13 = ') GROUP BY occasion)'
			q2 = str11 + str12 + str13
			count = Item.objects.raw(q2)
			return count
		def brand_sql(liked_index_list):
			str11 = 'SELECT id,max(mycount),brand FROM (SELECT id,brand, COUNT(brand) mycount FROM recommender_item where id in ('
			str12 = ','.join(map(str,liked_index_list))
			str13 = ') GROUP BY brand)'
			q2 = str11 + str12 + str13
			count = Item.objects.raw(q2)
			return count
		def pattern_sql(liked_index_list):
			none_check = 'N/A'
			str11 = 'SELECT id,max(mycount),pattern FROM (SELECT id,pattern, COUNT(pattern) mycount FROM recommender_item where pattern is not' 
			str12 = "'"+none_check+"'"
			str13 = 'and'
			str14 = ' id in ('
			str15 = ','.join(map(str,liked_index_list))
			str16 = ') GROUP BY pattern)'
			q2 = str11 + str12 + str13 + str14 + str15 +str16
			count = Item.objects.raw(q2)

			return count
		def fabric_sql(liked_index_list):
			str11 = 'SELECT id,max(mycount),fabric FROM (SELECT id,fabric, COUNT(fabric) mycount FROM recommender_item where id in ('
			str12 = ','.join(map(str,liked_index_list))
			str13 = ') GROUP BY fabric)'
			q2 = str11 + str12 + str13
			count = Item.objects.raw(q2)
			return count
		def length_sql(liked_index_list):
			str11 = 'SELECT id,max(mycount),length FROM (SELECT id,length, COUNT(length) mycount FROM recommender_item where id in ('
			str12 = ','.join(map(str,liked_index_list))
			str13 = ') GROUP BY length)'
			q2 = str11 + str12 + str13
			count = Item.objects.raw(q2)
			return count

		item_count = item_sql(liked_index_list)
		color_count = color_sql(liked_index_list)  
		fit_count = fit_sql(liked_index_list)
		occasion_count =  occasion_sql(liked_index_list)
		brand_count = brand_sql(liked_index_list)
		pattern_count = pattern_sql(liked_index_list)
		fabric_count = fabric_sql(liked_index_list)
		length_count = length_sql(liked_index_list)
		# print(item_count)
		# print(color_count)
		# print(fit_count)
		# print(occasion_count)
		# print(brand_count) 
		# print(pattern_count)
		# print(fabric_count)
		# print(length_count)
		user_preference_list = []
		for a,b,c,d,e,f,g,h in zip(item_count, color_count, fit_count, occasion_count, brand_count, pattern_count, fabric_count, length_count):
			user_preference_list.extend([a.item_type, b.color, c.fit, d.occasion, e.brand, f.pattern, g.fabric, h.length ])
		
		return get_sim(pref, liked_index_list, user_preference_list)

	def liked_item_ids(pref):
		def liked_ids_sql():
			with connection.cursor() as cursor:
				cursor.execute('select id from recommender_item where id in (select item_id from recommender_item_likes where user_id = %s)', [request.user.id])
				row = cursor.fetchall()
				return row
		liked_index_list = liked_ids_sql()
		liked_index_list = [e for l in liked_index_list for e in l]
		#print(liked_index_list)
		if len(liked_index_list) < 10:
			messages.info(request, 'You must like atleast 10 items for us to provide accurate recommendations')
		else:
			return get_preference_list(liked_index_list, pref)

	def get_user_pref():
		if request.method == 'POST':
			pref = request.POST.get('preferences')
			pref = pref.strip()
			#print(pref)
			return liked_item_ids(pref)



	def get_preference_list_single(pref, pref_index_list):
		column_mapping = {'item_type': 0, 'color': 1, 'fit': 2, 'occasion': 3, 'brand': 4, 'pattern': 5, 'fabric':6, 'length': 7}
		#Get preference index and actual prefernce choice of user (i.e if user enters color, then pref_index = 4 and value will be the value for color in preference list)
		for key in column_mapping.keys():
			if pref in key:
				pref_index = column_mapping[key]
				pref_choice = pref_list[pref_index]
				#print(pref_index)
				#print(type(pref_choice))
				break
		#Retrieve ids of liked items
		matching_pref_list = []

		#Retrieve all items that match entered preference
		user_pref = pref
		#print(type(request.user.id))
		user_pref_list = []
	
		str1 = 'select id FROM recommender_item WHERE id in (select item_id from recommender_item_likes where user_id = '
		str2 = str(request.user.id)
		str3 = ') and '
		str4 = user_pref
		str5 = ' = '
		str6 = "'"+pref_choice+"'"
		q = str1 + str2+ str3 + str4 + str5 + str6
		#print(q)
		user_items = Item.objects.raw(q)
		for item in user_items:
			user_pref_list.append(item.id)
		#print(user_pref_list)
		item_type_new_count = []
		item_type_new = []
		for ids in user_pref_list:
			item_type_new_count.append(Item.objects.only('item_type', 'color', 'fit', 'occasion', 'brand', 'pattern', 'fabric', 'length').filter(id = ids).values_list('item_type', 'color', 'fit', 'occasion', 'brand', 'pattern', 'fabric', 'length'))
		
		#print(item_type_new_count)
		for item in item_type_new_count:
			item_type_new.append(item[0])
	
	return render(request, template_name, context = get_user_pref())
		
def ItemLikeToggleView(request):
	#item = get_object_or_404(Item, id = request.POST.get('item_id'))
	item = get_object_or_404(Item, id = request.POST.get('id'))
	is_liked = False
	if item.likes.filter(id = request.user.id).exists():
		item.likes.remove(request.user)
		is_liked = False
	else:
		item.likes.add(request.user)
		is_liked = True
	context = {
		'item': item,
		'is_liked': is_liked,
		'total_likes': item.get_total_likes(),
	}
	if request.is_ajax():
		html = render_to_string('recommender/like_section.html', context, request = request)
		return JsonResponse({'form': html})

def ItemLikeAllToggleView(request):
	item = get_object_or_404(Item, id = request.POST.get('id'))
	is_liked = False
	if item.likes.filter(id = request.user.id).exists():
		item.likes.remove(request.user)
		is_liked = False
	else:
		item.likes.add(request.user)
		is_liked = True
	context = {
		'item': item,
		'is_liked':is_liked,
		'total_likes': item.get_total_likes(),
	}
	if request.is_ajax():
		html = render_to_string('recommender/like_all_section.html', context, request = request)
		return JsonResponse({'form': html})

def ItemsLikedToggleView(request):
	item = get_object_or_404(Item, id = request.POST.get('id'))
	print(item.get_total_likes())
	is_liked = False
	if item.likes.filter(id = request.user.id).exists():
		item.likes.remove(request.user)
		is_liked = False
	else:
		item.likes.add(request.user)
		is_liked = True
	context = {
		'item': item,
		'is_liked':is_liked,
		'total_likes': item.get_total_likes(),
	}
	if request.is_ajax():
		html = render_to_string('recommender/all_liked_toggle_section.html', context, request = request)
		return JsonResponse({'form': html})
	

def AllLikedItemsView(request, pk):
	paginate_by = 10
	def liked_item_id():
		with connection.cursor() as cursor:
			cursor.execute('select id, image_URL from recommender_item where id in (select item_id from recommender_item_likes where user_id = %s)', [request.user.id])
			row = cursor.fetchall()
			return row
	template_name = 'recommender/all_liked.html'
	item = liked_item_id()
	ids = []
	urls = []
	for i in item:
		ids.append(i[0])
		urls.append(i[1])
	likes = zip(ids, urls)
	context = {
		'is_liked': True,
		'liked_active_page': 'active',
		'likes': likes,
	}
	return render(request, template_name, context = context)

class ItemsAllView(generic.ListView):
	template_name = 'recommender/all_items.html'
	paginate_by = 20
	def get_queryset(self):
		return Item.objects.all().order_by('likes')[:50]

def ItemDetailView(request, pk):
	template_name = 'recommender/item_detail.html'
	paginate_by = 10
	item = get_object_or_404(Item, pk = pk)
	is_liked = False
	if item.likes.filter(id = request.user.id).exists():
		is_liked = True
	context = {

		'item': item,
		'is_liked': is_liked,
		'total_likes': item.get_total_likes(),
	}
	return render(request, template_name, context = context)

def ChartView(request):
	def liked_ids_sql():
		with connection.cursor() as cursor:
			cursor.execute('select id from recommender_item where id in (select item_id from recommender_item_likes where user_id = %s)', [request.user.id])
			row = cursor.fetchall()
			return row
	liked_index_list = liked_ids_sql()
	liked_index_list = [e for l in liked_index_list for e in l]
	
	item_type_count = Item.objects.filter(id__in = liked_index_list).values('item_type').annotate(total = Count('item_type')).order_by('-total')

	#print(item_type_count)
	item_type_data = []
	item_type_count_data = []
	for i in item_type_count:
		item_type_data.append(i['item_type'])
		item_type_count_data.append(i['total'])
	# print(item_type_data)
	# print(item_type_count_data)
	all_liked_count = []

	for i in Item.objects.raw('select id,item_id from recommender_item_likes'):
		all_liked_count.append(i.item_id)
	
	all_liked_count = tuple(map(int,all_liked_count))
	#print(all_liked_count)
	all_liked_items = []
	all_liked_items_count = []
	
	all_liked = Item.objects.filter(id__in = all_liked_count).values('item_type').annotate(total = Count('item_type')).order_by('-total')
	for i in all_liked:
		all_liked_items.append(i['item_type'])
		all_liked_items_count.append(i['total'])
	#print(all_liked_items)
	my_liked_color_list = []
	my_liked_color_count = []
	my_liked_color = Item.objects.filter(id__in = liked_index_list).values('color').annotate(total = Count('item_type')).order_by('-total')
	for i in my_liked_color:
		my_liked_color_list.append(i['color'])
		my_liked_color_count.append(i['total'])

	#print(my_liked_color_list)
	
	chart = {
		'stats_active_page': 'active',
		'item_type_data0': item_type_data[0],
		'item_type_data1': item_type_data[1],
		'item_type_data2': item_type_data[2],
		'item_type_data3': item_type_data[3],
		'item_type_data4': item_type_data[4],
		'item_type_count_data0': item_type_count_data[0],
		'item_type_count_data1': item_type_count_data[1],
		'item_type_count_data2': item_type_count_data[2],
		'item_type_count_data3': item_type_count_data[3],
		'item_type_count_data4': item_type_count_data[4],
		'all': all_liked_items[0],
		'all1': all_liked_items[1],
		'all2': all_liked_items[2],
		'all3': all_liked_items[3],
		'all4': all_liked_items[4],
		'all_count': all_liked_items_count[0],
		'all_count1': all_liked_items_count[1],
		'all_count2': all_liked_items_count[2],
		'all_count3': all_liked_items_count[3],
		'all_count4': all_liked_items_count[4],
		'my_color': my_liked_color_list[0],
		'my_color1': my_liked_color_list[1],
		'my_color2': my_liked_color_list[2],
		'my_color_count': my_liked_color_count[0],
		'my_color_count1': my_liked_color_count[1],
		'my_color_count2': my_liked_color_count[2]
		


		
	}
	
	return render(request, 'recommender/stats_chart.html', context = chart)






