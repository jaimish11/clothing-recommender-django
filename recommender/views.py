from django.shortcuts import render, get_object_or_404, redirect
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

def index(request):
	random_items = Item.objects.order_by('?').only('image_URL')[:21]
	context = {

		'random_items': random_items,
	}
	return render(request, 'index.html', context)
def RecommendedListView(request):
	model = Item
	template_name = 'recommender/recommended.html'
	paginate_by = 10

	def calculate_dice_coe(random_items, pks, liked_index_list, upl, column_mapping, pref, queue):
		desc_coe_list = []
		dice_coe = defaultdict(int)
		top_val_1 = []
		for i,pk in zip(range(len(random_items)),pks):
				if pk in liked_index_list:
					continue
				#random_item = Item.objects.only('item_type', 'color', 'fit', 'occasion', 'brand', 'pattern', 'fabric', 'length').filter(id=i).exclude(id__in=liked_index_list).values_list('item_type', 'color', 'fit', 'occasion', 'brand', 'pattern', 'fabric', 'length').first()
				#print(random_items[i])
				#print(upl)
				#print(pk)
				#print('------')
				#random_item = ','.join(map(str,random_item))
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
				# print(top)
				# print(bottom)
				# print(top/bottom)
				# print(round((2*top)/bottom,3))
				
				dice_coe[str(pk)] = round((2*top)/bottom,3)
				top_val_1.clear()
				#print(dice_coe)

		desc_coe_dict = sorted(dice_coe, key = dice_coe.get, reverse = True)
		for value in desc_coe_dict:
			#print(dice_coe[value])
			#print(value)
			desc_coe_list.append(value)

		#print(desc_coe_list[:11])
		context = {
			'desc_coe_list': desc_coe_list[:11]
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
		print(lastkey.id)
		firstkey = Item.objects.only('id').order_by('id').first()
		print(firstkey.id)
		start_time1 = time.time()
		for pk in Item.objects.only('id').values('id'):
			if pk['id'] in liked_index_list:
				continue
			else:
				pks.append(pk['id'])
		print(time.time() - start_time1)
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
		print('Time for retrieving tuples')
		print(time.time() - start_time2)
		try:
			queued_req1 = queue.Queue()
			#queued_req2 = queue.Queue()
			# queued_req3 = queue.Queue()
			# queued_req4 = queue.Queue()
			# queued_req5 = queue.Queue()
			# queued_req6 = queue.Queue()
			# queued_req7 = queue.Queue()
			# queued_req8 = queue.Queue()
			
			start_time3 = time.time()
			thread1 = Thread(target = calculate_dice_coe, args = (random_items, pks, liked_index_list, upl, column_mapping, pref, queued_req1,))
			
			#thread2 = Thread(target = calculate_dice_coe, args = (random_items[201:401], pks[201:401], liked_index_list, upl, column_mapping, pref, queued_req2,))
			
			# thread3 = Thread(target = calculate_dice_coe, args = (random_items[401:601], pks[401:601], liked_index_list, upl, column_mapping, pref, queued_req3,))
			
			# thread4 = Thread(target = calculate_dice_coe, args = (random_items[601:801], pks[601:801], liked_index_list, upl, column_mapping, pref, queued_req4,))
			
			# thread5 = Thread(target = calculate_dice_coe, args = (random_items[801:1001], pks[801:1001], liked_index_list, upl, column_mapping, pref, queued_req5,))
			
			# thread6 = Thread(target = calculate_dice_coe, args = (random_items[1001:1201], pks[1001:1201], liked_index_list, upl, column_mapping, pref, queued_req6,))
			
			# thread7 = Thread(target = calculate_dice_coe, args = (random_items[1201:1401], pks[1201:1401], liked_index_list, upl, column_mapping, pref, queued_req7,))
			
			# thread8 = Thread(target = calculate_dice_coe, args = (random_items[1401:len(random_items)], pks[1401:len(random_items)], liked_index_list, upl, column_mapping, pref, queued_req8,))
			
			
			thread1.start()
			#thread2.start()
			# thread3.start()
			# thread4.start()
			# thread5.start()
			# thread6.start()
			# thread7.start()
			# thread8.start()
			thread1.join()
			#thread2.join()
			# thread3.join()
			# thread4.join()
			# thread5.join()
			# thread6.join()
			# thread7.join()
			# thread8.join()
			


			context = queued_req1.get()
			
			#context['2'] = queued_req1.get()
			# context['3'] = queued_req3.get()
			# context['4'] = queued_req4.get()
			# context['5'] = queued_req5.get()
			# context['6'] = queued_req6.get()
			# context['7'] = queued_req7.get()
			# context['8'] = queued_req8.get()
			print(time.time() - start_time3)
			print(context)
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

		#print(item_count)
		user_preference_list = []
		for a,b,c,d,e,f,g,h in zip(item_count, color_count, fit_count, occasion_count, brand_count, pattern_count, fabric_count, length_count):
			user_preference_list.extend([a.item_type, b.color, c.fit, d.occasion, e.brand, f.pattern, g.fabric, h.length ])
		#print(user_preference_list)
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
		return get_preference_list(liked_index_list, pref)

	def get_user_pref():
		if request.method == 'POST':
			pref = request.POST.get('preference')
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
	
		str1 = 'select id FROM recommender_item WHERE id in (select item_id from recommender_item_likes where user_id ='
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
		

	'''context = {
		'pref' : pref,
		'item_type_count': item_type_count,
		'color_count': color_count,
		'fit_count': fit_count,
		'occasion_count': occasion_count,
		'brand_count': brand_count,
		'pattern_count': pattern_count,
		'fabric_count': fabric_count,
		'length_count': length_count,
	}'''
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

def ItemLikeAllToggleView(request, pk):
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
	

def AllLikedItemsView(request, pk):
	def liked_item_id():
		with connection.cursor() as cursor:
			cursor.execute('select image_URL from recommender_item where id in (select item_id from recommender_item_likes where user_id = %s)', [request.user.id])
			row = cursor.fetchall()
			return row
	template_name = 'recommender/all_liked.html'
	item = liked_item_id()
	#print(item)
	context = {
		'likes': item,
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


