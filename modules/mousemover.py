# код для перемещения мышки. работает и используется
# не трогать, дочищу сам
import time
import keyboard
from pynput.mouse import Controller


class MouseMover:
    def __init__(self) -> None:
        self.mouse = Controller()

    def _terminate(self) -> bool:

        keybind_value = "l"

        if keybind_value == "none":
            return False

        if keyboard.is_pressed(keybind_value):
            print("Script terminated.")
            return True
        
        return False

    def move_to(self, target_x, target_y, duration: float = 1):


        target_x = round(target_x)
        target_y = round(target_y)
        # Get the starting position of the mouse
        start_x, start_y = self.get_mouse_position()
        start_time = time.time()

        while time.time() - start_time <= duration:
            if self._terminate():
                exit()

            elapsed_time = time.time() - start_time
            progress = elapsed_time / duration

            # Calculate the current position based on the progress
            current_x = int(start_x + (target_x - start_x) * progress)
            current_y = int(start_y + (target_y - start_y) * progress)

            # Move the mouse to the current position
            self.set_mouse_position(current_x, current_y)

        # Set the final position to ensure accuracy
        self.set_mouse_position(target_x, target_y)


    def rel_move(self, dx: int, dy: int, duration: float):
        """
        Move the mouse relative to its current position by the specified amount.

        Args:
            dx (int): The amount to move the mouse in the x-direction.
            dy (int): The amount to move the mouse in the y-direction.
            duration (float): The duration of the movement in seconds.
        """
        # Get the current mouse position
        start_x, start_y = self.get_mouse_position()

        # Calculate the target position relative to the current position
        target_x = start_x + dx
        target_y = start_y + dy

        # Move the mouse to the target position
        self.move_to(target_x, target_y, duration)

    def set_mouse_position(self, x: int, y: int):
        """
        Set the mouse position to the specified coordinates.

        Args:
            x (int): The x-coordinate to set.
            y (int): The y-coordinate to set.
        """
        # Set the mouse position to the specified coordinates
        self.mouse.position = round(x), round(y)

    def get_mouse_position(self):

        # Get the current mouse position
        return self.mouse.position
