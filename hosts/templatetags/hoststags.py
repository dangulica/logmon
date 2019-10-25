from django import template


register = template.Library()


@register.filter
def next(some_list, current_index):
    """
    Returns the next element of the list using the current index if it exists.
    Otherwise returns the same element
    """
    if current_index >= 0 and current_index < len(some_list) - 1:
        return some_list[int(current_index) + 1]  # access the next element
    else:
        return some_list[int(current_index)]  # return same element if index is out of range


@register.filter
def previous(some_list, current_index):
    """
    Returns the previous element of the list using the current index if it exists.
    Otherwise returns the same element.
    """
    if current_index >= 1 and current_index < len(some_list):
        return some_list[int(current_index) - 1]  # access the next element
    else:
        return some_list[int(current_index)]  # return same element if index is out of range
