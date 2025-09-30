class BaseTool:
    def __init__(self, app):
        self.app = app

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    def on_mouse_down(self, x, y, modifiers):
        pass

    def on_mouse_move(self, x, y, modifiers):
        pass

    def on_mouse_up(self, x, y, modifiers):
        pass

    def render_preview(self, draw, zoom):
        pass

    def commit(self):
        pass

    def get_affected_bbox(self):
        return None