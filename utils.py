def get_neighbor_position(node, neighbor):
    x1, y1 = node
    x2, y2 = neighbor

    if x2 == x1 + 1 and y2 == y1:
        return 90
    elif x2 == x1 - 1 and y2 == y1:
        return 270
    elif x2 == x1 and y2 == y1 - 1:
        return 0
    elif x2 == x1 and y2 == y1 + 1:
        return 180
    else:
        return None