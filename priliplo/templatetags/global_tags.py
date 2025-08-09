from django import template

register = template.Library()


@register.simple_tag
def compare_current_w_prev(some_list, current_index):
    try:
        if current_index != 0:
            # return some_list[int(current_index)].odometer
            return some_list[int(current_index)].odometer - some_list[int(current_index) - 1].odometer  # access the next element
        else:
            return 0

    except:
        return 0  # return empty string in case of exception
