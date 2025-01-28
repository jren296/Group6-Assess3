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
        self.canvas = tk.Canvas(root, width=1000, height=800, bg='gray')
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
        self.canvas.bind('<B1-Motion', self.update_crop)
        self.canvas.bind('<ButtonRelease-1>', self.finish_crop)
        # Create keyboard shortcuts
        self.root.bind('<Control-z>', lambda event: self.undo())
        self.root.bind('<Control-y>', lambda event: self.redo())
        self.root.bind('<Control-s', lambda event: self.save_image())

    def load_image(self):
        



