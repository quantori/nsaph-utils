import os
import sys

import yaml


def document(title: str, path_to_cwl: str, path_to_md: str):
    with open(path_to_cwl, "rt") as yml:
        content = yaml.safe_load(yml)

    with open (path_to_md, "wt") as md:
        print("## {}".format(title), file=md)
        if "tool" in content["class"].lower():
            print("**Tool**", file=md)
        elif "workflow" in content["class"].lower():
            print("**Workflow**", file=md)
        print(file=md)
        src_path = os.path.relpath(path_to_cwl, os.path.dirname(path_to_md))
        name = os.path.basename(path_to_cwl)
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

    os.system(" ~/node_modules/.bin/markdown-toc -i {}".format(path_to_md))
    return 


if __name__ == '__main__':
    document(sys.argv[1], sys.argv[2], sys.argv[3])

