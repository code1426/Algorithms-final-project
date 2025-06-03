import pygame
from typing import Dict, Tuple, Any
from constants import *

class UIManager:
    
    def __init__(self):
        self.font = pygame.font.SysFont('arial', 16)
        self.title_font = pygame.font.SysFont('arial', 20, bold=True)
        self.button_positions: Dict[str, Any] = {}
        
    def draw_ui(self, window: pygame.Surface, app_state: Dict[str, Any]) -> None:
        # Define UI panel area
        ui_panel = pygame.Rect(GRID_COLS * CELL_SIZE, 0,
                              WINDOW_WIDTH - GRID_COLS * CELL_SIZE, WINDOW_HEIGHT)
        pygame.draw.rect(window, BG_LIGHT, ui_panel)
        
        y_offset = 20
        button_x = GRID_COLS * CELL_SIZE + BUTTON_MARGIN
        
        # Draw title
        y_offset = self._draw_title(window, y_offset)
        
        # Draw instructions
        y_offset = self._draw_instructions(window, y_offset)
        
        # Draw control buttons
        y_offset = self._draw_wall_generation_controls(window, button_x, y_offset, app_state)
        y_offset = self._draw_pathfinding_controls(window, button_x, y_offset, app_state)
        y_offset = self._draw_speed_controls(window, button_x, y_offset, app_state)
        y_offset = self._draw_clear_controls(window, button_x, y_offset, app_state)
        
        # Draw status and path info
        self._draw_status_info(window, button_x, y_offset, app_state)
    
    def _draw_title(self, window: pygame.Surface, y_offset: int) -> int:
        title = self.title_font.render("Dijkstra's Algorithm", True, TEXT_PRIMARY)
        window.blit(title, (GRID_COLS * CELL_SIZE + 20, y_offset))
        return y_offset + 40
    
    def _draw_instructions(self, window: pygame.Surface, y_offset: int) -> int:
        instructions = [
            "1. Click to set START point",
            "2. Click to set END point", 
            "3. Click 'Find Path' to run",
            "",
            "Controls:",
            "• Left click: Set points",
            "• Right click: Toggle walls",
            "• Hold and drag: Draw walls",
            "• Space: Find/Pause path",
            "• C: Clear path",
            "• R: Reset all"
        ]
        
        for instruction in instructions:
            text_surface = self.font.render(instruction, True, TEXT_SECONDARY)
            window.blit(text_surface, (GRID_COLS * CELL_SIZE + 20, y_offset))
            y_offset += 20
            
        return y_offset + 20
    
    def _draw_wall_generation_controls(self, window: pygame.Surface, button_x: int, 
                                     y_offset: int, app_state: Dict[str, Any]) -> int:

        can_interact = app_state['can_interact_with_grid']
        wall_type = app_state['wall_type']
        
        # Generate Walls button
        generate_enabled = can_interact
        generate_color = BUTTON_NORMAL if generate_enabled else BUTTON_DISABLED
        generate_rect = pygame.Rect(button_x, y_offset, BUTTON_WIDTH, BUTTON_HEIGHT)
        
        self.button_positions['generate_wall'] = (generate_rect, generate_enabled)
        
        pygame.draw.rect(window, generate_color, generate_rect)
        pygame.draw.rect(window, ACCENT if generate_enabled else BG_DARK, generate_rect, 2)
        
        text_color = TEXT_PRIMARY if generate_enabled else TEXT_SECONDARY
        generate_text = self.font.render("Generate Walls", True, text_color)
        text_rect = generate_text.get_rect(center=generate_rect.center)
        window.blit(generate_text, text_rect)
        
        y_offset += BUTTON_HEIGHT + BUTTON_MARGIN
        
        # Wall type buttons
        wall_types = ["Maze", "Random"]
        wall_type_keys = ['maze', 'random']
        self.button_positions['wall_types'] = []
        
        for i, (wtype_name, wtype_key) in enumerate(zip(wall_types, wall_type_keys)):
            if generate_enabled and wall_type == wtype_key:
                color = BUTTON_ACTIVE
            elif generate_enabled:
                color = BUTTON_NORMAL
            else:
                color = BUTTON_DISABLED
                
            type_rect = pygame.Rect(button_x + i * 55, y_offset, 50, 30)
            self.button_positions['wall_types'].append((type_rect, wtype_key, generate_enabled))
            
            pygame.draw.rect(window, color, type_rect)
            pygame.draw.rect(window, BG_DARK, type_rect, 1)
            
            text_color = TEXT_PRIMARY if generate_enabled else TEXT_SECONDARY
            type_text = pygame.font.SysFont('arial', 12).render(wtype_name, True, text_color)
            text_rect = type_text.get_rect(center=type_rect.center)
            window.blit(type_text, text_rect)
            
        return y_offset + 40
    
    def _draw_pathfinding_controls(self, window: pygame.Surface, button_x: int,
                                 y_offset: int, app_state: Dict[str, Any]) -> int:

        is_pathfinding = app_state['is_pathfinding_in_progress']
        is_paused = app_state['pathfinding_paused']
        can_start = app_state['can_start_pathfinding']
        
        # Determine button text and color
        if is_pathfinding:
            if is_paused:
                path_color = STATUS_WARNING
                path_text_str = "Resume Path Finding"
            else:
                path_color = STATUS_ERROR
                path_text_str = "Pause Path Finding"
            path_enabled = True
        elif can_start:
            path_color = STATUS_SUCCESS
            path_text_str = "Find Shortest Path"
            path_enabled = True
        else:
            path_color = BUTTON_DISABLED
            path_text_str = "Find Shortest Path"
            path_enabled = False
        
        path_rect = pygame.Rect(button_x, y_offset, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.button_positions['find_path'] = (path_rect, path_enabled)
        
        pygame.draw.rect(window, path_color, path_rect)
        pygame.draw.rect(window, ACCENT if path_enabled else BG_DARK, path_rect, 2)
        
        text_color = TEXT_PRIMARY if path_enabled else TEXT_SECONDARY
        path_text = self.font.render(path_text_str, True, text_color)
        text_rect = path_text.get_rect(center=path_rect.center)
        window.blit(path_text, text_rect)
        
        return y_offset + BUTTON_HEIGHT + BUTTON_MARGIN
    
    def _draw_speed_controls(self, window: pygame.Surface, button_x: int,
                           y_offset: int, app_state: Dict[str, Any]) -> int:

        current_speed = app_state['speed']
        is_pathfinding = app_state['is_pathfinding_in_progress']
        
        speed_text = self.font.render("Pathfinding Speed:", True, TEXT_PRIMARY)
        window.blit(speed_text, (button_x, y_offset))
        y_offset += 25
        
        speeds = [("Normal", NORMAL_SPEED), ("Fast", FAST_SPEED), ("Instant", INSTANT_SPEED)]
        self.button_positions['speeds'] = []
        speed_enabled = not is_pathfinding
        
        for i, (name, speed_val) in enumerate(speeds):
            if speed_enabled and abs(current_speed - speed_val) < 0.001:
                color = BUTTON_ACTIVE
            elif speed_enabled:
                color = BUTTON_NORMAL
            else:
                color = BUTTON_DISABLED
                
            speed_rect = pygame.Rect(button_x + i * 55, y_offset, 50, 30)
            self.button_positions['speeds'].append((speed_rect, speed_val, speed_enabled))
            
            pygame.draw.rect(window, color, speed_rect)
            pygame.draw.rect(window, BG_DARK, speed_rect, 1)
            
            text_color = TEXT_PRIMARY if speed_enabled else TEXT_SECONDARY
            speed_label = pygame.font.SysFont('arial', 12).render(name, True, text_color)
            text_rect = speed_label.get_rect(center=speed_rect.center)
            window.blit(speed_label, text_rect)
            
        return y_offset + 40
    
    def _draw_clear_controls(self, window: pygame.Surface, button_x: int,
                           y_offset: int, app_state: Dict[str, Any]) -> int:

        clear_enabled = app_state['can_interact_with_grid']
        
        # Clear Path button
        clear_path_color = STATUS_WARNING if clear_enabled else BUTTON_DISABLED
        clear_path_rect = pygame.Rect(button_x, y_offset, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.button_positions['clear_path'] = (clear_path_rect, clear_enabled)
        
        pygame.draw.rect(window, clear_path_color, clear_path_rect)
        pygame.draw.rect(window, ACCENT if clear_enabled else BG_DARK, clear_path_rect, 2)
        
        text_color = BG_LIGHT if clear_enabled else TEXT_SECONDARY
        clear_path_text = self.font.render("Clear Path", True, text_color)
        text_rect = clear_path_text.get_rect(center=clear_path_rect.center)
        window.blit(clear_path_text, text_rect)
        
        y_offset += BUTTON_HEIGHT + BUTTON_MARGIN
        
        # Clear All button
        clear_all_color = STATUS_ERROR if clear_enabled else BUTTON_DISABLED
        clear_all_rect = pygame.Rect(button_x, y_offset, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.button_positions['clear_all'] = (clear_all_rect, clear_enabled)
        
        pygame.draw.rect(window, clear_all_color, clear_all_rect)
        pygame.draw.rect(window, ACCENT if clear_enabled else BG_DARK, clear_all_rect, 2)
        
        text_color = TEXT_PRIMARY if clear_enabled else TEXT_SECONDARY
        clear_all_text = self.font.render("Clear All", True, text_color)
        text_rect = clear_all_text.get_rect(center=clear_all_rect.center)
        window.blit(clear_all_text, text_rect)
        
        return y_offset + BUTTON_HEIGHT + BUTTON_MARGIN * 2
    
    def _draw_status_info(self, window: pygame.Surface, button_x: int,
                         y_offset: int, app_state: Dict[str, Any]) -> None:

        last_path_length = app_state['last_path_length']
        current_state = app_state['state']
        is_pathfinding = app_state['is_pathfinding_in_progress']
        is_paused = app_state['pathfinding_paused']
        
        # Path length display
        if last_path_length > 0:
            path_info = self.font.render(f"Path Length: {last_path_length}", True, TEXT_PRIMARY)
            window.blit(path_info, (button_x, y_offset))
            y_offset += 25
        
        # Status message
        state_messages = {
            "WAITING_START": "Click to set START point",
            "WAITING_END": "Click to set END point", 
            "READY": "Ready to find path!",
            "PATHFINDING": "Finding path..." if not is_paused else "Path finding PAUSED"
        }
        
        status_color = TEXT_PRIMARY
        if is_pathfinding:
            status_color = STATUS_WARNING if is_paused else STATUS_SUCCESS
        elif current_state == "READY":
            status_color = STATUS_SUCCESS
            
        status_text = self.font.render(state_messages.get(current_state, ""), True, status_color)
        window.blit(status_text, (button_x, y_offset))
    
    def handle_ui_click(self, pos: Tuple[int, int]) -> Tuple[str, Any]:
        x, y = pos
        
        # Only handle clicks in UI area
        if x < GRID_COLS * CELL_SIZE:
            return None, None
            
        try:
            # Check Generate Walls button
            wall_rect, wall_enabled = self.button_positions['generate_wall']
            if wall_rect.collidepoint(x, y) and wall_enabled:
                return "generate_walls", None
            
            # Check Wall Type buttons
            for type_rect, wall_key, type_enabled in self.button_positions['wall_types']:
                if type_rect.collidepoint(x, y) and type_enabled:
                    return "set_wall_type", wall_key
            
            # Check Find Path button
            path_rect, path_enabled = self.button_positions['find_path']
            if path_rect.collidepoint(x, y) and path_enabled:
                return "toggle_pathfinding", None
            
            # Check Speed buttons
            for speed_rect, speed_val, speed_enabled in self.button_positions['speeds']:
                if speed_rect.collidepoint(x, y) and speed_enabled:
                    return "set_speed", speed_val
            
            # Check Clear Path button
            clear_path_rect, clear_enabled = self.button_positions['clear_path']
            if clear_path_rect.collidepoint(x, y) and clear_enabled:
                return "clear_path", None
            
            # Check Clear All button
            clear_all_rect, clear_all_enabled = self.button_positions['clear_all']
            if clear_all_rect.collidepoint(x, y) and clear_all_enabled:
                return "clear_all", None
                
        except (KeyError, ValueError):
            # Handle cases where button_positions might not be fully initialized
            pass
            
        return None, None