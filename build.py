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
from typing import Union, List, Dict, Optional, Set
from urllib import request

import yaml
from bs4 import BeautifulSoup, Tag
from bs4.formatter import HTMLFormatter
from typing.io import TextIO

INCLUDE_CONTEXT = False
BASEURL = 'http://mmif.clams.ai'
# this file will store a dict of at_type: version, where version is formatted as `v1`
ATTYPE_VERSIONS_JSONFILENAME = 'attypeversions.json'
VOCAB_TITLE = 'CLAMS Vocabulary'


def read_yaml(fp: Union[str, bytes, TextIO]) -> List[Dict]:
    """Read a YAML file and return a list of Python dictionaries, one for each
    document in the YAML file."""
    if isinstance(fp, str):
        fp = open(fp, 'r')
    docs = [doc for doc in yaml.safe_load_all(fp)]
    return docs


def get_soup() -> BeautifulSoup:
    """Return a basic top-level soup."""
    return BeautifulSoup("<html>" +
                         "<head></head>" +
                         "<body></body>" +
                         "</html>",
                         features='lxml')


def tag(tagname: str, attrs: Optional[Dict] = None, text: Optional[str] = None, dtrs: Optional[List[Tag]] = None) -> Tag:
    """Return a soup Tag element."""
    attrs = {} if attrs is None else attrs
    dtrs = [] if dtrs is None else dtrs
    newtag = BeautifulSoup('', features='lxml').new_tag(tagname, attrs=attrs)
    if text is not None:
        newtag.append(text)
    for dtr in dtrs:
        newtag.append(dtr)
    return newtag


def add_stylesheet(soup: BeautifulSoup, stylesheet: str) -> None:
    soup.head.append(tag('link', {'rel': 'stylesheet',
                                  'type': 'text/css',
                                  'href': stylesheet}))


def DIV(attrs: Optional[Dict] = None, text: Optional[str] = None, dtrs: Optional[List[Tag]] = None) -> Tag:
    return tag('div', attrs=attrs, text=text, dtrs=dtrs)


def TABLE(attrs: Optional[Dict] = None, dtrs: Optional[List[Tag]] = None) -> Tag:
    return tag('table', attrs=attrs, dtrs=dtrs)


def TABLE_ROW(table_cells: List[Tag]) -> Tag:
    return tag('tr', dtrs=table_cells)


def H1(text: str) -> Tag:
    return tag('h1', text=text)


def H2(text: str) -> Tag:
    return tag('h2', text=text)


def HREF(link: str, text: str) -> Tag:
    return tag('a', attrs={'href': link}, text=text)


def SPAN(text: str) -> Tag:
    return tag('span', text=text)


class Tree(object):
    types: List[Dict]
    types_idx: Dict[str, Dict]
    root: Dict

    def __init__(self, clams_types) -> None:
        """Take the generator object and put a dictionary"""
        self.types = clams_types
        self.types_idx = { t['name']: t for t in self.types }
        self.root = self.find_root()
        self.build_tree()

    def find_root(self) -> Optional[Dict]:
        for t in self.types:
            if t['parent'] is None:
                return t

    def build_tree(self) -> None:
        """Add links between all the type definitions by filling in parentNode
        and childNodes attributes."""
        # First initialize the dominance links and then populate them
        for t in self.types:
            t['parentNode'] = None
            t['childNodes'] = []
        for t in self.types:
            parentName = t['parent']
            if parentName is not None and parentName in self.types_idx:
                parentNode = self.types_idx.get(parentName)
                t['parentNode'] = parentNode
                parentNode.setdefault('childNodes', []).append(t)

    def print_tree(self, node, level=0) -> None:
        print("%s%s" % ('  ' * level, node['name']))
        for child in node['childNodes']:
            self.print_tree(child, level + 1)


def format_attype_version(version: Union[str, int]) -> str:
    return f'v{version}'


class Page(object):
    soup: BeautifulSoup
    stylesheet: str
    container: Tag
    main_content: Tag
    intro: Tag
    fpath: str
    fname: str
    
    def __init__(self) -> None:
        self.soup = get_soup()
        self._add_stylesheet()

    def _add_stylesheet(self) -> None:
        add_stylesheet(self.soup, self.stylesheet)

    def _add_title(self, title) -> None:
        self.soup.head.append(tag('title', text=title))

    def _add_main_structure(self) -> None:
        """Build the basic structure of the body, which is a container div with
        in it an intro div and a mainContent div."""
        container = DIV({'id': 'container'},
                        dtrs=[DIV({'id': 'intro'}),
                              DIV({'id': 'mainContent'})])
        self.soup.body.append(container)
        self.container = container
        self.intro = self.soup.find(id='intro')
        self.main_content = self.soup.find(id='mainContent')

    def _add_footer(self) -> None:
        footer = 'Page generated on %s' % time.strftime("%Y-%m-%d at %H:%M:%S")
        self.soup.body.append(DIV({'id': 'footer'}, text=footer))

    def _add_space(self) -> None:
        self.main_content.append(tag('br'))

    def write(self) -> None:
        if not os.path.exists(self.fpath):
            os.makedirs(self.fpath, exist_ok=True)
        with open(self.fname, 'w') as fh:
            # https://www.crummy.com/software/BeautifulSoup/bs4/doc/#bs4.HTMLFormatter
            fh.write(self.soup.prettify(formatter=HTMLFormatter(indent=2)))


class IndexPage(Page):

    def __init__(self, tree, outdir, version) -> None:
        self.stylesheet = 'css/lappsstyle.css'
        super().__init__()
        self.version = version
        self.fpath = outdir
        self.fname = pjoin(outdir, 'index.html')
        self.tree = tree
        self._add_title(VOCAB_TITLE)
        self._add_main_structure()
        self._add_header()
        self._add_description()
        self._add_tree(self.tree.root, self.main_content)
        self._add_space()
        #self._add_ontologies()
        #self._add_space()
        self._add_footer()

    def _add_description(self) -> None:
        span1_text = f"The {VOCAB_TITLE} defines an ontology" \
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

    def _add_tree(self, clams_type, soup_node) -> None:
        type_name = clams_type['name']
        fname = '%s' % type_name
        if 'version' in clams_type:
            fname += f' ({clams_type["version"]})'
        # TODO (krim @ 3/14/23): this relies on assumption of the URL format, should be a better, future-proof way. 
        link = HREF(f'../../../vocabulary/{clams_type["name"]}/{clams_type["version"]}', fname)
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

    def _add_ontologies(self) -> None:
        onto_soup = BeautifulSoup("""
      <p>The vocabulary is available in the following formats:
          <a href='ontologies/clams.vocabulary.rdf'>RDF</a>,
          <a href='ontologies/clams.vocabulary.owl'>OWL</a>,
          <a href='ontologies/clams.vocabulary.jsonld'>JSONLD</a> and
          <a href='ontologies/clams.vocabulary.ttl'>TTL</a>.</p>""", features="lxml")
        for element in onto_soup.body:
            self.main_content.append(element)

    def _add_header(self) -> None:
        header = DIV({'id': 'pageHeader'},
                     dtrs=[H1(VOCAB_TITLE),
                           H2(f'version {self.version}')])
        self.intro.append(header)


class TypePage(Page):

    def __init__(self, clams_type, outdir, included_in) -> None:
        subdirs = (clams_type['name'], clams_type['version'])
        self.stylesheet = f"{'/'.join(['..'] * len(subdirs))}/css/lappsstyle.css"
        super().__init__()
        self.clams_type = clams_type
        self.metadata = clams_type.get('metadata', [])
        self.properties = clams_type.get('properties', [])
        self.fpath = pjoin(outdir, *subdirs)
        self.fname = pjoin(self.fpath, 'index.html')
        self.baseurl = f'{BASEURL}/vocabulary'
        self._add_title(clams_type['name'])
        self._add_main_structure()
        self._add_header()
        sorted(included_in, reverse=True)
        self._add_home_button(included_in)
        # make sure old versions that include this type/version is descending-sorted
        self._add_head(included_in[0])
        self._add_definition()
        self._add_metadata()
        self._add_properties()
        self._add_space()
        self._add_footer()

    def _chain_to_top(self) -> List[Dict]:
        chain = []
        parent = self.clams_type['parentNode']
        while parent is not None:
            chain.append(parent)
            parent = parent['parentNode']
        return chain

    def _add_home_button(self, included_in: List[str]) -> None:
        included_vers = []
        for mmif_ver in included_in:
            if included_vers:
                included_vers.append(', ')
            included_vers.append(HREF('/'.join(['..', '..', '..', mmif_ver, 'vocabulary']), mmif_ver))
        self.main_content.append(
            DIV({'id': 'sectionbar'}, dtrs=[tag(
                'p',
                text="included in: ",
                dtrs=included_vers
            )]))

    def _add_head(self, cur_vocab_ver) -> None:
        chain = reversed(self._chain_to_top())
        dtrs = []
        for n in chain:
            uri_suffix = [n['name'], n['version']]
            dtrs.append(HREF('/'.join(['..'] * len(uri_suffix) + uri_suffix), n['name']))
            dtrs.append(SPAN('>'))
        dtrs.append(SPAN(self.clams_type['name']))
        p = tag('p', {'class': 'head'}, dtrs=dtrs)
        self.main_content.append(p)
        self._add_space()

    def _add_definition(self) -> None:
        url = '/'.join((self.baseurl, self.clams_type['name'], self.clams_type['version']))
        children = [TABLE_ROW([tag('td', {'class': 'fixed'}, dtrs=[tag('b', text='Definition')]), tag('td', text=self.clams_type['description'])]),
                    TABLE_ROW([tag('td', dtrs=[tag('b', text='URI')]), tag('td', dtrs=[HREF(url, url)])])]
        
        # Some hard-coding to make transition from old vocab URL (mmif/mmif_version/vocab/type) to the new one
        # (mmif/vocab/type/type_version)
        # See how transition is mapped: https://github.com/clamsproject/mmif/issues/14#issuecomment-1504439497
        # NOTE that there isn't ``Annotation/v1`` page and won't be (the new type_ver didn't exist in 0.4.[0,1] times).
        # The reason I used v2 for 0.4.2/Annotation and v1 for 0.4.[0,1]/Annotation is to make this transition
        # compatible in the mmif-python SDK implementation as well. 
        def get_identity_row(identity_url):
            return TABLE_ROW([tag('td', text='Also known as'), tag('td', dtrs=[HREF(identity_url, identity_url)])])
        if self.clams_type['version'] == 'v1':
            patches = [0, 1]
            if self.clams_type['name'] != 'Annotation':
                patches.append(2)
            for patch in patches:
                children.append(get_identity_row(f'https://mmif.clams.ai/0.4.{patch}/vocabulary/{self.clams_type["name"]}/'))
        elif self.clams_type['version'] == 'v2' and self.clams_type['name'] == 'Annotation':
            children.append(
                get_identity_row(f'https://mmif.clams.ai/0.4.2/vocabulary/{self.clams_type["name"]}/'))
        if 'similarTo' in self.clams_type:
            for s in self.clams_type['similarTo']:
                children.append(TABLE_ROW([tag('td', text='Similar to'), tag('td', dtrs=[HREF(s, s)])]))
        table = TABLE(dtrs=children)
        self.main_content.append(table)

    def _add_metadata(self) -> None:
        self.main_content.append(H1('Metadata'))
        if self.metadata:
            self._add_properties_aux(self.metadata)
        self._add_properties_from_chain('metadata')

    def _add_properties(self) -> None:
        self.main_content.append(H1('Properties'))
        if self.properties:
            self._add_properties_aux(self.properties)
        self._add_properties_from_chain('properties')

    def _add_properties_from_chain(self, proptype) -> None:
        for n in self._chain_to_top():
            properties = n.get(proptype, None)
            if properties is not None:
                h2 = H2("%s from %s" % (proptype.capitalize(), n['name']))
                self.main_content.append(h2)
                self._add_properties_aux(properties)

    def _add_properties_aux(self, properties) -> None:
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

    def _add_header(self) -> None:
        header = DIV({'id': 'pageHeader'},
                     dtrs=[
                         H1(f'{self.clams_type["name"]} ({self.clams_type["version"]})'),
                         H2(f'{VOCAB_TITLE}'), 
                         ])
        self.intro.append(header)


def copy(src_dir: str, dst_dir: str, include_fnames: Set = {}, exclude_fnames: Set = {}, templating: Dict = {}) -> None:
    for r, ds, fs in os.walk(src_dir):
        r = r[len(src_dir)+1:]
        for f in fs:
            if f.startswith('.') or r in exclude_fnames or f in exclude_fnames:
                continue
            elif not include_fnames or f in include_fnames:
                os.makedirs(pjoin(dst_dir, r), exist_ok=True)
                if templating and f.endswith('.json') or f.endswith('.md'):
                    with open(pjoin(src_dir, r, f), 'r') as in_f, open(pjoin(dst_dir, r, f), 'w') as out_f:
                        tmpl_to_compile = Template(in_f.read())
                        compiled = tmpl_to_compile.substitute(templating)
                        out_f.write(compiled)
                else:
                    shutil.copy(pjoin(src_dir, r, f), pjoin(dst_dir, r))


def check_version_exists(version: str):
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

    print(f"\n>>> Building vocabulary: index in {vocab_index_out_dir}, items in {vocab_items_out_dir}")
    vocab_tree = build_vocab(vocab_src_dir, vocab_index_out_dir, version, vocab_items_out_dir)

    print("\n>>> Creating directory structure in '%s'" % out_dir)
    os.makedirs(out_dir, exist_ok=True)

    print("\n>>> Building specification in '%s'" % out_dir)
    build_spec(spec_src_dir, out_dir, version, {t['name']: t['version'] for t in vocab_tree.types})

    print("\n>>> Building json schema in '%s'" % out_dir)
    build_schema(schema_src_dir, schema_out_dir, version)

    if INCLUDE_CONTEXT:
        # TODO: this is actually broken
        print("\n>>> Building json-ld context in '%s'" % out_dir)
        build_context(context_src_dir, out_dir, version)

    if args.testdir is None:
        print("\n>>> Updating jekyll configuration in '%s'" % jekyll_conf_file)
        update_jekyll_config(jekyll_conf_file, version)

    
def build_spec(src, dst, mmif_version, attypes_versions):
    version_dict = collections.defaultdict(lambda: 'v1')
    for name, version in attypes_versions.items():
        version_dict[f"{name}_VER"] = version 
    version_dict['VERSION'] = mmif_version
    copy(src, dst, exclude_fnames={'next.md', 'notes', 'samples/others'}, templating=version_dict)


def build_schema(src, dst, version):
    copy(src, dst, include_fnames=['lif.json', 'mmif.json'])


def build_context(src, dst, version):
    copy(src, dst, exclude_fnames=['example.json'])


def build_vocab(src, index_dir, mmif_version, item_dir) -> Tree:
    vocab_yaml_path = os.path.relpath(pjoin(src, "clams.vocabulary.yaml"), os.path.dirname(__file__))
    for d in (index_dir, item_dir):
        css_dir = pjoin(d, 'css')
        os.makedirs(css_dir, exist_ok=True)
        shutil.copy(pjoin(src, 'lappsstyle.css'), css_dir)

    cwd = os.path.abspath(os.path.dirname(__file__))
    git_tags = subprocess.run('git tag'.split(), cwd=cwd, capture_output=True).stdout.decode('ascii').split('\n')
    old_vers = sorted([tag for tag in git_tags if tag and re.match(r'\d+\.\d+\.\d+$', tag)])
    last_ver = old_vers[-1]
    proc = subprocess.run(f'git show {last_ver}:{vocab_yaml_path}'.split(), cwd=cwd, capture_output=True)
    if proc.returncode != 0:
        raise SystemError('cannot checkout latest vocab yaml to compute changes in vocab')
    last_clams_types = read_yaml(subprocess.run(f'git show {last_ver}:{vocab_yaml_path}'.split(), cwd=cwd, capture_output=True).stdout)
    new_clams_types = read_yaml(vocab_yaml_path)

    attype_versions_included = collections.defaultdict(lambda: collections.defaultdict(list))
    latest_attype_vers = collections.defaultdict(lambda: 1)
    for old_ver in old_vers:
        old_attype_versions_fname = os.path.join(cwd, 'docs', str(old_ver), 'vocabulary', ATTYPE_VERSIONS_JSONFILENAME)
        if not os.path.exists(old_attype_versions_fname):
            # see https://github.com/clamsproject/mmif/issues/14#issuecomment-1504439497 
            # to see why only this one gets v2 to start
            latest_attype_vers['Annotation'] = 2
        else:
            old_attype_versions = json.load(open(old_attype_versions_fname))
            for attypename, attypever in old_attype_versions.items():
                if old_ver == last_ver:
                    latest_attype_vers[attypename] = int(re.sub(r'[^0-9.]+', '', attypever))
                attype_versions_included[attypename][attypever].append(old_ver)
            
    old_types = {t['name']: t for t in last_clams_types}
    tree = Tree(new_clams_types)
    
    def how_different(type1, type2):
        """
        return 0 if the types are the same, 
        1 if the differences should be propagated to the children
        2 if the types are different in description and parent-ship only (no propagation),
        """
        for inheritable in ('properties', 'metadata'):
            if type1.get(inheritable, {}) != type2.get(inheritable, {}):
                return 1
        if type1['description'] != type2['description'] or type1['parent'] != type2['parent']:
            return 2
        return 0

    updated = collections.defaultdict(lambda: False)
    
    def propagate_version_changes(node, parent_changed=False):
        if parent_changed:
            updated[node['name']] = True
            for child in node['childNodes']:
                propagate_version_changes(child, True)
        else:
            difference = how_different(node, old_types[node['name']])
            if difference > 0:
                updated[node['name']] = True
            for child in node['childNodes']:
                propagate_version_changes(child, difference == 1)
    
    root = tree.root
    propagate_version_changes(root, False)

    for t in new_clams_types:
        v = latest_attype_vers[t['name']]
        if updated[t['name']]:
            v += 1
        t['version'] = format_attype_version(v)

    # the main `x.y.z/vocabulary/index.html` page with the vocab tree
    IndexPage(tree, index_dir, mmif_version).write()
    # then, redirection HTML files for each vocab types to its own versioned html page
    # (then, we decided not to do the redirection because it also adds confusions by 
    # reifying URLs for non-existing IRIs e.g. https://mmif.clams.ai/0.5.0/vocabulary/TimeFrame)
    
    # for clams_type in tree.types:
    for clams_type in []:
        redirect_dir = pjoin(index_dir, clams_type["name"])
        os.makedirs(redirect_dir, exist_ok=True)
        with open(pjoin(redirect_dir, 'index.html'), 'w') as redirect_page:
            redirect_page.write(
                f'<head> <meta http-equiv="Refresh" content="0; URL=../../../vocabulary/{clams_type["name"]}/{clams_type["version"]}" /> </head>'
            )
    # JSON to keep the versions of individual vocab types that will be used in the next release cycle
    with open(pjoin(index_dir, ATTYPE_VERSIONS_JSONFILENAME), 'w') as attype_versions_jsonfile:
        json.dump({t['name']: t['version'] for t in tree.types}, attype_versions_jsonfile)

    # finally, individually versioned annotation types pages
    for clams_type in tree.types:
        TypePage(clams_type, item_dir, 
                 # theoretically, `mmif_version` is a new string and shouldn't be in the `attype_vers_incl` dict. 
                 # so we add the "current" (new) version to include this current at_type
                 included_in=attype_versions_included[clams_type['name']][clams_type['version']] + [mmif_version]
                 ).write()
    return tree


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
