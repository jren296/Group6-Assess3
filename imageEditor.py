import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk
import numpy as np

class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor")
        self.image = None
        self.cropped_image = None
        self.displayed_cropped = None
        self.rect_start = None
        self.rect_end = None
        self.undo_stack = []
        self.redo_stack = []

        # Create GUI elements
        self.canvas = tk.Canvas(root, width=800, height=600, bg='gray')
        self.canvas.pack()
        buttonFrame = tk.Frame(root)
        buttonFrame.pack(side='top', pady=5)
        # Set up buttons
        self.loadButton = tk.Button(buttonFrame, text='Load Image', command=self.load_image)
        self.loadButton.grid(row=0, column=0, padx=5)
        self.saveButton = tk.Button(buttonFrame, text='Save Image', command=self.save_image, state=tk.DISABLED)
        self.saveButton.grid(row=0, column=1, padx=5)
        self.undoButton = tk.Button(buttonFrame, text='Undo', command=self.undo, state=tk.DISABLED)
        self.undoButton.grid(row=0, column=2, padx=5)
        self.redoButton = tk.Button(buttonFrame, text='Redo', command=self.redo, state=tk.DISABLED)
        self.redoButton.grid(row=0, column=3, padx=5)
        # Set up slider
        self.slider = tk.Scale(buttonFrame, from_=10, to=200, orient='horizontal', label='Resize Cropped Image')
        self.slider.grid(row=0, column=4, padx=5)
        self.slider.bind('<Motion>', self.resize_preview)
        # Bind mouse buttons for cropping
        self.canvas.bind('<Button-1>', self.start_crop)
        self.canvas.bind('<B1-Motion>', self.update_crop)
        self.canvas.bind('<ButtonRelease-1>', self.finish_crop)
        # Create keyboard shortcuts
        self.root.bind('<Control-z>', lambda event: self.undo())
        self.root.bind('<Control-y>', lambda event: self.redo())
        self.root.bind('<Control-s>', lambda event: self.save_image())

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpeg *.jpg *.png *.bmp")])
        if file_path:
            self.image = cv2.imread(file_path)
            self.display_image(self.image)
            self.saveButton.config(state=tk.DISABLED)
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.undoButton.config(state=tk.DISABLED)
            self.redoButton.config(state=tk.DISABLED)

    def display_image(self, image):
        self.thumbnail = cv2.resize(image, (800, 600), interpolation=cv2.INTER_AREA)
        thumbnail_pil = Image.fromarray(cv2.cvtColor(self.thumbnail, cv2.COLOR_BGR2RGB))
        thumbnail_tk = ImageTk.PhotoImage(thumbnail_pil)
        self.canvas.create_image(500, 400, image=thumbnail_tk, anchor="center")
        self.canvas.image = thumbnail_tk # Keeps a reference image

    def start_crop(self, event):
        if self.image is not None:
            self.rect_start = (event.x, event.y)

    def update_crop(self, event):
        if self.image is not None and self.rect_start:
            self.canvas.delete("crop_rect")
            self.rect_end = (event.x, event.y)
            self.canvas.create_rectangle(self.rect_start[0], self.rect_start[1], self.rect_end[0], self.rect_end[1],
                                         outline='blue', tag='crop_rect')
            
    def finish_crop(self, event):
        if self.image is not None and self.rect_start and self.rect_end:
            x1, y1 = self.rect_start
            x2, y2 = self.rect_end
            x1, x2 = sorted([x1, x2])
            y1, y2 = sorted([y1, y2])
            h, w, _ = self.image.shape
            scale_x = self.image.shape[1]/ 800
            scale_y = self.image.shape[0]/ 600
            # Map canvas coords to image coords
            x1 = int(x1 * scale_x)
            x2 = int(x2 * scale_x)
            y1 = int(y1 * scale_y)
            y2 = int(y2 * scale_y)
            # Crop and display image
            self.cropped_image = self.image[y1:y2, x1:x2]
            self.displayed_cropped = self.cropped_image.copy()
            self.display_cropped()
            # Set up undo and save
            self.undo_stack.append(self.image.copy())
            self.redo_stack.clear()
            self.undoButton.config(state=tk.NORMAL)
            self.redoButton.config(state=tk.DISABLED)
            self.saveButton.config(state=tk.NORMAL)

    def display_cropped(self):
        cropped_pil = Image.fromarray(cv2.cvtColor(self.displayed_cropped, cv2.COLOR_BGR2RGB))
        cropped_tk = ImageTk.PhotoImage(cropped_pil) 
        self.canvas.create_image(600, 300, image=cropped_tk, anchor='center')  
        self.canvas.cropped_image = cropped_tk # Keep the reference

    def resize_preview(self, event):
        if self.cropped_image is not None:
            scale = self.slider.get() / 100
            resized = cv2.resize(self.cropped_image, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
            self.displayed_cropped = resized
            self.display_cropped

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.image.copy())
            self.image = self.undo_stack.pop()
            self.display_image(self.image)
            self.redoButton.config(state=tk.NORMAL)
        if not self.undo_stack:
            self.undoButton.config(state=tk.DISABLED)

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.image.copy())
            self.image = self.undo_stack.pop()
            self.display_image(self.image)
            self.undoButton.config(state=tk.NORMAL)
        if not self.redo_stack:
            self.redoButton.config(state=tk.DISABLED)

    def save_image(self):
        if self.cropped_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
            if file_path:
                cv2.imwrite(file_path, cv2.cvtColor(self.displayed_cropped, cv2.COLOR_BGR2RGB))
                messagebox.showinfo("Save Image", "Save successful")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditor(root)
    root.mainloop()
