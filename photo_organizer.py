import os
import shutil
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
from PIL.ExifTags import TAGS
import subprocess

class PhotoOrganizer:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Photo Organizer")
        self.window.geometry("800x600")  # Increased window size
        self.window.configure(bg="#f0f0f0")
        self.window.minsize(800, 600)  # Set minimum window size
        
        # Set custom fonts
        self.title_font = ('Helvetica', 18, 'bold')  # Increased font size
        self.button_font = ('Helvetica', 11)  # Increased font size
        
        # Operation mode (copy or move)
        self.operation_mode = tk.StringVar(value="copy")
        
        # Create main frame with scrolling capability
        self.canvas = tk.Canvas(self.window, bg="#f0f0f0")
        self.scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=self.canvas.yview)
        self.main_frame = tk.Frame(self.canvas, bg="#f0f0f0")
        
        # Configure scrolling
        self.main_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Create a window in the canvas for the main frame
        self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw", width=780)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack the canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True, padx=(20, 0))
        self.scrollbar.pack(side="right", fill="y")
        
        # Create and pack widgets
        self.create_widgets()
        
        # Initialize view folder button (hidden initially)
        self.view_folder_button = None
        
    def on_enter(self, event):
        # Darken button color on hover
        current_bg = event.widget.cget('bg')
        if current_bg == '#4CAF50':
            event.widget.configure(bg='#45a049')
        elif current_bg == '#2196F3':
            event.widget.configure(bg='#1976D2')
        elif current_bg == '#FF5722':
            event.widget.configure(bg='#F4511E')
    
    def on_leave(self, event):
        # Restore original button color
        if 'Source' in event.widget.cget('text'):
            event.widget.configure(bg='#4CAF50')
        elif 'Destination' in event.widget.cget('text'):
            event.widget.configure(bg='#2196F3')
        else:
            event.widget.configure(bg='#FF5722')
    
    def update_status(self, message, is_error=False):
        self.status_label.configure(
            text=message,
            fg="#d32f2f" if is_error else "#666666"
        )
        self.window.update()
    
    def select_source_folder(self):
        self.source_path = filedialog.askdirectory(title="Select Source Folder")
        if self.source_path:
            self.source_button.config(text=f"Source: {Path(self.source_path).name}")
    
    def select_dest_folder(self):
        # Ask if user wants to create a new folder
        create_new = messagebox.askyesno(
            "Destination Folder",
            "Would you like to create a new destination folder?"
        )
        
        if create_new:
            # First select parent directory
            parent_dir = filedialog.askdirectory(title="Select Parent Directory for New Folder")
            if parent_dir:
                # Create a dialog for folder name
                dialog = tk.Toplevel(self.window)
                dialog.title("New Folder")
                dialog.geometry("300x100")
                
                tk.Label(dialog, text="Enter folder name:").pack(pady=5)
                folder_name = tk.Entry(dialog)
                folder_name.pack(pady=5)
                
                def create_folder():
                    name = folder_name.get().strip()
                    if name:
                        self.dest_path = os.path.join(parent_dir, name)
                        try:
                            os.makedirs(self.dest_path, exist_ok=True)
                            self.dest_button.config(text=f"Destination: {Path(self.dest_path).name}")
                            dialog.destroy()
                        except Exception as e:
                            messagebox.showerror("Error", f"Could not create folder: {str(e)}")
                    else:
                        messagebox.showerror("Error", "Please enter a folder name")
                
                tk.Button(dialog, text="Create", command=create_folder).pack(pady=5)
        else:
            # Use existing folder selection
            self.dest_path = filedialog.askdirectory(title="Select Destination Folder")
            if self.dest_path:
                self.dest_button.config(text=f"Destination: {Path(self.dest_path).name}")
    
    def get_creation_date(self, file_path):
        try:
            # First try to get date from image EXIF data
            with Image.open(file_path) as img:
                exif = img._getexif()
                if exif:
                    for tag_id in exif:
                        tag = TAGS.get(tag_id, tag_id)
                        if tag == 'DateTimeOriginal':
                            # Parse the date from EXIF
                            date_str = exif[tag_id]
                            return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                
            # If no EXIF data, fall back to file creation time
            timestamp = os.path.getctime(file_path)
            return datetime.fromtimestamp(timestamp)
        except Exception as e:
            # If any error occurs, fall back to file creation time
            timestamp = os.path.getctime(file_path)
            return datetime.fromtimestamp(timestamp)
    
    def open_destination_folder(self):
        """Open the destination folder in File Explorer"""
        if self.dest_path:
            try:
                # Use the default system file explorer to open the folder
                subprocess.run(['explorer', os.path.normpath(self.dest_path)])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open folder: {str(e)}")

    def show_view_folder_button(self):
        """Create and show the view folder button"""
        if self.view_folder_button:
            self.view_folder_button.destroy()
        
        self.view_folder_button = tk.Button(
            self.progress_frame,
            text="📂 View Organized Photos",
            command=self.open_destination_folder,
            font=self.button_font,
            bg="#2196F3",  # Blue
            fg="white",
            padx=10,
            pady=5,
            cursor="hand2"
        )
        self.view_folder_button.pack(pady=(10, 0))
        
        # Add hover effects
        self.view_folder_button.bind('<Enter>', self.on_enter)
        self.view_folder_button.bind('<Leave>', self.on_leave)
    
    def create_widgets(self):
        # Title
        title_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        title_frame.pack(fill='x', pady=(20, 30))
        
        title = tk.Label(
            title_frame,
            text="📸 Photo Organizer",
            font=self.title_font,
            bg="#f0f0f0",
            fg="#333333"
        )
        title.pack()
        
        # Description
        description = tk.Label(
            title_frame,
            text="Organize your photos by date automatically",
            font=('Helvetica', 12, 'italic'),
            bg="#f0f0f0",
            fg="#666666"
        )
        description.pack(pady=(5, 0))
        
        # Operation Mode frame
        operation_frame = tk.LabelFrame(
            self.main_frame,
            text="Operation Mode",
            bg="#f0f0f0",
            fg="#333333",
            font=self.button_font,
            padx=20,
            pady=15
        )
        operation_frame.pack(fill='x', pady=10, padx=20)
        
        # Radio buttons for operation mode
        copy_radio = tk.Radiobutton(
            operation_frame,
            text="Copy Photos (The original images will be retained in the source location)",
            variable=self.operation_mode,
            value="copy",
            bg="#f0f0f0",
            font=self.button_font,
            padx=10,
            wraplength=700  # Allow text to wrap if needed
        )
        copy_radio.pack(anchor='w', pady=(5,0))
        
        move_radio = tk.Radiobutton(
            operation_frame,
            text="Move Photos (The originals will be moved from the source location)",
            variable=self.operation_mode,
            value="move",
            bg="#f0f0f0",
            font=self.button_font,
            padx=10,
            wraplength=700  # Allow text to wrap if needed
        )
        move_radio.pack(anchor='w', pady=(5,5))
        
        # Source frame
        source_frame = tk.LabelFrame(
            self.main_frame,
            text="Source",
            bg="#f0f0f0",
            fg="#333333",
            font=self.button_font,
            padx=20,
            pady=15
        )
        source_frame.pack(fill='x', pady=10, padx=20)
        
        self.source_button = tk.Button(
            source_frame,
            text="Choose Source Folder",
            command=self.select_source_folder,
            font=self.button_font,
            bg="#4CAF50",
            fg="white",
            padx=30,
            pady=8,
            cursor="hand2"
        )
        self.source_button.pack(pady=5)
        
        # Destination frame
        dest_frame = tk.LabelFrame(
            self.main_frame,
            text="Destination",
            bg="#f0f0f0",
            fg="#333333",
            font=self.button_font,
            padx=20,
            pady=15
        )
        dest_frame.pack(fill='x', pady=10, padx=20)
        
        self.dest_button = tk.Button(
            dest_frame,
            text="Choose Destination Folder",
            command=self.select_dest_folder,
            font=self.button_font,
            bg="#2196F3",
            fg="white",
            padx=30,
            pady=8,
            cursor="hand2"
        )
        self.dest_button.pack(pady=5)
        
        # Progress frame
        self.progress_frame = tk.LabelFrame(
            self.main_frame,
            text="Progress",
            bg="#f0f0f0",
            fg="#333333",
            font=self.button_font,
            padx=20,
            pady=15
        )
        self.progress_frame.pack(fill='x', pady=10, padx=20)
        
        # Progress information
        self.progress_info = tk.Label(
            self.progress_frame,
            text="Waiting to start...",
            font=('Helvetica', 11),
            bg="#f0f0f0",
            fg="#666666"
        )
        self.progress_info.pack(fill='x')
        
        # Progress bar style
        style = ttk.Style()
        style.configure(
            'Custom.Horizontal.TProgressbar',
            troughcolor='#E0E0E0',
            background='#4CAF50',
            thickness=25  # Increased thickness
        )
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            style='Custom.Horizontal.TProgressbar'
        )
        self.progress_bar.pack(fill='x', pady=(10, 0))
        
        # Status frame
        self.status_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.status_frame.pack(fill='x', pady=10, padx=20)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Ready to organize",
            font=('Helvetica', 11),
            bg="#f0f0f0",
            fg="#666666"
        )
        self.status_label.pack()
        
        # Organize button
        self.organize_button = tk.Button(
            self.main_frame,
            text="🗂 Organize Photos",
            command=self.organize_photos,
            font=('Helvetica', 14, 'bold'),
            bg="#FF5722",
            fg="white",
            padx=40,
            pady=12,
            cursor="hand2"
        )
        self.organize_button.pack(pady=30)
        
        self.source_path = None
        self.dest_path = None
        
        # Bind hover effects
        for button in [self.source_button, self.dest_button, self.organize_button]:
            button.bind('<Enter>', self.on_enter)
            button.bind('<Leave>', self.on_leave)
    
    def organize_photos(self):
        if not self.source_path or not self.dest_path:
            self.update_status("Please select both source and destination folders", True)
            messagebox.showerror("Error", "Please select both source and destination folders")
            return
            
        # Confirm if user selected move operation
        if self.operation_mode.get() == "move":
            if not messagebox.askyesno(
                "Confirm Move Operation",
                "WARNING: You have selected to MOVE the photos.\n\n"
                "This means the original photos will be moved from their current location "
                "to the new organized folders.\n\n"
                "Do you want to continue?"
            ):
                return
            
        try:
            # Hide the view folder button if it exists
            if self.view_folder_button:
                self.view_folder_button.destroy()
            
            # Reset and show progress
            self.progress_var.set(0)
            self.progress_info.configure(text="Scanning files...")
            self.window.update()
            
            # Get all files from source directory
            files = [f for f in os.listdir(self.source_path) 
                    if os.path.isfile(os.path.join(self.source_path, f))
                    and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
            
            if not files:
                self.progress_info.configure(text="No image files found")
                self.update_status("No image files found in the source folder", True)
                messagebox.showinfo("Info", "No image files found in the source folder")
                return
            
            total_files = len(files)
            operation_text = "Moving" if self.operation_mode.get() == "move" else "Copying"
            
            # Process each file
            for i, filename in enumerate(files, 1):
                # Update progress information
                self.progress_info.configure(
                    text=f"{operation_text}: {filename} ({i}/{total_files})"
                )
                self.update_status(f"{operation_text} file {i} of {total_files}")
                
                file_path = os.path.join(self.source_path, filename)
                date = self.get_creation_date(file_path)
                
                # Create year/month folder structure
                year_folder = os.path.join(self.dest_path, str(date.year))
                month_folder = os.path.join(year_folder, date.strftime("%m-%B"))
                
                # Create folders if they don't exist
                os.makedirs(month_folder, exist_ok=True)
                
                # Move or copy file to new location
                dest_path = os.path.join(month_folder, filename)
                if self.operation_mode.get() == "move":
                    shutil.move(file_path, dest_path)
                else:
                    shutil.copy2(file_path, dest_path)
                
                # Update progress
                progress = (i / total_files) * 100
                self.progress_var.set(progress)
                self.window.update()
            
            operation_done = "moved" if self.operation_mode.get() == "move" else "copied"
            self.progress_info.configure(text=f"Organization complete! All files {operation_done}.")
            self.update_status("Organization complete!")
            messagebox.showinfo("Success", f"Successfully {operation_done} {total_files} photos!")
            
            # Show the view folder button
            self.show_view_folder_button()
            
        except Exception as e:
            self.progress_info.configure(text="Error occurred during organization")
            self.update_status(f"Error: {str(e)}", True)
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = PhotoOrganizer()
    app.run()
