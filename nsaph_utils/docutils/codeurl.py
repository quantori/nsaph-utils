import os

from docutils.nodes import Element
from sphinx.addnodes import pending_xref
from sphinx.domains import Domain


class URLDomain(Domain):
    """
    Resolve code links in markdown files .
    """

    def resolve_any_xref(self, env, fromdocname, builder, target, node, contnode):
        code_url = None
        if ".html" not in target and 'http' not in target and (
            target.endswith('py')
        ):
            code_url = self.link(target)
        if code_url is not None:
            print("Ref {}: {} ==> {}".format(fromdocname, target, code_url))
            contnode["refuri"] = code_url
            return [("code:module", contnode)]
        if (".html" not in target and 'http' not in target) and (
            "../nsaph/" in target
        ):
            base, ext = os.path.splitext(target)
            if not ext or ext == ".md":
                new_target = base + ".html"
            else:
                new_target = target
            new_target = new_target.replace("../nsaph/", "../platform/")
            print("Ref {}: {} ==> {}".format(fromdocname, target, new_target))
            contnode["refuri"] = new_target
            return [("md:module", contnode)]
        #print("XRef1 {}: {}".format(fromdocname, target))
        return []

    def resolve_xref(self, env, fromdocname: str,
                     builder, typ: str, target: str,
                     node: pending_xref, contnode: Element) -> Element:
        print("XRef2 {}: {} [{}]".format(fromdocname, target, typ))
        return super().resolve_xref(env, fromdocname, builder, typ, target,
                                    node, contnode)

    @staticmethod
    def link(path: str) -> str:
        name = os.path.basename(path)
        x = name.split('.')
        if len(x) < 2:
            return path
        x[1] = "html"
        if path.startswith('../'):
            return os.path.join("members", '.'.join(x))
        return os.path.join("doc", "members", '.'.join(x))



