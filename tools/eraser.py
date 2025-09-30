# tools/eraser.py - COMPLETE ERASER TOOL

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from tools.brush import MasterBrushTool

class EraserTool(MasterBrushTool):
    def __init__(self, app):
        super().__init__(app)
        self.name = "Eraser"
        
        # Eraser-specific properties
        self.brush_size = 30  # Slightly larger default
        self.brush_opacity = 100  # Full erase by default
        self.brush_type = "Round"  # Same brush types as brush tool
        
        print("✅ Eraser tool initialized")

    def on_activate(self):
        print("🧽 Eraser activated - same brush types as brush tool")
        # Show eraser-specific cursor or feedback

    def get_brush_color(self):
        """Eraser uses transparent color to remove pixels"""
        return (0, 0, 0, 0)  # Fully transparent

    def commit_quality_stroke(self):
        """Eraser commit with history"""
        if not self.app.active_document:
            return
            
        try:
            active_doc = self.app.active_document
            active_layer = active_doc.layers[0]
            
            # ✅ SAVE STATE BEFORE ERASING
            if hasattr(active_doc, 'history_manager'):
                active_doc.history_manager.push(active_layer.image.copy(), "Eraser Stroke")
            
            # Use same method as brush but with transparent color
            temp_image = Image.new("RGBA", active_layer.image.size, (0, 0, 0, 0))
            
            if self.brush_type in ["Round", "Soft Round", "Hard Round"]:
                self.draw_line_stroke(temp_image)
            else:
                self.draw_stamped_stroke(temp_image)
            
            # For eraser, we use destination-out composition
            # This properly removes pixels instead of just adding transparency
            result = self.eraser_composite(active_layer.image, temp_image)
            active_layer.image.paste(result)
            
            # Update display
            self.app.renderer.render(force=True)
            
            print("✅ Eraser stroke committed")
            
        except Exception as e:
            print(f"❌ Eraser commit error: {e}")

    def eraser_composite(self, base_image, erase_image):
        """Special composition for eraser - properly removes pixels"""
        try:
            # Convert to arrays for pixel-level operations
            base_array = np.array(base_image)
            erase_array = np.array(erase_image)
            
            # Get alpha channel from erase brush
            erase_alpha = erase_array[:, :, 3]
            
            # Reduce alpha in base image where eraser touched
            result_array = base_array.copy()
            result_array[:, :, 3] = result_array[:, :, 3] * (1 - erase_alpha / 255.0)
            
            # Convert back to PIL Image
            result_image = Image.fromarray(result_array.astype('uint8'), 'RGBA')
            return result_image
            
        except Exception as e:
            print(f"❌ Eraser composite error: {e}")
            # Fallback to standard composite
            return Image.alpha_composite(base_image, erase_image)