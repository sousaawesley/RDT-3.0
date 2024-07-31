from cursesmenu import CursesMenu
from cursesmenu.items import FunctionItem, SubmenuItem
from Server import Server
import threading

class ServerMenu:
    def __init__(self):
        self.server = Server()
        self.main_menu = CursesMenu("Server Menu", "Control and Monitor Server")
        self.network_conditions_menu = CursesMenu("Network Conditions", "Select a Network Condition")

        self.add_main_menu_items()
        self.add_network_conditions_menu_items()

        self.server_thread = threading.Thread(target=self.server.listen, daemon=True)
        self.server_thread.start()

    def add_main_menu_items(self):
        self.main_menu.append_item(SubmenuItem("Network Conditions", self.network_conditions_menu))
        self.main_menu.append_item(FunctionItem("Exit", self.exit))

    def add_network_conditions_menu_items(self):
        self.network_conditions_menu.append_item(FunctionItem("Set Network Condition to Drop", self.set_network_condition, args=("drop",)))
        self.network_conditions_menu.append_item(FunctionItem("Set Network Condition to Corrupt", self.set_network_condition, args=("corrupt",)))
        self.network_conditions_menu.append_item(FunctionItem("Set Network Condition to Delay", self.set_network_condition, args=("delay",)))
        self.network_conditions_menu.append_item(FunctionItem("Set Network Condition to Pass", self.set_network_condition, args=("pass",)))
        self.network_conditions_menu.append_item(FunctionItem("Back to Main Menu", self.back_to_main_menu))

    def set_network_condition(self, condition):
        try:
            self.server.set_network_condition(condition)
            print(f"Network condition set to: {condition}")
        except ValueError as e:
            print(e)

    def exit(self):
        print("Exiting...")
        exit(0)

    def back_to_main_menu(self):
        self.main_menu.show()

    def start(self):
        self.main_menu.show()


server_menu = ServerMenu()
server_menu.start()
