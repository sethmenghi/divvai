import re

phone_regex = re.compile(
    r"([0-9]( |-)?)?(\(?[0-9]{3}\)?|[0-9]{3})( |-)?([0-9]{3}( |-)?[0-9]{4}|[0-9]{7})"
)

street_address_regex = re.compile(
    r"\d{1,3}.?\d{0,3}\s[a-zA-Z]{2,30}\s[a-zA-Z]{2,15}"
)

email_regex = re.compile(
    "\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,3}"
)


def get_matches(s, regex):
    matches = regex.search(s)
    if matches:
        return matches.group(0)


def get_street(s):
    return get_matches(s, street_address_regex)


def get_email(s):
    return get_matches(s, email_regex)


def get_phone(s):
    return get_matches(s, phone_regex)
