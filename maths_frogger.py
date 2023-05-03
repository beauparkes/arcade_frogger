import arcade
import arcade.gui
import pyglet


SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
font_title_1 = "Kenney Future"
font_body_1 = "Segoe Print"
SCREEN_TITLE = "Maths Frogger - Deluxe Edition"
DEFAULT_LINE_HEIGHT = 20
TITLE_FONT_SIZE = 30
DEFAULT_FONT_SIZE = 20
FONT_COLOUR_GREEN = [0,255,50,255]
FONT_COLOUR_RED = [255,55,0,255]


#MOVEMENT_SPEED = 10
#MOVEMENT_LIMIT = 100
#DEAD_ZONE = 0.5


class Controllers():
    def __init__(self):
        print("controllers initialised")
        self.controller_manager = pyglet.input.ControllerManager()
        self.controller_manager.on_connect = self.on_connect
        self.controller_manager.on_disconnect = self.on_disconnect

        self.controller_manager.get_controllers()
        self.has_update = True
        # Initialise Controller variables
        self.controller_0 = False
        self.controller_1 = False
        self.control_0_status = "init"
        self.control_1_status = "init"
        self.update_controller_status()


    def on_connect(self, controller):
        self.has_update = True
        print(controller._mapping['name'][-1])
        self.update_controller_status()

    def on_disconnect(self, controller):
        self.has_update = True
        print(controller._mapping['name'][-1])
        self.update_controller_status()

    def update_controller_status(self):
        # Clear controllers
        if self.controller_0:
            self.controller_0.close()
        if self.controller_1:
            self.controller_1.close()
        
        # Find controllers
        controllers = self.controller_manager.get_controllers()
        if controllers:
            # Setup controller 1
            if controllers[0]:
                print("control: 0")
                self.control_0_status = "connected"
                # Connect up controller
                self.controller_0 = controllers[0]
                self.controller_0.open()
                #self.controller_0.push_handlers(self)
            else:
                self.control_0_status = "disconnected"
            # Setup controller 2
            if len(controllers) > 1:
                print("control: 1")
                self.control_1_status = "connected"
                # Connect up controller
                self.controller_1 = controllers[1]
                self.controller_1.open()
                #self.controller_1.push_handlers(self)
            else:
                self.control_1_status = "disconnected"
        else:
            self.control_0_status = "disconnected"
            self.control_1_status = "disconnected"
            if self.controller_0:
                self.controller_0.close()
            if self.controller_1:
                self.controller_1.close()
            print("No controllers found")


class DebugWindow(arcade.Window):
    """ Debug window."""
    def __init__(self):
        super().__init__(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            SCREEN_TITLE,
            visible=False
        )


class MainWindow(arcade.Window):
    """ Main window."""
    def __init__(self, debug):
        super().__init__(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            SCREEN_TITLE,
            center_window = True,
        )
        self.debug = debug

    def on_key_press(self, key, modifiers):
        if key == arcade.key.L:
            print("Debug window opened")
            if not self.debug.visible:
                self.debug.set_visible(True)
                self.activate()
            else:
                self.debug.set_visible(False)
                self.activate()
    
    def on_close(self):
        arcade.exit()


class MenuView(arcade.View, Controllers):
    """Class that manages the 'menu' view."""
    def __init__(self):

        # Call the parent class initializer
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.mode = "endless"
        self.difficulty = "easy"
        self.controllers = Controllers()


        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)


        # Setup menu button layout
        self.red_style = {
            "font_name": font_body_1,
            "font_size": DEFAULT_FONT_SIZE,
            "font_color": arcade.color.WHITE,
            "border_width": 5, "border_color": None,
            "bg_color": arcade.color.REDWOOD,
            # Used if button is pressed
            "bg_color_pressed": arcade.color.WHITE,
            "border_color_pressed": arcade.color.GREEN_YELLOW,  
            # also used when hovered
            "font_color_pressed": arcade.color.RED,
        }

        self.green_style = {
            "font_name": font_body_1,
            "font_size": DEFAULT_FONT_SIZE,
            "font_color": arcade.color.BLACK_BEAN,
            "border_width": 5, "border_color": None,
            "bg_color": arcade.color.GREEN,
            # Used if button is pressed
            "bg_color_pressed": arcade.color.WHITE,
            "border_color_pressed": arcade.color.GREEN_YELLOW,
            # also used when hovered
            "font_color_pressed": arcade.color.RED,
        }

        self.status_style = {
            "font_name": font_title_1,
            "font_size": DEFAULT_FONT_SIZE,
            "font_color": arcade.color.BLACK_BEAN,
            "border_width": 5, "border_color": None,
            "bg_color": arcade.color.RED,
            # Used if button is pressed
            "bg_color_pressed": arcade.color.WHITE,
            "border_color_pressed": arcade.color.GREEN_YELLOW,
            # also used when hovered
            "font_color_pressed": arcade.color.RED,
        }

        self.main_layout = arcade.gui.UIBoxLayout(vertical=True, space_between=10)
        self.player_text_layout = arcade.gui.UIBoxLayout(vertical=False, space_between=10)
        self.player_layout = arcade.gui.UIBoxLayout(vertical=False, space_between=10)
        self.mode_text_layout = arcade.gui.UIBoxLayout(vertical=False, space_between=10)
        self.mode_layout = arcade.gui.UIBoxLayout(vertical=False, space_between=10)
        self.difficulty_text_layout = arcade.gui.UIBoxLayout(vertical=True, space_between=10)
        self.difficulty_layout = arcade.gui.UIBoxLayout(vertical=False, space_between=10)
        self.start_layout = arcade.gui.UIBoxLayout(vertical=False, space_between=10)
        self.controller_layout = arcade.gui.UIBoxLayout(vertical=False, space_between=10,)

        # Create tile text
        self.title_layout = arcade.gui.UILabel(
            text=SCREEN_TITLE,
            size_hint=(300, 50),
            align="center",
            font_size=TITLE_FONT_SIZE,
            font_name=font_title_1,
        )
        
        self.manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="center_x",
            anchor_y="top",
            align_y=-25,
            child=self.title_layout)
        )

        # Create player label
        player_text = arcade.gui.UILabel(
            text="Players",
            size_hint=(300, 50),
            align="center",
            font_size=DEFAULT_FONT_SIZE,
            font_name=font_title_1,
        )
        self.player_text_layout.add(player_text.with_space_around(bottom=0))
        self.main_layout.add(self.player_text_layout.with_space_around(bottom=0))

        # Create player buttons
        one_player_button = arcade.gui.UIFlatButton(text="One Player", width=200, style=self.green_style)
        one_player_button.player_num = 1
        one_player_button.on_click = self.player_select
        self.player_layout.add(one_player_button.with_space_around(bottom=20))

        two_player_button = arcade.gui.UIFlatButton(text="Two Player", width=200, style=self.red_style)
        two_player_button.player_num = 2
        two_player_button.on_click = self.player_select
        self.player_layout.add(two_player_button.with_space_around(bottom=20))

        self.main_layout.add(self.player_layout)

        #Create option label
        mode_text = arcade.gui.UILabel(
            text="Mode",
            size_hint=(300, 50),
            align="center",
            font_size=DEFAULT_FONT_SIZE,
            font_name=font_title_1,
        )
        self.mode_text_layout.add(mode_text.with_space_around(bottom=0))
        self.main_layout.add(self.mode_text_layout.with_space_around(bottom=0))

        # Add player options to main layout
        self.player_options(1)
        self.main_layout.add(self.mode_layout.with_space_around(bottom=20))

        # Add player difficulty to main layout

        difficulty_text = arcade.gui.UILabel(
            text="Difficulty",
            size_hint=(300, 50),
            align="center",
            font_size=DEFAULT_FONT_SIZE,
            font_name=font_title_1,
        )
        self.difficulty_text_layout.add(difficulty_text.with_space_around(bottom=0))
        self.main_layout.add(self.difficulty_text_layout.with_space_around(bottom=0))

        difficulty_easy = arcade.gui.UIFlatButton(text="Easy", width=130, style=self.green_style)
        difficulty_easy.difficulty_setting = "easy"
        difficulty_easy.on_click = self.set_difficulty
        self.difficulty_layout.add(difficulty_easy.with_space_around(bottom=10))

        difficulty_medium = arcade.gui.UIFlatButton(text="Medium", width=130, style=self.red_style)
        difficulty_medium.difficulty_setting = "medium"
        difficulty_medium.on_click = self.set_difficulty
        self.difficulty_layout.add(difficulty_medium.with_space_around(bottom=10))

        difficulty_hard = arcade.gui.UIFlatButton(text="Hard", width=130, style=self.red_style)
        difficulty_hard.difficulty_setting = "hard"
        difficulty_hard.on_click = self.set_difficulty
        self.difficulty_layout.add(difficulty_hard.with_space_around(bottom=10))

        self.main_layout.add(self.difficulty_layout.with_space_around(bottom=50))

        # Add start to main layout
        start_button = arcade.gui.UIFlatButton(text="START", width=200, style=self.red_style)
        start_red_style = dict(self.red_style)
        start_red_style["bg_color"] = arcade.color.BALL_BLUE
        start_button._style = start_red_style
        self.start_layout.add(start_button.with_space_around(bottom=0))
        self.main_layout.add(self.start_layout.with_space_around(bottom=20))

        # Create a widget to hold the main_layout widget, that will center the buttons
        self.manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="center_x",
            anchor_y="center_y",
            child=self.main_layout)
        )

        # Create Controller status text

        # This will initialise the controller Manager so we can start getting event calls
        self.controller_0_status_text = "Controller 1 : Loading.."
        self.controller_1_status_text = "Controller 2 : loading.."

        self.controller_0_text = arcade.gui.UILabel(
            text=self.controller_0_status_text,
            #size_hint=(100, 50),
            width=500,
            align="center",
            font_size=12,
            font_name=font_title_1,
            text_color=FONT_COLOUR_RED,
        )
        
        self.controller_1_text = arcade.gui.UILabel(
            text=self.controller_1_status_text,
            #size_hint=(100, 50),
            width=500,
            align="center",
            font_size=12,
            font_name=font_title_1,
            text_color=FONT_COLOUR_RED,
        )

        self.controller_layout.add(self.controller_0_text.with_space_around(right=20))
        self.controller_layout.add(self.controller_1_text.with_space_around(left=20))


        self.manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="center_x",
            anchor_y="bottom",
            align_y=25,
            child=self.controller_layout)
        )
        

    def update_button_style(self, event):
        event.source._style = self.green_style
        children = event.source.parent.parent.children
        for child in children:
            if not child.child is event.source:
                child.child._style = self.red_style
                child.child.trigger_render()

    def player_select(self, event):
        """Runs when a players selection is made"""
        self.update_button_style(event)
        self.player_options(event.source.player_num)

    def set_mode(self, event):
        self.mode = event.source.mode
        self.update_button_style(event)

    def player_options(self, player):
        self.mode_layout.clear()
        if player == 1:
            button_endless = arcade.gui.UIFlatButton(text="Endless", width=200, style=self.green_style)
            button_endless.mode = "endless"
            self.mode = "endless"
            button_endless.on_click = self.set_mode
            self.mode_layout.add(button_endless.with_space_around(bottom=0))

            button_timetrial = arcade.gui.UIFlatButton(text="Time Trial", width=200, style=self.red_style)
            button_timetrial.mode = "timetrial"
            button_timetrial.on_click = self.set_mode
            self.mode_layout.add(button_timetrial.with_space_around(bottom=0))

        if player == 2:
            button_coop = arcade.gui.UIFlatButton(text="Co-Op", width=200, style=self.green_style)
            button_coop.mode = "coop"
            self.mode = "coop"
            button_coop.on_click = self.set_mode
            self.mode_layout.add(button_coop.with_space_around(bottom=0))

            button_vs = arcade.gui.UIFlatButton(text="Vs", width=200, style=self.red_style)
            button_vs.mode = "vs"
            button_vs.on_click = self.set_mode
            self.mode_layout.add(button_vs.with_space_around(bottom=0))


    def update_controller_status(self):
        if self.controllers.has_update == True:

            # Controller 0
            control_0_status = self.controllers.control_0_status
            control_1_status = self.controllers.control_1_status

            controller_0_status_text = f"Controller 1 : {control_0_status}"
            self.controller_0_text.text = controller_0_status_text
            self.controller_0_text.fit_content()

            if control_0_status == "connected":
                self.controller_0_text.label.color = FONT_COLOUR_GREEN
            else:
                self.controller_0_text.label.color = FONT_COLOUR_RED

            # Controller 1
            controller_1_status_text = f"Controller 2 : {control_1_status}"
            self.controller_1_text.text = controller_1_status_text
            self.controller_1_text.fit_content()

            if control_1_status == "connected":
                self.controller_1_text.label.color = FONT_COLOUR_GREEN
            else:
                self.controller_1_text.label.color = FONT_COLOUR_RED

            self.controller_0_text.trigger_render()
            self.controller_1_text.trigger_render()

            print("controllers updated")
            self.controllers.has_update = False


    def set_difficulty(self, event):
        self.difficulty = event.source.difficulty_setting
        self.update_button_style(event)

    def on_draw(self):
        """Draw the menu."""
        self.clear()
        size = self.window.get_size()
        arcade.draw_rectangle_filled(size[0]/2, size[1], size[0], 180, arcade.color.DARK_IMPERIAL_BLUE)
        arcade.draw_rectangle_filled(size[0]/2, 0, size[0], 150, arcade.color.DARK_IMPERIAL_BLUE)
        self.manager.draw()
        

    def on_update(self, delta_time):
        self.update_controller_status()


class Game():
    def __init__(self):
        self.gameWindow = MainWindow
        self.gameDebug = DebugWindow


def main():
    """Startup"""
    game = Game()
    debug = game.gameDebug()
    mainWindow = game.gameWindow(debug)
    menu_view = MenuView()
    mainWindow.show_view(menu_view)
    arcade.run()

if __name__ == "__main__":
    main()