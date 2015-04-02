from django.contrib import admin
from mealmatcher_app.models import UserProfile, Meal

class UserAdmin(admin.ModelAdmin):
	list_display = ('user',) 
class MealAdmin(admin.ModelAdmin):
	list_display = ('date', 'time', 'location', 'attire1', 'attire2',) # formatting
admin.site.register(UserProfile, UserAdmin)
admin.site.register(Meal, MealAdmin)

# current admin account:
# username: admin