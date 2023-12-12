import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from matplotlib.widgets import Button
from matplotlib.widgets import TextBox

from tkinter import Tk, filedialog

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
        plt.title("Proyección de Rectas")
        plt.xlabel("X")
        plt.ylabel("Y")

        # Create buttons
        self.ax_clear_last = plt.axes([0.1, 0.01, 0.2, 0.05])  # [left, bottom, width, height]
        self.btn_clear_last = Button(self.ax_clear_last, 'Borrar ultima linea')
        self.btn_clear_last.on_clicked(self.clear_last_line)

        self.ax_clear_last = plt.axes([0.8, 0.01, 0.1, 0.05])  # [left, bottom, width, height]
        self.btn_clear_last = Button(self.ax_clear_last, 'Guardar')
        self.btn_clear_last.on_clicked(self.save_lines)
        
        self.ax_clear_last = plt.axes([0.9, 0.01, 0.1, 0.05])  # [left, bottom, width, height]
        self.btn_clear_last = Button(self.ax_clear_last, 'Cargar')
        self.btn_clear_last.on_clicked(self.load_lines)

        texts = ['Tamaño:', 'Escala:']
        self.text_boxes = []

        for i in range(len(texts)):
            text_box = TextBox(plt.axes([0.05, 0.9 - i * 0.1, 0.05, 0.05]), f'{texts[i]}', f'{self._info[i]}')
            self.text_boxes.append(text_box)

        self.ax_load_values = plt.axes([0.01, 0.9 - len(texts) * 0.1, 0.1, 0.05])  # [left, bottom, width, height]
        self.btn_load_values = Button(self.ax_load_values, 'Cargar valores')
        self.btn_load_values.on_clicked(self.Load_info)
        
    #--------------------------------------------------------------
    #PRIVATE METHODS
    def Load_info(self, event):        
        for i in range(len(self._info)):
            print(f'{self._info[i]} = {self.text_boxes[i].text}')
            self._info[i] = (int)(self.text_boxes[i].text)       
        self.CreateBackground()

    def CalculatePosition(self, pos):
        if (pos is not None):
            pos_int, pos_float = divmod(pos, self._info[1])
            if (pos_float > self._info[1] / 2.0):
                pos_int += 1
            return pos_int * self._info[1], True
        return 0, False
         
    def CreateBackground(self):
        tam = self._info[0]
        i = 0

        for line in self.background_lines:
            line.remove()
        self.background_lines = []
        for line in self.lines:
            line.remove()
        self.lines = []
        self.fig.canvas.draw()

        while (i < tam):
            line = Line2D([-tam, tam], [i, i], color='gray', linestyle='-', alpha=0.1)
            self.background_lines.append(line)
            self.ax.add_line(line)

            line = Line2D([i, i], [-tam, tam], color='gray', linestyle='-', alpha=0.1)
            self.background_lines.append(line)
            self.ax.add_line(line)
            i += self._info[1]
        # Establecer límites de ejes
        self.ax.set_xlim([0, tam])
        self.ax.set_ylim([0, tam])

    def GetStyleLine(self, pressed):
        return '-' if pressed == 0 else 'dashed'
    #--------------------------------------------------------------    
    #EVENTS
    def on_press(self, event):
        if event.inaxes != self.ax:
            return
        
        if event.button == 1:
            self._button_press = 0
        elif event.button == 3:
            self._button_press = 1

        x, cond_x = self.CalculatePosition(event.xdata)
        y, cond_y = self.CalculatePosition(event.ydata)
        if (cond_x == True and cond_y == True):
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

        x, cond_x = self.CalculatePosition(event.xdata)
        y, cond_y = self.CalculatePosition(event.ydata)
        
        if self.text_label:
            self.text_label.remove()

        if (cond_x == True and cond_y == True):
            self.points.append((x, y))
            line = Line2D([self.points[0][0], self.points[1][0]],
                        [self.points[0][1], self.points[1][1]], color='black', linestyle=self.GetStyleLine(self._button_press))
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
        
        x, cond_x = self.CalculatePosition(event.xdata)
        y, cond_y = self.CalculatePosition(event.ydata)

        #self.text_label.set_position((x, y))
        self.text_label.set_text(f'dist: { ((x - self._pointPosition[0])**2+(y - self._pointPosition[1])**2)**0.5 }')
        self.fig.canvas.draw()

        if (cond_x == True and cond_y == True):
            self.current_line = Line2D([self.points[0][0], x],
                                    [self.points[0][1], y], color='gray', linestyle=self.GetStyleLine(self._button_press))
            self.ax.add_line(self.current_line)
            self.fig.canvas.draw()
    def on_key(self, event):
        if event.key == 'delete':
            x, y = event.xdata, event.ydata
            self.remove_closest_line(x, y)

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
    def save_lines(self, event):        
        if not self.lines:
            return
        
        root = Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(title="Guardar líneas como", filetypes=[("ISO projection", "*.ipr")])

        if file_path:
            print(f"Guardando líneas en {file_path}")
            with open(file_path, 'wt') as arch:
                arch.write(self._ISOMode)
                arch.write(self._info[0])
                arch.write(self._info[1])
                arch.write(0)
                arch.write(0)
                arch.write(0)
                for i, l in enumerate(self.lines):
                    arch.write(l.get_xdata()[0])
                    arch.write(l.get_ydata()[0])
                    arch.write(l.get_xdata()[1])
                    arch.write(l.get_ydata()[1])
                    arch.write(l.type_line)
            arch.close()

    def load_lines(self, event):
        # Cuadro de diálogo emergente para cargar líneas
        root = Tk()
        root.withdraw()  # Ocultar la ventana principal de Tkinter
        file_path = filedialog.askopenfilename(title="Seleccionar archivo para cargar líneas", filetypes=[("ISO projection", "*.ipr")])

        if file_path:
            print(f"Cargando líneas desde {file_path}")
            with open(file_path, 'rt') as arch:
                self._ISOMode = (int)(arch.read(1))
                self._info[0] = (int)(arch.read(1))
                self._info[1] = (int)(arch.read(1))
                arch.read(1)
                arch.read(1)
                arch.read(1)

                c = arch.read(1)
                while (c):
                    x1 = c
                    y1 = arch.read(1)
                    x2 = arch.read(1)
                    y2 = arch.read(1)
                    type = arch.read(1)

                    line = Line2D([x1, y1], [x2, y2], color='black', linestyle=self.GetStyleLine(type))
                    self.lines.append(line)
                    self.ax.add_line(line)


            arch.close()  

if __name__ == '__main__':
    drawer = ProjectionDrawer()

    plt.show()
