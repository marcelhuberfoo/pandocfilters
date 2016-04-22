#! /usr/bin/env python
"""
Pandoc filter to convert svg files to pdf as suggested at:
https://github.com/jgm/pandoc/issues/265#issuecomment-27317316
"""

__authororig__ = "Jerome Robert"
__author__ = "Marcel Huber"

import mimetypes
import hashlib
import subprocess
import os
import sys
from datetime import datetime
from pandocfilters import toJSONFilter, Str, Para, Image
try:
  from urllib import request as urlopener
except:
  import urllib2 as urlopener


def sha1(x):
    return hashlib.sha1(x.encode(sys.getfilesystemencoding())).hexdigest()

def runCommand(
    args,
    logpath='',
    filename=None,
    stdincontent=None,
    **kw):
  import subprocess
  res = 1
  popenObject = subprocess.Popen(args,
      stdin=subprocess.PIPE,
      stderr=subprocess.PIPE,
      stdout=subprocess.PIPE,
      **kw)

  if not os.path.isdir(logpath):
    os.makedirs(logpath)
  logfilebasename = os.path.basename(args[0])
  if filename:
    logfilebasename = logfilebasename + '.' + os.path.basename(filename)
  errfilename = os.path.join(logpath, logfilebasename + '.stderr')
  outfilename = os.path.join(logpath, logfilebasename + '.stdout')
  try:
    popen_out, popen_err = popenObject.communicate(stdincontent)
    if popen_err:
      with open(errfilename, 'w') as errfile:
        errfile.write(str(popen_err))
    if popen_out:
      with open(outfilename, 'w') as outfile:
        outfile.write(str(popen_out))
    res = popenObject.returncode
  except OSError as e:
    with open(errfilename, 'w') as errfile:
      print >> errfile, e
      for line in popenObject.stderr:
        print >> errfile, line
  return res

#TODO add emf export if fmt=="docx" ?
fmt_to_option = {
  "latex": "pdf",
  "beamer": "pdf",
  "html": "png",
}

imagedir = "img"

def svg_to_any(key, value, fmt, meta):
  if key == 'Image':
    try:
      [_id, _classes, _keyvallists], [alt], [src, title] = value
    except:
      return None
    mimet,_ = mimetypes.guess_type(src)
    option = fmt_to_option.get(fmt)
    if mimet == 'image/svg+xml' and option:
      if os.path.isfile(src):
        src = 'file://' + os.path.realpath(src)
      utime = 0
      content = ''
      with urlopener.urlopen(src) as urlhandle:
        utime = urlhandle.headers.get('date', urlhandle.headers.get('last-modified'))
        utime = datetime.strptime(utime, '%a, %d %b %Y %H:%M:%S %Z').timestamp()
        content = urlhandle.read()
      base_name = sha1(content.decode() if isinstance(content, bytes) else content)
      eps_name = os.path.join(imagedir, base_name) + "." + option
      try:
        mtime = -1
        if os.path.isfile(eps_name):
          mtime = os.path.getmtime(eps_name)
        if not os.path.isdir(imagedir):
          try:
            os.makedirs(imagedir)
          except OSError:
            sys.stderr.write('Failed to create directory ' + imagedir + '\n')
      except OSError:
        mtime = -1
      if mtime < utime:
        import shlex
        cmd_line = shlex.split('rsvg-convert --format='+option+' --output '+eps_name+' /dev/stdin')
        sys.stderr.write("Running %s\n" % " ".join(cmd_line))
        runCommand(cmd_line, logpath=os.getcwd(), filename=os.path.basename(eps_name), stdincontent=content)
      return Image([_id, _classes, _keyvallists], [alt], [eps_name, title])
  return None

if __name__ == "__main__":
  toJSONFilter(svg_to_any)
