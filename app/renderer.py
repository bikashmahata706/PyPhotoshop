# app/renderer.py - COMPLETE FIXED VERSION

import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import numpy as np
from typing import List, Tuple, Optional
import time

class Renderer:
    def __init__(self, app_state, canvas):
        self.app = app_state
        self.canvas = canvas
        
        # Core rendering state
        self.current_image = None
        self.photo_image = None
        self.original_image = None
        self.zoom_level = 1.0
        self.canvas_image_id = None
        
        # Brush tool coordinates
        self.last_image_x = 0
        self.last_image_y = 0
        self.last_display_width = 0
        self.last_display_height = 0

        # **FIXED: Better state management**
        self.is_rendering = False
        self.last_document_hash = None
        
        # Performance optimizations
        self.photo_references = []
        self.pending_render = None
        
        # Layer compositing cache
        self.composite_cache = None
        self.cache_dirty = True
        self.last_composite_hash = None
        
        # Bind events
        self.canvas.bind('<Configure>', self._on_canvas_resize)
        
        print("✅ Fixed Renderer initialized - Images will display properly")

    def _on_canvas_resize(self, event):
        """Handle canvas resize"""
        if self.pending_render:
            self.canvas.after_cancel(self.pending_render)
        
        self.pending_render = self.canvas.after(100, self._delayed_resize)

    def _delayed_resize(self):
        """Delayed resize to avoid excessive redraws"""
        if self.app.active_document:
            self._fit_and_display_image()
        else:
            self._show_placeholder()
        self.pending_render = None

    def _show_placeholder(self):
        """Show placeholder when no document is open - FIXED"""
        try:
            self.canvas.delete("all")
            self.canvas.update_idletasks()
            
            canvas_width = max(400, self.canvas.winfo_width())
            canvas_height = max(300, self.canvas.winfo_height())
            
            # Create a more visible placeholder
            self.canvas.create_rectangle(0, 0, canvas_width, canvas_height, fill="#2d2d30", outline="")
            
            # Center text
            self.canvas.create_text(
                canvas_width // 2, 
                canvas_height // 2, 
                text="No Image Open\n\nFile → Open to open an image\nFile → New to create new image", 
                fill="#888888", 
                font=("Arial", 14, "bold"),
                justify=tk.CENTER,
                anchor=tk.CENTER
            )
            
            # Add a border
            self.canvas.create_rectangle(
                20, 20, canvas_width-20, canvas_height-20,
                outline="#444444", width=2, dash=(4, 4)
            )
            
            self.canvas.update_idletasks()
            
        except Exception as e:
            print(f"❌ Placeholder error: {e}")

    def composite_all_layers(self) -> Optional[Image.Image]:
        """Composite all visible layers - FIXED"""
        if not self.app.active_document or not self.app.active_document.layers:
            return None
            
        active_doc = self.app.active_document
        visible_layers = [layer for layer in active_doc.layers if layer.visible]
        
        if not visible_layers:
            return None
            
        # **FIXED: Check if we have valid images**
        for layer in visible_layers:
            if not hasattr(layer, 'image') or layer.image is None:
                return None
        
        current_hash = self._get_layers_hash(visible_layers)
        if (not self.cache_dirty and self.composite_cache and 
            self.last_composite_hash == current_hash):
            return self.composite_cache
            
        try:
            # Start with bottom layer
            composite = visible_layers[0].image.copy()
            
            # Blend other layers on top
            for layer in visible_layers[1:]:
                if layer.opacity > 0 and hasattr(layer, 'image') and layer.image:
                    composite = self._blend_layers(composite, layer)
            
            # Update cache
            self.composite_cache = composite
            self.last_composite_hash = current_hash
            self.cache_dirty = False
            
            return composite
            
        except Exception as e:
            print(f"❌ Composite error: {e}")
            return None

    def _get_layers_hash(self, layers: List) -> str:
        """Generate hash for layers state"""
        hash_parts = []
        for layer in layers:
            if hasattr(layer, 'image') and layer.image:
                hash_parts.append(f"{layer.name}_{layer.visible}_{layer.opacity}_{layer.image.size}")
            else:
                hash_parts.append(f"{layer.name}_{layer.visible}_{layer.opacity}_noimage")
        return "_".join(hash_parts)

    def _blend_layers(self, base: Image.Image, layer) -> Image.Image:
        """Simple layer blending"""
        if layer.opacity >= 1.0 and layer.blend_mode == "normal":
            return Image.alpha_composite(base, layer.image)
            
        # Apply opacity
        if layer.opacity < 1.0:
            overlay = layer.image.copy()
            # Simple opacity implementation
            if overlay.mode == 'RGBA':
                r, g, b, a = overlay.split()
                a = a.point(lambda x: x * layer.opacity)
                overlay.putalpha(a)
            return Image.alpha_composite(base, overlay)
        else:
            return Image.alpha_composite(base, layer.image)

    def _fit_and_display_image(self):
        """Fit and display current active document's image - COMPLETELY FIXED"""
        print("🔄 _fit_and_display_image called")
        
        # Clear canvas first
        self.canvas.delete("all")
        
        if not self.app.active_document:
            print("❌ No active document")
            self._show_placeholder()
            return
        
        active_doc = self.app.active_document
        if not active_doc.layers:
            print("❌ No layers in document")
            self._show_placeholder()
            return
        
        # **FIXED: Get composite image**
        display_image = self.composite_all_layers()
        if not display_image:
            print("❌ No composite image")
            self._show_placeholder()
            return
            
        print(f"✅ Display image size: {display_image.size}")
        self.original_image = display_image
        
        # Get canvas dimensions - FIXED with better error handling
        self.canvas.update_idletasks()
        try:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 10 or canvas_height <= 10:
                canvas_width, canvas_height = 800, 600
                self.canvas.config(width=canvas_width, height=canvas_height)
        except:
            canvas_width, canvas_height = 800, 600
        
        print(f"✅ Canvas size: {canvas_width}x{canvas_height}")
        
        # Calculate scaling with margin
        margin = 40
        available_width = max(100, canvas_width - 2 * margin)
        available_height = max(100, canvas_height - 2 * margin)
        
        scale_x = available_width / display_image.width
        scale_y = available_height / display_image.height
        
        self.zoom_level = min(scale_x, scale_y, 1.0)
        
        # Calculate display size
        display_width = int(display_image.width * self.zoom_level)
        display_height = int(display_image.height * self.zoom_level)
        
        print(f"✅ Display size: {display_width}x{display_height}, Zoom: {self.zoom_level}")
        
        # Resize image
        try:
            self.current_image = display_image.resize(
                (display_width, display_height), 
                Image.Resampling.LANCZOS
            )
            print("✅ Image resized successfully")
        except Exception as e:
            print(f"❌ Image resize error: {e}")
            self._show_placeholder()
            return
        
        self._display_image(display_width, display_height, canvas_width, canvas_height)

    def _display_image(self, disp_width: int, disp_height: int, canvas_width: int, canvas_height: int):
        """Display image on canvas - COMPLETELY FIXED"""
        try:
            # Clear any existing image first
            if self.canvas_image_id:
                self.canvas.delete(self.canvas_image_id)
            
            # Create new PhotoImage
            print(f"🔄 Creating PhotoImage: {disp_width}x{disp_height}")
            new_photo = ImageTk.PhotoImage(self.current_image)
            
            # **FIXED: Proper reference management**
            self.photo_references = [new_photo]  # Keep only current reference
            self.photo_image = new_photo
            
            # Calculate center position
            x = (canvas_width - disp_width) // 2
            y = (canvas_height - disp_height) // 2

            # Store coordinates for tools
            self.last_image_x = x
            self.last_image_y = y
            self.last_display_width = disp_width
            self.last_display_height = disp_height
            
            print(f"✅ Image position: ({x}, {y})")
            
            # Create image on canvas
            self.canvas_image_id = self.canvas.create_image(
                x, y, 
                anchor=tk.NW, 
                image=self.photo_image,
                tags=("current_image",)
            )
            
            # **FIXED: Force multiple updates to ensure display**
            self.canvas.update_idletasks()
            self.canvas.update()
            
            print("✅ Image displayed successfully")
            
        except Exception as e:
            print(f"❌ Display error: {e}")
            import traceback
            traceback.print_exc()
            # If image display fails, show placeholder
            self._show_placeholder()

    def render(self, force: bool = False):
        """Render current active document - FIXED"""
        print(f"🎨 RENDER CALLED - force: {force}")
        
        if self.is_rendering:
            return
            
        self.is_rendering = True
        
        try:
            # Clear canvas first
            self.canvas.delete("all")
            
            if not self.app.active_document:
                print("❌ No active document to render")
                self._show_placeholder()
                return
            
            active_doc = self.app.active_document
            if not active_doc.layers:
                print("❌ No layers in active document")
                self._show_placeholder()
                return
            
            # **FIXED: Force fresh composite**
            self.cache_dirty = True
            self.composite_cache = None
            self.last_composite_hash = None
            
            print(f"✅ Rendering active document: {active_doc.filename}")
            self._fit_and_display_image()
            
            # **FIXED: Extra force updates**
            self.canvas.update_idletasks()
            self.canvas.update()
            
        except Exception as e:
            print(f"❌ Render error: {e}")
            self._show_placeholder()
        finally:
            self.is_rendering = False

    def render_partial(self, bbox: Tuple[int, int, int, int]):
        """Partial rendering for performance"""
        if not self.app.active_document or not self.photo_image:
            return
            
        try:
            # Convert image coordinates to canvas coordinates
            x1, y1, x2, y2 = bbox
            canvas_x1 = self.last_image_x + int(x1 * self.zoom_level)
            canvas_y1 = self.last_image_y + int(y1 * self.zoom_level)
            canvas_x2 = self.last_image_x + int(x2 * self.zoom_level)
            canvas_y2 = self.last_image_y + int(y2 * self.zoom_level)
            
            # Get the affected region from composite
            composite = self.composite_all_layers()
            if not composite:
                return
                
            # Crop and resize the affected region
            region = composite.crop(bbox)
            display_region = region.resize(
                (canvas_x2 - canvas_x1, canvas_y2 - canvas_y1),
                Image.Resampling.LANCZOS
            )
            
            # Create PhotoImage for the region
            region_photo = ImageTk.PhotoImage(display_region)
            self.photo_references.append(region_photo)
            
            # Draw rectangle over the old region and place new one
            self.canvas.delete("partial_update")
            self.canvas.create_image(
                canvas_x1, canvas_y1,
                anchor=tk.NW, image=region_photo, tags="partial_update"
            )
            
            # Cleanup references
            if len(self.photo_references) > 3:
                self.photo_references = self.photo_references[-3:]
                
        except Exception as e:
            print(f"❌ Partial render error: {e}")
            # Fallback to full render
            self.render(force=True)

    def mark_cache_dirty(self):
        """Mark cache as dirty"""
        print("🔄 Cache marked as dirty")
        self.cache_dirty = True
        self.composite_cache = None
        self.last_composite_hash = None

    def temporary_display(self, image: Image.Image):
        """Temporarily display an image for brush preview"""
        try:
            self.canvas.update_idletasks()
            canvas_width = max(400, self.canvas.winfo_width())
            canvas_height = max(300, self.canvas.winfo_height())
            
            # Calculate display size
            margin = 40
            available_width = max(100, canvas_width - 2 * margin)
            available_height = max(100, canvas_height - 2 * margin)
            
            scale_x = available_width / image.width
            scale_y = available_height / image.height
            zoom_level = min(scale_x, scale_y, 1.0)
            
            display_width = int(image.width * zoom_level)
            display_height = int(image.height * zoom_level)
            
            # Resize image
            display_image = image.resize(
                (display_width, display_height), 
                Image.Resampling.LANCZOS
            )
            
            # Create PhotoImage
            photo = ImageTk.PhotoImage(display_image)
            self.photo_references.append(photo)
            
            # Keep only last 3 references
            if len(self.photo_references) > 3:
                self.photo_references.pop(0)
            
            # Calculate center position
            x = (canvas_width - display_width) // 2
            y = (canvas_height - display_height) // 2
            
            # Store coordinates
            self.last_image_x = x
            self.last_image_y = y
            self.last_display_width = display_width
            self.last_display_height = display_height
            self.zoom_level = zoom_level
            
            # Clear and display
            self.canvas.delete("all")
            self.canvas.create_image(x, y, anchor=tk.NW, image=photo)
            
            # Force updates
            self.canvas.update_idletasks()
            self.canvas.update()
            
        except Exception as e:
            print(f"❌ Temporary display error: {e}")

    def load_image(self, image_path: str) -> bool:
        """**NEW: Direct image loading method**"""
        try:
            print(f"🖼️ Loading image: {image_path}")
            
            # Load image using PIL
            new_image = Image.open(image_path).convert("RGBA")
            print(f"📏 Loaded image size: {new_image.size}")
            
            # Create new document
            doc = self.app.open_document(image_path, new_image)
            
            # Force render
            self.render(force=True)
            
            print(f"✅ Image loaded and displayed: {image_path}")
            return True
            
        except Exception as e:
            print(f"❌ Image loading error: {e}")
            return False

    # Zoom and pan methods
    def zoom_in(self, x: int, y: int):
        if self.app.active_document:
            active_doc = self.app.active_document
            active_doc.zoom_level = min(8.0, active_doc.zoom_level * 1.2)
            self.mark_cache_dirty()
            self.render()

    def zoom_out(self, x: int, y: int):
        if self.app.active_document:
            active_doc = self.app.active_document
            active_doc.zoom_level = max(0.1, active_doc.zoom_level / 1.2)
            self.mark_cache_dirty()
            self.render()

    def pan(self, dx: int, dy: int):
        if self.panning_enabled and self.app.active_document:
            active_doc = self.app.active_document
            active_doc.offset_x += dx
            active_doc.offset_y += dy
            self.mark_cache_dirty()
            self.render()

    def fit_to_screen(self):
        """Fit to screen"""
        if self.app.active_document:
            self.app.active_document.zoom_level = 1.0
            self.app.active_document.offset_x = 0
            self.app.active_document.offset_y = 0
            self.mark_cache_dirty()
            self.render()
        else:
            self._show_placeholder()

    def create_new_image(self, width: int, height: int):
        """Create a new blank image/document"""
        doc = self.app.create_new_document(width, height)
        self.mark_cache_dirty()
        self.render(force=True)
        return True