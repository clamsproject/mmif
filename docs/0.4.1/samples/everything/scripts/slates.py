"""slates.py

Utility script to create the semantic tags of the slate parser view in the
example.

"""

from utils import print_annotation


# Tags from the text documents for the slates, again some repetition. Very
# similar to the named entities, but with the title added and non-slate entities
# removed.
tags = [
    ('1982-05-12', 'Date', 'v6:td2'),
    ('Loud Dogs', 'Title', 'v6:td4'),
    ('Jim Lehrer', 'Host', 'v6:td6'),
    ('Sara Just', 'Producer', 'v6:td8'),
    ('1982-05-12', 'Date', 'v6:td10'),
    ('Loud Dogs', 'Title', 'v6:td12'),
    ('Jim Lehrer', 'Host', 'v6:td14'),
    ('Sara Just', 'Producer', 'v6:td16'),
    ('1982-05-12', 'Date', 'v6:td18'),
    ('Loud Dogs', 'Title', 'v6:td20'),
    ('Jim Lehrer', 'Host', 'v6:td22'),
    ('Sara Just', 'Producer', 'v6:td24') ]


if __name__ == '__main__':

    count = 0
    for tag in tags:
        count += 1
        tag_id = 'st%s' % count
        text, cat, document = tag
        start = 0
        end = len(text)
        print_annotation(
            "http://vocab.lappsgrid.org/SemanticTag",
            [('id', tag_id),
             ('document', document),
             ('start', start),
             ('end', end),
             ('tagName', cat),
             ('text', text)])
