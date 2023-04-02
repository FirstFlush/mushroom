from typing import Container
from unicodedata import name
from django.db import models
from django.db.models import Sum


class Tek(models.Model):

    name    = models.CharField(max_length=255)
    url     = models.URLField(max_length=255)
    notes   = models.TextField(max_length=2048)

    def __str__(self):
        return self.name


class Bowl(models.Model):

    description     = models.TextField(max_length=512)
    weight_grams    = models.DecimalField(decimal_places=1, max_digits=16)

    def __str__(self):
        return f"{self.description} --- {self.weight_grams} g"


    def get_weight(self, total_weight):
        '''
        Subtract the bowl weight from the overall weight of the bowl+product
        '''
        return total_weight - self.weight_grams



class Strain(models.Model):

    name = models.CharField(max_length=64,unique=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name



class Ingredient(models.Model):

    name            = models.CharField(max_length=255, unique=True)
    volume_per_g    = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    weight_per_g    = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name



class RecipeType(models.Model):
    recipe_type = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.recipe_type



class Recipe(models.Model):

    name            = models.CharField(max_length=64)
    type_id         = models.ForeignKey(to=RecipeType, on_delete=models.CASCADE, blank=True, null=True)
    ingredient_mtm  = models.ManyToManyField(to=Ingredient, blank=True)
    recipe          = models.TextField()
    url             = models.URLField(max_length=255, blank=True, null=True)
    notes           = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.type_id}"



class Batch(models.Model):

    notes       = models.TextField(blank=True, null=True)

    def notes_short(self):
        return f"{self.notes[:20]}..."



class Crop(models.Model):

    # thing = models.TextField(blank=True, null=True)
    strain_id       = models.ForeignKey(to=Strain, on_delete=models.CASCADE)
    tek_mtm         = models.ManyToManyField(to=Tek, blank=True)
    yield_dry       = models.DecimalField(decimal_places=2, max_digits=16, default=0)
    date_created    = models.DateField()
    notes           = models.TextField(null=True, blank=True)


    def __str__(self):
        return f"{self.strain_id.name} - {self.date_created}"


    def flushes(self):
        '''Returns a queryset of all associated flushes.'''
        flushes = Flush.objects.filter(monotub_id__bag_id__syringe_id__crop_id=self.id)
        return flushes


    def start_date(self):
        '''Returns the date of the crop's first bag/jar injection.'''
        print(self.strain_id)
        first_injection = SpawnBag.objects.filter(syringe_id__crop_id=self.id).order_by('date_spawned').first()
        return first_injection.date_spawned


    def end_date(self):
        '''Returns the date of the crop's final flush.'''
        last_flush = self.flushes().order_by('date_harvested').last()
        return last_flush.date_harvested


    def get_yield_estimate(self):
        '''
        Sum of all yield_wet values in the corresponding Flush set. 
        Sum is then divided by 10 since wet shrooms lose 90% of their 
        weight when dried.
        '''
        # flushes = Flush.objects.filter(monotub_id__bag_id__syringe_id__harvest_id=self.id)
        yield_est = self.flushes().aggregate(Sum('yield_wet')).get('yield_wet__sum') / 10

        return yield_est


    def actual_vs_estimate(self):
        '''
        Return ratio of actual dry harvest quantity to the amount estimated when the flushes were measured wet.
        '''
        return self.yield_dry / self.get_yield_estimate()



class LiquidCultureJar(models.Model):

    strain_id       = models.ForeignKey(to=Strain, on_delete=models.CASCADE)
    recipe_id       = models.ForeignKey(to=Recipe, on_delete=models.CASCADE)
    label           = models.CharField(max_length=255)
    date_created    = models.DateField()



class Syringe(models.Model):

    strain_id       = models.ForeignKey(to=Strain, on_delete=models.CASCADE)
    crop_id         = models.ForeignKey(to=Crop, on_delete=models.SET_NULL, blank=True, null=True)
    cost            = models.DecimalField(max_digits=8, decimal_places=2)
    date_purchased  = models.DateField()

    def __str__(self):
        return f"{self.strain_id} - ${self.cost}"



class SpawnBag(models.Model):

    CONTAINER_CHOICES = (
        ('bag','Bag'),
        ('jar','Jar'),
    )

    syringe_id      = models.ForeignKey(to=Syringe, on_delete=models.CASCADE)
    recipe_id       = models.ForeignKey(to=Recipe, on_delete=models.CASCADE, null=True)
    container       = models.CharField(max_length=255, choices=CONTAINER_CHOICES, default='bag')
    volume          = models.DecimalField(decimal_places=2, max_digits=16)
    is_contaminated = models.BooleanField(default=False)
    date_spawned    = models.DateField()
    notes           = models.TextField(null=True, blank=True)

    def __str__(self):

        contam = lambda x : ' (CONTAM)' if x == True else ''
        return f"{self.syringe_id.strain_id} - {self.volume}L - {self.date_spawned}{contam(self.is_contaminated)}"


class MonotubSize(models.Model):
    '''Ikea Samla tote used as default'''

    name            = models.CharField(max_length=255)
    length_inch     = models.FloatField(max_length=10)
    width_inch      = models.FloatField(max_length=10)
    height_inch     = models.FloatField(max_length=10)
    sub_depth_inch  = models.FloatField(max_length=10)
    notes           = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.name}({self.length_inch} * {self.width_inch} * {self.height_inch})'

    def get_cm(self, value_inches):
        '''Return the a length, width, or height value as cm instead if inch.'''
        return round(value_inches * 2.54, 2)

    def get_volumes(self, ratio=tuple):
        '''
        Pass in ratio of spawn:bulk as a tuple and it will 
        give you the total volume (L) you will need of each.
        '''
        substrate = {}
        spawn_ratio = ratio[0]
        bulk_ratio  = ratio[1]
        volume_qb_inch = self.length_inch * self.width_inch * self.sub_depth_inch

        spawn_qb_inch = (spawn_ratio / (bulk_ratio + 1)) * volume_qb_inch
        bulk_qb_inch = spawn_qb_inch * bulk_ratio

        substrate['spawn'] = round(spawn_qb_inch / 61.024, 2)
        substrate['bulk'] = round(bulk_qb_inch / 61.024, 2)
        substrate['total'] = round(volume_qb_inch / 61.024, 2)

        return substrate


class Monotub(models.Model):
    '''volume attributes are in liters (L)'''

    bag_id          = models.ForeignKey(to=SpawnBag, on_delete=models.CASCADE)
    recipe_id       = models.ForeignKey(to=Recipe, on_delete=models.CASCADE, null=True)
    monotub_size_id = models.ForeignKey(to=MonotubSize, on_delete=models.CASCADE, null=True, default=0)
    volume_spawn    = models.DecimalField(decimal_places=2, max_digits=16)
    volume_bulk     = models.DecimalField(decimal_places=2, max_digits=16)
    sub_depth_inch  = models.FloatField(max_length=8, default=3.0)
    is_cased        = models.BooleanField(default=False)
    tub_code        = models.CharField(max_length=8, null=True, blank=True)
    is_contaminated = models.BooleanField(default=False)
    date_fruited    = models.DateField(blank=True,null=True)
    date_created    = models.DateField()
    notes           = models.TextField(null=True, blank=True)


    def volume_total(self):
        '''Returns total volume of substrate in the monotub'''
        return self.volume_spawn + self.volume_bulk


    def substrate_ratio(self):
        '''returns ratio of grain spawn to bulk substrate'''
        return self.volume_bulk / self.volume_spawn


    def __str__(self):
        contam = lambda x : ' (CONTAM)' if x == True else ''
        code = lambda x : f"({self.tub_code})" if x != None else ''

        return f"{self.bag_id.syringe_id.strain_id.name} {code(self.tub_code)} {self.date_created} {contam(self.is_contaminated)}" 
        # return f"{self.bag_id.syringe_id.strain_id.name} #{self.id} {self.date_created} - {self.date_fruited}{contam(self.is_contaminated)}" 



class FlushManager(models.Manager):
    '''not in use anywhere'''

    def flush_order(self, monotub):

        qs = super(FlushManager, self).filter(monotub_id=monotub).order_by('date_harvested')
        # get a number for each flush object based on date? i dunno
        return qs



class Flush(models.Model):
    '''yield_wet is in grams (g)'''

    monotub_id      = models.ForeignKey(to=Monotub, on_delete=models.CASCADE)
    yield_wet       = models.DecimalField(decimal_places=2, max_digits=16)
    partial_flush   = models.BooleanField(default=False)
    is_dunked       = models.BooleanField(default=True)
    date_harvested  = models.DateField()
    notes           = models.TextField(null=True, blank=True)

    objects = FlushManager()

    class Meta:
        verbose_name_plural = 'Flushes'


    def __str__(self):

        if self.yield_wet % 1 == 0:
            yw = int(self.yield_wet)
        else:
            yw = self.yield_wet
        partial = lambda x : '(partial)' if x == True else ''
        return f"{self.monotub_id.bag_id.syringe_id.strain_id.name} #{self.monotub_id.id} {yw}g {partial(self.partial_flush)}"



class ContamType(models.Model):

    KINGDOM_CHOICES = (
        ('fungus','Fungus'),
        ('animal','Animal'),
        ('bacteria','Bacteria'),
    )

    name = models.CharField(max_length=255, unique=True)
    kingdom = models.CharField(max_length=255, choices=KINGDOM_CHOICES)
    cause = models.TextField(null=True, blank=True)
    prevention = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name



class ContamManager(models.Manager):

    def get_all_type(self, type):
        '''
        Gets all contam instances of the following model options:
        'monotub',
        'bag',
        'lc_jar',
        '''
        if type == 'monotub':
            return Contam.objects.filter(tub_id__isnull=False)
        elif type == 'bag':
            return Contam.objects.filter(bag_id__isnull=False)
        elif type =='lc_jar':
            return Contam.objects.filter(lc_jar_id__isnull=False)
        else:
            return Contam.objects.all()


class Contam(models.Model):

    VISUAL_CHOICES = (
        ('green','Green'),
        ('pink','Pink'),
        ('black','Black'),
        ('white','White'),
        ('grey','Grey'),
        ('wet','Wet'),
        ('gnats','Gnats'),
        ('mycogone','Mycogone'),
        ('cobweb','Cobweb'),
    )

    type_guess_mtm  = models.ManyToManyField(to=ContamType)
    bag_id          = models.ForeignKey(to=SpawnBag,on_delete=models.CASCADE,null=True,blank=True)
    tub_id          = models.ForeignKey(to=Monotub,on_delete=models.CASCADE,null=True,blank=True)
    lc_jar_id       = models.ForeignKey(to=LiquidCultureJar,on_delete=models.CASCADE,null=True,blank=True)
    appearance      = models.CharField(max_length=255,choices=VISUAL_CHOICES)
    contam_img      = models.ImageField(upload_to='photos/contam', null=True, blank=True)
    description     = models.TextField(null=True, blank=True)

    objects = ContamManager()


    def __str__(self):
        
        if self.bag_id:
            thing = 'Bag'
        elif self.tub_id:
            thing = 'Monotub'
        elif self.lc_jar_id:
            thing = "LC Jar"
        else:
            thing = '-ERROR-'

        return f"{thing} - {self.appearance} - {self.desc_short(letter_count=20)}"


    def desc_short(self, letter_count=30):
        desc = f"{self.description[:letter_count]}..."
        return desc

