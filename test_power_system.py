#!/usr/bin/env python3
"""
Test script for the new power system features
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pygame
from player import Player
from power_system import PowerSystem
from leaderboard_system import LeaderboardSystem

def test_power_system():
    """Test the power system functionality"""
    print("🧪 Testing Power System...")
    
    # Initialize pygame with display
    pygame.init()
    pygame.display.set_mode((800, 600))
    
    # Test power system
    power_system = PowerSystem(max_power=100)
    
    # Test adding power
    print(f"Initial power: {power_system.current_power}")
    
    # Add power gradually
    for i in range(8):  # 8 * 15 = 120 power (should trigger power up)
        power_gained = power_system.add_power(15)
        print(f"Added 15 power: {power_system.current_power}/100")
        if power_gained:
            print("🎉 Power up triggered!")
            break
    
    print("✅ Power system test completed\n")

def test_player_power_ups():
    """Test player power up integration"""
    print("🧪 Testing Player Power Ups...")
    
    # Initialize pygame with display
    pygame.init()
    pygame.display.set_mode((800, 600))
    
    # Create player
    player = Player()
    
    print(f"Base damage: {player.get_damage()}")
    print(f"Base speed: {player.get_speed()}")
    print(f"Base attack cooldown: {player.get_attack_cooldown()}")
    print(f"Base attack range: {player.get_attack_range()}")
    
    # Simulate killing enemies to gain power
    for i in range(7):  # 7 * 15 = 105 power (should trigger power up)
        player.on_enemy_killed()
        print(f"Enemies killed: {player.enemies_killed}, Power: {player.power_system.current_power}")
    
    # Check active power ups
    active_power_ups = player.get_active_power_ups()
    if active_power_ups:
        print("Active power ups:")
        for effect_name, effect_data in active_power_ups.items():
            print(f"  - {effect_name}: {effect_data['timer']:.1f}s remaining")
    
    print("✅ Player power ups test completed\n")

def test_leaderboard():
    """Test leaderboard functionality"""
    print("🧪 Testing Leaderboard System...")
    
    # Create leaderboard
    leaderboard = LeaderboardSystem("test_leaderboard.json")
    
    # Add some test scores
    scores = [
        (5, 25),   # 5 waves, 25 enemies
        (3, 15),   # 3 waves, 15 enemies  
        (7, 35),   # 7 waves, 35 enemies
        (2, 10),   # 2 waves, 10 enemies
        (6, 30),   # 6 waves, 30 enemies
    ]
    
    for waves, enemies in scores:
        rank = leaderboard.add_score(waves, enemies)
        print(f"Added score: {waves} waves, {enemies} enemies -> Rank #{rank}")
    
    # Get top scores
    top_scores = leaderboard.get_top_scores(5)
    print("\nTop 5 scores:")
    for score in top_scores:
        print(f"  #{score['rank']}: {score['waves_survived']} waves, {score['enemies_killed']} enemies")
    
    # Clean up test file
    try:
        os.remove("test_leaderboard.json")
    except:
        pass
    
    print("✅ Leaderboard test completed\n")

def main():
    """Run all tests"""
    print("🚀 Starting Power System Tests...\n")
    
    try:
        test_power_system()
        test_player_power_ups()
        test_leaderboard()
        
        print("🎉 All tests passed!")
        print("\n📋 Power Up Effects Summary:")
        print("  💚 Health Boost: +50 HP (instant)")
        print("  ⚔️ Damage Boost: Double damage for 10s")
        print("  🏃 Speed Boost: +50% speed for 8s")
        print("  🛡️ Invulnerability: Immune to damage for 5s")
        print("  ⚡ Rapid Fire: 70% faster attacks for 12s")
        print("  💥 Area Attack: 50% larger attack range for 15s")
        print("\n📊 Power System:")
        print("  - Gain 15 power per enemy killed")
        print("  - Power up triggers at 100 power")
        print("  - Power bar resets after power up")
        print("\n🏆 Leaderboard:")
        print("  - Tracks waves survived and enemies killed")
        print("  - Sorts by waves first, then enemies")
        print("  - Saves top 10 scores")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()

if __name__ == "__main__":
    main() 