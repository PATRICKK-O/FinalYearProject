from django.contrib import admin
from .models import Material, MaterialType

class MaterialTypeAdmin(admin.ModelAdmin):
  list_display = ('id', 'type_name')

class MaterialAdmin(admin.ModelAdmin):
  list_display = ('subject', 'level', 'description', 'keywords')
  filter_horizontal = ('material_types',) # enables checkboxes for ManyToManyField
  
admin.site.register(Material, MaterialAdmin)
admin.site.register(MaterialType, MaterialTypeAdmin)  
