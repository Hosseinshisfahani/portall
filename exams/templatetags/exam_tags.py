from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Gets an item from a dictionary using the key.
    Returns None if key is not found.
    Usage: {{ mydict|get_item:key }}
    """
    try:
        if not dictionary or not isinstance(dictionary, dict):
            return None
        return dictionary.get(key)
    except (AttributeError, KeyError, TypeError):
        return None

@register.filter
def format_time_remaining(seconds):
    """
    Formats seconds into mm:ss format
    Usage: {{ seconds|format_time_remaining }}
    """
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"

@register.filter
def has_status(registrations, status):
    """
    Returns True if any registration in the queryset has the given status.
    Usage: {{ registrations|has_status:'pending' }}
    """
    return registrations.filter(status=status).exists()

@register.filter
def has_completed(registrations):
    """
    Returns True if any registration in the queryset has completed_at set.
    Usage: {{ registrations|has_completed }}
    """
    return registrations.filter(completed_at__isnull=False).exists()

@register.filter
def viewed_answer(user_answer):
    """
    Returns the viewed_answer attribute of a UserAnswer object.
    Usage: {{ user_answer|viewed_answer }}
    """
    if user_answer:
        return user_answer.viewed_answer
    return False

@register.filter
def card_format(card_number):
    """
    Formats a card number with spaces for better readability.
    Usage: {{ card_number|card_format }}
    """
    if not card_number:
        return ""
    
    # Remove any existing spaces
    card_number = card_number.replace(" ", "")
    
    # Add a space every 4 digits
    chunks = []
    for i in range(0, len(card_number), 4):
        chunks.append(card_number[i:i+4])
    
    # Join chunks and add Unicode left-to-right mark to prevent RTL reversal
    formatted = "\u200E " + " \u200E".join(chunks) + " \u200E"
    
    return formatted

@register.filter
def get_index(list_obj, index):
    """Get item from list by index"""
    try:
        return list_obj[index]
    except (IndexError, TypeError):
        return None

@register.filter
def attr(obj, attr_name):
    """Get attribute from object"""
    try:
        return getattr(obj, attr_name)
    except (AttributeError, TypeError):
        return None 