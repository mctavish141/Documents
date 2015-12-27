from django import forms

class AddArticleForm(forms.Form):
    title = forms.CharField(max_length=100, label='', required=True)
    description = forms.CharField(widget=forms.Textarea, label='', required=True)
    #(attrs={'cols': 100, 'rows': 1})

class AddCommentForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea, label='', required=True)

class LoginForm(forms.Form):
    login = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class RegisterForm(forms.Form):
    login = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    name = forms.CharField(required=True)
    surname = forms.CharField(required=True)

class ManageCommentsForm(forms.Form):
    comments_list = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, label='Choose comments', choices=())
    def __init__(self, *args, **kwargs):
        comments = kwargs.pop('comments', None)
        super(ManageCommentsForm, self).__init__(*args, **kwargs)

        if comments is not None:
            list1 = []
            for comment in comments:
                commentStr = "%s\n%s" % (comment["author"], comment["description"])
                tuple = (comment['id'], commentStr)
                list1.append(tuple)
            self.fields['comments_list'].choices = list1

    def is_valid(self):
        return True

from datetime import datetime
from django.forms.extras.widgets import SelectDateWidget
from db import getMinYear

class SearchArticlesForm(forms.Form):
    current_datetime = datetime.now()
    minYear = getMinYear()
    year_choices = range(minYear, current_datetime.year + 1)
    #date_from = forms.DateField(widget=SelectDateWidget(years=year_choices), initial='2015-12-01')
    #date_to = forms.DateField(widget=SelectDateWidget(years=year_choices), initial='2015-12-21')
    date_from = forms.DateField(widget=SelectDateWidget(years=year_choices), initial='{0}-01-01'.format(minYear))
    date_to = forms.DateField(widget=SelectDateWidget(years=year_choices), initial=current_datetime.date())
    title = forms.CharField(required=False)
