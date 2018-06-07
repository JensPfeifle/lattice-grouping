from collections import defaultdict


def read_beams_from_inp(beam_lines):
    beams = {}
    for data_line in beam_lines:
        eid, node1, node2 = data_line.split(',')
        eid = int(eid.strip())
        node1 = int(node1.strip())
        node2 = int(node2.strip())
        beams[eid] = (node1, node2)
    return beams


def associate_beams_to_nodes(beam_lines):
    nodes_dict = defaultdict(list)
    for data_line in beam_lines:
        eid, node1, node2 = data_line.split(',')
        eid = int(eid.strip())
        node1 = int(node1.strip())
        node2 = int(node2.strip())
        nodes_dict[node1].append(eid)
        nodes_dict[node2].append(eid)
    return nodes_dict


def get_node_sets(beam_node_associations):
    lattice_node_nodes = set()
    lattice_end_nodes = set()
    lattice_inner_nodes = set()
    for nid, elems in beam_node_associations.items():
        if len(elems) < 2:
            lattice_end_nodes.add(nid)
        if len(elems) > 2:
            lattice_node_nodes.add(nid)
        else:
            lattice_inner_nodes.add(nid)
    return {'ends': lattice_end_nodes, 'nodes': lattice_node_nodes, 'inner': lattice_inner_nodes}


def get_element_sets(beam_node_associations):
    lattice_node_elems = set()
    lattice_end_elems = set()
    lattice_inner_elems = set()
    for nid, elems in beams_by_node.items():
        if len(elems) < 2:
            [lattice_end_elems.add(e) for e in elems]
        if len(elems) > 2:
            [lattice_node_elems.add(e) for e in elems]
        else:
            [lattice_inner_elems.add(e) for e in elems]
    return {'ends': lattice_end_elems, 'nodes': lattice_node_elems, 'inner': lattice_inner_elems}


def get_groups_at_node(node_id):
    groups = []
    attached_elems = beams_by_node[node_id]
    for elem_id in attached_elems:
        this_group = set()
        current_node = node_id
        current_elem = elem_id
        at_end = False
        while (not at_end):
            node1, node2 = beams[current_elem]
            # print('element {} is attached to nodes {} and {}'.format(current_elem,node1,node2))
            if node1 == current_node:
                next_node = node2
            else:
                next_node = node1
            # print('checking node {}'.format(next_node))
            current_node = next_node
            elems = beams_by_node[next_node]
            # print('elements {} are attached to node {}'.format(elems, next_node))
            if len(elems) == 2:
                elem1, elem2 = elems
                if elem1 == current_elem:
                    next_elem = elem2
                else:
                    next_elem = elem1
            else:
                # print('at end or lattice node')
                at_end = True
            # print('checking elem {}'.format(next_elem))
            this_group.add(current_elem)
            current_elem = next_elem
            # print('EOL')
        if len(this_group) == 0:
            print('zero size group at node {}, elem {}'.format(node_id, elem_id))
        else:
            groups.append(this_group)
    # print('Found {} groups at node {}'.format(len(groups), node_id))
    return groups


# TODO: modify this to get element group starting from any element
def get_group_of_elem(elem_id):
    this_group = set()
    current_elem = elem_id
    at_end = False
    while (not at_end):
        node1, node2 = beams[current_elem]
        # print('element {} is attached to nodes {} and {}'.format(current_elem,node1,node2))
        if node1 == current_node:
            next_node = node2
        else:
            next_node = node1
        # print('checking node {}'.format(next_node))
        current_node = next_node
        elems = beams_by_node[next_node]
        # print('elements {} are attached to node {}'.format(elems, next_node))
        if len(elems) == 2:
            elem1, elem2 = elems
            if elem1 == current_elem:
                next_elem = elem2
            else:
                next_elem = elem1
        else:
            # print('at end or lattice node')
            at_end = True
        # print('checking elem {}'.format(next_elem))
        this_group.add(current_elem)
        current_elem = next_elem
        # print('EOL')
    if len(this_group) == 0:
        print('zero size group at node {}, elem {}'.format(node_id, elem_id))
    return this_group


def elset_for_inp(name, elems):
    header_line = '*Elset, elset=_name_'
    header_line = header_line.replace('_name_', name)
    data_line = ''
    for n, e in enumerate(elems):
        if n % 10 == 0:
            data_line += '\n'
        data_line += str(e) + ','
    data_line += '\n'
    return header_line + data_line


def dvcon_block_for_par(names):
    header = '''
DVCON_SIZING
  ID_NAME        = MY_DVCON_SIZING
  CHECK_TYPE     = CLUSTER_GROUPS
'''
    data_lines = ''
    for name in names:
        data_lines += '  EL_GROUP       = {}\n'.format(name)

    return header + data_lines + 'END_\n'


if __name__ == '__main__':
    INPUT_FILE = 'Job-12-Triangles.inp'

    with open(INPUT_FILE, 'r') as f:
        file_contents = f.readlines()

    beam_lines = file_contents[47513:92978]
    shell_lines = file_contents[1332:2212]

    # get elements as {eid:[node1, node2]}
    beams = read_beams_from_inp(beam_lines)
    beams_by_node = associate_beams_to_nodes(beam_lines)

    element_list = list(beams.keys())

    group = get_group_of_elem(element_list[5])

    """
    groups_at_nodes = {}
    for n in lattice_node_nodes:
        groups_at_nodes[n] = get_groups_at_node(n)

    flat_groups = [g for k, ng in groups_at_nodes.items() for g in ng]

    unique_sets = list(set(frozenset(fg) for fg in flat_groups))
    # convert back to set
    # [set(item) for item in set(frozenset(item) for item in L)]#
    
    num_sets = len(unique_sets)
    print('Writing {} element sets to output.inp'.format(num_sets))
    set_names = ['beams_{:06}'.format(n + 1) for n in range(num_sets)]
    with open('output.inp', 'w') as f:
        for n, elemset in enumerate(unique_sets):
            f.write(elset_for_inp(set_names[n], elemset))
    with open('dvcon.par', 'w') as f:
        f.write(dvcon_block_for_par(set_names))
    """
