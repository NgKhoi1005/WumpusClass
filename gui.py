from tkinter import *
from tkinter import font
from tkinter import scrolledtext
from tkinter.filedialog import *
import time
import sys
import os.path

DELAY = 10
X_OFFSET, Y_OFFSET = 150, 100

class World:
    def __init__(self, map_size):
        self.root = Tk()
        self.root.title("WUMPUS WORLD")
        self.root.geometry(f"+{X_OFFSET}+{Y_OFFSET}")

        self.canvas = Canvas(self.root, width=64 * map_size, height=64 * map_size + 64, background='white')
        self.outputFrame = Frame(self.root)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.outputFrame.pack(side="right", fill="both", expand=False)
        
        # KB and Action
        self.KBArea = None
        self.actionArea = None
        self.buttonStep = None
        self.buttonRun = None
        self.buttonOpen = None
        self.buttonFont = font.Font(font='Consolas', size=10)

        self.runMode = -1

        self.tiles = []
        self.objects = []
        self.warnings = []
        self.terrains = []
        self.player = None
        self.display_score = None

        self.scoreFont = font.Font(family='Consolas', size=22)

        self.root.mainloop()

    def createWorld(self, map):

        
