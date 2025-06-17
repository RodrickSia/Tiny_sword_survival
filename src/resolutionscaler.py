# resolutionscaler.py
import pygame
import os
import platform

class ResolutionScalerFullScreenStretch:
    def __init__(self, logic_width, logic_height):
        self.logic_width = logic_width
        self.logic_height = logic_height

        # Detect platform
        self.platform = self._detect_platform()
        
        # Get display info
        display_info = pygame.display.Info()
        self.screen_width = display_info.current_w
        self.screen_height = display_info.current_h

        # Platform specific screen handling
        self._handle_platform_screen()

        # Calculate scaling factors
        self.scale_x = self.screen_width / self.logic_width
        self.scale_y = self.screen_height / self.logic_height

        # Set up the display mode based on platform
        self._setup_display_mode()

        pygame.display.set_caption("Full Screen Game")

        # Create the logic surface with original game dimensions
        self.logic_surface = pygame.Surface((self.logic_width, self.logic_height))

        self.display_surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    def _detect_platform(self):
        """Detect the current platform"""
        system = platform.system().lower()
        if 'ANDROID_DATA' in os.environ:
            return 'android'
        elif system == 'darwin':  # macOS or iOS
            return 'ios' if 'iOS' in platform.platform() else 'macos'
        elif system == 'linux':
            return 'ubuntu' if 'ubuntu' in platform.platform().lower() else 'linux'
        return system

    def _handle_platform_screen(self):
        """Handle platform specific screen settings"""
        if self.platform == 'android':
            # Force landscape mode on Android
            if self.screen_height > self.screen_width:
                self.screen_width, self.screen_height = self.screen_height, self.screen_width
        elif self.platform == 'ios':
            # Handle iOS screen scaling and notch
            self.screen_width = int(self.screen_width * 0.95)  # Account for notch
            self.screen_height = int(self.screen_height * 0.95)
        elif self.platform == 'ubuntu':
            # Handle Ubuntu's display scaling
            try:
                # Try to get Ubuntu's display scaling factor
                import gi
                gi.require_version('Gdk', '3.0')
                from gi.repository import Gdk
                display = Gdk.Display.get_default()
                monitor = display.get_primary_monitor()
                scale_factor = monitor.get_scale_factor()
                self.screen_width = int(self.screen_width / scale_factor)
                self.screen_height = int(self.screen_height / scale_factor)
            except:
                pass  # Fallback to default if can't get scaling factor

    def _setup_display_mode(self):
        """Setup display mode based on platform"""
        flags = pygame.FULLSCREEN
        
        if self.platform == 'android':
            flags |= pygame.SCALED
        elif self.platform == 'ios':
            flags |= pygame.SCALED | pygame.HWSURFACE
        elif self.platform == 'ubuntu':
            flags |= pygame.SCALED | pygame.HWSURFACE | pygame.DOUBLEBUF

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), flags)

    def begin_frame(self):
        self.logic_surface.fill((0, 0, 0))
        return self.logic_surface

    def end_frame(self):
        try:
            if self.platform in ['android', 'ios']:
                # Use smoothscale for mobile platforms
                scaled = pygame.transform.smoothscale(self.logic_surface, 
                                                    (self.screen_width, self.screen_height))
            else:
                # Use regular scale for desktop platforms
                scaled = pygame.transform.scale(self.logic_surface, 
                                             (self.screen_width, self.screen_height))
            
            self.screen.blit(scaled, (0, 0))
            pygame.display.flip()
        except pygame.error as e:
            print(f"Scaling error: {e}")
            # Fallback to direct blit if scaling fails
            self.screen.blit(self.logic_surface, (0, 0))
            pygame.display.flip()

    def get_logic_surface(self):
        return self.logic_surface

    def get_screen_size(self):
        return (self.screen_width, self.screen_height)

    def get_scale_factors(self):
        return (self.scale_x, self.scale_y)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()
            
            # Handle platform specific keys
            if self.platform == 'android' and event.key == pygame.K_AC_BACK:
                pygame.quit()
                exit()
            elif self.platform == 'ios' and event.key == pygame.K_MENU:
                # Handle iOS menu button
                pass

    def screen_to_logic(self, pos):
        """Chuyển đổi tọa độ từ màn hình thật về logic surface"""
        screen_w, screen_h = self.display_surface.get_size()
        logic_x = int(pos[0] * self.logic_width / screen_w)
        logic_y = int(pos[1] * self.logic_height / screen_h)
        return (logic_x, logic_y)
