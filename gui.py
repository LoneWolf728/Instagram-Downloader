import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import threading
import re
import ast
from downloader import download_media

class InstaDownloaderApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Instagram Downloader - Anonymous Story & Media Downloader")
        self.geometry("570x700")
        self.minsize(570, 700)
        
        # Dark theme colors with neon purple accents
        self.colors = {
            'bg': '#1a1a1a',           # Dark background
            'fg': '#ffffff',           # White text
            'accent': '#9d4edd',       # Neon purple
            'accent_light': '#c77dff', # Lighter purple
            'accent_dark': '#7b2cbf',  # Darker purple
            'secondary': '#2d2d2d',    # Secondary background
            'tertiary': '#3a3a3a',     # Tertiary background
            'success': '#06ffa5',      # Neon green
            'warning': '#ffbe0b',      # Neon yellow
            'error': '#ff006e',        # Neon pink
            'text_light': '#e0e0e0',   # Light gray text
            'border': '#444444'        # Border color
        }

        self.config_file = "config.json"
        self.config = self.load_config()
        self.cancel_event = threading.Event()

        # Setup theme first, then create widgets
        self.setup_theme()
        self.create_widgets()

    def setup_theme(self):
        """Configure the dark theme with neon purple accents"""
        self.configure(bg=self.colors['bg'])
        
        # Configure ttk styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles for various widgets
        self.style.configure('Title.TLabel',
                            background=self.colors['bg'],
                            foreground=self.colors['accent'],
                            font=('Segoe UI', 14, 'bold'))
        
        self.style.configure('Heading.TLabel',
                            background=self.colors['bg'],
                            foreground=self.colors['accent_light'],
                            font=('Segoe UI', 10, 'bold'))
        
        self.style.configure('Custom.TLabel',
                            background=self.colors['secondary'],
                            foreground=self.colors['fg'],
                            font=('Segoe UI', 9))
        
        self.style.configure('Progress.TLabel',
                            background=self.colors['bg'],
                            foreground=self.colors['fg'],
                            font=('Segoe UI', 9))
        
        self.style.configure('Custom.TFrame',
                            background=self.colors['secondary'],
                            relief='flat',
                            borderwidth=1)
        
        # Fix LabelFrame styling
        self.style.configure('Accent.TLabelframe',
                            background=self.colors['secondary'],
                            bordercolor=self.colors['accent'],
                            borderwidth=2,
                            relief='flat')
        
        self.style.configure('Accent.TLabelframe.Label',
                            background=self.colors['secondary'],
                            foreground=self.colors['accent_light'],
                            font=('Segoe UI', 10, 'bold'))
        
        # Purple gradient buttons
        self.style.configure('Accent.TButton',
                            background=self.colors['accent'],
                            foreground='white',
                            borderwidth=0,
                            font=('Segoe UI', 9, 'bold'),
                            padding=(10, 5),
                            relief='flat')
        
        self.style.map('Accent.TButton',
                      background=[('active', self.colors['accent_light']),
                                 ('pressed', self.colors['accent_dark'])])
        
        # Success button (green)
        self.style.configure('Success.TButton',
                            background=self.colors['success'],
                            foreground='black',
                            borderwidth=0,
                            font=('Segoe UI', 9, 'bold'),
                            padding=(10, 5),
                            relief='flat')
        
        self.style.map('Success.TButton',
                      background=[('active', '#00e894'),
                                 ('pressed', '#00cc80')])
        
        # Danger button (red/pink)
        self.style.configure('Danger.TButton',
                            background=self.colors['error'],
                            foreground='white',
                            borderwidth=0,
                            font=('Segoe UI', 9, 'bold'),
                            padding=(8, 4),
                            relief='flat')
        
        self.style.map('Danger.TButton',
                      background=[('active', '#ff1a75'),
                                 ('pressed', '#e6005d')])
        
        # Entry and text widgets
        self.style.configure('Custom.TEntry',
                            fieldbackground=self.colors['tertiary'],
                            foreground=self.colors['fg'],
                            bordercolor=self.colors['accent'],
                            insertcolor=self.colors['accent'],
                            borderwidth=2,
                            relief='flat')
        
        self.style.map('Custom.TEntry',
                      bordercolor=[('focus', self.colors['accent_light'])])
        
        # Checkbuttons
        self.style.configure('Custom.TCheckbutton',
                            background=self.colors['secondary'],
                            foreground=self.colors['fg'],
                            focuscolor=self.colors['accent'],
                            font=('Segoe UI', 9))
        
        self.style.map('Custom.TCheckbutton',
                      background=[('active', self.colors['secondary'])])
        
        # Progressbar
        self.style.configure('Custom.Horizontal.TProgressbar',
                            background=self.colors['accent'],
                            troughcolor=self.colors['tertiary'],
                            borderwidth=0,
                            lightcolor=self.colors['accent_light'],
                            darkcolor=self.colors['accent_dark'])

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "cookies": "",
                "usernames": [],
                "download_path": os.path.expanduser("~/Downloads/Insta")
            }

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
        self.log("Settings saved.", "success")

    def create_widgets(self):
        # Main container with scrolling capability
        main_canvas = tk.Canvas(self, bg=self.colors['bg'], highlightthickness=0)
        main_scrollbar = ttk.Scrollbar(self, orient="vertical", command=main_canvas.yview)
        self.scrollable_main_frame = tk.Frame(main_canvas, bg=self.colors['bg'])
        
        self.scrollable_main_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=self.scrollable_main_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Main container with padding
        main_container = tk.Frame(self.scrollable_main_frame, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Title
        title_frame = tk.Frame(main_container, bg=self.colors['bg'])
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(title_frame, 
                               text="Instagram Downloader", 
                               style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, 
                                  text="Anonymous Story & Media Downloader", 
                                  style='Heading.TLabel')
        subtitle_label.pack()

        # --- Saved Users ---
        users_frame = ttk.LabelFrame(main_container, text="Saved Usernames", 
                                    style='Accent.TLabelframe', padding="10")
        users_frame.pack(fill=tk.X, pady=(0, 8))

        self.user_vars = {}
        
        # Scrollable user list
        user_list_frame = tk.Frame(users_frame, bg=self.colors['secondary'])
        user_list_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.user_canvas = tk.Canvas(user_list_frame, 
                                    bg=self.colors['secondary'], 
                                    height=80, 
                                    highlightthickness=0)
        user_scrollbar = ttk.Scrollbar(user_list_frame, orient="vertical", command=self.user_canvas.yview)
        self.scrollable_user_frame = tk.Frame(self.user_canvas, bg=self.colors['secondary'])
        
        self.scrollable_user_frame.bind(
            "<Configure>",
            lambda e: self.user_canvas.configure(scrollregion=self.user_canvas.bbox("all"))
        )
        
        self.user_canvas.create_window((0, 0), window=self.scrollable_user_frame, anchor="nw")
        self.user_canvas.configure(yscrollcommand=user_scrollbar.set)
        
        self.user_canvas.pack(side="left", fill="both", expand=True)
        user_scrollbar.pack(side="right", fill="y")

        # Add user controls
        add_user_frame = tk.Frame(users_frame, bg=self.colors['secondary'])
        add_user_frame.pack(fill=tk.X, pady=3)
        
        ttk.Label(add_user_frame, text="Username:", style='Custom.TLabel').pack(side=tk.LEFT, padx=(0, 8))
        self.new_user_entry = ttk.Entry(add_user_frame, style='Custom.TEntry', font=('Segoe UI', 9))
        self.new_user_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 8))
        
        ttk.Button(add_user_frame, text="Add", 
                  command=self.add_user, style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(add_user_frame, text="Remove Selected", 
                  command=self.remove_selected_users, style='Danger.TButton').pack(side=tk.LEFT)

        # --- Quick Download ---
        quick_download_frame = ttk.LabelFrame(main_container, text="Quick Download", 
                                            style='Accent.TLabelframe', padding="10")
        quick_download_frame.pack(fill=tk.X, pady=(0, 8))

        quick_user_frame = tk.Frame(quick_download_frame, bg=self.colors['secondary'])
        quick_user_frame.pack(fill=tk.X)
        
        ttk.Label(quick_user_frame, text="Username:", style='Custom.TLabel').pack(side=tk.LEFT, padx=(0, 8))
        self.quick_user_entry = ttk.Entry(quick_user_frame, style='Custom.TEntry', font=('Segoe UI', 9))
        self.quick_user_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 8))
        ttk.Button(quick_user_frame, text="Download", 
                  command=self.quick_download, style='Success.TButton').pack(side=tk.LEFT)

        # --- Download Options ---
        options_frame = ttk.LabelFrame(main_container, text="Download Options", 
                                     style='Accent.TLabelframe', padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.download_stories_var = tk.BooleanVar(value=True)
        self.download_posts_var = tk.BooleanVar(value=True)
        
        stories_cb = ttk.Checkbutton(options_frame, text="Download Stories (Anonymous)", 
                                   variable=self.download_stories_var, style='Custom.TCheckbutton')
        stories_cb.pack(anchor=tk.W, pady=1)
        
        posts_cb = ttk.Checkbutton(options_frame, text="Download Posts & Reels", 
                                 variable=self.download_posts_var, style='Custom.TCheckbutton')
        posts_cb.pack(anchor=tk.W, pady=1)

        # --- Settings ---
        settings_frame = ttk.LabelFrame(main_container, text="Settings", 
                                      style='Accent.TLabelframe', padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 8))

        # Cookies section
        cookies_label = ttk.Label(settings_frame, text="Instagram Cookies (Required):", 
                                style='Custom.TLabel')
        cookies_label.pack(anchor=tk.W, pady=(0, 3))
        
        self.cookies_text = tk.Text(settings_frame, 
                                   height=4, 
                                   bg=self.colors['tertiary'],
                                   fg=self.colors['fg'],
                                   insertbackground=self.colors['accent'],
                                   selectbackground=self.colors['accent'],
                                   relief='flat',
                                   borderwidth=2,
                                   font=('Consolas', 8))
        self.cookies_text.pack(fill=tk.X, pady=(0, 8))
        self.cookies_text.insert(tk.END, self.config.get("cookies", ""))

        # Download path
        path_frame = tk.Frame(settings_frame, bg=self.colors['secondary'])
        path_frame.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(path_frame, text="Save to:", style='Custom.TLabel').pack(side=tk.LEFT, padx=(0, 8))
        self.path_var = tk.StringVar(value=self.config.get("download_path"))
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, 
                             state="readonly", style='Custom.TEntry')
        path_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 8))
        ttk.Button(path_frame, text="Browse", 
                  command=self.browse_path, style='Accent.TButton').pack(side=tk.LEFT)

        ttk.Button(settings_frame, text="Save Settings", 
                  command=self.save_settings, style='Success.TButton').pack(pady=5)

        # --- Actions ---
        action_frame = tk.Frame(main_container, bg=self.colors['bg'])
        action_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.start_button = ttk.Button(action_frame, 
                                      text="Start Download for Selected (0)", 
                                      command=self.start_download_thread, 
                                      style='Success.TButton')
        self.start_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 8))
        
        self.cancel_button = ttk.Button(action_frame, text="Cancel", 
                                       command=self.cancel_download, 
                                       state=tk.DISABLED, style='Danger.TButton')
        self.cancel_button.pack(side=tk.LEFT)

        # --- Progress Bar ---
        progress_frame = tk.Frame(main_container, bg=self.colors['bg'])
        progress_frame.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(progress_frame, text="Progress:", style='Progress.TLabel').pack(anchor=tk.W)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                          variable=self.progress_var, 
                                          maximum=100,
                                          style='Custom.Horizontal.TProgressbar')
        self.progress_bar.pack(fill=tk.X, pady=3)

        # --- Status Log ---
        log_frame = ttk.LabelFrame(main_container, text="Status Log", 
                                 style='Accent.TLabelframe', padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Log text with scrollbar
        log_text_frame = tk.Frame(log_frame, bg=self.colors['secondary'])
        log_text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        
        self.log_text = tk.Text(log_text_frame, 
                               state='disabled', 
                               wrap=tk.WORD, 
                               height=8,
                               bg=self.colors['tertiary'],
                               fg=self.colors['text_light'],
                               insertbackground=self.colors['accent'],
                               selectbackground=self.colors['accent'],
                               relief='flat',
                               borderwidth=0,
                               font=('Consolas', 8))
        
        log_scrollbar = ttk.Scrollbar(log_text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text['yscrollcommand'] = log_scrollbar.set
        
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Button(log_frame, text="Clear Logs", 
                  command=self.clear_logs, style='Accent.TButton').pack()

        self.update_user_listbox()
        self.log("Ready to download!", "success")
        self.log(f"Loading config from {self.config_file}...", "info")

    def update_user_listbox(self):
        """Update the scrollable user list with checkboxes"""
        for widget in self.scrollable_user_frame.winfo_children():
            widget.destroy()
        
        self.user_vars = {}
        for username in sorted(self.config.get("usernames", [])):
            var = tk.BooleanVar()
            
            # Create a frame for each user
            user_frame = tk.Frame(self.scrollable_user_frame, bg=self.colors['secondary'])
            user_frame.pack(fill=tk.X, pady=1, padx=3)
            
            cb = ttk.Checkbutton(user_frame, 
                               text=f"@{username}", 
                               variable=var, 
                               command=self.update_start_button_text,
                               style='Custom.TCheckbutton')
            cb.pack(anchor=tk.W)
            
            self.user_vars[username] = var
        
        self.update_start_button_text()

    def add_user(self):
        new_user = self.new_user_entry.get().strip()
        if new_user and new_user not in self.config["usernames"]:
            self.config["usernames"].append(new_user)
            self.update_user_listbox()
            self.new_user_entry.delete(0, tk.END)
            self.log(f"Added user: @{new_user}", "success")
        elif not new_user:
            self.log("Error: Username cannot be empty.", "error")
        else:
            self.log(f"Error: User @{new_user} already exists.", "warning")

    def remove_selected_users(self):
        removed_count = 0
        for username, var in list(self.user_vars.items()):
            if var.get():
                self.config["usernames"].remove(username)
                removed_count += 1
        if removed_count > 0:
            self.update_user_listbox()
            self.log(f"Removed {removed_count} user(s).", "success")
        else:
            self.log("No users selected to remove.", "warning")

    def browse_path(self):
        path = filedialog.askdirectory(initialdir=self.path_var.get())
        if path:
            self.path_var.set(path)
            self.log(f"Download path set to: {path}", "info")

    def save_settings(self):
        self.config["cookies"] = self.cookies_text.get("1.0", tk.END).strip()
        self.config["download_path"] = self.path_var.get()
        self.save_config()

    def get_selected_users(self):
        return [username for username, var in self.user_vars.items() if var.get()]

    def update_start_button_text(self):
        count = len(self.get_selected_users())
        self.start_button.config(text=f"Start Download for Selected ({count})")

    def log(self, message, log_type="info"):
        """Enhanced logging with icons"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.config(state='disabled')
        self.log_text.see(tk.END)

    def clear_logs(self):
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state='disabled')
        self.log("Logs cleared.", "info")

    def cancel_download(self):
        self.cancel_event.set()
        self.log("Cancellation signal sent. Finishing current operation...", "warning")

    def update_progress(self, value):
        self.progress_var.set(value)

    def quick_download(self):
        username = self.quick_user_entry.get().strip()
        if not username:
            self.log("Error: Quick Download username cannot be empty.", "error")
            return
        self.start_download_thread([username])

    def start_download_thread(self, usernames=None):
        if usernames is None:
            usernames_to_download = self.get_selected_users()
        else:
            usernames_to_download = usernames

        if not usernames_to_download:
            self.log("No users selected for download.", "warning")
            return

        download_stories = self.download_stories_var.get()
        download_posts = self.download_posts_var.get()
        if not download_stories and not download_posts:
            messagebox.showerror("Error", "You must select to download stories, posts, or both.")
            return

        cookies_str = self.config.get("cookies", "").strip()
        if not cookies_str:
            messagebox.showerror("Error", "Cookies are required. Please add them in the settings.")
            return

        cookies = None
        if "cookies = {" in cookies_str:
            match = re.search(r"cookies\s*=\s*(\{.*?\})", cookies_str, re.DOTALL)
            if match:
                try:
                    cookies = ast.literal_eval(match.group(1))
                except (ValueError, SyntaxError):
                    pass

        if cookies is None:
            try:
                cookies = json.loads(cookies_str)
            except json.JSONDecodeError:
                pass

        if cookies is None:
            try:
                items = [item for item in cookies_str.split(';') if item.strip()]
                if all('=' in item for item in items):
                    cookies = {k.strip(): v.strip() for k, v in (item.split('=', 1) for item in items)}
                else:
                    raise ValueError("Invalid semicolon-separated format")
            except Exception:
                pass

        if cookies is None:
            messagebox.showerror("Error", "Could not parse cookies. Please paste the full code snippet including 'cookies = {...}', a valid JSON object, or a 'key=value;' string.")
            return

        download_path = self.config.get("download_path")
        self.cancel_event.clear()
        self.progress_var.set(0)

        thread = threading.Thread(target=self.run_downloads, args=(usernames_to_download, cookies, download_path, download_stories, download_posts))
        thread.daemon = True
        thread.start()

    def run_downloads(self, usernames, cookies, download_path, download_stories, download_posts):
        self.start_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)

        total_users = len(usernames)
        for i, username in enumerate(usernames):
            if self.cancel_event.is_set():
                self.log("Download process cancelled by user.", "warning")
                break
            
            self.log(f"Processing user {i+1} of {total_users}: @{username}", "download")
            # This progress update is for the user level
            user_progress_start = (i / total_users) * 100
            user_progress_end = ((i + 1) / total_users) * 100
            
            def user_progress_callback(step_progress):
                # Scale the 0-100 step_progress to the user's portion of the total progress
                total_progress = user_progress_start + (step_progress / 100) * (user_progress_end - user_progress_start)
                self.update_progress(total_progress)

            download_media(username, cookies, download_path, self.log, user_progress_callback, self.cancel_event, download_stories, download_posts)

        if not self.cancel_event.is_set():
            self.log("All downloads completed!", "success")
            self.update_progress(100)
        else:
            self.log("Download process finished with cancellation.", "warning")

        self.start_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    app = InstaDownloaderApp()
    app.mainloop()
