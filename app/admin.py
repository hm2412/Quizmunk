from django.contrib import admin
# Register models for Django admin interface here
from app.models.user import User
from app.models.classroom import Classroom, ClassroomStudent, ClassroomInvitation

admin.site.register(User)
admin.site.register(Classroom)
admin.site.register(ClassroomStudent)
admin.site.register(ClassroomInvitation)
