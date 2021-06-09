"""kaldi.py

Utility script to create the tokens, time frames and alignments of the Kaldi
view in the example.

"""

from utils import print_annotation


TOKENS = "Hello, this is Jim Lehrer with the NewsHour on PBS. In the nineteen eighties, barking dogs have increasingly become a problem in urban areas.".split()


# Calculating time offsets from text offsets
FIRST_TEXT_OFFSET = 0
LAST_TEXT_OFFSET = 141
FIRST_TIME_OFFSET = 5500
LAST_TIME_OFFSET = 22000
STEP = int((LAST_TIME_OFFSET - FIRST_TIME_OFFSET) / LAST_TEXT_OFFSET)


def gather_annotations():
    offset = 0
    token_annotations = []
    for token in TOKENS:
        if token[-1] in ',.':
            token_annotations.append((offset, offset + len(token) - 1, token[:-1]))
            token_annotations.append((offset + len(token) - 1, offset + len(token), token[-1]))
        else:
            token_annotations.append((offset, offset + len(token), token))
        offset += len(token) + 1
    return token_annotations


if __name__ == '__main__':

    count = 0
    for p1, p2, token in gather_annotations():
        count += 1
        token_id = 't%s' % count
        frame_id = 'tf%s' % count
        align_id = 'a%s' % (count + 1)
        frame_p1 = FIRST_TIME_OFFSET + p1 * STEP
        frame_p2 = FIRST_TIME_OFFSET + p2 * STEP
        print_annotation(
            "http://vocab.lappsgrid.org/Token",
            [('id', token_id), ('start', p1), ('end', p2), ('text', token)])
        print_annotation(
            "http://mmif.clams.ai/0.2.0/vocabulary/TimeFrame",
            [('id', frame_id), ('start', frame_p1), ('end', frame_p2)])
        print_annotation(
            "http://mmif.clams.ai/0.2.0/vocabulary/Alignment",
            [('id', align_id), ('source', frame_id), ('target', token_id)])
