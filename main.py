import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from matplotlib.widgets import Button
from matplotlib.widgets import TextBox

from tkinter import Tk, filedialog
import math

class ProjectionDrawer:

    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.lines = []
        self.points = []
        self.background_lines = []
        self.current_line = None
        self.is_drawing = False

        self.fig.canvas.manager.window.state('zoomed')  # Maximizar la ventana usando el backend TkAgg
        
        self._ISOMode = 0
        self._button_press = 0
        self._text_position = None
        self._scale_position = [0,0]

        self.ax.set_aspect('equal')

        self.fig.canvas.toolbar.pack_forget()

        self._info = [140, 5]

        self.CreateBackground()

        self.cid_press = self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.cid_release = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.cid_motion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.cid_key = self.fig.canvas.mpl_connect('key_press_event', self.on_key)

        self.LoadGUI()
    #--------------------------------------------------------------
    #Info
    def LoadGUI(self):        
        self.ax.set_title("Monge")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")

        # Create buttons
        self.ax_clear_last = plt.axes([0.1, 0.01, 0.2, 0.05])  # [left, bottom, width, height]
        self.btn_clear_last = Button(self.ax_clear_last, 'Borrar ultima linea')
        self.btn_clear_last.on_clicked(self.clear_last_line)

        self.ax_save = plt.axes([0.8, 0.01, 0.08, 0.05])  # [left, bottom, width, height]
        self.btn_save = Button(self.ax_save, 'Guardar')
        self.btn_save.on_clicked(self.save_lines)
        
        self.ax_load = plt.axes([0.9, 0.01, 0.08, 0.05])  # [left, bottom, width, height]
        self.btn_load = Button(self.ax_load, 'Cargar')
        self.btn_load.on_clicked(self.load_lines)

        texts = ['Tamaño:', 'Escala:']
        self.text_boxes = []

        for i in range(len(texts)):
            text_box = TextBox(plt.axes([0.05, 0.9 - i * 0.1, 0.05, 0.05]), f'{texts[i]}', f'{self._info[i]}')
            self.text_boxes.append(text_box)

        self.ax_load_values = plt.axes([0.01, 0.9 - len(texts) * 0.1, 0.1, 0.05])  # [left, bottom, width, height]
        self.btn_load_values = Button(self.ax_load_values, 'Cargar valores')
        self.btn_load_values.on_clicked(self.Load_info)

        self.ax_change_mode = plt.axes([0.01, 0.9 - (len(texts) + 1)* 0.1, 0.1, 0.05])  # [left, bottom, width, height]
        self.btn_change_mode = Button(self.ax_change_mode, 'Cambiar modo')
        self.btn_change_mode.on_clicked(self.Change_Mode)
        
    #--------------------------------------------------------------
    #PRIVATE METHODS
    def Change_Mode(self, event):
        self._ISOMode = (self._ISOMode + 1) % 2
        self.ax.set_title("Monge" if self._ISOMode == 0 else 'Isometria')
        self.CreateBackground()
    def Load_info(self, event):        
        for i in range(len(self._info)):
            print(f'{self._info[i]} = {self.text_boxes[i].text}')
            self._info[i] = (int)(self.text_boxes[i].text)       
        self.CreateBackground()

    def CalculatePosition(self, x, y):
        if (x is not None and y is not None):
            if (self._ISOMode == 0):
                x_int, x_float = divmod(x, self._info[1])
                y_int, y_float = divmod(y, self._info[1])
                if (x_float > self._info[1] / 2.0):
                    x_int += 1
                if (y_float > self._info[1] / 2.0):
                    y_int += 1
                return x_int * self._info[1], y_int * self._info[1], True
            else:
                x += self._info[1] / (math.tan(math.radians(30)) * 2)

                return x_int * self._info[1], y_int * self._info[1], True

        return 0, False
         
    def CreateBackground(self):
        tam = self._info[0]
        i = 0 if self._ISOMode == 0 else -tam

        for line in self.background_lines:
            line.remove()
        self.background_lines = []
        for line in self.lines:
            line.remove()
        self.lines = []

        self.ax.set_xticks(ticks=range(0, tam, self._info[1]))
        self.ax.set_yticks(ticks=range(0, tam, self._info[1]))
        x = 0

        self._scale_position = [self._info[1] / (math.tan(math.radians(30)) * 2)]
        while (i < tam * 2):
            if (self._ISOMode == 0):
                line = Line2D([0, tam], [i, i], color='gray', linestyle='-', alpha=0.1)
                self.background_lines.append(line)
                self.ax.add_line(line)#H

                line = Line2D([i, i], [0, tam], color='gray', linestyle='-', alpha=0.1)
                self.background_lines.append(line)#V
                self.ax.add_line(line)
                i += self._info[1]
            else:
                y1 = (float)(i) - math.tan(math.radians(30)) * tam
                line = Line2D([0, tam], [i, y1], color='gray', linestyle='-', alpha=0.1)
                self.background_lines.append(line)
                self.ax.add_line(line)#H
                y2 = (float)(i) + math.tan(math.radians(30)) * tam
                line = Line2D([0, tam], [i, y2], color='gray', linestyle='-', alpha=0.1)
                self.background_lines.append(line)
                self.ax.add_line(line)#H

                x += self._info[1] / (math.tan(math.radians(30)) * 2)
                line = Line2D([x, x], [0, tam], color='gray', linestyle='-', alpha=0.1)
                self.background_lines.append(line)#V
                self.ax.add_line(line)
                i += self._info[1]
        # Establecer límites de ejes
        self.ax.set_xlim([0, tam])
        self.ax.set_ylim([0, tam])

        self.fig.canvas.draw()

    def GetStyleLine(self, pressed):
        return '-' if pressed == 0 else 'dashed'
    def GetLineWidth(self, pressed):
        return 2.0 if pressed == 0 else 1.4
    #--------------------------------------------------------------    
    #EVENTS
    def on_press(self, event):
        if event.inaxes != self.ax:
            return
        
        if event.button == 1:
            self._button_press = 0
        elif event.button == 3:
            self._button_press = 1

        x, y, cond = self.CalculatePosition(event.xdata, event.ydata)
        if (cond == True):
            self.points.append((x, y))
            self.is_drawing = True

        self._pointPosition = (x, y)
        self.text_label = self.ax.text(x, y, f'dist: {0}', ha='center', va='center', bbox=dict(facecolor='white', alpha=0.8))

    def on_release(self, event):
        if event.inaxes != self.ax or not self.is_drawing:
            return
        if self.current_line is not None:
            self.current_line.remove()
            self.current_line = None

        x, y, cond = self.CalculatePosition(event.xdata, event.ydata)
        
        if self.text_label:
            self.text_label.remove()

        if (cond == True):
            self.points.append((x, y))
            line = Line2D([self.points[0][0], self.points[1][0]],
                        [self.points[0][1], self.points[1][1]], color='black', linestyle=self.GetStyleLine(self._button_press), linewidth=self.GetLineWidth(self._button_press))
            line.type_line = self._button_press
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
            self.current_line = None
        
        x, y, cond = self.CalculatePosition(event.xdata, event.ydata)

        #self.text_label.set_position((x, y))
        self.text_label.set_text(f'dist: { ((x - self._pointPosition[0])**2+(y - self._pointPosition[1])**2)**0.5 }')
        self.fig.canvas.draw()

        if (cond == True):
            self.current_line = Line2D([self.points[0][0], x],
                                    [self.points[0][1], y], color='gray', linestyle=self.GetStyleLine(self._button_press), linewidth=self.GetLineWidth(self._button_press))
            self.ax.add_line(self.current_line)
            self.fig.canvas.draw()

    def on_key(self, event):
        if event.key == 'delete':
            x, y = event.xdata, event.ydata
            self.remove_closest_line(x, y)
        """if event.key == 'control':
            x, y, cond = self.CalculatePosition(event.xdata, event.ydata)
            if (self._text_position == None):
                self._text_position = self.ax.text(x, y, f'[{x},{y}]', ha='center', va='center', bbox=dict(facecolor='white', alpha=0.8))
            self._text_position.set_position((x, y))
            self._text_position.set_text(f'[{x},{y}]')
            self.fig.canvas.draw()
        else:
            if (self._text_position != None):
                self._text_position.remove()"""


    def remove_closest_line(self, x, y):
        if not self.lines:
            return
        line = None
        dist = None
        for i, l in enumerate(self.lines):
            d = self.Calculate_Dist(l, x, y)
            if (dist == None or dist > d):
                dist = d
                line = l
        if (line != None):
            line.remove()
            self.lines.remove(line)
            self.fig.canvas.draw()

    def Calculate_Dist(self, line, px, py):
        x1 = line.get_xdata()[0]
        y1 = line.get_ydata()[0]
        x2 = line.get_xdata()[1]
        y2 = line.get_ydata()[1]
        return (abs((x2-x1)*(y1-py)-(x1-px)*(y2-y1)) / (((x2-x1)**2+(y2-y1)**2)**0.5))
    #--------------------------------------------------------------
    #BUTTONS    
    def clear_last_line(self, event):
        if self.lines:
            last_line = self.lines.pop()
            last_line.remove()
            self.fig.canvas.draw()
    #--------------------------------------------------------------
    #SAVE AND LOAD
    def load_lines(self, event):
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(title="Cargar archivo", filetypes=[("ISO projection", "*.ipr")])

        if file_path:
            print(f"Cargando líneas desde {file_path}")
            with open(file_path, 'r') as arch:
                l = arch.readlines()
                self._ISOMode = int(l[0].strip())
                self._info[0] = int(l[1].strip())
                self._info[1] = int(l[2].strip())
                a = int(l[3].strip())
                b = int(l[4].strip())
                c = int(l[5].strip())
                self.CreateBackground()

                for i in range(6, len(l), 5):
                    x1 = float(l[i + 0].strip())
                    y1 = float(l[i + 1].strip())
                    x2 = float(l[i + 2].strip())
                    y2 = float(l[i + 3].strip())
                    type = int(l[i + 4].strip())
                    print(x1)
                    print(y1)
                    print(x2)
                    print(y2)

                    line = Line2D([x1, x2], [y1, y2], color='black', linestyle=self.GetStyleLine(type), linewidth=self.GetLineWidth(type))
                    line.type_line = type
                    self.lines.append(line)
                    self.ax.add_line(line)
            self.fig.canvas.draw()
            arch.close()

    def save_lines(self, event):
        if not self.lines:
            return
        self.fig.canvas.manager.window.after(0, self.save_lines_threaded)

    def save_lines_threaded(self):
        root = Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(title="Guardar archivo", filetypes=[("ISO projection", "*.ipr")])

        if file_path:
            f = file_path.split('.')
            print(file_path)
            print(f)
            if (len(f) > 0 and f[-1] != 'ipr'):
                file_path += '.ipr'
            print(file_path)
            with open(file_path, 'w') as arch:
                arch.write(str(self._ISOMode)+ "\n")
                arch.write(str(self._info[0])+ "\n")
                arch.write(str(self._info[1])+ "\n")
                arch.write(str(0)+ "\n")
                arch.write(str(0)+ "\n")
                arch.write(str(0)+ "\n")
                for i, l in enumerate(self.lines):
                    arch.write(str(l.get_xdata()[0]) + "\n")
                    arch.write(str(l.get_ydata()[0]) + "\n")
                    arch.write(str(l.get_xdata()[1]) + "\n")
                    arch.write(str(l.get_ydata()[1]) + "\n")
                    arch.write(str(l.type_line) + "\n")
            arch.close()


if __name__ == '__main__':
    drawer = ProjectionDrawer()

    plt.show()
