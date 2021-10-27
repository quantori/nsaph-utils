import glob
import os
import sys

m_template = """..
    autogenerated
    
The {name} Module
============================================================================

.. automodule:: {module}
   :members:
   :undoc-members:

"""


class ModuleCollector:

    def __init__(self,
                 destination: str = "doc/members",
                 pattern = "**/*.py",
                 template = m_template):
        self.dest = destination
        self.pattern = pattern
        self.template = template

    def collect(self, source_path: str):
        modules = glob.glob(os.path.join(source_path, self.pattern),
                            recursive=True)
        for module in modules:
            name = os.path.basename(module)
            name, _ = os.path.splitext(name)
            if name.startswith("_"):
                continue
            target = name + ".rst"
            target = os.path.join(self.dest, target)
            if os.path.exists(target):
                with open(target) as f:
                    lines = [line for line in f][:2]
                    if lines[0].strip() != '..' or lines[1].strip() != "autogenerated":
                        continue
            x, _ = os.path.splitext(os.path.relpath(module, source_path))
            x = x.replace('/', '.')
            content = self.template.format(name=name, module=x)
            with open(target, "wt") as f:
                f.write(content)
        return


if __name__ == '__main__':
    collector = ModuleCollector()
    collector.collect(sys.argv[1])

