import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.widgets import Button

class CustomToolbar(NavigationToolbar2Tk):
    def __init__(self, canvas, root):
        super().__init__(canvas, root)
        
        # Agregar botón personalizado
        self.toolitems += (
            ('CustomButton', 'Botón Personalizado', 'home', 'custom_button'),
        )

    def custom_button(self):
        print("¡Botón Personalizado Presionado!")

class ProjectionDrawer:

    def __init__(self, root):
        self.root = root
        self.fig, self.ax = plt.subplots()
        self.lines = []
        self.points = []
        self.current_line = None
        self.is_drawing = False

        self._button_press = 0
        self._SCALE = 0.5

        self.CreateBackground()

        self.cid_press = self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.cid_release = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.cid_motion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)

        plt.title("Proyección de Rectas")
        plt.xlabel("X")
        plt.ylabel("Y")

    #--------------------------------------------------------------
    #PRIVATE METHODS
    def CalculatePosition(self, pos):
        pos_int, pos_float = divmod(pos, self._SCALE)
        if (pos_float > self._SCALE / 2.0):
            pos_int += 1
        return pos_int * self._SCALE
         
    def CreateBackground(self):
        i = -20
        while (i < 20):
            line = Line2D([-20, 20], [i, i], color='gray', linestyle='dashed', alpha=0.2)
            self.lines.append(line)
            self.ax.add_line(line)

            line = Line2D([i, i], [-20, 20], color='gray', linestyle='dashed', alpha=0.2)
            self.lines.append(line)
            self.ax.add_line(line)
            i += self._SCALE

    def GetStyleLine(self):
        return '-' if self._button_press == 0 else 'dashed'
    #--------------------------------------------------------------    
    #EVENTS
    def on_press(self, event):
        if event.inaxes != self.ax:
            return
        
        if event.button == 1:
            self._button_press = 0
        elif event.button == 3:
            self._button_press = 1

        x, y = self.CalculatePosition(event.xdata), self.CalculatePosition(event.ydata)
        self.points.append((x, y))
        self.is_drawing = True

    def on_release(self, event):
        if event.inaxes != self.ax or not self.is_drawing:
            return

        x, y = self.CalculatePosition(event.xdata), self.CalculatePosition(event.ydata)
        self.points.append((x, y))

        line = Line2D([self.points[0][0], self.points[1][0]],
                      [self.points[0][1], self.points[1][1]], color='black', linestyle=self.GetStyleLine())
        self.lines.append(line)
        self.ax.add_line(line)
        self.fig.canvas.draw()

        self.is_drawing = False
        self.points = []

    def on_motion(self, event):
        if not self.is_drawing:
            return

        if self.current_line is not None:
            self.current_line.remove()

        x, y = self.CalculatePosition(event.xdata), self.CalculatePosition(event.ydata)

        self.current_line = Line2D([self.points[0][0], x],
                                   [self.points[0][1], y], color='gray', linestyle=self.GetStyleLine())
        self.ax.add_line(self.current_line)
        self.fig.canvas.draw()
    #--------------------------------------------------------------
    #BUTTONS    
    def clear_last_line(self, event):
        if self.lines:
            last_line = self.lines.pop()
            last_line.remove()
            self.fig.canvas.draw()
    #--------------------------------------------------------------

if __name__ == '__main__':
    drawer = ProjectionDrawer()
    drawer.ax.set_aspect('equal')
    plt.show()
