"""Add users to Django Admin."""

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from rest_framework.authtoken.models import TokenProxy

from .models import User

import logging
logger = logging.getLogger(__name__)

import json 
from django.contrib.admin.widgets import AdminTextInputWidget
class JSONCheckboxWidget(AdminTextInputWidget):
       def render(self, name, value, renderer, attrs=None):
           if value:
               try:
                   value_dict = json.loads(value)
               except json.JSONDecodeError:
                   value_dict = {}
           else:
               value_dict = {}

           checkbox_html = ""
           """
           <div class="checkbox-row"> 
                <input type="checkbox" name="is_superuser" id="id_is_superuser"><label class="vCheckboxLabel" for="id_is_superuser">Superuser status</label>
                <div class="help">Designates that this user has all permissions without explicitly assigning them.</div>
           </div>
           """
           for key, val in value_dict.items():
               checkbox_html += f'<input type="checkbox" name="{name}_{key}" value="1" id="id_{name}_{key}" {"checked" if val else ""}> <label class="vCheckboxLabel" for=f"id_{name}_{key}"> {key}</label> <br>'

           if checkbox_html != "":
                return f"<p>{checkbox_html}</p>"
           else:
                return ""

       def value_from_datadict(self, data, files, name):
           result = {}
           for key in data:
               if key.startswith(name + "_"):
                   result[key[len(name) + 1:]] = True
           return json.dumps(result)


class UserForm(forms.ModelForm):
    """Customize the user admin form."""
    

    class Meta:
        """Define customizations."""

        model = User
        exclude = ['password', 'user_permissions']
        readonly_fields = ['last_login', 'date_joined', 'login_gov_uuid', 'hhs_id', 'access_request']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['feature_flags'] = forms.JSONField(widget=JSONCheckboxWidget)

    def clean(self):
        """Add extra validation for locations based on roles."""
        cleaned_data = super().clean()
        groups = cleaned_data['groups']
        if len(groups) > 1:
            raise ValidationError("User should not have multiple groups")

        return cleaned_data

from django.db import models
from django.contrib.postgres.forms import JSONField as JSONFormField

import json 
from django.contrib.admin.widgets import AdminTextInputWidget



"""

class JSONCheckboxField(JSONFormField):
    def prepare_value(self, value):
        if isinstance(value, dict):
            return [(k, v) for k, v in value.items() if v]
        return value

    def to_python(self, value):
        pass

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs['class'] = 'json-checkbox-field'  # Add a custom class for styling
        return attrs
"""


class UserAdmin(admin.ModelAdmin):
    """Customize the user admin functions."""

    exclude = ['password', 'user_permissions', 'is_active']
    readonly_fields = ['last_login', 'date_joined', 'login_gov_uuid', 'hhs_id', 'access_request', 'deactivated']
    form = UserForm
    list_filter = ('account_approval_status', 'region', 'stt')
    list_display = [
        "username",
        'access_requested_date',
        "region",
        "stt",
        "account_approval_status",
    ]
    autocomplete_fields = ['stt']

    """
    formfield_overrides = {
        models.JSONField: {
            #'form_class': JSONCheckboxField,
            'widget': JSONCheckboxWidget}
    }
    """

    def has_add_permission(self, request):
        """Disable User object creation through Django Admin."""
        return False


admin.site.register(User, UserAdmin)
admin.site.unregister(TokenProxy)
