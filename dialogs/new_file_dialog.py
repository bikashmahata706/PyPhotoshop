import tkinter as tk
from tkinter import ttk, messagebox

class NewFileDialog(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.result = None
        self.transient(parent)
        self.grab_set()
        
        # Default values
        self.width = 800
        self.height = 600
        self.resolution = 72
        self.color_mode = "RGB"
        self.background = "White"
        self.unit = "Pixels"
        
        self.build_ui()
        self.center_window()
    
    def center_window(self):
        self.update_idletasks()
        
        # Window size
        width = 500
        height = 650
        
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate position for perfect center
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        # Ensure window stays within screen bounds
        x = max(0, min(x, screen_width - width))
        y = max(0, min(y, screen_height - height))
        
        # Apply geometry
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        print(f"✅ Dialog centered at ({x}, {y})")
    
    def build_ui(self):
        self.title("ImageForge - New Document")
        self.configure(bg="#2d2d30")
        self.resizable(False, False)
        
        # Main container
        main_frame = tk.Frame(self, bg="#2d2d30", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="New Document", 
                              font=("Arial", 16, "bold"), 
                              fg="white", bg="#2d2d30")
        title_label.pack(pady=(0, 20))
        
        # Preset Section
        self.create_preset_section(main_frame)
        
        # Document Size Section
        self.create_size_section(main_frame)
        
        # Advanced Options
        self.create_advanced_section(main_frame)
        
        # Action Buttons
        self.create_action_buttons(main_frame)
    
    def create_preset_section(self, parent):
        preset_frame = tk.LabelFrame(parent, text="Preset", 
                                   font=("Arial", 10, "bold"),
                                   fg="white", bg="#2d2d30", 
                                   labelanchor="nw", padx=10, pady=10)
        preset_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Preset dropdown
        presets = [
            "Custom",
            "Default Photoshop Size",
            "Letter", "Legal", "Tabloid",
            "A4", "A3", "A2",
            "Web 1920x1080", "Web 1280x720",
            "Mobile 1080x1920", "Mobile 750x1334",
            "Instagram Post (1080x1080)", "Instagram Story (1080x1920)"
        ]
        
        self.preset_var = tk.StringVar(value="Default Photoshop Size")
        preset_combo = ttk.Combobox(preset_frame, textvariable=self.preset_var,
                                   values=presets, state="readonly", width=30)
        preset_combo.pack(fill=tk.X, pady=5)
        preset_combo.bind("<<ComboboxSelected>>", self.on_preset_change)
        
        # Recent documents (placeholder)
        recent_label = tk.Label(preset_frame, text="Recent Documents: None",
                               fg="#cccccc", bg="#2d2d30", font=("Arial", 9))
        recent_label.pack(anchor="w", pady=(10, 0))
    
    def create_size_section(self, parent):
        size_frame = tk.LabelFrame(parent, text="Document Size", 
                                 font=("Arial", 10, "bold"),
                                 fg="white", bg="#2d2d30", 
                                 labelanchor="nw", padx=10, pady=10)
        size_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Width/Height row
        size_grid = tk.Frame(size_frame, bg="#2d2d30")
        size_grid.pack(fill=tk.X, pady=5)
        
        # Width
        tk.Label(size_grid, text="Width:", fg="white", bg="#2d2d30").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.width_var = tk.StringVar(value="800")
        width_entry = tk.Entry(size_grid, textvariable=self.width_var, width=10, bg="#3c3c3c", fg="white")
        width_entry.grid(row=0, column=1, padx=(0, 10))
        
        # Height
        tk.Label(size_grid, text="Height:", fg="white", bg="#2d2d30").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.height_var = tk.StringVar(value="600")
        height_entry = tk.Entry(size_grid, textvariable=self.height_var, width=10, bg="#3c3c3c", fg="white")
        height_entry.grid(row=0, column=3, padx=(0, 10))
        
        # Units
        units = ["Pixels", "Inches", "cm", "mm", "Points", "Picas"]
        self.unit_var = tk.StringVar(value="Pixels")
        unit_combo = ttk.Combobox(size_grid, textvariable=self.unit_var,
                                 values=units, state="readonly", width=8)
        unit_combo.grid(row=0, column=4)
        unit_combo.bind("<<ComboboxSelected>>", self.on_unit_change)
        
        # Resolution
        res_frame = tk.Frame(size_frame, bg="#2d2d30")
        res_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(res_frame, text="Resolution:", fg="white", bg="#2d2d30").pack(side=tk.LEFT, padx=(0, 10))
        self.res_var = tk.StringVar(value="72")
        res_entry = tk.Entry(res_frame, textvariable=self.res_var, width=8, bg="#3c3c3c", fg="white")
        res_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(res_frame, text="pixels/inch", fg="white", bg="#2d2d30").pack(side=tk.LEFT)
        
        # Aspect ratio lock
        self.lock_aspect = tk.BooleanVar(value=True)
        lock_btn = tk.Checkbutton(size_frame, text="Lock aspect ratio", 
                                 variable=self.lock_aspect,
                                 fg="white", bg="#2d2d30", selectcolor="#2d2d30")
        lock_btn.pack(anchor="w", pady=5)
    
    def create_advanced_section(self, parent):
        advanced_frame = tk.LabelFrame(parent, text="Advanced Options", 
                                     font=("Arial", 10, "bold"),
                                     fg="white", bg="#2d2d30", 
                                     labelanchor="nw", padx=10, pady=10)
        advanced_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Color Mode
        mode_frame = tk.Frame(advanced_frame, bg="#2d2d30")
        mode_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(mode_frame, text="Color Mode:", fg="white", bg="#2d2d30").pack(side=tk.LEFT, padx=(0, 10))
        color_modes = ["RGB Color", "CMYK Color", "Grayscale", "Lab Color"]
        self.color_var = tk.StringVar(value="RGB Color")
        color_combo = ttk.Combobox(mode_frame, textvariable=self.color_var,
                                  values=color_modes, state="readonly", width=12)
        color_combo.pack(side=tk.LEFT)
        
        # Background Contents
        bg_frame = tk.Frame(advanced_frame, bg="#2d2d30")
        bg_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(bg_frame, text="Background Contents:", fg="white", bg="#2d2d30").pack(side=tk.LEFT, padx=(0, 10))
        bg_options = ["White", "Background Color", "Transparent", "Black"]
        self.bg_var = tk.StringVar(value="White")
        bg_combo = ttk.Combobox(bg_frame, textvariable=self.bg_var,
                               values=bg_options, state="readonly", width=15)
        bg_combo.pack(side=tk.LEFT)
        
        # Color Profile (advanced)
        profile_frame = tk.Frame(advanced_frame, bg="#2d2d30")
        profile_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(profile_frame, text="Color Profile:", fg="white", bg="#2d2d30").pack(side=tk.LEFT, padx=(0, 10))
        profiles = ["sRGB IEC61966-2.1", "Adobe RGB (1998)", "ProPhoto RGB"]
        self.profile_var = tk.StringVar(value="sRGB IEC61966-2.1")
        profile_combo = ttk.Combobox(profile_frame, textvariable=self.profile_var,
                                    values=profiles, state="readonly", width=20)
        profile_combo.pack(side=tk.LEFT)
        
        # Pixel Aspect Ratio
        pixel_frame = tk.Frame(advanced_frame, bg="#2d2d30")
        pixel_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(pixel_frame, text="Pixel Aspect Ratio:", fg="white", bg="#2d2d30").pack(side=tk.LEFT, padx=(0, 10))
        ratios = ["Square Pixels", "DVCPRO HD 1080 (1.5)", "Anamorphic 2:1 (2.0)"]
        self.ratio_var = tk.StringVar(value="Square Pixels")
        ratio_combo = ttk.Combobox(pixel_frame, textvariable=self.ratio_var,
                                  values=ratios, state="readonly", width=18)
        ratio_combo.pack(side=tk.LEFT)
    
    def create_action_buttons(self, parent):
        btn_frame = tk.Frame(parent, bg="#2d2d30")
        btn_frame.pack(fill=tk.X, pady=20)
        
        # Cancel Button
        cancel_btn = tk.Button(btn_frame, text="Cancel", width=10,
                              bg="#5a5a5a", fg="white", relief="flat",
                              command=self.cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # OK Button
        ok_btn = tk.Button(btn_frame, text="OK", width=10,
                          bg="#007acc", fg="white", relief="flat",
                          command=self.ok)
        ok_btn.pack(side=tk.RIGHT)
        
        # Set focus to OK button
        ok_btn.focus_set()
        
        # Bind Enter key to OK, Escape to Cancel
        self.bind('<Return>', lambda e: self.ok())
        self.bind('<Escape>', lambda e: self.cancel())
    
    def on_preset_change(self, event):
        preset = self.preset_var.get()
        presets = {
            "Default Photoshop Size": ("800", "600", "72"),
            "Letter": ("8.5", "11", "300", "Inches"),
            "A4": ("210", "297", "300", "mm"),
            "Web 1920x1080": ("1920", "1080", "72"),
            "Mobile 1080x1920": ("1080", "1920", "72"),
            "Instagram Post (1080x1080)": ("1080", "1080", "72")
        }
        
        if preset in presets:
            values = presets[preset]
            self.width_var.set(values[0])
            self.height_var.set(values[1])
            self.res_var.set(values[2])
            if len(values) > 3:
                self.unit_var.set(values[3])
    
    def on_unit_change(self, event):
        # Convert dimensions based on unit change
        pass
    
    def ok(self):
        try:
            self.result = {
                'width': int(self.width_var.get()),
                'height': int(self.height_var.get()),
                'resolution': int(self.res_var.get()),
                'color_mode': self.color_var.get(),
                'background': self.bg_var.get(),
                'unit': self.unit_var.get()
            }
            self.destroy()
        except ValueError:
            tk.messagebox.showerror("Error", "Please enter valid numbers for width and height")
    
    def cancel(self):
        self.result = None
        self.destroy()