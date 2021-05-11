"""pbcore.py

Script to experiment with exporting information from a MMIF file into PBCore.

See ../pbcore.md for a description.

"""

import sys
import json


CONTRIBUTOR_TYPES = ('Host', 'Producer')
TITLE_TYPE = 'Title'
DATE_TYPE = 'Date'

TAG_TYPE = 'http://vocab.lappsgrid.org/SemanticTag'

ENTITY_TYPE = 'http://vocab.lappsgrid.org/NamedEntity'
ENTITY_CATEGORY = 'Person'


class MMIF(object):

    """Simplistic MMIF class, will be deprecated when the MMIF SDK is stable."""
    
    def __init__(self, fname):
        self.json = json.load(open(infile))
        self.metadata = self.json['metadata']
        self.documents = self.json['documents']
        self.views = [View(self, view) for view in self.json['views']]

    def get_view(self, view_id):
        for view in self.views:
            if view.id == view_id:
                return view
    

class View(object):

    def __init__(self, mmif, json_obj):
        self.mmif = mmif
        self.id = json_obj['id']
        self.metadata = json_obj['metadata']
        self.annotations = [Annotation(self, anno) for anno in json_obj['annotations']]

    def __str__(self):
        return "<View %s %s>" % (self.id, self.metadata['app'])

    def get_document(self, annotation):
        return (
            annotation.get_property('document')
            or self.metatdata['contains'][annotation.type]['document'])

    def get_entities(self):
        entities = {}
        for anno in self.annotations:
            if anno.type == ENTITY_TYPE:
                entity = anno.get_property('text')
                cat = anno.get_property('category')
                doc = self.get_document(anno)
                p1 = anno.get_property('start')
                p2 = anno.get_property('end')
                entities.setdefault(cat, {})
                entities[cat].setdefault(entity, []).append((entity, doc, p1, p2, anno, anno))
        return entities

    def get_persons(self):
        persons = []
        for anno in self.annotations:
            if (anno.type == ENTITY_TYPE
                and anno.get_property('category') == ENTITY_CATEGORY):
                persons.append(anno)
        return persons

    def get_contributors(self):
        """Pull all contributors from the slate parser view."""
        contributors = {}
        for anno in self.annotations:
            tagname = anno.get_property('tagName')
            if anno.type == TAG_TYPE and tagname in CONTRIBUTOR_TYPES:
                contributors.setdefault(tagname, set()).add(anno.get_property('text'))
        return contributors


class Annotation(object):

    def __init__(self, view, json_obj):
        self.view = view
        self.type = json_obj['@type']
        self.id = json_obj['properties']['id']
        self.properties = json_obj['properties']

    def get_property(self, prop):
        return self.properties.get(prop)


def print_entities(entities):
    for cat in entities:
        for entity in entities[cat]:
            print("%-16s%-15s" % (cat, entity), end='')
            for spec in entities[cat][entity]:
                anchor = "%s-%s-%s" % (spec[1], spec[2], spec[3])
                print(anchor, end=' ')
            print()


if __name__ == '__main__':

    infile = sys.argv[1]
    mmif = MMIF(infile)

    bt_view = mmif.get_view("v1")
    ner_view = mmif.get_view("v7")
    tags_view = mmif.get_view("v8")

    print(bt_view)
    print(ner_view)
    print(tags_view)
    
    entities = ner_view.get_entities()
    persons = ner_view.get_persons()
    #locations = ner_view.get_locations()
    
    contributors = tags_view.get_contributors()
    #date = tags_view.get_date()
    #title = tags_view.get_date()

    print_entities(entities)

    print(persons)
    print(contributors)
