#!/usr/bin/env python
"""
Pandoc filter to inline SOLUTION 'html' blocks into markdown.
Works for RawInline and RawBlock.
"""

from pandocfilters import toJSONFilter, Str, Plain, Para
from subprocess import call, PIPE, Popen
import re
import json

SOL_RE = re.compile(r'^<!--\sSOLUTION\s+(?P<contents>.*)\s*-->$', re.MULTILINE |
                    re.UNICODE | re.DOTALL)


def solution(key, value, format, meta):
    if key in ['RawInline', 'RawBlock']:
        if value[0] == 'html':
            solution_match = SOL_RE.search(value[1])
            if solution_match:
                p = Popen(['pandoc', '-f', 'markdown', '-t', 'json'],
                          stdin=PIPE,
                          stdout=PIPE)
                output, _ = p.communicate(solution_match.group(
                    'contents').encode('utf8'))
                out_json = json.loads(output.decode('utf8'))[1]
                if key == 'RawBlock':
                    return out_json
                return out_json[0].get('c')


if __name__ == "__main__":
    toJSONFilter(solution)
