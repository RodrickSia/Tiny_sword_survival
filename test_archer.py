import pygame
import sys
import os

# Add src to path
sys.path.append('src')

from enemy_system import Enemy, Arrow
from player import Player
from health_system import HealthSystem

def test_archer():
    """Test archer enemy shooting arrows"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Archer Test")
    clock = pygame.time.Clock()
    
    # Create player
    player = Player(groups=pygame.sprite.Group(), pos=(400, 300))
    
    # Create archer enemy
    archer = Enemy('archer', (200, 200), player)
    
    # Test arrow creation
    print("Testing arrow creation...")
    arrow = Arrow((200, 200), (400, 300), 10)
    print(f"Arrow created: pos={arrow.rect.center}, damage={arrow.damage}")
    
    # Test archer shooting
    print("Testing archer shooting...")
    archer._shoot_arrow()
    print(f"Archer arrows: {len(archer.arrows)}")
    
    # Test arrow movement
    print("Testing arrow movement...")
    for i in range(10):
        arrow.update(0.016)  # 60 FPS
        print(f"Arrow position: {arrow.rect.center}")
    
    print("✅ Archer test completed successfully!")
    pygame.quit()

if __name__ == "__main__":
    test_archer() 