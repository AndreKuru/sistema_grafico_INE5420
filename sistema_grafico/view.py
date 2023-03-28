from dataclasses import dataclass, field
from tkinter import Tk, Frame, Canvas, Label, Button, Toplevel, Listbox, Entry, Menu
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controller import Controller

from model import Coordinates

WIDTH = 5
COLOR = "green"

def ask_coordinates(coord_frame):
    point_x = Frame(coord_frame)
    point_x.pack()

    point_x_label = Label(point_x, text="X:")
    point_x_label.pack(side="left")

    point_x_entry = Entry(point_x, width=4)
    point_x_entry.pack(side="right")

    point_y = Frame(coord_frame)
    point_y.pack()

    point_y_label = Label(point_y, text="Y:")
    point_y_label.pack(side="left")

    point_y_entry = Entry(point_y, width=4)
    point_y_entry.pack(side="right")


def ask_several_coordinates(coord_frame):
    Label(coord_frame, text="All endpoints").pack()
    all_coordinates = Listbox(coord_frame)
    all_coordinates.pack()

    Label(coord_frame, text="New endpoint").pack()
    ask_coordinates(coord_frame)

    insert_coordinates = Button(coord_frame, text="Insert")
    insert_coordinates.pack()

#Creation of point - still not working
def create_point(_main_window: Tk):
    create_point = Toplevel(_main_window)
    create_point.title("Create point")

    point_coord_frame = Frame(create_point)
    point_coord_frame.pack()

    ask_coordinates(point_coord_frame)

    create_point_button = Button(point_coord_frame, text="Create")
    create_point_button.pack()

# Creation of line
def create_line(_main_window: Tk):
    create_line = Toplevel(_main_window)
    create_line.title("Create line")

    line_coord_frame = Frame(create_line)
    line_coord_frame.pack()

    endpoint1 = Label(line_coord_frame, text="Endpoint 1")
    endpoint1.pack()

    ask_coordinates(line_coord_frame)

    endpoint2 = Label(line_coord_frame, text="Endpoint 2")
    endpoint2.pack()

    ask_coordinates(line_coord_frame)

    create_line_button = Button(line_coord_frame, text="Create")
    create_line_button.pack()

# Creation of wireframe
def create_wireframe(_main_window: Tk):
    create_wireframe = Toplevel(_main_window)
    create_wireframe.title("Create wireframe")

    wireframe_coord_frame = Frame(create_wireframe)
    wireframe_coord_frame.pack()

    ask_several_coordinates(wireframe_coord_frame)

    create_wireframe_button = Button(wireframe_coord_frame, text="Create")
    create_wireframe_button.pack()

def init_window_function(_main_window):

    window_function = Frame(_main_window, highlightbackground="grey", highlightthickness=2)
    window_function.pack(side="left")

    Label(window_function, text="Functions menu").pack()
    '''
    window_function = Toplevel(self._main_window)
    window_function.title("Window Functions")
    '''

    #Display File
    display_file_frame = Frame(window_function, highlightbackground="grey", highlightthickness=1)
    display_file_frame.pack()

    display_file_label = Label(display_file_frame, text="Display File").pack()
    display_file_list = Listbox(display_file_frame).pack()

    delete = Button(display_file_frame, text="Delete").pack()

    create_frame = Frame(display_file_frame)
    create_frame.pack()

    label = Label(create_frame, text="Create:").pack()


    create_point_button = Button(create_frame, 
                                 text="Point", 
                                 command=lambda : create_point(_main_window)).pack(side="left")
    create_line_button = Button(create_frame, 
                                text="Line", 
                                command=lambda : create_line(_main_window)).pack(side="left")
    create_wireframe_button = Button(create_frame, 
                                text="Wireframe", 
                                command=lambda : create_wireframe(_main_window)).pack(side="left")

    #Window control
    window_control_frame = Frame(window_function)
    window_control_frame.pack()

    window_control_label = Label(window_control_frame, text="Window control").pack()

    #Directions
    directions = Frame(window_control_frame)
    directions.pack()

    up_button = Button(directions, text="Up").pack(side="top")
    down_button = Button(directions, text="Down").pack(side="bottom")
    left_button = Button(directions, text="Left").pack(side="left")
    right_button = Button(directions, text="Right").pack(side="right")

    #Zoom
    zoom = Frame(window_function)
    zoom.pack()

    zoom_in_button = Button(zoom, text="+").pack(side="right")
    zoom_out_button = Button(zoom, text="-").pack(side="left")

    return display_file_list

@dataclass
class Graphic_Viewer:
    #Controller: Controller
    _main_window: Tk = field(default_factory=Tk)
    _canvas: Canvas = field(init=False)
    _display_file_list: Listbox = field(init=False)

    def __post_init__(self):

        viewport_frame = Frame(self._main_window)
        viewport_frame.pack(side="right")

        self._canvas = Canvas(viewport_frame, width=960, height=540, background="white", border=10, relief="raised")
        self._canvas.pack()

        # canvas.create_line(100, 200, 200, 35, fill=COLOR, width=WIDTH)
        # p = 300
        # canvas.create_oval(p, p, p+3, p+3, fill=COLOR, outline="")

        self._display_file_list = init_window_function(self._main_window)

    def draw_point(self, coordinates: Coordinates):
        self._canvas.create_oval(coordinates.x, coordinates.y, coordinates.x + 3, coordinates + 3, outline="")

    def run(self):
        self._main_window.mainloop()

app = Graphic_Viewer()
app.run()