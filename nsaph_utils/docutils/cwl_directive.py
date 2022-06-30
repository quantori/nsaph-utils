import os

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
        filename = os.getcwd() + "/project/epa/src/cwl/" + self.arguments[0] + ".cwl"

        with open(filename) as f:
            content = f.read()

        parser.parse(content, doc)

        return doc.children


def setup(app):
    app.add_directive('cwldirective', CWLDirective)

    return {'version': sphinx.__version__, 'parallel_read_safe': True}
