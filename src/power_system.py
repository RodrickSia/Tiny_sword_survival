import pygame
from typing import List, Callable

class PowerBar:
    def __init__(self, width: int = 200, height: int = 8, border_width: int = 1):
        self.width = width
        self.height = height
        self.border_width = border_width
        
        # Colors
        self.border_color = (0, 0, 0)
        self.background_color = (32, 32, 32)
        self.power_color = (255, 255, 0)  # Yellow
        self.full_color = (255, 0, 255)   # Magenta when full
        
    def draw(self, surface: pygame.Surface, current_power: int, max_power: int, position: tuple):
        """Draw power bar at given position"""
        x, y = position
        
        # Draw border
        pygame.draw.rect(surface, self.border_color, 
                        (x - self.border_width, y - self.border_width, 
                         self.width + self.border_width * 2, 
                         self.height + self.border_width * 2))
        
        # Draw background
        pygame.draw.rect(surface, self.background_color, 
                        (x, y, self.width, self.height))
        
        # Draw power
        power_width = int(self.width * (current_power / max_power))
        if power_width > 0:
            # Change color based on power level
            color = self.full_color if current_power >= max_power else self.power_color
            pygame.draw.rect(surface, color, (x, y, power_width, self.height))

class PowerSystem:
    def __init__(self, max_power: int = 100):
        self.current_power = 0
        self.max_power = max_power
        self.power_bar = PowerBar(width=200, height=8)
        
        # Power up effects
        self.power_up_effects = [
            'health_boost',      # Tăng máu
            'damage_boost',      # Tăng sát thương
            'speed_boost',       # Tăng tốc độ
            'invulnerability',   # Bất tử tạm thời
            'rapid_fire',        # Tấn công nhanh
            'area_attack'        # Tấn công diện rộng
        ]
        
        # Callback when power up is activated
        self.on_power_up: Callable = None
        
    def add_power(self, amount: int) -> bool:
        """Add power and return True if power up is triggered"""
        self.current_power = min(self.max_power, self.current_power + amount)
        
        # Check if power up is triggered
        if self.current_power >= self.max_power:
            self.trigger_power_up()
            return True
        return False
        
    def trigger_power_up(self):
        """Trigger a power up effect"""
        import random
        effect = random.choice(self.power_up_effects)
        
        # Reset power bar
        self.current_power = 0
        
        # Call callback if set
        if self.on_power_up:
            self.on_power_up(effect)
            
    def get_power_percentage(self) -> float:
        """Get current power as a percentage"""
        return self.current_power / self.max_power if self.max_power > 0 else 0
        
    def reset(self):
        """Reset power to 0"""
        self.current_power = 0
        
    def draw(self, surface: pygame.Surface, position: tuple):
        """Draw power bar"""
        self.power_bar.draw(surface, self.current_power, self.max_power, position) 