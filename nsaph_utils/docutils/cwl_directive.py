import os
import sys

import sphinx
from docutils.parsers.rst import Directive
from docutils import nodes, utils

from .cwl_parser import CWLParser


class CWLDirective(Directive):
    required_arguments = 1
    has_content = True

    def run(self):
        parser = CWLParser()
        node = nodes.container()
        node.document = self.state.document
        doc = utils.new_document(self.content, settings=self.state.document.settings)

        current_path = self.state.document.current_source
        cwl_path = current_path.replace('doc/pipeline', 'src/cwl').replace('.rst', '.cwl')

        with open(cwl_path) as f:
            content = f.read()

        parser.parse(content, doc)

        return doc.children


def setup(app):
    app.add_directive('cwldirective', CWLDirective)

    return {'version': sphinx.__version__, 'parallel_read_safe': True}
