import re
from datetime import datetime

VALID_NAME_REGEX = re.compile(r'^[A-Za-z0-9._-]+$')  # allows alphanum + . _ -

def generate_timestamped_name(prefix: str, slugify: bool = True) -> str:
    """
    Generates a timestamped name like: SS.12-Apr-25_1042 or slugified.
    """
    now = datetime.now()
    name = f"{prefix}.{now.strftime('%d-%b-%y_%H%M')}"
    return slugify_string(name) if slugify else name

def slugify_string(name: str) -> str:
    """
    Slugify a name by replacing spaces, colons, or other invalid chars.
    """
    return re.sub(r'[^A-Za-z0-9._-]', '-', name)

def is_valid_name(name: str) -> bool:
    """
    Validate that the name contains only allowed characters.
    """
    return bool(VALID_NAME_REGEX.match(name))