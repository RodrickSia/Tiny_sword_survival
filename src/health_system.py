import pygame
from typing import Optional, Callable

class HealthSystem:
    def __init__(self, max_health: int, current_health: Optional[int] = None):
        self.max_health = max_health
        self.current_health = current_health if current_health is not None else max_health
        self.invulnerability_time = 0.0
        self.invulnerability_duration = 1.0  # 1 second of invulnerability after taking damage
        self.is_invulnerable = False
        
        # Callback for when health reaches 0
        self.on_death: Optional[Callable] = None
        
    def take_damage(self, damage: int) -> bool:
        """Take damage and return True if damage was actually taken"""
        if self.is_invulnerable or self.current_health <= 0:
            return False
            
        self.current_health = max(0, self.current_health - damage)
        self.is_invulnerable = True
        self.invulnerability_time = self.invulnerability_duration
        
        if self.current_health <= 0 and self.on_death:
            self.on_death()
            
        return True
    
    def heal(self, amount: int) -> bool:
        """Heal and return True if healing was applied"""
        if self.current_health <= 0:
            return False
            
        old_health = self.current_health
        self.current_health = min(self.max_health, self.current_health + amount)
        return self.current_health > old_health
    
    def update(self, dt: float):
        """Update invulnerability timer"""
        if self.is_invulnerable:
            self.invulnerability_time -= dt
            if self.invulnerability_time <= 0:
                self.is_invulnerable = False
    
    def get_health_percentage(self) -> float:
        """Get current health as a percentage"""
        return self.current_health / self.max_health if self.max_health > 0 else 0
    
    def is_alive(self) -> bool:
        """Check if entity is alive"""
        return self.current_health > 0
    
    def reset(self):
        """Reset health to maximum"""
        self.current_health = self.max_health
        self.is_invulnerable = False
        self.invulnerability_time = 0.0

class HealthBar:
    def __init__(self, width: int = 100, height: int = 10, border_width: int = 2):
        self.width = width
        self.height = height
        self.border_width = border_width
        
        # Colors
        self.border_color = (0, 0, 0)
        self.background_color = (64, 64, 64)
        self.health_color = (0, 255, 0)
        self.low_health_color = (255, 0, 0)
        
    def draw(self, surface: pygame.Surface, health_system: HealthSystem, position: tuple):
        """Draw health bar at given position"""
        x, y = position
        
        # Draw border
        pygame.draw.rect(surface, self.border_color, 
                        (x - self.border_width, y - self.border_width, 
                         self.width + self.border_width * 2, 
                         self.height + self.border_width * 2))
        
        # Draw background
        pygame.draw.rect(surface, self.background_color, 
                        (x, y, self.width, self.height))
        
        # Draw health
        health_width = int(self.width * health_system.get_health_percentage())
        if health_width > 0:
            # Change color based on health percentage
            color = self.low_health_color if health_system.get_health_percentage() < 0.3 else self.health_color
            pygame.draw.rect(surface, color, (x, y, health_width, self.height)) 