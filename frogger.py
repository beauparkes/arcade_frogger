import arcade
import arcade.gui
from dataclasses import dataclass
import pyglet


pyglet.options["xinput_controllers"] = False

SPRITE_SCALING = 1

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 1200
SCREEN_TITLE = "Maths Frogger - Deluxe Edition"
DEFAULT_LINE_HEIGHT = 45
DEFAULT_FONT_SIZE = 20

MOVEMENT_SPEED = 10
MOVEMENT_LIMIT = 100
DEAD_ZONE = 0.5

@dataclass
class Burst:
    """ Track for each burst. """
    buffer: arcade.gl.Buffer
    vao: arcade.gl.Geometry
    start_time: float

class QuitButton(arcade.gui.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        arcade.exit()

class MyWindow(arcade.Window):
    """ Main window"""
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)
        self.burst_list = []

        # Program to visualize the points
        self.program = self.ctx.load_program(
            vertex_shader="shader/vertex_shader.glsl",
            fragment_shader="shader/fragment_shader.glsl",
        )

        self.ctx.enable_only(self.ctx.BLEND)

class MenuView(arcade.View):
    """Class that manages the 'menu' view."""

    def __init__(self):

        # Call the parent class initializer
        super().__init__()
        self.num_players = 1
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        self.red_style = {
            "font_name": ("calibri", "arial"),
            "font_size": 15,
            "font_color": arcade.color.WHITE,
            "border_width": 2,
            "border_color": None,
            "bg_color": arcade.color.REDWOOD,

            # used if button is pressed
            "bg_color_pressed": arcade.color.WHITE,
            "border_color_pressed": arcade.color.RED,  # also used when hovered
            "font_color_pressed": arcade.color.RED,
        }

        self.green_style = {
            "font_name": ("calibri", "arial"),
            "font_size": 15,
            "font_color": arcade.color.GREEN_YELLOW,
            "border_width": 2,
            "border_color": None,
            "bg_color": arcade.color.GRAPE,

            # used if button is pressed
            "bg_color_pressed": arcade.color.WHITE,
            "border_color_pressed": arcade.color.RED,  # also used when hovered
            "font_color_pressed": arcade.color.RED,
        }
        
        self.main_layout = arcade.gui.UIBoxLayout(vertical=True, space_between=10)
        self.player_layout = arcade.gui.UIBoxLayout(vertical=False, space_between=10)
        self.player_option_layout = arcade.gui.UIBoxLayout(vertical=False, space_between=10)

        # Create a vertical BoxGroup to align buttons
        #self.main_player_group = arcade.gui.UIBoxLayout()
        #self.main_button_group = arcade.gui.UIBoxLayout()

        # Create player buttons
        one_player_button = arcade.gui.UIFlatButton(text="One Player", width=200, style=self.red_style)
        self.player_layout.add(one_player_button.with_space_around(bottom=20))

        two_player_button = arcade.gui.UIFlatButton(text="Two Player", width=200, style=self.green_style)
        self.player_layout.add(two_player_button.with_space_around(bottom=20))

        self.main_layout.add(self.player_layout)


        # number of player options
        event = ""
        self.one_player_select(event)
        self.main_layout.add(self.player_option_layout)



        # Again, method 1. Use a child class to handle events.
        quit_button = QuitButton(text="Quit", width=200)
        self.main_layout.add(quit_button)

        # --- Method 2 for handling click events,
        # assign self.on_click_start as callback
        one_player_button.on_click = self.one_player_select
        two_player_button.on_click = self.two_player_select

        # --- Method 3 for handling click events,
        # use a decorator to handle on_click events
        #@settings_button.event("on_click")
        #def on_click_settings(event):
        #    print("Settings:", event)

        # Create a widget to hold the main_button_group widget, that will center the buttons
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.main_layout)
        )

        controllers = arcade.get_game_controllers()
        # If we have any...
        if controllers:
            # Grab the first one in  the list
            self.controller = controllers[0]

            # Open it for input
            self.controller.open()

            # Push this object as a handler for controller events.
            # Required for the on_joy* events to be called.
            self.controller.push_handlers(self)
            print("Controllers were found")
            #print(dir(self.controller))
            #print(self.controller.button_controls)
            #print(self.controller.buttons)
            self.enter_msg = "PRESS 'A BUTTON' TO JUMP IN"
        else:
            # Handle if there are no controllers.
            print("No controllers found")
            self.controller = None
            self.enter_msg = "PRESS 'ENTER' TO JUMP IN"

    def on_resize(self, SCREEN_WIDTH, SCREEN_HEIGHT):
        #super().on_resize(WIDTH, HEIGHT)
        print(f"Window resized to: {SCREEN_WIDTH}, {SCREEN_HEIGHT}")
    

    def on_draw(self):
        """Draw the menu"""
        self.clear()
        self.manager.draw()
        #arcade.start_render()


    def on_update(self, delta_time):
        if self.controller:
            if self.controller.buttons[0]:
                game_view = GameView()
                game_view.setup()
                self.window.show_view(game_view)

    def on_key_press(self, key, _modifiers):
        """If user hits enter, begin gameview"""
        if key == arcade.key.ENTER:
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)

    def player_menu(self):
        """ Initialises the player menu"""

        #players is set to 1
        if self.num_players == 1:
            self.player_option_layout.clear()
            one_player_option1 = arcade.gui.UIFlatButton(text="Standard", width=200)
            one_player_option2 = arcade.gui.UIFlatButton(text="Time Trial", width=200)
            self.player_option_layout.add(one_player_option1.with_space_around(bottom=20))
            self.player_option_layout.add(one_player_option2.with_space_around(bottom=20))

            one_player_option1.on_click = self.start_game_standard
            one_player_option2.on_click = self.start_game_standard

            
        #players is set to 2
        if self.num_players == 2:
            self.player_option_layout.clear()
            two_player_option1 = arcade.gui.UIFlatButton(text="Versus", width=200)
            two_player_option2 = arcade.gui.UIFlatButton(text="Co-Op", width=200)
            self.player_option_layout.add(two_player_option1.with_space_around(bottom=20))
            self.player_option_layout.add(two_player_option2.with_space_around(bottom=20))

            two_player_option1.on_click = self.start_game_standard
            two_player_option2.on_click = self.start_game_standard

    def one_player_select(self, event):
        self.num_players = 1
        self.player_menu()
        if event:
            #self.player_layout.clear()
            self.main_layout.clear()

            #one_player_button = arcade.gui.UIFlatButton(text="One Player", width=200, style=self.red_style)
            #two_player_button = arcade.gui.UIFlatButton(text="Two Player", width=200, style=self.green_style)
            #self.player_layout.add(one_player_button.with_space_around(bottom=20),)
            #self.player_layout.add(two_player_button.with_space_around(bottom=20))
            quit_button = QuitButton(text="Quit", width=200)
            self.main_layout.add(self.player_layout)
            self.main_layout.add(quit_button)


    def two_player_select(self, event):
        self.num_players = 2
        self.player_menu()

    def start_game_standard(self, event):
        game_view = GameView()
        game_view.setup()
        self.window.show_view(game_view)


class Player(arcade.Sprite):

    def __init__(self, filename, scale, last_x=0, last_y=0, moving_x=0, moving_y=0):
        super().__init__(filename, scale)

        self.last_x = last_x
        self.last_y = last_y
        self.moving_x = moving_x
        self.moving_y = moving_y

    def update(self):
        # Move the player
        # Remove these lines if physics engine is moving player.
        self.center_x += self.change_x
        self.center_y += self.change_y

        if abs(self.center_y - self.last_y) > MOVEMENT_LIMIT and self.moving_y == 1:
            self.change_y = 0
            self.update_player_texture(0)
            self.last_y = 0
            self.moving_y = 0
            if self.bottom <= 0:
                self.bottom = 0
            elif self.top >= SCREEN_HEIGHT:
                self.top = SCREEN_HEIGHT
        if abs(self.center_x - self.last_x) > MOVEMENT_LIMIT and self.moving_x == 1:
            self.change_x = 0
            self.update_player_texture(0)
            self.last_x = 0
            self.moving_x = 0
            if self.left <= 0:
                self.left = 0
            elif self.right >= SCREEN_WIDTH:
                self.right = SCREEN_WIDTH

    def update_player_texture(self, val):
        self.set_texture(val)


class GameView(arcade.View):
    """
    Main application class.
    """

    def __init__(self):
        """
        Initializer
        
        """

        # Call the parent class initializer
        super().__init__()

        # Variables that will hold sprite lists
        self.player_list = None

        # Set up the player info
        self.player_sprite = None

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.controller_dir_reset = True

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

        # Get list of game controllers that are available
        controllers = arcade.get_game_controllers()

        # If we have any...
        if controllers:
            # Grab the first one in  the list
            self.controller = controllers[0]

            # Open it for input
            self.controller.open()

            # Push this object as a handler for controller events.
            # Required for the on_joy* events to be called.
            self.controller.push_handlers(self)
            #print("Controllers were found")
            #print(dir(self.controller))
            #print(self.controller.button_controls)
            #print(self.controller.buttons)
        else:
            # Handle if there are no controllers.
            print("No controllers found")
            self.controller = None

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = Player(":resources:images/enemies/frog.png", SPRITE_SCALING)
        self.player_sprite.append_texture(arcade.load_texture(":resources:images/enemies/frog_move.png"))
        self.player_sprite.center_x = SCREEN_WIDTH/2
        self.player_sprite.bottom = 0
        self.player_list.append(self.player_sprite)

    def on_draw(self):
        """ Render the screen. """

        # Clear the screen
        self.clear()

        # Draw all the sprites.
        self.player_list.draw()

    def update_player_speed(self):
        self.player_sprite.update_player_texture(1)

        if self.up_pressed and not self.down_pressed:
            self.player_sprite.moving_y = 1
            self.player_sprite.change_y = MOVEMENT_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.moving_y = 1
            self.player_sprite.change_y = -MOVEMENT_SPEED
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.moving_x = 1
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.moving_x = 1
            self.player_sprite.change_x = MOVEMENT_SPEED

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Call update to move the sprite
        # If using a physics engine, call update player to rely on physics engine
        # for movement, and call physics engine here.
        self.player_list.update()

        if self.controller:

            # use bellow to see which button was pressed
            #print(self.controller.buttons)

            # controller Up
            if self.controller.y < (DEAD_ZONE*-1) and self.player_sprite.moving_y == 0 and self.controller_dir_reset:
                self.up_pressed = True
                self.player_sprite.last_y = self.player_sprite.center_y
                self.update_player_speed()
                self.controller_dir_reset = False

            # controller Down
            if self.controller.y > DEAD_ZONE and self.player_sprite.moving_y == 0 and self.controller_dir_reset:
                self.down_pressed = True
                self.player_sprite.last_y = self.player_sprite.center_y
                self.update_player_speed()
                self.controller_dir_reset = False

            # controller Right
            if self.controller.x > DEAD_ZONE and self.player_sprite.moving_x == 0 and self.controller_dir_reset:
                self.right_pressed = True
                self.player_sprite.last_x = self.player_sprite.center_x
                self.update_player_speed()
                self.controller_dir_reset = False

            # controller Left
            if self.controller.x < (DEAD_ZONE*-1) and self.player_sprite.moving_x == 0 and self.controller_dir_reset:
                self.left_pressed = True
                self.player_sprite.last_x = self.player_sprite.center_x
                self.update_player_speed()
                self.controller_dir_reset = False

            # controler dir reset
            if abs(self.controller.x) < DEAD_ZONE and abs(self.controller.y) < DEAD_ZONE:
                self.up_pressed = False
                self.down_pressed = False
                self.left_pressed = False
                self.right_pressed = False
                self.controller_dir_reset = True

            #if self.controller.buttons[0]:
            #    pass
            if self.controller.buttons[1]:
                menu_view = MenuView()
                self.window.show_view(menu_view)


    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
            self.player_sprite.last_y = self.player_sprite.center_y
            self.update_player_speed()
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
            self.player_sprite.last_y = self.player_sprite.center_y
            self.update_player_speed()
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
            self.player_sprite.last_x = self.player_sprite.center_x
            self.update_player_speed()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
            self.player_sprite.last_x = self.player_sprite.center_x
            self.update_player_speed()
        if key == arcade.key.ESCAPE:
            menu_view = MenuView()
            self.window.show_view(menu_view)

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False


def main():
    """Startup"""
    window = MyWindow()
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()