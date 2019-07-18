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
               'placeholder': 'https://github.com/sun-hacks'}))
    devpost = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'https://devpost.com/sunhacks'}))
    linkedin = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'https://www.linkedin.com/in/sunhacks'}))
    site = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'https://sunhacks.io'}))
    phone_number = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '##########'}))

    lenny_face = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '( ﾉ ﾟｰﾟ)ﾉ☀'}))

    university = forms.CharField(required=True,
                                 label='What university do you study at?',
                                 help_text='Current or most recent school you attended',
                                 widget=forms.TextInput(
                                     attrs={'class': 'typeahead-schools', 'autocomplete': 'off'}))

    degree = forms.CharField(required=True, label='What\'s your major/degree?',
                             help_text='Current or most recent degree you\'ve received',
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
        label='Do you need a travel reimbursement to attend?',
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
                                      label='I have read and agree to the '
                                            '<a href="%s" target="_blank">MLH Code of Conduct</a>.' %
                                      getattr(settings, 'CODE_CONDUCT_LINK', '/code_conduct'), )

    mlh_consent = forms.BooleanField(required=False,
                                     label="I further agree to the terms"
                                     " of both the <a target='_blank' href='"
                                     "https://github.com/MLH/mlh-policies/blob/master/"
                                     "prize-terms-and-conditions/contest-terms.md'"
                                     ">MLH Contest Terms and Conditions</a> "
                                     "and the <a target='_blank' href='https://mlh.io/privacy'>"
                                     "MLH Privacy Policy</a>.", )

    data_consent = forms.TypedChoiceField(
        required=False,
        label=(
            "I authorize you to share my application/registration information "
            "for event administration, ranking, MLH administration, pre- and "
            "post-event informational emails, and occasional messages about "
            "hackathons in-line with the MLH Privacy Policy."
        ),
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')),
        initial=False,
        widget=forms.RadioSelect
    )

    sponsor_consent = forms.TypedChoiceField(
        required=False,
        label="I would like my CV, name, and year of graduation to be shared with the event sponsors.",
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')),
        initial=False,
        widget=forms.RadioSelect
    )

    def clean_code_conduct(self):
        cc = self.cleaned_data.get('code_conduct', False)
        # Check that if it's the first submission hackers checks code of conduct checkbox
        # self.instance.pk is None if there's no Application existing before
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not cc and not self.instance.pk:
            raise forms.ValidationError(
                "To attend %s you must abide by our code of conduct." % settings.HACKATHON_NAME
            )
        return cc

    def clean_data_consent(self):
        cc = self.cleaned_data.get('data_consent', False)
        return cc

    def clean_sponsor_consent(self):
        cc = self.cleaned_data.get('sponsor_consent', False)
        return cc

    def clean_mlh_consent(self):
        cc = self.cleaned_data.get('mlh_consent', False)
        if not cc and not self.instance.pk:
            raise forms.ValidationError(
                "To attend %s you must agree to MLH's"
                " privacy policy and terms and conditions." % settings.HACKATHON_NAME
            )
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
            raise forms.ValidationError("Please tell us your specific dietary requirements")
        return data

    def clean_other_gender(self):
        data = self.cleaned_data['other_gender']
        gender = self.cleaned_data['gender']
        if gender == models.GENDER_OTHER and not data:
            raise forms.ValidationError("Please enter this field or select 'Prefer not to answer'")
        return data

    def __getitem__(self, name):
        item = super(ApplicationForm, self).__getitem__(name)
        item.field.disabled = not self.instance.can_be_edit()
        return item

    def fieldsets(self):
        # Fieldsets ordered and with description
        self._fieldsets = [
            ('Personal Info',
             {'fields': ('university', 'degree', 'education', 'graduation_year', 'gender', 'other_gender',
                         'ethnicity', 'other_ethnicity', 'phone_number',
                         'tshirt_size', 'diet', 'other_diet'),
              'description': 'Hey there, before we begin we would like to know a little more about you.', }),
            ('Hackathons?', {'fields': ('description', 'first_timer', 'projects', 'lennyface'), }),
            ('Show us what you\'ve built',
             {'fields': ('github', 'devpost', 'linkedin', 'site', 'resume'),
              'description': 'Some of our sponsors may use this information for recruitment purposes,'
              'so please include as much as you can.'}),
        ]
        deadline = getattr(settings, 'REIMBURSEMENT_DEADLINE', False)
        r_enabled = getattr(settings, 'REIMBURSEMENT_ENABLED', False)
        if r_enabled and deadline and deadline <= timezone.now() and not self.instance.pk:
            self._fieldsets.append(('Travelling',
                                    {'fields': ('origin',),
                                     'description': 'Reimbursement applications are now closed. '
                                                    'Sorry for the inconvenience.',
                                     }))
        elif self.instance.pk and r_enabled:
            self._fieldsets.append(('Travelling',
                                    {'fields': ('origin',),
                                     'description': 'If you applied for reimbursement, check out the Travel tab. '
                                                    'Email us at %s for any change needed on reimbursements.' %
                                                    settings.HACKATHON_CONTACT_EMAIL,
                                     }))
        elif not r_enabled:
            self._fieldsets.append(('Traveling',
                                    {'fields': ('origin',)}), )
        else:
            self._fieldsets.append(('Travelling',
                                    {'fields': ('origin', 'reimb', 'reimb_amount'), }), )

        # Fields that we only need the first time the hacker fills the application
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not self.instance.pk:
            self._fieldsets.append(('Legal', {'fields': ('code_conduct', 'mlh_consent',
                                                         'data_consent', 'sponsor_consent', 'under_age')}))
        else:
            self._fieldsets.append(('Legal', {'fields': ('data_consent', 'sponsor_consent')}))
        return super(ApplicationForm, self).fieldsets

    class Meta:
        model = models.Application
        help_texts = {
            'education': 'Current or most recent level of education',
            'gender': 'This is for demographic purposes',
            'ethnicity': 'This is also for demographic purposes',
            'graduation_year': 'What year have you graduated on or when will '
                               'you graduate',
            'degree': 'What\'s your major/degree?',
            'other_diet': 'Please fill here in your dietary requirements. We want to make sure we have food for you!',
            'projects': 'You can talk about about past hackathons, personal projects, awards, and so on. '
                        'We love links, show us your passion!',
            'reimb_amount': 'We try our best to cover costs for all hackers, but our budget is limited'
        }

        widgets = {
            'origin': forms.TextInput(attrs={'autocomplete': 'off'}),
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'projects': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'graduation_year': forms.RadioSelect(),
        }

        labels = {
            'education': 'What level of education are you enrolled in?',
            'gender': 'What gender do you identify as?',
            'other_gender': 'Self-describe',
            'ethnicity': 'What ethnicity do you identify as?',
            'other_ethnicity': 'Self-describe',
            'graduation_year': 'What year will you graduate?',
            'tshirt_size': 'What\'s your t-shirt size?',
            'diet': 'Dietary requirements',
            'origin': 'Where are you joining us from?',
            'description': 'Why are you excited about %s? (1500 char max)' % settings.HACKATHON_NAME,
            'projects': 'What projects have you worked on? (1500 char max)',
            'lennyface': 'What is your favorite emoticon? (300 char max, go wild)',
            'resume': 'Upload your resume (PDF only)',
            'reimb_amount': 'How much money (%s) would you need to afford traveling to %s?' % (
                getattr(settings, 'CURRENCY', '$'), settings.HACKATHON_NAME),

        }

        exclude = ['user', 'uuid', 'invited_by', 'submission_date', 'status_update_date', 'status', ]
