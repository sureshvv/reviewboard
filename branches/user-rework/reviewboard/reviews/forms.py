from django import newforms as forms
from django.contrib.auth.models import User, Group
from reviewboard.reviews.models import ReviewRequest

class NewReviewRequestForm(forms.Form):
    summary = forms.CharField(max_length=300)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 10}))
    testing_done = forms.CharField(widget=forms.Textarea(attrs={'rows': 10}))
    bugs_closed = forms.CharField()
    branch = forms.CharField()
    target_groups = forms.CharField()
    target_people = forms.CharField()

    def create_from_list(data, constructor, error):
        """Helper function to combine the common bits of clean_target_people
           and clean_target_groups"""
        result = []
        names = [name.strip() for name in data.split(',')]
        for name in names:
            try:
                result.append(constructor(name))
            except:
                raise forms.ValidationError(error % name)
        return set(result)

    def clean_target_people(self):
        return create_from_list(self.clean_data['target_people'],
                                lambda x: User.objects.get(username=x),
                                'Reviewer "%s" does not exist')

    def clean_target_groups(self):
        return create_from_list(self.clean_data['target_groups'],
                                lambda x: User.objects.get(name=x),
                                'Group "%s" does not exist')

    def clean(self):
        if not self.clean_data['target_people'] and \
           not self.clean_data['target_groups']:
            raise forms.ValidationError(
                'You must specify at least one reviewer or group')

    def create(self):
        review_request = ReviewRequest(**self.clean_data)
        review_request.save()
        return review_request
