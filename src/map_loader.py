import pygame
import xml.etree.ElementTree as ET
import os
import base64
import zlib
import struct
import pytmx
class MapLoader:
    def __init__(self, tmx_path):
        self.tmx_path = tmx_path
        self.map_data = pytmx.load_pygame(tmx_path)
        self.tilesets = {}
        self.layers = []
        self.collision_sprites = []
        self.animated_tiles = []
        self.tile_animations = {}  # Store animation data for tiles
        self.collision_rects = []
        # Map properties
        self.map_width = self.map_data.width
        self.map_height = self.map_data.height
        self.tile_width = self.map_data.tilewidth
        self.tile_height = self.map_data.tileheight
        self.map_pixel_width = self.map_width * self.tile_width
        self.map_pixel_height = self.map_height * self.tile_height
        


    

    
    
    
    def load_map(self):
        """Load and parse the TMX file"""
        try:
            if not os.path.exists(self.tmx_path):
                print(f"TMX file not found: {self.tmx_path}")
                return False

            # Parse XML
            tree = ET.parse(self.tmx_path)
            self.map_data = tree.getroot()
            
            # Get map dimensions
            self.map_width = int(self.map_data.get('width'))
            self.map_height = int(self.map_data.get('height'))
            self.tile_width = int(self.map_data.get('tilewidth'))
            self.tile_height = int(self.map_data.get('tileheight'))
            self.map_pixel_width = self.map_width * self.tile_width
            self.map_pixel_height = self.map_height * self.tile_height
            
            print(f"Map loaded: {self.map_width}x{self.map_height} tiles, {self.tile_width}x{self.tile_height} tile size")
            
            # Load tilesets
            self._load_tilesets()
            
            return True
            
        except Exception as e:
            print(f"Error loading map: {e}")
            return False

    def _load_tilesets(self):
        """Load tileset images and data"""
        map_dir = os.path.dirname(self.tmx_path)
        
        for tileset in self.map_data.findall('tileset'):
            firstgid = int(tileset.get('firstgid'))
            
            # Handle external tileset files
            source = tileset.get('source')
            tileset_elem = tileset
            if source:
                tsx_path = os.path.join(map_dir, source)
                if os.path.exists(tsx_path):
                    tsx_tree = ET.parse(tsx_path)
                    tileset_elem = tsx_tree.getroot()
            
            # Get tileset properties
            tile_width = int(tileset_elem.get('tilewidth'))
            tile_height = int(tileset_elem.get('tileheight'))
            tile_count = int(tileset_elem.get('tilecount', 0))
            columns = int(tileset_elem.get('columns', 1))
            
            # Find image element
            image_elem = tileset_elem.find('image')
            if image_elem is not None:
                image_source = image_elem.get('source')
                image_width = int(image_elem.get('width'))
                image_height = int(image_elem.get('height'))
                
                # Load tileset image
                image_path = os.path.join(map_dir, image_source)
                if os.path.exists(image_path):
                    try:
                        tileset_image = pygame.image.load(image_path).convert_alpha()
                        
                        # Create tileset data
                        self.tilesets[firstgid] = {
                            'image': tileset_image,
                            'tile_width': tile_width,
                            'tile_height': tile_height,
                            'columns': columns,
                            'tile_count': tile_count,
                            'image_width': image_width,
                            'image_height': image_height
                        }
                        
                        # Load tile animations
                        self._load_tile_animations(tileset_elem, firstgid)
                        
                        print(f"Loaded tileset: {image_source} (GID: {firstgid}, Tiles: {tile_count})")
                        
                    except pygame.error as e:
                        print(f"Failed to load tileset image {image_path}: {e}")
                else:
                    print(f"Tileset image not found: {image_path}")

    def _load_tile_animations(self, tileset_elem, firstgid):
        """Load animation data for animated tiles"""
        for tile in tileset_elem.findall('tile'):
            tile_id = int(tile.get('id'))
            global_id = firstgid + tile_id
            
            animation = tile.find('animation')
            if animation is not None:
                frames = []
                for frame in animation.findall('frame'):
                    frame_tileid = int(frame.get('tileid'))
                    frame_duration = int(frame.get('duration'))  # Duration in milliseconds
                    frames.append({
                        'tileid': firstgid + frame_tileid,
                        'duration': frame_duration
                    })
                
                if frames:
                    self.tile_animations[global_id] = {
                        'frames': frames,
                        'current_frame': 0,
                        'current_time': 0,
                        'total_duration': sum(frame['duration'] for frame in frames)
                    }
                    print(f"Loaded animation for tile {global_id} with {len(frames)} frames")

    def setup_layers(self):
        """Process map layers"""
        if not self.map_data:
            return
        
        # Clear animated tiles list
        self.animated_tiles = []
        self.collision_sprites = pygame.sprite.Group()

        # Process tile layers
        for layer in self.map_data.findall('layer'):
            layer_name = layer.get('name')
            
            # Skip collision layer for now
                
            layer_width = int(layer.get('width'))
            layer_height = int(layer.get('height'))
            
            # Get layer data
            data_elem = layer.find('data')
            if data_elem is not None:
                encoding = data_elem.get('encoding')
                compression = data_elem.get('compression')
                
                # Parse tile data
                tile_data = self._parse_layer_data(data_elem, encoding, compression)
                
                if tile_data:
                    layer_info = {
                        'name': layer_name,
                        'width': layer_width,
                        'height': layer_height,
                        'data': tile_data,
                        'surface': None
                    }
                    
                    # Find animated tiles in this layer
                    self._find_animated_tiles(layer_info)
                    
                    # Pre-render layer to surface for better performance (static tiles only)
                    layer_info['surface'] = self._render_layer_to_surface(layer_info)
                    self.layers.append(layer_info)
                    
                    print(f"Processed layer: {layer_name} ({layer_width}x{layer_height})")

        # Process object layers (for collision)
        for objectgroup in self.map_data.findall('objectgroup'):
            group_name = objectgroup.get('name', '').lower()
            if group_name == 'collision' or 'collision' in group_name:
                for obj in objectgroup.findall('object'):
                    x = float(obj.get('x', 0))
                    y = float(obj.get('y', 0))
                    w = float(obj.get('width', 0))
                    h = float(obj.get('height', 0))

                    if w != None and h != None:
                        StaticObstacle((x, y), (w, h), [self.collision_sprites])
                    else:
                        print(f"⚠️ Bỏ qua object không hợp lệ: x={x}, y={y}, w={w}, h={h}")

                print(f"✔ Đã load {len(self.collision_sprites)} vật cản từ object layer.")
              

    def _find_animated_tiles(self, layer_info):
        """Find and store animated tile positions"""
        tile_data = layer_info['data']
        
        for y in range(layer_info['height']):
            for x in range(layer_info['width']):
                tile_index = y * layer_info['width'] + x
                if tile_index < len(tile_data):
                    gid = tile_data[tile_index]
                    
                    if gid > 0 and gid in self.tile_animations:
                        animated_tile = {
                            'gid': gid,
                            'x': x * self.tile_width,
                            'y': y * self.tile_height,
                            'layer': layer_info['name'],
                            'current_frame': 0,
                            'current_time': 0
                        }
                        self.animated_tiles.append(animated_tile)

    def _parse_layer_data(self, data_elem, encoding, compression):
        """Parse tile data from layer"""
        try:
            if encoding == 'base64':
                # Decode base64 data
                raw_data = base64.b64decode(data_elem.text.strip())
                
                # Decompress if needed
                if compression == 'zlib':
                    raw_data = zlib.decompress(raw_data)
                elif compression == 'gzip':
                    import gzip
                    raw_data = gzip.decompress(raw_data)
                
                # Convert to tile IDs (4 bytes per tile, little endian)
                tile_count = len(raw_data) // 4
                tile_data = []
                
                for i in range(tile_count):
                    tile_id = struct.unpack('<I', raw_data[i*4:(i+1)*4])[0]
                    # Remove flip flags (upper 3 bits)
                    tile_id = tile_id & 0x1FFFFFFF
                    tile_data.append(tile_id)
                
                return tile_data
                
            elif encoding == 'csv':
                # Parse CSV data
                csv_data = data_elem.text.strip()
                tile_data = [int(x.strip()) for x in csv_data.split(',') if x.strip()]
                return tile_data
                
            else:
                # Parse tile elements directly
                tiles = data_elem.findall('tile')
                tile_data = [int(tile.get('gid', 0)) for tile in tiles]
                return tile_data
                
        except Exception as e:
            print(f"Error parsing layer data: {e}")
            return None

    def _render_layer_to_surface(self, layer_info):
        """Pre-render a layer to a surface for better performance (static tiles only)"""
        surface = pygame.Surface((self.map_pixel_width, self.map_pixel_height), pygame.SRCALPHA)
        
        tile_data = layer_info['data']
        
        for y in range(layer_info['height']):
            for x in range(layer_info['width']):
                tile_index = y * layer_info['width'] + x
                if tile_index < len(tile_data):
                    gid = tile_data[tile_index]
                    
                    # Only render static tiles to the surface
                    if gid > 0 and gid not in self.tile_animations:
                        tile_image = self._get_tile_image(gid)
                        if tile_image:
                            pos_x = x * self.tile_width
                            pos_y = y * self.tile_height
                            surface.blit(tile_image, (pos_x, pos_y))
        
        return surface

    def _get_tile_image(self, gid):
        """Get tile image from GID"""
        if gid == 0:
            return None
        
        # Find the correct tileset
        tileset_data = None
        local_id = gid
        
        # Sort tilesets by firstgid in descending order
        sorted_tilesets = sorted(self.tilesets.items(), reverse=True)
        
        for firstgid, tileset in sorted_tilesets:
            if gid >= firstgid:
                tileset_data = tileset
                local_id = gid - firstgid
                break
        
        if not tileset_data:
            return None
        
        # Calculate tile position in tileset
        columns = tileset_data['columns']
        tile_x = (local_id % columns) * tileset_data['tile_width']
        tile_y = (local_id // columns) * tileset_data['tile_height']
        
        # Extract tile from tileset
        try:
            tile_rect = pygame.Rect(tile_x, tile_y, tileset_data['tile_width'], tileset_data['tile_height'])
            tile_surface = pygame.Surface((tileset_data['tile_width'], tileset_data['tile_height']), pygame.SRCALPHA)
            tile_surface.blit(tileset_data['image'], (0, 0), tile_rect)
            return tile_surface
        except:
            return None

    def draw_static_layers(self, screen, camera_x=0, camera_y=0):
        """Draw all pre-rendered layers to screen"""
        for layer in self.layers:
            if layer['surface']:
                screen.blit(layer['surface'], (-camera_x, -camera_y))

    def draw_animated_tiles(self, screen, camera_x=0, camera_y=0):
        """Draw animated tiles"""
        for animated_tile in self.animated_tiles:
            gid = animated_tile['gid']
            if gid in self.tile_animations:
                animation_data = self.tile_animations[gid]
                current_frame = animated_tile['current_frame']
                
                if current_frame < len(animation_data['frames']):
                    frame_gid = animation_data['frames'][current_frame]['tileid']
                    tile_image = self._get_tile_image(frame_gid)
                    
                    if tile_image:
                        screen_x = animated_tile['x'] - camera_x
                        screen_y = animated_tile['y'] - camera_y
                        screen.blit(tile_image, (screen_x, screen_y))

    def update_animations(self, dt):
        """Update animated tiles"""
        dt_ms = dt * 1000  # Convert to milliseconds
        
        for animated_tile in self.animated_tiles:
            gid = animated_tile['gid']
            if gid in self.tile_animations:
                animation_data = self.tile_animations[gid]
                animated_tile['current_time'] += dt_ms
                
                if len(animation_data['frames']) > 0:
                    current_frame = animated_tile['current_frame']
                    frame_duration = animation_data['frames'][current_frame]['duration']
                    
                    if animated_tile['current_time'] >= frame_duration:
                        animated_tile['current_time'] = 0
                        animated_tile['current_frame'] = (current_frame + 1) % len(animation_data['frames'])

    def get_map_size(self):
        """Get map size in pixels"""
        return self.map_pixel_width, self.map_pixel_height

    def get_tile_at(self, x, y, layer_name=None):
        """Get tile ID at world coordinates"""
        tile_x = x // self.tile_width
        tile_y = y // self.tile_height
        
        if layer_name:
            for layer in self.layers:
                if layer['name'] == layer_name:
                    if 0 <= tile_x < layer['width'] and 0 <= tile_y < layer['height']:
                        tile_index = tile_y * layer['width'] + tile_x
                        if tile_index < len(layer['data']):
                            return layer['data'][tile_index]
        
        return 0
    
class StaticObstacle(pygame.sprite.Sprite):
    def __init__(self, pos, size, groups):
        super().__init__(groups)
        self.image = pygame.Surface(size)
        self.image = pygame.Surface(size, pygame.SRCALPHA)  
        self.image.fill((255, 255, 0, 100))
        self.rect = self.image.get_rect(topleft=pos)
        self.old_rect = self.rect.copy()
