import pygame
import os
from utils import LoadSprite, AnimationManager, InputHandler, CombatSystem
from health_system import HealthSystem, HealthBar
from power_system import PowerSystem

class Player(pygame.sprite.Sprite):
    def __init__(self, groups , pos=(400, 300), collision_sprites = None ):
        super().__init__(groups)
        
        # Configuration
        self.config = {
            'speed': 250,
            'attack_duration': 0.2,
            'attack_cooldown': 0.025,
            'max_combo': 2,
            'combo_window': 0.6,
            'combo_end_cooldown': 0.4,
            'attack_push_speed': 400,
            'attack_push_duration': 0.12,
            'attack_recovery_time': 0.08,
            'max_health': 100,
            'base_damage': 25
        }
        
        # Initialize sprite system
        self._init_sprite_system()
        
        # Initialize systems
        self._init_systems()
        
        # Initialize health system
        self._init_health_system()
        
        # Initialize power system
        self._init_power_system()
        
        # Stats tracking
        self.enemies_killed = 0
        self.waves_survived = 0
        
        # Movement properties
        self.diagonal_speed = self.config['speed'] * 0.707
        
        # Position
        self.rect.center = pos
        self.pos = pygame.math.Vector2(self.rect.topleft)

        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        self.old_rect = self.rect.copy()
        # Movement and direction state
        self.is_moving = False
        self.direction = 'right'
        self.last_direction = 'right'
        self.last_horizontal_direction = 'right'
        
        # Input state
        self.move_x = 0
        self.move_y = 0

        # Collision system - accept collision sprites from parameter
        self.collision_sprites = collision_sprites

    def _init_sprite_system(self):
        """Initialize sprite and animation system"""
        sprite_path = os.path.join("assets", "Factions", "Knights", "Troops", "Warrior", "Blue", "Warrior_Blue.png")
        sprite_loader = LoadSprite(sprite_path)
        animations = sprite_loader.get_all_animations_player(sprite_width=192, sprite_height=192, scale=0.75)
        
        animation_speeds = {
            'idle_animation_speed': 8,
            'attack_animation_speed': 25
        }
        
        # Because there is no left idle animation we need to create both left and right idle animation
        self.animation_manager = AnimationManager(animations, animation_speeds)
        self.animation_manager.create_directional_idle_animations()
        
        # Set initial image
        self.image = self.animation_manager._get_current_frame()
        self.rect = self.image.get_rect()

    def _init_systems(self):
        """Initialize system objects"""
        self.input_handler = InputHandler()
        self.combat_system = CombatSystem(self.config)
        self.combat_system.set_player_ref(self)  # Set reference to self

    def _init_health_system(self):
        """Initialize health system"""
        self.health_system = HealthSystem(self.config['max_health'])
        self.health_bar = HealthBar(width=200, height=15)

    def _init_power_system(self):
        """Initialize power system"""
        self.power_system = PowerSystem(max_power=100)
        self.power_system.on_power_up = self._handle_power_up
        
        # Power up effects tracking
        self.active_power_ups = {}
        self.base_stats = {
            'damage': self.config['base_damage'],
            'speed': self.config['speed'],
            'attack_cooldown': self.config['attack_cooldown']
        }
        # Hiệu ứng power up vừa nhận
        self.last_powerup_effect = None
        self.last_powerup_time = 0
        self.last_powerup_desc = None

    def _handle_power_up(self, effect_type: str):
        """Handle power up effects"""
        import time
        effect_desc = {
            'health_boost': '💚 Health Boost: +50 HP!',
            'damage_boost': '⚔️ Damage Boost: Double damage for 10s!',
            'speed_boost': '🏃 Speed Boost: +50% speed for 8s!',
            'invulnerability': '🛡️ Invulnerability: Immune to damage for 5s!',
            'rapid_fire': '⚡ Rapid Fire: 70% faster attacks for 12s!',
            'area_attack': '💥 Area Attack: 50% larger attack range for 15s!'
        }
        self.last_powerup_effect = effect_type
        self.last_powerup_time = time.time()
        self.last_powerup_desc = effect_desc.get(effect_type, effect_type)
        
        if effect_type == 'health_boost':
            self.health_system.heal(50)
            print(effect_desc['health_boost'])
        elif effect_type == 'damage_boost':
            duration = 10.0
            self.active_power_ups['damage_boost'] = {
                'start_time': time.time(),
                'duration': duration,
                'multiplier': 2.0
            }
            print(effect_desc['damage_boost'])
        elif effect_type == 'speed_boost':
            duration = 8.0
            self.active_power_ups['speed_boost'] = {
                'start_time': time.time(),
                'duration': duration,
                'multiplier': 1.5
            }
            print(effect_desc['speed_boost'])
        elif effect_type == 'invulnerability':
            duration = 5.0
            self.active_power_ups['invulnerability'] = {
                'start_time': time.time(),
                'duration': duration
            }
            self.health_system.is_invulnerable = True
            self.health_system.invulnerability_time = duration
            print(effect_desc['invulnerability'])
        elif effect_type == 'rapid_fire':
            duration = 12.0
            self.active_power_ups['rapid_fire'] = {
                'start_time': time.time(),
                'duration': duration,
                'multiplier': 0.3
            }
            print(effect_desc['rapid_fire'])
        elif effect_type == 'area_attack':
            duration = 15.0
            self.active_power_ups['area_attack'] = {
                'start_time': time.time(),
                'duration': duration,
                'range_multiplier': 1.5
            }
            print(effect_desc['area_attack'])

    def update_power_ups(self, dt):
        """Update active power up timers"""
        import time
        current_time = time.time()
        
        # Check for expired power ups
        expired_effects = []
        for effect_name, effect_data in self.active_power_ups.items():
            if current_time - effect_data['start_time'] >= effect_data['duration']:
                expired_effects.append(effect_name)
                print(f"⏰ {effect_name.title()} effect expired!")
        
        # Remove expired effects
        for effect_name in expired_effects:
            del self.active_power_ups[effect_name]
            
        # Handle specific effect cleanup
        if 'invulnerability' in expired_effects:
            self.health_system.is_invulnerable = False

    def handle_input(self):
        """Handle player input and return movement vector"""
        # Get movement input
        self.move_x, self.move_y, self.is_moving, moving_directions = self.input_handler.get_movement_input()
        
        # Update direction based on movement (only when not attacking)
        if not self.combat_system.is_attacking:
            self.direction, self.last_direction, self.last_horizontal_direction = \
                self.input_handler.update_direction(moving_directions, self.direction, 
                                                  self.last_direction, self.last_horizontal_direction)
        
        # Handle attack input with improved detection
        attack_pressed = self.input_handler.get_attack_input()
        if attack_pressed:
            # Try to queue or execute attack
            self.combat_system.try_attack(self.direction)
        
        # Don't move while attacking
        if self.combat_system.is_attacking:
            self.move_x = 0
            self.move_y = 0
            self.is_moving = False
        
        return self.move_x, self.move_y
    

    def collision(self, direction):
        col_sprites = pygame.sprite.spritecollide(self, self.collision_sprites, False)
        if col_sprites:
            if direction == 'horizontal':
                for sprite in col_sprites:
                    if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.rect.left:
                        self.rect.right = sprite.rect.left
                        self.pos_x = self.rect.x

                    if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.rect.right:
                        self.rect.left = sprite.rect.right
                        self.pos_x = self.rect.x

            if direction == 'vertical':
                for sprite in col_sprites:
                    if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.rect.top:
                        self.rect.bottom = sprite.rect.top
                        self.pos_y = self.rect.y

                    if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.rect.bottom:
                        self.rect.top = sprite.rect.bottom
                        self.pos_y = self.rect.y


    def update(self, dt):
        self.old_rect = self.rect.copy()
        """Main update function"""
        # Update health system
        self.health_system.update(dt)
        
        # Update power ups
        self.update_power_ups(dt)
        
        # Update combat system timers
        self.combat_system.update_timers(dt)
        
        # Handle input
        move_x, move_y = self.handle_input()
        
        # Apply movement
        self._apply_movement(dt, move_x, move_y)
        
        # Update animation
        self._update_animation(dt)

        

       

    def _apply_movement(self, dt, move_x, move_y):
        """Apply movement calculations"""
        total_move_x, total_move_y = 0, 0
        
        # Regular movement
        if self.is_moving and not self.combat_system.is_attacking:
            total_move_x, total_move_y = self._calculate_regular_movement(dt, move_x, move_y)
        
        # Attack push movement
        push_x, push_y = self.combat_system.get_push_movement(dt)
        total_move_x += push_x
        total_move_y += push_y
        
        # Apply movement
        if total_move_x != 0 or total_move_y != 0:
            self._update_position(total_move_x, total_move_y)

    def _calculate_regular_movement(self, dt, move_x, move_y):
        """Calculate regular movement"""
        is_diagonal = (move_x != 0 and move_y != 0)
        base_speed = self.get_speed()  # Use dynamic speed from power ups
        diagonal_speed = base_speed * 0.707
        
        current_speed = diagonal_speed if is_diagonal else base_speed
        
        # Apply recovery speed reduction
        if self.combat_system.is_in_recovery:
            recovery_progress = self.combat_system.attack_recovery_timer / self.config['attack_recovery_time']
            speed_multiplier = 0.3 + (0.7 * recovery_progress)
            current_speed = current_speed * speed_multiplier
        
        move_x = move_x * current_speed * dt
        move_y = move_y * current_speed * dt
        
        return move_x, move_y

    def _update_position(self, total_move_x, total_move_y):
        """Update player position"""
        self.pos_x += total_move_x
        self.pos_y += total_move_y
        
        # Track distance for animation
        if self.is_moving and not self.combat_system.is_attacking:
            distance = (total_move_x**2 + total_move_y**2)**0.5
            self.animation_manager.add_distance_traveled(distance)
        
        # Keep on screen
        self.pos_x = max(0, min(1280 - self.rect.width, self.pos_x))
        self.pos_y = max(0, min(800 - self.rect.height, self.pos_y))
        
        self.rect.x = int(self.pos_x)
        self.collision('horizontal')
        self.rect.y = int(self.pos_y)
        self.collision('vertical')


    def _update_animation(self, dt):
        """Update animation"""
        self.image = self.animation_manager.update_animation(
            dt, self.combat_system.is_attacking, self.combat_system.attack_combo,
            self.is_moving, self.direction, self.last_horizontal_direction,
            self.combat_system.is_in_recovery
        )

    def take_damage(self, damage: int) -> bool:
        """Take damage from enemies"""
        return self.health_system.take_damage(damage)

    def heal(self, amount: int) -> bool:
        """Heal the player"""
        return self.health_system.heal(amount)

    def get_damage(self) -> int:
        """Get current attack damage with power up modifiers"""
        damage = self.base_stats['damage']
        
        # Apply damage boost if active
        if 'damage_boost' in self.active_power_ups:
            damage *= self.active_power_ups['damage_boost']['multiplier']
            
        return int(damage)

    def get_speed(self) -> float:
        """Get current movement speed with power up modifiers"""
        speed = self.base_stats['speed']
        
        # Apply speed boost if active
        if 'speed_boost' in self.active_power_ups:
            speed *= self.active_power_ups['speed_boost']['multiplier']
            
        return speed

    def get_attack_cooldown(self) -> float:
        """Get current attack cooldown with power up modifiers"""
        cooldown = self.base_stats['attack_cooldown']
        
        # Apply rapid fire if active
        if 'rapid_fire' in self.active_power_ups:
            cooldown *= self.active_power_ups['rapid_fire']['multiplier']
            
        return cooldown

    def get_attack_range(self) -> float:
        """Get current attack range with power up modifiers"""
        base_range = 10
        
        # Apply area attack if active
        if 'area_attack' in self.active_power_ups:
            base_range *= self.active_power_ups['area_attack']['range_multiplier']
            
        return base_range

    def get_active_power_ups(self) -> dict:
        """Get currently active power ups with remaining time"""
        import time
        current_time = time.time()
        active_effects = {}
        
        for effect_name, effect_data in self.active_power_ups.items():
            remaining_time = effect_data['duration'] - (current_time - effect_data['start_time'])
            if remaining_time > 0:
                active_effects[effect_name] = {
                    'timer': remaining_time,
                    'duration': effect_data['duration']
                }
                
        return active_effects

    def is_alive(self) -> bool:
        """Check if player is alive"""
        return self.health_system.is_alive()

    def add_power(self, amount: int) -> bool:
        """Add power and return True if power up was triggered"""
        return self.power_system.add_power(amount)

    def on_enemy_killed(self):
        """Called when player kills an enemy"""
        self.enemies_killed += 1
        # Add power for killing enemy
        power_gained = 15  # 15 power per enemy killed
        if self.add_power(power_gained):
            print(f"Power up triggered! Enemies killed: {self.enemies_killed}")

    def on_wave_completed(self):
        """Called when a wave is completed"""
        self.waves_survived += 1

    def reset(self):
        """Reset player to initial state"""
        self.health_system.reset()
        self.combat_system.reset()
        self.power_system.reset()
        self.enemies_killed = 0
        self.waves_survived = 0
        self.pos_x = 640  # Center of screen
        self.pos_y = 400
        self.rect.center = (self.pos_x, self.pos_y)

    def get_last_powerup_popup(self):
        """Trả về (desc, thời gian còn lại) nếu hiệu ứng vừa nhận còn hiển thị"""
        import time
        popup_duration = 2.5  # giây
        if self.last_powerup_effect and (time.time() - self.last_powerup_time) < popup_duration:
            return self.last_powerup_desc, popup_duration - (time.time() - self.last_powerup_time)
        return None, 0