import pygame
import random
import math
import os
from typing import List, Dict, Tuple
from utils import LoadSprite, AnimationManager
from health_system import HealthSystem, HealthBar
from pygame.math import Vector2
from map_loader import MapLoader


class Arrow(pygame.sprite.Sprite):
    def __init__(self, start_pos: Tuple[int, int], target_pos: Tuple[int, int], damage: int, speed: float = 200, player_velocity: Tuple[float, float] = (0, 0)):
        super().__init__()
        
        # Arrow properties
        self.damage = damage
        self.speed = speed
        self.lifetime = 100.0  # Arrow disappears after 18 seconds (tăng 1.5 lần từ 12)
        self.lifetime_timer = 0.0
        
        # Trail effect properties
        self.trail_positions = []
        self.max_trail_length = 12  # Tăng trail cho đẹp
        
        # Calculate direction to current target position (không dự đoán)
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            self.direction_x = dx / distance
            self.direction_y = dy / distance
        else:
            self.direction_x = 0
            self.direction_y = 1
        
        # Vẽ lại mũi tên với hình dạng đẹp hơn
        arrow_w, arrow_h = 80, 16  # Giảm chiều cao để mũi tên mảnh hơn
        self.image = pygame.Surface((arrow_w, arrow_h), pygame.SRCALPHA)
        
        # Bóng dưới mũi tên
        shadow = pygame.Surface((arrow_w, 4), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0,0,0,40), (10, arrow_h-4, arrow_w-20, 4))
        self.image.blit(shadow, (0,0))
        
        # Thân mũi tên (gradient nâu-vàng)
        for i in range(50):
            # Gradient từ nâu sang vàng
            color = (
                139 + int(i*2),  # R tăng dần
                69 + int(i*3),   # G tăng dần
                19 + int(i*4)    # B tăng dần
            )
            pygame.draw.rect(self.image, color, (10+i, 6, 1, 4))
        
        # Đầu mũi tên (hình tam giác cân, màu xám đậm)
        pygame.draw.polygon(self.image, (64,64,64), [(60,2),(arrow_w-2,arrow_h//2),(60,arrow_h-2)])
        # Viền đầu mũi tên
        pygame.draw.polygon(self.image, (32,32,32), [(60,2),(arrow_w-2,arrow_h//2),(60,arrow_h-2)], 1)
        
        # Đuôi lông vũ (3 lông vũ trắng)
        feather_colors = [(255,255,255), (240,240,240), (220,220,220)]
        for i in range(3):
            y_offset = 2 + i * 2
            pygame.draw.polygon(self.image, feather_colors[i], [(8,arrow_h//2),(2,y_offset),(2,arrow_h-y_offset)])
        
        # Thêm chi tiết lông vũ
        pygame.draw.line(self.image, (200,200,200), (4,4), (8,arrow_h//2), 1)
        pygame.draw.line(self.image, (200,200,200), (4,arrow_h-4), (8,arrow_h//2), 1)
        pygame.draw.line(self.image, (180,180,180), (6,6), (8,arrow_h//2), 1)
        pygame.draw.line(self.image, (180,180,180), (6,arrow_h-6), (8,arrow_h//2), 1)
        self.rect = self.image.get_rect()
        # Position
        self.rect.center = start_pos
        self.pos_x = float(start_pos[0])
        self.pos_y = float(start_pos[1])
        # Calculate rotation angle
        self.angle = math.degrees(math.atan2(-dy, dx))
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        
    def update(self, dt: float):
        """Update arrow movement"""
        self.lifetime_timer += dt
        
        if self.lifetime_timer >= self.lifetime:
            self.kill()
            return
        
        # Store current position for trail
        self.trail_positions.append((int(self.pos_x), int(self.pos_y)))
        if len(self.trail_positions) > self.max_trail_length:
            self.trail_positions.pop(0)
        
        # Move arrow
        self.pos_x += self.direction_x * self.speed * dt
        self.pos_y += self.direction_y * self.speed * dt
        
        # Update rect
        self.rect.center = (int(self.pos_x), int(self.pos_y))
        
    def draw(self, surface: pygame.Surface):
        """Draw the arrow with trail effect"""
        # Draw trail với hiệu ứng mờ dần (không còn vạch ngang rõ ràng)
        for i, pos in enumerate(self.trail_positions):
            # Alpha giảm dần từ đầu đến cuối trail
            alpha = int(80 * (i / len(self.trail_positions)))
            if alpha > 5:  # Chỉ vẽ nếu đủ sáng
                # Trail nhỏ hơn và mờ hơn
                trail_surface = pygame.Surface((16, 3), pygame.SRCALPHA)
                trail_surface.fill((255, 180, 40, alpha))  # Màu cam nhạt thay vì vàng
                trail_rect = trail_surface.get_rect(center=pos)
                surface.blit(trail_surface, trail_rect)
        
        # Draw main arrow
        surface.blit(self.image, self.rect)

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
                'speed': 80,
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
                'speed': 70,
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
                'speed': 60,
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

        # AI state
        self.state = 'chase'  # chase, attack, retreat, dead
        self.attack_timer = 0.0
        self.last_attack_time = 0.0
        
        # Archer specific properties
        self.arrows = pygame.sprite.Group()
        self.is_archer = enemy_type == 'archer'
        
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
            'idle_animation_speed': 10,
            'walk_animation_speed': 15,
            'attack_animation_speed': 18
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

        self.old_rect = self.rect.copy()
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
        
        # Update arrows if archer
        if self.is_archer:
            self.arrows.update(dt)

        

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
        
        # Determine state based on enemy type
        if self.is_archer:
            # Archer behavior: keep distance and shoot
            min_range = 80  # Minimum distance to keep
            max_range = self.config['attack_range']  # Maximum shooting range
            
            if distance < min_range:
                self.state = 'retreat'
            elif distance <= max_range:
                self.state = 'attack'
            else:
                self.state = 'chase'
        else:
            # Melee enemy behavior
            if distance <= self.config['attack_range']:
                self.state = 'attack'
            else:
                self.state = 'chase'
            
        # Execute state behavior
        if self.state == 'chase':
            self._chase_player(dt, dx, dy, distance)
        elif self.state == 'attack':
            self._attack_player(dt, dx, dy, distance)
        elif self.state == 'retreat':
            self._retreat_from_player(dt, dx, dy, distance)
            
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
            # Di chuyển theo trục X
            self.pos_x += move_x
            self.rect.x = int(self.pos_x)
            self.check_collision('horizontal')

            # Di chuyển theo trục Y
            self.pos_y += move_y
            self.rect.y = int(self.pos_y)
            self.check_collision('vertical')
            
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

    def check_collision(self, direction):
        hits = pygame.sprite.spritecollide(self, self.collision_sprites, False)
        if direction == 'horizontal':
            for sprite in hits:
                if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.rect.left:
                    self.rect.right = sprite.rect.left
                    self.pos_x = self.rect.x
                elif self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.rect.right:
                    self.rect.left = sprite.rect.right
                    self.pos_x = self.rect.x
        elif direction == 'vertical':
            for sprite in hits:
                if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.rect.top:
                    self.rect.bottom = sprite.rect.top
                    self.pos_y = self.rect.y
                elif self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.rect.bottom:
                    self.rect.top = sprite.rect.bottom
                    self.pos_y = self.rect.y
        
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
        if not self.player_ref or not self.player_ref.health_system.is_alive():
            return
            
        if self.is_archer:
            # Archer shoots arrow
            self._shoot_arrow()
        else:
            # Melee attack
            self.player_ref.take_damage(self.config['damage'])
        
        #direction = pygame.math.Vector2(self.player_ref.rect.center) - pygame.math.Vector2(self.rect.center)
        #if direction.length() == 0:
           # direction = pygame.math.Vector2(1, 0)
        #direction = direction.normalize()

    # Knockback ngược hướng tấn công
        #self.knockback_vector = -direction * 250  # 150 px/s là tốc độ bị đẩy lùi
        #self.knockback_timer = self.knockback_duration

        self.player_ref.rect.x = int(self.player_ref.pos_x)
        self.player_ref.rect.y = int(self.player_ref.pos_y)

    def _shoot_arrow(self):
        """Shoot an arrow at the player"""
        if not self.player_ref:
            return
            
        # Calculate target position (current player position)
        target_x = self.player_ref.rect.centerx
        target_y = self.player_ref.rect.centery
        
        # Create arrow with current target position (no prediction)
        arrow = Arrow(
            start_pos=self.rect.center,
            target_pos=(target_x, target_y),
            damage=self.config['damage'],
            speed=200,  # Giảm tốc độ từ 350 xuống 200
            player_velocity=(0, 0)  # Không dùng prediction
        )
        
        # Add arrow to group
        self.arrows.add(arrow)

    def _retreat_from_player(self, dt: float, dx: float, dy: float, distance: float):
        """Retreat from player (for archers)"""
        if distance > 0:
            # Move away from player
            dx = -dx / distance
            dy = -dy / distance
            
            # Move away from player
            speed = self.config['speed'] * 0.8  # Slightly slower when retreating
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
    
    def draw_arrows(self, surface: pygame.Surface):
        """Draw arrows if archer"""
        if self.is_archer:
            for arrow in self.arrows:
                arrow.draw(surface)


    

class WaveManager:
    def __init__(self, player_ref, collision_sprites=None):
        self.player_ref = player_ref
        self.collision_sprites = collision_sprites or pygame.sprite.Group()

        self.current_wave = 0
        self.enemies = pygame.sprite.Group()
        self.enemy_types = ['goblin', 'archer', 'warrior']
        
        # Wave configuration
        self.wave_config = {
            'enemies_per_wave': 4,
            'enemy_increase_per_wave': 1,
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
         # Camera view (giả sử logic 1280x720, có thể lấy từ Game nếu cần)
        self.camera_rect = pygame.Rect(0, 0, 1280, 720)
        
        
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
        
    def update(self, dt: float, camera_rect=None):
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
        if camera_rect is None:
            camera_rect = self.camera_rect
        for enemy in list(self.enemies):
            if camera_rect.colliderect(enemy.rect):
                enemy.update(dt)
            else:
                # Update arrows even if enemy is off-screen (for long-range arrows)
                if enemy.is_archer:
                    enemy.arrows.update(dt)
        
        # Check arrow collisions with player
        self._check_arrow_collisions()
        
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
        spawn_rect = pygame.Rect(200, 200, 900, 400)  # ví dụ: mép phải màn hình

        spawn_x = random.uniform(spawn_rect.left, spawn_rect.right)
        spawn_y = random.uniform(spawn_rect.top, spawn_rect.bottom)
        
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
    
    def draw(self, surface: pygame.Surface, camera_rect=None):
        """Draw all enemies and their health bars (only if visible)"""
        if camera_rect is None:
            camera_rect = self.camera_rect
        
        # Draw enemies and their arrows
        for enemy in self.enemies:
            if camera_rect.colliderect(enemy.rect):
                surface.blit(enemy.image, enemy.rect)
                enemy.draw_health_bar(surface)
                enemy.draw_arrows(surface)
            else:
                # Draw arrows even if enemy is off-screen (for long-range arrows)
                enemy.draw_arrows(surface)
            
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
    
    def _check_arrow_collisions(self):
        """Check if any arrows hit the player"""
        if not self.player_ref:
            return
            
        for enemy in self.enemies:
            if enemy.is_archer:
                for arrow in list(enemy.arrows):
                    if arrow.rect.colliderect(self.player_ref.rect):
                        # Arrow hit player
                        self.player_ref.take_damage(arrow.damage)
                        arrow.kill()  # Remove the arrow
    
    def _check_arrow_collisions(self):
        """Check if any arrows hit the player"""
        if not self.player_ref:
            return
            
        for enemy in self.enemies:
            if enemy.is_archer:
                for arrow in list(enemy.arrows):
                    if arrow.rect.colliderect(self.player_ref.rect):
                        # Arrow hit player
                        self.player_ref.take_damage(arrow.damage)
                        arrow.kill()  # Remove the arrow 