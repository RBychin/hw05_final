from django import template
register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


@register.filter
def get_obj_attr(obj, attr):
    return getattr(obj, str(attr))

@register.filter
def in_likes(things, category):
    return things.get(post=category)


@register.filter
def news(object, read):
    return object.filter(is_readed=read)
