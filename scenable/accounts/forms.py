from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from scenable.accounts.models import UserProfile, BetaMember, Organization

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate


class EmailAuthenticationForm(AuthenticationForm):
    '''
    AuthenticationForm that accepts an email address as well as a username.
    '''
    def clean(self):
        '''
        Override default logging in behavior to allow for email address
        login. Doing this here instead of clean_username because we don't
        want to reveal email addresses via a field-specific error message.
        '''
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            if '@' in username:
                # grab all possible usernames associated with this email address to authenitcate with
                # we'll never allow a login for more than one, but trying all of them allows us to
                # hold off on the multi-user email error until after a good password is used
                usernames = [u.username for u in User.objects.filter(email=username)]
                auth_users = [authenticate(username=username, password=password) for username in usernames]
                if not any(auth_users):
                    raise forms.ValidationError("Please enter a correct email address and password. Note that both fields are case-sensitive.")
                if len(auth_users) > 1:
                    raise forms.ValidationError("This email address is associated with more than one user. Please use a username.")
                self.user_cache = auth_users[0]
            else:
                # standard authentication
                self.user_cache = authenticate(username=username, password=password)
                if self.user_cache is None:
                    raise forms.ValidationError("Please enter a correct username and password. Note that both fields are case-sensitive.")
                elif not self.user_cache.is_active:
                    raise forms.ValidationError("This account is inactive.")
        self.check_for_test_cookie()
        return self.cleaned_data


class RememberMeForm(forms.Form):
    '''
    Basic checkbox for remembering the user. Responsibility of the view to
    do something with this value.
    '''
    remember_me = forms.BooleanField(label="Keep me logged in on this computer", initial=False)


class RegistrationForm(UserCreationForm):
    '''
    Overrides UserCreationForm to include email address, also disallows @
    symbols in usernames.
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


class EmailForm(forms.ModelForm):
    """
    A form for changing a user's email. Note that this form mandates that a
    user has an email address.
    """
    # same as default field, but with required turned off
    email = forms.EmailField(max_length=75, required=True, label=u'E-mail address')

    class Meta:
        model = User
        fields = ("email",)


class BetaRegistrationForm(RegistrationForm):
    '''
    Special registration form for the private beta. Only allows users with
    email addresses in a BetaMember object to register.
    '''
    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
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


class CredentialsForm(PasswordChangeForm):
    email = forms.EmailField(label=u'Email address')

    def __init__(self, user, *args, **kwargs):
        initial = kwargs.setdefault('initial', {})
        if 'email' not in initial:
            initial['email'] = user.email
        super(CredentialsForm, self).__init__(user, *args, **kwargs)

    def save(self, commit=True):
        # parent sets the new password
        super(CredentialsForm, self).save(commit=False)
        self.user.email = self.cleaned_data['email']
        if commit:
            self.user.save()
        return self.user
CredentialsForm.base_fields.keyOrder = ['email', 'old_password',
                                        'new_password1', 'new_password2']


class OrganizationForm(forms.ModelForm):
    '''
    Organization-backed model form. Only exposes organization name.
    '''
    class Meta:
        model = Organization
