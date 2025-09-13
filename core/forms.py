from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Skill, SkillPost

class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["bio"]

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ["name", "category"]

class SkillPostForm(forms.ModelForm):
    class Meta:
        model = SkillPost
        fields = ["skill", "description", "kind"]

    def save(self, user=None, commit=True):
        instance = super().save(commit=False)
        if user:
            instance.user = user
        if commit:
            instance.save()
        return instance
