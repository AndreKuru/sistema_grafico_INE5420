from controller import Controller
from view import Graphic_Viewer


def main():
    controller = Controller()
    drawer = Graphic_Viewer(controller=controller)
    drawer.run()

main()