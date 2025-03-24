#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Файл запуска графического интерфейса бота
"""

import tkinter as tk
from gui import BotConfigGUI
import time

if __name__ == "__main__":
    root = tk.Tk()
    app = BotConfigGUI(root)
    root.mainloop() 