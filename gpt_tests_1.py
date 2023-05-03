import arcade

class Window1(arcade.Window):
    def __init__(self):
        super().__init__(640, 480, "Window 1")
        self.window2_visible = True

    def on_draw(self):
        arcade.start_render()
        # Draw the contents of Window 1 here

    def on_key_press(self, key, modifiers):
        if key == arcade.key.V:
            window2 = Window2()
            self.window2_visible = not self.window2_visible
            window2.set_visible(self.window2_visible)
            if self.window2_visible:
                window2.set_exclusive_mouse(True)
            else:
                window2.set_exclusive_mouse(False)

class Window2(arcade.Window):
    def __init__(self):
        super().__init__(320, 240, "Window 2")

# Create instances of the windows
window1 = Window1()


# Run the game loop
arcade.run()