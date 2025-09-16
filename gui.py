from tkinter import Tk

class GUI:
    def __init__(self):
        self.root = Tk()
        self.root.title("My GUI Application")
        self.root.geometry("400x300")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = GUI()
    gui.run()