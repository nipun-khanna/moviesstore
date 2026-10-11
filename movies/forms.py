from django import forms

class RatingForm(forms.Form):
    score = forms.TypedChoiceField(
        label='Your rating',
        widget=forms.RadioSelect,
        coerce=int,
        choices=[
            (score, f"{score} star{'s' if score > 1 else ""}")
            for score in range(1, 6)
        ]
    )