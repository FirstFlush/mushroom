from django.contrib import admin
from .models import Strain, Syringe, SpawnBag, Monotub, Flush, Bowl, Recipe, RecipeType, Crop, Ingredient, MonotubSize, ContamType, Contam, Batch



class BowlAdmin(admin.ModelAdmin):

    list_display = [
        'description',
        'weight_grams',
        ]




class StrainAdmin(admin.ModelAdmin):

    list_display = ['name']
    search_fields = ['name']


class CropAdmin(admin.ModelAdmin):

    list_display = [
        'strain_id',
        'yield_dry',
        # 'start_date',
    ]



class RecipeTypeAdmin(admin.ModelAdmin):

    list_display = [
        'recipe_type',
    ]



class RecipeAdmin(admin.ModelAdmin):

    list_display = [
        'name',
        'type_id',
        'url',
        # 'type_id',
    ]



class SyringeAdmin(admin.ModelAdmin):

    list_display = [
        'strain_id',
        'cost',
        'date_purchased',
    ]


class SpawnBagAdmin(admin.ModelAdmin):

    list_display = [
        'syringe_id',
        'volume',
        'date_spawned',
        'is_contaminated',
    ]


class MonotubSizeAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'length_inch',
        'width_inch',
        'height_inch',
        # 'notes',
    ]



class MonotubAdmin(admin.ModelAdmin):

    list_display = [
        'bag_id',
        'recipe_id',
        'volume_spawn',
        'volume_bulk',
        'is_cased',
        'monotub_size_id',
        'date_fruited',
        'date_created',
        'is_contaminated',
    ]


class FlushAdmin(admin.ModelAdmin):

    list_display = [
        'monotub_id',
        'yield_wet',
        'is_dunked',
        'partial_flush',
        'date_harvested',
    ]

    list_filter = [
        'monotub_id__bag_id__syringe_id__strain_id__name',
    ]

    search_fields = [
        'monotub_id__bag_id__syringe_id__strain_id__name',
    ]


class IngredientAdmin(admin.ModelAdmin):

    list_display = [
        'name',
        'volume_per_g',
        'weight_per_g',
    ]



class ContamTypeAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'kingdom',
        'cause',
        'prevention',
    ]


class ContamAdmin(admin.ModelAdmin):

    list_display = [
        # 'kingdom',
        # 'type_guess_mtm',
        'appearance',
        'tub_id',
        'bag_id',
        'lc_jar_id',
        'desc_short',
    ]


class BatchAdmin(admin.ModelAdmin):

    list_display = [
        'notes',
    ]


admin.site.register(Bowl, BowlAdmin)
admin.site.register(Strain, StrainAdmin)
admin.site.register(Crop, CropAdmin)
admin.site.register(RecipeType, RecipeTypeAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Syringe, SyringeAdmin)
admin.site.register(SpawnBag, SpawnBagAdmin)
admin.site.register(Monotub, MonotubAdmin)
admin.site.register(Flush, FlushAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(MonotubSize, MonotubSizeAdmin)
admin.site.register(ContamType, ContamTypeAdmin)
admin.site.register(Contam, ContamAdmin)
admin.site.register(Batch, BatchAdmin)
