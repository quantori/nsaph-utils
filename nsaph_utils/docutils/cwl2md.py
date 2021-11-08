import os
import sys
from typing import Dict, Optional
from pathlib import Path
import yaml


def find_tool(content: Dict) -> str:
    if "baseCommand" not in content:
        return ""
    command = content["baseCommand"]
    if command[0] != "python":
        return '`{}`'.format(" ".join(command))

    module: str = None
    for i in range(len(command) - 2):
        if command[i+1] == '-m':
            module = command[i+2]
            break
    if not module:
        for c in command[1:]:
            if not c.startswith('-'):
                module = c
                break

    path = ""
    if module.endswith(".py"):
        name = os.path.basename(module)[:-3]
    else:
        x = module.split('.')
        name = x[-1]
        path = x[:-1]
    if not module:
        return '`{}`'.format(" ".join(command))
    if module.startswith("nsaph.") or "/nsaph/" in module:
        target = os.path.join("..", "..", "..", "..",
                              "platform", "doc", "members", name + ".html")
    else:
        target = os.path.join("..", "..", "src", "python", *path, name + ".py")
    return "[{}]({})".format(module, target)


def document(path_to_cwl: str, t_ref_mode: str):
    p = Path(path_to_cwl)
    name = os.path.basename(path_to_cwl)
    path_to_md_dir  = os.path.join(p.parents[2], "doc", "pipeline")
    if not os.path.isdir(path_to_md_dir):
        os.makedirs(path_to_md_dir, exist_ok=True)
    path_to_md = os.path.join(path_to_md_dir, name.replace(".cwl", ".md"))
    with open(path_to_cwl, "rt") as yml:
        content = yaml.safe_load(yml)
        yml.seek(0)
        comments = [
            line for line in yml if line.startswith("###")
        ]
        title = comments[0][3:].strip()
        tool = find_tool(content)

    with open (path_to_md, "wt") as md:
        print("# {}".format(title), file=md)
        if "tool" in content["class"].lower():
            print("**Tool** \t{}".format(tool), file=md)
        elif "workflow" in content["class"].lower():
            print("**Workflow**", file=md)
        print(file=md)
        src_path = os.path.relpath(path_to_cwl, os.path.dirname(path_to_md))
        print("**Source**: [{}]({})".format(name, src_path), file=md)
        print(file=md)
        print("<!-- toc -->", file=md)
        print(file=md)
        if "doc" in content:
            print("## Description", file=md)
            print(content["doc"], file=md)
            print(file=md)
        if "inputs" in content:
            print("## Inputs", file=md)
            print(file=md)
            print("| Name | Type | Default | Description |", file=md)
            print("|------|------|---------|-------------|", file=md)
            for name in content["inputs"]:
                arg = content["inputs"][name]
                doc = arg.get("doc", " ").replace('\n', ' ')
                tp = arg.get("type", "string").replace('?', '')
                df = arg.get("default", None)
                if df is not None:
                    df = "`{}`".format(df)
                else:
                    df = " "

                print("|{name}|{type}|{default}|{desc}|"
                      .format(name=name, type=tp, default=df, desc=doc),
                      file=md)

        if "outputs" in content:
            print(file=md)
            print("## Outputs", file=md)
            print(file=md)
            print("| Name | Type | Description |", file=md)
            print("|------|------|-------------|", file=md)
            for name in content["outputs"]:
                arg = content["outputs"][name]
                doc = arg.get("doc", " ").replace('\n', ' ')
                tp = arg.get("type", "string").replace('?', '')
                print("|{name}|{type}|{desc}|"
                      .format(name=name, type=tp, desc=doc),
                      file=md)

        if "steps" in content:
            steps = content["steps"]
            print(file=md)
            print("## Steps", file=md)
            print(file=md)
            print("| Name | Runs | Description |", file=md)
            print("|------|------|-------------|", file=md)
            for name in steps:
                arg = steps[name]
                doc = arg.get("doc", " ").replace('\n', ' ')
                runs = arg["run"]
                target = runs.replace(".cwl", "." + t_ref_mode)
                print("|{name}|[{runs}]({target})|{desc}|"
                      .format(name=name, runs=runs, target=target, desc=doc),
                      file=md)

    os.system(" ~/node_modules/.bin/markdown-toc -i {}".format(path_to_md))
    return 


if __name__ == '__main__':
    if len(sys.argv) > 2:
        table_ref_mode = sys.argv[2]
    else:
        table_ref_mode = "md"
    document(sys.argv[1], table_ref_mode)

