from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from onlyinpgh.accounts.models import UserProfile, BetaMember


class RegistrationForm(UserCreationForm):
    '''
    Overrides UserCreationForm to include email address.
    Also disallows @ symbols in usernames.
    '''
    username = forms.RegexField(label="Username", max_length=30, regex=r'^[\w.+-]+$',
        help_text="Required. 30 characters or fewer. Letters, digits and ./+/-/_ only.",
        error_messages={'invalid': "This value may contain only letters, numbers and ./+/-/_ characters."})
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


class BetaRegistrationForm(RegistrationForm):
    '''
    Special registration form for the private beta. Only allows users with
    email addresses in a BetaMember object to register.
    '''
    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if BetaMember.objects.filter(email=email).count() < 1:
            raise forms.ValidationError('This email address is not registered for entry into the Scenable private beta launch. '\
                                  'Are you sure you used the email address we have on record?')
        try:
            existing_user = User.objects.get(email=email)
            if existing_user.organization_set.count() > 0:
                raise forms.ValidationError('An business account for this email address already exists. Go ahead to the login page to enter the site.')
        except User.DoesNotExist:
            return email


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user', 'points')

    birth_date = forms.DateField(label=u'Birth date',
        widget=forms.DateInput(format='%m/%d/%Y'),
        input_formats=('%m/%d/%Y', '%m/%d/%y',),
        required=False)


class ActivityPreferencesForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('public_favorites', 'public_attendance', 'public_coupons')


# TODO: hook this up to User model
class CredentialsForm(forms.Form):
    email = forms.EmailField(label=u'Email address')

    current_password = forms.CharField(label=u'Current password')
    new_password = forms.CharField(label=u'New password')
    confirm_new_password = forms.CharField(label=u'Confirm new password')

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

