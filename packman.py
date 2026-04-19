"""
Combines logic from https://www.reddit.com/r/arcaea/comments/1i132ai/arcaea_nsw_mods_packing_script/ for repacking,
and my own for unpacking, for a multifunctional .pack manager, useful for modding the NX version of Arcaea. Tested on
v2.0.1 of the game.
"""

import json
import copy
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from datetime import datetime

BASE_JSON = {
    "Groups": [
        {"Name": "startup", "Offset": 0, "Length": 0, "OrderedEntries": []},
        {"Name": "audio_init", "Offset": 0, "Length": 0, "OrderedEntries": []},
        {"Name": "buttons", "Offset": 0, "Length": 0, "OrderedEntries": []},
        {"Name": "mainmenu", "Offset": 0, "Length": 0, "OrderedEntries": []},
        {"Name": "topbar", "Offset": 0, "Length": 0, "OrderedEntries": []},
        {"Name": "base_shutters", "Offset": 0, "Length": 0, "OrderedEntries": []},
        {"Name": "jackets_large", "Offset": 0, "Length": 0, "OrderedEntries": []},
        {"Name": "jackets_small", "Offset": 0, "Length": 0, "OrderedEntries": []},
        {"Name": "packs", "Offset": 0, "Length": 0, "OrderedEntries": []},
        {"Name": "charts", "Offset": 0, "Length": 0, "OrderedEntries": []},
        {"Name": "songselect_bgs", "Offset": 0, "Length": 0, "OrderedEntries": []},
        {"Name": "character_sprites", "Offset": 0, "Length": 0, "OrderedEntries": []},
        {"Name": "not_large_png", "Offset": 0, "Length": 0, "OrderedEntries": []},
        {"Name": "not_large_jpg", "Offset": 0, "Length": 0, "OrderedEntries": []},
        {"Name": "not_audio_or_images", "Offset": 0, "Length": 0, "OrderedEntries": []},
        {"Name": "audio_wav", "Offset": 0, "Length": 0, "OrderedEntries": []},
        {"Name": "not_audio", "Offset": 0, "Length": 0, "OrderedEntries": []},
        {"Name": "Fallback", "Offset": 0, "Length": 0, "OrderedEntries": []}
    ]
}

class ArcaeaPackManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Arcaea Pack Manager")
        self.root.geometry("900x700")
        
        style = ttk.Style()
        style.theme_use("clam")
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.extract_frame = ttk.Frame(self.notebook)
        self.repack_frame = ttk.Frame(self.notebook)
        self.log_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.extract_frame, text="Extract Pack")
        self.notebook.add(self.repack_frame, text="Repack Files")
        self.notebook.add(self.log_frame, text="Log")
        
        self.extract_input_path = tk.StringVar()
        self.extract_metadata_path = tk.StringVar()
        self.extract_output_path = tk.StringVar(value="extracted")
        
        self.repack_work_path = tk.StringVar(value="arc_work")
        self.repack_output_path = tk.StringVar(value="arc_6.pack")
        self.repack_json_path = tk.StringVar(value="arc_6.json")

        self.setup_extract_tab()
        self.setup_repack_tab()
        self.setup_log_tab()

        self.log_queue = []
        
    def setup_extract_tab(self):
        """Setup the extraction tab UI"""
        main_frame = ttk.Frame(self.extract_frame, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Input pack file
        ttk.Label(main_frame, text="Pack File (.pack):", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0,5))
        pack_frame = ttk.Frame(main_frame)
        pack_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0,15))
        ttk.Entry(pack_frame, textvariable=self.extract_input_path).pack(side="left", fill="x", expand=True, padx=(0,5))
        ttk.Button(pack_frame, text="Browse...", command=self.browse_extract_input).pack(side="right")
        
        # Metadata JSON file
        ttk.Label(main_frame, text="Metadata JSON:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=(0,5))
        meta_frame = ttk.Frame(main_frame)
        meta_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(0,15))
        ttk.Entry(meta_frame, textvariable=self.extract_metadata_path).pack(side="left", fill="x", expand=True, padx=(0,5))
        ttk.Button(meta_frame, text="Browse...", command=self.browse_extract_metadata).pack(side="right")
        
        # Output directory
        ttk.Label(main_frame, text="Output Directory:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky="w", pady=(0,5))
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(0,20))
        ttk.Entry(output_frame, textvariable=self.extract_output_path).pack(side="left", fill="x", expand=True, padx=(0,5))
        ttk.Button(output_frame, text="Browse...", command=self.browse_extract_output).pack(side="right")
        
        # Progress bar
        self.extract_progress = ttk.Progressbar(main_frame, mode="indeterminate")
        self.extract_progress.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(0,10))
        
        # Extract button
        self.extract_button = ttk.Button(main_frame, text="Extract Pack", command=self.start_extraction, style="Accent.TButton")
        self.extract_button.grid(row=7, column=0, columnspan=3, pady=(0,10))
        
        # Status label
        self.extract_status = ttk.Label(main_frame, text="Ready", foreground="gray")
        self.extract_status.grid(row=8, column=0, columnspan=3)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        
    def setup_repack_tab(self):
        """Setup the repacking tab UI"""
        main_frame = ttk.Frame(self.repack_frame, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Working directory
        ttk.Label(main_frame, text="Working Directory (with modded files):", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0,5))
        work_frame = ttk.Frame(main_frame)
        work_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0,15))
        ttk.Entry(work_frame, textvariable=self.repack_work_path).pack(side="left", fill="x", expand=True, padx=(0,5))
        ttk.Button(work_frame, text="Browse...", command=self.browse_repack_work).pack(side="right")
        
        # Output pack file
        ttk.Label(main_frame, text="Output Pack File:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=(0,5))
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(0,15))
        ttk.Entry(output_frame, textvariable=self.repack_output_path).pack(side="left", fill="x", expand=True, padx=(0,5))
        ttk.Button(output_frame, text="Browse...", command=self.browse_repack_output).pack(side="right")
        
        # Output JSON file
        ttk.Label(main_frame, text="Output JSON File:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky="w", pady=(0,5))
        json_frame = ttk.Frame(main_frame)
        json_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(0,20))
        ttk.Entry(json_frame, textvariable=self.repack_json_path).pack(side="left", fill="x", expand=True, padx=(0,5))
        ttk.Button(json_frame, text="Browse...", command=self.browse_repack_json).pack(side="right")
        
        # Progress bar
        self.repack_progress = ttk.Progressbar(main_frame, mode="indeterminate")
        self.repack_progress.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(0,10))
        
        # Repack button
        self.repack_button = ttk.Button(main_frame, text="Repack Files", command=self.start_repacking)
        self.repack_button.grid(row=7, column=0, columnspan=3, pady=(0,10))
        
        # Status label
        self.repack_status = ttk.Label(main_frame, text="Ready", foreground="gray")
        self.repack_status.grid(row=8, column=0, columnspan=3)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        
    def setup_log_tab(self):
        """Setup the log tab UI"""
        main_frame = ttk.Frame(self.log_frame, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Log text widget with scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill="both", expand=True)
        
        self.log_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=("Courier", 9))
        self.log_text.pack(fill="both", expand=True)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Save Log", command=self.save_log).pack(side="left", padx=5)
        
    def log(self, message, level="INFO"):
        """Add a message to the log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        # Add to log text widget
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # Update status based on level
        if level == "ERROR":
            if hasattr(self, "extract_status"):
                self.extract_status.config(text=f"Error: {message[:50]}", foreground="red")
            if hasattr(self, "repack_status"):
                self.repack_status.config(text=f"Error: {message[:50]}", foreground="red")
        
    def clear_log(self):
        """Clear the log text widget"""
        self.log_text.delete(1.0, tk.END)
        self.log("Log cleared", "INFO")
        
    def save_log(self):
        """Save the log to a file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log(f"Log saved to {file_path}", "INFO")
            except Exception as e:
                self.log(f"Failed to save log: {e}", "ERROR")
                messagebox.showerror("Error", f"Failed to save log: {e}")
    
    # Browser functions for extract tab
    def browse_extract_input(self):
        filename = filedialog.askopenfilename(title="Select pack file", filetypes=[("Pack files", "*.pack"), ("All files", "*.*")])
        if filename:
            self.extract_input_path.set(filename)
            self.log(f"Selected pack file: {filename}")
            
    def browse_extract_metadata(self):
        filename = filedialog.askopenfilename(title="Select metadata JSON", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if filename:
            self.extract_metadata_path.set(filename)
            self.log(f"Selected metadata: {filename}")
            
    def browse_extract_output(self):
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.extract_output_path.set(directory)
            self.log(f"Output directory: {directory}")
    
    # Browser functions for repack tab
    def browse_repack_work(self):
        directory = filedialog.askdirectory(title="Select working directory")
        if directory:
            self.repack_work_path.set(directory)
            self.log(f"Working directory: {directory}")
            
    def browse_repack_output(self):
        filename = filedialog.asksaveasfilename(title="Save pack file as", defaultextension=".pack", filetypes=[("Pack files", "*.pack"), ("All files", "*.*")])
        if filename:
            self.repack_output_path.set(filename)
            self.log(f"Output pack file: {filename}")
            
    def browse_repack_json(self):
        filename = filedialog.asksaveasfilename(title="Save JSON metadata as", defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if filename:
            self.repack_json_path.set(filename)
            self.log(f"Output JSON file: {filename}")
    
    def start_extraction(self):
        """Start extraction in a separate thread"""
        if not self.extract_input_path.get():
            messagebox.showerror("Error", "Please select a pack file")
            return
        if not self.extract_metadata_path.get():
            messagebox.showerror("Error", "Please select a metadata JSON file")
            return
            
        self.extract_button.config(state="disabled", text="Extracting...")
        self.extract_progress.start()
        self.extract_status.config(text="Extracting...", foreground="blue")
        
        thread = threading.Thread(target=self.extract_pack, daemon=True)
        thread.start()
        
    def extract_pack(self):
        """Extract files from pack"""
        try:
            pack_path = self.extract_input_path.get()
            metadata_path = self.extract_metadata_path.get()
            output_dir = self.extract_output_path.get()
            
            self.log(f"Starting extraction: {pack_path} -> {output_dir}")
            
            # Load metadata
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            
            if "Groups" not in metadata:
                raise ValueError("Metadata file does not contain 'Groups' field")
            
            # Read pack file
            with open(pack_path, "rb") as f:
                pack_data = f.read()
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            total_files = 0
            extracted_count = 0
            
            # Process each group
            for group in metadata["Groups"]:
                group_name = group.get("Name", "unknown")
                entries = group.get("OrderedEntries", [])
                self.log(f"Processing group '{group_name}' with {len(entries)} files")
                
                for entry in entries:
                    filename = entry.get("OriginalFilename", "")
                    offset = entry.get("Offset", 0)
                    length = entry.get("Length", 0)
                    
                    if not filename or length == 0:
                        continue
                    
                    out_path = Path(output_dir) / filename
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Extract file
                    file_data = pack_data[offset:offset + length]
                    with open(out_path, "wb") as out_file:
                        out_file.write(file_data)
                    
                    extracted_count += 1
                    total_files += 1
                    
                    if extracted_count % 100 == 0:
                        self.log(f"Extracted {extracted_count} files...")
            
            self.log(f"Extraction complete! Extracted {extracted_count} files to {output_dir}", "INFO")
            self.root.after(0, self.extraction_complete, True, extracted_count)
            
        except Exception as e:
            self.log(f"Extraction failed: {e}", "ERROR")
            self.root.after(0, self.extraction_complete, False, str(e))
            
    def extraction_complete(self, success, message):
        """Handle extraction completion"""
        self.extract_progress.stop()
        self.extract_button.config(state="normal", text="Extract Pack")
        
        if success:
            self.extract_status.config(text=f"Complete! Extracted {message} files", foreground="green")
            messagebox.showinfo("Success", f"Successfully extracted {message} files!")
        else:
            self.extract_status.config(text="Extraction failed", foreground="red")
            messagebox.showerror("Error", f"Extraction failed: {message}")
            
    def start_repacking(self):
        """Start repacking in a separate thread"""
        if not os.path.exists(self.repack_work_path.get()):
            messagebox.showerror("Error", "Working directory does not exist")
            return
            
        self.repack_button.config(state="disabled", text="Repacking...")
        self.repack_progress.start()
        self.repack_status.config(text="Repacking...", foreground="blue")
        
        thread = threading.Thread(target=self.repack_files, daemon=True)
        thread.start()
        
    def repack_files(self):
        """Repack files into pack"""
        try:
            work_dir = self.repack_work_path.get()
            output_pack = self.repack_output_path.get()
            output_json = self.repack_json_path.get()
            
            self.log(f"Starting repacking from {work_dir}")
            
            # Load base JSON structure
            pack_index = copy.deepcopy(BASE_JSON) # fixed a state persistence issue when previous repacks would impact each other due to shallow copies

            # Walk through working directory
            for root, dirs, files in os.walk(work_dir):
                for filename in files:
                    file_path = os.path.normpath(os.path.join(root, filename))
                    file_ext = os.path.splitext(file_path)[1].lower()
                    file_size = os.path.getsize(file_path)
                    
                    # Get relative path
                    rel_path = os.path.relpath(file_path, work_dir).replace("\\", "/")
                    
                    file_entry = {
                        "OriginalFilename": rel_path,
                        "Offset": 0,
                        "Length": file_size
                    }
                    
                    self.log(f"Processing: {rel_path} ({file_size} bytes)")
                    
                    # Categorize file
                    categorized = False
                    
                    if file_ext == ".jpg":
                        if "songs" in root:
                            if "_256" in filename:
                                for group in pack_index["Groups"]:
                                    if group["Name"] == "jackets_small":
                                        group["OrderedEntries"].append(file_entry)
                                        categorized = True
                                        break
                            else:
                                for group in pack_index["Groups"]:
                                    if group["Name"] == "jackets_large":
                                        group["OrderedEntries"].append(file_entry)
                                        categorized = True
                                        break
                        else:
                            if file_size < 100000:
                                for group in pack_index["Groups"]:
                                    if group["Name"] == "not_large_jpg":
                                        group["OrderedEntries"].append(file_entry)
                                        categorized = True
                                        break
                            else:
                                for group in pack_index["Groups"]:
                                    if group["Name"] == "not_audio":
                                        group["OrderedEntries"].append(file_entry)
                                        categorized = True
                                        break
                                        
                    elif file_ext == ".png":
                        if "char" in root:
                            for group in pack_index["Groups"]:
                                if group["Name"] == "character_sprites":
                                    group["OrderedEntries"].append(file_entry)
                                    categorized = True
                                    break
                        elif "songs" in root:
                            if "pack" in root:
                                for group in pack_index["Groups"]:
                                    if group["Name"] == "packs":
                                        group["OrderedEntries"].append(file_entry)
                                        categorized = True
                                        break
                            else:
                                if "_256" in filename:
                                    for group in pack_index["Groups"]:
                                        if group["Name"] == "jackets_small":
                                            group["OrderedEntries"].append(file_entry)
                                            categorized = True
                                            break
                                else:
                                    for group in pack_index["Groups"]:
                                        if group["Name"] == "jackets_large":
                                            group["OrderedEntries"].append(file_entry)
                                            categorized = True
                                            break
                        else:
                            if file_size < 100000:
                                for group in pack_index["Groups"]:
                                    if group["Name"] == "not_large_png":
                                        group["OrderedEntries"].append(file_entry)
                                        categorized = True
                                        break
                            else:
                                for group in pack_index["Groups"]:
                                    if group["Name"] == "not_audio":
                                        group["OrderedEntries"].append(file_entry)
                                        categorized = True
                                        break
                                        
                    elif file_ext == ".aff":
                        for group in pack_index["Groups"]:
                            if group["Name"] == "charts":
                                group["OrderedEntries"].append(file_entry)
                                categorized = True
                                break
                                
                    elif file_ext in [".json", ".ttf", ".csb"]:
                        for group in pack_index["Groups"]:
                            if group["Name"] == "not_audio_or_images":
                                group["OrderedEntries"].append(file_entry)
                                categorized = True
                                break
                                
                    elif file_ext == ".ogg":
                        for group in pack_index["Groups"]:
                            if group["Name"] == "Fallback":
                                group["OrderedEntries"].append(file_entry)
                                categorized = True
                                break
                                
                    else:
                        if any(keyword in filename for keyword in ["packlist", "songlist", "unlocks"]):
                            for group in pack_index["Groups"]:
                                if group["Name"] == "not_audio_or_images":
                                    group["OrderedEntries"].append(file_entry)
                                    categorized = True
                                    break
                        else:
                            for group in pack_index["Groups"]:
                                if group["Name"] == "Fallback":
                                    group["OrderedEntries"].append(file_entry)
                                    categorized = True
                                    break
                    
                    if not categorized:
                        self.log(f"Warning: Could not categorize {rel_path}, placing in Fallback", "WARNING")
                        for group in pack_index["Groups"]:
                            if group["Name"] == "Fallback":
                                group["OrderedEntries"].append(file_entry)
                                break
            
            # Write pack file
            self.log("Writing pack file...")
            with open(output_pack, "wb") as pack_data:
                current_offset = 0
                for group in pack_index["Groups"]:
                    group_offset = current_offset
                    group_length = 0
                    group["Offset"] = group_offset
                    
                    for file_entry in group["OrderedEntries"]:
                        file_path = os.path.join(work_dir, file_entry["OriginalFilename"])
                        file_entry["Offset"] = group_offset + group_length
                        
                        with open(file_path, "rb") as file_data:
                            pack_data.write(file_data.read())
                        
                        group_length += file_entry["Length"]
                    
                    group["Length"] = group_length
                    current_offset += group_length
            
            # Write JSON metadata
            with open(output_json, "w", encoding="utf-8") as json_file:
                json.dump(pack_index, json_file, indent=2)
            
            self.log(f"Repacking complete! Created {output_pack} and {output_json}", "INFO")
            self.root.after(0, self.repacking_complete, True, output_pack)
            
        except Exception as e:
            self.log(f"Repacking failed: {e}", "ERROR")
            self.root.after(0, self.repacking_complete, False, str(e))
            
    def repacking_complete(self, success, message):
        """Handle repacking completion"""
        self.repack_progress.stop()
        self.repack_button.config(state="normal", text="Repack Files")
        
        if success:
            self.repack_status.config(text=f"Complete! Created {os.path.basename(message)}", foreground="green")
            messagebox.showinfo("Success", f"Successfully created pack file:\n{message}")
        else:
            self.repack_status.config(text="Repacking failed", foreground="red")
            messagebox.showerror("Error", f"Repacking failed: {message}")

def main():
    root = tk.Tk()
    app = ArcaeaPackManager(root=root)
    root.mainloop()

if __name__ == "__main__":
    main()
