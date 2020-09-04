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
branch then the site at http://mmif.clams.ai/VERSION/vocabulary will be
automatically updated.

This requires BeautifulSoup as well as the lxml parser

$ pip install bs4, lxml

"""


import os
import sys
import shutil
import time
import yaml

from glob import glob
from bs4 import BeautifulSoup
from string import Template


VERSION = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'VERSION')).read().strip()

VOCABULARY_URL = 'http://mmif.clams.ai/%s/vocabulary' % VERSION

INCLUDE_CONTEXT = False


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
        self._add_stylesheet()

    def _add_stylesheet(self):
        add_stylesheet(self.soup, self.stylesheet)

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
        if not os.path.exists(self.fpath):
            os.mkdir(self.fpath)
        with open(self.fname, 'w') as fh:
            fh.write(increase_leading_space(self.soup.prettify()))


class IndexPage(Page):

    def __init__(self, tree, outdir, version):
        self.stylesheet = 'css/lappsstyle.css'
        super().__init__(outdir, version)
        self.fpath = outdir
        self.fname = os.path.join(outdir, 'index.html')
        self.tree = tree
        self._add_title('CLAMS Vocabulary')
        self._add_main_structure()
        self._add_header()
        self._add_description()
        self._add_tree(self.tree.root, self.main_content)
        self._add_space()
        #self._add_ontologies()
        #self._add_space()
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
        fname = '%s' % type_name
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

    def _add_ontologies(self):
        onto_soup = BeautifulSoup("""
      <p>The vocabulary is available in the following formats:
          <a href='ontologies/clams.vocabulary.rdf'>RDF</a>,
          <a href='ontologies/clams.vocabulary.owl'>OWL</a>,
          <a href='ontologies/clams.vocabulary.jsonld'>JSONLD</a> and
          <a href='ontologies/clams.vocabulary.ttl'>TTL</a>.</p>""", features="lxml")
        for element in onto_soup.body:
            self.main_content.append(element)


class TypePage(Page):

    def __init__(self, clams_type, outdir, version):
        self.stylesheet = '../css/lappsstyle.css'
        super().__init__(outdir, version)
        self.clams_type = clams_type
        self.name = clams_type['name']
        self.description = clams_type['description']
        self.metadata = clams_type.get('metadata', [])
        self.properties = clams_type.get('properties', [])
        self.fpath = os.path.join(outdir, self.name)
        self.fname = os.path.join(outdir, self.name, 'index.html')
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
                dtrs=[tag('p', dtrs=[HREF('../index.html', 'Home')])]))

    def _add_head(self):
        chain = reversed(self._chain_to_top())
        dtrs = []
        for n in chain:
            dtrs.append(HREF("../%s" % n['name'], n['name']))
            dtrs.append(SPAN('>'))
        dtrs.append(SPAN(self.name))
        p = tag('p', {'class': 'head'}, dtrs=dtrs)
        self.main_content.append(p)
        self._add_space()

    def _add_definition(self):
        url = '%s/%s' % (VOCABULARY_URL, self.name)
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
    """Hack to double the indentation since I didn't like the single character
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


def compile_index_md(source_md, target_dir):
    source_md_f = open(source_md, 'r')
    #  print(source_md_f.read())
    tmpl_to_compile = Template(source_md_f.read())
    compiled = tmpl_to_compile.substitute(VERSION=VERSION)
    source_md_f.close()
    compiled_md_f = open(os.path.join(target_dir, 'index.md'), 'w') 
    compiled_md_f.write(compiled)
    compiled_md_f.close()


def setup(out_dir, vocab_dir, schema_dir, context_dir):
    """Copy non-vocabulary files to theoutput directory."""
    css_dir = os.path.join(vocab_dir, 'css')
    if not os.path.exists(css_dir):
        os.makedirs(css_dir)
    shutil.copy('lappsstyle.css', css_dir)
    compile_index_md('../specifications/index.md', out_dir)
    shutil.copy('../specifications/pi78oGjdT.jpg', out_dir)
    shutil.copy('../specifications/pi78oGjdT-annotated.jpg', out_dir)
    samples_in = '../specifications/samples'
    samples_out = os.path.join(out_dir, 'samples')
    shutil.copytree(samples_in, os.path.join(out_dir, 'samples'))
    # these are probably even obsolete, so don't publish them
    for fname in (glob(samples_out + '/image*')
                  + glob(samples_out + '/video*')
                  + glob(samples_out + '/slate*')):
        os.remove(fname)
    if not os.path.exists(schema_dir):
        os.makedirs(schema_dir)
    shutil.copy('../schema/lif.json', schema_dir)
    shutil.copy('../schema/mmif.json', schema_dir)
    if INCLUDE_CONTEXT:
        if not os.path.exists(context_dir):
            os.makedirs(context_dir)
        shutil.copy('../context/mmif.json', context_dir)
        shutil.copy('../context/vocab-clams.json', context_dir)
        shutil.copy('../context/vocab-lapps.json', context_dir)
        compile_index_md('../context/index.md', context_dir)


if __name__ == '__main__':
    out_dir =  os.path.join('..', 'docs', VERSION)
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        out_dir = 'www'
    shutil.rmtree(out_dir, ignore_errors=True)
    os.mkdir(out_dir)
    vocab_dir = os.path.join(out_dir, 'vocabulary')
    schema_dir = os.path.join(out_dir, 'schema')
    context_dir = os.path.join(out_dir, 'context')
    print("\n>>> Creating directory structure in '%s'" % out_dir)
    print(">>> Copying non-vocabulary files to '%s'" % out_dir)
    setup(out_dir, vocab_dir, schema_dir, context_dir)
    print(">>> Adding vocabulary pages to '%s'\n" % vocab_dir)
    clams_types = read_yaml("clams.vocabulary.yaml")
    tree = Tree(clams_types)
    write_hierarchy(tree, vocab_dir, VERSION)
    write_pages(tree, vocab_dir, VERSION)
