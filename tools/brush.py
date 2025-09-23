# tools/brush.py - FINAL WORKING VERSION

from PIL import Image, ImageDraw
from tools.base_tool import BaseTool

class BrushTool(BaseTool):
    def __init__(self, app):
        super().__init__(app)
        self.brush_size = 20
        self.brush_color = (255, 0, 0, 255)  # Bright red
        self.is_drawing = False
        self.last_point = None
        
    def on_activate(self):
        print("🎨 Brush tool ACTIVATED")
        if self.app.canvas:
            self.app.canvas.config(cursor="circle")
    
    def on_mouse_down(self, x, y, modifiers):
        if not self._has_valid_image():
            print("❌ No valid image to draw on")
            return
            
        image_x, image_y = self._get_image_coords(x, y)
        
        if image_x >= 0 and image_y >= 0:
            print(f"📍 Mouse DOWN at image: ({image_x}, {image_y})")
            
            self.is_drawing = True
            self.last_point = (image_x, image_y)
            
            # Draw immediate dot
            self._draw_single_point(image_x, image_y)
    
    def on_mouse_move(self, x, y, modifiers):
        if not self.is_drawing or not self._has_valid_image():
            return
            
        image_x, image_y = self._get_image_coords(x, y)
        
        if image_x >= 0 and image_y >= 0 and self.last_point:
            print(f"🖱️ Mouse MOVE from {self.last_point} to ({image_x}, {image_y})")
            
            # Draw line between points
            self._draw_line_between_points(self.last_point, (image_x, image_y))
            self.last_point = (image_x, image_y)
    
    def on_mouse_up(self, x, y, modifiers):
        if self.is_drawing:
            print("✅ Mouse UP - stroke completed")
            self.is_drawing = False
            self.last_point = None
    
    def _has_valid_image(self):
        """Check if we have a valid image to draw on"""
        return (hasattr(self.app, 'original_image') and 
                self.app.original_image is not None)
    
    def _get_image_coords(self, canvas_x, canvas_y):
        """Convert canvas coordinates to image coordinates"""
        if not self._has_valid_image():
            return -1, -1
        
        try:
            # Get original image size
            orig_width, orig_height = self.app.original_image.size
            
            # Get displayed image size
            if hasattr(self.app, 'current_image') and self.app.current_image:
                disp_width = self.app.current_image.width
                disp_height = self.app.current_image.height
            else:
                disp_width, disp_height = orig_width, orig_height
            
            # Get canvas size
            canvas_width = self.app.canvas.winfo_width()
            canvas_height = self.app.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width, canvas_height = 800, 600
            
            # Calculate where image is displayed
            image_x = (canvas_width - disp_width) // 2
            image_y = (canvas_height - disp_height) // 2
            
            # Convert to display coordinates
            disp_x = canvas_x - image_x
            disp_y = canvas_y - image_y
            
            # Check if within display bounds
            if (0 <= disp_x < disp_width and 0 <= disp_y < disp_height):
                # Convert to original image coordinates
                scale_x = orig_width / disp_width
                scale_y = orig_height / disp_height
                
                orig_x = int(disp_x * scale_x)
                orig_y = int(disp_y * scale_y)
                
                # Ensure within bounds
                orig_x = max(0, min(orig_width - 1, orig_x))
                orig_y = max(0, min(orig_height - 1, orig_y))
                
                return orig_x, orig_y
            
            return -1, -1
            
        except Exception as e:
            print(f"❌ Coordinate error: {e}")
            return -1, -1
    
    def _draw_single_point(self, x, y):
        """Draw a single point on the image"""
        try:
            # Create drawing context on ORIGINAL image
            draw = ImageDraw.Draw(self.app.original_image)
            
            # Draw a circle/point
            r = self.brush_size // 2
            draw.ellipse([x-r, y-r, x+r, y+r], fill=self.brush_color)
            
            # IMMEDIATELY update display
            self._force_display_update()
            
            print("✅ Point drawn")
            
        except Exception as e:
            print(f"❌ Point drawing error: {e}")
    
    def _draw_line_between_points(self, start, end):
        """Draw a line between two points"""
        try:
            # Create drawing context on ORIGINAL image
            draw = ImageDraw.Draw(self.app.original_image)
            
            # Draw line
            draw.line([start, end], fill=self.brush_color, width=self.brush_size)
            
            # IMMEDIATELY update display
            self._force_display_update()
            
            print("✅ Line drawn")
            
        except Exception as e:
            print(f"❌ Line drawing error: {e}")
    
    def _force_display_update(self):
        """Force the display to update with current image"""
        try:
            if (hasattr(self.app, 'renderer') and 
                self.app.renderer is not None):
                
                # CRITICAL: Tell renderer to redraw from current original image
                self.app.renderer.render(force=True)
                
                # Force canvas update
                self.app.canvas.update_idletasks()
                
                print("🔄 Display updated")
                
        except Exception as e:
            print(f"❌ Display update error: {e}")

def make_tool(app):
    return BrushTool(app)