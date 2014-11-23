"""
This module implements a fast SGML parser using xml.parsers.expat.
It quickly collects the text content under a certain XML tag in a document.
It deals with multiple documents in a single XML file.

In addition, it implements a wrapper to mini dom that eases the creation of simple 
sgml-formatted document container files.

@author waziz
"""
import gzip
import xml.parsers.expat
from xml.dom.minidom import getDOMImplementation
from xml.sax.saxutils import escape, unescape
from functools import partial

class TextFromSGML(object):

    def __init__(self, content, text_under, root=None):
        """
        Parses the XML content of a file.
        :param str content: XML content
        :param str text_under: tag name under which we will find text (e.g. doc, text)
        :param str root: if not None, it is interpreted as the single root tag name to be added to the XML content
        """
        assert text_under is not None, 'You need to specify a text tag'
        parser = xml.parsers.expat.ParserCreate()
        # parser state
        state = {}
        # parsed documents
        state['documents'] = []
        # temporary data (e.g. curent document's id, sentences and status)
        state['_id'] = None
        state['_doc'] = None
        state['_reading'] = False
        state['_text_under'] = text_under
        # handlers
        parser.StartElementHandler = partial(TextFromSGML._start_element, state=state)
        parser.EndElementHandler = partial(TextFromSGML._end_element, state=state)
        parser.CharacterDataHandler = partial(TextFromSGML._char_data, state=state)
        # add root if necessary
        if root is None:
            parser.Parse(content, 1)
        else:
            parser.Parse('<{0}>{1}</{0}>'.format(root, content), 1)
        # store parser's state
        self._state = state

    def iterdocs(self):
        """Iterates over documents in a given sgm file -> {'id':doc_id, 'data':doc_sentences}"""
        for did, doc in self._state['documents']:
            yield {'id': did, 'text':'\n'.join(doc)}

    @staticmethod
    def _start_element(name, attrs, state):
        """starts a document"""
        if name.lower() == 'doc':
            state['_doc'] = []
            state['_id'] = attrs['id']
        if state['_text_under'].lower() == name.lower():
            state['_reading'] = True

    @staticmethod
    def _end_element(name, state):
        """ends a document"""
        if name.lower() == 'doc':
            state['documents'].append((state['_id'], state['_doc']))
            state['_doc'] = None
            state['_id'] = None
        if state['_text_under'].lower() == name.lower():
            state['_reading'] = False

    @staticmethod
    def _char_data(txt_data, state):
        """stores non blank lines in a document"""
        if state['_reading']:
            # encode utf-8 into a python string
            line = txt_data.encode('utf-8').strip()
            if line:
                state['_doc'].append(line)


class MakeSGMLDocs(object):

    def __init__(self, **kwargs):
        self._dom = getDOMImplementation()
        self._docs = self._dom.createDocument(None, 'docs', None)
        for k, v in kwargs.iteritems():
            self._docs.documentElement.setAttribute(k, v)

    def add(self, doc_text, **kwargs):
        doc = self._docs.createElement('doc')
        for k, v in kwargs.iteritems():
            doc.setAttribute(k, v)
        # decode python strings into utf-8
        doc.appendChild(self._docs.createTextNode(doc_text.decode('utf-8')))
        self._docs.documentElement.appendChild(doc)

    def writegz(self, path):
        if not path.endswith('.gz'):
            path += '.gz'
        with gzip.open(path, 'wb') as fout:
            # returns utf-8 encoded into python string
            fout.write(self._docs.toprettyxml(encoding='utf-8'))
