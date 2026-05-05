import ast
import networkx as nx

def build_cfg(nodes, G, prev_nodes):
    current_prev = prev_nodes
    for stmt in nodes:
        node_id = f"n{len(G.nodes)}"
        label = ast.unparse(stmt).split('\n')[0]
        G.add_node(node_id, label=label)

        for p in current_prev:
            G.add_edge(p, node_id)

        if isinstance(stmt, ast.If):
            if_last = build_cfg(stmt.body, G, [node_id])
            if stmt.orelse:
                else_last = build_cfg(stmt.orelse, G, [node_id])
                current_prev = if_last + else_last
            else:
                current_prev = if_last + [node_id]
        elif isinstance(stmt, (ast.Return, ast.Raise)):
            current_prev = []
            break
        else:
            current_prev = [node_id]
    return current_prev


with open("auth.py", "r") as f:
    code = f.read()

tree = ast.parse(code)
func = [n for n in tree.body if isinstance(n, ast.FunctionDef)][0]

G = nx.DiGraph()
G.add_node("start", label="START")

build_cfg(func.body, G, ["start"])

G.add_node("end", label="END")
for n in [node for node in G.nodes if G.out_degree(node) == 0 and node != "end"]:
    G.add_edge(n, "end")

paths = list(nx.all_simple_paths(G, source="start", target="end"))
print("Шляхи виконання (all_simple_paths):")
for path in paths:
    print(path)

E = G.number_of_edges()
N = G.number_of_nodes()
M = E - N + 2

print(f"Вузлів (N): {N}, Ребер (E): {E}")
print(f"Цикломатична складність: {M}")

nx.nx_pydot.write_dot(G, "cfg.dot")