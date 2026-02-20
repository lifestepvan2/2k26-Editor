from __future__ import annotations

import ast
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path("nba2k_editor")
JSON_OUT = ROOT / "call_graph.json"
MD_OUT = ROOT / "CALL_GRAPH.md"


@dataclass
class DefInfo:
    node_id: str
    module: str
    qualname: str
    file: str
    line: int
    class_path: tuple[str, ...]
    parent_func: str | None
    node: ast.AST


def _module_name_for(path: Path) -> str:
    return ".".join(path.with_suffix("").parts)


def _resolve_from_module(current_module: str, level: int, module: str | None) -> str:
    parts = current_module.split(".")
    pkg = parts[:-1]
    if level > 0:
        up = level - 1
        if up > 0:
            pkg = pkg[:-up]
    if module:
        pkg += module.split(".")
    return ".".join(pkg)


def _expr_text(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:
        return node.__class__.__name__


def _flatten_attr(node: ast.AST) -> list[str] | None:
    parts: list[str] = []
    cur = node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        parts.append(cur.id)
        parts.reverse()
        return parts
    return None


def collect_modules(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts or ".ruff_cache" in path.parts:
            continue
        files.append(path)
    return files


def parse_modules(files: list[Path]) -> dict[str, dict[str, Any]]:
    modules: dict[str, dict[str, Any]] = {}
    for file in files:
        module = _module_name_for(file)
        tree = ast.parse(file.read_text(encoding="utf-8", errors="ignore"), filename=str(file))
        modules[module] = {
            "path": str(file).replace("\\", "/"),
            "tree": tree,
            "module_node_id": f"{module}::<module>",
            "defs": {},
            "defs_by_node": {},
            "top_funcs": {},
            "top_classes": {},
            "class_methods": {},
            "class_inits": {},
            "imports_module": {},
            "imports_symbol": {},
            "local_defs": {},
        }
    return modules


def collect_defs(modules: dict[str, dict[str, Any]]) -> None:
    for module, info in modules.items():
        tree: ast.Module = info["tree"]

        def walk_body(
            body: list[ast.stmt],
            class_stack: list[str],
            func_stack: list[str],
            parent_func: str | None,
        ) -> None:
            # direct local defs for current lexical scope
            direct_map: dict[str, str] = {}
            for stmt in body:
                if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    qual = ".".join(class_stack + func_stack + [stmt.name])
                    direct_map[stmt.name] = f"{module}::{qual}"
            if parent_func is not None:
                info["local_defs"][parent_func] = direct_map

            for stmt in body:
                if isinstance(stmt, ast.ClassDef):
                    class_stack.append(stmt.name)
                    if not func_stack and len(class_stack) == 1:
                        info["top_classes"][stmt.name] = ".".join(class_stack)
                    walk_body(stmt.body, class_stack, func_stack, parent_func)
                    class_stack.pop()
                    continue
                if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    qual = ".".join(class_stack + func_stack + [stmt.name])
                    node_id = f"{module}::{qual}"
                    di = DefInfo(
                        node_id=node_id,
                        module=module,
                        qualname=qual,
                        file=info["path"],
                        line=stmt.lineno,
                        class_path=tuple(class_stack),
                        parent_func=parent_func,
                        node=stmt,
                    )
                    info["defs"][node_id] = di
                    info["defs_by_node"][id(stmt)] = node_id
                    if not class_stack and not func_stack:
                        info["top_funcs"][stmt.name] = node_id
                    if class_stack:
                        cls = ".".join(class_stack)
                        info["class_methods"][(cls, stmt.name)] = node_id
                        if stmt.name == "__init__":
                            info["class_inits"][cls] = node_id
                    func_stack.append(stmt.name)
                    walk_body(stmt.body, class_stack, func_stack, node_id)
                    func_stack.pop()

        walk_body(tree.body, [], [], None)


def collect_imports(modules: dict[str, dict[str, Any]]) -> None:
    module_names = set(modules.keys())
    for module, info in modules.items():
        tree: ast.Module = info["tree"]
        for stmt in tree.body:
            if isinstance(stmt, ast.Import):
                for alias in stmt.names:
                    target = alias.name
                    asname = alias.asname or alias.name.split(".")[0]
                    if target in module_names or target.startswith("nba2k_editor"):
                        info["imports_module"][asname] = target
            elif isinstance(stmt, ast.ImportFrom):
                resolved = _resolve_from_module(module, stmt.level, stmt.module)
                if not resolved.startswith("nba2k_editor"):
                    continue
                for alias in stmt.names:
                    if alias.name == "*":
                        continue
                    asname = alias.asname or alias.name
                    info["imports_symbol"][asname] = (resolved, alias.name)


def build_symbol_indexes(modules: dict[str, dict[str, Any]]) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    top_funcs: dict[str, dict[str, str]] = {}
    top_classes: dict[str, dict[str, str]] = {}
    class_inits: dict[str, dict[str, str]] = {}
    for module, info in modules.items():
        top_funcs[module] = dict(info["top_funcs"])
        top_classes[module] = dict(info["top_classes"])
        class_inits[module] = dict(info["class_inits"])
    return top_funcs, top_classes, class_inits


def resolve_symbol_target(
    module: str,
    info: dict[str, Any],
    name: str,
    current_def: DefInfo | None,
    top_funcs: dict[str, dict[str, str]],
    top_classes: dict[str, dict[str, str]],
    class_inits: dict[str, dict[str, str]],
) -> list[str]:
    targets: list[str] = []

    # local/nested defs in current or ancestor function scopes
    if current_def is not None:
        check: str | None = current_def.node_id
        while check is not None:
            local_map = info["local_defs"].get(check, {})
            if name in local_map:
                targets.append(local_map[name])
                return targets
            parent = info["defs"].get(check)
            check = parent.parent_func if parent else None

    if name in info["top_funcs"]:
        targets.append(info["top_funcs"][name])
        return targets

    if name in info["imports_symbol"]:
        target_module, target_name = info["imports_symbol"][name]
        if target_name in top_funcs.get(target_module, {}):
            targets.append(top_funcs[target_module][target_name])
        elif target_name in top_classes.get(target_module, {}):
            cls = top_classes[target_module][target_name]
            init = class_inits.get(target_module, {}).get(cls)
            if init:
                targets.append(init)
        return targets

    if name in info["top_classes"]:
        cls = info["top_classes"][name]
        init = info["class_inits"].get(cls)
        if init:
            targets.append(init)
    return targets


def resolve_expr_targets(
    expr: ast.AST,
    module: str,
    info: dict[str, Any],
    current_def: DefInfo | None,
    top_funcs: dict[str, dict[str, str]],
    top_classes: dict[str, dict[str, str]],
    class_inits: dict[str, dict[str, str]],
) -> list[str]:
    if isinstance(expr, ast.Name):
        return resolve_symbol_target(module, info, expr.id, current_def, top_funcs, top_classes, class_inits)

    if isinstance(expr, ast.Attribute):
        # self.method() / cls.method()
        if isinstance(expr.value, ast.Name) and expr.value.id in {"self", "cls"} and current_def is not None and current_def.class_path:
            cls = ".".join(current_def.class_path)
            hit = info["class_methods"].get((cls, expr.attr))
            return [hit] if hit else []

        # imported module aliases (direct or chained)
        chain = _flatten_attr(expr)
        if chain:
            root = chain[0]
            if root in info["imports_module"]:
                base_mod = info["imports_module"][root]
                attr = chain[-1]
                mid = chain[1:-1]
                target_module = ".".join([base_mod, *mid]) if mid else base_mod
                out: list[str] = []
                if attr in top_funcs.get(target_module, {}):
                    out.append(top_funcs[target_module][attr])
                elif attr in top_classes.get(target_module, {}):
                    cls = top_classes[target_module][attr]
                    init = class_inits.get(target_module, {}).get(cls)
                    if init:
                        out.append(init)
                return out
    return []


def walk_calls(node: ast.AST) -> list[ast.Call]:
    calls: list[ast.Call] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            calls.append(child)
    return calls


def build_edges(modules: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, set[str]], dict[str, set[str]], dict[str, set[str]]]:
    top_funcs, top_classes, class_inits = build_symbol_indexes(modules)
    edge_keys: set[tuple[str, str, str, int]] = set()
    edges: list[dict[str, Any]] = []
    callers: dict[str, set[str]] = defaultdict(set)
    callees: dict[str, set[str]] = defaultdict(set)
    callback_edges: dict[str, set[str]] = defaultdict(set)

    def add_edge(src: str, dst: str, kind: str, line: int, expr_text: str) -> None:
        key = (src, dst, kind, line)
        if key in edge_keys:
            return
        edge_keys.add(key)
        edges.append({"source": src, "target": dst, "kind": kind, "line": line, "expr": expr_text})
        if kind == "callback_ref":
            callback_edges[src].add(dst)
        else:
            callers[dst].add(src)
            callees[src].add(dst)

    for module, info in modules.items():
        module_node = info["module_node_id"]
        info["defs"][module_node] = DefInfo(
            node_id=module_node,
            module=module,
            qualname="<module>",
            file=info["path"],
            line=1,
            class_path=tuple(),
            parent_func=None,
            node=info["tree"],
        )

        # module-level calls
        for call in walk_calls(info["tree"]):
            targets = resolve_expr_targets(call.func, module, info, None, top_funcs, top_classes, class_inits)
            for t in targets:
                add_edge(module_node, t, "call", getattr(call, "lineno", 0), _expr_text(call.func))

        # function-level calls
        for node_id, def_info in list(info["defs"].items()):
            if node_id == module_node:
                continue
            for call in walk_calls(def_info.node):
                targets = resolve_expr_targets(call.func, module, info, def_info, top_funcs, top_classes, class_inits)
                for t in targets:
                    add_edge(def_info.node_id, t, "call", getattr(call, "lineno", 0), _expr_text(call.func))

                # callback references (function object passed as arg/kw)
                arg_nodes: list[ast.AST] = list(call.args) + [kw.value for kw in call.keywords]
                for arg in arg_nodes:
                    if not isinstance(arg, (ast.Name, ast.Attribute)):
                        continue
                    cb_targets = resolve_expr_targets(arg, module, info, def_info, top_funcs, top_classes, class_inits)
                    for t in cb_targets:
                        add_edge(def_info.node_id, t, "callback_ref", getattr(arg, "lineno", 0), _expr_text(arg))

    edges.sort(key=lambda e: (e["source"], e["line"], e["target"], e["kind"]))
    return edges, callers, callees, callback_edges


def write_outputs(
    modules: dict[str, dict[str, Any]],
    edges: list[dict[str, Any]],
    callers: dict[str, set[str]],
    callees: dict[str, set[str]],
    callback_edges: dict[str, set[str]],
) -> None:
    nodes: list[dict[str, Any]] = []
    all_defs: dict[str, DefInfo] = {}
    for info in modules.values():
        all_defs.update(info["defs"])
    for node_id, di in sorted(all_defs.items(), key=lambda kv: (kv[1].module, kv[1].line, kv[1].qualname)):
        nodes.append(
            {
                "id": node_id,
                "module": di.module,
                "qualname": di.qualname,
                "file": di.file,
                "line": di.line,
                "type": "module" if di.qualname == "<module>" else "function",
                "calls": sorted(callees.get(node_id, set())),
                "called_by": sorted(callers.get(node_id, set())),
                "callback_refs": sorted(callback_edges.get(node_id, set())),
            }
        )

    payload = {
        "summary": {
            "nodes": len(nodes),
            "edges": len(edges),
            "call_edges": sum(1 for e in edges if e["kind"] == "call"),
            "callback_edges": sum(1 for e in edges if e["kind"] == "callback_ref"),
            "modules": len(modules),
        },
        "nodes": nodes,
        "edges": edges,
    }
    JSON_OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Call Graph (Static)",
        "",
        "Generated from AST analysis. This captures static call/callback references in `nba2k_editor`.",
        "",
        "## Summary",
        f"- Modules: {payload['summary']['modules']}",
        f"- Nodes (functions + module scopes): {payload['summary']['nodes']}",
        f"- Call edges: {payload['summary']['call_edges']}",
        f"- Callback-reference edges: {payload['summary']['callback_edges']}",
        "",
        "## Artifacts",
        "- Machine-readable graph: `call_graph.json`",
        "- This index: `CALL_GRAPH.md`",
        "",
        "## Limitations",
        "- Dynamic dispatch (`getattr`, reflective calls), runtime monkey-patching, and library-internal callbacks may not resolve.",
        "- Import aliasing and chained attributes are resolved best-effort for in-repo modules only.",
        "- This graph is static and does not represent runtime execution frequency or conditional reachability.",
        "",
        "## How To Trace",
        "1. Locate a node id in `call_graph.json` (format: `module::qualname`).",
        "2. Check its `calls`, `called_by`, and `callback_refs` arrays.",
        "3. Use `edges` for line-level detail and edge kind.",
        "",
        "## Top Fan-Out Nodes",
    ]

    fan_out = sorted(((n["id"], len(n["calls"])) for n in nodes), key=lambda x: x[1], reverse=True)[:25]
    for node_id, count in fan_out:
        if count > 0:
            lines.append(f"- `{node_id}` -> {count} calls")

    lines.extend(["", "## Top Fan-In Nodes"])
    fan_in = sorted(((n["id"], len(n["called_by"])) for n in nodes), key=lambda x: x[1], reverse=True)[:25]
    for node_id, count in fan_in:
        if count > 0:
            lines.append(f"- `{node_id}` <- {count} callers")

    lines.extend(["", "## Module Index"])
    by_module: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for n in nodes:
        by_module[n["module"]].append(n)
    for module in sorted(by_module):
        lines.append(f"### `{module}`")
        for n in sorted(by_module[module], key=lambda x: (x["line"], x["qualname"])):
            lines.append(
                f"- `{n['id']}` | calls={len(n['calls'])} called_by={len(n['called_by'])} callback_refs={len(n['callback_refs'])}"
            )
        lines.append("")

    MD_OUT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    files = collect_modules(ROOT)
    modules = parse_modules(files)
    collect_defs(modules)
    collect_imports(modules)
    edges, callers, callees, callback_edges = build_edges(modules)
    write_outputs(modules, edges, callers, callees, callback_edges)
    print(f"Wrote {JSON_OUT} and {MD_OUT}")


if __name__ == "__main__":
    main()
