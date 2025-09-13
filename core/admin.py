from django.contrib import admin
from .models import Profile, Skill, SkillPost, MatchRequest, Session

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "bio", "credits")

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    search_fields = ("name", "category")

@admin.register(SkillPost)
class SkillPostAdmin(admin.ModelAdmin):
    list_display = ("user", "skill", "kind", "created_at")
    list_filter = ("kind", "created_at")
    search_fields = ("skill__name", "description")

@admin.register(MatchRequest)
class MatchRequestAdmin(admin.ModelAdmin):
    list_display = ("from_user", "to_user", "skill", "status", "created_at")
    list_filter = ("status",)

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("teacher", "learner", "skill", "status", "created_at")
    list_filter = ("status",)
