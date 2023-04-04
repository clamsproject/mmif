"""

Script to collect MMIF specifications and generate source files for
publication as a github-page. Generated source files are located under
`docs/VERSION` directory where the actual version is taken from the `VERSION`
file in the project root.

When you use the default output directory and merge changes into the master
branch then the site at http://mmif.clams.ai/VERSION will be automatically
created or updated.

"""
import argparse
import collections
import json
import os
import re
import shutil
import subprocess
import time
import urllib.error
import warnings
from os.path import join as pjoin
from string import Template
from urllib import request

import yaml
from bs4 import BeautifulSoup

INCLUDE_CONTEXT = False
BASEURL = 'http://mmif.clams.ai'
ATTYPE_VERSIONS_JSONFILENAME = 'attypeversions.json'

def read_yaml(fp):
    """Read a YAML file and return a list of Python dictionaries, one for each
    document in the YAML file."""
    if isinstance(fp, str):
        fp = open(fp, 'r')
    docs = [doc for doc in yaml.safe_load_all(fp)]
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


def format_attype_version(version):
    return str(version)


def write_hierarchy(tree: Tree, index_dir: str, version: str):
    """
    This will create three things; 
    1. the index.html page with the vocab tree
    2. redirection HTML files for each vocab types to its own versioned html page
    3. a json to keep the versions of individual vocab types that will be used in the next release cycle
    """
    IndexPage(tree, index_dir, version).write()
    for clams_type in tree.types:
        type_ver = format_attype_version(clams_type.get('version', version))
        redirect_dir = pjoin(index_dir, clams_type["name"])
        os.makedirs(redirect_dir, exist_ok=True)
        with open(pjoin(redirect_dir, 'index.html'), 'w') as redirect_page:
            # TODO (krim @ 3/14/23): this relies on assumption of the URL format, should be a better, future-proof way. 
            redirect_page.write(
                f'<head> <meta http-equiv="Refresh" content="0; URL=../../../vocabulary/{clams_type["name"]}/{type_ver}" /> </head>'
            )
    with open(pjoin(index_dir, ATTYPE_VERSIONS_JSONFILENAME), 'w') as attype_versions_jsonfile:
        json.dump({t['name']: t['version'] for t in tree.types}, attype_versions_jsonfile)
        


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
        """
        We use a MMIF version as a "CLAMS Vocabulary" version in the headers of
        1. the hierarchy page
        2. individual annotation type pages
        
        The number used in the headers will always point to the latest MMIF 
        version at the time of building even on the pages of individual types, 
        which have their own versions. Namely, a version of an annotation type 
        can be included in multiple (but all consecutive) MMIF versions, yet it 
        has only one MMIF version "printed" on its HTML version, which is the 
        largest number.
         
        For example, 
          - situation: TimeFrame/v2 is first introduced into the vocab hierarchy at MMIF/x.y.0 and stayed unchanged until it's changed in MMIF/x.y.10
          - expect 1) MMIF/x.y.[0-9]/vocabulary website all have link to the TimeFrame/v2 website
          - expect 2) the header of the TimeFrmae/v2 website always has the latest MMIF/x.y.? only
        """
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
            os.makedirs(self.fpath, exist_ok=True)
        with open(self.fname, 'w') as fh:
            fh.write(increase_leading_space(self.soup.prettify()))


class IndexPage(Page):

    def __init__(self, tree, outdir, version):
        self.stylesheet = 'css/lappsstyle.css'
        super().__init__(outdir, version)
        self.fpath = outdir
        self.fname = pjoin(outdir, 'index.html')
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
        if 'version' in clams_type:
            name_cell.append(SPAN(text=f"({format_attype_version(clams_type['version'])})"))
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

    def __init__(self, clams_type, outdir, mmif_version):
        subdirs = (clams_type['name'], format_attype_version(clams_type.get('version', mmif_version)))
        self.stylesheet = f"{'/'.join(['..'] * len(subdirs))}/css/lappsstyle.css"
        super().__init__(outdir, mmif_version)
        self.clams_type = clams_type
        self.metadata = clams_type.get('metadata', [])
        self.properties = clams_type.get('properties', [])
        self.fpath = pjoin(outdir, *subdirs)
        self.fname = pjoin(self.fpath, 'index.html')
        self.baseurl = f'{BASEURL}/vocabulary'
        self._add_title(clams_type['name'])
        self._add_main_structure()
        self._add_header()
        self._add_home_button(mmif_version)
        self._add_head(mmif_version)
        self._add_definition(mmif_version)
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

    def _add_home_button(self, mmif_version):
        self.main_content.append(
            DIV({'id': 'sectionbar'},
                dtrs=[tag('p', dtrs=[HREF(f'../../../{mmif_version}/vocabulary/index.html', 'Home')])]))

    def _add_head(self, mmif_version):
        chain = reversed(self._chain_to_top())
        dtrs = []
        for n in chain:
            uri_suffix = [n['name'], format_attype_version(n.get('version', mmif_version))]
            dtrs.append(HREF('/'.join(['..'] * len(uri_suffix) + uri_suffix), n['name']))
            dtrs.append(SPAN('>'))
        dtrs.append(SPAN(self.clams_type['name']))
        p = tag('p', {'class': 'head'}, dtrs=dtrs)
        self.main_content.append(p)
        self._add_space()

    def _add_definition(self, mmif_version):
        url = '/'.join((self.baseurl, self.clams_type['name'], format_attype_version(self.clams_type.get('version', mmif_version))))
        table = TABLE(dtrs=[TABLE_ROW([tag('td', {'class': 'fixed'},
                                           dtrs=[tag('b', text='Definition')]),
                                       tag('td', text=self.clams_type['description'])]),
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


def copy(src_dir, dst_dir, include_fnames=[], exclude_fnames=[], templating=None):
    for r, ds, fs in os.walk(src_dir):
        r = r[len(src_dir)+1:]
        for f in fs:
            if f.startswith('.') or r in exclude_fnames or f in exclude_fnames:
                continue
            elif len(include_fnames) == 0 or f in include_fnames:
                os.makedirs(pjoin(dst_dir, r), exist_ok=True)
                if templating is not None and f.endswith('.json') or f.endswith('.md'):
                    with open(pjoin(src_dir, r, f), 'r') as in_f, open(pjoin(dst_dir, r, f), 'w') as out_f:
                        tmpl_to_compile = Template(in_f.read())
                        compiled = tmpl_to_compile.substitute(
                            **templating
                        )
                        out_f.write(compiled)
                else:
                    shutil.copy(pjoin(src_dir, r, f), pjoin(dst_dir, r))


def check_version_exists(version):
    try:
        res = request.urlopen('https://api.github.com/repos/clamsproject/mmif/git/refs/tags')
        body = json.loads(res.read())
        tags = [os.path.basename(tag['ref']) for tag in body]
        if version in tags:
            raise RuntimeError(f"{version} already exists, can't overwrite an exising version.")
    except urllib.error.URLError:
        warnings.warn(f"Cannot connect to the remote repository.\n"
                      f"Now using local git tags to check version conflict.",
                      category=RuntimeWarning)
        proc = subprocess.run('git tag'.split(), cwd=os.path.abspath(os.path.dirname(__file__)), capture_output=True)
        if version in proc.stdout.decode('ascii').split('\n'):
            raise RuntimeError(f"{version} already exists, can't overwrite an exising version.")



def build(dirname, args):
    
    version = open(pjoin(dirname, 'VERSION')).read().strip()
    check_version_exists(version)
    out_dir = pjoin(dirname, args.testdir, version) if args.testdir else pjoin(dirname, 'docs', version)
    jekyll_conf_file = pjoin(dirname, 'docs', '_config.yml')
    vocab_src_dir = pjoin(dirname, 'vocabulary')
    spec_src_dir = pjoin(dirname, 'specifications')
    schema_src_dir = pjoin(dirname, 'schema')
    context_src_dir = pjoin(dirname, 'context')
    vocab_index_out_dir = pjoin(out_dir, 'vocabulary')
    # vocab items will have individual versions, thus they won't be placed in the MMIF version directory
    vocab_items_out_dir = pjoin(os.path.dirname(out_dir), 'vocabulary')
    vocab_css_out_dir = pjoin(vocab_index_out_dir, 'css')
    schema_out_dir = pjoin(out_dir, 'schema')
    context_out_dir = pjoin(out_dir, 'context')
    shutil.rmtree(out_dir, ignore_errors=True)

    print("\n>>> Creating directory structure in '%s'" % out_dir)
    os.makedirs(out_dir, exist_ok=True)

    print(">>> Building specification in '%s'" % out_dir)
    build_spec(spec_src_dir, out_dir, version)

    print(">>> Building json schema in '%s'" % out_dir)
    build_schema(schema_src_dir, schema_out_dir, version)

    if INCLUDE_CONTEXT:
        # TODO: this is actually broken
        print(">>> Building json-ld context in '%s'" % out_dir)
        build_context(context_src_dir, out_dir, version)

    print(f">>> Building vocabulary: index in {vocab_index_out_dir}, items in {vocab_items_out_dir}")
    build_vocab(vocab_src_dir, vocab_index_out_dir, version, vocab_items_out_dir)

    if args.testdir is None:
        print(">>> Updating jekyll configuration in '%s'" % jekyll_conf_file)
        update_jekyll_config(jekyll_conf_file, version)

    
def build_spec(src, dst, version):
    copy(src, dst, exclude_fnames=['next.md', 'notes', 'samples/others'], templating={'VERSION': version})


def build_schema(src, dst, version):
    copy(src, dst, include_fnames=['lif.json', 'mmif.json'])


def build_context(src, dst, version):
    copy(src, dst, exclude_fnames=['example.json'])


def build_vocab(src, index_dir, version, item_dir):
    vocab_yaml_path = os.path.relpath(pjoin(src, "clams.vocabulary.yaml"), os.path.dirname(__file__))
    for d in (index_dir, item_dir):
        css_dir = pjoin(d, 'css')
        os.makedirs(css_dir, exist_ok=True)
        shutil.copy(pjoin(src, 'lappsstyle.css'), css_dir)

    cwd = os.path.abspath(os.path.dirname(__file__))
    git_tags = subprocess.run('git tag'.split(), cwd=cwd, capture_output=True).stdout.decode('ascii').split('\n')
    last_ver = sorted([tag for tag in git_tags if tag and re.match(r'\d+\.\d+\.\d+$', tag)])[-1]
    proc = subprocess.run(f'git show {last_ver}:{vocab_yaml_path}'.split(), cwd=cwd, capture_output=True)
    if proc.returncode != 0:
        raise SystemError('cannot checkout latest vocab yaml to compute changes in vocab')
    old_clams_types = read_yaml(subprocess.run(f'git show {last_ver}:{vocab_yaml_path}'.split(), cwd=cwd, capture_output=True).stdout)
    new_clams_types = read_yaml(vocab_yaml_path)

    old_vocab_json_fname = os.path.join(cwd, 'docs', str(last_ver), 'vocabulary', ATTYPE_VERSIONS_JSONFILENAME)
    if not os.path.exists(old_vocab_json_fname):
        latest_attype_vers = collections.defaultdict(lambda: 1)
    else:
        latest_attype_vers = json.load(open(old_vocab_json_fname))
        
    old_types = {t['name']: t for t in old_clams_types}
    for t in new_clams_types:
        # a new type added in this version
        if t['name'] not in old_types:
            v = 1
        else:
            # existing type
            v = latest_attype_vers[t['name']]
            # but changed
            if t != old_types[t['name']]:
                v += 1
        t['version'] = v

    tree = Tree(new_clams_types)
    write_hierarchy(tree, index_dir, version)
    write_pages(tree, item_dir, version)


def update_jekyll_config(infname, version):
    outfname = infname + '.new'
    with open(infname) as config_f, \
            open(outfname, 'w') as out_f:
        new_version_line = f"    - {version}: '{version}'\n"
        lines = config_f.readlines()
        for i, line in enumerate(lines):
            out_f.write(line)
            if line == '  VERSIONS:\n':
                if lines[i+1] != new_version_line:
                    out_f.write(new_version_line)
    shutil.move(outfname, infname)


if __name__ == '__main__':

    dirname = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--test', dest="testdir", nargs="?", default=None, const='testbuild',
                        help='build version in test output directory')
    args = parser.parse_args()
    print(args)
    build(dirname, args)
