from business_rules import run_all
from business_rules.actions import BaseActions
from business_rules.variables import BaseVariables, string_rule_variable
from business_rules.fields import FIELD_TEXT

class FieldMappingVariables(BaseVariables):
    def __init__(self, field_name):
        self.field_name = field_name

    @string_rule_variable
    def field_name(self):
        return self.field_name

class FieldMappingActions(BaseActions):
    def __init__(self, field_name):
        self.field_name = field_name
        self.mapped_name = None

    def map_field(self, new_name):
        self.mapped_name = new_name

def map_fields(field_dict):
    """
    Maps field names using business rules.
    Falls back to original name if no mapping rule matches.
    """
    rules = [
        {
            'conditions': {
                'name': 'field_name',
                'operator': 'equal_to',
                'value': 'first_name'
            },
            'actions': [
                {
                    'name': 'map_field',
                    'params': {'new_name': 'firstName'}
                }
            ]
        }
        # Add more rules as needed
    ]

    mapped = {}
    for name, source in field_dict.items():
        variables = FieldMappingVariables(name)
        actions = FieldMappingActions(name)
        run_all(rule_list=rules, variables=variables, actions=actions)
        mapped[name] = actions.mapped_name if actions.mapped_name else source
    return mapped
