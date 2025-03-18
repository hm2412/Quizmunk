from django.contrib import admin
# Register models for Django admin interface here
from app.models.user import User
from app.models.classroom import Classroom, ClassroomStudent, ClassroomInvitation
from app.models.room import Room

admin.site.register(User)
admin.site.register(Classroom)
admin.site.register(ClassroomStudent)
admin.site.register(ClassroomInvitation)
admin.site.register(Room)