# Models of discourse coherence

* entity-based

* syntax-based


# The toolkit

Most of our code uses a simple plain text format to represent documents (see [`doctext`](##doctext)).
There is code for a bunch of things, you should check subpackages' README files.

# File formats

* [*doctext*](##doctext) multiple documents in a single text file
* [*docsgml*](##docsgml) SGML container for multiple LDC documents

## doctext

The following format will be used to keep several documents (without loosing document boundaries) in a single text file.

``` text
# id=ldc_doc_1
CONTENT

# id=ldc_doc_2
CONTENT
```

For this to work there is a simple constraint: ***the content cannot contain blank lines***.
One can also store other key-value pairs in the header if one wishes.

The module `doctext` contains helper functions to read and write in this format:

```python
from doctext import writedoctext, iterdoctext
import sys

for lines, attributes in iterdoctext(sys.stdin):
  writedoctext(sys.stdout, lines, **attributes)

```

You can easily put together a bunch of plain text docouments (1 document per file) into a single `doctext`.

    cat list_of_files.txt | python -m discourse.doctext > corpus.doctext

You can also quite easily convert from WMT SGML format to `doctext`.

    python -m discourse.docsgml < newstest2013-src.de.sgml > docs/newstest2013-src.de.doctext

Note that WMT files are not well-formatted XML files, because of that `discourse.docsgml` does not really parse WMT files using an XML parser, instead it uses a set of WMT-specific regular expressions.

## docsgml

LDC files can be processed into a simpler SGML container `discouse.docsgml`.
The *simpler* container remembers only document boundaries (as shown below) and nothing else.

``` xml
<docs filte="ldc_name">
    <doc id="ldc_doc_1">
    CONTENT
    </doc>
    <doc id="ldc_doc_2">
    CONTENT
    </doc>
</docs>
```

The content of a document is not restricted in any way.

