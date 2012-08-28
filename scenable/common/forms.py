from django import forms
from haystack.forms import SearchForm


def CategorySearchFormFactory(choices):
    class CategorySearchForm(SearchForm):
        category = forms.ChoiceField(choices=choices, required=False)

        # TODO: category filtering should go here, but we'd need to
        # change the indexes to do this in any non-hacky way, and
        # I kind of have to build two native apps right now. Sooo, later.
    return CategorySearchForm
