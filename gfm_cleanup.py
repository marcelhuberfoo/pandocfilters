#!/usr/bin/env python
"""
Pandoc filter that:
-  removes backticks within InlineMath contents
"""

from pandocfilters import toJSONFilter, Math
import re

STRIP_BACKTICKS_RE = re.compile(r'^`(?P<contents>.*)`$', re.MULTILINE |
                                re.UNICODE | re.DOTALL)


def cleanup(k, v, fmt, meta):
    if k in ['Math']:
        if fmt in ['latex', 'beamer', 'json']:
            math_type = v[0].get('t', None)
            if math_type in [u'InlineMath'] and len(v) > 1:
                solution_match = STRIP_BACKTICKS_RE.search(v[1])
                if solution_match:
                    return Math(v[0], solution_match.group('contents'))


if __name__ == "__main__":
    toJSONFilter(cleanup)
