"""tesseract.py

Utility script to create the text documents and alignments of the EAST view in
the example.

"""

from utils import print_annotation


# These are lined up in order of the bounding boxes from EAST. Notice the
# repetition reflecting that identical bounding boxes form three time points
text_values = [
    'DATE', '1982-05-12', 'TITLE', 'Loud Dogs', 'HOST', 'Jim Lehrer', 'PROD', 'Sara Just',
    'DATE', '1982-05-12', 'TITLE', 'Loud Dogs', 'HOST', 'Jim Lehrer', 'PROD', 'Sara Just',
    'DATE', '1982-05-12', 'TITLE', 'Loud Dogs', 'HOST', 'Jim Lehrer', 'PROD', 'Sara Just',
    'Dog in New York' ]


if __name__ == '__main__':

    count = 0
    for text in text_values:
        count += 1
        box_id = 'v5:bb%s' % count
        text_id = 'td%s' % count
        align_id = 'a%s' % count
        print_annotation(
            "http://mmif.clams.ai/0.2.0/vocabulary/TextDocument",
            [('id', text_id),
             ('text-@value', text)])
        print_annotation(
            "http://mmif.clams.ai/0.2.0/vocabulary/Alignment",
            [('id', align_id),
             ('source', box_id),
             ('target', text_id)])
