"""publish.py

Script to create webpages from a YAML file with the vocabulary.

Usage:

$ python publish.py
$ python publish.py --test

This takes the vocabulary specifications in clams.vocabulary.yaml and write
webpages to ../docs/VERSION/vocabulary. The actual version is taken from the
VERSION file in the top-level directory of this repository. If the output
directory exists then files in it will be overwritten.

With the --test option files will be written to www in this directory.

When you use the default output directory and merge changes into the master
branch then the site at http://miff.clams.ai/vocabulary will be automatically
updated.

"""


import os
import sys
import shutil
import time
import yaml

from bs4 import BeautifulSoup


VERSION = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'VERSION')).read().strip()
VOCABULARY_URL = 'http://mmif.clams.ai/%s/vocabulary' % VERSION


def read_yaml(fname):
    """Read a YAML file and return a list of Python dictionaries, one for each
    document in the YAML file."""
    stream = open(fname, 'r')
    docs = [doc for doc in yaml.safe_load_all(stream)]
    return docs


def get_soup():
    """Return a basic top-level soup."""
    return BeautifulSoup("<html>" +
                         "<head></head>" +
                         "<body></body>" +
                         "</html>",
                         features='lxml')


def tag(tagname, attrs=None, text=None, dtrs=None):
    """Return a soup Tag element."""
    attrs = {} if attrs is None else attrs
    dtrs = [] if dtrs is None else dtrs
    newtag = BeautifulSoup('', features='lxml').new_tag(tagname, attrs=attrs)
    if text is not None:
        newtag.append(text)
    for dtr in dtrs:
        newtag.append(dtr)
    return newtag


def add_stylesheet(soup, stylesheet):
    soup.head.append(tag('link', {'rel': 'stylesheet',
                                  'type': 'text/css',
                                  'href': stylesheet}))


def DIV(attrs=None, text=None, dtrs=None):
    return tag('div', attrs=attrs, text=text, dtrs=dtrs)


def TABLE(attrs=None, dtrs=None):
    return tag('table', attrs=attrs, dtrs=dtrs)


def TABLE_ROW(table_cells):
    return tag('tr', dtrs=table_cells)


def H1(text):
    return tag('h1', text=text)


def H2(text):
    return tag('h2', text=text)


def HREF(link, text):
    return tag('a', attrs={'href': link}, text=text)


def SPAN(text):
    return tag('span', text=text)


class Tree(object):

    def __init__(self, clams_types):
        """Take the generator object and put a dictionary"""
        self.types = clams_types
        self.types_idx = { t['name']: t for t in self.types }
        self.tree = []
        self.root = self.find_root()
        self.build_tree()

    def find_root(self):
        for t in self.types:
            if t['parent'] is None:
                return t

    def build_tree(self):
        """Add links between all the type definitions by filling in parentNode
        and childNodes attributes."""
        # First initialize the dominance links and then populate them
        for t in self.types:
            t['parentNode'] = None
            t['childNodes'] = []
        for t in self.types:
            parentName = t['parent']
            if parentName is not None:
                parentNode = self.types_idx.get(parentName)
                t['parentNode'] = parentNode
                parentNode.setdefault('childNodes', []).append(t)

    def print_tree(self, node, level=0):
        print("%s%s" % ('  ' * level, node['name']))
        for child in node['childNodes']:
            self.print_tree(child, level + 1)


def write_hierarchy(tree, outdir, version):
    IndexPage(tree, outdir, version).write()


def write_pages(tree, outdir, version):
    for clams_type in tree.types:
        TypePage(clams_type, outdir, version).write()



class Page(object):

    def __init__(self, outdir, version):
        self.outdir = outdir
        self.version = version
        self.soup = get_soup()
        # the following three will be set by _add_main_structure()
        self.container = None
        self.intro = None
        self.main_content = None
        self._add_stylesheet('css/lappsstyle.css')

    def _add_stylesheet(self, stylesheet):
        add_stylesheet(self.soup, stylesheet)

    def _add_title(self, title):
        self.soup.head.append(tag('title', text=title))

    def _add_header(self):
        title = 'CLAMS Vocabulary'
        version = 'version %s' % self.version
        header = DIV({'id': 'pageHeader'},
                     dtrs=[H1(title),
                           H2(version)])
        self.intro.append(header)

    def _add_main_structure(self):
        """Build the basic structure of the body, which is a container div with
        in it an intro div and a mainContent div."""
        container = DIV({'id': 'container'},
                        dtrs=[DIV({'id': 'intro'}),
                              DIV({'id': 'mainContent'})])
        self.soup.body.append(container)
        self.container = container
        self.intro = self.soup.find(id='intro')
        self.main_content = self.soup.find(id='mainContent')

    def _add_footer(self):
        footer = 'Page generated on %s' % time.strftime("%Y-%m-%d at %H:%M:%S")
        self.soup.body.append(DIV({'id': 'footer'}, text=footer))

    def _add_space(self):
        self.main_content.append(tag('br'))

    def write(self):
        with open(self.fname, 'w') as fh:
            fh.write(increase_leading_space(self.soup.prettify()))


class IndexPage(Page):

    def __init__(self, tree, outdir, version):
        super().__init__(outdir, version)
        self.fname = os.path.join(outdir, 'index.html')
        self.tree = tree
        self._add_title('CLAMS Vocabulary')
        self._add_main_structure()
        self._add_header()
        self._add_description()
        self._add_tree(self.tree.root, self.main_content)
        self._add_space()
        self._add_footer()

    def _add_description(self):
        span1_text = "The CLAMS Vocabulary defines an ontology" \
                     + " of terms for a core of objects and features exchanged" \
                     + " amongst tools that process multi-media data. It is based" \
                     + " on the LAPPS Web Service Exchange Vocabulary at "
        span2_text = "The vocabulary is being developed bottom-up on an as-needed" \
                     + " basis for use in the development of the CLAMS platform."
        span3_text = "In the hierarchy below annotation types are printed with the" \
                     " properties defined for them, metadata properties are printed" \
                     " between square brackets."
        url = 'http://vocab.lappsgrid.org'
        p1 = tag('p', dtrs=[SPAN(text=span1_text),
                            HREF(url, url + '.'),
                            SPAN(text=span2_text),
                            SPAN(text=span3_text)])
        self.main_content.append(p1)
        self._add_space()

    def _add_tree(self, clams_type, soup_node):
        type_name = clams_type['name']
        fname = '%s.html' % type_name
        link = HREF(fname, type_name)
        name_cell = tag('td', {'class': 'tc', 'colspan': 4})
        name_cell.append(link)
        if 'metadata' in clams_type:
            properties = ', '.join(clams_type['metadata'].keys())
            name_cell.append(SPAN(text=": [" + properties + ']'))
        if 'properties' in clams_type:
            properties = ', '.join(clams_type['properties'].keys())
            name_cell.append(SPAN(text=": " + properties))
        sub_cell = tag('td')
        table = TABLE({'class': 'h'})
        row1 = TABLE_ROW([name_cell])
        row2 = TABLE_ROW([tag('td', {'class': 'space'}),
                          tag('td', {'class': 'bar'}),
                          tag('td', {'class': 'space'}),
                          sub_cell])
        table.extend([row1, row2])
        soup_node.append(table)
        for subtype in clams_type['childNodes']:
            self._add_tree(subtype, sub_cell)


class TypePage(Page):

    def __init__(self, clams_type, outdir, version):
        super().__init__(outdir, version)
        self.clams_type = clams_type
        self.name = clams_type['name']
        self.description = clams_type['description']
        self.metadata = clams_type.get('metadata', [])
        self.properties = clams_type.get('properties', [])
        self.fname = os.path.join(outdir, '%s.html' % self.name)
        self._add_title(self.name)
        self._add_main_structure()
        self._add_header()
        self._add_home_button()
        self._add_head()
        self._add_definition()
        self._add_metadata()
        self._add_properties()
        self._add_space()
        self._add_footer()

    def _chain_to_top(self):
        chain = []
        parent = self.clams_type['parentNode']
        while parent is not None:
            chain.append(parent)
            parent = parent['parentNode']
        return chain

    def _add_home_button(self):
        self.main_content.append(
            DIV({'id': 'sectionbar'},
                dtrs=[tag('p', dtrs=[HREF('index.html', 'Home')])]))

    def _add_head(self):
        chain = reversed(self._chain_to_top())
        dtrs = []
        for n in chain:
            dtrs.append(HREF("%s.html" % n['name'], n['name']))
            dtrs.append(SPAN('>'))
        dtrs.append(SPAN(self.name))
        p = tag('p', {'class': 'head'}, dtrs=dtrs)
        self.main_content.append(p)
        self._add_space()

    def _add_definition(self):
        url = '%s/%s.html' % (VOCABULARY_URL, self.name)
        table = TABLE(dtrs=[TABLE_ROW([tag('td', {'class': 'fixed'},
                                           dtrs=[tag('b', text='Definition')]),
                                       tag('td', text=self.description)]),
                            TABLE_ROW([tag('td', dtrs=[tag('b', text='URI')]),
                                       tag('td', dtrs=[HREF(url, url)])])])
        self.main_content.append(table)

    def _add_metadata(self):
        self.main_content.append(H1('Metadata'))
        if self.metadata:
            self._add_properties_aux(self.metadata)
        self._add_properties_from_chain('metadata')

    def _add_properties(self):
        self.main_content.append(H1('Properties'))
        if self.properties:
            self._add_properties_aux(self.properties)
        self._add_properties_from_chain('properties')

    def _add_properties_from_chain(self, proptype):
        for n in self._chain_to_top():
            properties = n.get(proptype, None)
            if properties is not None:
                h2 = H2("%s from %s" % (proptype.capitalize(), n['name']))
                self.main_content.append(h2)
                self._add_properties_aux(properties)

    def _add_properties_aux(self, properties):
        if properties:
            th1 = tag('th', {'class': 'fixed'}, text='Property')
            th2 = tag('th', {'class': 'fixed'}, text='Type')
            th3 = tag('th', text='Description')
            table = TABLE({'class': 'definition-table'},
                          dtrs=[TABLE_ROW([th1, th2, th3])])
            for prop in properties:
                val = properties[prop]
                prop_type = val['type']
                prop_description = val.get('description', '')
                prop_required = val.get('required', False)
                description_cell = tag('td', {}, prop_description)
                if prop_required:
                    req = tag('span', {'class': 'required'}, text='[Required]')
                    description_cell.append(req)
                row = TABLE_ROW([tag('td', {}, prop),
                                 tag('td', {}, prop_type),
                                 description_cell])
                table.append(row)
            self.main_content.append(table)


def increase_leading_space(text):
    """Hack to double the indentation since didn't like the single character
    indent in bs4 and there is apparently no way to change that."""
    # TODO: there are other minor problems with the bs4 pretty print
    # TODO: find another way to take that string and pretty print it
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        for i, char in enumerate(line):
            if char != ' ':
                new_lines.append("%s%s" % (' ' * i, line))
                break
    return '\n'.join(new_lines)


def setup(outdir):
    css_dir = os.path.join(outdir, 'css')
    if not os.path.exists(css_dir):
        os.makedirs(css_dir)
    shutil.copy('lappsstyle.css', css_dir)



if __name__ == '__main__':

    outdir =  os.path.join('..', 'docs', VERSION, 'vocabulary')
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        outdir = 'www'
    setup(outdir)
    print("Creating webpages in '%s'" % outdir)
    clams_types = read_yaml("clams.vocabulary.yaml")
    tree = Tree(clams_types)
    write_hierarchy(tree, outdir, VERSION)
    write_pages(tree, outdir, VERSION)
