#!/usr/bin/env python3
"""
Test script to verify all game features are working correctly
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def init_pygame():
    """Initialize pygame with a display for testing"""
    import pygame
    pygame.init()
    # Create a small display for testing
    pygame.display.set_mode((800, 600))
    return pygame

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        import pygame
        print("✓ Pygame imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import pygame: {e}")
        return False
    
    try:
        from health_system import HealthSystem, HealthBar
        print("✓ Health system imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import health system: {e}")
        return False
    
    try:
        from enemy_system import Enemy, WaveManager
        print("✓ Enemy system imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import enemy system: {e}")
        return False
    
    try:
        from powerup_system import PowerUp, PowerUpManager
        print("✓ Power-up system imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import power-up system: {e}")
        return False
    
    try:
        from audio_system import AudioSystem
        print("✓ Audio system imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import audio system: {e}")
        return False
    
    try:
        from ui_system import Menu, HUD, GameOverScreen
        print("✓ UI system imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import UI system: {e}")
        return False
    
    try:
        from player import Player
        print("✓ Player imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import player: {e}")
        return False
    
    return True

def test_health_system():
    """Test health system functionality"""
    print("\nTesting health system...")
    try:
        from health_system import HealthSystem, HealthBar
        # Test health system
        health = HealthSystem(100)
        print("Initial health:", health.current_health)
        assert health.current_health == 100
        assert health.max_health == 100
        assert health.is_alive() == True
        print("After creation: PASS")
        # Test taking damage
        result = health.take_damage(30)
        print("After taking 30 damage:", health.current_health, "Result:", result)
        assert result == True
        assert health.current_health == 70
        assert abs(health.get_health_percentage() - 0.7) < 1e-6
        print("After damage: PASS")
        # Test healing
        result = health.heal(20)
        print("After healing 20:", health.current_health, "Result:", result)
        assert result == True
        assert health.current_health == 90
        print("After heal: PASS")
        # Wait for invulnerability to expire
        health.update(2.0)
        # Test death
        health.take_damage(100)
        print("After lethal damage:", health.current_health)
        assert health.current_health == 0
        assert health.is_alive() == False
        print("After death: PASS")
        print("✓ Health system working correctly")
        return True
    except Exception as e:
        print(f"✗ Health system test failed: {e}")
        return False

def test_enemy_system():
    """Test enemy system functionality"""
    print("\nTesting enemy system...")
    
    try:
        pygame = init_pygame()
        
        from enemy_system import Enemy, WaveManager
        from player import Player
        
        # Create a dummy player for testing
        player = Player()
        
        # Test wave manager
        wave_manager = WaveManager(player)
        assert wave_manager.current_wave == 0
        assert wave_manager.get_enemy_count() == 0
        
        # Test starting a wave
        wave_manager.start_wave()
        assert wave_manager.current_wave == 1
        assert wave_manager.wave_in_progress == True
        
        print("✓ Enemy system working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Enemy system test failed: {e}")
        return False

def test_powerup_system():
    """Test power-up system functionality"""
    print("\nTesting power-up system...")
    
    try:
        pygame = init_pygame()
        
        from powerup_system import PowerUp, PowerUpManager
        from player import Player
        
        # Create a dummy player for testing
        player = Player()
        
        # Test power-up manager
        powerup_manager = PowerUpManager(player)
        assert len(powerup_manager.powerups) == 0
        assert len(powerup_manager.active_effects) == 0
        
        # Test applying power-up
        powerup_manager.apply_powerup('health')
        assert player.health_system.current_health == player.health_system.max_health
        
        print("✓ Power-up system working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Power-up system test failed: {e}")
        return False

def test_audio_system():
    """Test audio system functionality"""
    print("\nTesting audio system...")
    
    try:
        from audio_system import AudioSystem
        
        # Test audio system initialization
        audio = AudioSystem()
        assert audio.sfx_volume == 0.7
        assert audio.music_volume == 0.5
        assert audio.sound_enabled == True
        assert audio.music_enabled == True
        
        # Test volume controls
        audio.set_sfx_volume(0.5)
        assert audio.get_sfx_volume() == 0.5
        
        audio.set_music_volume(0.3)
        assert audio.get_music_volume() == 0.3
        
        print("✓ Audio system working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Audio system test failed: {e}")
        return False

def test_ui_system():
    """Test UI system functionality"""
    print("\nTesting UI system...")
    
    try:
        pygame = init_pygame()
        
        from ui_system import Menu, HUD, GameOverScreen
        from player import Player
        from enemy_system import WaveManager
        from powerup_system import PowerUpManager
        
        # Test menu creation
        menu = Menu("Test Menu", 400, 300)
        assert menu.title == "Test Menu"
        assert menu.width == 400
        assert menu.height == 300
        
        # Test HUD creation
        player = Player()
        wave_manager = WaveManager(player)
        powerup_manager = PowerUpManager(player)
        hud = HUD(player, wave_manager, powerup_manager)
        
        # Test game over screen
        game_over = GameOverScreen(5, lambda: None, lambda: None)
        
        print("✓ UI system working correctly")
        return True
        
    except Exception as e:
        print(f"✗ UI system test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Running feature tests for Tiny Sword Survival...\n")
    
    tests = [
        test_imports,
        test_health_system,
        test_enemy_system,
        test_powerup_system,
        test_audio_system,
        test_ui_system
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The game features are working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 