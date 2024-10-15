from django import forms
from .models import Journal

class JournalForm(forms.ModelForm):
    class Meta:
        model = Journal
        fields = ['title', 'content']  # 필요한 필드만 폼에 표시
