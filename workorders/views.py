from django.shortcuts import render
from django.http import HttpResponse
import json

from .models import Category, Product

def index(request):	
	return HttpResponse("Hello, World! You're at the work orders index.")

def new(request):
	# Fetch Category
	category_list = Category.objects.values('id', 'name')

	# Fetch products
	product_list = Product.objects.values('id','name','category_id','dimensions__id','dimensions__name','dimensions__styles__name','dimensions__styles__id')

	context = {
		'category': json.dumps(list(category_list)),
		'product': json.dumps(list(product_list)),
	}
	return render(request, 'workorders/base_workorder_form.html', context)