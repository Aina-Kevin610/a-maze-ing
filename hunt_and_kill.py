import random

def remove_wall(self, grid, visited, x, y, xn, yn):
    dx, dy = xn - x, yn - y
    if dx == 1:   dir, opp = 0b0010, 0b1000
    elif dx == -1:dir, opp = 0b1000, 0b0010
    elif dy == 1: dir, opp = 0b0100, 0b0001
    elif dy == -1:dir, opp = 0b0001, 0b0100
    else: raise ValueError("Cellules non adjacentes")

    grid[y][x]  &= ~dir
    grid[yn][xn] &= ~opp
    visited[yn][xn] = True
    return xn, yn

def get_neighbors(self, visited, x, y):
    way = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    neighbors = []
    for dx, dy in way:
        xn, yn = x + dx, y + dy
        if 0 <= xn < self.width and 0 <= yn < self.height and not visited[yn][xn]:
            neighbors.append((xn, yn))  # ✅ Tuple unique
    return neighbors

def hunt_and_kill(self):  # (tu peux garder le nom dfs si tu veux)
    grid = [[0b1111 for _ in range(self.width)] for _ in range(self.height)]
    visited = [[False] * self.width for _ in range(self.height)]
    
    # Point de départ valide
    x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
    visited[y][x] = True
    
    # Optimisation : reprendre le scan Hunt là où il s'est arrêté
    hunt_x, hunt_y = 0, 0

    while True:
        # ================= PHASE KILL =================
        while True:
            neighbors = self.get_neighbors(visited, x, y)
            if not neighbors:
                break  # Cul-de-sac → passer à Hunt
                
            xn, yn = random.choice(neighbors)
            x, y = self.remove_wall(grid, visited, x, y, xn, yn)

        # ================= PHASE HUNT =================
        found = False
        for sy in range(hunt_y, self.height):
            start_sx = hunt_x if sy == hunt_y else 0
            for sx in range(start_sx, self.width):
                if not visited[sy][sx]:  # Cellule non visitée trouvée
                    # Vérifie si elle touche une cellule déjà visitée
                    for dx, dy in [(0,-1), (1,0), (0,1), (-1,0)]:
                        nx, ny = sx + dx, sy + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height and visited[ny][nx]:
                            x, y = self.remove_wall(grid, visited, sx, sy, nx, ny)
                            hunt_x, hunt_y = sx, sy
                            found = True
                            break
                if found: break
            if found: break

        if not found:
            break  # ✅ Plus de cellule non visitée → labyrinthe terminé

    self.print_maze(grid, visited)  # Affichage unique à la fin