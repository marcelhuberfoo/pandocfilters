#!/usr/bin/env python
"""
Pandoc filter to process code blocks with class "graphviz" into
graphviz-generated images.
"""

import hashlib
import os
import sys
from pandocfilters import toJSONFilter, Str, Para, Image
from pygraphviz import AGraph as graph

imagedir = "img"
classtriggers = ['graphviz', 'dot']


def sha1(x):
    return hashlib.sha1(x.encode(sys.getfilesystemencoding())).hexdigest()


def filter_keyvalues(kv):
    kwargs = {'caption': [],
              'title': '',
              'kvlist': [],
              'name': '',
              'prog': 'dot'}
    for k, v in kv:
        if k in [u'caption', u'alt']:
            kwargs['caption'] = [Str(v)]
        elif k in [u'title', u'name', u'prog']:
            kwargs[k] = v
        else:
            kwargs['kvlist'].append([k, v])

    return kwargs


def ensure_writable_outputdir(imagedir):
    if not os.path.isdir(imagedir):
        try:
            os.makedirs(imagedir)
        except OSError:
            sys.stderr.write('Failed to create directory ' + imagedir + '\n')
            return False
    testfile = os.path.join(imagedir, '.tst.file.')
    try:
        with open(testfile, 'w+') as f:
            pass
    except (os.error, IOError):
        sys.stderr.write('Directory ' + imagedir + ' not writable\n')
        return False
    finally:
        os.unlink(testfile)
    return True


def prepare_code(code):
    return code


def graphviz(key, value, format, meta):
    if key == 'CodeBlock':
        try:
            [[ident, classes, keyvals], code] = value
        except:
            return None
        if set(classtriggers).intersection(set(classes)):
            kwargs = filter_keyvalues(keyvals)
            txt = prepare_code(code)
            G = graph(string=txt, name=kwargs['name'])
            filename = sha1(txt)
            if format == "html":
                filetype = "svg"
            elif format in ['latex', 'beamer']:
                filetype = "pdf"
            else:
                filetype = "png"
            if ensure_writable_outputdir(imagedir):
                dest = os.path.join(imagedir, '.'.join([filename, filetype]))
                if not os.path.isfile(dest):
                    G.draw(dest, prog=kwargs['prog'])
                    sys.stderr.write('Created image ' + dest + '\n')
                _classes = list(set(classes).difference(set(classtriggers)))
                return Para([Image([ident, _classes, kwargs['kvlist']],
                                   kwargs['caption'], [dest, kwargs['title']])])
    return None


if __name__ == "__main__":
    toJSONFilter(graphviz)
