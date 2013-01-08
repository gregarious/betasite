from django import forms
from haystack.forms import SearchForm


class CategorySearchForm(SearchForm):
    def __init__(self, choices, *args, **kwargs):
        super(CategorySearchForm, self).__init__(*args, **kwargs)
        self.fields['category'] = forms.ChoiceField(choices=choices, required=False)
