# Models of discourse coherence

* entity-based

* syntax-based


### *doctext*: documents in plain text format

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

You can also use it directly to put together a bunch of plain text docouments (1 document per file) into a single `doctext`.

    cat list_of_files.txt | python doctext.py > corpus.doctext


### *docsgml*: documents in SGML style

The following format is used to keep several documents in a single XML-formatted file. XML can complicate things sometimes, so use with care ;)

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

