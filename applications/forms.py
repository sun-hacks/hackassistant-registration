from django import forms
from django.conf import settings
from django.template.defaultfilters import filesizeformat
from django.utils import timezone
from form_utils.forms import BetterModelForm

from app.mixins import OverwriteOnlyModelFormMixin
from app.utils import validate_url
from applications import models


class ApplicationForm(OverwriteOnlyModelFormMixin, BetterModelForm):
    github = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'https://github.com/johnBiene'}))
    devpost = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'https://devpost.com/JohnBiene'}))
    linkedin = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'https://www.linkedin.com/in/john_biene'}))
    site = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'https://biene.space'}))
    phone_number = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '+############'}))
    university = forms.CharField(required=True,
                                 label='What university are you studying at?',
                                 help_text='Current or most recent school you attended.',
                                 widget=forms.TextInput(
                                     attrs={'class': 'typeahead-schools', 'autocomplete': 'off'}))

    degree = forms.CharField(required=True, label='What\'s your degree?',
                             help_text='Current or most recent degree you\'ve received.',
                             widget=forms.TextInput(
                                 attrs={'class': 'typeahead-degrees', 'autocomplete': 'off'}))

    first_timer = forms.TypedChoiceField(
        required=True,
        label='Will %s be your first hackathon?' % settings.HACKATHON_NAME,
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')),
        widget=forms.RadioSelect
    )

    reimb = forms.TypedChoiceField(
        required=False,
        label='Will you need a travel reimbursement to attend?',
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')),
        initial=False,
        widget=forms.RadioSelect
    )

    under_age = forms.BooleanField(
        required=False,
        label='I declare that I am at least 18 years of age.',
    )

    code_conduct = forms.BooleanField(required=False,
                                      label='I have read and accept the '
                                            '<a href="/code_conduct" target="_blank">%s Code of Conduct</a>' % (
                                                settings.HACKATHON_NAME), )

    def clean_resume(self):
        resume = self.cleaned_data['resume']
        size = getattr(resume, '_size', 0)
        if size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError("Please keep resume size under %s. Current filesize %s" % (
                filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(size)))
        return resume

    def clean_code_conduct(self):
        cc = self.cleaned_data.get('code_conduct', False)
        # Check that if it's the first submission hackers checks code of conduct checkbox
        # self.instance.pk is None if there's no Application existing before
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not cc and not self.instance.pk:
            raise forms.ValidationError("You must accept our code of conduct.")
        return cc

    def clean_under_age(self):
        over_18 = self.cleaned_data.get('under_age', False)
        if not over_18 and not self.instance.pk:
            raise forms.ValidationError("You must be 18 or over to attend.")
        return not over_18

    def clean_github(self):
        data = self.cleaned_data['github']
        validate_url(data, 'github.com')
        return data

    def clean_devpost(self):
        data = self.cleaned_data['devpost']
        validate_url(data, 'devpost.com')
        return data

    def clean_linkedin(self):
        data = self.cleaned_data['linkedin']
        validate_url(data, 'linkedin.com')
        return data

    def clean_projects(self):
        data = self.cleaned_data['projects']
        if not data:
            raise forms.ValidationError("This field is required.")
        return data

    def clean_reimb_amount(self):
        data = self.cleaned_data['reimb_amount']
        reimb = self.cleaned_data.get('reimb', False)
        if reimb and not data:
            raise forms.ValidationError("To apply for reimbursement please set a valid amount")
        deadline = getattr(settings, 'REIMBURSEMENT_DEADLINE', False)
        if data and deadline and deadline <= timezone.now():
            raise forms.ValidationError("Reimbursement applications are now closed. Trying to hack us?")
        return data

    def clean_reimb(self):
        reimb = self.cleaned_data.get('reimb', False)
        deadline = getattr(settings, 'REIMBURSEMENT_DEADLINE', False)
        if reimb and deadline and deadline <= timezone.now():
            raise forms.ValidationError("Reimbursement applications are now closed. Trying to hack us?")
        return reimb

    def clean_other_diet(self):
        data = self.cleaned_data['other_diet']
        diet = self.cleaned_data['diet']
        if diet == 'Other' and not data:
            raise forms.ValidationError("Please fill your specific diet requirements")
        return data

    def __getitem__(self, name):
        item = super(ApplicationForm, self).__getitem__(name)
        item.field.disabled = not self.instance.can_be_edit()
        return item

    def fieldsets(self):
        # Fieldsets ordered and with description
        self._fieldsets = [
            ('Personal Info',
             {'fields': ('university', 'degree', 'graduation_year', 'gender',
                         'phone_number', 'tshirt_size', 'diet', 'other_diet'),
              'description': 'Hey there, before we begin we would like to know a little more about you.', }),
            ('Hackathons?', {'fields': ('description', 'first_timer', 'projects'), }),
            ('Show us what you\'ve built', {'fields': ('github', 'devpost', 'linkedin', 'site', 'resume'), }),
        ]
        deadline = getattr(settings, 'REIMBURSEMENT_DEADLINE', False)
        if deadline and deadline <= timezone.now() and not self.instance.pk:
            self._fieldsets.append(('Travelling',
                                    {'fields': ('origin',),
                                     'description': 'Reimbursement applications are now closed. '
                                                    'Sorry for the inconvenience.',
                                     }))
        elif self.instance.pk:
            self._fieldsets.append(('Travelling',
                                    {'fields': ('origin',),
                                     'description': 'If you applied for reimbursement see it on the Travel tab. '
                                                    'Email us at %s for any change needed on reimbursements.' %
                                                    settings.HACKATHON_CONTACT_EMAIL,
                                     }))
        else:
            self._fieldsets.append(('Travelling',
                                    {'fields': ('origin', 'reimb', 'reimb_amount'), }), )

        # Fields that we only need the first time the hacker fills the application
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not self.instance.pk:
            self._fieldsets.append(('Code of Conduct', {'fields': ('code_conduct', 'under_age')}))
        return super(ApplicationForm, self).fieldsets

    class Meta:
        model = models.Application
        help_texts = {
            'gender': 'This is for demographic purposes. Feel free to skip this '
                      'question.',
            'graduation_year': 'What year did you graduate or when will '
                               'you graduate?',
            'degree': 'What\'s your degree?',
            'other_diet': 'We\'ll make sure you can enjoy all the food.',
            'projects': 'You can talk about about past hackathons, personal projects, awards, and so on. '
                        'We love links, so show us your passion! Go into lots of detail.',
            'reimb_amount': 'We try our best to cover costs for all hackers, but our budget is limited'
        }

        widgets = {
            'origin': forms.TextInput(attrs={'autocomplete': 'off'}),
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'projects': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'tshirt_size': forms.RadioSelect(),
            'graduation_year': forms.RadioSelect(),
        }

        labels = {
            'gender': 'What gender do you identify as?',
            'graduation_year': 'What year will you graduate?',
            'tshirt_size': 'What\'s your t-shirt size?',
            'diet': 'Dietary requirements',
            'origin': 'Where are you joining us from?',
            'description': 'Why are you excited about %s?' % settings.HACKATHON_NAME,
            'projects': 'What projects have you worked on?',
            'resume': 'Upload your resume',
            'reimb_amount': 'How much money (%s) would you need to afford travelling to %s?' % (
                settings.CURRENCY, settings.HACKATHON_NAME),

        }

        exclude = ['user', 'uuid', 'invited_by', 'submission_date', 'status_update_date', 'status', 'lennyface', ]
