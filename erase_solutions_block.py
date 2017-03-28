#!/usr/bin/env python
"""
Pandoc filter that causes everything between
'<!-- BEGIN SOLUTION -->' and '<!-- END SOLUTION -->'
to be ignored.  The comment lines must appear on
lines by themselves, with blank lines surrounding
them.
"""

from pandocfilters import toJSONFilter
import re

incomment = False


def comment(k, v, fmt, meta):
    global incomment
    if k in ['RawBlock', 'RawInline']:
        fmt, s = v
        if fmt == "html":
            if re.search("<!-- BEGIN SOLUTION -->", s):
                incomment = True
                return []
            elif re.search("<!-- END SOLUTION -->", s):
                incomment = False
                return []
    if incomment:
        return []  # suppress anything in a comment


if __name__ == "__main__":
    toJSONFilter(comment)
