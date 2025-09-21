class BaseTool:
    def __init__(self, app):
        self.app = app
        
    def on_activate(self):
        """Called when the tool is activated"""
        pass
        
    def on_deactivate(self):
        """Called when the tool is deactivated"""
        pass
        
    def on_mouse_down(self, x, y, modifiers):
        """Handle mouse button down event"""
        pass
        
    def on_mouse_move(self, x, y, modifiers):
        """Handle mouse movement"""
        pass
        
    def on_mouse_up(self, x, y, modifiers):
        """Handle mouse button release"""
        pass
        
    def render_preview(self, draw, zoom):
        """Render tool preview on the canvas"""
        pass
        
    def commit(self):
        """Apply permanent changes to the image"""
        pass
        
    def get_affected_bbox(self):
        """
        Return the bounding box of affected area
        Returns: (x1, y1, x2, y2) or None for full image
        """
        return None