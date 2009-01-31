from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from datetime import date


class ParamProfile(models.Model):
    profile_id = models.AutoField(primary_key=True)
    display_order = models.IntegerField()
    name = models.CharField(max_length=300, unique=True, db_column='profile_name')
    
    def __unicode__(self):
        return self.name
    class Meta:
        db_table = u'rs_param_profiles'
        verbose_name = 'Profile'

class DataUser(models.Model):
    user_id = models.AutoField(primary_key=True)
    last_name = models.CharField(max_length=150, blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    login = models.CharField(unique=True, max_length=60, blank=True)
    profile = models.ForeignKey(ParamProfile, db_column='profile_id')
    email = models.CharField(max_length=240, blank=True)
    password = models.CharField(max_length=60, blank=True)
    locked = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    remarks = models.CharField(max_length=765, blank=True)
    
    def __unicode__(self):
        return self.login
    class Meta:
        db_table = u'rs_data_users'
        verbose_name = 'openbookings user'

def create_datauser(sender, instance=None, **kwargs):
    if instance is None:
        return
    defprofile = ParamProfile.objects.get(name='User')
    datauser, created = DataUser.objects.get_or_create(
                            login=instance.username,defaults={
                                'password':instance.password[:20],
                                'profile':defprofile,
                                'remarks':'django auth auto created'
                            })
    if not created:
        datauser.last_name=instance.last_name
        datauser.first_name=instance.first_name
        datauser.email=instance.email
        datauser.locked=not instance.is_active
        datauser.save()

post_save.connect(create_datauser, sender=User)

class ParamFamily(models.Model):
    family_id = models.AutoField(primary_key=True)
    sort_order = models.IntegerField()
    name = models.CharField(max_length=150, db_column='family_name')
    
    def __unicode__(self):
        return self.name
    class Meta:
        db_table = u'rs_param_families'
        verbose_name = 'Family'
        verbose_name_plural = 'Families'

class Data(models.Model):
    object_id = models.AutoField(primary_key=True)
    rand_code = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=150, db_column='object_name')
    family = models.ForeignKey(ParamFamily)
    manager = models.ForeignKey(DataUser)
    misc_info = models.CharField(max_length=765, blank=True)
    
    checked = None
    
    def color(self):
        try:
            return Param.objects.get(name=u'color-%s'%self.name).value
        except Exception:
            return "white"
    
    def span_color(self, width=1, force_span=False, day=None):
        if day:
            av = True
            for booking in self.databooking_set.all():
                if not booking.day_available(day):
                    av = False
                    break
            if av: return ""
        
        color = self.color()
        if color == "white" and not force_span:
            return "" 
        nbsp = '&nbsp;' * width
        return '<span style="background:%s;">%s</span>' % (color, nbsp)
    span_color.allow_tags = True
    
    def __unicode__(self):
        return self.name
    class Meta:
        db_table = u'rs_data_objects'
        verbose_name = 'Bookable object'

class DataBooking(models.Model):
    book_id = models.AutoField(primary_key=True)
    rand_code = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(db_column='book_date')
    data = models.ForeignKey(Data, db_column='object_id', verbose_name='object')
    user = models.ForeignKey(DataUser)
    start = models.DateTimeField(db_column='book_start')
    end = models.DateTimeField(db_column='book_end')
    validated = models.BooleanField()
    misc_info = models.CharField(max_length=765)
    
    def day_available2(self, year, month, day):
        return self.day_available2(date(year, month, day))
    
    def day_available(self, wdate):
        if wdate < self.start.date(): return True
        if wdate > self.end.date(): return True
        return False

    def __unicode__(self):
        return self.data.name
    class Meta:
        db_table = u'rs_data_bookings'
        verbose_name = 'Booking'

class Param(models.Model):
    name = models.CharField(max_length=75, primary_key=True, db_column='param_name')
    value = models.CharField(max_length=75, db_column='param_value')
    
    def value_or_color(self):
        if self.name.startswith('color-') or self.value.startswith('#'):
            color = self.value
            return '<span style="background:%s;">&nbsp;&nbsp;</span>' % color
        else:
            return self.value
    value_or_color.allow_tags = True
    
    def __unicode__(self):
        return self.name
    class Meta:
        db_table = u'rs_param'
        verbose_name = 'Parameter'

def create_data_color(sender, instance=None, **kwargs):
    if instance is None:
        return
    import random
    pcolors = list(Param.objects.filter(name__startswith='color-name:'))
    color = random.choice(pcolors)
    Param.objects.get_or_create(name='color-%s' % instance.name,
                                defaults={'value':color.value})
    
post_save.connect(create_data_color, sender=Data)


class ParamLang(models.Model):
    lang_id = models.AutoField(primary_key=True)
    english = models.CharField(max_length=765, blank=True)
    french = models.CharField(max_length=765, blank=True)
    german = models.CharField(max_length=765, blank=True)
    norwegian = models.CharField(max_length=765, blank=True)
    
    def __unicode__(self):
        return self.english
    class Meta:
        db_table = u'rs_param_lang'
        verbose_name = 'Language parameter'
