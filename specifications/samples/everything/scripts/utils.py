
def print_annotation(attype, properties):
    print("        {")
    print('          "@type": "%s",' % attype)
    print('          "properties": {')
    for prop, value in properties[:-1]:
        print_property(prop, value)
    for prop, value in properties[-1:]:
        print_property(prop, value, last=True)
    print("        },")


def print_property(prop, value, last=False):
    eol = ' }' if last else ','
    if type(value) in (int, list):
        print('            "%s": %s%s' % (prop, value, eol))
    elif prop == 'text-@value':
        print('            "text": { "@value": "%s" }%s' % (value, eol))
    else:
        print('            "%s": "%s"%s' % (prop, value, eol))
