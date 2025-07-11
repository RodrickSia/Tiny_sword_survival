import pygame
from typing import Dict, List, Tuple, Optional, Callable
from health_system import HealthBar

class Button:
    def __init__(self, text: str, rect: pygame.Rect, callback: Callable, 
                 color: Tuple[int, int, int] = (100, 100, 100),
                 hover_color: Tuple[int, int, int] = (150, 150, 150),
                 text_color: Tuple[int, int, int] = (255, 255, 255)):
        self.text = text
        self.rect = rect
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.font = pygame.font.Font(None, 36)
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.update_text_rect()
        
    def update_text_rect(self):
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events, return True if button was clicked"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.callback()
                return True
        return False
        
    def draw(self, surface: pygame.Surface):
        """Draw the button"""
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        
        # Cập nhật lại text_rect nếu button thay đổi vị trí
        self.update_text_rect()
        surface.blit(self.text_surface, self.text_rect)

class Slider:
    def __init__(self, rect: pygame.Rect, min_value: float, max_value: float, 
                 initial_value: float, callback: Callable):
        self.rect = rect
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.callback = callback
        self.is_dragging = False
        self.slider_width = 20
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events, return True if slider was changed"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.is_dragging = True
                self._update_value(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                self._update_value(event.pos[0])
                return True
        return False
        
    def _update_value(self, x: int):
        """Update slider value based on mouse position"""
        relative_x = max(0, min(x - self.rect.x, self.rect.width))
        self.value = self.min_value + (relative_x / self.rect.width) * (self.max_value - self.min_value)
        self.callback(self.value)
        
    def draw(self, surface: pygame.Surface):
        """Draw the slider"""
        # Draw background
        pygame.draw.rect(surface, (64, 64, 64), self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        
        # Draw slider handle
        handle_x = self.rect.x + (self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width
        handle_rect = pygame.Rect(handle_x - self.slider_width // 2, 
                                self.rect.y - 5, 
                                self.slider_width, 
                                self.rect.height + 10)
        pygame.draw.rect(surface, (200, 200, 200), handle_rect)
        pygame.draw.rect(surface, (0, 0, 0), handle_rect, 2)

class Menu:
    def __init__(self, title: str, width: int, height: int):
        self.title = title
        self.width = width
        self.height = height
        self.buttons: List[Button] = []
        self.sliders: List[Slider] = []
        self.font = pygame.font.Font(None, 48)
        self.title_font = pygame.font.Font(None, 72)
        
    def add_button(self, text: str, rect: pygame.Rect, callback: Callable, **kwargs):
        """Add a button to the menu"""
        self.buttons.append(Button(text, rect, callback, **kwargs))
        
    def add_slider(self, rect: pygame.Rect, min_value: float, max_value: float, 
                   initial_value: float, callback: Callable):
        """Add a slider to the menu"""
        self.sliders.append(Slider(rect, min_value, max_value, initial_value, callback))
        
    def handle_events(self, events: List[pygame.event.Event]):
        """Handle events for all menu elements"""
        for event in events:
            for button in self.buttons:
                if button.handle_event(event):
                    return True
            for slider in self.sliders:
                if slider.handle_event(event):
                    return True
        return False
        
    def draw(self, surface: pygame.Surface):
        """Draw the menu"""
        # Draw background
        menu_rect = pygame.Rect((surface.get_width() - self.width) // 2,
                              (surface.get_height() - self.height) // 2,
                              self.width, self.height)
        pygame.draw.rect(surface, (50, 50, 50), menu_rect)
        pygame.draw.rect(surface, (100, 100, 100), menu_rect, 3)
        
        # Draw title
        title_surface = self.title_font.render(self.title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(centerx=menu_rect.centerx, 
                                          top=menu_rect.top + 20)
        surface.blit(title_surface, title_rect)
        
        # Draw buttons and sliders
        for button in self.buttons:
            button.draw(surface)
        for slider in self.sliders:
            slider.draw(surface)

class HUD:
    def __init__(self, player_ref, wave_manager_ref, powerup_manager_ref):
        self.player_ref = player_ref
        self.wave_manager_ref = wave_manager_ref
        self.powerup_manager_ref = powerup_manager_ref
        
        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
        
        # Health bar
        self.health_bar = HealthBar(width=200, height=15)
        
        # Colors
        self.text_color = (255, 255, 255)
        self.warning_color = (255, 255, 0)
        self.danger_color = (255, 0, 0)
        self.wave_color = (0, 255, 255)
        
    def draw(self, surface: pygame.Surface):
        """Draw the HUD"""
        if not self.player_ref:
            return
            
        # Draw health bar
        bar_x = self.player_ref.rect.centerx - self.health_bar.width // 2
        bar_y = self.player_ref.rect.top - 20
        health_x = 20
        health_y = 20
        self.health_bar.draw(surface, self.player_ref.health_system, (bar_x, bar_y))
        
        # Draw health text
        health_text = f"Health: {self.player_ref.health_system.current_health}/{self.player_ref.health_system.max_health}"
        health_surface = self.font.render(health_text, True, self.text_color)
        surface.blit(health_surface, (bar_x, bar_y + 25))
        
        # Draw power bar
        power_x = 20
        power_y = health_y + 50
        self.player_ref.power_system.draw(surface, (power_x, power_y))
        
        # Draw power text
        power_text = f"Power: {self.player_ref.power_system.current_power}/{self.player_ref.power_system.max_power}"
        power_surface = self.font.render(power_text, True, self.warning_color)
        surface.blit(power_surface, (power_x, power_y + 15))
        
        # Draw stats
        stats_x = 20
        stats_y = power_y + 40
        enemies_text = f"Enemies Killed: {self.player_ref.enemies_killed}"
        enemies_surface = self.small_font.render(enemies_text, True, self.text_color)
        surface.blit(enemies_surface, (stats_x, stats_y))
        
        # Draw wave information
        if self.wave_manager_ref:
            wave_text = f"Wave: {self.wave_manager_ref.current_wave}"
            wave_surface = self.font.render(wave_text, True, self.text_color)
            surface.blit(wave_surface, (20, stats_y + 25))
            
            enemies_text = f"Enemies: {self.wave_manager_ref.get_enemy_count()}"
            enemies_surface = self.font.render(enemies_text, True, self.text_color)
            surface.blit(enemies_surface, (20, stats_y + 55))
            
            # Draw wave transition info
            if self.wave_manager_ref.wave_completed:
                transition_progress = self.wave_manager_ref.get_wave_transition_progress()
                remaining_time = self.wave_manager_ref.wave_transition_duration - self.wave_manager_ref.wave_transition_timer
                
                # Wave completed message
                completed_text = f"Wave {self.wave_manager_ref.current_wave} Completed!"
                completed_surface = self.large_font.render(completed_text, True, self.wave_color)
                completed_rect = completed_surface.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 - 50))
                surface.blit(completed_surface, completed_rect)
                
                # Next wave countdown
                countdown_text = f"Next wave in {remaining_time:.1f}s"
                countdown_surface = self.font.render(countdown_text, True, self.warning_color)
                countdown_rect = countdown_surface.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
                surface.blit(countdown_surface, countdown_rect)
                
                # Progress bar
                bar_width = 300
                bar_height = 10
                bar_x = (surface.get_width() - bar_width) // 2
                bar_y = surface.get_height() // 2 + 30
                
                # Background
                pygame.draw.rect(surface, (64, 64, 64), (bar_x, bar_y, bar_width, bar_height))
                pygame.draw.rect(surface, (128, 128, 128), (bar_x, bar_y, bar_width, bar_height), 2)
                
                # Progress
                progress_width = int(bar_width * transition_progress)
                if progress_width > 0:
                    pygame.draw.rect(surface, self.wave_color, (bar_x, bar_y, progress_width, bar_height))
            
        # Draw active power-ups
        if self.powerup_manager_ref:
            active_effects = self.powerup_manager_ref.get_active_effects()
            if active_effects:
                effects_y = stats_y + 85
                effects_text = "Active Effects:"
                effects_surface = self.small_font.render(effects_text, True, self.text_color)
                surface.blit(effects_surface, (20, effects_y))
                
                effects_y += 25
                for effect_name, effect_data in active_effects.items():
                    timer = effect_data.get('timer', 0)
                    effect_text = f"{effect_name.title()}: {timer:.1f}s"
                    effect_surface = self.small_font.render(effect_text, True, self.warning_color)
                    surface.blit(effect_surface, (30, effects_y))
                    effects_y += 20
        
        # Draw player power-ups (from power system)
        player_power_ups = self.player_ref.get_active_power_ups()
        if player_power_ups:
            effects_y = stats_y + 85
            if not self.powerup_manager_ref.get_active_effects():
                effects_text = "Active Power-ups:"
                effects_surface = self.small_font.render(effects_text, True, self.text_color)
                surface.blit(effects_surface, (20, effects_y))
                effects_y += 25
            
            for effect_name, effect_data in player_power_ups.items():
                timer = effect_data.get('timer', 0)
                effect_text = f"{effect_name.title()}: {timer:.1f}s"
                effect_surface = self.small_font.render(effect_text, True, (255, 0, 255))  # Magenta for power-ups
                surface.blit(effect_surface, (30, effects_y))
                effects_y += 20
        
        # Draw controls hint
        controls_text = "WASD: Move | Mouse: Attack | ESC: Menu"
        controls_surface = self.small_font.render(controls_text, True, (200, 200, 200))
        surface.blit(controls_surface, (20, surface.get_height() - 30))

        # Draw power up popup if any
        popup_text, popup_time = self.player_ref.get_last_powerup_popup()
        if popup_text:
            popup_font = pygame.font.Font(None, 54)
            popup_surface = popup_font.render(popup_text, True, (255, 255, 0))
            popup_rect = popup_surface.get_rect(centerx=surface.get_width() // 2, top=40)
            # Draw background box
            bg_rect = popup_rect.inflate(40, 20)
            pygame.draw.rect(surface, (0, 0, 0), bg_rect, border_radius=12)
            pygame.draw.rect(surface, (255, 255, 0), bg_rect, 3, border_radius=12)
            surface.blit(popup_surface, popup_rect)

class GameOverScreen:
    def __init__(self, waves_survived: int, restart_callback: Callable, menu_callback: Callable):
        self.waves_survived = waves_survived
        self.restart_callback = restart_callback
        self.menu_callback = menu_callback
        
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)
        
    def handle_events(self, events: List[pygame.event.Event]):
        """Handle events for game over screen"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.restart_callback()
                    return True
                elif event.key == pygame.K_m:
                    self.menu_callback()
                    return True
        return False
        
    def draw(self, surface: pygame.Surface):
        """Draw the game over screen"""
        # Draw background overlay
        overlay = pygame.Surface(surface.get_size())
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Draw title
        title_text = "GAME OVER"
        title_surface = self.title_font.render(title_text, True, (255, 0, 0))
        title_rect = title_surface.get_rect(centerx=surface.get_width() // 2, top=100)
        surface.blit(title_surface, title_rect)
        
        # Draw stats
        stats_y = 200
        stats_text = f"Waves Survived: {self.waves_survived}"
        stats_surface = self.font.render(stats_text, True, (255, 255, 255))
        stats_rect = stats_surface.get_rect(centerx=surface.get_width() // 2, top=stats_y)
        surface.blit(stats_surface, stats_rect)
        
        # Draw instructions
        restart_text = "Press R to Restart"
        restart_surface = self.font.render(restart_text, True, (255, 255, 255))
        restart_rect = restart_surface.get_rect(centerx=surface.get_width() // 2, 
                                               centery=surface.get_height() // 2 + 50)
        surface.blit(restart_surface, restart_rect)
        
        menu_text = "Press M for Main Menu"
        menu_surface = self.font.render(menu_text, True, (255, 255, 255))
        menu_rect = menu_surface.get_rect(centerx=surface.get_width() // 2, 
                                         centery=surface.get_height() // 2 + 80)
        surface.blit(menu_surface, menu_rect)

class LeaderboardScreen:
    def __init__(self, leaderboard_ref, back_callback: Callable):
        self.leaderboard_ref = leaderboard_ref
        self.back_callback = back_callback
        
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)
        
    def handle_events(self, events: List[pygame.event.Event]):
        """Handle events for leaderboard screen"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_b:
                    self.back_callback()
                    return True
        return False
        
    def draw(self, surface: pygame.Surface):
        """Draw the leaderboard screen"""
        # Draw background
        overlay = pygame.Surface(surface.get_size())
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Draw title
        title_text = "LEADERBOARD"
        title_surface = self.title_font.render(title_text, True, (255, 255, 255))
        title_rect = title_surface.get_rect(centerx=surface.get_width() // 2, top=50)
        surface.blit(title_surface, title_rect)
        
        # Draw leaderboard
        scores = self.leaderboard_ref.get_top_scores(10)
        
        if not scores:
            # No scores yet
            no_scores_text = "No scores yet! Play the game to set a record!"
            no_scores_surface = self.font.render(no_scores_text, True, (200, 200, 200))
            no_scores_rect = no_scores_surface.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
            surface.blit(no_scores_surface, no_scores_rect)
        else:
            # Draw scores table
            table_x = (surface.get_width() - 600) // 2
            table_y = 150
            
            # Draw headers
            headers = ["Rank", "Waves", "Enemies", "Score", "Date"]
            header_x = table_x
            for i, header in enumerate(headers):
                header_surface = self.font.render(header, True, (255, 255, 0))
                surface.blit(header_surface, (header_x, table_y))
                header_x += 120
            
            # Draw scores
            for i, score in enumerate(scores):
                row_y = table_y + 40 + i * 30
                
                # Rank
                rank_surface = self.font.render(f"#{score['rank']}", True, (255, 255, 255))
                surface.blit(rank_surface, (table_x, row_y))
                
                # Waves
                waves_surface = self.font.render(str(score['waves_survived']), True, (255, 255, 255))
                surface.blit(waves_surface, (table_x + 120, row_y))
                
                # Enemies
                enemies_surface = self.font.render(str(score['enemies_killed']), True, (255, 255, 255))
                surface.blit(enemies_surface, (table_x + 240, row_y))
                
                # Score
                score_surface = self.font.render(str(score['total_score']), True, (255, 255, 255))
                surface.blit(score_surface, (table_x + 360, row_y))
                
                # Date
                date_surface = self.small_font.render(score['date'], True, (200, 200, 200))
                surface.blit(date_surface, (table_x + 480, row_y))
        
        # Draw instructions
        instructions_text = "Press ESC or B to go back"
        instructions_surface = self.small_font.render(instructions_text, True, (200, 200, 200))
        instructions_rect = instructions_surface.get_rect(centerx=surface.get_width() // 2, bottom=surface.get_height() - 30)
        surface.blit(instructions_surface, instructions_rect) 