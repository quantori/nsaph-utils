import os
import sys
from typing import List


def get_header_level(line: str) -> int:
    for i in range(len(line)):
        if line[i] != '#':
            return i
    return -1


def read_section(source: str, section: str) -> List[str]:
    content: List[str] = []
    inside = False
    level = None
    with open(source, "rt") as f:
        for line in f:
            if not line.startswith('#'):
                if inside:
                    content.append(line)
                continue
            lh = get_header_level(line)
            if not inside:
                header = line[lh:].strip()
                if header.lower() != section.lower():
                    continue
                level = lh
                inside = True
                continue
            if lh <= level:
                break

    return content


def insert_section(source: str, to: str, project: str = None):
    if project is None:
        project = os.path.basename(os.path.dirname(source))
    with open(to, "rt") as f:
        content = [line for line in f]
    start = None
    end = None
    section = None
    end_of_section = None
    for l1, line in enumerate(content):
        if not line.startswith("<!--"):
            continue
        statement = line[4:].strip().lower()
        if start is None:
            if statement.startswith("section"):
                tokens = statement.split()
                if len(tokens) < 3:
                    continue
                try:
                    n = tokens.index("from")
                except ValueError:
                    n = len(tokens)
                if project != tokens[n+1]:
                    continue
                section = ' '.join(tokens[1:n])
                start = l1
                end_of_section = "<!-- end of section {} from {} -->\n"\
                    .format(section, project)
                continue
        if line == end_of_section:
            end = l1 + 1
            break
    if start is None:
        raise ValueError("Not found")
    section_content = read_section(source, section)
    with open(to, "wt") as f:
        for line in content[:start + 1]:
            f.write(line)
        f.write("\n")
        for line in section_content:
            f.write(line)
        f.write(end_of_section)
        if end is None:
            end = start + 2
        for line in content[end:]:
            f.write(line)
    return


if __name__ == '__main__':
    if len(sys.argv) > 3:
        prj = sys.argv[3]
    else:
        prj = None
    insert_section(sys.argv[1], sys.argv[2], prj)
