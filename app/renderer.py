# app/renderer.py - FIXED MULTIPLE IMAGE LOADING

import tkinter as tk
from PIL import Image, ImageTk
import time

class Renderer:
    def __init__(self, app_state, canvas):
        self.app = app_state
        self.canvas = canvas
        self.current_image = None
        self.photo_image = None
        self.original_image = None
        self.zoom_level = 1.0
        self.canvas_image_id = None
        
        # Multiple image support
        self.photo_references = []  # Keep all photo references
        self.image_history = []     # Track loaded images
        
        # Bind events
        self.canvas.bind('<Configure>', self._on_canvas_resize)
        
        print("✅ Multi-image renderer initialized")
    
    def load_image(self, image_path):
        """Load image with proper cleanup for multiple loads"""
        try:
            print(f"🖼️ Loading: {image_path}")
            
            # COMPLETE CLEANUP of previous image
            self._cleanup_previous_image()
            
            # Load new image
            new_image = Image.open(image_path).convert("RGBA")
            print(f"📏 New image size: {new_image.size}")
            
            # Store in history
            self.image_history.append(image_path)
            
            # Set as current images
            self.original_image = new_image
            self.app.original_image = new_image
            
            # Clear canvas completely
            self.canvas.delete("all")
            
            # Fit and display new image
            self._fit_and_display_image()
            
            print(f"✅ Image {len(self.image_history)} loaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Load error: {e}")
            return False
    
    def _cleanup_previous_image(self):
        """Complete cleanup of previous image resources"""
        print("🧹 Cleaning up previous image...")
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Reset canvas image reference
        self.canvas_image_id = None
        
        # Clear current images
        self.current_image = None
        self.original_image = None
        
        # Clear app state images
        if hasattr(self.app, 'current_image'):
            self.app.current_image = None
        if hasattr(self.app, 'original_image'):
            self.app.original_image = None
        
        # Force garbage collection of old photo references
        self.photo_references.clear()
        
        # Force canvas update
        self.canvas.update_idletasks()
        print("✅ Cleanup completed")
    
    def _on_canvas_resize(self, event):
        """Handle canvas resize"""
        if self.original_image:
            self._fit_and_display_image()
    
    def _fit_and_display_image(self):
        """Fit and display current image"""
        if not self.original_image:
            print("❌ No image to display")
            return
            
        # Get canvas dimensions with forced update
        self.canvas.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 10 or canvas_height <= 10:
            canvas_width, canvas_height = 800, 600
            print("⚠️ Using default canvas size")
        
        print(f"🎯 Canvas: {canvas_width}x{canvas_height}")
        
        # Calculate scaling
        margin = 0.04
        available_width = canvas_width * (1 - 2 * margin)
        available_height = canvas_height * (1 - 2 * margin)
        
        scale_x = available_width / self.original_image.width
        scale_y = available_height / self.original_image.height
        
        self.zoom_level = min(scale_x, scale_y, 1.0)
        
        # Calculate display size
        display_width = int(self.original_image.width * self.zoom_level)
        display_height = int(self.original_image.height * self.zoom_level)
        
        print(f"🔍 Zoom: {self.zoom_level:.3f}, Display: {display_width}x{display_height}")
        
        # Resize image
        self.current_image = self.original_image.resize(
            (display_width, display_height), 
            Image.Resampling.LANCZOS
        )
        
        # Display the image
        self._display_image(display_width, display_height, canvas_width, canvas_height)
    
    def _display_image(self, disp_width, disp_height, canvas_width, canvas_height):
        """Display image with proper reference management"""
        try:
            # Create new PhotoImage
            new_photo = ImageTk.PhotoImage(self.current_image)
            
            # Store reference to prevent garbage collection
            self.photo_references.append(new_photo)
            self.photo_image = new_photo
            
            # Keep only last 3 references to prevent memory leak
            if len(self.photo_references) > 3:
                self.photo_references.pop(0)
            
            # Calculate center position
            x = (canvas_width - disp_width) // 2
            y = (canvas_height - disp_height) // 2
            
            print(f"📍 Display at: ({x}, {y})")
            
            # Create new canvas image item (don't reuse old one)
            if self.canvas_image_id:
                self.canvas.delete(self.canvas_image_id)
                
            self.canvas_image_id = self.canvas.create_image(
                x, y, 
                anchor=tk.NW, 
                image=self.photo_image,
                tags=("current_image", f"image_{len(self.image_history)}")
            )
            
            # Update app state
            self.app.current_image = self.current_image
            self.app.original_image = self.original_image
            
            # Force canvas update
            self.canvas.update_idletasks()
            
            print("✅ Image displayed on canvas")
            
        except Exception as e:
            print(f"❌ Display error: {e}")
    
    def render(self, force=False):
        """Render current image"""
        if self.original_image:
            self._fit_and_display_image()
    
    def fit_to_screen(self):
        """Fit to screen"""
        self._fit_and_display_image()
    
    # Utility methods for image management
    def get_loaded_images_count(self):
        """Get count of loaded images"""
        return len(self.image_history)
    
    def get_current_image_info(self):
        """Get current image information"""
        if self.original_image:
            return {
                'size': self.original_image.size,
                'mode': self.original_image.mode,
                'zoom': self.zoom_level
            }
        return None