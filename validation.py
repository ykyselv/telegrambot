import re

def validation(msg):
    pattern = r'([0-1][0-9]|[2][0-3]):[0-5][0-9]'
    match = re.fullmatch(pattern, msg)
    if match:
        return True
    else:
        return False
