from tools.base_tool import BaseTool

class MoveTool(BaseTool):
    def __init__(self, app):
        super().__init__(app)
        self.start_x = 0
        self.start_y = 0
        self.is_dragging = False
        self.last_x = 0
        self.last_y = 0
    
    def on_activate(self):
        print("Move tool activated")
        if self.app.canvas:
            self.app.canvas.config(cursor="fleur")
    
    def on_deactivate(self):
        print("Move tool deactivated")
        if self.app.canvas:
            self.app.canvas.config(cursor="")
    
    def on_mouse_down(self, x, y, modifiers):
        self.start_x = x
        self.start_y = y
        self.last_x = x
        self.last_y = y
        self.is_dragging = True
    
    def on_mouse_move(self, x, y, modifiers):
        if self.is_dragging:
            dx = x - self.last_x
            dy = y - self.last_y
            self.last_x = x
            self.last_y = y
            
            # Scroll the canvas
            self.app.canvas.xview_scroll(-dx, "pixels")
            self.app.canvas.yview_scroll(-dy, "pixels")
    
    def on_mouse_up(self, x, y, modifiers):
        self.is_dragging = False
    
    def on_mouse_wheel(self, event):
        # Zoom with Ctrl+Mouse wheel
        if event.state & 0x4:  # Ctrl key pressed
            zoom_factor = 1.1 if event.delta > 0 else 0.9
            self.app.zoom_level *= zoom_factor
            print(f"Zoom level: {self.app.zoom_level:.2f}")
    
    def get_context_menu(self):
        # Context menu items for the move tool
        return [
            ("Auto-Select", lambda: print("Auto-Select toggled")),
            ("Show Transform Controls", lambda: print("Transform Controls toggled")),
            ("---", None),
            ("Free Transform", lambda: print("Free Transform activated")),
            ("---", None),
            ("Align Left", lambda: print("Align Left")),
            ("Align Center", lambda: print("Align Center")),
            ("Align Right", lambda: print("Align Right")),
        ]

def make_tool(app):
    return MoveTool(app)