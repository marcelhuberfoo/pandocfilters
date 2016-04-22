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


def sha1(x):
    return hashlib.sha1(x.encode(sys.getfilesystemencoding())).hexdigest()

imagedir = "img"
classtriggers = ['graphviz', 'dot']

def graphviz(key, value, format, meta):
    if key == 'CodeBlock':
        try:
            [[ident, classes, keyvals], code] = value
        except:
            return None
        keyvaldict = dict([(x[0],x[1]) for x in keyvals])
        if set(classtriggers).intersection(set(classes)):
            caption = keyvaldict.get('alt', 'picture placeholder')
            name = keyvaldict.get('name', '')
            title = keyvaldict.get('title', '')
            prog = keyvaldict.get('prog', 'dot')
            G = graph(string=code, name=name)
            filename = sha1(code)
            if format == "html":
                filetype = "svg"
            elif format in ['latex', 'beamer']:
                filetype = "pdf"
            else:
                filetype = "png"
            alt = Str(caption)
            src = imagedir + '/' + filename + '.' + filetype
            if not os.path.isdir(imagedir):
              try:
                os.makedirs(imagedir)
              except OSError:
                sys.stderr.write('Failed to create directory ' + imagedir + '\n')
            if not os.path.isfile(src):
                G.draw(src, prog=prog)
                sys.stderr.write('Created image ' + src + '\n')
            _id = ident
            _classes = list(set(classes).difference(set(classtriggers)))
            _keyvallists = [[k,v] for (k,v) in keyvaldict.items() if k not in ['name', 'title', 'alt']]
            return Para([Image([_id, _classes, _keyvallists], [alt], [src, title])])
    return None

if __name__ == "__main__":
    toJSONFilter(graphviz)
