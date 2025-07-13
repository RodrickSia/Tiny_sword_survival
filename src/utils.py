import pygame
import os
from typing import Dict, List, Tuple

class LoadSprite:
    def __init__(self, image_path):
        self.image = pygame.image.load(image_path).convert_alpha()
        print(f"Loaded sprite sheet size: {self.image.get_size()}")  # Debug info
    
    def get_image(self, x, y, width=192, height=192, scale=0.5):
        """Get a single sprite from specific coordinates"""
        # Create surface with per-pixel alpha
        img = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        img.fill((0, 0, 0, 0))  # Fill with transparent
        
        # Blit the sprite from the sheet
        img.blit(self.image, (0, 0), (x, y, width, height))
        
        # Scale the image
        if scale != 1:
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = pygame.transform.scale(img, (new_width, new_height))
        
        return img
    
    def get_all_animations_player(self, sprite_width=192, sprite_height=192, scale=0.5, spacing=0):
        """Get animations based on new sprite layout - 6 columns, 8 rows"""
        animations = {}
        
        print(f"Extracting animations with sprite size: {sprite_width}x{sprite_height}, scale: {scale}")
        print("Sprite sheet layout: 6 columns x 8 rows")
        
        # Row 0: Idle animation
        idle_frames = []
        for col in range(6):  # 6 columns
            x = col * sprite_width
            y = 0 * sprite_height
            frame = self.get_image(x, y, sprite_width, sprite_height, scale)
            idle_frames.append(frame)
        animations['idle'] = idle_frames
        print(f"Loaded idle animation: {len(idle_frames)} frames")
        
        # Row 1: Walking right animation
        walk_right_frames = []
        for col in range(6):  # 6 columns
            x = col * sprite_width
            y = 1 * sprite_height
            frame = self.get_image(x, y, sprite_width, sprite_height, scale)
            walk_right_frames.append(frame)
        animations['walk_right'] = walk_right_frames
        print(f"Loaded walk_right animation: {len(walk_right_frames)} frames")
        
        # Walking left: flip the walking right frames
        walk_left_frames = []
        for frame in walk_right_frames:
            flipped_frame = pygame.transform.flip(frame, True, False)
            walk_left_frames.append(flipped_frame)
        animations['walk_left'] = walk_left_frames
        print(f"Created walk_left animation: {len(walk_left_frames)} frames")
        
        # Row 2: First attack right sequence
        attack_right_frames = []
        for col in range(6):  # 6 columns
            x = col * sprite_width
            y = 2 * sprite_height
            frame = self.get_image(x, y, sprite_width, sprite_height, scale)
            attack_right_frames.append(frame)
        animations['attack_right'] = attack_right_frames
        print(f"Loaded attack_right animation: {len(attack_right_frames)} frames")
        
        # Row 3: Second attack right sequence  
        attack2_right_frames = []
        for col in range(6):  # 6 columns
            x = col * sprite_width
            y = 3 * sprite_height
            frame = self.get_image(x, y, sprite_width, sprite_height, scale)
            attack2_right_frames.append(frame)
        animations['attack2_right'] = attack2_right_frames
        print(f"Loaded attack2_right animation: {len(attack2_right_frames)} frames")
        
        # Attack left: flip both attack sequences
        attack_left_frames = []
        for frame in attack_right_frames:
            flipped_frame = pygame.transform.flip(frame, True, False)
            attack_left_frames.append(flipped_frame)
        animations['attack_left'] = attack_left_frames
        
        attack2_left_frames = []
        for frame in attack2_right_frames:
            flipped_frame = pygame.transform.flip(frame, True, False)
            attack2_left_frames.append(flipped_frame)
        animations['attack2_left'] = attack2_left_frames
        print(f"Created attack_left and attack2_left animations")
        
        # Row 4: First attack down sequence
        attack_down_frames = []
        for col in range(6):  # 6 columns
            x = col * sprite_width
            y = 4 * sprite_height
            frame = self.get_image(x, y, sprite_width, sprite_height, scale)
            attack_down_frames.append(frame)
        animations['attack_down'] = attack_down_frames
        print(f"Loaded attack_down animation: {len(attack_down_frames)} frames")
        
        # Row 5: Second attack down sequence
        attack2_down_frames = []
        for col in range(6):  # 6 columns
            x = col * sprite_width
            y = 5 * sprite_height
            frame = self.get_image(x, y, sprite_width, sprite_height, scale)
            attack2_down_frames.append(frame)
        animations['attack2_down'] = attack2_down_frames
        print(f"Loaded attack2_down animation: {len(attack2_down_frames)} frames")
        
        # Row 6: First attack up sequence
        attack_up_frames = []
        for col in range(6):  # 6 columns
            x = col * sprite_width
            y = 6 * sprite_height
            frame = self.get_image(x, y, sprite_width, sprite_height, scale)
            attack_up_frames.append(frame)
        animations['attack_up'] = attack_up_frames
        print(f"Loaded attack_up animation: {len(attack_up_frames)} frames")
        
        # Row 7: Second attack up sequence
        attack2_up_frames = []
        for col in range(6):  # 6 columns
            x = col * sprite_width
            y = 7 * sprite_height
            frame = self.get_image(x, y, sprite_width, sprite_height, scale)
            attack2_up_frames.append(frame)
        animations['attack2_up'] = attack2_up_frames
        print(f"Loaded attack2_up animation: {len(attack2_up_frames)} frames")
        
        print(f"Total animations loaded: {list(animations.keys())}")
        return animations
    
    # Keep your existing methods for backward compatibility
    def get_walking_animations(self, sprite_width=16, sprite_height=16, scale=2, spacing=0):
        """Extract walking animations for the first 4 rows and 4 columns"""
        animations = {
            'idle_down': [],
            'walk_down': [],
            'idle_up': [],
            'walk_up': [],
            'idle_left': [],
            'walk_left': [],
            'idle_right': [],
            'walk_right': []
        }
        
        # Direction mapping based on your sprite sheet order (columns are directions)
        directions = ['down', 'up', 'left', 'right']
        
        # Extract only the first 4 columns (directions) and 4 rows (frames)
        for col in range(4):  # Only first 4 columns (directions)
            direction = directions[col]
            
            # Get idle frame (first row)
            x = col * (sprite_width + spacing)
            y = 0 * (sprite_height + spacing)
            idle_frame = self.get_image(x, y, sprite_width, sprite_height, scale)
            animations[f'idle_{direction}'].append(idle_frame)
            
            # Get walking frames (first 4 rows)
            walk_frames = []
            for row in range(4):  # Only first 4 rows (frames)
                x = col * (sprite_width + spacing)
                y = row * (sprite_height + spacing)
                frame = self.get_image(x, y, sprite_width, sprite_height, scale)
                walk_frames.append(frame)
            
            animations[f'walk_{direction}'] = walk_frames
        
        return animations
    
    def get_attack_animations(self, sprite_width=16, sprite_height=16, scale=2, spacing=0):
        """Extract attack animations from row 5 (0-indexed row 4)"""
        animations = {
            'attack_down': [],
            'attack_up': [],
            'attack_left': [],
            'attack_right': []
        }
        
        # Direction mapping based on your sprite sheet order (columns are directions)
        directions = ['down', 'up', 'left', 'right']
        
        # Extract attack animations from row 5 (0-indexed row 4)
        attack_row = 4  # Row 5 in 1-indexed becomes row 4 in 0-indexed
        
        for col in range(4):  # Only first 4 columns (directions)
            direction = directions[col]
            
            # Get attack frames from row 5
            attack_frames = []
            for frame in range(4):  # Assuming 4 frames for attack animation
                x = col * (sprite_width + spacing)
                y = attack_row * (sprite_height + spacing)
                attack_frame = self.get_image(x, y, sprite_width, sprite_height, scale)
                attack_frames.append(attack_frame)
            
            animations[f'attack_{direction}'] = attack_frames
        
        return animations
    
    def get_all_animations(self, sprite_width=16, sprite_height=16, scale=2, spacing=0):
        """Get both walking and attack animations"""
        animations = {}
        
        # Get walking animations
        walk_animations = self.get_walking_animations(sprite_width, sprite_height, scale, spacing)
        animations.update(walk_animations)
        
        # Get attack animations
        attack_animations = self.get_attack_animations(sprite_width, sprite_height, scale, spacing)
        animations.update(attack_animations)
        
        return animations

class AnimationManager:
    def __init__(self, animations: Dict, animation_speeds: Dict[str, float]):
        self.animations = animations
        self.animation_speeds = animation_speeds
        self.current_animation = 'idle'
        self.animation_frame = 0
        self.animation_timer = 0
        self.distance_traveled = 0
        self.steps_per_frame = 20

    def create_directional_idle_animations(self):
        """Create left and right idle animations from existing idle"""
        if 'idle' in self.animations:
            # Rename current idle to idle_right
            self.animations['idle_right'] = self.animations['idle'].copy()
            
            # Create idle_left by horizontally flipping idle_right frames
            idle_left_frames = []
            for frame in self.animations['idle']:
                flipped_frame = pygame.transform.flip(frame, True, False)
                idle_left_frames.append(flipped_frame)
            self.animations['idle_left'] = idle_left_frames

    def get_animation_name(self, is_attacking: bool, attack_combo: int, is_moving: bool, 
                          direction: str, last_horizontal_direction: str) -> str:
        """Determine which animation to play based on current state"""
        if is_attacking:
            return self._get_attack_animation(direction, attack_combo)
        elif is_moving:
            return self._get_movement_animation(direction, last_horizontal_direction)
        else:
            return self._get_idle_animation(last_horizontal_direction)

    def _get_attack_animation(self, direction: str, combo: int) -> str:
        """Get attack animation based on direction and combo"""
        attack_type = 'attack' if combo == 0 else 'attack2'
        
        if direction in ['right', 'left']:
            return f'{attack_type}_{direction}'
        elif direction == 'up':
            return f'{attack_type}_up'
        else:  # down
            return f'{attack_type}_down'

    def _get_movement_animation(self, direction: str, last_horizontal: str) -> str:
        """Get movement animation based on direction"""
        if direction in ['right', 'left']:
            return f'walk_{direction}'
        elif direction in ['up', 'down']:
            return f'walk_{last_horizontal}'
        else:
            return 'walk_right'

    def _get_idle_animation(self, last_horizontal: str) -> str:
        """Get idle animation based on last horizontal direction"""
        return f'idle_{last_horizontal}'

    def should_reset_animation(self, new_animation: str, is_in_recovery: bool) -> bool:
        """Determine if animation should reset on transition"""
        if new_animation == self.current_animation:
            return False

        # Don't reset for similar animation types
        current_type = self.current_animation.split('_')[0]
        new_type = new_animation.split('_')[0]
        
        if current_type == new_type:
            return False

        # Don't reset when transitioning from attack to movement during recovery
        if (self.current_animation.startswith('attack') and 
            new_animation.startswith('walk') and 
            is_in_recovery):
            return False

        return True

    def update_animation(self, dt: float, is_attacking: bool, attack_combo: int, 
                        is_moving: bool, direction: str, last_horizontal_direction: str,
                        is_in_recovery: bool) -> pygame.Surface:
        """Update animation and return current frame"""
        new_animation = self.get_animation_name(is_attacking, attack_combo, is_moving, 
                                              direction, last_horizontal_direction)
        
        if self.should_reset_animation(new_animation, is_in_recovery):
            self.animation_frame = 0
            self.animation_timer = 0
            self.distance_traveled = 0
        
        self.current_animation = new_animation
        
        if self._should_advance_frame(dt, is_attacking, is_moving):
            self._advance_frame(is_attacking)
        
        return self._get_current_frame()

    def _should_advance_frame(self, dt: float, is_attacking: bool, is_moving: bool) -> bool:
        """Determine if frame should advance"""
        if self.current_animation.startswith('attack'):
            return self._update_time_based_animation(dt, 'attack')
        elif is_moving and self.current_animation.startswith('walk'):
            return self._update_time_based_animation(dt, 'walk')
        else:
            return self._update_time_based_animation(dt, 'idle')

    def _update_time_based_animation(self, dt: float, animation_type: str) -> bool:
        """Update time-based animation"""
        self.animation_timer += dt
        speed_key = f'{animation_type}_animation_speed'
        frame_duration = 1.0 / self.animation_speeds.get(speed_key, 8)
        
        if self.animation_timer >= frame_duration:
            self.animation_timer = 0
            return True
        return False

    def _update_distance_based_animation(self) -> bool:
        """Update distance-based animation for walking"""
        if self.distance_traveled >= self.steps_per_frame:
            self.distance_traveled = 0
            return True
        return False

    def _advance_frame(self, is_attacking: bool):
        """Advance to next animation frame"""
        if self.current_animation in self.animations:
            frames = self.animations[self.current_animation]
            
            if len(frames) > 0:
                if self.current_animation.startswith('attack') and is_attacking:
                    # Attack animations play once and hold last frame
                    if self.animation_frame < len(frames) - 1:
                        self.animation_frame += 1
                else:
                    # Other animations loop
                    self.animation_frame = (self.animation_frame + 1) % len(frames)

    def _get_current_frame(self) -> pygame.Surface:
        """Get current animation frame"""
        if self.current_animation in self.animations:
            frames = self.animations[self.current_animation]
            if len(frames) > 0:
                return frames[self.animation_frame]
        
        # Fallback
        if 'idle' in self.animations:
            return self.animations['idle'][0]
        return None

    def add_distance_traveled(self, distance: float):
        """Add distance for animation sync"""
        self.distance_traveled += distance

class InputHandler:
    def __init__(self):
        self.movement_keys = {
            pygame.K_w: (0, -1),
            pygame.K_s: (0, 1),
            pygame.K_a: (-1, 0),
            pygame.K_d: (1, 0)
        }
        self.attack_keys = [pygame.K_j]
        self.attack_key_pressed = False

    def get_movement_input(self) -> Tuple[float, float, bool, List[str]]:
        """Get movement input and return move vector, is_moving, and directions"""
        keys = pygame.key.get_pressed()
        
        move_x = 0
        move_y = 0
        is_moving = False
        moving_directions = []
        
        for key, (dx, dy) in self.movement_keys.items():
            if keys[key]:
                move_x += dx
                move_y += dy
                is_moving = True
                
                if dx > 0:
                    moving_directions.append('right')
                elif dx < 0:
                    moving_directions.append('left')
                if dy < 0:
                    moving_directions.append('up')
                elif dy > 0:
                    moving_directions.append('down')
        return move_x, move_y, is_moving, moving_directions

    def get_attack_input(self) -> bool:
        """Get attack input, returns True on new attack press"""
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed() # Return a tuple of mouse button states (left, middle, right)
        
        attack_input = mouse_buttons[0] or any(keys[key] for key in self.attack_keys)
        
        # Return True only on new press (not held)
        if attack_input and not self.attack_key_pressed:
            self.attack_key_pressed = True
            return True
        elif not attack_input:
            self.attack_key_pressed = False
        
        return False

    def update_direction(self, moving_directions: List[str], current_direction: str, 
                        last_direction: str, last_horizontal_direction: str) -> Tuple[str, str, str]:
        """Update direction based on movement input"""
        if not moving_directions:
            return current_direction, last_direction, last_horizontal_direction
        
        # Priority: horizontal movement first, then vertical
        if 'right' in moving_directions:
            return 'right', 'right', 'right'
        elif 'left' in moving_directions:
            return 'left', 'left', 'left'
        elif 'up' in moving_directions:
            return 'up', 'up', last_horizontal_direction
        elif 'down' in moving_directions:
            return 'down', 'down', last_horizontal_direction
        
        return current_direction, last_direction, last_horizontal_direction

class CombatSystem:
    def __init__(self, config):
        self.config = config
        self.player_ref = None
        self.audio_system = None
        
        # Attack state
        self.is_attacking = False
        self.attack_direction = 'right'
        self.attack_start_time = 0.0
        self.attack_combo = 0
        self.next_attack_time = 0.0
        
        # Combo system
        self.can_combo = False
        self.combo_available_time = 0.0
        self.combo_window_end = 0.0
        
        # Attack push/dash system
        self.attack_push_timer = 0.0
        self.is_in_recovery = False
        self.attack_recovery_timer = 0.0
        
    def set_player_ref(self, player):
        """Set reference to player object"""
        self.player_ref = player
        if hasattr(player, 'audio_system'):
            self.audio_system = player.audio_system
    
    def reset(self):
        """Reset combat system to initial state"""
        self.is_attacking = False
        self.attack_direction = 'right'
        self.attack_start_time = 0.0
        self.attack_combo = 0
        self.next_attack_time = 0.0
        self.can_combo = False
        self.combo_available_time = 0.0
        self.combo_window_end = 0.0
        self.attack_push_timer = 0.0
        self.is_in_recovery = False
        self.attack_recovery_timer = 0.0
        
    def try_attack(self, direction):
        """Try to execute an attack"""
        current_time = pygame.time.get_ticks() / 1000.0
        
        if not self.is_attacking and current_time >= self.next_attack_time:
            self._execute_attack(direction)
            return True
        elif self.is_attacking and self.can_combo and current_time >= self.combo_available_time:
            self._execute_combo_attack(direction)
            return True
        return False
    
    def _execute_attack(self, direction):
        """Execute the initial attack"""
        current_time = pygame.time.get_ticks() / 1000.0
        self.is_attacking = True
        self.attack_direction = direction
        self.attack_start_time = current_time
        self.attack_combo = 1
        
        # Play attack sound
        if self.audio_system:
            self.audio_system.play_sound('player_attack', volume=0.4)
        
        # Set up combo timing
        self.can_combo = True
        self.combo_available_time = current_time + 0.1
        self.combo_window_end = current_time + self.config['combo_window']
        
        # Set up attack push
        self.attack_push_timer = self.config['attack_push_duration']
        
        print(f"Attack 1 executed in direction: {direction}")
    
    def _execute_combo_attack(self, direction):
        """Execute a combo attack"""
        current_time = pygame.time.get_ticks() / 1000.0
        self.attack_combo = 2
        self.can_combo = False
        
        # Play attack sound for combo
        if self.audio_system:
            self.audio_system.play_sound('player_attack', volume=0.4)
        
        # Reset attack push for combo
        self.attack_push_timer = self.config['attack_push_duration']
        
        print(f"Combo attack executed in direction: {direction}")
    
    def update_timers(self, dt):
        """Update all combat timers"""
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Update attack state
        if self.is_attacking:
            if current_time >= self.attack_start_time + self.config['attack_duration']:
                self._end_attack()
        
        # Update combo window
        if self.can_combo and current_time >= self.combo_window_end:
            self.can_combo = False
        
        # Update attack push timer
        if self.attack_push_timer > 0:
            self.attack_push_timer -= dt
            if self.attack_push_timer <= 0:
                self.attack_push_timer = 0
                self.is_in_recovery = True
                self.attack_recovery_timer = self.config['attack_recovery_time']
        
        # Update recovery timer
        if self.is_in_recovery:
            self.attack_recovery_timer -= dt
            if self.attack_recovery_timer <= 0:
                self.is_in_recovery = False
                self.attack_recovery_timer = 0
    
    def _end_attack(self):
        """End the current attack"""
        current_time = pygame.time.get_ticks() / 1000.0
        self.is_attacking = False
        
        # Set cooldown for next attack
        if self.attack_combo >= 2:
            self.next_attack_time = current_time + self.config['combo_end_cooldown']
        else:
            self.next_attack_time = current_time + self.config['attack_cooldown']
        
        # Reset combo state
        self.can_combo = False
        self.attack_combo = 0
        
        print("Attack ended")
    
    def get_push_movement(self, dt):
        """Get push movement vector for attack dash"""
        if self.attack_push_timer <= 0:
            return 0, 0
        
        push_speed = self.config['attack_push_speed']
        progress = self.attack_push_timer / self.config['attack_push_duration']
        current_push_speed = push_speed * progress
        
        push_x, push_y = 0, 0
        if self.attack_direction == 'right':
            push_x = current_push_speed * dt
        elif self.attack_direction == 'left':
            push_x = -current_push_speed * dt
        elif self.attack_direction == 'down':
            push_y = current_push_speed * dt
        elif self.attack_direction == 'up':
            push_y = -current_push_speed * dt
        
        return push_x, push_y

# TESTING
'''
def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    sprite_path = os.path.join("..", "assets", "Factions", "Knights", "Troops", "Warrior", "Blue", "Warrior_Blue.png")

    load = LoadSprite(sprite_path)
    
    # Get all animations with correct sprite dimensions
    animations = load.get_all_animations_new_layout(sprite_width=192, sprite_height=192, scale=0.5)
    
    pygame.display.set_caption("All Animations Display")
    running = True
    current_animation = 0
    animation_names = list(animations.keys())
    frame_index = 0
    timer = 0
    
    while running:
        dt = pygame.time.Clock().tick(60) / 1000.0
        timer += dt
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    current_animation = (current_animation + 1) % len(animation_names)
                    frame_index = 0
                    timer = 0
                    print(f"Switched to animation: {animation_names[current_animation]}")
        
        # Auto-advance frames
        if timer > 0.2:  # Change frame every 200ms
            frame_index = (frame_index + 1) % len(animations[animation_names[current_animation]])
            timer = 0
        
        # Display current animation
        animation_name = animation_names[current_animation]
        frames = animations[animation_name]
        current_frame = frames[frame_index]
        
        screen.fill((50, 50, 50))  # Dark gray background
        screen.blit(current_frame, (400 - current_frame.get_width()//2, 300 - current_frame.get_height()//2))
        
        # Display animation info
        font = pygame.font.Font(None, 36)
        text = font.render(f"{animation_name} - Frame {frame_index + 1}/{len(frames)}", True, (255, 255, 255))
        screen.blit(text, (50, 50))
        
        instruction_text = font.render("Press SPACE to change animation", True, (255, 255, 255))
        screen.blit(instruction_text, (50, 100))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
'''