import re

_COLON = re.compile(r'\s*:\s*')
_BRACKET_TAG = re.compile(r'\[(SYSTEM|ERROR|ADMIN|GAME|HOST|RULE)\]', re.IGNORECASE)
_FENCE = re.compile(r'[-=_]{3,}')


def sanitize_text(text: str) -> str:
    text = _COLON.sub(' - ', text)
    text = _BRACKET_TAG.sub('', text)
    text = _FENCE.sub('', text)
    return text


INACTIVITY_TIMEOUT = 900  # seconds before idle round gate disconnects the session
