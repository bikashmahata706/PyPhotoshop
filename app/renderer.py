# app/renderer.py - COMPLETE FIXED VERSION WITH MULTI-DOCUMENT SUPPORT
import tkinter as tk
from PIL import Image, ImageTk

class Renderer:
    def __init__(self, app_state, canvas):
        self.app = app_state
        self.canvas = canvas
        self.current_image = None
        self.photo_image = None
        self.original_image = None
        self.zoom_level = 1.0
        self.canvas_image_id = None
        
        # Move Tool support
        self.offset_x = 0
        self.offset_y = 0
        self.panning_enabled = True
        
        # Multiple image support
        self.photo_references = []
        self.image_history = []
        
        # Bind events
        self.canvas.bind('<Configure>', self._on_canvas_resize)
        
        print("✅ Fixed renderer initialized")
    
    def load_image(self, image_path):
        """Load image with proper cleanup - DEPRECATED: Use app.open_document instead"""
        try:
            print(f"🖼️ Loading: {image_path}")
            
            # Cleanup previous image
            self._cleanup_previous_image()
            
            # Load new image
            new_image = Image.open(image_path).convert("RGBA")
            print(f"📏 New image size: {new_image.size}")
            
            # Create new document
            doc = self.app.open_document(image_path, new_image)
            
            # Store in both app state and renderer
            self.original_image = new_image
            
            # Store in history
            self.image_history.append(image_path)
            
            # Clear canvas and display
            self.canvas.delete("all")
            self._fit_and_display_image()
            
            print(f"✅ Image loaded successfully as new document")
            return True
            
        except Exception as e:
            print(f"❌ Load error: {e}")
            return False
    
    def _cleanup_previous_image(self):
        """Cleanup previous image resources"""
        self.canvas.delete("all")
        self.canvas_image_id = None
        self.current_image = None
        self.original_image = None
        
        self.photo_references.clear()
        self.canvas.update_idletasks()
    
    def _on_canvas_resize(self, event):
        """Handle canvas resize"""
        if self.app.active_document:
            self._fit_and_display_image()
        else:
            self._show_placeholder()
    
    def _show_placeholder(self):
        """Show placeholder when no document is open - FIXED VERSION"""
        # Clear canvas completely
        self.canvas.delete("all")
        
        # Force canvas update to get correct dimensions
        self.canvas.update_idletasks()
        
        # Get actual canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Use reasonable defaults if canvas is too small
        if canvas_width < 100 or canvas_height < 100:
            canvas_width, canvas_height = 800, 600
            # Configure canvas to minimum size
            self.canvas.config(width=canvas_width, height=canvas_height)
        
        print(f"🔄 Placeholder canvas size: {canvas_width}x{canvas_height}")
        
        # Create a simple placeholder text - PERFECTLY CENTERED
        placeholder_text = "No image open\n\nFile → Open to open an image\nFile → New to create new image"
        
        # Create text in the exact center
        self.canvas.create_text(
            canvas_width // 2, 
            canvas_height // 2, 
            text=placeholder_text, 
            fill="#666666", 
            font=("Arial", 14, "bold"),
            justify=tk.CENTER,
            anchor=tk.CENTER  # This ensures perfect centering
        )
        
        # Add a subtle border rectangle
        border_margin = 20
        self.canvas.create_rectangle(
            border_margin, 
            border_margin, 
            canvas_width - border_margin, 
            canvas_height - border_margin,
            outline="#444444",
            width=2,
            dash=(4, 4)
        )
    
    def _fit_and_display_image(self):
        """Fit and display current active document's image - FIXED VERSION"""
        # Clear canvas FIRST before displaying image
        self.canvas.delete("all")
        
        # Check if we have an active document
        if not self.app.active_document:
            self._show_placeholder()
            return
        
        # Get image from active document
        active_doc = self.app.active_document
        if not active_doc.layers or not active_doc.layers[0].image:
            self._show_placeholder()
            return
        
        display_image = active_doc.layers[0].image
        self.original_image = display_image
        
        print(f"🔄 Displaying image: {display_image.size}")
        
        # Get canvas dimensions
        self.canvas.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 10 or canvas_height <= 10:
            canvas_width, canvas_height = 800, 600
        
        # Calculate scaling with margin
        margin = 40  # Increased margin for better appearance
        available_width = max(100, canvas_width - 2 * margin)
        available_height = max(100, canvas_height - 2 * margin)
        
        scale_x = available_width / display_image.width
        scale_y = available_height / display_image.height
        
        self.zoom_level = min(scale_x, scale_y, 1.0)
        
        # Calculate display size
        display_width = int(display_image.width * self.zoom_level)
        display_height = int(display_image.height * self.zoom_level)
        
        print(f"🔄 Display size: {display_width}x{display_height}")
        
        # Resize image
        self.current_image = display_image.resize(
            (display_width, display_height), 
            Image.Resampling.LANCZOS
        )
        
        # Display the image
        self._display_image(display_width, display_height, canvas_width, canvas_height)
    
    def _display_image(self, disp_width, disp_height, canvas_width, canvas_height):
        """Display image on canvas - FIXED VERSION"""
        try:
            # Clear any existing image first
            if self.canvas_image_id:
                self.canvas.delete(self.canvas_image_id)
                self.canvas_image_id = None
            
            # Create new PhotoImage
            new_photo = ImageTk.PhotoImage(self.current_image)
            
            # Store reference
            self.photo_references.append(new_photo)
            self.photo_image = new_photo
            
            # Keep only last 3 references
            if len(self.photo_references) > 3:
                self.photo_references.pop(0)
            
            # Calculate center position
            x = (canvas_width - disp_width) // 2
            y = (canvas_height - disp_height) // 2
            
            print(f"🔄 Image position: ({x}, {y})")
            
            # Create image on canvas
            self.canvas_image_id = self.canvas.create_image(
                x, y, 
                anchor=tk.NW, 
                image=self.photo_image,
                tags=("current_image",)
            )
            
            # Force update to ensure image is displayed
            self.canvas.update_idletasks()
            
            print("✅ Image displayed successfully - placeholder should be gone")
            
        except Exception as e:
            print(f"❌ Display error: {e}")
            # If image display fails, show placeholder
            self._show_placeholder()
    
    def render(self, force=False):
        """Render current active document's image - FIXED VERSION"""
        print("🔄 Renderer.render() called")
        
        # Clear canvas first to remove any existing content including placeholder
        self.canvas.delete("all")
        
        # Check if we have an active document
        if not self.app.active_document:
            print("❌ No active document to render")
            self._show_placeholder()
            return
        
        active_doc = self.app.active_document
        if not active_doc.layers or not active_doc.layers[0].image:
            print("❌ No image in active document")
            self._show_placeholder()
            return
        
        # Use active document's image
        self.original_image = active_doc.layers[0].image
        
        print(f"✅ Rendering active document: {active_doc.filename}")
        self._fit_and_display_image()
        self.canvas.update_idletasks()
    
    def fit_to_screen(self):
        """Fit to screen"""
        if self.app.active_document:
            self._fit_and_display_image()
        else:
            self._show_placeholder()
    
    # Zoom methods for move tool
    def zoom_in(self, x, y):
        if self.app.active_document:
            active_doc = self.app.active_document
            active_doc.zoom_level *= 1.2
            self.render()
    
    def zoom_out(self, x, y):
        if self.app.active_document:
            active_doc = self.app.active_document
            active_doc.zoom_level = max(0.1, active_doc.zoom_level / 1.2)
            self.render()
    
    def pan(self, dx, dy):
        if self.panning_enabled and self.app.active_document:
            active_doc = self.app.active_document
            active_doc.offset_x += dx
            active_doc.offset_y += dy
            self.render()
    
    def create_new_image(self, width, height):
        """Create a new blank image/document"""
        doc = self.app.create_new_document(width, height)
        self.render(force=True)
        return True