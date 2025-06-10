import pygame
import os
from utils import LoadSprite, AnimationManager, InputHandler, CombatSystem

class Player(pygame.sprite.Sprite):
    def __init__(self, pos=(400, 300), collision_sprites=None):
        super().__init__()
        
        # Configuration
        self.config = {
            'speed': 350,
            'attack_duration': 0.2,
            'attack_cooldown': 0.025,
            'max_combo': 2,
            'combo_window': 0.6,
            'combo_end_cooldown': 0.4,
            'attack_push_speed': 400,
            'attack_push_duration': 0.12,
            'attack_recovery_time': 0.08
        }
        
        # Initialize sprite system
        self._init_sprite_system()
        
        # Initialize systems
        self._init_systems()
        
        # Movement properties
        self.diagonal_speed = self.config['speed'] * 0.707
        
        # Position
        self.rect.center = pos
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        
        # Movement and direction state
        self.is_moving = False
        self.direction = 'right'
        self.last_direction = 'right'
        self.last_horizontal_direction = 'right'
        
        # Input state
        self.move_x = 0
        self.move_y = 0

        # Collision system - accept collision sprites from parameter
        self.collision_sprites = collision_sprites or pygame.sprite.Group()

    def _init_sprite_system(self):
        """Initialize sprite and animation system"""
        sprite_path = os.path.join("..", "assets", "Factions", "Knights", "Troops", "Warrior", "Blue", "Warrior_Blue.png")
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

    def update(self, dt):
        """Main update function"""
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
        base_speed = self.diagonal_speed if is_diagonal else self.config['speed']
        
        # Apply recovery speed reduction
        if self.combat_system.is_in_recovery:
            recovery_progress = self.combat_system.attack_recovery_timer / self.config['attack_recovery_time']
            speed_multiplier = 0.3 + (0.7 * recovery_progress)
            current_speed = base_speed * speed_multiplier
        else:
            current_speed = base_speed
        
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
        self.rect.y = int(self.pos_y)

    def _update_animation(self, dt):
        """Update animation"""
        self.image = self.animation_manager.update_animation(
            dt, self.combat_system.is_attacking, self.combat_system.attack_combo,
            self.is_moving, self.direction, self.last_horizontal_direction,
            self.combat_system.is_in_recovery
        )