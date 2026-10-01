"""
Base screen class. Parent for all UI screens.
"""
from ui.renderer import Renderer


class BaseScreen:
    """Parent class for all game screens."""
    
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.renderer = Renderer()
    
    def handle_event(self, event):
        """Handle pygame events. Override in subclasses."""
        pass
    
    def update(self, dt):
        """Update screen state. Override in subclasses."""
        pass
    
    def render(self, screen):
        """Render screen. Override in subclasses."""
        pass
