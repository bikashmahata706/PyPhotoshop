# app/history.py - COMPLETE UNDO/REDO SYSTEM

import pickle
import zlib
from PIL import Image
import io
import os
from datetime import datetime

class HistoryAction:
    """Base class for all history actions"""
    def __init__(self, description):
        self.description = description
        self.timestamp = datetime.now()
        self.affected_bbox = None  # (x1, y1, x2, y2) for partial updates
    
    def apply(self, image):
        """Apply this action to an image"""
        raise NotImplementedError("Subclasses must implement apply()")
    
    def revert(self, image):
        """Revert this action from an image"""
        raise NotImplementedError("Subclasses must implement revert()")
    
    def get_memory_usage(self):
        """Estimate memory usage of this action"""
        return 0

class BrushStrokeAction(HistoryAction):
    """History action for brush strokes"""
    def __init__(self, description, stroke_data, brush_size, brush_color):
        super().__init__(f"Brush: {description}")
        self.stroke_data = stroke_data  # List of points [(x1,y1), (x2,y2), ...]
        self.brush_size = brush_size
        self.brush_color = brush_color
        self.snapshot = None
        self.affected_bbox = None
        
    def apply(self, image):
        """Apply brush stroke to image"""
        if self.snapshot is None:
            # Take snapshot of affected area before applying
            self._take_snapshot(image)
        
        # The brush stroke is already applied in real-time, so this is mostly for redo
        pass
    
    def revert(self, image):
        """Revert brush stroke by restoring snapshot"""
        if self.snapshot and self.affected_bbox:
            self._restore_snapshot(image)
    
    def _take_snapshot(self, image):
        """Take snapshot of affected area"""
        if not self.stroke_data:
            return
            
        # Calculate bounding box of stroke with padding
        x_coords = [p[0] for p in self.stroke_data]
        y_coords = [p[1] for p in self.stroke_data]
        
        padding = self.brush_size + 10
        x1 = max(0, min(x_coords) - padding)
        y1 = max(0, min(y_coords) - padding)
        x2 = min(image.width, max(x_coords) + padding)
        y2 = min(image.height, max(y_coords) + padding)
        
        self.affected_bbox = (x1, y1, x2, y2)
        
        # Crop and save the affected region
        region = image.crop(self.affected_bbox)
        
        # Convert to compressed bytes to save memory
        buffer = io.BytesIO()
        region.save(buffer, format='PNG', optimize=True)
        self.snapshot = zlib.compress(buffer.getvalue())
    
    def _restore_snapshot(self, image):
        """Restore snapshot to affected area"""
        if self.snapshot and self.affected_bbox:
            # Decompress and load the snapshot
            decompressed = zlib.decompress(self.snapshot)
            snapshot_image = Image.open(io.BytesIO(decompressed))
            
            # Paste back to original position
            image.paste(snapshot_image, self.affected_bbox[:2])
    
    def get_memory_usage(self):
        """Estimate memory usage"""
        if self.snapshot:
            return len(self.snapshot)
        return 0

class ImageLoadAction(HistoryAction):
    """History action for image loading"""
    def __init__(self, description, image_path):
        super().__init__(f"Load: {description}")
        self.image_path = image_path
        self.previous_state = None
        
    def apply(self, image):
        """Load image - handled by main application"""
        pass
    
    def revert(self, image):
        """Revert to previous state"""
        if self.previous_state:
            # Decompress previous image
            decompressed = zlib.decompress(self.previous_state)
            previous_image = Image.open(io.BytesIO(decompressed))
            
            # Replace current image
            image = previous_image.copy()
            return image
        return image
    
    def set_previous_state(self, image):
        """Store the previous image state"""
        if image:
            buffer = io.BytesIO()
            image.save(buffer, format='PNG', optimize=True)
            self.previous_state = zlib.compress(buffer.getvalue())

class TransformationAction(HistoryAction):
    """History action for transformations (resize, rotate, etc.)"""
    def __init__(self, description, transform_type, parameters):
        super().__init__(f"{transform_type}: {description}")
        self.transform_type = transform_type
        self.parameters = parameters
        self.previous_state = None
        self.previous_size = None
        
    def apply(self, image):
        """Apply transformation"""
        if self.transform_type == "resize":
            new_width = self.parameters['width']
            new_height = self.parameters['height']
            return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        elif self.transform_type == "rotate":
            angle = self.parameters['angle']
            return image.rotate(angle, expand=True)
        return image
    
    def revert(self, image):
        """Revert transformation"""
        if self.previous_state:
            decompressed = zlib.decompress(self.previous_state)
            return Image.open(io.BytesIO(decompressed))
        return image
    
    def set_previous_state(self, image):
        """Store previous image state"""
        if image:
            self.previous_size = image.size
            buffer = io.BytesIO()
            image.save(buffer, format='PNG', optimize=True)
            self.previous_state = zlib.compress(buffer.getvalue())

class HistoryManager:
    """Main history manager for undo/redo functionality"""
    
    def __init__(self, max_steps=50, max_memory_mb=100):
        self.max_steps = max_steps
        self.max_memory_mb = max_memory_mb * 1024 * 1024  # Convert to bytes
        
        self.undo_stack = []  # Actions that can be undone
        self.redo_stack = []  # Actions that can be redone
        
        self.current_memory_usage = 0
        self.enabled = True
        
        print(f"✅ History Manager: {max_steps} steps, {max_memory_mb//(1024*1024)}MB max")
    
    def push_action(self, action, current_image=None):
        """Push a new action to the history stack"""
        if not self.enabled:
            return
            
        # Clear redo stack when new action is performed
        self.redo_stack.clear()
        
        # For certain actions, store the previous state
        if isinstance(action, ImageLoadAction) and current_image:
            action.set_previous_state(current_image)
        elif isinstance(action, TransformationAction) and current_image:
            action.set_previous_state(current_image)
        
        # Add to undo stack
        self.undo_stack.append(action)
        
        # Update memory usage
        self.current_memory_usage += action.get_memory_usage()
        
        # Cleanup if limits are exceeded
        self._cleanup_old_actions()
        
        print(f"📝 History: {action.description} (Memory: {self.current_memory_usage//1024}KB)")
    
    def undo(self, current_image):
        """Undo the last action"""
        if not self.undo_stack or not self.enabled:
            return current_image, False
            
        # Pop the last action
        action = self.undo_stack.pop()
        
        # Revert the action
        result_image = action.revert(current_image)
        
        # Move to redo stack
        self.redo_stack.append(action)
        
        # Update memory usage (action moves between stacks, no change)
        
        print(f"↩️  Undo: {action.description}")
        return result_image, True
    
    def redo(self, current_image):
        """Redo the last undone action"""
        if not self.redo_stack or not self.enabled:
            return current_image, False
            
        # Pop from redo stack
        action = self.redo_stack.pop()
        
        # Re-apply the action
        result_image = action.apply(current_image)
        
        # Move back to undo stack
        self.undo_stack.append(action)
        
        print(f"↪️  Redo: {action.description}")
        return result_image, True
    
    def can_undo(self):
        """Check if undo is possible"""
        return len(self.undo_stack) > 0 and self.enabled
    
    def can_redo(self):
        """Check if redo is possible"""
        return len(self.redo_stack) > 0 and self.enabled
    
    def get_undo_description(self):
        """Get description of next undo action"""
        if self.can_undo():
            return self.undo_stack[-1].description
        return "Nothing to undo"
    
    def get_redo_description(self):
        """Get description of next redo action"""
        if self.can_redo():
            return self.redo_stack[-1].description
        return "Nothing to redo"
    
    def clear(self):
        """Clear all history"""
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.current_memory_usage = 0
        print("🗑️ History cleared")
    
    def get_history_info(self):
        """Get history statistics"""
        return {
            'undo_count': len(self.undo_stack),
            'redo_count': len(self.redo_stack),
            'memory_usage_kb': self.current_memory_usage // 1024,
            'max_steps': self.max_steps,
            'max_memory_mb': self.max_memory_mb // (1024 * 1024)
        }
    
    def _cleanup_old_actions(self):
        """Cleanup old actions when limits are exceeded"""
        # Check step count limit
        while len(self.undo_stack) > self.max_steps:
            old_action = self.undo_stack.pop(0)
            self.current_memory_usage -= old_action.get_memory_usage()
        
        # Check memory limit
        while self.current_memory_usage > self.max_memory_mb and self.undo_stack:
            old_action = self.undo_stack.pop(0)
            self.current_memory_usage -= old_action.get_memory_usage()
    
    def save_history(self, filepath):
        """Save history to file (for session persistence)"""
        try:
            with open(filepath, 'wb') as f:
                data = {
                    'undo_stack': self.undo_stack,
                    'redo_stack': self.redo_stack,
                    'current_memory_usage': self.current_memory_usage
                }
                pickle.dump(data, f)
            print(f"💾 History saved: {filepath}")
            return True
        except Exception as e:
            print(f"❌ History save error: {e}")
            return False
    
    def load_history(self, filepath):
        """Load history from file"""
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.undo_stack = data.get('undo_stack', [])
                self.redo_stack = data.get('redo_stack', [])
                self.current_memory_usage = data.get('current_memory_usage', 0)
            print(f"📂 History loaded: {filepath}")
            return True
        except Exception as e:
            print(f"❌ History load error: {e}")
            return False
    
    def enable(self):
        """Enable history tracking"""
        self.enabled = True
        print("✅ History enabled")
    
    def disable(self):
        """Disable history tracking"""
        self.enabled = False
        print("⏸️ History disabled")

# Factory functions for creating history actions
def create_brush_stroke(stroke_points, brush_size, brush_color, description="Stroke"):
    """Create a brush stroke history action"""
    return BrushStrokeAction(description, stroke_points, brush_size, brush_color)

def create_image_load(image_path, description=None):
    """Create an image load history action"""
    if description is None:
        description = os.path.basename(image_path)
    return ImageLoadAction(description, image_path)

def create_resize(new_width, new_height, description="Resize"):
    """Create a resize transformation action"""
    params = {'width': new_width, 'height': new_height}
    return TransformationAction(description, "resize", params)

def create_rotation(angle, description="Rotate"):
    """Create a rotation transformation action"""
    params = {'angle': angle}
    return TransformationAction(description, "rotate", params)