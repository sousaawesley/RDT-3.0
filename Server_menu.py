from cursesmenu import CursesMenu
from cursesmenu.items import FunctionItem, SubmenuItem
from Server import Server
import threading
import time

class ServerMenu:
    def __init__(self):
        self.server = Server()
        self.main_menu = CursesMenu("Server Menu", "Control and Monitor Server")
        
        self.sender_conditions_menu = CursesMenu("Sender Network Conditions", "Select a Network Condition for Sender")
        self.receiver_conditions_menu = CursesMenu("Receiver Network Conditions", "Select a Network Condition for Receiver")
        self.logs_menu = CursesMenu("Server Logs", "View Server Logs")

        self.add_main_menu_items()
        self.add_sender_conditions_menu_items()
        self.add_receiver_conditions_menu_items()
        self.add_logs_menu_items()

        # Start server in a separate thread
        self.server_thread = threading.Thread(target=self.server.listen, daemon=True)
        self.server_thread.start()

        # Start log updater in a separate thread
        self.log_updater_thread = threading.Thread(target=self.update_logs, daemon=True)
        self.log_updater_thread.start()

    def add_main_menu_items(self):
        self.main_menu.items.append(SubmenuItem("Sender Network Conditions", self.sender_conditions_menu))
        self.main_menu.items.append(SubmenuItem("Receiver Network Conditions", self.receiver_conditions_menu))
        self.main_menu.items.append(SubmenuItem("View Server Logs", self.logs_menu))
        self.main_menu.items.append(FunctionItem("Exit", self.exit))

    def add_sender_conditions_menu_items(self):
        self.sender_conditions_menu.items.append(FunctionItem("Set Sender Condition to Drop", self.set_sender_condition, args=("drop",)))
        self.sender_conditions_menu.items.append(FunctionItem("Set Sender Condition to Corrupt", self.set_sender_condition, args=("corrupt",)))
        self.sender_conditions_menu.items.append(FunctionItem("Set Sender Condition to Delay", self.set_sender_condition, args=("delay",)))
        self.sender_conditions_menu.items.append(FunctionItem("Set Sender Condition to Pass", self.set_sender_condition, args=("pass",)))
        self.sender_conditions_menu.items.append(FunctionItem("Back to Main Menu", self.back_to_main_menu))

    def add_receiver_conditions_menu_items(self):
        self.receiver_conditions_menu.items.append(FunctionItem("Set Receiver Condition to Drop", self.set_receiver_condition, args=("drop",)))
        self.receiver_conditions_menu.items.append(FunctionItem("Set Receiver Condition to Corrupt", self.set_receiver_condition, args=("corrupt",)))
        self.receiver_conditions_menu.items.append(FunctionItem("Set Receiver Condition to Delay", self.set_receiver_condition, args=("delay",)))
        self.receiver_conditions_menu.items.append(FunctionItem("Set Receiver Condition to Pass", self.set_receiver_condition, args=("pass",)))
        self.receiver_conditions_menu.items.append(FunctionItem("Back to Main Menu", self.back_to_main_menu))

    def add_logs_menu_items(self):
        self.logs_menu.items.append(FunctionItem("Show Logs", self.show_logs))
        self.logs_menu.items.append(FunctionItem("Back to Main Menu", self.back_to_main_menu))

    def set_sender_condition(self, condition):
        try:
            self.server.set_net_sndr_condition(condition)
            print(f"Sender network condition set to: {condition}")
        except ValueError as e:
            print(e)

    def set_receiver_condition(self, condition):
        try:
            self.server.set_net_rcv_condition(condition)
            print(f"Receiver network condition set to: {condition}")
        except ValueError as e:
            print(e)

    def show_logs(self):
        pass

    def update_logs(self):
        while True:
            logs = self.server.get_logs()
            if logs:
                # Clear screen and update with new logs
                self.logs_menu.clear()
                for log in logs:
                    self.logs_menu.add_item(FunctionItem(log, self.inut))
            time.sleep(5)  # Update every 5 seconds

    def inut(self):
        pass

    def exit(self):
        print("Exiting...")
        exit(0)

    def back_to_main_menu(self):
        self.main_menu.show()

    def start(self):
        self.main_menu.show()

if __name__ == "__main__":
    server_menu = ServerMenu()
    server_menu.start()
