from django import forms
from apps.accounts.models import User
from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "manager"]
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
                    "placeholder": (
                        "Describe your project. "
                        "You can include a project URL."
                    ),
                }
            ),
            "manager": forms.Select(
                attrs={"class": "form-select"}
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["manager"].queryset = User.objects.filter(
            role=User.Role.MANAGER,
            is_active=True,
        )

        if not (
            user
            and (
                user.is_superuser
                or user.role == User.Role.ADMIN
            )
        ):
            self.fields.pop("manager")

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        manager = cleaned_data.get("manager")

        if (
            name
            and manager
            and Project.objects.filter(
                name=name,
                manager=manager,
            ).exclude(pk=self.instance.pk).exists()
        ):
            self.add_error(
                "name",
                "This Manager already has a project with this name.",
            )

        return cleaned_data


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
