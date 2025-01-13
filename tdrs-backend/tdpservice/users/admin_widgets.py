import json 
from django.contrib.admin.widgets import AdminTextInputWidget

import logging
logger = logging.getLogger(__name__)

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
               logger.info(f"key-------: {key}, val--------: {val}")
               checkbox_html += f'<input type="checkbox" name="{name}_{key}" value="1" {"checked" if val else ""}> {key}'

           return f'<div class="checkbox-row>{checkbox_html}</div>'

       def value_from_datadict(self, data, files, name):
           result = {}
           for key in data:
               if key.startswith(name + "_"):
                   result[key[len(name) + 1:]] = True
           return json.dumps(result)
