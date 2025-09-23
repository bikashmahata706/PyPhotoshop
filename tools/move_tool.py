# tools/move_tool.py - ENHANCED VERSION

from tools.base_tool import BaseTool

class MoveTool(BaseTool):
    def __init__(self, app):
        super().__init__(app)
        self.is_dragging = False
        self.last_x = 0
        self.last_y = 0
    
    def on_activate(self):
        print("🖱️ Move tool activated")
        if self.app.canvas:
            self.app.canvas.config(cursor="fleur")
    
    def on_mouse_down(self, x, y, modifiers):
        self.is_dragging = True
        self.last_x = x
        self.last_y = y
    
    def on_mouse_move(self, x, y, modifiers):
        if self.is_dragging and hasattr(self.app, 'renderer'):
            dx = x - self.last_x
            dy = y - self.last_y
            
            # Pan the canvas
            self.app.renderer.offset_x += dx
            self.app.renderer.offset_y += dy
            
            self.app.renderer.render(force=True)
            
            self.last_x = x
            self.last_y = y
    
    def on_mouse_up(self, x, y, modifiers):
        self.is_dragging = False
    
    def on_mouse_wheel(self, event):
        # Professional zoom with Ctrl+Mouse wheel
        if event.state & 0x4:  # Ctrl key
            if hasattr(self.app, 'renderer'):
                if event.delta > 0:
                    self.app.renderer.zoom_in(event.x, event.y)
                else:
                    self.app.renderer.zoom_out(event.x, event.y)

def make_tool(app):
    return MoveTool(app)