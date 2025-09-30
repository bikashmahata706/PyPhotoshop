# app/core.py - COMPLETE VERSION WITH MULTI-DOCUMENT SUPPORT
import os
import threading
from typing import Dict, Optional, Callable, TYPE_CHECKING, List
from PIL import Image, ImageTk
import numpy as np
from app.history import HistoryManager

if TYPE_CHECKING:
    from tools.base_tool import BaseTool
    from app.renderer import Renderer

class Document:
    def __init__(self, filename=None, image=None, width=800, height=600):
        self.filename = filename or "Untitled"
        self.layers = []
        self.active_layer_index = 0
        self.zoom_level = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.history_manager = HistoryManager()
        
        # Initialize with a background layer
        if image:
            bg_layer = Layer("Background")
            bg_layer.image = image
            self.layers.append(bg_layer)
        else:
            bg_layer = Layer("Background", width, height)
            bg_layer.image = Image.new("RGBA", (width, height), (255, 255, 255, 255))
            self.layers.append(bg_layer)

class AppState:
    def __init__(self, root):
        self.root = root
        self.canvas = None
        self.active_tool = None
        self.tools: Dict[str, 'BaseTool'] = {}
        self.worker_pool = None
        self.renderer = None
        
        # Multiple document support
        self.documents: List[Document] = []
        self.active_document_index = -1
        
        # Global properties (not document-specific)
        self.foreground_color = "black"
        self.background_color = "white"
    
    @property
    def active_document(self):
        if 0 <= self.active_document_index < len(self.documents):
            return self.documents[self.active_document_index]
        return None
    
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
    
    def create_new_document(self, width=800, height=600):
        doc = Document(width=width, height=height)
        self.documents.append(doc)
        self.active_document_index = len(self.documents) - 1
        return doc
    
    # In app/core.py - FIXED open_document method

    def open_document(self, filename, image):
        """Open document - FIXED VERSION"""
        try:
            print(f"📄 Creating document for: {filename}")
            
            # Create document with the image
            doc = Document(filename=filename, image=image)
            self.documents.append(doc)
            self.active_document_index = len(self.documents) - 1
            
            print(f"✅ Document created: {doc.filename}, Layers: {len(doc.layers)}")
            
            # **FIXED: Ensure the layer has a valid image**
            if doc.layers and doc.layers[0].image:
                print(f"✅ Layer image size: {doc.layers[0].image.size}")
            else:
                print("❌ No valid layer image")
                
            return doc
            
        except Exception as e:
            print(f"❌ Error creating document: {e}")
            raise
    
    def close_document(self, index):
        """Close document and update active index - FIXED VERSION"""
        if 0 <= index < len(self.documents):
            # Remove the document
            self.documents.pop(index)
            
            # Update active index properly
            if len(self.documents) == 0:
                self.active_document_index = -1
            elif self.active_document_index >= len(self.documents):
                self.active_document_index = len(self.documents) - 1
            # If we closed a tab before the active tab, adjust index
            elif index < self.active_document_index:
                self.active_document_index -= 1
            
            print(f"✅ Document {index} closed. New active index: {self.active_document_index}")
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