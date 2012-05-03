from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from onlyinpgh.feedback.forms import GenericFeedbackForm


@login_required
def submit_generic(request):
    if request.POST:
        form = GenericFeedbackForm(user=request.user, data=request.POST)
        if form.is_valid():
            if form.cleaned_data['feedback'].strip() != '':
                form.save()
    return HttpResponse()
