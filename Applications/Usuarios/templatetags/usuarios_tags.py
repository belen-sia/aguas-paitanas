# Usuarios/templatetags/usuarios_tags.py
from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Agrega una clase CSS a un campo de formulario de Django.
    Si el objeto no es un BoundField, lo devuelve tal cual.
    """
    try:
        return field.as_widget(attrs={'class': css_class})
    except AttributeError:
        # Si no tiene .as_widget(), probablemente es un string u otro objeto
        return field