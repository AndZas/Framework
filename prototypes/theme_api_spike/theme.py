"""Experimental token grammar and resolution. No production framework imports."""
from dataclasses import dataclass
from pathlib import Path
import math
import re

DEFAULTS = dict(background='#f3f5fa', foreground='#202b43', panel='#ffffff',
                accent='#405cc7', accent_text='#ffffff', radius=14.0, opacity=1.0,
                gradient=('#405cc7', '#27a998'))
DARK = dict(background='#131a2a', foreground='#e5eafa', panel='#202c42',
            accent='#819bff', accent_text='#131a2a', gradient=('#395bb4', '#237d80'))


def validate(values, source):
    if not isinstance(values, dict):
        raise ValueError(f'{source}: expected a token dictionary')
    result = {}
    for key, value in values.items():
        where = f'{source}: {key}={value!r}'
        if key not in DEFAULTS:
            raise ValueError(f'{where}: unsupported token')
        if key in ('radius', 'opacity'):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f'{where}: expected a finite number')
            limit = 48 if key == 'radius' else 1
            if not 0 <= value <= limit:
                raise ValueError(f'{where}: expected 0..{limit}')
            result[key] = float(value)
        elif key == 'gradient':
            if not isinstance(value, (tuple, list)) or len(value) != 2:
                raise ValueError(f'{where}: expected two #RRGGBB colors')
            result[key] = tuple(validate({'accent': c}, where)['accent'] for c in value)
        else:
            if not isinstance(value, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', value):
                raise ValueError(f'{where}: expected #RRGGBB')
            result[key] = value.lower()
    return result


@dataclass(frozen=True, init=False)
class Theme:
    name: str
    _values: tuple

    def __init__(self, name, **tokens):
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, '_values', tuple(validate(tokens, name).items()))

    @property
    def tokens(self):
        return dict(self._values)

    @classmethod
    def load(cls, path):
        path = Path(path)
        return parse(path.read_text(encoding='utf-8-sig'), str(path))


def parse(text, source='<theme>'):
    match = re.fullmatch(r'\s*:theme\s*\{([^{}]*)\}\s*', text)
    if not match:
        raise ValueError(f'{source}: expected exactly one :theme {{ ... }} block; other selectors/comments are unsupported')
    tokens = {}
    body = match.group(1)
    offset = match.start(1)
    for declaration in body.split(';')[:-1]:
        first_token = offset + len(declaration) - len(declaration.lstrip())
        line = text.count('\n', 0, first_token) + 1
        location = f'{source}:{line}'
        offset += len(declaration) + 1
        pair = re.fullmatch(r'\s*([a-z][a-z-]*)\s*:\s*(.*?)\s*', declaration)
        if not pair:
            raise ValueError(f'{location}: invalid declaration {declaration!r}')
        key, value = pair.groups()
        key = key.replace('-', '_')
        if key in tokens:
            raise ValueError(f'{location}: duplicate token {key}')
        if key in ('radius', 'opacity'):
            if not re.fullmatch(r'\d+(?:\.\d+)?', value):
                raise ValueError(f'{location}: {key}={value!r}: expected unitless decimal')
            value = float(value)
        elif key == 'gradient':
            gradient = re.fullmatch(r'linear-gradient\(\s*(#[\da-fA-F]{6})\s*,\s*(#[\da-fA-F]{6})\s*\)', value)
            if not gradient:
                raise ValueError(f'{location}: gradient={value!r}: expected linear-gradient(#RRGGBB, #RRGGBB)')
            value = gradient.groups()
        tokens.update(validate({key: value}, location))
    if body.split(';')[-1].strip():
        raise ValueError(f'{source}: final declaration requires a semicolon')
    return Theme(source, **tokens)


def resolve(theme, override=None):
    return DEFAULTS | theme.tokens | validate(override or {}, 'widget style')


CUSTOM = Theme('Lagoon / Python', background='#eaf5f2', foreground='#173b3a',
               panel='#ffffff', accent='#126e67', accent_text='#ffffff',
               radius=20, opacity=0.94, gradient=('#126e67', '#65b8a3'))
