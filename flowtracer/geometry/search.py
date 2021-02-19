from scipy.spatial import KDTree


def create_search_tree(nodes):
    print("\nBuilding spatial search index...")
    kdtree = KDTree(nodes[:, (0, 1)])
    return kdtree
