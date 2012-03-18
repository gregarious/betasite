from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class OrgSignupForm(UserCreationForm):
    '''
    Form for org signups in the org admin panel. Similar to a UserCreationForm
    but with an additional organization name input.

    Currently assumes email address is username.
    '''
    # override the default username field as an email address. this is how business
    # signups will be handled for now
    username = forms.EmailField(label="Email address", initial='', max_length=30, required=True)
    orgname = forms.CharField(label="Organization", initial='', required=True)

    def clean_username(self):
        '''
        Overridden to rephrase username validation error
        '''
        try:
            cleaned = super(OrgSignupForm, self).clean_username()
            print 'returned as ', cleaned
        except forms.ValidationError:
            # rephrase the validation error
            raise forms.ValidationError("An organization with that email already exists.")
        else:
            return cleaned

    def save(self, commit=True):
        '''
        Override of User ModelForm that saves the email address as well as
        username and password.
        '''
        user = super(OrgSignupForm, self).save(commit=False)
        user.email = self.cleaned_data['username']
        if commit:
            user.save()
        return user



class OrgLoginForm(AuthenticationForm):
    '''
    Form for org admin login.

    Currently assumes email address is username.
    '''
    username = forms.EmailField(label="Email address", initial='', max_length=30)
