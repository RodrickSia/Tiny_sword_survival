import pygame
import random
import math
import os
from typing import Dict, List, Tuple
from utils import LoadSprite

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, powerup_type: str, pos: Tuple[int, int]):
        super().__init__()
        self.powerup_type = powerup_type
        
        # Power-up configurations
        self.configs = {
            'health': {
                'heal_amount': 50,
                'duration': 0,  # Instant
                'sprite_path': os.path.join("assets", "UI", "Icons", "Regular_01.png"),
                'color': (0, 255, 0),
                'scale': 0.8
            },
            'speed': {
                'speed_multiplier': 1.5,
                'duration': 10.0,  # 10 seconds
                'sprite_path': os.path.join("assets", "UI", "Icons", "Regular_02.png"),
                'color': (0, 255, 255),
                'scale': 0.8
            },
            'damage': {
                'damage_multiplier': 2.0,
                'duration': 8.0,  # 8 seconds
                'sprite_path': os.path.join("UI", "Icons", "Regular_03.png"),
                'color': (255, 0, 0),
                'scale': 0.8
            },
            'invulnerability': {
                'duration': 5.0,  # 5 seconds
                'sprite_path': os.path.join("assets", "UI", "Icons", "Regular_04.png"),
                'color': (255, 255, 0),
                'scale': 0.8
            },
            'rapid_fire': {
                'attack_speed_multiplier': 3.0,
                'duration': 6.0,  # 6 seconds
                'sprite_path': os.path.join("assets", "UI", "Icons", "Regular_05.png"),
                'color': (255, 0, 255),
                'scale': 0.8
            }
        }
        
        self.config = self.configs[powerup_type]
        
        # Initialize sprite
        self._init_sprite()
        
        # Position
        self.rect.center = pos
        
        # Animation
        self.bob_timer = 0.0
        self.bob_speed = 2.0
        self.bob_amount = 5
        self.original_y = self.rect.y
        
        # Rotation
        self.rotation = 0.0
        self.rotation_speed = 90.0  # degrees per second
        
    def _init_sprite(self):
        """Initialize power-up sprite"""
        try:
            sprite_loader = LoadSprite(self.config['sprite_path'])
            self.image = sprite_loader.get_image(0, 0, 64, 64, self.config['scale'])
        except:
            # Fallback to colored rectangle if sprite not found
            self.image = pygame.Surface((32, 32))
            self.image.fill(self.config['color'])
            
        self.rect = self.image.get_rect()
        
    def update(self, dt: float):
        """Update power-up animation"""
        # Bobbing animation
        self.bob_timer += dt
        bob_offset = math.sin(self.bob_timer * self.bob_speed) * self.bob_amount
        self.rect.y = self.original_y + bob_offset
        
        # Rotation animation
        self.rotation += self.rotation_speed * dt
        if self.rotation >= 360:
            self.rotation -= 360
            
        # Rotate image
        if hasattr(self, 'original_image'):
            self.image = pygame.transform.rotate(self.original_image, self.rotation)
        else:
            self.original_image = self.image.copy()
            self.image = pygame.transform.rotate(self.original_image, self.rotation)

class PowerUpManager:
    def __init__(self, player_ref):
        self.player_ref = player_ref
        self.powerups = pygame.sprite.Group()
        self.active_effects = {}
        
        # Spawn configuration
        self.spawn_timer = 0.0
        self.spawn_interval = 15.0  # Spawn power-up every 15 seconds
        self.spawn_chance = 0.3  # 30% chance to spawn when timer expires
        
        # Power-up types and their weights
        self.powerup_types = ['health', 'speed', 'damage', 'invulnerability', 'rapid_fire']
        self.powerup_weights = [0.3, 0.2, 0.2, 0.15, 0.15]  # Health is most common
        
    def update(self, dt: float):
        """Update power-up manager"""
        # Update spawn timer
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            if random.random() < self.spawn_chance:
                self._spawn_powerup()
            self.spawn_timer = 0.0
            
        # Update power-ups
        self.powerups.update(dt)
        
        # Update active effects
        self._update_active_effects(dt)
        
    def _spawn_powerup(self):
        """Spawn a random power-up"""
        if not self.player_ref:
            return
            
        spawn_rect = pygame.Rect(200, 200, 900, 400)  # ví dụ: mép phải màn hình

        spawn_x = random.uniform(spawn_rect.left, spawn_rect.right)
        spawn_y = random.uniform(spawn_rect.top, spawn_rect.bottom)
        
        # Choose power-up type
        powerup_type = random.choices(self.powerup_types, weights=self.powerup_weights)[0]
        
        # Create power-up
        powerup = PowerUp(powerup_type, (spawn_x, spawn_y))
        self.powerups.add(powerup)
        
    def _update_active_effects(self, dt: float):
        """Update active power-up effects"""
        effects_to_remove = []
        
        for effect_name, effect_data in self.active_effects.items():
            effect_data['timer'] -= dt
            if effect_data['timer'] <= 0:
                effects_to_remove.append(effect_name)
                self._remove_effect(effect_name)
                
        for effect_name in effects_to_remove:
            del self.active_effects[effect_name]
            
    def _remove_effect(self, effect_name: str):
        """Remove a power-up effect"""
        if effect_name == 'speed':
            # Reset speed to normal
            pass  # Speed is handled in player movement
        elif effect_name == 'damage':
            # Reset damage to normal
            pass  # Damage is handled in combat system
        elif effect_name == 'invulnerability':
            # Remove invulnerability
            if self.player_ref and hasattr(self.player_ref, 'health_system'):
                self.player_ref.health_system.is_invulnerable = False
        elif effect_name == 'rapid_fire':
            # Reset attack speed to normal
            pass  # Attack speed is handled in combat system
            
    def apply_powerup(self, powerup_type: str):
        """Apply a power-up effect"""
        config = PowerUp(powerup_type, (0, 0)).config
        
        if powerup_type == 'health':
            # Instant heal
            if self.player_ref and hasattr(self.player_ref, 'health_system'):
                self.player_ref.health_system.heal(config['heal_amount'])
                
        elif powerup_type == 'speed':
            # Speed boost
            self.active_effects['speed'] = {
                'multiplier': config['speed_multiplier'],
                'timer': config['duration']
            }
            
        elif powerup_type == 'damage':
            # Damage boost
            self.active_effects['damage'] = {
                'multiplier': config['damage_multiplier'],
                'timer': config['duration']
            }
            
        elif powerup_type == 'invulnerability':
            # Invulnerability
            if self.player_ref and hasattr(self.player_ref, 'health_system'):
                self.player_ref.health_system.is_invulnerable = True
                self.player_ref.health_system.invulnerability_time = config['duration']
                
            self.active_effects['invulnerability'] = {
                'timer': config['duration']
            }
            
        elif powerup_type == 'rapid_fire':
            # Attack speed boost
            self.active_effects['rapid_fire'] = {
                'multiplier': config['attack_speed_multiplier'],
                'timer': config['duration']
            }
            
    def get_active_effects(self) -> Dict:
        """Get currently active effects"""
        return self.active_effects.copy()
        
    def draw(self, surface: pygame.Surface):
        """Draw all power-ups"""
        self.powerups.draw(surface)
        
    def check_collisions(self):
        """Check for collisions between player and power-ups"""
        if not self.player_ref:
            return
            
        # Get colliding power-ups
        colliding_powerups = pygame.sprite.spritecollide(self.player_ref, self.powerups, True)
        
        # Apply effects
        for powerup in colliding_powerups:
            self.apply_powerup(powerup.powerup_type)
            print(f"Applied power-up: {powerup.powerup_type}")
            
    def clear_powerups(self):
        """Clear all power-ups"""
        self.powerups.empty()
        self.active_effects.clear() 