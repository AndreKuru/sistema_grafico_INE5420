from tkinter import Tk, Frame, Canvas, Label, Button, Toplevel, Listbox, Entry

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
main_window = Tk()

viewport_frame = Frame(main_window)
viewport_frame.pack(side="right")

canvas = Canvas(viewport_frame, width=960, height=540, background="white", border=10, relief="raised")
canvas.pack()
canvas.create_line(100, 200, 200, 35, fill=COLOR, width=WIDTH)
p = 300
canvas.create_oval(p, p, p+3, p+3, fill=COLOR, outline="")

###
create_point = Toplevel(main_window)
create_point.title("Create point")

create_line = Toplevel(main_window)
create_line.title("Create line")

create_wireframe = Toplevel(main_window)
create_wireframe.title("Create wireframe")

window_function = Toplevel(main_window)
window_function.title("Window Functions")

'''
window_function = Frame(main_window, highlightbackground="grey", highlightthickness=2)
window_function.pack(side="left")

Label(window_function, text="Functions menu").pack()
'''
#Display File
display_file_frame = Frame(window_function)
display_file_frame.pack()

display_file_label = Label(display_file_frame, text="Display File")
display_file_label.pack()

display_file = Listbox(display_file_frame)
display_file.pack()

#Window control
window_control_frame = Frame(window_function)
window_control_frame.pack()

window_control_label = Label(window_control_frame, text="Window control")
window_control_label.pack()

#Directions
directions = Frame(window_function)
directions.pack()

up_button = Button(directions, text="Up")
up_button.pack(side="top")

down_button = Button(directions, text="Down")
down_button.pack(side="bottom")

left_button = Button(directions, text="Left")
left_button.pack(side="left")

right_button = Button(directions, text="Right")
right_button.pack(side="right")

#Zoom
zoom = Frame(window_function)
zoom.pack()

zoom_in_button = Button(zoom, text="+")
zoom_in_button.pack(side="right")

zoom_out_button = Button(zoom, text="-")
zoom_out_button.pack(side="left")


#Creation of point - still not working
point_coord_frame = Frame(create_point)
point_coord_frame.pack()

ask_coordinates(point_coord_frame)

create_point_button = Button(point_coord_frame, text="Create")
create_point_button.pack()

# Creation of line
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

wireframe_coord_frame = Frame(create_wireframe)
wireframe_coord_frame.pack()

ask_several_coordinates(wireframe_coord_frame)

create_wireframe_button = Button(wireframe_coord_frame, text="Create")
create_wireframe_button.pack()

main_window.mainloop()
