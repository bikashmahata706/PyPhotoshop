# app/core.py - COMPLETE VERSION
import os
import threading
from typing import Dict, Optional, Callable, TYPE_CHECKING
from PIL import Image, ImageTk
import numpy as np

if TYPE_CHECKING:
    from tools.base_tool import BaseTool
    from app.renderer import Renderer

class AppState:
    def __init__(self, root):
        self.root = root
        self.canvas = None
        self.active_tool = None
        self.tools: Dict[str, 'BaseTool'] = {}
        self.layers = []
        self.active_layer_index = -1
        self.zoom_level = 1.0
        self.history_manager = None
        self.worker_pool = None
        self.renderer = None
        self.current_file = None
        self.foreground_color = "black"
        self.background_color = "white"
        
        self.current_image = None
        self.original_image = None
        self.photo_reference = None
    
    def setup_renderer(self, canvas):
        from app.renderer import Renderer
        self.renderer = Renderer(self, canvas)
    
    def set_canvas(self, canvas):
        self.canvas = canvas
        
    def register_tool(self, name: str, tool_factory: Callable):
        self.tools[name] = tool_factory(self)
        
    def set_active_tool(self, tool_name: str):
        if self.active_tool:
            self.active_tool.on_deactivate()
        if tool_name in self.tools:
            self.active_tool = self.tools[tool_name]
            self.active_tool.on_activate()
            return True
        return False

class ToolManager:
    def __init__(self, app_state: AppState):
        self.app = app_state
        
    def register_tool(self, name: str, tool_factory: Callable):
        self.app.register_tool(name, tool_factory)
        
    def switch_tool(self, tool_name: str):
        return self.app.set_active_tool(tool_name)

class Layer:
    def __init__(self, name, width=800, height=600):
        self.name = name
        self.image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        self.visible = True
        self.opacity = 1.0
        self.blend_mode = "normal"
        self.locked = False
        self.mask = None
        
    def get_thumbnail(self, size=(64, 64)):
        return self.image.resize(size, Image.Resampling.LANCZOS)