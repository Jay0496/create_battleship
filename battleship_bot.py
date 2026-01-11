#!/usr/bin/env python3
"""
Code Clash Battleship Bot Challenge - CREATE UofT - Winter 2026

YOUR CUSTOM BATTLESHIP BOT STRATEGY
Override the strategy methods below to implement your bot.

===========================================
IMPORTANT:
===========================================
- DO NOT modify battleship_api.py
- ONLY override the 3 strategy methods below
- Use helper methods (starting with _) from the API
- Test your bot with bot_validator.py before submission

Have fun!
"""

import random
from typing import Any, Dict, List, Optional, Set, Tuple
from battleship_api import BattleshipBotAPI, run_bot, ABILITY_CODES, BOARD_SIZE

class MyBattleshipBot(BattleshipBotAPI):
    def ability_selection(self) -> list:
        """Choose 2 abilities for the entire game."""
        return ["SP", "RF"]  # Sonar Pulse and Hailstorm
    
    def place_ship_strategy(self, ship_name: str, game_state: dict) -> dict:
        """Place a ship on your board."""
        placed_coords = self._get_placed_coordinates(game_state)
        if ship_name in ('ship_1x2', 'ship_1x3'):
            placement = self._get_random_placement_small(ship_name, placed_coords, game_state)
        else: placement = self._get_random_placement(ship_name, placed_coords, game_state)

        if placement:
            return placement
        
        # Fallback
        return {
            "placement": {
                "cell": [0, 0],
                "direction": 'H'
            }
        }
    
    def _get_random_placement(self, ship_name: str, placed_coords: Set[Tuple[int, int]], game_state: dict) -> Optional[Dict[str, Any]]:
        """Generate random valid ship placement."""
        for _ in range(100):
            start_row = random.randint(0, 7)
            start_col = random.randint(0, 7)
            orientation = self._get_random_orientation()
            
            cells = self._get_ship_cells(ship_name, start_row, start_col, orientation)
            if cells and self._is_valid_placement(cells, placed_coords) and self._respects_border_rule(set(cells), game_state["player_ships"]):
                return {
                    "placement": {
                        "name": ship_name,
                        "cell": [start_row, start_col],
                        "direction": orientation
                    }
                }
        return None
    
    def  _get_random_placement_small(self, ship_name: str, placed_coords: Set[Tuple[int, int]], game_state: dict) -> Optional[Dict[str, Any]]:
        """Generate random valid ship placement for small ships."""
        valid_positions = [1, 2, 5, 6]
        for _ in range(100):
            start_row = random.choice(valid_positions)
            start_col = random.choice(valid_positions)
            orientation = self._get_random_orientation()

            size = ship_name.split('x')[1]
            border_collision = False

            if (orientation == 'H'):
                check_max_col = start_col + int(size) - 1
                if (check_max_col > 6):
                    border_collision = True

            if (orientation == 'V'):
                check_max_row = start_row + int(size) - 1
                if (check_max_row > 6):
                    border_collision = True

            cells = self._get_ship_cells(ship_name, start_row, start_col, orientation)
            if (cells and self._is_valid_placement(cells, placed_coords) and not border_collision and self._respects_border_rule(set(cells), game_state["player_ships"])):
                return {
                    "placement": {
                        "name": ship_name,
                        "cell": [start_row, start_col],
                        "direction": orientation
                    }
                }
        return None

    def _get_random_orientation(self):
        if random.random() <= 0.6:
            return 'V'
        return 'H'
    
    def _get_ship_border_cells(self, occupied_cells: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        """Given the cells occupied by a ship, return all adjacent (including diagonal) border cells, excluding the ship itself."""

        border_cells = set()

        neighbor_offsets = [
            (-1, -1), (-1, 0), (-1, 1),
            ( 0, -1),          ( 0, 1),
            ( 1, -1), ( 1, 0), ( 1, 1),
        ]

        for ship_row, ship_col in occupied_cells:
            for row_offset, col_offset in neighbor_offsets:
                neighbor_row = ship_row + row_offset
                neighbor_col = ship_col + col_offset

                if 0 <= neighbor_row < 8 and 0 <= neighbor_col < 8:
                    border_cells.add((neighbor_row, neighbor_col))

        # Remove the ship's own cells from its border
        return border_cells - occupied_cells

    def _respects_border_rule(self, candidate_cells: Set[Tuple[int, int]], placed_ships: list) -> bool:
        """Ensure the candidate ship overlaps at most ONE border cell of EACH already placed ship."""

        for placed_ship in placed_ships:
            occupied_cells = {
                tuple(cell) for cell in placed_ship.get("coordinates", [])
            }

            border_zone = self._get_ship_border_cells(occupied_cells)

            border_overlap = len(candidate_cells & border_zone)

            if border_overlap > 1:
                return False

        return True
    
    # !---------------- COMBAT STRATEGY ----------------
    def combat_strategy(self, game_state: dict) -> dict:
        
        """Choose a combat move."""
        available_abilities = self._get_available_abilities(game_state)
        opponent_grid = self._get_opponent_grid(game_state)
        available_cells = self._get_available_cells(opponent_grid)
        ability = {"None": {}}
        
        # 1 random target if not using RF, 2 if using RF
        target = self._get_target_cell(opponent_grid) 
        
        if "RF" in available_abilities:
            RF_targets = self._get_target_cell(opponent_grid, RFability=True) 
            ability = {"RF": RF_targets}
        elif target:
            target = target[0]
        elif available_cells:
            target = random.choice(available_cells)
        else:
            target = [0, 0]

        return {
            "combat": {
                "cell": target,
                "ability": ability
            }
        }
    
    def _is_valid_cell(self, row:int, col:int) -> bool:
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE 

    def _get_first_hit_cluster(self, opponent_grid: List[List[str]], visited = set()) -> List[List[int]]:
        rows = BOARD_SIZE
        cols = BOARD_SIZE

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        visited = set()

        for r in range(rows):
            for c in range(cols):
                if opponent_grid[r][c] == 'H' and (r, c) not in visited:
                    stack = [(r, c)]
                    cluster: List[List[int]] = []
                    # iterates through grid finding an H and append to cluster
                    while stack:
                        cluster_row, cluster_c = stack.pop()
                        if (cluster_row, cluster_c) in visited:
                            continue

                        visited.add((cluster_row, cluster_c))
                        cluster.append([cluster_row, cluster_c])
                        # further visit all 4 neighbours of H, append if unvisited
                        for dr, dc in directions:
                            nr, nc = cluster_row + dr, cluster_c + dc
                            if (
                                0 <= nr < rows and
                                0 <= nc < cols and
                                opponent_grid[nr][nc] == 'H' and
                                (nr, nc) not in visited
                            ):
                                stack.append((nr, nc))
                    return cluster  # return first ship cluster found
        return []  # no hit ships found
 
    # checks for cells, H -- ships that have been hit but likely not fully sunk
        # if ship hit --> keep hitting around ship to sink
    # cluster of H's with N's around it
    def _get_target_cell(self, opponent_grid: List[List[str]], RFability=False) -> List[List[int]]:
        # first ship / cluster of Hs
        cluster = self._get_first_hit_cluster(opponent_grid)
        if not cluster:
            return []  # no Hs --> no target

        directions = [(-1,0),(1,0),(0,-1),(0,1)]
        targets: List[List[int]] = []

        # collect all valid N neighbours of H cluster 
        for r, c in cluster:
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if self._is_valid_cell(nr, nc) and opponent_grid[nr][nc] == 'N':
                    pair = [nr, nc]
                    if pair not in targets:
                        targets.append(pair)

        if RFability:
            # if at least two N neighbours, return first 2
            if len(targets) >= 2:
                return [targets[0], targets[1]]
            # if only one N neighbour, pick a second random N 
            if len(targets) == 1:
                other_Ns = [cell for cell in self._get_available_cells(opponent_grid) if cell != targets[0]]
                if other_Ns:
                    return [targets[0], random.choice(other_Ns)]
                # fallback: duplicate the single target so caller gets two entries
                return [targets[0], targets[0]]
            return []  # no neighbours found
        # RFability False: return one neighbour to preserve existing callers
        return targets[:1]
        
if __name__ == '__main__':
    run_bot(MyBattleshipBot)