import pygame
import os
from typing import Dict, Optional

class AudioSystem:
    def __init__(self):
        pygame.mixer.init()
        
        # Audio settings
        self.sfx_volume = 0.7
        self.music_volume = 0.5
        self.sound_enabled = True
        self.music_enabled = True
        
        # Sound effects dictionary
        self.sounds = {}
        
        # Background music
        self.current_music = None
        
        # Initialize sounds
        self._load_sounds()
        
    def _load_sounds(self):
        """Load all sound effects"""
        # Create sounds directory if it doesn't exist
        sounds_dir = "assets/sounds"
        if not os.path.exists(sounds_dir):
            os.makedirs(sounds_dir)
            print(f"Created sounds directory: {sounds_dir}")
            return
            
        # Load sound effects
        sound_files = {
            'player_attack': 'attack.wav',
            'player_hurt': 'hurt.wav',
            'enemy_death': 'enemy_death.wav',
            'powerup_pickup': 'powerup.wav',
            'wave_start': 'wave_start.wav',
            'wave_complete': 'wave_complete.wav',
            'game_over': 'game_over.wav',
            'menu_select': 'menu_select.wav',
            'menu_confirm': 'menu_confirm.wav',
            'footstep': 'footstep.wav',
            'sword_swing': 'sword_swing.wav',
            'enemy_hit': 'enemy_hit.wav'
        }
        
        for sound_name, filename in sound_files.items():
            filepath = os.path.join(sounds_dir, filename)
            if os.path.exists(filepath):
                try:
                    self.sounds[sound_name] = pygame.mixer.Sound(filepath)
                    self.sounds[sound_name].set_volume(self.sfx_volume)
                except:
                    print(f"Failed to load sound: {filepath}")
            else:
                # Create placeholder sound
                self._create_placeholder_sound(sound_name)
                
    def _create_placeholder_sound(self, sound_name: str):
        """Create a placeholder sound effect"""
        try:
            # Try to use numpy for better sound generation
            import numpy as np
            
            # Generate a simple beep sound
            sample_rate = 44100
            duration = 0.1  # 100ms
            
            if sound_name in ['player_attack', 'sword_swing']:
                frequency = 800  # Higher pitch for attacks
            elif sound_name in ['player_hurt', 'enemy_hit']:
                frequency = 200  # Lower pitch for hits
            elif sound_name in ['powerup_pickup', 'menu_select']:
                frequency = 600  # Medium pitch for pickups
            elif sound_name in ['wave_start', 'wave_complete']:
                frequency = 400  # Medium-low pitch for events
            else:
                frequency = 500  # Default pitch
                
            # Generate sine wave
            t = np.linspace(0, duration, int(sample_rate * duration))
            wave = np.sin(2 * np.pi * frequency * t)
            
            # Convert to 16-bit PCM - make it stereo (2D array)
            wave = (wave * 32767).astype(np.int16)
            if len(wave.shape) == 1:
                wave = np.stack([wave, wave], axis=-1)  # Make stereo
            
            # Create pygame sound
            sound = pygame.sndarray.make_sound(wave)
            self.sounds[sound_name] = sound
            self.sounds[sound_name].set_volume(self.sfx_volume)
            
        except ImportError:
            # Fallback: create a simple silent sound
            print(f"numpy not available, creating silent placeholder for {sound_name}")
            # Create a minimal silent sound
            silent_data = bytes([0] * 4410)  # 0.1 seconds of silence at 44.1kHz
            try:
                sound = pygame.mixer.Sound(buffer=silent_data)
                self.sounds[sound_name] = sound
                self.sounds[sound_name].set_volume(0)  # Make it silent
            except:
                # If even that fails, just skip this sound
                print(f"Could not create placeholder sound for {sound_name}")
        except Exception as e:
            # Handle any other errors in sound creation
            print(f"Error creating sound for {sound_name}: {e}")
            # Create a silent placeholder
            try:
                silent_data = bytes([0] * 4410)
                sound = pygame.mixer.Sound(buffer=silent_data)
                self.sounds[sound_name] = sound
                self.sounds[sound_name].set_volume(0)
            except:
                print(f"Could not create placeholder sound for {sound_name}")
        
    def play_sound(self, sound_name: str, volume: Optional[float] = None):
        """Play a sound effect"""
        if not self.sound_enabled or sound_name not in self.sounds:
            return
            
        sound = self.sounds[sound_name]
        if volume is not None:
            original_volume = sound.get_volume()
            sound.set_volume(volume)
            sound.play()
            sound.set_volume(original_volume)
        else:
            sound.play()
            
    def play_music(self, music_file: str, loop: bool = True):
        """Play background music"""
        if not self.music_enabled:
            return
            
        music_path = os.path.join("assets", "sounds", music_file)
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1 if loop else 0)
                self.current_music = music_file
            except:
                print(f"Failed to load music: {music_path}")
                
    def stop_music(self):
        """Stop background music"""
        pygame.mixer.music.stop()
        self.current_music = None
        
    def pause_music(self):
        """Pause background music"""
        pygame.mixer.music.pause()
        
    def unpause_music(self):
        """Unpause background music"""
        pygame.mixer.music.unpause()
        
    def set_sfx_volume(self, volume: float):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)
            
    def set_music_volume(self, volume: float):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
        
    def toggle_sound(self):
        """Toggle sound effects on/off"""
        self.sound_enabled = not self.sound_enabled
        
    def toggle_music(self):
        """Toggle music on/off"""
        self.music_enabled = not self.music_enabled
        if not self.music_enabled:
            self.stop_music()
        elif self.current_music:
            self.play_music(self.current_music)
            
    def get_sfx_volume(self) -> float:
        """Get current SFX volume"""
        return self.sfx_volume
        
    def get_music_volume(self) -> float:
        """Get current music volume"""
        return self.music_volume
        
    def is_sound_enabled(self) -> bool:
        """Check if sound is enabled"""
        return self.sound_enabled
        
    def is_music_enabled(self) -> bool:
        """Check if music is enabled"""
        return self.music_enabled 