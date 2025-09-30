# tools/brush.py - COMPLETE FIXED VERSION

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import math
import random
from tools.base_tool import BaseTool

class MasterBrushTool(BaseTool):
    def __init__(self, app):
        super().__init__(app)
        self.name = "Master Brush"
        
        # Brush properties
        self.brush_size = 20
        self.brush_hardness = 85
        self.brush_opacity = 100
        self.brush_color = "black"
        self.brush_type = "Round"
        
        self.available_brush_types = [
            "Round", "Soft Round", "Hard Round", 
            "Square", "Flat", "Texture", 
            "Charcoal", "Pencil", "Spatter"
        ]
        
        # Advanced settings
        self.texture_intensity = 50
        self.grain = 25
        
        # Drawing state
        self.drawing = False
        self.last_point = None
        self.stroke_points = []
        self.preview_image = None
        self.brush_cache = {}
        
        # Temporary stroke tracking
        self.temp_stroke_image = None
        self.stroke_started = False
        
        print("✅ Fixed Master Brush initialized")

    def on_activate(self):
        print(f"🎨 {self.brush_type} Brush activated")

    def on_deactivate(self):
        if self.drawing:
            self.commit_stroke()

    def on_mouse_down(self, x, y, modifiers):
        if not self.app.active_document:
            return
            
        img_x, img_y = self.canvas_to_image(x, y)
        if img_x is None:
            return
            
        self.drawing = True
        self.stroke_started = False
        self.last_point = (img_x, img_y)
        self.stroke_points = [(img_x, img_y)]
        
        print(f"🖱️ Mouse DOWN at image: ({img_x}, {img_y})")
        
        self.start_stroke(img_x, img_y)

    def on_mouse_move(self, x, y, modifiers):
        if not self.drawing:
            return
            
        img_x, img_y = self.canvas_to_image(x, y)
        if img_x is None:
            return
            
        self.stroke_points.append((img_x, img_y))
        
        if not self.stroke_started and len(self.stroke_points) >= 2:
            self.stroke_started = True
        
        # Real-time preview
        self.draw_real_time_preview()
        
        self.last_point = (img_x, img_y)

    def on_mouse_up(self, x, y, modifiers):
        if not self.drawing:
            return
            
        print(f"🖱️ Mouse UP - Committing {len(self.stroke_points)} points")
        self.drawing = False
        
        if len(self.stroke_points) > 1:
            self.commit_quality_stroke()
        else:
            print("⚠️ Not enough points for stroke")
        
        self.last_point = None
        self.stroke_points = []
        self.stroke_started = False
        self.temp_stroke_image = None

    def get_brush_color(self):
        """Get brush color with opacity"""
        try:
            current_color = self.app.foreground_color
            
            if current_color.startswith('#'):
                hex_color = current_color.lstrip('#')
                rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            else:
                color_map = {
                    'black': (0, 0, 0),
                    'white': (255, 255, 255),
                    'red': (255, 0, 0),
                    'green': (0, 255, 0),
                    'blue': (0, 0, 255),
                    'yellow': (255, 255, 0),
                    'cyan': (0, 255, 255),
                    'magenta': (255, 0, 255)
                }
                rgb = color_map.get(current_color, (0, 0, 0))
            
            alpha = int(255 * self.brush_opacity / 100)
            return rgb + (alpha,)
            
        except Exception as e:
            print(f"❌ Color error: {e}")
            return (0, 0, 0, 255)

    def draw_real_time_preview(self):
        """Real-time preview"""
        if len(self.stroke_points) < 2:
            return
            
        try:
            active_doc = self.app.active_document
            if not active_doc or not active_doc.layers:
                return
                
            base_image = active_doc.layers[0].image.copy()
            temp_image = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
            
            if self.brush_type in ["Round", "Soft Round", "Hard Round"]:
                self.draw_line_stroke(temp_image)
            else:
                self.draw_stamped_stroke(temp_image)
            
            composite = Image.alpha_composite(base_image, temp_image)
            self.temp_stroke_image = temp_image
            
            if hasattr(self.app.renderer, 'temporary_display'):
                self.app.renderer.temporary_display(composite)
                
        except Exception as e:
            print(f"❌ Preview error: {e}")

    def draw_line_stroke(self, image):
        """Draw stroke using line method"""
        draw = ImageDraw.Draw(image)
        color = self.get_brush_color()
        
        if len(self.stroke_points) >= 2:
            if self.brush_type == "Soft Round":
                draw.line(self.stroke_points, fill=color, width=self.brush_size, joint="curve")
            elif self.brush_type == "Hard Round":
                draw.line(self.stroke_points, fill=color, width=self.brush_size)
            else:
                draw.line(self.stroke_points, fill=color, width=self.brush_size, joint="curve")

    def draw_stamped_stroke(self, image):
        """Draw stroke using brush stamping"""
        if len(self.stroke_points) < 2:
            return
            
        color = self.get_brush_color()
        
        for i in range(len(self.stroke_points) - 1):
            start = self.stroke_points[i]
            end = self.stroke_points[i + 1]
            
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            distance = max(1, math.sqrt(dx*dx + dy*dy))
            
            spacing = max(2, self.brush_size // 3)
            num_stamps = max(2, int(distance / spacing))
            
            for j in range(num_stamps):
                t = j / (num_stamps - 1) if num_stamps > 1 else 0
                x = int(start[0] + dx * t)
                y = int(start[1] + dy * t)
                
                self.draw_brush_stamp(image, x, y, color)

    def draw_brush_stamp(self, image, x, y, color):
        """Draw a single brush stamp"""
        try:
            brush_tip = self.get_brush_tip()
            if not brush_tip:
                return
                
            radius = self.brush_size // 2
            x1 = max(0, x - radius)
            y1 = max(0, y - radius)
            x2 = min(image.width, x + radius + 1)
            y2 = min(image.height, y + radius + 1)
            
            tip_size = (x2 - x1, y2 - y1)
            if tip_size[0] > 0 and tip_size[1] > 0:
                resized_tip = brush_tip.resize(tip_size, Image.Resampling.LANCZOS)
                colored_tip = self.colorize_brush_tip(resized_tip, color)
                
                region = image.crop((x1, y1, x2, y2))
                composite = Image.alpha_composite(region, colored_tip)
                image.paste(composite, (x1, y1))
                
        except Exception as e:
            print(f"Brush stamp error: {e}")

    def get_brush_tip(self):
        """Generate brush tip"""
        cache_key = f"{self.brush_type}_{self.brush_size}_{self.brush_hardness}"
        
        if cache_key in self.brush_cache:
            return self.brush_cache[cache_key].copy()
        
        try:
            if self.brush_type == "Round":
                brush_tip = self.create_round_brush()
            elif self.brush_type == "Soft Round":
                brush_tip = self.create_soft_round_brush()
            elif self.brush_type == "Hard Round":
                brush_tip = self.create_hard_round_brush()
            elif self.brush_type == "Square":
                brush_tip = self.create_square_brush()
            elif self.brush_type == "Flat":
                brush_tip = self.create_flat_brush()
            elif self.brush_type == "Texture":
                brush_tip = self.create_texture_brush()
            elif self.brush_type == "Charcoal":
                brush_tip = self.create_charcoal_brush()
            elif self.brush_type == "Pencil":
                brush_tip = self.create_pencil_brush()
            elif self.brush_type == "Spatter":
                brush_tip = self.create_spatter_brush()
            else:
                brush_tip = self.create_round_brush()
            
            brush_tip = self.apply_hardness(brush_tip)
            self.brush_cache[cache_key] = brush_tip.copy()
            return brush_tip
            
        except Exception as e:
            print(f"Brush tip creation error: {e}")
            return self.create_round_brush()

    def create_round_brush(self):
        size = self.brush_size
        brush = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(brush)
        draw.ellipse([0, 0, size-1, size-1], fill=255)
        return brush

    def create_soft_round_brush(self):
        size = self.brush_size
        brush = Image.new("L", (size*2, size*2), 0)
        draw = ImageDraw.Draw(brush)
        
        center = size
        for r in range(size, 0, -1):
            alpha = int(255 * (r / size) ** 0.5)
            bbox = [center - r, center - r, center + r, center + r]
            draw.ellipse(bbox, fill=alpha)
        
        return brush.crop((size//2, size//2, size*3//2, size*3//2))

    def create_hard_round_brush(self):
        return self.create_round_brush()

    def create_square_brush(self):
        size = self.brush_size
        brush = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(brush)
        draw.rectangle([0, 0, size-1, size-1], fill=255)
        return brush

    def create_flat_brush(self):
        size = self.brush_size
        brush = Image.new("L", (size, max(3, size//3)), 0)
        draw = ImageDraw.Draw(brush)
        draw.ellipse([0, 0, size-1, max(3, size//3)-1], fill=255)
        return brush

    def create_texture_brush(self):
        size = self.brush_size
        base = self.create_soft_round_brush()
        texture = Image.new("L", base.size, 255)
        
        for x in range(0, texture.width, 3):
            for y in range(0, texture.height, 3):
                if random.random() < self.texture_intensity/100:
                    texture.putpixel((x, y), random.randint(150, 200))
        
        textured = Image.blend(base, texture, 0.3)
        return textured

    def create_charcoal_brush(self):
        size = self.brush_size
        base = self.create_soft_round_brush()
        charcoal = Image.new("L", base.size, 255)
        
        for x in range(0, charcoal.width, 2):
            for y in range(0, charcoal.height, 2):
                if random.random() < 0.7:
                    charcoal.putpixel((x, y), random.randint(150, 200))
        
        return Image.blend(base, charcoal, 0.4)

    def create_pencil_brush(self):
        size = self.brush_size
        brush = Image.new("L", (max(3, size//4), size), 0)
        draw = ImageDraw.Draw(brush)
        draw.ellipse([0, 0, max(3, size//4)-1, size-1], fill=255)
        return brush

    def create_spatter_brush(self):
        size = self.brush_size
        brush = Image.new("L", (size, size), 0)
        
        for i in range(size // 3):
            center_x = random.randint(0, size-1)
            center_y = random.randint(0, size-1)
            splatter_size = random.randint(size//4, size//2)
            
            draw = ImageDraw.Draw(brush)
            for r in range(splatter_size, 0, -1):
                if random.random() < 0.7:
                    alpha = random.randint(100, 200)
                    bbox = [center_x-r, center_y-r, center_x+r, center_y+r]
                    draw.ellipse(bbox, fill=alpha)
        
        return brush

    def apply_hardness(self, brush_tip):
        hardness = self.brush_hardness / 100.0
        
        if hardness < 0.9:
            blur_radius = (1.0 - hardness) * (self.brush_size / 8)
            brush_tip = brush_tip.filter(ImageFilter.GaussianBlur(max(0.5, blur_radius)))
        
        return brush_tip

    def colorize_brush_tip(self, brush_tip, color):
        try:
            colored = Image.new("RGBA", brush_tip.size, color)
            alpha = brush_tip.split()[0]
            colored.putalpha(alpha)
            return colored
        except:
            return Image.new("RGBA", brush_tip.size, color)

    def start_stroke(self, x, y):
        """Initialize stroke"""
        active_doc = self.app.active_document
        if not active_doc or not active_doc.layers:
            return
        
        print("🔄 Starting new stroke")
        self.stroke_started = True

    def commit_quality_stroke(self):
        """FINAL FIX: Permanently save stroke to layer"""
        if not self.app.active_document:
            print("❌ No active document for commit")
            return
            
        try:
            active_doc = self.app.active_document
            active_layer = active_doc.layers[0]

            print(f"💾 Committing stroke to layer: {active_layer.name}")

            # **FIXED: Save to history BEFORE modification**
            if hasattr(active_doc, 'history_manager'):
                # **FIXED: Use simple push without region check**
                active_doc.history_manager.push(active_layer.image.copy(), "Brush Stroke")
                print("✅ History saved")

            # Create the stroke on a temporary image
            temp_image = Image.new("RGBA", active_layer.image.size, (0, 0, 0, 0))
            
            # Draw the actual stroke
            if self.brush_type in ["Round", "Soft Round", "Hard Round"]:
                self.draw_line_stroke(temp_image)
            else:
                self.draw_stamped_stroke(temp_image)

            # Composite and REPLACE the layer image
            composite = Image.alpha_composite(active_layer.image, temp_image)
            active_layer.image = composite  # Complete replacement
            
            print(f"✅ Layer image replaced with new composite")

            # **FIXED: Force renderer refresh**
            if hasattr(self.app, 'renderer') and self.app.renderer:
                # Mark cache as dirty
                if hasattr(self.app.renderer, 'mark_cache_dirty'):
                    self.app.renderer.mark_cache_dirty()
                
                # Force complete re-render
                self.app.renderer.render(force=True)
                print("✅ Renderer forced to refresh")
            
            print(f"✅ {self.brush_type} stroke PERMANENTLY committed and displayed")
            
        except Exception as e:
            print(f"❌ Commit error: {e}")
            import traceback
            traceback.print_exc()

    def commit_stroke(self):
        """Alternative commit method"""
        self.commit_quality_stroke()

    def canvas_to_image(self, x, y):
        """Coordinate conversion"""
        if not hasattr(self.app, 'renderer') or not self.app.renderer:
            return None, None
            
        renderer = self.app.renderer
        if not hasattr(renderer, 'last_image_x'):
            return None, None
            
        img_x = (x - renderer.last_image_x) / renderer.zoom_level
        img_y = (y - renderer.last_image_y) / renderer.zoom_level
        
        active_doc = self.app.active_document
        if not active_doc or not active_doc.layers:
            return None, None
            
        layer = active_doc.layers[0]
        
        if (img_x < 0 or img_y < 0 or img_x >= layer.image.width or img_y >= layer.image.height):
            return None, None
            
        return int(img_x), int(img_y)

    def get_affected_bbox(self):
        """Bounding box calculation for partial rendering"""
        if not self.stroke_points:
            return None
            
        try:
            points = np.array(self.stroke_points)
            min_x, min_y = points.min(axis=0)
            max_x, max_y = points.max(axis=0)
            
            margin = self.brush_size
            
            active_doc = self.app.active_document
            if active_doc and active_doc.layers:
                layer = active_doc.layers[0]
                return (
                    max(0, int(min_x - margin)),
                    max(0, int(min_y - margin)),
                    min(layer.image.width, int(max_x + margin)),
                    min(layer.image.height, int(max_y + margin))
                )
        except:
            return None
            
        return None

    def _is_small_region(self, bbox: tuple, image_size: tuple) -> bool:
        """**NEW ADDED: Check if region is small enough for optimized saving**"""
        if not bbox:
            return False
            
        try:
            x1, y1, x2, y2 = bbox
            region_area = (x2 - x1) * (y2 - y1)
            total_area = image_size[0] * image_size[1]
            
            # Save region if it's less than 30% of total area
            return region_area < total_area * 0.3
        except:
            return False


def make_tool(app):
    return MasterBrushTool(app)