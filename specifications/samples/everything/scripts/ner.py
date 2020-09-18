"""ner.py

Utility script to create the named entities of the NER view in the example.

"""

from utils import print_annotation


# Entities from the text documents, again some repetition.
entities = [
    ('1982-05-12', 'Date', 'v6:td2'),
    ('Jim Lehrer', 'Person', 'v6:td6'),
    ('Sara Just', 'Person', 'v6:td8'),
    ('1982-05-12', 'Date', 'v6:td10'),
    ('Jim Lehrer', 'Person', 'v6:td14'),
    ('Sara Just', 'Person', 'v6:td16'),
    ('1982-05-12', 'Date', 'v6:td18'),
    ('Jim Lehrer', 'Person', 'v6:td22'),
    ('Sara Just', 'Person', 'v6:td24'),
    ('New York', 'Location', 'v6:td24', 7, 15),
    ('Jim Lehrer', 'Person', 'v4:td1', 15, 25),
    ('PBS', 'Organization', 'v4:td1', 47, 50) ]


if __name__ == '__main__':

    count = 0
    for entity in entities:
        count += 1
        ner_id = 'ne%s' % count
        text = entity[0]
        cat = entity[1]
        document = entity[2]
        if len(entity) == 5:
            start = entity[3]
            end = entity[4]
        else:
            start = 0
            end = len(text)
        print_annotation(
            "http://vocab.lappsgrid.org/NamedEntity",
            [('id', ner_id),
             ('document', document),
             ('start', start),
             ('end', end),
             ('category', cat),
             ('text', text)])
