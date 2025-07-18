def get_all_paths(graph, src, dest):
        paths = []

        def dfs(node, path, visited):
            if node == dest:
                paths.append(path[:])
                return
            for neighbor, _ in graph.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    path.append(neighbor)
                    dfs(neighbor, path, visited)
                    path.pop()
                    visited.remove(neighbor)

        dfs(src, [src], set([src]))
        return paths