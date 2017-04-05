#!/usr/bin/env python
"""
Pandoc filter that:
-  prepends CI_PROJECT_URL contents to relative links
   uses CI_COMMIT_REF_NAME or CI_BUILD_REF_NAME or master as fallback
"""

from pandocfilters import toJSONFilter, Link
import re
import os

CI_PROJECT_URL = os.environ.get('CI_PROJECT_URL', None)
CI_COMMIT_REF_NAME = os.environ.get('CI_COMMIT_REF_NAME', os.environ.get(
    'CI_BUILD_REF_NAME', 'master'))
LINK_REF_TO_REPLACE_RE = re.compile(
    r'^(?P<absolute>/\.\./)?(?P<rel_link>\w.*)$', re.UNICODE)


def add_gitlab_ref(k, v, fmt, meta):
    if k in ['Link'] and CI_PROJECT_URL is not None:
        if fmt in ['latex', 'beamer']:
            link_contents = v[-1]
            link_ref = link_contents[0]
            link_match = LINK_REF_TO_REPLACE_RE.search(link_ref)
            if link_match:
                rel_link = link_match.group('rel_link')
                if rel_link.startswith('http'):
                    return
                link_spec = [CI_PROJECT_URL]
                if link_match.group('absolute') is None:
                    link_spec.extend(['tree', CI_COMMIT_REF_NAME])
                link_spec.append(link_match.group('rel_link'))
                link_ref = os.path.join(*link_spec)
                link_contents[0] = link_ref
                return Link(v[0], v[1], link_contents)


if __name__ == "__main__":
    toJSONFilter(add_gitlab_ref)
