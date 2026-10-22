from django import forms
from apps.accounts.models import User
from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter project name",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Describe your project...",
                }
            ),
        }


class ProjectMemberForm(forms.Form):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role=User.Role.MEMBER, is_active=True),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-select",
                "size": 8,
            }
        ),
    )
