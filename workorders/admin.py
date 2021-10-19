from django.contrib import admin

# Add models to make them editable in admin site
from .models import Category, Product, Dimension, Style, Package, Department, User, Asset, WorkOrder

class ProductInline(admin.TabularInline):
	model = WorkOrder.products.through
	extra = 1

class ProductAdmin(admin.ModelAdmin):
	inlines = [
		ProductInline,
	]
	exclude = ('products',)

class WorkOrderAdmin(admin.ModelAdmin):
	inlines = [
		ProductInline,
	]

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Dimension)
admin.site.register(Style)
admin.site.register(Package)
admin.site.register(Department)
admin.site.register(User)
admin.site.register(Asset)
admin.site.register(WorkOrder, WorkOrderAdmin)