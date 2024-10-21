from django import forms
from .models import Questions

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Questions
        fields = ['title', 'content']  # 필요한 필드만 폼에 표시