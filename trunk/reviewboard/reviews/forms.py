import re

from django import newforms as forms
from django.contrib.auth.models import User

from reviewboard.diffviewer.models import DiffSetHistory
from reviewboard.reviews.models import Review, ReviewRequest, \
                                       ReviewRequestDraft, Screenshot

class NewReviewRequestForm(forms.Form):
    summary = forms.CharField(max_length=300)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 10}))
    testing_done = forms.CharField(widget=forms.Textarea(attrs={'rows': 10}))
    bugs_closed = forms.CharField()
    branch = forms.CharField()
    target_groups = forms.CharField()
    target_people = forms.CharField()

    @staticmethod
    def create_from_list(data, constructor, error):
        """Helper function to combine the common bits of clean_target_people
           and clean_target_groups"""
        result = []
        names = [x for x in map(str.strip, re.split('[, ]+', data)) if x]
        for name in names:
            result.append(constructor(name))
        return set(result)

    def create(self):
        diffset_history = DiffSetHistory()
        diffset_history.save()

        review_request = ReviewRequest(**self.clean_data)
        review_request.diffset_history = diffset_history
        review_request.save()
        return review_request

class UploadScreenshotForm(forms.Form):
    caption = forms.CharField(required=False)
    path = forms.CharField(widget=forms.FileInput())

    def create(self, data, review):
        draft = ReviewRequestDraft.create(review)

        screenshot = Screenshot(caption=self.clean_data['caption'])
        screenshot.save()
        screenshot.save_image_file(data["filename"], data["content"])

        draft.screenshots.add(screenshot)

        return screenshot
