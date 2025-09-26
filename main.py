# main.py - Corrected imports section
import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import numpy as np
import os
import cv2
import json

# Tool imports - CORRECTED
from tools.base_tool import BaseTool
from tools.move_tool import make_tool as make_move_tool
from app.core import AppState, ToolManager, Layer


# Main Application Class
class ImageForge:
    def __init__(self, root):
        self.root = root
        self.root.title("ImageForge - Professional Image Editor")
        self.root.geometry("1600x1000")
        self.root.configure(bg="#404040")
        
        # Initialize app state
        self.app_state = AppState(root)
        
        # Create main container
        self.main_container = tk.Frame(root, bg="#404040")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create interface components
        self.create_menu_bar()
        self.create_option_bar()
        self.create_tab_bar()
        self.create_tool_bar()
        self.create_main_content()
        self.create_layers_panel()
        
        # Initialize tool manager
        self.tool_manager = ToolManager(self.app_state)
        self.register_tools()

        self.app_state.setup_renderer(self.canvas)  # Canvas দিয়ে renderer setup
        self.app_state.renderer.fit_to_screen()
        
        # Set initial tool
        self.tool_manager.switch_tool("move")
        
        # Bind right-click event for tools
        self.bind_tool_events()
        
        # Current colors
        self.foreground_color = "black"
        self.background_color = "white"
        self.root.bind('<Configure>', self._on_window_resize)

        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-Z>', lambda e: self.redo())
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
    
    def _on_window_resize(self, event):
        """Handle main window resize"""
        # Only handle when the root window is resized (not child widgets)
        if event.widget == self.root:
            print(f"🏠 Window resized to: {event.width}x{event.height}")
            
            # Force canvas update
            self.canvas.update_idletasks()
            
            # Trigger renderer resize if image is loaded
            if (hasattr(self.app_state, 'renderer') and 
                self.app_state.renderer and 
                hasattr(self.app_state, 'original_image') and 
                self.app_state.original_image):
                
                self.app_state.renderer.fit_to_screen()

    def create_menu_bar(self):
        # Menu bar with Photoshop-like styling
        menubar = tk.Menu(self.root, tearoff=0, bg="#2d2d30", fg="#cccccc")
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg="#2d2d30", fg="#cccccc")
        file_menu.add_command(label="New...", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Browse in Bridge", command=self.browse_in_bridge)
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_command(label="Check In...", command=self.check_in)
        file_menu.add_separator()
        file_menu.add_command(label="Export", command=self.export_file)
        file_menu.add_command(label="Export As...", command=self.export_as)
        file_menu.add_command(label="Export for Web (Legacy)...", command=self.export_for_web)
        file_menu.add_separator()
        file_menu.add_command(label="Automate", command=self.automate)
        file_menu.add_command(label="Scripts", command=self.scripts)
        file_menu.add_separator()
        file_menu.add_command(label="File Info...", command=self.file_info)
        file_menu.add_command(label="Print...", command=self.print_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg="#2d2d30", fg="#cccccc")
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Shift+Z")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Copy Merged", command=self.copy_merged, accelerator="Ctrl+Shift+C")
        edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_command(label="Paste Special", command=self.paste_special)
        edit_menu.add_command(label="Clear", command=self.clear)
        edit_menu.add_separator()
        edit_menu.add_command(label="Search", command=self.search)
        edit_menu.add_separator()
        edit_menu.add_command(label="Fill...", command=self.fill)
        edit_menu.add_command(label="Stroke...", command=self.stroke)
        edit_menu.add_separator()
        edit_menu.add_command(label="Content-Aware Scale", command=self.content_aware_scale)
        edit_menu.add_command(label="Puppet Warp", command=self.puppet_warp)
        edit_menu.add_separator()
        edit_menu.add_command(label="Perspective Warp", command=self.perspective_warp)
        edit_menu.add_separator()
        edit_menu.add_command(label="Transform", command=self.transform)
        edit_menu.add_separator()
        edit_menu.add_command(label="Auto-Blend Layers", command=self.auto_blend_layers)
        edit_menu.add_command(label="Auto-Align Layers", command=self.auto_align_layers)
        edit_menu.add_separator()
        edit_menu.add_command(label="Define Brush Preset...", command=self.define_brush_preset)
        edit_menu.add_command(label="Define Pattern...", command=self.define_pattern)
        edit_menu.add_separator()
        edit_menu.add_command(label="Purge", command=self.purge)
        edit_menu.add_separator()
        edit_menu.add_command(label="Adobe PDF Presets...", command=self.adobe_pdf_presets)
        edit_menu.add_separator()
        edit_menu.add_command(label="Remote Connections...", command=self.remote_connections)
        edit_menu.add_separator()
        edit_menu.add_command(label="Preferences", command=self.preferences)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # Image menu
        image_menu = tk.Menu(menubar, tearoff=0, bg="#2d2d30", fg="#cccccc")
        image_menu.add_command(label="Mode", command=self.mode)
        image_menu.add_separator()
        image_menu.add_command(label="Adjustments", command=self.adjustments)
        image_menu.add_separator()
        image_menu.add_command(label="Auto Tone", command=self.auto_tone, accelerator="Ctrl+Shift+L")
        image_menu.add_command(label="Auto Contrast", command=self.auto_contrast, accelerator="Ctrl+Alt+Shift+L")
        image_menu.add_command(label="Auto Color", command=self.auto_color, accelerator="Ctrl+Shift+B")
        image_menu.add_separator()
        image_menu.add_command(label="Image Size...", command=self.image_size)
        image_menu.add_command(label="Canvas Size...", command=self.canvas_size)
        image_menu.add_command(label="Image Rotation", command=self.image_rotation)
        image_menu.add_separator()
        image_menu.add_command(label="Crop", command=self.crop)
        image_menu.add_command(label="Trim...", command=self.trim)
        image_menu.add_command(label="Reveal All", command=self.reveal_all)
        image_menu.add_separator()
        image_menu.add_command(label="Duplicate...", command=self.duplicate_image)
        image_menu.add_command(label="Apply Image...", command=self.apply_image)
        image_menu.add_command(label="Calculations...", command=self.calculations)
        image_menu.add_separator()
        image_menu.add_command(label="Variables", command=self.variables)
        image_menu.add_command(label="Apply Data Set...", command=self.apply_data_set)
        image_menu.add_separator()
        image_menu.add_command(label="Trap...", command=self.trap)
        menubar.add_cascade(label="Image", menu=image_menu)
        
        # Layer menu
        layer_menu = tk.Menu(menubar, tearoff=0, bg="#2d2d30", fg="#cccccc")
        layer_menu.add_command(label="New", command=self.new_layer_menu)
        def duplicate_layer(self):
            if hasattr(self, 'layers') and self.layers and self.current_layer_index < len(self.layers):
                current_layer = self.layers[self.current_layer_index]
                new_layer = current_layer.copy()
                self.layers.append(new_layer)
                self.current_layer_index = len(self.layers) - 1
                self.update_layer_listbox()
        layer_menu.add_command(label="Delete", command=self.delete_layer_menu)
        layer_menu.add_separator()
        layer_menu.add_command(label="Layer Properties...", command=self.layer_properties)
        layer_menu.add_command(label="Layer Style", command=self.layer_style)
        layer_menu.add_separator()
        layer_menu.add_command(label="New Fill Layer", command=self.new_fill_layer)
        layer_menu.add_command(label="New Adjustment Layer", command=self.new_adjustment_layer)
        layer_menu.add_separator()
        layer_menu.add_command(label="Layer Mask", command=self.layer_mask)
        layer_menu.add_command(label="Vector Mask", command=self.vector_mask)
        layer_menu.add_command(label="Create Clipping Mask", command=self.create_clipping_mask, accelerator="Ctrl+Alt+G")
        layer_menu.add_separator()
        layer_menu.add_command(label="Smart Objects", command=self.smart_objects)
        layer_menu.add_command(label="Video Layers", command=self.video_layers)
        layer_menu.add_command(label="3D Layers", command=self.three_d_layers)
        layer_menu.add_separator()
        layer_menu.add_command(label="Type", command=self.type_menu)
        layer_menu.add_separator()
        layer_menu.add_command(label="Rasterize", command=self.rasterize)
        layer_menu.add_separator()
        layer_menu.add_command(label="New Layer Based Slice", command=self.new_layer_based_slice)
        layer_menu.add_separator()
        layer_menu.add_command(label="Group Layers", command=self.group_layers, accelerator="Ctrl+G")
        layer_menu.add_command(label="Ungroup Layers", command=self.ungroup_layers, accelerator="Ctrl+Shift+G")
        layer_menu.add_separator()
        layer_menu.add_command(label="Hide Layers", command=self.hide_layers)
        layer_menu.add_command(label="Arrange", command=self.arrange_layers)
        layer_menu.add_separator()
        layer_menu.add_command(label="Merge Layers", command=self.merge_layers, accelerator="Ctrl+E")
        layer_menu.add_command(label="Merge Visible", command=self.merge_visible, accelerator="Ctrl+Shift+E")
        layer_menu.add_command(label="Flatten Image", command=self.flatten_image)
        layer_menu.add_separator()
        layer_menu.add_command(label="Matting", command=self.matting)
        menubar.add_cascade(label="Layer", menu=layer_menu)
        
        # Select menu
        select_menu = tk.Menu(menubar, tearoff=0, bg="#2d2d30", fg="#cccccc")
        select_menu.add_command(label="All", command=self.select_all, accelerator="Ctrl+A")
        select_menu.add_command(label="Deselect", command=self.deselect, accelerator="Ctrl+D")
        select_menu.add_command(label="Reselect", command=self.reselect, accelerator="Ctrl+Shift+D")
        select_menu.add_command(label="Inverse", command=self.inverse_selection, accelerator="Ctrl+Shift+I")
        select_menu.add_separator()
        select_menu.add_command(label="All Layers", command=self.select_all_layers)
        select_menu.add_command(label="Deselect Layers", command=self.deselect_layers)
        select_menu.add_separator()
        select_menu.add_command(label="Find Layers", command=self.find_layers)
        select_menu.add_separator()
        select_menu.add_command(label="Color Range...", command=self.color_range)
        select_menu.add_command(label="Focus Area...", command=self.focus_area)
        select_menu.add_separator()
        select_menu.add_command(label="Modify", command=self.modify_selection)
        select_menu.add_separator()
        select_menu.add_command(label="Grow", command=self.grow_selection)
        select_menu.add_command(label="Similar", command=self.similar_selection)
        select_menu.add_separator()
        select_menu.add_command(label="Transform Selection", command=self.transform_selection)
        select_menu.add_separator()
        select_menu.add_command(label="Edit in Quick Mask Mode", command=self.quick_mask_mode, accelerator="Q")
        select_menu.add_command(label="Load Selection...", command=self.load_selection)
        select_menu.add_command(label="Save Selection...", command=self.save_selection)
        menubar.add_cascade(label="Select", menu=select_menu)
        
        # Filter menu
        filter_menu = tk.Menu(menubar, tearoff=0, bg="#2d2d30", fg="#cccccc")
        filter_menu.add_command(label="Last Filter", command=self.last_filter, accelerator="Ctrl+F")
        filter_menu.add_command(label="Convert for Smart Filters", command=self.convert_for_smart_filters)
        filter_menu.add_separator()
        filter_menu.add_command(label="Filter Gallery...", command=self.filter_gallery)
        filter_menu.add_command(label="Adaptive Wide Angle...", command=self.adaptive_wide_angle)
        filter_menu.add_command(label="Camera Raw Filter...", command=self.camera_raw_filter, accelerator="Ctrl+Shift+A")
        filter_menu.add_command(label="Lens Correction...", command=self.lens_correction)
        filter_menu.add_command(label="Liquify...", command=self.liquify, accelerator="Ctrl+Shift+X")
        filter_menu.add_command(label="Oil Paint...", command=self.oil_paint)
        filter_menu.add_command(label="Vanishing Point...", command=self.vanishing_point, accelerator="Ctrl+Alt+V")
        filter_menu.add_separator()
        filter_menu.add_command(label="3D", command=self.three_d_filters)
        filter_menu.add_command(label="Blur", command=self.blur_filters)
        filter_menu.add_command(label="Distort", command=self.distort_filters)
        filter_menu.add_command(label="Noise", command=self.noise_filters)
        filter_menu.add_command(label="Pixelate", command=self.pixelate_filters)
        filter_menu.add_command(label="Render", command=self.render_filters)
        filter_menu.add_command(label="Sharpen", command=self.sharpen_filters)
        filter_menu.add_command(label="Stylize", command=self.stylize_filters)
        filter_menu.add_command(label="Texture", command=self.texture_filters)
        filter_menu.add_command(label="Video", command=self.video_filters)
        filter_menu.add_command(label="Other", command=self.other_filters)
        filter_menu.add_command(label="Digimarc", command=self.digimarc_filters)
        menubar.add_cascade(label="Filter", menu=filter_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg="#2d2d30", fg="#cccccc")
        view_menu.add_command(label="Proof Setup", command=self.proof_setup)
        view_menu.add_command(label="Proof Colors", command=self.proof_colors, accelerator="Ctrl+Y")
        view_menu.add_command(label="Gamut Warning", command=self.gamut_warning, accelerator="Ctrl+Shift+Y")
        view_menu.add_separator()
        view_menu.add_command(label="Pixel Aspect Ratio", command=self.pixel_aspect_ratio)
        view_menu.add_separator()
        view_menu.add_command(label="32-bit Preview Options", command=self.thirty_two_bit_preview)
        view_menu.add_separator()
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Fit on Screen", command=self.fit_on_screen, accelerator="Ctrl+0")
        view_menu.add_command(label="Actual Pixels", command=self.actual_pixels, accelerator="Ctrl+1")
        view_menu.add_command(label="Print Size", command=self.print_size)
        view_menu.add_separator()
        view_menu.add_command(label="Screen Mode", command=self.screen_mode)
        view_menu.add_separator()
        view_menu.add_command(label="Extras", command=self.extras, accelerator="Ctrl+H")
        view_menu.add_command(label="Show", command=self.show_menu)
        view_menu.add_command(label="Rulers", command=self.toggle_rulers, accelerator="Ctrl+R")
        view_menu.add_command(label="Snap", command=self.toggle_snap, accelerator="Ctrl+;")
        view_menu.add_command(label="Snap To", command=self.snap_to)
        view_menu.add_command(label="Lock Guides", command=self.lock_guides, accelerator="Ctrl+Alt+;")
        view_menu.add_command(label="New Guide...", command=self.new_guide)
        view_menu.add_command(label="Clear Guides", command=self.clear_guides)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Window menu
        window_menu = tk.Menu(menubar, tearoff=0, bg="#2d2d30", fg="#cccccc")
        window_menu.add_command(label="Arrange", command=self.arrange_windows)
        window_menu.add_command(label="Workspace", command=self.workspace_menu)
        window_menu.add_separator()
        window_menu.add_command(label="Actions", command=self.toggle_actions, accelerator="Alt+F9")
        window_menu.add_command(label="Adjustments", command=self.toggle_adjustments)
        window_menu.add_command(label="Brush", command=self.toggle_brush)
        window_menu.add_command(label="Brush Presets", command=self.toggle_brush_presets)
        window_menu.add_command(label="Channels", command=self.toggle_channels)
        window_menu.add_command(label="Character", command=self.toggle_character)
        window_menu.add_command(label="Color", command=self.toggle_color, accelerator="F6")
        window_menu.add_command(label="Histogram", command=self.toggle_histogram)
        window_menu.add_command(label="History", command=self.toggle_history, accelerator="F9")
        window_menu.add_command(label="Info", command=self.toggle_info, accelerator="F8")
        window_menu.add_command(label="Layer Comps", command=self.toggle_layer_comps)
        window_menu.add_command(label="Layers", command=self.toggle_layers, accelerator="F7")
        window_menu.add_command(label="Navigator", command=self.toggle_navigator)
        window_menu.add_command(label="Options", command=self.toggle_options)
        window_menu.add_command(label="Paragraph", command=self.toggle_paragraph)
        window_menu.add_command(label="Paths", command=self.toggle_paths, accelerator="Shift+F11")
        window_menu.add_command(label="Properties", command=self.toggle_properties)
        window_menu.add_command(label="Styles", command=self.toggle_styles)
        window_menu.add_command(label="Swatches", command=self.toggle_swatches)
        window_menu.add_command(label="Timeline", command=self.toggle_timeline)
        window_menu.add_command(label="Tool Presets", command=self.toggle_tool_presets)
        window_menu.add_command(label="Tools", command=self.toggle_tools)
        window_menu.add_separator()
        window_menu.add_command(label="Reset Panels", command=self.reset_panels)
        menubar.add_cascade(label="Window", menu=window_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg="#2d2d30", fg="#cccccc")
        help_menu.add_command(label="ImageForge Help", command=self.help, accelerator="F1")
        help_menu.add_command(label="About ImageForge", command=self.about)
        help_menu.add_separator()
        help_menu.add_command(label="System Info", command=self.system_info)
        help_menu.add_command(label="Updates", command=self.updates)
        help_menu.add_command(label="Manage Extensions", command=self.manage_extensions)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_option_bar(self):
        # Option bar (below menu bar)
        self.option_bar = tk.Frame(self.main_container, bg="#4d4d4d", height=40)
        self.option_bar.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)
        
        # Tool name display
        self.tool_name_label = tk.Label(self.option_bar, text="Move Tool", bg="#4d4d4d", fg="white", font=("Arial", 10))
        self.tool_name_label.pack(side=tk.LEFT, padx=10)
        
        # This will be populated with tool-specific options
        self.options_frame = tk.Frame(self.option_bar, bg="#4d4d4d")
        self.options_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Show default options for move tool
        self.show_tool_options("move")

    def create_tab_bar(self):
        """Create tab bar for multiple document support - IMPROVED"""
        self.tab_bar = tk.Frame(self.main_container, bg="#2d2d30", height=35)  # Darker background
        self.tab_bar.pack(side=tk.TOP, fill=tk.X, after=self.option_bar)
        self.tab_bar.pack_propagate(False)
        
        self.tab_container = tk.Frame(self.tab_bar, bg="#2d2d30")
        self.tab_container.pack(fill=tk.X, padx=5, pady=2)
        
        self.tab_buttons = {}
        self.update_tab_bar()

    def update_tab_bar(self):
        """Simpler version with visible close button"""
        # Clear existing tabs
        for widget in self.tab_container.winfo_children():
            widget.destroy()
        
        self.tab_buttons = {}
        
        # Create tabs for each document
        for i, doc in enumerate(self.app_state.documents):
            is_active = (i == self.app_state.active_document_index)
            tab_bg = "#5a5a5a" if is_active else "#3c3c3c"
            
            # Create tab frame
            tab_frame = tk.Frame(self.tab_container, bg=tab_bg, relief="sunken" if is_active else "raised", 
                                borderwidth=1, height=30)
            tab_frame.pack(side=tk.LEFT, padx=(0, 1))
            
            # Filename label
            display_name = doc.filename
            if len(display_name) > 20:
                display_name = display_name[:17] + "..."
            
            tab_label = tk.Label(tab_frame, text=display_name, bg=tab_bg, 
                                fg="white", padx=10, pady=5, font=("Arial", 9))
            tab_label.pack(side=tk.LEFT)
            
            self.create_tooltip(tab_label, doc.filename)
            
            # **SIMPLE VISIBLE CLOSE BUTTON**
            close_btn = tk.Button(tab_frame, text="X", 
                                bg="#ff4444", fg="white",  # Red background, white text
                                relief="raised", borderwidth=1,
                                font=("Arial", 8, "bold"),
                                width=2, height=1,
                                command=lambda idx=i: self.close_tab(idx))
            close_btn.pack(side=tk.RIGHT, padx=5, pady=2)
            
            # Bind events
            tab_label.bind("<Button-1>", lambda e, idx=i: self.switch_tab(idx))
            tab_frame.bind("<Button-1>", lambda e, idx=i: self.switch_tab(idx))
            
            self.tab_buttons[i] = (tab_frame, tab_label, close_btn)
        
        # Show/hide tab bar
        if len(self.app_state.documents) == 0:
            self.tab_bar.pack_forget()
        else:
            self.tab_bar.pack(side=tk.TOP, fill=tk.X, after=self.option_bar)

    def switch_tab(self, index):
        """Switch to different tab/document - FIXED VERSION"""
        if 0 <= index < len(self.app_state.documents):
            print(f"🔄 Switching to tab {index}")
            
            self.app_state.active_document_index = index
            self.update_tab_bar()
            
            # Update window title
            active_doc = self.app_state.active_document
            if active_doc:
                self.root.title(f"ImageForge - {active_doc.filename}")
            
            # FORCE RENDER with proper cleanup
            if self.app_state.renderer:
                # Clear canvas first
                self.app_state.renderer.canvas.delete("all")
                
                # Force render
                self.app_state.renderer.render(force=True)
                
                # Extra updates to ensure display
                self.app_state.renderer.canvas.update_idletasks()
                self.canvas.update_idletasks()
            
            print(f"✅ Switched to tab {index}")

    def close_tab(self, index):
        """Close a tab/document - COMPLETELY FIXED VERSION"""
        if 0 <= index < len(self.app_state.documents):
            print(f"🗑️ Closing tab {index}, total docs: {len(self.app_state.documents)}")
            
            # Store the current active index before closing
            was_active = (index == self.app_state.active_document_index)
            
            # Close the document
            self.app_state.close_document(index)
            
            # Update tab bar FIRST
            self.update_tab_bar()
            
            # Update window title
            if self.app_state.active_document:
                self.root.title(f"ImageForge - {self.app_state.active_document.filename}")
            else:
                self.root.title("ImageForge - Professional Image Editor")
            
            # FORCE CANVAS UPDATE - This is the key fix!
            if self.app_state.renderer:
                # Clear canvas completely
                self.app_state.renderer.canvas.delete("all")
                
                if self.app_state.active_document:
                    print(f"🔄 Switching to document: {self.app_state.active_document.filename}")
                    # Force render the active document
                    self.app_state.renderer.render(force=True)
                else:
                    print("🔄 No documents left, showing placeholder")
                    # Show placeholder with force
                    self.app_state.renderer._show_placeholder()
                
                # Extra force updates
                self.app_state.renderer.canvas.update_idletasks()
                self.canvas.update_idletasks()
            
            print(f"✅ Tab closed. Active document index: {self.app_state.active_document_index}")
            return True
        return False
    
    def create_tooltip(self, widget, text):
        """Create a tooltip for widgets"""
        def on_enter(event):
            # Create tooltip window
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            
            # Create toplevel window
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            label = tk.Label(self.tooltip, text=text, justify='left',
                            background="#ffffe0", relief='solid', borderwidth=1,
                            font=("Arial", 10))
            label.pack(ipadx=1)
        
        def on_leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def create_tool_bar(self):
        # Tool bar (left side) - Smart tool bar with nested tools
        self.tool_bar = tk.Frame(self.main_container, bg="#404040", width=70)
        self.tool_bar.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        self.tool_bar.pack_propagate(False)
        
        # Tool groups with nested tools - Complete list as requested
        tool_groups = [
            # Format: (main_icon, main_tool_id, group_name, [(tool_icon, tool_name, tool_id), ...])
            ("🖱", "move", "Move Tool", [("🖱", "Move Tool", "move")]),
            
            ("⬜", "rect_marquee", "Selection Tools", [
                ("⬜", "Rectangular Marquee", "rect_marquee"),
                ("⭕", "Elliptical Marquee", "elliptical_marquee"),
                ("🔰", "Lasso Tool", "lasso"),
                ("🔷", "Polygonal Lasso", "polygonal_lasso"),
                ("🧲", "Magnetic Lasso", "magnetic_lasso"),
                ("✨", "Magic Selection", "magic_selection")
            ]),
            
            ("✂️", "crop", "Crop Tools", [
                ("✂️", "Crop Tool", "crop"),
                ("🔳", "Perspective Crop", "perspective_crop")
            ]),
            
            ("🖌", "brush", "Brush Tools", [
                ("🖌", "Brush Tool", "brush"),
                ("✏️", "Pencil Tool", "pencil")
            ]),
            
            ("🔄", "clone_stamp", "Clone Tools", [
                ("🔄", "Clone Stamp", "clone_stamp"),
                ("❤️", "Healing Brush", "healing_brush"),
                ("🔲", "Patch Tool", "patch_tool")
            ]),
            
            ("🧽", "eraser", "Eraser Tools", [
                ("🧽", "Eraser Tool", "eraser"),
                ("🧹", "Background Eraser", "background_eraser"),
                ("🔮", "Magic Eraser", "magic_eraser")
            ]),
            
            ("🌈", "gradient", "Gradient Tools", [
                ("🌈", "Gradient Tool", "gradient"),
                ("🪣", "Paint Bucket", "paint_bucket")
            ]),
            
            ("🌀", "blur", "Blur Tools", [
                ("🌀", "Blur Tool", "blur"),
                ("⚡", "Sharpen Tool", "sharpen"),
                ("👆", "Smudge Tool", "smudge")
            ]),
            
            ("🌞", "dodge", "Toning Tools", [
                ("🌞", "Dodge Tool", "dodge"),
                ("🌚", "Burn Tool", "burn"),
                ("🧽", "Sponge Tool", "sponge")
            ]),
            
            ("🖊", "pen", "Pen Tools", [
                ("🖊", "Pen Tool", "pen"),
                ("✏️", "Freeform Pen", "freeform_pen"),
                ("➕", "Add Anchor Point", "add_anchor"),
                ("➖", "Delete Anchor Point", "delete_anchor")
            ]),
            
            ("T", "horizontal_text", "Text Tools", [
                ("T", "Horizontal Text", "horizontal_text"),
                ("T", "Vertical Text", "vertical_text"),
                ("🔠", "Horizontal Type Mask", "horizontal_mask"),
                ("🔡", "Vertical Type Mask", "vertical_mask")
            ]),
            
            ("👁", "eyedropper", "Eyedropper Tool", [("👁", "Eyedropper Tool", "eyedropper")]),
            
            ("🔍", "zoom", "Zoom Tool", [("🔍", "Zoom Tool", "zoom")])
        ]
        
        # Create tool buttons
        self.tool_buttons = {}
        self.tool_groups = {}
        self.current_tools = {}  # Track current tool in each group
        
        for main_icon, main_tool_id, group_name, tools in tool_groups:
            # Create button frame
            btn_frame = tk.Frame(self.tool_bar, bg="#404040")
            btn_frame.pack(pady=2)
            
            # Create button with visual indicator for nested tools
            if len(tools) > 1:
                # Button with dropdown indicator
                btn_container = tk.Frame(btn_frame, bg="#404040")
                btn_container.pack()
                
                btn = tk.Button(btn_container, text=main_icon, width=3, height=2, 
                               bg="#404040", fg="white", relief="flat",
                               command=lambda tid=main_tool_id: self.switch_tool(tid))
                btn.pack(side=tk.LEFT)
                
                # Dropdown indicator (small triangle)
                indicator = tk.Label(btn_container, text="▼", font=("Arial", 6), 
                                    bg="#404040", fg="white")
                indicator.pack(side=tk.RIGHT, padx=(0, 2))
                
                # Store the current tool for this group
                self.current_tools[main_tool_id] = tools[0][2]  # First tool in group
            else:
                # Single tool button
                btn = tk.Button(btn_frame, text=main_icon, width=3, height=2, 
                               bg="#404040", fg="white", relief="flat",
                               command=lambda tid=main_tool_id: self.switch_tool(tid))
                btn.pack()
                
                # Store the current tool for this group
                self.current_tools[main_tool_id] = tools[0][2]  # The only tool
            
            # Store button reference
            self.tool_buttons[main_tool_id] = btn
            self.tool_groups[main_tool_id] = tools
            
            # Add right-click menu for groups with multiple tools
            if len(tools) > 1:
                btn.bind("<Button-3>", lambda e, g=group_name, t=tools, gtid=main_tool_id: 
                        self.show_tool_group_menu(e, g, t, gtid))
        
        # Add color swatches at the bottom (Photoshop style)
        color_frame = tk.Frame(self.tool_bar, bg="#404040")
        color_frame.pack(side=tk.BOTTOM, pady=20)
        
        # Foreground color (top square)
        self.fg_color_btn = tk.Button(color_frame, width=3, height=1, bg="black", relief="solid",
                                     command=lambda: self.choose_color("foreground"))
        self.fg_color_btn.pack(pady=2)
        
        # Background color (bottom square)
        self.bg_color_btn = tk.Button(color_frame, width=3, height=1, bg="white", relief="solid",
                                     command=lambda: self.choose_color("background"))
        self.bg_color_btn.pack(pady=2)
        
        # Swap colors button
        swap_btn = tk.Button(color_frame, text="↔", width=3, height=1, 
                            bg="#404040", fg="white", relief="flat",
                            command=self.swap_colors)
        swap_btn.pack(pady=2)
        
        # Default colors button
        default_btn = tk.Button(color_frame, text="D", width=3, height=1, 
                               bg="#404040", fg="white", relief="flat",
                               command=self.set_default_colors)
        default_btn.pack(pady=2)
    
    def create_main_content(self):
        # Main content area (canvas only)
        self.canvas_frame = tk.Frame(self.main_container, bg="#404040")
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create canvas with scrollbars
        hscrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, bg="#404040")
        hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        vscrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, bg="#404040")
        vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas
        self.canvas = tk.Canvas(self.canvas_frame, bg="#2d2d30", 
                               yscrollcommand=vscrollbar.set,
                               xscrollcommand=hscrollbar.set,
                               highlightthickness=0)
        
        vscrollbar.config(command=self.canvas.yview)
        hscrollbar.config(command=self.canvas.xview)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Set canvas in app state
        self.app_state.set_canvas(self.canvas)
        
        # Add a centered placeholder
        self.add_centered_placeholder()
        
        # Bind events
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
    
    def create_layers_panel(self):
        # Layers panel (right side)
        self.layers_panel = tk.Frame(self.main_container, width=250, bg="#404040")
        self.layers_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=0, pady=0)
        self.layers_panel.pack_propagate(False)
        
        # Panel title
        title_bar = tk.Frame(self.layers_panel, bg="#2d2d30", height=25)
        title_bar.pack(fill=tk.X)
        
        title_label = tk.Label(title_bar, text="Layers", bg="#2d2d30", fg="white")
        title_label.pack(side=tk.LEFT, padx=5)
        
        # Blend mode dropdown
        blend_frame = tk.Frame(self.layers_panel, bg="#404040")
        blend_frame.pack(fill=tk.X, padx=5, pady=5)
        
        blend_label = tk.Label(blend_frame, text="Mode:", bg="#404040", fg="white")
        blend_label.pack(side=tk.LEFT)
        
        blend_modes = ["Normal", "Multiply", "Screen", "Overlay", "Soft Light", "Hard Light", 
                      "Color Dodge", "Color Burn", "Darken", "Lighten", "Difference", "Exclusion",
                      "Hue", "Saturation", "Color", "Luminosity"]
        self.blend_var = tk.StringVar(value="Normal")
        blend_dropdown = ttk.Combobox(blend_frame, textvariable=self.blend_var, 
                                     values=blend_modes, state="readonly", width=12)
        blend_dropdown.pack(side=tk.LEFT, padx=5)
        blend_dropdown.bind("<<ComboboxSelected>>", self.on_blend_mode_change)
        
        # Opacity slider
        opacity_frame = tk.Frame(self.layers_panel, bg="#404040")
        opacity_frame.pack(fill=tk.X, padx=5, pady=5)
        
        opacity_label = tk.Label(opacity_frame, text="Opacity:", bg="#404040", fg="white")
        opacity_label.pack(side=tk.LEFT)
        
        self.opacity_var = tk.IntVar(value=100)
        opacity_slider = tk.Scale(opacity_frame, from_=0, to=100, variable=self.opacity_var,
                                 orient=tk.HORIZONTAL, length=150, bg="#404040",
                                 highlightthickness=0, showvalue=False)
        opacity_slider.pack(side=tk.LEFT, padx=5)
        opacity_slider.bind("<B1-Motion>", self.on_opacity_change)
        
        opacity_value = tk.Label(opacity_frame, textvariable=self.opacity_var, 
                                bg="#404040", fg="white", width=3)
        opacity_value.pack(side=tk.LEFT)
        
        # Lock options
        lock_frame = tk.Frame(self.layers_panel, bg="#404040")
        lock_frame.pack(fill=tk.X, padx=5, pady=5)
        
        lock_buttons = []
        lock_icons = ["🔒", "🎨", "📌", "🔒"]  # Lock position, lock pixels, lock all
        for icon in lock_icons:
            btn = tk.Button(lock_frame, text=icon, width=2, height=1, 
                           bg="#404040", fg="white", relief="flat")
            btn.pack(side=tk.LEFT, padx=2)
            lock_buttons.append(btn)
        
        # Layers list with scrollbar
        layers_list_frame = tk.Frame(self.layers_panel, bg="#2d2d30")
        layers_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Layers scrollbar
        layer_scrollbar = tk.Scrollbar(layers_list_frame, bg="#404040")
        layer_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Layers listbox
        self.layers_listbox = tk.Listbox(layers_list_frame, yscrollcommand=layer_scrollbar.set,
                                        bg="#2d2d30", fg="#cccccc", selectmode=tk.SINGLE,
                                        highlightthickness=0, borderwidth=0, 
                                        font=("Arial", 10))
        layer_scrollbar.config(command=self.layers_listbox.yview)
        
        self.layers_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.layers_listbox.bind("<<ListboxSelect>>", self.on_layer_select)
        
        # Add some sample layers
        self.add_sample_layers()
        
        # Layer controls
        controls_frame = tk.Frame(self.layers_panel, bg="#404040")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Layer control buttons
        buttons = [
            ("👁", self.toggle_layer_visibility),
            ("📄", self.new_layer),
            ("🗑️", self.delete_layer),
            ("📂", self.new_group),
            ("🔗", self.link_layers),
        ]
        
        for icon, command in buttons:
            btn = tk.Button(controls_frame, text=icon, width=2, height=1, 
                           bg="#404040", fg="white", relief="flat", command=command)
            btn.pack(side=tk.LEFT, padx=2)
    
    def add_sample_layers(self):
        # Add some sample layers
        self.layers_listbox.insert(0, "Background")
        self.layers_listbox.insert(1, "Layer 1")
        self.layers_listbox.insert(2, "Layer 2")
        self.layers_listbox.selection_set(0)  # Select the first layer
        
        # Create layer objects
        self.app_state.layers = [
            Layer("Background", 800, 600),
            Layer("Layer 1", 800, 600),
            Layer("Layer 2", 800, 600)
        ]
        self.app_state.active_layer_index = 0
    
    def add_centered_placeholder(self):
        # Remove existing placeholder if any
        if hasattr(self, 'placeholder'):
            self.canvas.delete(self.placeholder)
            self.canvas.delete(self.placeholder_text)
        
        # Get current canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Use reasonable defaults if canvas is too small
        if canvas_width < 100:
            canvas_width = 800
        if canvas_height < 100:
            canvas_height = 600
        
        # Calculate centered position
        placeholder_width = min(450, canvas_width - 100)
        placeholder_height = min(350, canvas_height - 100)
        x1 = (canvas_width - placeholder_width) / 2
        y1 = (canvas_height - placeholder_height) / 2
        x2 = x1 + placeholder_width
        y2 = y1 + placeholder_height
        

    
    def register_tools(self):
        # Register tools here
        self.tool_manager.register_tool("move", make_move_tool)
        
        # ADD BRUSH TOOL
        from tools.brush import make_tool as make_brush_tool
        self.tool_manager.register_tool("brush", make_brush_tool)
        
        # Add more tools as we implement them
            
    
    def bind_tool_events(self):
        # Bind right-click event for canvas
        self.canvas.bind("<Button-3>", self.on_right_click)
    
    def switch_tool(self, tool_id):
        self.tool_manager.switch_tool(tool_id)
        self.show_tool_options(tool_id)
        
        # Update tool name in option bar
        for group_id, tools in self.tool_groups.items():
            for icon, name, tid in tools:
                if tid == tool_id:
                    self.tool_name_label.config(text=name)
                    
                    # Update the button icon if this is a nested tool
                    if len(tools) > 1 and group_id in self.tool_buttons:
                        # Change the main button to show the selected tool's icon
                        self.tool_buttons[group_id].config(text=icon)
                        self.current_tools[group_id] = tool_id
                    break
        
        # Highlight the active tool button
        for tid, btn in self.tool_buttons.items():
            if tid == tool_id or self.current_tools.get(tid) == tool_id:
                btn.config(bg="#2d2d30", relief="sunken")
            else:
                btn.config(bg="#404040", relief="flat")
    
    def show_tool_options(self, tool_id):
        # Clear existing options
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        
        # Add tool-specific options based on the selected tool
        if tool_id == "move":
            # Move tool options
            auto_select = tk.Checkbutton(self.options_frame, text="Auto-Select", 
                                        bg="#4d4d4d", fg="white", selectcolor="#2d2d30")
            auto_select.pack(side=tk.LEFT, padx=5)
            
            tk.Label(self.options_frame, text="Show Transform Controls", 
                    bg="#4d4d4d", fg="white").pack(side=tk.LEFT, padx=20)
            
            transform_ctl = tk.Checkbutton(self.options_frame, bg="#4d4d4d", 
                                          fg="white", selectcolor="#2d2d30")
            transform_ctl.pack(side=tk.LEFT, padx=5)
        
        elif tool_id == "rect_marquee":
            # Marquee tool options
            mode_var = tk.StringVar(value="New Selection")
            mode_dropdown = ttk.Combobox(self.options_frame, textvariable=mode_var, 
                                        values=["New Selection", "Add to Selection", "Subtract from Selection", "Intersect with Selection"],
                                        state="readonly", width=16)
            mode_dropdown.pack(side=tk.LEFT, padx=5)
            
            tk.Label(self.options_frame, text="Feather:", bg="#4d4d4d", fg="white").pack(side=tk.LEFT, padx=(20, 5))
            feather_var = tk.StringVar(value="0 px")
            feather_entry = tk.Entry(self.options_frame, textvariable=feather_var, width=6, bg="#3c3c3c", fg="white")
            feather_entry.pack(side=tk.LEFT, padx=5)
            
            anti_alias = tk.Checkbutton(self.options_frame, text="Anti-alias", 
                                       bg="#4d4d4d", fg="white", selectcolor="#2d2d30")
            anti_alias.pack(side=tk.LEFT, padx=20)
    
    def show_tool_group_menu(self, event, group_name, tools, group_tool_id):
        # Create context menu for tool group
        context_menu = tk.Menu(self.root, tearoff=0, bg="#2d2d30", fg="white")
        
        # Add tools to the menu
        for icon, name, tool_id in tools:
            context_menu.add_command(label=f"{icon} {name}", 
                                    command=lambda tid=tool_id: self.switch_tool(tid))
        
        # Display the context menu
        context_menu.post(event.x_root, event.y_root)
    
    def choose_color(self, which):
        # Open color picker dialog (Photoshop style)
        color = colorchooser.askcolor(title=f"Choose {which} Color", 
                                     initialcolor=self.foreground_color if which == "foreground" else self.background_color)
        if color[1]:
            if which == "foreground":
                self.foreground_color = color[1]
                self.fg_color_btn.config(bg=color[1])
            else:
                self.background_color = color[1]
                self.bg_color_btn.config(bg=color[1])
    
    def swap_colors(self):
        # Swap foreground and background colors (Photoshop style)
        fg_color = self.fg_color_btn.cget("bg")
        bg_color = self.bg_color_btn.cget("bg")
        
        self.fg_color_btn.config(bg=bg_color)
        self.bg_color_btn.config(bg=fg_color)
        
        self.foreground_color, self.background_color = self.background_color, self.foreground_color
    
    def set_default_colors(self):
        # Set default colors (black foreground, white background) - Photoshop style
        self.fg_color_btn.config(bg="black")
        self.bg_color_btn.config(bg="white")
        self.foreground_color = "black"
        self.background_color = "white"
    
    def on_canvas_resize(self, event):
        # Recenter placeholder when canvas is resized
        self.add_centered_placeholder()
    
    def on_layer_select(self, event):
        selection = self.layers_listbox.curselection()
        if selection:
            self.app_state.active_layer_index = selection[0]
            # Update layer properties in the UI
            if self.app_state.active_layer_index < len(self.app_state.layers):
                layer = self.app_state.layers[self.app_state.active_layer_index]
                self.blend_var.set(layer.blend_mode)
                self.opacity_var.set(int(layer.opacity * 100))
    
    def on_blend_mode_change(self, event):
        if self.app_state.active_layer_index >= 0 and self.app_state.active_layer_index < len(self.app_state.layers):
            layer = self.app_state.layers[self.app_state.active_layer_index]
            layer.blend_mode = self.blend_var.get()
    
    def on_opacity_change(self, event):
        if self.app_state.active_layer_index >= 0 and self.app_state.active_layer_index < len(self.app_state.layers):
            layer = self.app_state.layers[self.app_state.active_layer_index]
            layer.opacity = self.opacity_var.get() / 100.0
    
    def toggle_layer_visibility(self):
        selection = self.layers_listbox.curselection()
        if selection and selection[0] < len(self.app_state.layers):
            layer = self.app_state.layers[selection[0]]
            layer.visible = not layer.visible
            # Update the layer display (you would update the canvas here)
    
    def new_layer(self):
        layer_name = f"Layer {len(self.app_state.layers)}"
        new_layer = Layer(layer_name, 800, 600)
        self.app_state.layers.append(new_layer)
        self.layers_listbox.insert(tk.END, layer_name)
        self.layers_listbox.selection_clear(0, tk.END)
        self.layers_listbox.selection_set(tk.END)
        self.app_state.active_layer_index = len(self.app_state.layers) - 1
    
    def delete_layer(self):
        selection = self.layers_listbox.curselection()
        if selection and selection[0] < len(self.app_state.layers):
            if len(self.app_state.layers) > 1:  # Don't delete the last layer
                self.app_state.layers.pop(selection[0])
                self.layers_listbox.delete(selection[0])
                if self.app_state.active_layer_index >= len(self.app_state.layers):
                    self.app_state.active_layer_index = len(self.app_state.layers) - 1
                if self.app_state.active_layer_index >= 0:
                    self.layers_listbox.selection_set(self.app_state.active_layer_index)
    
    def new_group(self):
        group_name = f"Group {len(self.app_state.layers)}"
        self.layers_listbox.insert(tk.END, group_name)
        # In a full implementation, you would create a layer group object
    
    def link_layers(self):
        # Link selected layers
        selection = self.layers_listbox.curselection()
        if len(selection) > 1:
            print(f"Linking {len(selection)} layers")
    
    def on_right_click(self, event):
        # Create context menu based on active tool
        context_menu = tk.Menu(self.root, tearoff=0, bg="#2d2d30", fg="white")
        
        # Add tool-specific context menu items
        if self.app_state.active_tool and hasattr(self.app_state.active_tool, 'get_context_menu'):
            menu_items = self.app_state.active_tool.get_context_menu()
            for label, command in menu_items:
                if label == "---":
                    context_menu.add_separator()
                else:
                    context_menu.add_command(label=label, command=command)
        
        # Display the context menu
        context_menu.post(event.x_root, event.y_root)
    
    def on_mouse_down(self, event):
        if self.app_state.active_tool:
            modifiers = {
                "shift": (event.state & 0x1) != 0,
                "ctrl": (event.state & 0x4) != 0,
                "alt": (event.state & 0x8) != 0
            }
            self.app_state.active_tool.on_mouse_down(event.x, event.y, modifiers)
    
    def on_mouse_move(self, event):
        if self.app_state.active_tool:
            modifiers = {
                "shift": (event.state & 0x1) != 0,
                "ctrl": (event.state & 0x4) != 0,
                "alt": (event.state & 0x8) != 0
            }
            self.app_state.active_tool.on_mouse_move(event.x, event.y, modifiers)
    
    def on_mouse_up(self, event):
        if self.app_state.active_tool:
            modifiers = {
                "shift": (event.state & 0x1) != 0,
                "ctrl": (event.state & 0x4) != 0,
                "alt": (event.state & 0x8) != 0
            }
            self.app_state.active_tool.on_mouse_up(event.x, event.y, modifiers)
    
    def on_mouse_wheel(self, event):
        if self.app_state.active_tool and hasattr(self.app_state.active_tool, 'on_mouse_wheel'):
            self.app_state.active_tool.on_mouse_wheel(event)
    
    # Menu command methods (simplified implementations)
    # main.py এর new_file method পরিবর্তন করুন:
    def new_file(self):
        from dialogs.new_file_dialog import NewFileDialog
        
        dialog = NewFileDialog(self.root, self)
        self.root.wait_window(dialog)
        
        if dialog.result:
            result = dialog.result
            print(f"📄 Creating new document: {result['width']}x{result['height']}")
            
            # Create new document with the specified parameters
            doc = self.app_state.create_new_document(result['width'], result['height'])
            
            # Update UI
            self.update_tab_bar()
            
            # Render the new document
            if self.app_state.renderer:
                self.app_state.renderer.render(force=True)
            
            self.root.title(f"ImageForge - {doc.filename}")
    

    # In main.py, update the open_file method:

    def open_file(self): 
        filename = filedialog.askopenfilename(
            title="Open Image", 
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff")]
        )
        if filename:
            print(f"📁 Opening: {filename}")
            
            try:
                # Load image
                new_image = Image.open(filename).convert("RGBA")
                
                # Create new document using app state
                doc = self.app_state.open_document(filename, new_image)
                
                # Update UI
                self.update_tab_bar()
                
                # Render the document
                if self.app_state.renderer:
                    self.app_state.renderer.render(force=True)
                
                self.root.title(f"ImageForge - {filename}")
                print("✅ Document opened successfully")
                
            except Exception as e:
                print(f"❌ Error opening file: {e}")
                messagebox.showerror("Error", f"Could not open file: {e}")
    
    def save_file(self): 
        print("Save file command")
    
    def save_as_file(self): 
        print("Save as file command")
    
    # main.py-এ শুধু এই undo/redo methods গুলো রাখুন:

    def undo(self):
        print("🔄 Undo triggered")
        
        if (hasattr(self.app_state, 'history_manager') and 
            hasattr(self.app_state, 'original_image') and
            self.app_state.original_image):
            
            new_image, success = self.app_state.history_manager.undo(self.app_state.original_image)
            
            if success:
                self.app_state.original_image = new_image
                if hasattr(self.app_state, 'renderer'):
                    self.app_state.renderer.render(force=True)
                print("✅ Undo completed")
            else:
                print("❌ Nothing to undo")
        else:
            print("❌ Cannot undo")

    def redo(self):
        print("🔄 Redo triggered")
        
        if (hasattr(self.app_state, 'history_manager') and 
            hasattr(self.app_state, 'original_image') and
            self.app_state.original_image):
            
            new_image, success = self.app_state.history_manager.redo(self.app_state.original_image)
            
            if success:
                self.app_state.original_image = new_image
                if hasattr(self.app_state, 'renderer'):
                    self.app_state.renderer.render(force=True)
                print("✅ Redo completed")
            else:
                print("❌ Nothing to redo")
        else:
            print("❌ Cannot redo")

    def cut(self): print("Cut command")
    def copy(self): print("Copy command")
    def paste(self): print("Paste command")
    
    # Placeholder methods for all menu commands
    def browse_in_bridge(self): print("Browse in Bridge")
    def check_in(self): print("Check In")
    def export_file(self): print("Export")
    def export_as(self): print("Export As")
    def export_for_web(self): print("Export for Web")
    def automate(self): print("Automate")
    def scripts(self): print("Scripts")
    def file_info(self): print("File Info")
    def print_file(self): print("Print")
    def copy_merged(self): print("Copy Merged")
    def paste_special(self): print("Paste Special")
    def clear(self): print("Clear")
    def search(self): print("Search")
    def fill(self): print("Fill")
    def stroke(self): print("Stroke")
    def content_aware_scale(self): print("Content-Aware Scale")
    def puppet_warp(self): print("Puppet Warp")
    def perspective_warp(self): print("Perspective Warp")
    def transform(self): print("Transform")
    def auto_blend_layers(self): print("Auto-Blend Layers")
    def auto_align_layers(self): print("Auto-Align Layers")
    def define_brush_preset(self): print("Define Brush Preset")
    def define_pattern(self): print("Define Pattern")
    def purge(self): print("Purge")
    def adobe_pdf_presets(self): print("Adobe PDF Presets")
    def remote_connections(self): print("Remote Connections")
    def preferences(self): print("Preferences")
    def mode(self): print("Mode")
    def adjustments(self): print("Adjustments")
    def auto_tone(self): print("Auto Tone")
    def auto_contrast(self): print("Auto Contrast")
    def auto_color(self): print("Auto Color")
    def image_size(self): print("Image Size")
    def canvas_size(self): print("Canvas Size")
    def image_rotation(self): print("Image Rotation")
    def crop(self): print("Crop")
    def trim(self): print("Trim")
    def reveal_all(self): print("Reveal All")
    def duplicate_image(self): print("Duplicate Image")
    def apply_image(self): print("Apply Image")
    def calculations(self): print("Calculations")
    def variables(self): print("Variables")
    def apply_data_set(self): print("Apply Data Set")
    def trap(self): print("Trap")
    def new_layer_menu(self): print("New Layer")
    def delete_layer_menu(self): print("Delete Layer")
    def layer_properties(self): print("Layer Properties")
    def layer_style(self): print("Layer Style")
    def new_fill_layer(self): print("New Fill Layer")
    def new_adjustment_layer(self): print("New Adjustment Layer")
    def layer_mask(self): print("Layer Mask")
    def vector_mask(self): print("Vector Mask")
    def create_clipping_mask(self): print("Create Clipping Mask")
    def smart_objects(self): print("Smart Objects")
    def video_layers(self): print("Video Layers")
    def three_d_layers(self): print("3D Layers")
    def type_menu(self): print("Type")
    def rasterize(self): print("Rasterize")
    def new_layer_based_slice(self): print("New Layer Based Slice")
    def group_layers(self): print("Group Layers")
    def ungroup_layers(self): print("Ungroup Layers")
    def hide_layers(self): print("Hide Layers")
    def arrange_layers(self): print("Arrange Layers")
    def merge_layers(self): print("Merge Layers")
    def merge_visible(self): print("Merge Visible")
    def flatten_image(self): print("Flatten Image")
    def matting(self): print("Matting")
    def select_all(self): print("Select All")
    def deselect(self): print("Deselect")
    def reselect(self): print("Reselect")
    def inverse_selection(self): print("Inverse Selection")
    def select_all_layers(self): print("Select All Layers")
    def deselect_layers(self): print("Deselect Layers")
    def find_layers(self): print("Find Layers")
    def color_range(self): print("Color Range")
    def focus_area(self): print("Focus Area")
    def modify_selection(self): print("Modify Selection")
    def grow_selection(self): print("Grow Selection")
    def similar_selection(self): print("Similar Selection")
    def transform_selection(self): print("Transform Selection")
    def quick_mask_mode(self): print("Quick Mask Mode")
    def load_selection(self): print("Load Selection")
    def save_selection(self): print("Save Selection")
    def last_filter(self): print("Last Filter")
    def convert_for_smart_filters(self): print("Convert for Smart Filters")
    def filter_gallery(self): print("Filter Gallery")
    def adaptive_wide_angle(self): print("Adaptive Wide Angle")
    def camera_raw_filter(self): print("Camera Raw Filter")
    def lens_correction(self): print("Lens Correction")
    def liquify(self): print("Liquify")
    def oil_paint(self): print("Oil Paint")
    def vanishing_point(self): print("Vanishing Point")
    def three_d_filters(self): print("3D Filters")
    def blur_filters(self): print("Blur Filters")
    def distort_filters(self): print("Distort Filters")
    def noise_filters(self): print("Noise Filters")
    def pixelate_filters(self): print("Pixelate Filters")
    def render_filters(self): print("Render Filters")
    def sharpen_filters(self): print("Sharpen Filters")
    def stylize_filters(self): print("Stylize Filters")
    def texture_filters(self): print("Texture Filters")
    def video_filters(self): print("Video Filters")
    def other_filters(self): print("Other Filters")
    def digimarc_filters(self): print("Digimarc Filters")
    def proof_setup(self): print("Proof Setup")
    def proof_colors(self): print("Proof Colors")
    def gamut_warning(self): print("Gamut Warning")
    def pixel_aspect_ratio(self): print("Pixel Aspect Ratio")
    def thirty_two_bit_preview(self): print("32-bit Preview")
    def zoom_in(self): print("Zoom In")
    def zoom_out(self): print("Zoom Out")
    def fit_on_screen(self): print("Fit on Screen")
    def actual_pixels(self): print("Actual Pixels")
    def print_size(self): print("Print Size")
    def screen_mode(self): print("Screen Mode")
    def extras(self): print("Extras")
    def show_menu(self): print("Show Menu")
    def toggle_rulers(self): print("Toggle Rulers")
    def toggle_snap(self): print("Toggle Snap")
    def snap_to(self): print("Snap To")
    def lock_guides(self): print("Lock Guides")
    def new_guide(self): print("New Guide")
    def clear_guides(self): print("Clear Guides")
    def arrange_windows(self): print("Arrange Windows")
    def workspace_menu(self): print("Workspace")
    def toggle_actions(self): print("Toggle Actions")
    def toggle_adjustments(self): print("Toggle Adjustments")
    def toggle_brush(self): print("Toggle Brush")
    def toggle_brush_presets(self): print("Toggle Brush Presets")
    def toggle_channels(self): print("Toggle Channels")
    def toggle_character(self): print("Toggle Character")
    def toggle_color(self): print("Toggle Color")
    def toggle_histogram(self): print("Toggle Histogram")
    def toggle_history(self): print("Toggle History")
    def toggle_info(self): print("Toggle Info")
    def toggle_layer_comps(self): print("Toggle Layer Comps")
    def toggle_layers(self): print("Toggle Layers")
    def toggle_navigator(self): print("Toggle Navigator")
    def toggle_options(self): print("Toggle Options")
    def toggle_paragraph(self): print("Toggle Paragraph")
    def toggle_paths(self): print("Toggle Paths")
    def toggle_properties(self): print("Toggle Properties")
    def toggle_styles(self): print("Toggle Styles")
    def toggle_swatches(self): print("Toggle Swatches")
    def toggle_timeline(self): print("Toggle Timeline")
    def toggle_tool_presets(self): print("Toggle Tool Presets")
    def toggle_tools(self): print("Toggle Tools")
    def reset_panels(self): print("Reset Panels")
    def help(self): print("Help")
    def about(self): print("About")
    def system_info(self): print("System Info")
    def updates(self): print("Updates")
    def manage_extensions(self): print("Manage Extensions")

# dialogs/new_file_dialog.py
class NewFileDialog(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.result = None
        self.build_ui()


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageForge(root)
    root.mainloop()