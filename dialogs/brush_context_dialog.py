# dialogs/brush_context_dialog.py - COMPLETE FIXED VERSION

import tkinter as tk
from tkinter import ttk

class BrushContextDialog(tk.Toplevel):
    def __init__(self, parent, brush_tool, x, y):
        super().__init__(parent)
        print(f"🎯 Dialog opening at screen coordinates: ({x}, {y})")
        self.brush_tool = brush_tool
        self.parent = parent
        self.is_syncing = False
        
        # ✅ FIX: Increased dialog height
        self.title("Brush Settings")
        self.geometry("300x400")  # Increased from 280x350
        self.configure(bg="#2d2d30")
        self.resizable(False, False)
        
        # ✅ FIX: Remove shadow to simplify
        self.main_frame = tk.Frame(self, bg="#404040", padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.geometry(f"+{x+10}+{y+10}")
        
        self.transient(parent)
        self.grab_set()
        
        self.build_ui()
        
        # Bind escape key
        self.bind('<Escape>', lambda e: self.cancel())
        self.focus_force()
        
        print("✅ Brush dialog created")
    
    def build_ui(self):
        # ✅ FIX: Use grid for better control
        self.main_frame.columnconfigure(0, weight=1)
        
        # Title
        title_frame = tk.Frame(self.main_frame, bg="#404040")
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        
        # ✅ FIX: Create slider sections with grid
        self.create_slider_section("Brush Size", "brush_size", 1, 100, 1)
        self.create_slider_section("Hardness", "brush_hardness", 0, 100, 2)
        self.create_slider_section("Opacity", "brush_opacity", 1, 100, 3)
        
        # Brush Type
        type_frame = tk.Frame(self.main_frame, bg="#404040")
        type_frame.grid(row=4, column=0, sticky="ew", pady=10)
        
        tk.Label(type_frame, text="Brush Type:", bg="#404040", fg="white",
                font=("Arial", 9)).pack(anchor="w")
        
        brush_types = ["Round", "Soft Round", "Hard Round", "Square", "Flat", "Texture", "Charcoal", "Pencil", "Spatter"]
        self.brush_type_var = tk.StringVar(value=getattr(self.brush_tool, 'brush_type', 'Round'))
        
        type_combo = ttk.Combobox(type_frame, textvariable=self.brush_type_var,
                                values=brush_types, state="readonly", width=15)
        type_combo.pack(fill=tk.X, pady=5)
        type_combo.bind("<<ComboboxSelected>>", self.on_brush_type_change)
        
        # ✅ FIX: Buttons at the bottom with proper spacing
        btn_frame = tk.Frame(self.main_frame, bg="#404040")
        btn_frame.grid(row=5, column=0, sticky="ew", pady=(20, 0))
        
        # Configure button frame columns
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", 
                            bg="#5a5a5a", fg="white", relief="flat",
                            command=self.cancel)
        cancel_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        ok_btn = tk.Button(btn_frame, text="OK",
                        bg="#007acc", fg="white", relief="flat",
                        command=self.ok)
        ok_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        
        # ✅ FIX: Store variables
        self.slider_vars = {
            'size': self.size_var,
            'hardness': self.hardness_var, 
            'opacity': self.opacity_var,
            'type': self.brush_type_var
        }

    def create_slider_section(self, label, attribute, from_val, to_val, row):
        """Create slider section using grid"""
        frame = tk.Frame(self.main_frame, bg="#404040")
        frame.grid(row=row, column=0, sticky="ew", pady=8)
        
        # Label and value
        top_frame = tk.Frame(frame, bg="#404040")
        top_frame.pack(fill=tk.X)
        
        tk.Label(top_frame, text=label, bg="#404040", fg="white",
                font=("Arial", 9)).pack(side=tk.LEFT)
        
        current_value = getattr(self.brush_tool, attribute, from_val)
        
        # Create variables
        if attribute == "brush_size":
            self.size_var = tk.IntVar(value=current_value)
            value_var = self.size_var
        elif attribute == "brush_hardness":
            self.hardness_var = tk.IntVar(value=current_value)  
            value_var = self.hardness_var
        elif attribute == "brush_opacity":
            self.opacity_var = tk.IntVar(value=current_value)
            value_var = self.opacity_var
        else:
            value_var = tk.IntVar(value=current_value)
        
        value_label = tk.Label(top_frame, textvariable=value_var, 
                            bg="#404040", fg="#007acc", font=("Arial", 9, "bold"))
        value_label.pack(side=tk.RIGHT)
        
        # Slider
        slider = tk.Scale(frame, from_=from_val, to=to_val, variable=value_var,
                        orient=tk.HORIZONTAL, length=200,
                        bg="#404040", fg="white", highlightthickness=0,
                        showvalue=False, troughcolor="#606060")
        slider.pack(fill=tk.X)
        
        # Event binding
        if attribute == "brush_size":
            slider.bind("<B1-Motion>", lambda e: self.on_size_change(value_var))
        elif attribute == "brush_hardness":
            slider.bind("<B1-Motion>", lambda e: self.on_hardness_change(value_var))
        elif attribute == "brush_opacity":
            slider.bind("<B1-Motion>", lambda e: self.on_opacity_change(value_var))

    # dialogs/brush_context_dialog.py - REAL-TIME SYNC
    def on_size_change(self, value_var):
        """Handle size change from dialog - WITH REAL-TIME SYNC"""
        if getattr(self, 'is_syncing', False):
            return
            
        self.is_syncing = True
        new_size = value_var.get()
        
        try:
            # Update brush tool
            self.brush_tool.brush_size = new_size
            
            # ✅ FIX: REAL-TIME sync to option bar
            if hasattr(self.parent, 'brush_size_var'):
                self.parent.brush_size_var.set(new_size)
            
            if hasattr(self.parent, 'size_value_var'):
                self.parent.size_value_var.set(f"{new_size}px")
                
            print(f"🔄 Real-time size sync: {new_size}")
            
        finally:
            self.is_syncing = False

    # Similarly for hardness and opacity...
    def on_hardness_change(self, value_var):
        if getattr(self, 'is_syncing', False):
            return
            
        self.is_syncing = True
        new_hardness = value_var.get()
        
        try:
            self.brush_tool.brush_hardness = new_hardness
            
            if hasattr(self.parent, 'brush_hardness_var'):
                self.parent.brush_hardness_var.set(new_hardness)
            
            if hasattr(self.parent, 'hardness_value_var'):
                self.parent.hardness_value_var.set(f"{new_hardness}%")
                
            print(f"🔄 Real-time hardness sync: {new_hardness}")
            
        finally:
            self.is_syncing = False

    def on_opacity_change(self, value_var):
        if getattr(self, 'is_syncing', False):
            return
            
        self.is_syncing = True
        new_opacity = value_var.get()
        
        try:
            self.brush_tool.brush_opacity = new_opacity
            
            if hasattr(self.parent, 'brush_opacity_var'):
                self.parent.brush_opacity_var.set(new_opacity)
            
            if hasattr(self.parent, 'opacity_value_var'):
                self.parent.opacity_value_var.set(f"{new_opacity}%")
                
            print(f"🔄 Real-time opacity sync: {new_opacity}")
            
        finally:
            self.is_syncing = False

    def on_brush_type_change(self, event):
        if getattr(self, 'is_syncing', False):
            return
        self.is_syncing = True
        new_type = self.brush_type_var.get()
        try:
            self.brush_tool.brush_type = new_type
            if hasattr(self.parent, 'sync_from_dialog'):
                self.parent.sync_from_dialog('type', new_type)
        finally:
            self.is_syncing = False

    def ok(self):
        """OK button - PROPER SYNC WITH OPTION BAR"""
        print("🔄 Dialog OK clicked - syncing to option bar")
        
        # Update brush tool
        self.brush_tool.brush_size = self.size_var.get()
        self.brush_tool.brush_hardness = self.hardness_var.get() 
        self.brush_tool.brush_opacity = self.opacity_var.get()
        self.brush_tool.brush_type = self.brush_type_var.get()
        
        # ✅ FIX 1: Call parent's update method
        if hasattr(self.parent, 'update_brush_display'):
            self.parent.update_brush_display(
                self.size_var.get(),
                self.hardness_var.get(),
                self.opacity_var.get(),
                self.brush_type_var.get()
            )
            print("✅ Called update_brush_display")
        
        # ✅ FIX 2: Also try alternative method names
        elif hasattr(self.parent, 'update_brush_options'):
            self.parent.update_brush_options(
                self.size_var.get(),
                self.hardness_var.get(),
                self.opacity_var.get(),
                self.brush_type_var.get()
            )
            print("✅ Called update_brush_options")
        
        # ✅ FIX 3: Direct variable update as fallback
        else:
            print("❌ No update method found, trying direct update")
            self.update_option_bar_directly()
        
        self.destroy()
        print("✅ Dialog closed with sync")

    def update_option_bar_directly(self):
        """Directly update option bar variables"""
        try:
            # Find and update option bar widgets
            if hasattr(self.parent, 'brush_size_var'):
                self.parent.brush_size_var.set(self.size_var.get())
                print(f"✅ Direct updated size: {self.size_var.get()}")
            
            if hasattr(self.parent, 'brush_hardness_var'):
                self.parent.brush_hardness_var.set(self.hardness_var.get())
                print(f"✅ Direct updated hardness: {self.hardness_var.get()}")
                
            if hasattr(self.parent, 'brush_opacity_var'):
                self.parent.brush_opacity_var.set(self.opacity_var.get())
                print(f"✅ Direct updated opacity: {self.opacity_var.get()}")
                
        except Exception as e:
            print(f"❌ Direct update error: {e}")

    def cancel(self):
        self.destroy()
        print("❌ Dialog closed with Cancel")