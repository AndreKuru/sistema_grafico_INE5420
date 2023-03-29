from __future__ import annotations
from dataclasses import dataclass, field
from tkinter import Tk, Frame, Canvas, Label, Button, Toplevel, Listbox, Entry, Menu
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controller import Controller

from model import Coordinates

WIDTH = 5
COLOR = "green"

@dataclass
class Graphic_Viewer:
    controller: Controller
    _main_window: Tk = field(default_factory=Tk)
    _canvas: Canvas = field(init=False)
    _display_file_list: Listbox = field(init=False)

    def __post_init__(self):

        viewport_frame = Frame(self._main_window)
        viewport_frame.pack(side="right")

        self._canvas = Canvas(viewport_frame, width=760, height=540, background="white", border=10, relief="raised")
        self._canvas.pack()

        # canvas.create_line_window(100, 200, 200, 35, fill=COLOR, width=WIDTH)
        # p = 300
        # canvas.create_oval(p, p, p+3, p+3, fill=COLOR, outline="")

        self.init_window_function()

        self.controller.set_drawer(self)

    def clear(self):
        self._canvas.delete("all")

    def insert_drawable(self, drawable):
        self._display_file_list.insert("end", drawable.name)


    def ask_coordinates(self, coord_frame):
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

        return point_x_entry, point_y_entry

    def insert_coordinates(self, list_x: Listbox, list_y: Listbox, entry_x: Entry, entry_y: Entry):
        list_x.insert("end", entry_x.get())
        list_y.insert("end", entry_y.get())
        

    def ask_several_coordinates(self, coord_frame):
        Label(coord_frame, text="All endpoints").pack()
        all_coordinates = Frame(coord_frame)
        all_coordinates.pack()

        all_x = Listbox(all_coordinates, width=5)
        all_x.pack(side="left")

        all_y = Listbox(all_coordinates, width=5)
        all_y.pack(side="right")

        Label(coord_frame, text="New endpoint").pack()
        entry_x, entry_y = self.ask_coordinates(coord_frame)
        Button(coord_frame,
               command=lambda : self.insert_coordinates(all_x, all_y, entry_x, entry_y),
                text="Insert").pack()

        return all_x, all_y

    #Creation of point - still not working
    def create_point_window(self):
        create_point_window = Toplevel(self._main_window)
        create_point_window.title("Create point")

        point_coord_frame = Frame(create_point_window)
        point_coord_frame.pack()

        entry_x, entry_y = self.ask_coordinates(point_coord_frame)

        create_point_button = Button(point_coord_frame, 
                                     command=lambda :self.controller.create_point(int(entry_x.get()), 
                                                                                  int(entry_y.get())),
                                     text="Create").pack()

    # Creation of line
    def create_line_window(self):
        create_line_window = Toplevel(self._main_window)
        create_line_window.title("Create line")

        line_coord_frame = Frame(create_line_window)
        line_coord_frame.pack()

        endpoint1 = Label(line_coord_frame, text="Endpoint 1")
        endpoint1.pack()

        x1_entry, y1_entry = self.ask_coordinates(line_coord_frame)

        endpoint2 = Label(line_coord_frame, text="Endpoint 2")
        endpoint2.pack()

        x2_entry, y2_entry = self.ask_coordinates(line_coord_frame)

        Button(line_coord_frame, 
               command=lambda : self.controller.create_line(int(x1_entry.get()),
                                                            int(y1_entry.get()),
                                                            int(x2_entry.get()),
                                                            int(y2_entry.get())),
               text="Create").pack()

    def create_wireframe(self, listbox_x: Listbox, listbox_y: Listbox):
        all_x = list()
        for x in listbox_x.get(0, listbox_x.size()):
            all_x.append(int(x))

        all_y = list()
        for y in listbox_y.get(0, listbox_x.size()):
            all_y.append(int(y))

        self.controller.create_wireframe(all_x, all_y)


    # Creation of wireframe
    def create_wireframe_window(self):
        create_wireframe_window = Toplevel(self._main_window)
        create_wireframe_window.title("Create wireframe")

        wireframe_coord_frame = Frame(create_wireframe_window)
        wireframe_coord_frame.pack()

        listbox_x, listbox_y = self.ask_several_coordinates(wireframe_coord_frame)

        Button(wireframe_coord_frame, 
               command=lambda : self.create_wireframe(listbox_x, listbox_y), 
               text="Create").pack()

    def init_window_function(self):

        window_function = Frame(self._main_window, highlightbackground="grey", highlightthickness=2)
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
        display_file_list = Listbox(display_file_frame)
        display_file_list.pack()

        self._display_file_list = display_file_list

        delete = Button(display_file_frame, text="Delete").pack()

        create_frame = Frame(display_file_frame)
        create_frame.pack()

        label = Label(create_frame, text="Create:").pack()


        create_point_button = Button(create_frame, 
                                    text="Point", 
                                    command=lambda : self.create_point_window()).pack(side="left")
        create_line_button = Button(create_frame, 
                                    text="Line", 
                                    command=lambda : self.create_line_window()).pack(side="left")
        create_wireframe_button = Button(create_frame, 
                                    text="Wireframe", 
                                    command=lambda : self.create_wireframe_window()).pack(side="left")

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



    def draw_point(self, coordinates: Coordinates):
        self._canvas.create_oval(coordinates.x, coordinates.y, coordinates.x + 5, coordinates.y + 5, fill="black", outline="")
        # self._canvas.create_line(100, 200, 200, 35, fill=COLOR, width=WIDTH)
        # p = 300
        # self._canvas.create_oval(300, 300, 300+3, 300+3, fill="black", outline="")
    
    def draw_line(self, endpoint1: Coordinates, endpoint2: Coordinates):
        self._canvas.create_line(endpoint1.x, endpoint1.y, endpoint2.x, endpoint2.y)

    def run(self):
        self._main_window.mainloop()