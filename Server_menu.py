import curses
import threading
import time
from Server import Server
from collections import deque

class ServerMenu:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()


        self.control_win = curses.newwin(self.height, self.width // 2, 0, 0)
        self.log_win = curses.newwin(self.height, self.width // 2, 0, self.width // 2)

        self.control_win.box()
        self.log_win.box()

        self.server = Server()
        self.server_thread = threading.Thread(target=self.server.listen, daemon=True)
        self.server_thread.start()

        self.logs = deque(maxlen=self.height - 2)

        self.update_logs_thread = threading.Thread(target=self.update_logs, daemon=True)
        self.update_logs_thread.start()

        self.main_menu()   

    def main_menu(self):
        
        self.set_null_condition()

        while True:
            self.control_win.clear()
            self.control_win.box()
            self.control_win.addstr(1, 1, "Sender Network Conditions")
            self.control_win.addstr(2, 1, "1. Set Sender Condition to Drop")
            self.control_win.addstr(3, 1, "2. Set Sender Condition to Corrupt")
            self.control_win.addstr(4, 1, "3. Set Server Condition to Delay")
            self.control_win.addstr(5, 1, "4. Set Sender Condition to Pass")
            self.control_win.addstr(6, 1, "5. Set Receiver Condition to Drop")
            self.control_win.addstr(7, 1, "6. Set Receiver Condition to Corrupt")
            self.control_win.addstr(8, 1, "7. Set Receiver Condition to Pass")
            self.control_win.addstr(9, 1, "8. Exit")

            key = self.stdscr.getch()
            self.handle_menu_input(key)

    def handle_menu_input(self, key):
        
        if key == ord('0'):
            self.set_null_condition()
        if key == ord('1'):
            self.set_sender_condition("drop")
        if key == ord('2'):
            self.set_sender_condition("corrupt")
        if key == ord('3'):
            self.set_sender_condition("delay")
        if key == ord('4'):
            self.set_sender_condition("pass")
        
        #receiver
        if key == ord('5'):
            self.set_receiver_condition("drop")
        if key == ord('6'):
            self.set_receiver_condition("corrupt")
        if key == ord('7'):
            self.set_receiver_condition("pass")
        if key == ord('8'):
            curses.endwin()
            exit(0)

            

    def set_null_condition(self):
        try:
            self.control_win.addstr(self.height - 1, 1, f" [SERVER MENU] ", curses.A_BOLD)
        except ValueError as e:
            self.control_win.addstr(self.height - 1, 1, str(e), curses.A_BOLD)
        self.control_win.refresh()

    def set_sender_condition(self, condition):
        try:
            self.server.set_net_sndr_condition(condition)
            self.control_win.addstr(self.height - 1, 1, f" [SERVER MENU] Sender network condition set to: {condition}", curses.A_BOLD)
        except ValueError as e:
            self.control_win.addstr(self.height - 1, 1, str(e), curses.A_BOLD)
        self.control_win.refresh()

    def set_receiver_condition(self, condition):
        try:
            self.server.set_net_rcv_condition(condition)
            self.control_win.addstr(self.height - 1, 1, f" [SERVER MENU] Receiver network condition set to: {condition}", curses.A_BOLD)
        except ValueError as e:
            self.control_win.addstr(self.height - 1, 1, str(e), curses.A_BOLD)
        self.control_win.refresh()

    def update_logs(self):
        while True:
            new_logs = self.server.get_logs()

            self.logs.clear()
            self.logs.extend(new_logs)

            self.log_win.clear()
            self.log_win.box()
            for i, log in enumerate(self.logs):
                self.log_win.addstr(i + 1, 1, log)
            self.log_win.refresh()

            time.sleep(2) 

def main(stdscr):
    curses.curs_set(0)
    menu = ServerMenu(stdscr)

curses.wrapper(main)
