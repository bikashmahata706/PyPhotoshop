import os
import threading
from typing import Dict, Optional, Callable
from PIL import Image, ImageTk
import numpy as np
from tools.base_tool import BaseTool  # নতুন added line

class AppState:
    def __init__(self, root):
        self.root = root
        self.canvas = None
        self.active_tool = None
        self.tools: Dict[str, BaseTool] = {}  # এখন error show করবে না
        self.layers = []
        self.active_layer_index = -1
        self.zoom_level = 1.0
        self.history_manager = None
        self.worker_pool = None
        self.renderer = None
        
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