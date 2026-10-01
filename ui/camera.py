"""
Camera system. Manages viewport following the player (old-school FF style).
"""


class CameraManager:
    """Manages camera viewport following player."""
    
    def __init__(self, viewport_width=800, viewport_height=600):
        """Initialize camera with viewport size."""
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.camera_x = 0.0  # World pixel coords (top-left of viewport)
        self.camera_y = 0.0
    
    def update(self, player_x, player_y, map_width, map_height, tile_size):
        """Update camera to center on player, respecting map bounds."""
        # Convert player tile coords to pixel coords
        player_pixel_x = player_x * tile_size
        player_pixel_y = player_y * tile_size
        
        # Center camera on player (player in middle of screen)
        self.camera_x = player_pixel_x - (self.viewport_width // 2) + (tile_size // 2)
        self.camera_y = player_pixel_y - (self.viewport_height // 2) + (tile_size // 2)
        
        # Clamp to map bounds
        map_pixel_width = map_width * tile_size
        map_pixel_height = map_height * tile_size
        
        self.camera_x = max(0, min(self.camera_x, map_pixel_width - self.viewport_width))
        self.camera_y = max(0, min(self.camera_y, map_pixel_height - self.viewport_height))
    
    def world_to_screen(self, world_x, world_y, tile_size):
        """Convert world tile coords to screen pixel coords."""
        screen_x = world_x * tile_size - self.camera_x
        screen_y = world_y * tile_size - self.camera_y
        return screen_x, screen_y
    
    def screen_to_world(self, screen_x, screen_y, tile_size):
        """Convert screen pixel coords to world tile coords."""
        world_x = int((screen_x + self.camera_x) / tile_size)
        world_y = int((screen_y + self.camera_y) / tile_size)
        return world_x, world_y
    
    def get_viewport_bounds(self):
        """Get camera bounds (left, top, right, bottom) in world pixels."""
        return (
            self.camera_x,
            self.camera_y,
            self.camera_x + self.viewport_width,
            self.camera_y + self.viewport_height
        )
