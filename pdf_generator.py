#!/usr/bin/env python3
"""
Standalone PDF generator for AstroBookBot
This script provides a simple interface to generate PDF covers without using Streamlit's rerun functionality.
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from indesign_generator import generate_indesign_covers

class PDFGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AstroBookBot PDF Generator")
        self.root.geometry("500x400")
        self.root.configure(bg="#262730")
        
        # Set style
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#262730")
        self.style.configure("TLabel", background="#262730", foreground="white", font=("Arial", 12))
        self.style.configure("TButton", font=("Arial", 12, "bold"), background="#9370DB")
        self.style.map("TButton", background=[("active", "#8A2BE2")])
        self.style.configure("TEntry", font=("Arial", 12))
        
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(self.main_frame, text="Generate InDesign PDF Covers", 
                              font=("Arial", 16, "bold"), bg="#262730", fg="white")
        title_label.pack(pady=(0, 20))
        
        # Form frame
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Birth Date
        ttk.Label(form_frame, text="Birth Date (MM/DD/YYYY):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.birth_date_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.birth_date_var, width=30).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Birth Time
        ttk.Label(form_frame, text="Birth Time (HH:MM AM/PM):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.birth_time_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.birth_time_var, width=30).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Location
        ttk.Label(form_frame, text="Location:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.location_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.location_var, width=30).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Generate button
        generate_button = ttk.Button(form_frame, text="Generate PDF Covers", command=self.generate_pdfs)
        generate_button.grid(row=4, column=0, columnspan=2, pady=20)
        
        # Status
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_label = ttk.Label(form_frame, textvariable=self.status_var)
        status_label.grid(row=5, column=0, columnspan=2, pady=5)
        
        # Try to load data from temp file if it exists
        self.load_data_from_temp_file()
        
        # Set default values if not loaded from file
        if not self.name_var.get():
            self.name_var.set("John Doe")
        if not self.birth_date_var.get():
            self.birth_date_var.set("01/01/2000")
        if not self.birth_time_var.get():
            self.birth_time_var.set("12:00 PM")
        if not self.location_var.get():
            self.location_var.set("New York, NY, USA")
    
    def generate_pdfs(self):
        """Generate PDF covers using InDesign"""
        try:
            # Get values
            name = self.name_var.get().strip()
            birth_date_str = self.birth_date_var.get().strip()
            birth_time_str = self.birth_time_var.get().strip()
            location = self.location_var.get().strip()
            
            # Validate
            if not name or not birth_date_str or not birth_time_str or not location:
                messagebox.showerror("Error", "All fields are required")
                return
            
            # Format birth info
            try:
                # Parse date
                birth_date = datetime.strptime(birth_date_str, "%m/%d/%Y")
                birth_date_formatted = birth_date.strftime("%B %d, %Y")
                
                # Combine
                birth_info = f"{birth_date_formatted} - {birth_time_str}"
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use MM/DD/YYYY")
                return
            
            # Update status
            self.status_var.set("Generating PDFs... Please wait")
            self.root.update()
            
            # Call the generator
            result = generate_indesign_covers(name, birth_info, location)
            
            # Check result
            if result['success']:
                messagebox.showinfo("Success", f"PDF covers generated successfully!\nSaved to: {result['output_folder']}")
                self.status_var.set("PDFs generated successfully")
            else:
                messagebox.showerror("Error", f"Failed to generate PDFs: {result['error']}")
                self.status_var.set("Error generating PDFs")
                
        except Exception as e:
            import traceback
            error_msg = f"Error: {str(e)}\n\n{traceback.format_exc()}"
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Error occurred")
    
    def load_data_from_temp_file(self):
        """Load data from temporary file if it exists"""
        try:
            temp_file = "/tmp/astrobook_data.txt"
            if os.path.exists(temp_file):
                with open(temp_file, "r") as f:
                    lines = f.readlines()
                    
                for line in lines:
                    if line.startswith("Name:"):
                        self.name_var.set(line.replace("Name:", "").strip())
                    elif line.startswith("Birth Date:"):
                        self.birth_date_var.set(line.replace("Birth Date:", "").strip())
                    elif line.startswith("Birth Time:"):
                        self.birth_time_var.set(line.replace("Birth Time:", "").strip())
                    elif line.startswith("Location:"):
                        self.location_var.set(line.replace("Location:", "").strip())
                        
                # Delete the temp file after reading
                try:
                    os.remove(temp_file)
                except:
                    pass
                        
                return True
        except Exception as e:
            print(f"Error loading data from temp file: {e}")
            return False

def main():
    root = tk.Tk()
    app = PDFGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
