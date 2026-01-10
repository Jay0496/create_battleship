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
from typing import Any, Dict, Optional, Set, Tuple
from battleship_api import BattleshipBotAPI, run_bot, ABILITY_CODES

class MyBattleshipBot(BattleshipBotAPI):
    def ability_selection(self) -> list:
        """Choose 2 abilities for the entire game."""
        return ["SP", "HS"]  # Sonar Pulse and Hailstorm
    
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

    
    def combat_strategy(self, game_state: dict) -> dict:
        """Choose a combat move."""
        # TODO: Replace with your strategy
        available_abilities = self._get_available_abilities(game_state)
        opponent_grid = self._get_opponent_grid(game_state)
        available_cells = self._get_available_cells(opponent_grid)
        
        if available_cells:
            target = random.choice(available_cells)
        else:
            target = [random.randint(0, 7), random.randint(0, 7)]
        
        return {
            "combat": {
                "cell": target,
                "ability": {"None": {}}
            }
        }

if __name__ == '__main__':
    run_bot(MyBattleshipBot)