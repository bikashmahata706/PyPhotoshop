import tkinter as tk
from tkinter import ttk
from app.core import AppState, ToolManager
from tools.move_tool import make_tool as make_move_tool

class PhotoshopClone:
    def __init__(self, root):
        self.root = root
        self.root.title("PyPhotoshop")
        self.root.geometry("1200x800")
        
        # Initialize app state
        self.app_state = AppState(root)
        
        # Create UI
        self.create_menu()
        self.create_toolbar()
        self.create_canvas()
        
        # Initialize tool manager
        self.tool_manager = ToolManager(self.app_state)
        self.register_tools()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Move Tool", command=lambda: self.tool_manager.switch_tool("move"))
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        self.root.config(menu=menubar)
    
    def create_toolbar(self):
        toolbar = ttk.Frame(self.root, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        move_btn = ttk.Button(toolbar, text="Move", command=lambda: self.tool_manager.switch_tool("move"))
        move_btn.pack(side=tk.LEFT, padx=2, pady=2)
    
    def create_canvas(self):
        # Create canvas with scrollbars
        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True)
        
        vscrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        hscrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)
        
        self.canvas = tk.Canvas(frame, bg="#333333", 
                               yscrollcommand=vscrollbar.set,
                               xscrollcommand=hscrollbar.set)
        
        vscrollbar.config(command=self.canvas.yview)
        hscrollbar.config(command=self.canvas.xview)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vscrollbar.grid(row=0, column=1, sticky="ns")
        hscrollbar.grid(row=1, column=0, sticky="ew")
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Set canvas in app state
        self.app_state.set_canvas(self.canvas)
        
        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
    
    def register_tools(self):
        # Register tools here
        self.tool_manager.register_tool("move", make_move_tool)
    
    def on_mouse_down(self, event):
        if self.app_state.active_tool:
            self.app_state.active_tool.on_mouse_down(event.x, event.y, {"shift": False, "ctrl": False})
    
    def on_mouse_move(self, event):
        if self.app_state.active_tool:
            self.app_state.active_tool.on_mouse_move(event.x, event.y, {"shift": False, "ctrl": False})
    
    def on_mouse_up(self, event):
        if self.app_state.active_tool:
            self.app_state.active_tool.on_mouse_up(event.x, event.y, {"shift": False, "ctrl": False})
    
    def new_file(self):
        print("New file command")
    
    def open_file(self):
        print("Open file command")
    
    def save_file(self):
        print("Save file command")

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoshopClone(root)
    root.mainloop()