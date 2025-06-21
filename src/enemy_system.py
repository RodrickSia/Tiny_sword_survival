import pygame
import random
import math
import os
from typing import List, Dict, Tuple
from utils import LoadSprite, AnimationManager
from health_system import HealthSystem, HealthBar
from pygame.math import Vector2
from map_loader import MapLoader
class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type: str, pos: Tuple[int, int], player_ref,  all_enemies_group=None, collision_sprites=None):
        super().__init__()
        self.enemy_type = enemy_type
        self.player_ref = player_ref
        self.all_enemies = all_enemies_group
        # Enemy configurations
        self.configs = {
            'goblin': {
                'health': 30,
                'speed': 120,
                'damage': 5,
                'attack_range': 50,
                'attack_cooldown': 1.0,
                'sprite_path': os.path.join("assets", "Factions", "Goblins", "Troops", "Torch", "Red", "Torch_Red.png"),
                'sprite_width': 192,
                'sprite_height': 192,
                'scale': 0.6
            },
            'archer': {
                'health': 20,
                'speed': 100,
                'damage': 7,
                'attack_range': 150,
                'attack_cooldown': 2.0,
                'sprite_path': os.path.join("assets", "Factions", "Knights", "Troops", "Archer", "Red", "Archer_Red.png"),
                'sprite_width': 192,
                'sprite_height': 192,
                'scale': 0.6
            },
            'warrior': {
                'health': 50,
                'speed': 80,
                'damage': 10,
                'attack_range': 60,
                'attack_cooldown': 1.5,
                'sprite_path': os.path.join("assets", "Factions", "Knights", "Troops", "Warrior", "Red", "Warrior_Red.png"),
                'sprite_width': 192,
                'sprite_height': 192,
                'scale': 0.6
            }
        }
        
        self.config = self.configs[enemy_type]
        self.collision_sprites = collision_sprites
        # Initialize systems
        self._init_sprite_system()
        self._init_health_system()
        self._init_ai_system()
        
        # Position and movement
        self.knockback_vector = pygame.math.Vector2(0, 0)
        self.knockback_timer = 0
        self.knockback_duration = 0.15
        self.rect.center = pos
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        self.old_rect = self.rect.copy()
        self.pos = (self.pos_x, self.pos_y)

        # AI state
        self.state = 'chase'  # chase, attack, retreat, dead
        self.attack_timer = 0.0
        self.last_attack_time = 0.0
        
        # Animation state
        self.direction = 'right'
        self.is_moving = False
        
        # Death animation properties
        self.death_timer = 0.0
        self.death_duration = 1.0  # 1 second death animation
        self.original_image = None
        self.death_rotation = 0.0
        self.death_scale = 1.0
        self.death_alpha = 255
        
    def _init_sprite_system(self):
        """Initialize sprite and animation system"""
        sprite_loader = LoadSprite(self.config['sprite_path'])
        animations = sprite_loader.get_all_animations_player(
            sprite_width=self.config['sprite_width'],
            sprite_height=self.config['sprite_height'],
            scale=self.config['scale']
        )
        
        animation_speeds = {
            'idle_animation_speed': 8,
            'attack_animation_speed': 15
        }
        
        self.animation_manager = AnimationManager(animations, animation_speeds)
        self.animation_manager.create_directional_idle_animations()
        
        # Set initial image
        self.image = self.animation_manager._get_current_frame()
        self.rect = self.image.get_rect()
        
    def _init_health_system(self):
        """Initialize health system"""
        self.health_system = HealthSystem(self.config['health'])
        self.health_system.on_death = self._on_death
        self.health_bar = HealthBar(width=80, height=8)
        
    def _init_ai_system(self):
        """Initialize AI system"""
        self.target_pos = None
        self.pathfinding_timer = 0.0
        self.pathfinding_interval = 0.5  # Update path every 0.5 seconds
        
    def _on_death(self):
        """Handle enemy death"""
        self.state = 'dead'
        self.death_timer = 0.0
        # Store original image for death animation
        self.original_image = self.image.copy()
        
    def take_damage(self, damage: int) -> bool:
        """Take damage from player"""
        return self.health_system.take_damage(damage)
    
    def _avoid_others(self):
        """Đẩy enemy ra xa các enemy khác nếu bị đè lên nhau"""
        if not self.all_enemies:
            return

        for other in self.all_enemies:
            if other == self or other.state == 'dead':
                continue

            if self.rect.colliderect(other.rect):
                offset = Vector2(self.rect.center) - Vector2(other.rect.center)
                if offset.length() == 0:
                    offset = Vector2(random.uniform(-1, 1), random.uniform(-1, 1))  # tránh chia 0
                offset = offset.normalize() * 1.5  # lực đẩy nhẹ
                self.pos_x += offset.x
                self.pos_y += offset.y
                self.rect.x = int(self.pos_x)
                self.rect.y = int(self.pos_y)



        
    def update(self, dt: float):
        """Update enemy logic"""
        if self.state == 'dead':
            self._update_death_animation(dt)
            return
            
        if not self.health_system.is_alive():
            return
            
        # Update health system
        self.health_system.update(dt)
        
        # Update AI
        self._update_ai(dt)

        self._avoid_others()

        # Update animation
        self._update_animation(dt)

        self.old_rect = self.rect.copy()
        

        if self.knockback_timer > 0:
            self.pos_x += self.knockback_vector.x * dt
            self.pos_y += self.knockback_vector.y * dt
            self.rect.topleft = (int(self.pos_x), int(self.pos_y))
            self.knockback_timer -= dt
        else:
            self.knockback_vector = pygame.math.Vector2(0, 0)
              

    def _update_death_animation(self, dt: float):
        """Update death animation"""
        self.death_timer += dt
        progress = self.death_timer / self.death_duration
        
        if progress >= 1.0:
            # Animation complete, remove enemy
            self.kill()
            return
            
        # Calculate death effects
        self.death_rotation = progress * 360  # Full rotation
        self.death_scale = 1.0 - progress * 0.5  # Scale down to 50%
        self.death_alpha = int(255 * (1.0 - progress))  # Fade out
        
        # Apply effects to image
        if self.original_image:
            # Rotate
            rotated = pygame.transform.rotate(self.original_image, self.death_rotation)
            
            # Scale
            new_width = int(rotated.get_width() * self.death_scale)
            new_height = int(rotated.get_height() * self.death_scale)
            if new_width > 0 and new_height > 0:
                scaled = pygame.transform.scale(rotated, (new_width, new_height))
                
                # Apply alpha
                if self.death_alpha < 255:
                    alpha_surface = pygame.Surface(scaled.get_size(), pygame.SRCALPHA)
                    alpha_surface.fill((255, 255, 255, self.death_alpha))
                    scaled.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                self.image = scaled
                # Update rect to center the scaled image
                old_center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = old_center
        
    def _update_ai(self, dt: float):
        """Update AI behavior"""
        if not self.player_ref or not self.player_ref.health_system.is_alive():
            return
            
        # Calculate distance to player
        dx = self.player_ref.rect.centerx - self.rect.centerx
        dy = self.player_ref.rect.centery - self.rect.centery
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Update attack timer
        self.attack_timer += dt
        
        # Determine state
        if distance <= self.config['attack_range']:
            self.state = 'attack'
        else:
            self.state = 'chase'
            
        # Execute state behavior
        if self.state == 'chase':
            self._chase_player(dt, dx, dy, distance)
        elif self.state == 'attack':
            self._attack_player(dt, dx, dy, distance)
            
    def _chase_player(self, dt: float, dx: float, dy: float, distance: float):
        """Chase the player"""
        if distance > 0:
            # Normalize direction
            dx /= distance
            dy /= distance
            
            # Move towards player
            speed = self.config['speed']
            move_x = dx * speed * dt
            move_y = dy * speed * dt
            
            # Update position
            self.pos_x += move_x
            self.pos_y += move_y
            
            # Update direction for animation
            if abs(dx) > abs(dy):
                self.direction = 'right' if dx > 0 else 'left'
            else:
                self.direction = 'down' if dy > 0 else 'up'
                
            self.is_moving = True
            
            # Update rect
            self.rect.x = int(self.pos_x)
            self.rect.y = int(self.pos_y)
            
        else:
            self.is_moving = False
            
    def _attack_player(self, dt: float, dx: float, dy: float, distance: float):
        """Attack the player"""
        self.is_moving = False
        
        # Update direction for animation
        if abs(dx) > abs(dy):
            self.direction = 'right' if dx > 0 else 'left'
        else:
            self.direction = 'down' if dy > 0 else 'up'
            
        # Attack if cooldown is ready
        if self.attack_timer >= self.config['attack_cooldown']:
            self._perform_attack()
            self.attack_timer = 0.0
            
    def _perform_attack(self):
        """Perform attack on player"""
        if self.player_ref and self.player_ref.health_system.is_alive():
            self.player_ref.health_system.take_damage(self.config['damage'])
        
        direction = pygame.math.Vector2(self.player_ref.rect.center) - pygame.math.Vector2(self.rect.center)
        if direction.length() == 0:
            direction = pygame.math.Vector2(1, 0)
        direction = direction.normalize()

    # Knockback ngược hướng tấn công
        self.knockback_vector = -direction * 250  # 150 px/s là tốc độ bị đẩy lùi
        self.knockback_timer = self.knockback_duration

        self.player_ref.rect.x = int(self.player_ref.pos_x)
        self.player_ref.rect.y = int(self.player_ref.pos_y)

    def _update_animation(self, dt: float):
        """Update enemy animation"""
        if self.health_system.is_alive():
            self.image = self.animation_manager.update_animation(
                dt, False, 0, self.is_moving, self.direction, self.direction, False
            )
            
    def draw_health_bar(self, surface: pygame.Surface):
        """Draw health bar above enemy"""
        if self.health_system.is_alive() and self.state != 'dead':
            bar_x = self.rect.centerx - self.health_bar.width // 2
            bar_y = self.rect.top - 20
            self.health_bar.draw(surface, self.health_system, (bar_x, bar_y))


    

class WaveManager:
    def __init__(self, player_ref, collision_sprites=None):
        self.player_ref = player_ref
        self.collision_sprites = collision_sprites or pygame.sprite.Group()

        self.current_wave = 0
        self.enemies = pygame.sprite.Group()
        self.enemy_types = ['goblin', 'archer', 'warrior']
        
        # Wave configuration
        self.wave_config = {
            'enemies_per_wave': 5,
            'enemy_increase_per_wave': 2,
            'boss_wave_interval': 5,  # Every 5 waves spawn a boss
            'spawn_radius': 200,  # Distance from player to spawn enemies
        }
        
        # Spawn timer
        self.spawn_timer = 0.0
        self.spawn_interval = 1.0  # Spawn enemy every 1 second
        
        # Wave state
        self.wave_in_progress = False
        self.enemies_to_spawn = 0
        self.enemies_spawned = 0
        
        # Wave transition timer
        self.wave_transition_timer = 0.0
        self.wave_transition_duration = 3.0  # 3 seconds between waves
        self.wave_completed = False
        
        
    def start_wave(self):
        """Start a new wave"""
        self.current_wave += 1
        self.wave_in_progress = True
        self.wave_completed = False
        
        # Calculate enemies for this wave
        base_enemies = self.wave_config['enemies_per_wave']
        increase = self.wave_config['enemy_increase_per_wave']
        self.enemies_to_spawn = base_enemies + (self.current_wave - 1) * increase
        
        # Add boss for boss waves
        if self.current_wave % self.wave_config['boss_wave_interval'] == 0:
            self.enemies_to_spawn += 1
            
        self.enemies_spawned = 0
        self.spawn_timer = 0.0
        
        print(f"Starting wave {self.current_wave} with {self.enemies_to_spawn} enemies")
        
    def update(self, dt: float):
        """Update wave manager"""
        # Handle wave transition
        if self.wave_completed:
            self.wave_transition_timer += dt
            if self.wave_transition_timer >= self.wave_transition_duration:
                self.wave_completed = False
                self.wave_transition_timer = 0.0
                self.start_wave()
            return
        
        # Spawn enemies
        if self.wave_in_progress and self.enemies_spawned < self.enemies_to_spawn:
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_interval:
                self._spawn_enemy()
                self.spawn_timer = 0.0
                
        # Update enemies
        self.enemies.update(dt)
        
        # Check if wave is complete
        if self.wave_in_progress and self.enemies_spawned >= self.enemies_to_spawn:
            if len(self.enemies) == 0:
                self.wave_in_progress = False
                self.wave_completed = True
                self.wave_transition_timer = 0.0
                print(f"Wave {self.current_wave} completed! Next wave in {self.wave_transition_duration} seconds...")
                
    def _spawn_enemy(self):
        """Spawn a new enemy"""
        if not self.player_ref:
            return
            
        # Get spawn position around player
        angle = random.uniform(0, 2 * math.pi)
        spawn_x = self.player_ref.rect.centerx + math.cos(angle) * self.wave_config['spawn_radius']
        spawn_y = self.player_ref.rect.centery + math.sin(angle) * self.wave_config['spawn_radius']
        
        # Choose enemy type
        if self.current_wave % self.wave_config['boss_wave_interval'] == 0 and self.enemies_spawned == self.enemies_to_spawn - 1:
            # Spawn boss (warrior)
            enemy_type = 'warrior'
        else:
            # Random enemy type with weighted selection
            weights = [0.5, 0.3, 0.2]  # goblin, archer, warrior
            enemy_type = random.choices(self.enemy_types, weights=weights)[0]
           
        # Create enemy
        enemy = Enemy(enemy_type, (spawn_x, spawn_y), self.player_ref,  all_enemies_group=self.enemies, collision_sprites=self.player_ref.collision_sprites)

        self.enemies.add(enemy)
        self.enemies_spawned += 1
    
    def draw(self, surface: pygame.Surface):
        """Draw all enemies and their health bars"""
        self.enemies.draw(surface)
        
        # Draw health bars
        for enemy in self.enemies:
            enemy.draw_health_bar(surface)
            
    def get_enemy_count(self) -> int:
        """Get current number of enemies"""
        return len(self.enemies)
        
    def clear_enemies(self):
        """Clear all enemies"""
        self.enemies.empty()
        self.wave_in_progress = False
        self.wave_completed = False
        self.wave_transition_timer = 0.0
        
    def get_wave_transition_progress(self) -> float:
        """Get progress of wave transition (0.0 to 1.0)"""
        if not self.wave_completed:
            return 0.0
        return min(1.0, self.wave_transition_timer / self.wave_transition_duration) 