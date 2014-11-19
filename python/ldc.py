"""
This module implements some helper functions to deal with LDC files.

@author waziz
"""
import re
import os

# regex to decompose LDC file names
_LDC_NAME_RE_ = re.compile('([a-z]+)_([a-z]+)_([0-9]{4})([0-9]{2})')

def ldc_name_re():
    return _LDC_NAME_RE_


def get_ldc_name(path):
    """returns the LDC name of the file without the parent directory and without extension"""
    return os.path.splitext(os.path.basename(path))[0]


def parse_ldc_name(ldc_name):
    """
    Parses an LDC file name and returns a dictionary with info
    Usages: 
        parse_ldc_name('afp_eng_201202') 
        parse_ldc_name(get_ldc_name('/home/waziz/ldc/files/afp_eng_201202.gz')) 
    """
    corpus, lang, year, month = ldc_name_re().match(ldc_name).groups()
    return {'corpus': corpus, 'language': lang, 'year': year, 'month': month, 'name': ldc_name}


def parse_ldc_name_from_path(path):
    return parse_ldc_name(get_ldc_name(path))


def writetxtdoc(lines, out, **kwargs):
    attr_str = ' '.join('{0}={1}'.format(k, v) for k, v in kwargs.iteritems())
    print >> out, '# %s' % attr_str
    for line in lines:
        if line:
            print >> out, line
    print >> out

def itertxtdocs(istream):
    attrs = None
    content = None
    for line in istream:
        line = line.strip()
        if line.startswith('#'):
            line = line.replace('#', '')
            attrs = {k:v for k, v in [kv.split('=') for kv in line.split()]}
            content = []
        elif line and content is not None:
            content.append(line)
        elif content is not None:
            yield content, attrs
            content = None
            attrs = None
    if content is not None:
        yield content, attrs
