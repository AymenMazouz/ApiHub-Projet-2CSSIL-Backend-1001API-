import re


def is_email_valid(email: str) -> bool:
    return bool(re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", email))
