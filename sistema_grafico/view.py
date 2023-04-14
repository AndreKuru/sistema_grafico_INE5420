from __future__ import annotations
from dataclasses import dataclass, field
from tkinter import (
    Tk,
    Frame,
    Canvas,
    Label,
    Button,
    Toplevel,
    Listbox,
    Entry,
    Scrollbar,
    Menu,
    ttk,
    Radiobutton,
    IntVar,
)
from pathlib import Path

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controller import Controller

from model import Coordinates, Area2d, Color

WIDTH = 5
COLOR = "green"

ORIGIN = 1
SELECTED_OBJECT = 2
ARBITRARY_POSITION = 3


@dataclass
class Graphic_Viewer:
    controller: Controller
    _main_window: Tk = field(default_factory=Tk)
    _canvas: Canvas = field(init=False)
    _display_file_list: Listbox = field(init=False)
    _viewport: Area2d = field(init=False)

    def __post_init__(self):
        viewport_frame = Frame(self._main_window)
        viewport_frame.pack(side="right")

        width = 700
        height = 700
        self._viewport = Area2d(Coordinates(0, 0), Coordinates(width, height))
        self._canvas = Canvas(
            viewport_frame,
            width=width,
            height=height,
            background="white",
            border=10,
            relief="raised",
        )
        self._canvas.pack()

        # canvas.create_line_window(100, 200, 200, 35, fill=COLOR, width=WIDTH)
        # p = 300
        # canvas.create_oval(p, p, p+3, p+3, fill=COLOR, outline="")

        self.init_window_function()

        self.controller.set_drawer(self)

    def clear(self):
        self._canvas.delete("all")

    def insert_drawable(self, name: str):
        self._display_file_list.insert("end", name)

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

    def insert_coordinates(
        self, list_x: Listbox, list_y: Listbox, entry_x: Entry, entry_y: Entry
    ):
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
        Button(
            coord_frame,
            command=lambda: self.insert_coordinates(all_x, all_y, entry_x, entry_y),
            text="Insert",
        ).pack()

        return all_x, all_y

    def create_color(self, parent: Frame) -> ttk.Combobox:
        predefinied_colors = [
            "Black",
            "Red",
            "Green",
            "Blue",
            "Cyan",
            "Yellow",
            "Magenta",
        ]

        Color_picked = ttk.Combobox(parent, values=predefinied_colors, state="readonly")
        Color_picked.set("Black")
        Color_picked.pack()

        return Color_picked

    def map_color(self, predefinied_color):
        match predefinied_color:
            case "Black":
                return Color.BLACK
            case "Red":
                return Color.RED
            case "Green":
                return Color.GREEN
            case "Blue":
                return Color.BLUE
            case "Cyan":
                return Color.CYAN
            case "Yellow":
                return Color.YELLOW
            case _:
                return Color.MAGENTA

    # Creation of point - still not working
    def create_point_window(self):
        create_point_window = Toplevel(self._main_window)
        create_point_window.title("Create point")

        point_coord_frame = Frame(create_point_window)
        point_coord_frame.pack()

        entry_x, entry_y = self.ask_coordinates(point_coord_frame)

        color = self.create_color(point_coord_frame)

        Button(
            point_coord_frame,
            command=lambda: self.controller.create_point(
                float(entry_x.get()), float(entry_y.get()), self.map_color(color.get())
            ),
            text="Create",
        ).pack()

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

        color = self.create_color(line_coord_frame)

        Button(
            line_coord_frame,
            command=lambda: self.controller.create_line(
                float(x1_entry.get()),
                float(y1_entry.get()),
                float(x2_entry.get()),
                float(y2_entry.get()),
                self.map_color(color.get()),
            ),
            text="Create",
        ).pack()

    def create_wireframe(self, listbox_x: Listbox, listbox_y: Listbox, color: Color):
        all_x = list()
        for x in listbox_x.get(0, listbox_x.size()):
            all_x.append(float(x))

        all_y = list()
        for y in listbox_y.get(0, listbox_x.size()):
            all_y.append(float(y))

        self.controller.create_wireframe(all_x, all_y, color)

    # Creation of wireframe
    def create_wireframe_window(self):
        create_wireframe_window = Toplevel(self._main_window)
        create_wireframe_window.title("Create wireframe")

        wireframe_coord_frame = Frame(create_wireframe_window)
        wireframe_coord_frame.pack()

        listbox_x, listbox_y = self.ask_several_coordinates(wireframe_coord_frame)

        color = self.create_color(wireframe_coord_frame)

        Button(
            wireframe_coord_frame,
            command=lambda: self.create_wireframe(
                listbox_x, listbox_y, self.map_color(color.get())
            ),
            text="Create",
        ).pack()

    def move_up(self):
        movement = Coordinates(0, -1)
        self.controller.pan_window(movement, 0.1)

    def move_down(self):
        movement = Coordinates(0, 1)
        self.controller.pan_window(movement, 0.1)

    def move_left(self):
        movement = Coordinates(1, 0)
        self.controller.pan_window(movement, 0.1)

    def move_right(self):
        movement = Coordinates(-1, 0)
        self.controller.pan_window(movement, 0.1)

    def display_popup(self, event, popup: Menu):
        try:
            print(type(event))
            popup.tk_popup(event.x_root, event.y_root)
        finally:
            popup.grab_release()

    def add_transformation(
        self,
        transform_window: ttk.Notebook,
        translate_x: Entry,
        translate_y: Entry,
        scaling_x: Entry,
        scaling_y: Entry,
        angle: Entry,
        rotate_in: IntVar,
        arbitrary_point_x: Entry,
        arbitrary_point_y: Entry,
        history: Listbox,
    ):
        tab = transform_window.index(transform_window.select())
        match tab:
            case 0:  # Translate
                x = str(float(translate_x.get()))
                y = str(float(translate_y.get()))
                history.insert("end", "t(" + x + "," + y + ")")

            case 1:  # Scaling
                x = str(float(scaling_x.get()))
                y = str(float(scaling_y.get()))
                history.insert("end", "s(" + x + "," + y + ")")

            case 2:  # Rotate
                a = str(float(angle.get()))
                rotate_in_index = rotate_in.get()

                match rotate_in_index:
                    case 1:  # ORIGIN:
                        rotate_in_option = "o"
                        history.insert("end", "r(" + a + "," + rotate_in_option + ")")
                    case 2:  # SELECTED_OBJECT:
                        rotate_in_option = "s"
                        history.insert("end", "r(" + a + "," + rotate_in_option + ")")
                    case 3:  # ARBITRARY_POSITION:
                        rotate_in_option = "a"
                        x = str(float(arbitrary_point_x.get()))
                        y = str(float(arbitrary_point_y.get()))
                        history.insert(
                            "end",
                            "r(" + a + "," + rotate_in_option + "," + x + "," + y + ")",
                        )

    def apply_transformation(self, history: Listbox, name: str):
        transformations_formatted = list()

        transformations = history.get(0, history.size())
        for transformation in transformations:
            operation = transformation.split("(")[0]
            operands = transformation.split("(")[1]
            operands = operands.split(")")[0]
            op1 = operands.split(",")[0]
            op2 = operands.split(",")[1]
            if op2 == "a":
                x = operands.split(",")[2]
                y = operands.split(",")[3]

                transformations_formatted.append((operation, op1, op2, x, y))
            else:
                if operation == "r":
                    transformations_formatted.append((operation, float(op1), op2))
                else:
                    transformations_formatted.append(
                        (operation, float(op1), float(op2))
                    )

        history.delete(0, history.size() - 1)
        self.controller.transform_drawable(transformations_formatted, name)

    def ask_arbitrary_point(self, arbitrary_point: ttk.Frame):
        arbitrary_point.pack()

    def unask_arbitrary_point(self, arbitrary_point: ttk.Frame):
        arbitrary_point.pack_forget()

    def transform_window(self):
        if not self._display_file_list.curselection():
            return

        index = self._display_file_list.curselection()[0]

        name_selected = self._display_file_list.get(index)

        transform_window = Toplevel(self._main_window)
        transform_window.title("Transform")

        transform_options = ttk.Notebook(transform_window)

        traslate_option = ttk.Frame(transform_options)
        scaling_option = ttk.Frame(transform_options)
        rotation_option = ttk.Frame(transform_options)

        transform_options.add(traslate_option, text="Translate")
        transform_options.add(scaling_option, text="Scaling")
        transform_options.add(rotation_option, text="Rotation")

        transform_options.pack(side="left", expand=1)

        # Traslate
        translate_x, translate_y = self.ask_coordinates(traslate_option)

        # Scaling
        scaling_x, scaling_y = self.ask_coordinates(scaling_option)

        # Rotation
        Label(rotation_option, text="Angle:").pack()
        angle = Entry(rotation_option, width=6)
        angle.pack()

        arbitrary_point = Frame(rotation_option)
        arbitrary_point_x, arbitrary_point_y = self.ask_coordinates(arbitrary_point)

        rotate_in = IntVar()

        origin = Radiobutton(
            rotation_option,
            text="Rotate in origin",
            variable=rotate_in,
            value=ORIGIN,
            command=lambda: self.unask_arbitrary_point(arbitrary_point),
        )
        origin.pack(anchor="w")

        selected_object = Radiobutton(
            rotation_option,
            text="Rotate in self center",
            variable=rotate_in,
            value=SELECTED_OBJECT,
            command=lambda: self.unask_arbitrary_point(arbitrary_point),
        )
        selected_object.pack(anchor="w")

        arbitrary_position = Radiobutton(
            rotation_option,
            text="Rotate in arbitrary position",
            variable=rotate_in,
            value=ARBITRARY_POSITION,
            command=lambda: self.ask_arbitrary_point(arbitrary_point),
        )
        arbitrary_position.pack(anchor="w")

        # Notebook end

        transformations_to_apply = Frame(transform_window)
        transformations_to_apply.pack(side="right")

        transformations_history = Listbox(transformations_to_apply)
        transformations_history.pack()

        transformations_buttons = Frame(transformations_to_apply)
        transformations_buttons.pack()

        Button(
            transformations_buttons,
            command=lambda: self.add_transformation(
                transform_options,
                translate_x,
                translate_y,
                scaling_x,
                scaling_y,
                angle,
                rotate_in,
                arbitrary_point_x,
                arbitrary_point_y,
                transformations_history,
            ),
            text="Add",
        ).pack(side="left")

        Button(
            transformations_buttons,
            command=lambda: self.apply_transformation(
                transformations_history, name_selected
            ),
            text="Apply",
        ).pack(side="right")

    def export_window(self):
        if not self._display_file_list.curselection():
            return

        index = self._display_file_list.curselection()[0]

        name_selected = self._display_file_list.get(index)

        export_window = Toplevel(self._main_window)
        export_window.title("Export")

        Label(export_window, text="Path").pack()

        path = Entry(export_window, width=30)
        path.insert(0, Path().home() / f"{name_selected}.obj")
        path.pack()

        Button(export_window, text="Confirm").pack()


    def init_window_function(self):
        window_function = Frame(
            self._main_window, highlightbackground="grey", highlightthickness=2
        )
        window_function.pack(side="left")

        Label(window_function, text="Functions menu").pack()

        # Display File
        display_file_frame = Frame(
            window_function,
            highlightbackground="grey",
            highlightthickness=1,
        )
        display_file_frame.pack()

        Label(display_file_frame, text="Display File").pack(side="top")

        display_file_inner_frame = Frame(display_file_frame)
        display_file_inner_frame.pack()

        display_file_list = Listbox(display_file_inner_frame, selectmode="SINGLE")
        display_file_list.pack(side="left")

        display_file_scroll = Scrollbar(display_file_inner_frame)
        display_file_scroll.pack(side="right")

        display_file_list.config(yscrollcommand=display_file_scroll.set)
        display_file_scroll.config(command=display_file_list.yview)

        self._display_file_list = display_file_list

        display_file_popup = Menu(display_file_frame, tearoff=0)

        # display_file_popup.add_command(label="Delete")
        # display_file_popup.add_separator
        display_file_popup.add_command(
            label="Transform", command=lambda: self.transform_window()
        )

        display_file_popup.add_command(
            label="Export", command=lambda: self.export_window()
        )

        display_file_list.bind(
            "<Button-3>", lambda event: self.display_popup(event, display_file_popup)
        )

        create_frame = Frame(display_file_frame)
        create_frame.pack()

        label = Label(create_frame, text="Create:").pack()

        create_point_button = Button(
            create_frame, text="Point", command=lambda: self.create_point_window()
        ).pack(side="left")
        create_line_button = Button(
            create_frame, text="Line", command=lambda: self.create_line_window()
        ).pack(side="left")
        create_wireframe_button = Button(
            create_frame,
            text="Wireframe",
            command=lambda: self.create_wireframe_window(),
        ).pack(side="left")

        # Window control
        window_control_frame = Frame(window_function)
        window_control_frame.pack()

        window_control_label = Label(window_control_frame, text="Window control").pack()

        # Directions
        directions = Frame(window_control_frame)
        directions.pack()

        Button(directions, command=lambda: self.move_up(), text="Up").pack(side="top")
        Button(directions, command=lambda: self.move_down(), text="Down").pack(
            side="bottom"
        )
        Button(directions, command=lambda: self.move_left(), text="Left").pack(
            side="left"
        )
        Button(directions, command=lambda: self.move_right(), text="Right").pack(
            side="right"
        )

        # Zoom
        zoom = Frame(window_function)
        zoom.pack()

        Button(zoom, command=lambda: self.controller.zoom(Coordinates(1.1, 1.1)), text="+").pack(
            side="right"
        )
        Button(zoom, command=lambda: self.controller.zoom(Coordinates(0.9, 0.9)), text="-").pack(
            side="left"
        )

        # Window rotation
        window_rotation = Frame(window_function)
        window_rotation.pack()

        Label(window_rotation, text="Rotate").pack()

        angle = Entry(window_rotation, width=6)

        Button(window_rotation, command=lambda: self.controller.transform_window([("r", float(angle.get()), "o")]), text="CCW").pack(side="left")

        angle.pack(side="left")
        
        Button(window_rotation, command=lambda: self.controller.transform_window([("r", - float(angle.get()), "o")]), text="CW").pack(side="left")
        
    def draw_point(self, drawable_coordinates: Coordinates, color: Color):
        coordinates = self.controller.transform_window_to_viewport(drawable_coordinates)

        self._canvas.create_oval(
            coordinates.x - 2,
            coordinates.y - 2,
            coordinates.x + 2,
            coordinates.y + 2,
            fill=color.value,
            outline="",
        )
        # self._canvas.create_line(100, 200, 200, 35, fill=COLOR, width=WIDTH)
        # p = 300
        # self._canvas.create_oval(300, 300, 300+3, 300+3, fill="black", outline="")

    def draw_line(
        self, window_endpoint1: Coordinates, window_endpoint2: Coordinates, color: Color
    ):
        endpoint1 = self.controller.transform_window_to_viewport(window_endpoint1)
        endpoint2 = self.controller.transform_window_to_viewport(window_endpoint2)

        self._canvas.create_line(
            endpoint1.x, endpoint1.y, endpoint2.x, endpoint2.y, fill=color.value
        )

    def run(self):
        self._main_window.mainloop()
