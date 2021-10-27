import os
from sphinx.domains import Domain


class URLDomain(Domain):
    """
    Resolve code links in markdown files .
    """

    def resolve_any_xref(self, env, fromdocname, builder, target, node, contnode):
        code_url = None
        if ".html" not in target and 'http' not in target and (
            target.endswith('py')
            or target.endswith('.cwl')
        ):
            code_url = self.link(target)
        if code_url is not None:
            print("Ref {}:{} ==> {}".format(fromdocname, target, code_url))
            contnode["refuri"] = code_url
            return [("code:module", contnode)]
        else:
            return []

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



