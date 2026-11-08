"""Print the scene names of an explainer's main.py, one per line, in playing order.

usage: python3 scripts/scenes.py explainers/02-mle/main.py

The order is SCENES_IN_ORDER when the file defines it (ManimGL uses the same list),
otherwise the order of the scene classes in the file. Reads the file without running it.
"""
import ast
import sys

tree = ast.parse(open(sys.argv[1], encoding="utf-8").read())
body = tree.body

for node in body:
    if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "SCENES_IN_ORDER" for t in node.targets):
        print("\n".join(element.id for element in node.value.elts))
        sys.exit()

scene_names = set()
for node in body:
    if isinstance(node, ast.ClassDef):
        bases = {getattr(base, "id", getattr(base, "attr", "")) for base in node.bases}
        if any(name.endswith("Scene") or name in scene_names for name in bases):
            scene_names.add(node.name)
            print(node.name)
