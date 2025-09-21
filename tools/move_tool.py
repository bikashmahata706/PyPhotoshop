from tools.base_tool import BaseTool

class MoveTool(BaseTool):
    def __init__(self, app):
        super().__init__(app)
        self.start_x = 0
        self.start_y = 0
        self.is_dragging = False
    
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
        self.is_dragging = True
    
    def on_mouse_move(self, x, y, modifiers):
        if self.is_dragging:
            dx = x - self.start_x
            dy = y - self.start_y
            self.start_x = x
            self.start_y = y
            
            # Scroll the canvas
            self.app.canvas.xview_scroll(-dx, "pixels")
            self.app.canvas.yview_scroll(-dy, "pixels")
    
    def on_mouse_up(self, x, y, modifiers):
        self.is_dragging = False

def make_tool(app):
    return MoveTool(app)