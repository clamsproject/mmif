# TODO (krim @ 10/7/2018): reimplement with proper enum
class AnnotationTypes(object):
    FA = "https://vocab.clams.ai/attype/forced-alignment"
    # FFA = "filtered-forced-alignment"
    BD = "https://vocab.clams.ai/attype/bar-detection"
    SD = "https://vocab.clams.ai/attype/slate-detection"
    TD = "https://vocab.clams.ai/attype/tone-detection"
    ND = "https://vocab.clams.ai/attype/noise-detection"
    OCR = "https://vocab.clams.ai/attype/raw-ocr-output"
    TBOX = "https://vocab.clams.ai/attype/text-box"
    FACE = "https://vocab.clams.ai/attype/face-box"
    SHOT = "https://vocab.clams.ai/attype/shot-detection"
    # TODO linguistic annotations to leverage on the LAPPS/LIF vocab
    # Sentences = "segment-sentences"
    # Paragraphs = "segment-paragraphs"
    # Tokens = "segment-tokens"


class MediaTypes(object):
    V = "https://vocab.clams.ai/mtype/audio-video"
    A = "https://vocab.clams.ai/mtype/audio-only"
    T = "https://vocab.clams.ai/mtype/text"
    I = "https://vocab.clams.ai/mtype/image"

