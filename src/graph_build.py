import networkx as nx
from common import database

def normalize(name):
    if not name:
        return None
    return ' '.join(name.upper().split())

def build_graph():
    g = nx.DiGraph()

    persons = list(database['sa_pa_persons'])
    directorships = list(database['sa_pa_directorships'])
    mines = list(database['sa_mines'])

    # Index mines by normalized owner name for the bridge join
    mines_by_owner = {}
    for mine in mines:
        owner_key = normalize(mine.get('mine_owner'))
        if owner_key:
            mines_by_owner.setdefault(owner_key, []).append(mine)

    # Person nodes
    for p in persons:
        g.add_node(f"person:{p['popit_id']}", label=p['name'], kind='person')

    # Directorship edges: person -> company
    company_keys_seen = set()
    for d in directorships:
        person_node = f"person:{d['person_id']}"
        if person_node not in g:
            continue
        company_key = normalize(d.get('company_name'))
        if not company_key:
            continue
        company_node = f"company:{company_key}"
        if company_key not in company_keys_seen:
            g.add_node(company_node, label=d['company_name'], kind='company')
            company_keys_seen.add(company_key)
        g.add_edge(person_node, company_node, relation='directorship', report=d.get('report'))

        # Bridge: does this company own any mines?
        for mine in mines_by_owner.get(company_key, []):
            mine_node = f"mine:{mine['mine_code']}"
            if mine_node not in g:
                g.add_node(mine_node, label=mine['mine_name'], kind='mine')
            g.add_edge(company_node, mine_node, relation='owns')

    return g

if __name__ == '__main__':
    g = build_graph()
    print(f"Nodes: {g.number_of_nodes()}")
    print(f"Edges: {g.number_of_edges()}")
    kinds = {}
    for _, data in g.nodes(data=True):
        kinds[data['kind']] = kinds.get(data['kind'], 0) + 1
    print(f"By kind: {kinds}")
    nx.write_graphml(g, '../data/madlanga_graph.graphml')
    print("Saved to data/madlanga_graph.graphml")