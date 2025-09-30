# app/history.py - COMPLETE SMOOTH UNDO/REDO VERSION

import os
import tempfile
from PIL import Image
import numpy as np
from typing import Tuple, Dict, Any, Optional, List

class HistoryManager:
    def __init__(self, max_history: int = 30):
        self.history_stack = []
        self.redo_stack = []
        self.max_history = max_history
        self.temp_dir = tempfile.mkdtemp(prefix="imageforge_")
        
        # **NEW: Performance optimizations for smooth undo/redo**
        self.memory_cache = {}
        self.max_memory_cache = 8  # Increased for better performance
        self.compression_quality = 4  # Faster compression
        
        # **NEW: Region-based undo tracking**
        self.region_states = []
        self.enable_partial_undo = True
        
        # **NEW: Smart caching for frequent operations**
        self.last_full_state = None
        self.last_full_key = None
        
        print(f"✅ Smooth HistoryManager initialized (max: {max_history})")

    def push(self, image: Image.Image, action_name: str = "Action", bbox: Optional[Tuple] = None) -> bool:
        """Save state to history - OPTIMIZED FOR SMOOTH OPERATION"""
        try:
            # **NEW: Smart state management**
            cache_key = f"state_{len(self.history_stack)}_{action_name}"
            
            # Store in memory cache for instant access
            self.memory_cache[cache_key] = image.copy()
            
            # **NEW: Only save to disk if necessary (lazy saving)**
            if len(self.history_stack) < self.max_memory_cache:
                temp_path = os.path.join(self.temp_dir, f"{cache_key}.png")
                image.save(temp_path, "PNG", optimize=True, compress_level=self.compression_quality)
            else:
                temp_path = None
            
            # Add to history stack
            history_entry = {
                'path': temp_path,
                'action': action_name,
                'cache_key': cache_key,
                'type': 'full'
            }
            
            # **NEW: Store bounding box for partial rendering if provided**
            if bbox and self.enable_partial_undo:
                history_entry['bbox'] = bbox
                history_entry['type'] = 'region_aware'
            
            self.history_stack.append(history_entry)
            
            # **NEW: Smart redo stack clearing**
            self._smart_clear_redo()
            
            # **NEW: Optimized history limiting**
            self._smart_enforce_limits()
            
            print(f"✅ History saved: {action_name} (memory: {len(self.memory_cache)})")
            return True
            
        except Exception as e:
            print(f"❌ History push error: {e}")
            return False

    def push_region(self, image: Image.Image, bbox: Tuple[int, int, int, int], action_name: str = "Brush Stroke") -> bool:
        """**NEW: Optimized region-based history for brush strokes**"""
        try:
            if not self._is_region_worth_saving(bbox, image.size):
                # Region too large, save full image instead
                return self.push(image, action_name, bbox)
                
            x1, y1, x2, y2 = bbox
            region = image.crop(bbox)
            
            # Store region in memory cache
            cache_key = f"region_{len(self.history_stack)}"
            self.memory_cache[cache_key] = region.copy()
            
            # Save region to disk only if necessary
            if len(self.history_stack) < self.max_memory_cache:
                temp_path = os.path.join(self.temp_dir, f"{cache_key}.png")
                region.save(temp_path, "PNG", optimize=True, compress_level=self.compression_quality)
            else:
                temp_path = None
            
            # Add region state to history
            self.history_stack.append({
                'path': temp_path,
                'action': action_name,
                'cache_key': cache_key,
                'type': 'region',
                'bbox': bbox
            })
            
            # Clear redo stack
            self._smart_clear_redo()
            
            # Enforce limits
            self._smart_enforce_limits()
            
            print(f"✅ Region history: {action_name} ({(x2-x1)}x{(y2-y1)})")
            return True
            
        except Exception as e:
            print(f"❌ Region push error: {e}")
            # Fallback to full image save
            return self.push(image, action_name, bbox)

    def _is_region_worth_saving(self, bbox: Tuple[int, int, int, int], image_size: Tuple[int, int]) -> bool:
        """Check if region save is more efficient than full save"""
        x1, y1, x2, y2 = bbox
        region_area = (x2 - x1) * (y2 - y1)
        total_area = image_size[0] * image_size[1]
        
        # Save region if it's less than 50% of total area (increased threshold for better performance)
        return region_area < total_area * 0.5

    def undo(self, current_image: Image.Image) -> Tuple[Image.Image, bool, Optional[Tuple]]:
        """**SMOOTH UNDO: Fast undo with partial rendering support**"""
        if not self.history_stack:
            return current_image, False, None
            
        try:
            # **NEW: Fast current state capture**
            redo_cache_key = f"redo_{len(self.redo_stack)}"
            self.memory_cache[redo_cache_key] = current_image.copy()
            
            # Save current state to redo stack (lazy disk saving)
            if len(self.redo_stack) < self.max_memory_cache:
                redo_path = os.path.join(self.temp_dir, f"{redo_cache_key}.png")
                current_image.save(redo_path, "PNG", optimize=True, compress_level=self.compression_quality)
            else:
                redo_path = None
            
            self.redo_stack.append({
                'path': redo_path,
                'action': 'Redo State',
                'cache_key': redo_cache_key,
                'type': 'full'
            })
            
            # **NEW: Fast state restoration from memory cache**
            previous_state = self.history_stack.pop()
            
            # Get the previous image from memory cache
            if previous_state['cache_key'] in self.memory_cache:
                previous_image = self.memory_cache[previous_state['cache_key']].copy()
            else:
                # Fallback to disk load (should be rare)
                previous_image = Image.open(previous_state['path'])
                self.memory_cache[previous_state['cache_key']] = previous_image.copy()
            
            # **NEW: Handle different state types for optimal rendering**
            bbox = None
            result_image = previous_image
            
            if previous_state['type'] == 'region' and 'bbox' in previous_state:
                # Region-based undo: paste region back onto current image
                x1, y1, x2, y2 = previous_state['bbox']
                current_image.paste(previous_image, (x1, y1))
                result_image = current_image
                bbox = previous_state['bbox']
                
            elif previous_state['type'] == 'region_aware' and 'bbox' in previous_state:
                # Full image but with bbox info for partial rendering
                bbox = previous_state['bbox']
            
            print(f"✅ Smooth Undo: {previous_state['action']}")
            return result_image, True, bbox
            
        except Exception as e:
            print(f"❌ Undo error: {e}")
            return current_image, False, None

    def redo(self, current_image: Image.Image) -> Tuple[Image.Image, bool, Optional[Tuple]]:
        """**SMOOTH REDO: Fast redo with partial rendering support**"""
        if not self.redo_stack:
            return current_image, False, None
            
        try:
            # **NEW: Fast current state capture**
            history_cache_key = f"state_{len(self.history_stack)}"
            self.memory_cache[history_cache_key] = current_image.copy()
            
            # Save current state to history stack (lazy disk saving)
            if len(self.history_stack) < self.max_memory_cache:
                history_path = os.path.join(self.temp_dir, f"{history_cache_key}.png")
                current_image.save(history_path, "PNG", optimize=True, compress_level=self.compression_quality)
            else:
                history_path = None
            
            self.history_stack.append({
                'path': history_path,
                'action': 'History State',
                'cache_key': history_cache_key,
                'type': 'full'
            })
            
            # **NEW: Fast state restoration from memory cache**
            next_state = self.redo_stack.pop()
            
            if next_state['cache_key'] in self.memory_cache:
                next_image = self.memory_cache[next_state['cache_key']].copy()
            else:
                # Fallback to disk load
                next_image = Image.open(next_state['path'])
                self.memory_cache[next_state['cache_key']] = next_image.copy()
            
            # **NEW: Handle bbox for partial rendering**
            bbox = None
            if next_state['type'] == 'region' and 'bbox' in next_state:
                bbox = next_state['bbox']
            elif next_state['type'] == 'region_aware' and 'bbox' in next_state:
                bbox = next_state['bbox']
            
            print(f"✅ Smooth Redo")
            return next_image, True, bbox
            
        except Exception as e:
            print(f"❌ Redo error: {e}")
            return current_image, False, None

    def _smart_clear_redo(self):
        """**NEW: Smart redo stack clearing with memory management**"""
        # Clear disk files for redo stack
        for state in self.redo_stack:
            self._cleanup_state(state)
        
        # Clear memory cache entries for redo
        redo_keys = [state['cache_key'] for state in self.redo_stack]
        for key in redo_keys:
            if key in self.memory_cache and not self._is_key_in_history(key):
                del self.memory_cache[key]
        
        self.redo_stack.clear()

    def _is_key_in_history(self, key: str) -> bool:
        """Check if a cache key is in history stack"""
        for state in self.history_stack:
            if state['cache_key'] == key:
                return True
        return False

    def _smart_enforce_limits(self):
        """**NEW: Smart history limiting with memory optimization**"""
        while len(self.history_stack) > self.max_history:
            old_state = self.history_stack.pop(0)
            self._cleanup_state(old_state)
        
        # **NEW: Smart memory cache cleanup**
        self._optimize_memory_cache()

    def _optimize_memory_cache(self):
        """**NEW: Optimize memory cache while keeping recent states**"""
        if len(self.memory_cache) <= self.max_memory_cache * 1.5:
            return
            
        # Get all keys from memory cache
        all_keys = list(self.memory_cache.keys())
        
        # Keep recent history and redo states
        history_keys = [state['cache_key'] for state in self.history_stack[-self.max_memory_cache:]]
        redo_keys = [state['cache_key'] for state in self.redo_stack[-self.max_memory_cache//2:]]
        
        protected_keys = set(history_keys + redo_keys)
        
        # Remove old entries
        for key in all_keys:
            if key not in protected_keys:
                del self.memory_cache[key]
                
        print(f"🔄 Memory cache optimized: {len(self.memory_cache)} entries")

    def _cleanup_state(self, state: Dict[str, Any]):
        """Cleanup individual history state"""
        try:
            # Only remove from memory cache if not in active use
            if (state['cache_key'] in self.memory_cache and 
                not self._is_key_active(state['cache_key'])):
                del self.memory_cache[state['cache_key']]
            
            # Remove disk file if it exists
            if state['path'] and os.path.exists(state['path']):
                os.remove(state['path'])
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")

    def _is_key_active(self, key: str) -> bool:
        """Check if cache key is in active history or redo stacks"""
        for state in self.history_stack[-5:]:  # Check recent history
            if state['cache_key'] == key:
                return True
        for state in self.redo_stack[-3:]:  # Check recent redo
            if state['cache_key'] == key:
                return True
        return False

    def get_history_info(self) -> Dict[str, Any]:
        """**NEW: Enhanced history information for UI**"""
        return {
            'total_actions': len(self.history_stack),
            'can_undo': len(self.history_stack) > 0,
            'can_redo': len(self.redo_stack) > 0,
            'memory_usage': len(self.memory_cache),
            'last_action': self.history_stack[-1]['action'] if self.history_stack else None,
            'memory_efficiency': f"{len(self.memory_cache)}/{self.max_memory_cache}"
        }

    def clear(self):
        """Clear all history - OPTIMIZED"""
        # Clear memory cache
        self.memory_cache.clear()
        
        # Clear disk files
        for state in self.history_stack + self.redo_stack:
            try:
                if state['path'] and os.path.exists(state['path']):
                    os.remove(state['path'])
            except:
                pass
        
        # Clear stacks
        self.history_stack.clear()
        self.redo_stack.clear()
        
        print("✅ History cleared completely")

    def enable_region_undo(self, enable: bool = True):
        """**NEW: Enable/disable region-based undo**"""
        self.enable_partial_undo = enable
        print(f"🔄 Region-based undo: {'enabled' if enable else 'disabled'}")

    def set_memory_cache_size(self, size: int):
        """**NEW: Adjust memory cache size dynamically**"""
        self.max_memory_cache = max(3, min(size, 20))  # Limit between 3-20
        self._optimize_memory_cache()
        print(f"🔄 Memory cache size set to: {self.max_memory_cache}")

    def get_performance_stats(self) -> Dict[str, Any]:
        """**NEW: Get performance statistics**"""
        memory_usage = sum(
            img.size[0] * img.size[1] * 4  # Approximate memory (RGBA)
            for img in self.memory_cache.values()
        ) / (1024 * 1024)  # Convert to MB
        
        return {
            'history_states': len(self.history_stack),
            'redo_states': len(self.redo_stack),
            'memory_cache_entries': len(self.memory_cache),
            'estimated_memory_mb': round(memory_usage, 2),
            'region_undo_enabled': self.enable_partial_undo,
            'cache_efficiency': f"{len(self.memory_cache)}/{self.max_memory_cache}"
        }

    def __del__(self):
        """Cleanup temp directory on destruction"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except:
            pass