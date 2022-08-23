#  Copyright (c) 2021. Harvard University
#
#  Developed by Research Software Engineering,
#  Faculty of Arts and Sciences, Research Computing (FAS RC)
#  Author: Michael A Bouzinier
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import argparse
import logging
import os
from typing import Optional

import yaml

from nsaph_utils.docutils.md_creator import MDCreator

logger = logging.getLogger('script')
logger.addHandler(logging.StreamHandler())

arg_parser = argparse.ArgumentParser(description='Convert CWL files into Markdown')
arg_parser.add_argument(
    '-i', '--input-dir', type=str, required=True, dest='input_dir', help='An input dir with CWL files'
)
arg_parser.add_argument(
    '-o', '--output-dir', type=str, required=True, dest='output_dir', help='An output dir for Markdown files'
)
arg_parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='An extended logging')


class CWLParser:
    def __init__(self, content: str, output_file_name: str):
        logger.info(output_file_name)
        self.raw_content = content
        self.yaml_content = yaml.safe_load(content)
        self.output_file_name = output_file_name
        self.md_file = MDCreator(file_name=self.output_file_name)

    def parse(self):
        self._add_title()
        self._add_contents()
        self._add_header()
        self._add_docs()
        self._add_inputs()
        self._add_outputs()
        self._add_steps()

        self.md_file.save()

    def _add_title(self):
        title = self._find_title(self.raw_content) or self._get_filename(self.output_file_name)
        self.md_file.add_header(text=title, level=1)

    @staticmethod
    def _find_title(content: str) -> Optional[str]:
        for line in content.splitlines():
            if line.startswith('###'):
                return line.replace('###', '').strip()

    @staticmethod
    def _get_filename(output_file_name: str) -> str:
        filename = output_file_name.split(os.path.sep)[-1]
        return filename.replace('.md', '.cwl')

    def _add_contents(self):
        contents = [
            '```{contents}',
            '---',
            'local:',
            '---',
            '```',
        ]

        self.md_file.add_text('\n'.join(contents))

    def _add_header(self):
        if 'tool' in self.yaml_content['class'].lower():
            header = '**Tool** ' + self._extract_tool(str(self.yaml_content['baseCommand']))
        elif 'workflow' in self.yaml_content['class'].lower():
            header = '**Workflow**'
        else:
            header = '**Unknown class**'

        self.md_file.add_text(header)

    @staticmethod
    def _extract_tool(base_command: str) -> str:
        tool = base_command.replace('[', '').replace(']', '').replace("'", '').split(', ')[-1]
        return f'[]({tool})'

    def _add_docs(self):
        self.md_file.add_header(text='Description', level=2)
        self.md_file.add_text(self.yaml_content['doc'])

    def _add_inputs(self):
        self.md_file.add_header(text='Inputs', level=2)

        data = [('Name', 'Type', 'Default', 'Description')]
        for name, arg in self.yaml_content['inputs'].items():
            if isinstance(arg, str):
                doc = name
                tp = arg.replace('?', '')
                df = None
            else:
                doc = arg.get('doc', ' ').replace('\n', ' ')
                tp = arg.get('type', 'string')
                df = arg.get('default', None)

            if df is not None:
                df = f'`{df}`'
            else:
                df = ' '

            data.append((name, tp, df, doc))

        self.md_file.add_table(data=data)

    def _add_outputs(self):
        self.md_file.add_header(text='Outputs', level=2)

        data = [('Name', 'Type', 'Description')]
        for name, arg in self.yaml_content['outputs'].items():
            doc = arg.get('doc', ' ').replace('\n', ' ')
            tp = arg.get('type', 'string')

            if isinstance(tp, str):
                tp = tp.replace('?', '')
            elif isinstance(tp, dict):
                tp = tp['type']

            data.append((name, tp, doc))

        self.md_file.add_table(data=data)

    def _add_steps(self):
        if 'steps' not in self.yaml_content:
            return

        self.md_file.add_header(text='Steps', level=2)

        data = [('Name', 'Runs', 'Description')]
        for item in self.yaml_content['steps']:
            if isinstance(item, dict):
                name = item['id']
                arg = item
            else:
                name = item
                arg = self.yaml_content['steps'][name]

            doc = arg.get('doc', ' ').replace('\n', ' ')
            runs = arg['run']
            if isinstance(runs, str):
                ref_uri = runs.replace(".cwl", ".md")
                target = f'[{runs}]({ref_uri})'
            else:
                target = runs.get('baseCommand', 'command')

            data.append((name, target, doc))

        self.md_file.add_table(data=data)


def main():
    args = arg_parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.INFO)

    cwl_files = os.listdir(args.input_dir)

    for file_name in cwl_files:
        if os.path.splitext(file_name)[1].lower() != '.cwl':
            continue

        input_file_path = os.path.join(os.path.abspath(args.input_dir), file_name)
        output_file_path = os.path.join(os.path.abspath(args.output_dir), file_name.replace('.cwl', '.md'))

        with open(input_file_path, 'r') as cwl_file:
            CWLParser(cwl_file.read(), output_file_path).parse()


if __name__ == '__main__':
    main()
