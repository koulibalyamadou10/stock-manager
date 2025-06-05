from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter(name='gnf')
def gnf_currency(value):
    """Format a value as GNF currency"""
    try:
        if value is None:
            return "0 GNF"
        # Convert to float first to handle both string and numeric inputs
        float_value = float(value)
        # Convert to integer as GNF doesn't use decimals
        int_value = int(float_value)
        # Format with thousand separators
        formatted_value = "{:,}".format(int_value).replace(",", " ")
        return f"{formatted_value} GNF"
    except (ValueError, TypeError):
        return "0 GNF"  # Return safe default for invalid values
