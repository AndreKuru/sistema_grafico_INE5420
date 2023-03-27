from tkinter import Tk, Frame, Canvas, Label, Button, Toplevel, Listbox

WIDTH = 5
COLOR = "green"

main_window = Tk()

viewport_frame = Frame(main_window)
viewport_frame.pack(side="right")

canvas = Canvas(viewport_frame, width=960, height=540, background="white", border=10, relief="raised")
canvas.pack()
canvas.create_line(100, 200, 200, 35, fill=COLOR, width=WIDTH)
canvas.create_oval(300, 300, 350, 350, fill=COLOR, width=WIDTH, outline="")

###
creation_of_object = Toplevel(main_window)
creation_of_object.title("Creation of object")

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

main_window.mainloop()