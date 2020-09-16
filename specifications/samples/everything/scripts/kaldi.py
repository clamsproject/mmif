"""kaldi.py

Utility script to create the tokens, time frames and alignments of the Kaldi
view in the example.

"""


tokens = "Hello, this is Jim Lehrer with the NewsHour on PBS. In the nineteen eighties, barking dogs have increasingly become a problem in urban areas.".split()

offset = 0

token_annotations = []
timeframe_annotations = []


text_offset_range = (0, 141)
timeframe_offset_range = (5500, 22000)

step = int((22000 - 5500) / 141)

for token in tokens:
    if token[-1] in ',.':
        token1 = token[:-1]
        token2 = token[-1]
        token_annotations.append((offset, offset + len(token) - 1, token1))
        token_annotations.append((offset + len(token) - 1, offset + len(token), token2))
    else:
        token_annotations.append((offset, offset + len(token), token))
    offset += len(token) + 1

token_id = 0
for p1, p2, token in token_annotations:
    token_id += 1
    #print(p1, p2, token)
    print("\t\t\t\t{")
    print('\t\t\t\t\t"@type": "http://vocab.lappsgrid.org/Token",')
    print('\t\t\t\t\t"properties: {')
    print('\t\t\t\t\t\t"id": "t%d",' % token_id)
    print('\t\t\t\t\t\t"start": "%s",' % p1)
    print('\t\t\t\t\t\t"end": "%s",' % p2)
    print('\t\t\t\t\t\t"text": "%s" }' % token)
    print("\t\t\t\t},")
    print("\t\t\t\t{")
    print('\t\t\t\t\t"@type": "http://mmif.clams.ai/0.2.0/vocabulary/TimeFrame",')
    print('\t\t\t\t\t"properties: {')
    print('\t\t\t\t\t\t"id": "tf%d",' % token_id)
    print('\t\t\t\t\t\t"start": "%s",' % (5500 + p1 * step))
    print('\t\t\t\t\t\t"end": "%s" }' % (5500 + p2 * step))
    print("\t\t\t\t},")
    print("\t\t\t\t{")
    print('\t\t\t\t\t"@type": "http://mmif.clams.ai/0.2.0/vocabulary/Alignment",')
    print('\t\t\t\t\t"properties: {')
    print('\t\t\t\t\t\t"id": "a%d",' % (token_id + 1))
    print('\t\t\t\t\t\t"source": "tf%s",' % token_id)
    print('\t\t\t\t\t\t"target": "t%s" }' % token_id)
    print("\t\t\t\t},")

