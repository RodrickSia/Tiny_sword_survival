import pygame
from settings import *
from player import Player
from map_loader import MapLoader
from enemy_system import WaveManager
from powerup_system import PowerUpManager
from audio_system import AudioSystem
from ui_system import Menu, HUD, GameOverScreen, LeaderboardScreen
from leaderboard_system import LeaderboardSystem
import os
from resolutionscaler import ResolutionScalerFullScreenStretch

class Game:
    def __init__(self):
        pygame.init()

        # Set fixed logic dimensions
        self.logic_width = 1280
        self.logic_height = 720

        self.scaler = ResolutionScalerFullScreenStretch(self.logic_width, self.logic_height)
        self.screen = self.scaler.get_logic_surface()  

        pygame.display.set_caption("Tiny Sword Survival")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.game_state = 'menu'  # 'menu', 'playing', 'paused', 'game_over', 'leaderboard'
        
        # Initialize systems
        self.setup_audio()
        self.setup_leaderboard()
        self.setup_map()
        self.setup_sprites()
        self.setup_ui()
        
        # Start background music
        self.audio_system.play_music("background_music.wav", loop=True)

    def setup_audio(self):
        """Setup audio system"""
        self.audio_system = AudioSystem()

    def setup_leaderboard(self):
        """Setup leaderboard system"""
        self.leaderboard = LeaderboardSystem()

    def setup_map(self):
        """Setup map loading and processing"""
        tmx_path = os.path.join("tiled_map", "Basic_maps.tmx")
        
        self.map_loader = MapLoader(tmx_path)
        
        if self.map_loader.load_map():
            self.map_loader.setup_layers()
            print("Map setup complete")
            print(f"Collision objects created: {len(self.map_loader.collision_sprites)}")
            print(f"Animated tiles: {len(self.map_loader.animated_tiles)}")
        else:
            print("Failed to load map")
            self.map_loader = None

    def setup_sprites(self):
        """Setup player and sprite groups"""
        self.all_sprites = pygame.sprite.Group()
        
        # Pass collision sprites to player if map loaded
        collision_sprites = None
        if self.map_loader:
            collision_sprites = self.map_loader.collision_sprites
            
        self.player = Player(collision_sprites=collision_sprites)
        
        # Center the player on screen
        self.player.rect.center = (self.logic_width // 2, self.logic_height // 2)
        self.player.pos_x = float(self.player.rect.x)
        self.player.pos_y = float(self.player.rect.y)
    
        self.all_sprites.add(self.player)
        
        # Setup wave manager
        self.wave_manager = WaveManager(self.player)
        
        # Setup power-up manager
        self.powerup_manager = PowerUpManager(self.player)

    def setup_ui(self):
        """Setup UI systems"""
        # Setup HUD
        self.hud = HUD(self.player, self.wave_manager, self.powerup_manager)
        
        # Setup main menu
        self.setup_main_menu()
        
        # Setup pause menu
        self.setup_pause_menu()
        
        # Setup settings menu
        self.setup_settings_menu()
        
        # Setup leaderboard screen
        self.leaderboard_screen = LeaderboardScreen(self.leaderboard, self.return_to_menu)

    def setup_main_menu(self):
        """Setup main menu"""
        self.main_menu = Menu("Tiny Sword Survival", 500, 420)
        # Căn giữa menu và button
        button_width = 260
        button_height = 56
        num_buttons = 4
        spacing = 28
        menu_padding_top = 60
        menu_padding_bottom = 40
        total_height = num_buttons * button_height + (num_buttons - 1) * spacing
        menu_x = (self.logic_width - 500) // 2
        menu_y = (self.logic_height - (total_height + menu_padding_top + menu_padding_bottom)) // 2
        # Start
        start_rect = pygame.Rect(menu_x + 120, menu_y + menu_padding_top, button_width, button_height)
        self.main_menu.add_button("Start Game", start_rect, self.start_game)
        # Settings
        settings_rect = pygame.Rect(menu_x + 120, menu_y + menu_padding_top + (button_height + spacing) * 1, button_width, button_height)
        self.main_menu.add_button("Settings", settings_rect, self.open_settings)
        # Leaderboard
        leaderboard_rect = pygame.Rect(menu_x + 120, menu_y + menu_padding_top + (button_height + spacing) * 2, button_width, button_height)
        self.main_menu.add_button("Leaderboard", leaderboard_rect, self.open_leaderboard)
        # Quit
        quit_rect = pygame.Rect(menu_x + 120, menu_y + menu_padding_top + (button_height + spacing) * 3, button_width, button_height)
        self.main_menu.add_button("Quit", quit_rect, self.quit_game)

    def setup_pause_menu(self):
        """Setup pause menu"""
        self.pause_menu = Menu("Paused", 400, 300)
        button_width = 260
        button_height = 56
        num_buttons = 3
        spacing = 28
        menu_padding_top = 50
        total_height = num_buttons * button_height + (num_buttons - 1) * spacing
        menu_x = (self.logic_width - 400) // 2
        menu_y = (self.logic_height - (total_height + menu_padding_top)) // 2
        resume_rect = pygame.Rect(menu_x + 70, menu_y + menu_padding_top, button_width, button_height)
        self.pause_menu.add_button("Resume", resume_rect, self.resume_game)
        settings_rect = pygame.Rect(menu_x + 70, menu_y + menu_padding_top + (button_height + spacing) * 1, button_width, button_height)
        self.pause_menu.add_button("Settings", settings_rect, self.open_settings)
        menu_rect = pygame.Rect(menu_x + 70, menu_y + menu_padding_top + (button_height + spacing) * 2, button_width, button_height)
        self.pause_menu.add_button("Main Menu", menu_rect, self.return_to_menu)

    def setup_settings_menu(self):
        """Setup settings menu"""
        self.settings_menu = Menu("Settings", 500, 400)
        button_width = 320
        button_height = 56
        menu_padding_top = 60
        menu_x = (self.logic_width - 500) // 2
        menu_y = (self.logic_height - 400) // 2
        # SFX Volume slider
        sfx_rect = pygame.Rect(menu_x + 90, menu_y + menu_padding_top + 60, 320, 20)
        self.settings_menu.add_slider(sfx_rect, 0.0, 1.0, self.audio_system.get_sfx_volume(), self.audio_system.set_sfx_volume)
        # Music Volume slider
        music_rect = pygame.Rect(menu_x + 90, menu_y + menu_padding_top + 120, 320, 20)
        self.settings_menu.add_slider(music_rect, 0.0, 1.0, self.audio_system.get_music_volume(), self.audio_system.set_music_volume)
        # Back button
        back_rect = pygame.Rect(menu_x + 90, menu_y + menu_padding_top + 200, button_width, button_height)
        self.settings_menu.add_button("Back", back_rect, self.close_settings)

    def start_game(self):
        """Start a new game"""
        self.game_state = 'playing'
        self.player.reset()
        self.wave_manager.clear_enemies()
        self.wave_manager.current_wave = 0  # Reset wave counter
        self.powerup_manager.clear_powerups()
        self.wave_manager.start_wave()
        self.audio_system.play_sound('wave_start')

    def resume_game(self):
        """Resume the game"""
        self.game_state = 'playing'

    def pause_game(self):
        """Pause the game"""
        self.game_state = 'paused'

    def return_to_menu(self):
        """Return to main menu"""
        self.game_state = 'menu'

    def open_settings(self):
        """Open settings menu"""
        self.game_state = 'settings'

    def close_settings(self):
        """Close settings menu"""
        if self.game_state == 'settings':
            self.game_state = 'menu'

    def open_leaderboard(self):
        """Open leaderboard"""
        self.game_state = 'leaderboard'

    def quit_game(self):
        """Quit the game"""
        self.running = False

    def check_game_over(self):
        """Check if game is over"""
        if not self.player.is_alive():
            # Add score to leaderboard
            rank = self.leaderboard.add_score(
                self.player.waves_survived, 
                self.player.enemies_killed
            )
            
            self.game_state = 'game_over'
            self.game_over_screen = GameOverScreen(
                self.player.waves_survived,
                self.start_game,
                self.return_to_menu
            )
            self.audio_system.play_sound('game_over')
            
            # Show rank if it's a good score
            if rank <= 3:
                print(f"🎉 New record! Rank #{rank}")

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Convert to seconds
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()

    def handle_events(self):
        events = pygame.event.get()
        # Chuyển đổi event.pos về logic surface nếu là sự kiện chuột
        logic_events = []
        for event in events:
            if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                # Chuyển đổi tọa độ chuột
                logic_pos = self.scaler.screen_to_logic(event.pos)
                # Tạo event mới với pos đã chuyển đổi
                event_dict = event.dict.copy()
                event_dict['pos'] = logic_pos
                logic_event = pygame.event.Event(event.type, event_dict)
                logic_events.append(logic_event)
            else:
                logic_events.append(event)
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == 'playing':
                        self.pause_game()
                    elif self.game_state == 'paused':
                        self.resume_game()
                    elif self.game_state == 'settings':
                        self.close_settings()
            self.scaler.handle_event(event)
        # Handle menu events với logic_events
        if self.game_state == 'menu':
            self.main_menu.handle_events(logic_events)
        elif self.game_state == 'paused':
            self.pause_menu.handle_events(logic_events)
        elif self.game_state == 'settings':
            self.settings_menu.handle_events(logic_events)
        elif self.game_state == 'game_over':
            self.game_over_screen.handle_events(logic_events)
        elif self.game_state == 'leaderboard':
            self.leaderboard_screen.handle_events(logic_events)

    def update(self, dt):
        if self.game_state != 'playing':
            return
            
        # Update map animations
        if self.map_loader:
            self.map_loader.update_animations(dt)
        
        # Update sprites
        self.all_sprites.update(dt)
        
        # Update wave manager
        self.wave_manager.update(dt)
        
        # Check for wave completion
        if self.wave_manager.wave_completed and self.wave_manager.wave_transition_timer < dt:
            # Just completed wave, play sound and update player stats
            self.audio_system.play_sound('wave_complete')
            self.player.on_wave_completed()
        
        # Update power-up manager
        self.powerup_manager.update(dt)
        
        # Check collisions
        self.check_collisions()
        
        # Check game over
        self.check_game_over()

    def check_collisions(self):
        """Check all collisions"""
        # Check player attacks on enemies
        if self.player.combat_system.is_attacking:
            self.check_player_attacks()
        
        # Check power-up collisions
        self.powerup_manager.check_collisions()

    def check_player_attacks(self):
        """Check if player attacks hit enemies"""
        # Get attack area based on direction
        attack_rect = self.get_attack_area()
        
        # Check enemies in attack area
        for enemy in self.wave_manager.enemies:
            if attack_rect.colliderect(enemy.rect):
                if enemy.take_damage(self.player.get_damage()):
                    self.audio_system.play_sound('enemy_hit')
                    # Remove dead enemies
                    if not enemy.health_system.is_alive():
                        # Play death sound when enemy starts death animation
                        self.audio_system.play_sound('enemy_death')
                        # Update player stats
                        self.player.on_enemy_killed()
                        # Note: enemy.kill() is now called automatically in death animation

    def get_attack_area(self):
        """Get the attack area rectangle based on player direction"""
        attack_range = self.player.get_attack_range()  # Use dynamic range
        attack_width = 60
        
        if self.player.direction == 'right':
            return pygame.Rect(self.player.rect.right, self.player.rect.centery - attack_width//2, 
                             attack_range, attack_width)
        elif self.player.direction == 'left':
            return pygame.Rect(self.player.rect.left - attack_range, self.player.rect.centery - attack_width//2, 
                             attack_range, attack_width)
        elif self.player.direction == 'down':
            return pygame.Rect(self.player.rect.centerx - attack_width//2, self.player.rect.bottom, 
                             attack_width, attack_range)
        else:  # up
            return pygame.Rect(self.player.rect.centerx - attack_width//2, self.player.rect.top - attack_range, 
                             attack_width, attack_range)

    def draw(self):
        surface = self.scaler.begin_frame()

        if self.game_state == 'playing':
            self.draw_game(surface)
        elif self.game_state == 'menu':
            self.draw_game(surface)  # Draw game in background
            self.main_menu.draw(surface)
        elif self.game_state == 'paused':
            self.draw_game(surface)  # Draw game in background
            self.pause_menu.draw(surface)
        elif self.game_state == 'settings':
            self.draw_game(surface)  # Draw game in background
            self.settings_menu.draw(surface)
        elif self.game_state == 'game_over':
            self.draw_game(surface)  # Draw game in background
            self.game_over_screen.draw(surface)
        elif self.game_state == 'leaderboard':
            self.draw_game(surface)  # Draw game in background
            self.leaderboard_screen.draw(surface)

        self.scaler.end_frame()

    def draw_game(self, surface):
        """Draw the game world"""
        surface.fill((64, 128, 64))  # Green background

        if self.map_loader:
            self.map_loader.draw_static_layers(surface)
            self.map_loader.draw_animated_tiles(surface)
        else:
            font = pygame.font.Font(None, 36)
            text = font.render("Map failed to load!", True, (255, 255, 255))
            surface.blit(text, (50, 50))

        # Draw sprites
        self.all_sprites.draw(surface)
        
        # Draw enemies
        self.wave_manager.draw(surface)
        
        # Draw power-ups
        self.powerup_manager.draw(surface)
        
        # Draw HUD
        self.hud.draw(surface)

if __name__ == "__main__":
    game = Game()
    game.run()