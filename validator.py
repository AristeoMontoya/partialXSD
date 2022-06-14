import sys
import logging
import argparse
from os import listdir
from os import path
from lxml import etree
from glob import glob

root_for_schema = {}

def set_handler(logger, handler):
    formatter = logging.Formatter('%(message)s')
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def initalize_logger(logfile: str):
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    set_handler(root, logging.FileHandler(logfile or 'validator.log'))
    set_handler(root, logging.StreamHandler(sys.stdout))

def get_arguments():
    parser = argparse.ArgumentParser(description='Schema validator')
    parser.add_argument('target', help='File or dir to validate')
    parser.add_argument('schema', help='XSD or directory containing XSD files to apply')
    parser.add_argument('-o', '--output', help='Log output', required=False)
    parser.add_argument('-r',
            '--recursive', 
            help='Search recursively',
            required=False,
            action='store_true')
    return parser.parse_args()

def search_in_dir(target: str, recurse: bool, ext:str):
    return [
        i for i in glob(target + '/**', recursive=recurse) if i.endswith(ext)
    ]

def list_files(target: str, recurse: bool, ext: str):
    return [target] if path.isfile(target) else search_in_dir(target, recurse, ext)

def get_schemas(schema_dir: str):
    '''List all XSD files in a given dir'''
    if path.exists(schema_dir):
        return [xsd for xsd in listdir(schema_dir) if xsd.endswith('.xsd')]
    else:
        return []

def extract_tag(schema):
    comment = schema.xpath('.//comment()')[0]
    return comment.text.strip()

def split_url(url: str):
    return url.split('/')[-1]

def get_subtree_root(schema):
    xsd_file = split_url(schema.docinfo.URL)
    if xsd_file in root_for_schema:
        return root_for_schema[xsd_file]
    else:
        root_for_schema[xsd_file] = extract_tag(schema)
        return get_subtree_root(schema)

def test_schema(schema_doc, subdoc):
    schema = etree.XMLSchema(schema_doc)
    try:
        schema.assertValid(subdoc)
        return True
    except:
        return False

def find_tags(document, tag: str):
    root = document.getroot()
    return root.findall(f'.//{tag}')

def compare_schemas(xml: str, xsd_files: list):
    document = etree.parse(xml)
    for xsd in xsd_files:
        matches = 0
        schema = etree.parse(xsd)
        to_find = get_subtree_root(schema)
        occurrences = find_tags(document, to_find)
        for occurrence in occurrences:
            if test_schema(schema, occurrence):
                logging.info(f'Occurrence of {xsd} at line {occurrence.sourceline}')
                matches += 1
        if matches > 0:
            add_to_summary(xsd, matches)

def process_files(xml_files: list, schemas: list):
    for xml in xml_files:
        logging.info('---------------------------------------------------------')
        logging.info(f'Analyzing {xml}')
        compare_schemas(xml, schemas)

if __name__ == '__main__':
    args = get_arguments()
    initalize_logger(args.output)
    xml_files = list_files(args.target, args.recursive, 'xml')
    xsd_files = list_files(args.schema, args.recursive, 'xsd')
    logging.info(f'Files to analize: {len(xml_files)}')
    logging.info(f'Schemas to apply: {len(xsd_files)}')
    process_files(xml_files, xsd_files)
