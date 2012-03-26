from django import forms
from django.contrib.auth.forms import UserCreationForm

from onlyinpgh.accounts.models import UserProfile


class RegistrationForm(UserCreationForm):
    '''
    Overrides UserCreationForm to include email address.
    '''
    email = forms.EmailField(label="Email address", required=True)

    class Meta(UserCreationForm.Meta):
        fields = ("username", "email",)

    def save(self, commit=True):
        '''
        Adds email to saved user.
        '''
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user', 'points')
        widgets = {'birth_year': forms.TextInput(attrs={'maxlength': '4'})}

# BROKEN: PROBABLY NEVER FIX
# class EmailOnlyRegistrationForm(UserCreationForm):
#     """
#     Registration form that autogenerates a username from an email
#     address. Useful for presenting signup options to a user who has no
#     need to know his/her username (e.g. business-only accounts).
#     """
#     username = forms.CharField(widget=forms.widgets.HiddenInput(), required=False)
#     email = forms.EmailField(label="Email address", required=True)

#     class Meta(UserCreationForm.Meta):
#         fields = ("email",)

#     def clean_username(self):
#         '''
#         Autogenerates a username.
#         '''
#         if 'email' not in self.data:
#             forms.ValidationError("Username cannot be created without email address")
#         username = basename = self.data['email'].split('@')[0][:30]
#         suffix_int = 1
#         while True:
#             try:
#                 User.objects.get(username=username)
#             except User.DoesNotExist:
#                 return username
#             suffix = str(suffix_int)
#             while len(basename + suffix) > 30:
#                 basename = basename[:-1]
#             username = basename + suffix
#             suffix_int += 1

#     def clean_email(self):
#         email = self.cleaned_data["email"]
#         try:
#             User.objects.get(email=email)
#         except User.DoesNotExist:
#             return email
#         raise forms.ValidationError("A user with that email address already exists.")

#     def save(self, commit=True):
#         '''
#         Adds email to saved user.
#         '''
#         user = super(EmailOnlyRegistrationForm, self).save(commit=False)
#         user.username = self.cleaned_data['username']   # doesn't seem to work in parent save
#         user.email = self.cleaned_data['email']
#         if commit:
#             user.save()
#         return user
