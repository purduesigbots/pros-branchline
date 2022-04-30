import argparse
import importlib.resources

import jsonpath_ng as jsonpath
import jsonpickle
import jsonschema
import pathlib
import re
import yaml

from pros.conductor.templates.template import BaseTemplate
from typing import List


class MarkedSafeLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = super().construct_mapping(node, deep=deep)
        mapping['__mark__'] = {
            'start': {
                'line': node.start_mark.line,
                'col': node.start_mark.column
            },
            'end': {
                'line': node.end_mark.line,
                'col': node.end_mark.column
            }
        }
        return mapping


def _load_templates(paths: List[pathlib.Path]):
    templates = {}
    for path in paths:
        if path.is_dir():
            templates.update({
                f'{t}': yaml.load(t.open('r'), MarkedSafeLoader) for t in path.iterdir() if t.suffix == '.yaml'
            })
        else:
            if path.suffix == '.yaml':
                templates.update(**{f'{path}': yaml.load(path.open('r'), MarkedSafeLoader)})
    return templates


def check(args):
    import build_depot.validation
    templates = _load_templates(args.paths)

    schema = yaml.safe_load(
        importlib.resources.files(build_depot.validation).joinpath('template.schema.yaml').open('r')
    )
    validator = jsonschema.Draft202012Validator(schema)

    checks = []
    by_file = {}

    failure = False
    for name, instance in templates.items():
        print(f'Validating {name}: ')

        by_file[name] = {
            'counts': {
                'failure': 0
            },
            'details': []
        }

        for error in validator.iter_errors(instance):
            path = error.json_path
            if match := re.search(r'\d', path):
                # XXX: need to quote the keys that are also versions to make jsonpath happy but this is a bad heuristic
                #   that just assumes said keys will always be the end of a path. this is true at time of writing but
                #   it's not so future-proof
                path = path[:match.start()] + '"' + path[match.start():] + '"'
            path = f'{path}.__mark__'
            mark = [m.value for m in jsonpath.parse(path).find(instance)][0]

            sep = '\n- '
            checks.append({
                'file': name,
                'line': mark['start']['line'],
                'title': error.message,
                'message': f'{sep.join([s.message for s in sorted(error.context, key=lambda e: e.schema_path)])}',
                'annotation_level': 'failure',
            })
            by_file[name]['counts']['failure'] += 1
            by_file[name]['details'].append({
                'category': 'failure',
                'title': error.message,
                'message': f'{sep.join([s.message for s in sorted(error.context, key=lambda e: e.schema_path)])}',
                'startLine': mark['start']['line'],
                'startColumn': mark['start']['col']
            })
            print(f'\t{name}:{mark["start"]["line"]}:{mark["start"]["col"]} {error.json_path}: {error.message}')

            for suberror in sorted(error.context, key=lambda e: e.schema_path):
                print(f"\t\t{'.'.join(list(suberror.path))}: {suberror.message}")

            failure = True

        print('PASS' if not failure else 'FAIL')

        check_results = {
            'name': 'PROS Template Schema Validation',
            'summary': 'PASS' if not failure else 'FAIL',
            'counts': {
                'failure': sum([val['counts']['failure'] for _, val in by_file.items()])
            },
            'byFile': by_file
        }

        if args.output_file is not None:
            with open(args.output_file, 'w') as f:
                f.write(jsonpickle.pickler.encode(checks, indent=3, unpicklable=False))

    return failure


def build(args):
    templates = _load_templates(args)
    template_data = [BaseTemplate(
        metadata=dict({
                'location': (
                    val.get('location', data.get('location')) if isinstance(val, dict) else data.get('location')
                ).format(name=data.get('name'), version=version)
            },
            **data.get('metadata', {})
        ),
        name=data.get('name'),
        supported_kernels=val.get('kernel') if isinstance(val, dict) else val,
        target=val.get('target', data.get('target')) if isinstance(val, dict) else data.get('target'),
        version=version
    ) for _, data in templates.items() for version, val in data.items()]

    print(f'writing depot file {args.build}.json')
    with open(f'{args.build}.json', 'w') as depot:
        depot.write(jsonpickle.pickler.encode(template_data, indent=3))


def main():
    parser = argparse.ArgumentParser(description='build a pros remote depot file from some yaml files')
    parser.add_argument('-b', '--build', metavar='depot name', const=None)
    parser.add_argument('--build-only', '--no-check', dest='no_check', default=False, action='store_true')
    parser.add_argument('-o', '--output', dest='output_file', metavar='output file', const=None, type=pathlib.Path,
                        help='path to write JSON file containing a summary of the schema validation. has no effect if '
                             '--build-only is specified')
    parser.add_argument('paths', metavar='path', nargs='+', type=pathlib.Path,
                        help='directories or files to use as input')

    args = parser.parse_args()

    if args.no_check and args.build is None:
        print('command has no effect')
        return 0

    ok = True
    if not args.no_check:
        ok = check(args)

    if not ok:
        return -1

    if args.build is not None:
        build(args)

    return 0
