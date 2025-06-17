import pygame
from settings import *
from player import Player
from map_loader import MapLoader
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

        pygame.display.set_caption("Game")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize map
        self.setup_map()
        
        # Initialize sprites
        self.setup_sprites()

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

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Convert to seconds
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.scaler.handle_event(event)

    def update(self, dt):
        # Update map animations
        if self.map_loader:
            self.map_loader.update_animations(dt)
        
        # Update sprites
        self.all_sprites.update(dt)

    def draw(self):
        surface = self.scaler.begin_frame()

        surface.fill((64, 128, 64))  # Green background

        if self.map_loader:
            self.map_loader.draw_static_layers(surface)
            self.map_loader.draw_animated_tiles(surface)
        else:
            font = pygame.font.Font(None, 36)
            text = font.render("Map failed to load!", True, (255, 255, 255))
            surface.blit(text, (50, 50))

        self.all_sprites.draw(surface)

        self.scaler.end_frame()
            

if __name__ == "__main__":
    game = Game()
    game.run()