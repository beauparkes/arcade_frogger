import arcade
import arcade.gui
import pyglet
import random


SCREEN_WIDTH = 1040
SCREEN_HEIGHT = 1035
font_title_1 = "Kenney Future"
font_body_1 = "Segoe Print"
SCREEN_TITLE = "Maths Frogger - Deluxe Edition"
DEFAULT_LINE_HEIGHT = 20
TITLE_FONT_SIZE = 30
DEFAULT_FONT_SIZE = 20
FONT_COLOUR_GREEN = [0,255,50,255]
FONT_COLOUR_RED = [255,55,0,255]
SPRITE_SCALING = 0.5


MOVEMENT_SPEED = 10
MOVEMENT_LIMIT_X = (SCREEN_WIDTH  / 12) - 10
MOVEMENT_LIMIT_Y = (SCREEN_HEIGHT + 0.5) / 16
DEAD_ZONE = 0.5

def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]


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
    """ Debug window, currently not well implimented."""
    def __init__(self):
        super().__init__(
            int(SCREEN_WIDTH/2),
            int(SCREEN_HEIGHT/2),
            SCREEN_TITLE,
            visible=False,
       )

    def on_close(self):
        arcade.exit()


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
            if not self.debug.visible:
                print("Debug window opened")
                self.debug.set_visible(True)
                self.activate()
            else:
                print("Debug window closed")
                self.debug.set_visible(False)
                self.activate()

    def on_resize(self, width, height):
        # this function is called any time the window is resized
        print(f"{width} {height}")

    def on_close(self):
        arcade.exit()


class MenuView(arcade.View, Controllers):
    """Class that manages the 'menu' view."""
    def __init__(self):

        # Call the parent class initializer
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.players = 1
        self.mode = "endless"
        self.difficulty = "easy"
        self.controllers = Controllers()

        # Setup base background colour
        arcade.set_background_color(arcade.color.BLACK)

        # Setup menu button layouts
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
        
        # Create all layouts
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
        # Add title to manager
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
        # Add player label to layout
        self.player_text_layout.add(player_text.with_space_around(bottom=0))
        self.main_layout.add(self.player_text_layout.with_space_around(bottom=0))

        # Create player1 buttons
        one_player_button = arcade.gui.UIFlatButton(text="One Player", width=200, style=self.green_style)
        one_player_button.player_num = 1
        one_player_button.on_click = self.player_select
        self.player_layout.add(one_player_button.with_space_around(bottom=20))
        # Create player2 buttons
        two_player_button = arcade.gui.UIFlatButton(text="Two Player", width=200, style=self.red_style)
        two_player_button.player_num = 2
        two_player_button.on_click = self.player_select
        self.player_layout.add(two_player_button.with_space_around(bottom=20))
        # Add player layout to main layout
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
        # Add difficulty label to layout
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
        start_button.on_click = self.startGame
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
        self.players = event.source.player_num

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

    def startGame(self, event):
        game_view = GameView(self.players, self.mode, self.difficulty, self.controllers)
        game_view.player_setup()
        game_view.level_setup()
        self.window.show_view(game_view)


class Player(arcade.Sprite):
    """ Player class """
    def __init__(self, scale):
        super().__init__()
        self.scale = scale
        self.last_x = 0
        self.last_y = 0
        self.moving_x = 0
        self.moving_y = 0
        self.flipped_v = 0
        frog_idle = ":resources:images/enemies/frog.png"
        frog_jump_lr = ":resources:images/enemies/frog_move.png"
        frog_jump_c = ":resources:images/enemies/slimeGreen.png"
        frog_dead = ":resources:images/enemies/wormGreen_dead.png"
        self.frog_idle_pair = load_texture_pair(frog_idle)
        self.frog_jump_lr_pair = load_texture_pair(frog_jump_lr)
        self.frog_jump_c_pair = load_texture_pair(frog_jump_c)
        self.frog_dead_pair = load_texture_pair(frog_dead)
        self.texture = self.frog_idle_pair[0]
        self.texture_direction = 0
        self.landable_collided_sprites = []
        self.collide_offset = "none"
        self.death_collided_sprites = []

    def update(self):
        # Move the player
        # Remove these lines if physics engine is moving player.

        # if death
        print(self.top)
        if self.death_collided_sprites:
            if not self.landable_collided_sprites:
                self.texture = self.frog_dead_pair[0]

        if self.change_x  == 0 and self.change_y == 0:
            if not self.landable_collided_sprites:
                return
            if self.collide_offset == "none":
                self.collide_offset = self.center_x - self.landable_collided_sprites[0].center_x
            else:
                self.set_position(self.landable_collided_sprites[0].center_x + self.collide_offset, self.center_y)

        else:
            self.collide_offset = "none"
            self.center_x += self.change_x
            self.center_y += self.change_y

            if abs(self.center_y - self.last_y) >= MOVEMENT_LIMIT_Y and self.moving_y == 1:
                self.change_y = 0
                self.update_player_texture("idle")
                self.last_y = 0
                self.moving_y = 0
                if self.bottom <= 0:
                    self.bottom = 0
                elif self.top >= SCREEN_HEIGHT:
                    self.top = SCREEN_HEIGHT
            if abs(self.center_x - self.last_x) >= MOVEMENT_LIMIT_X and self.moving_x == 1:
                self.change_x = 0
                self.update_player_texture("idle")
                self.last_x = 0
                self.moving_x = 0
                if self.left <= 0:
                    self.left = 0
                elif self.right >= SCREEN_WIDTH:
                    self.right = SCREEN_WIDTH

    def update_player_texture(self, texture_state):
        if texture_state == "idle":
            self.texture = self.frog_idle_pair[self.texture_direction]
        if texture_state == "jump_lr":
            self.texture = self.frog_jump_lr_pair[self.texture_direction]
        if texture_state == "jump_c":
            self.texture = self.frog_jump_c_pair[self.texture_direction]
        if texture_state == "dead":
            self.texture = self.frog_dead_pair[self.texture_direction]


class GameView(arcade.View):
    """
    Main application class.

    """
    def __init__(self, players, mode, difficulty, controllers):
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

        # menu class varaibles
        self.players = players
        self.mode = mode
        self.difficulty = difficulty
        self.controllers = controllers

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

    def player_setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = Player(SPRITE_SCALING)
        self.player_sprite.center_x = SCREEN_WIDTH/2
        self.player_sprite.bottom = 0
        self.player_list.append(self.player_sprite)


    
    def level_setup(self):
        """ A function that will setup the frogger game enemies which includes logs, turtles, cars, and trucks.

        """
        # A list of all the logs
        self.log_list = arcade.SpriteList()

        # A list of all the turtles
        self.turtle_list = arcade.SpriteList()

        # A list of all the cars
        self.car_list = arcade.SpriteList()

        # A list of all the trucks
        self.truck_list = arcade.SpriteList()

        # Setup water
        self.water_rect = arcade.create_rectangle_filled(SCREEN_WIDTH*0.5, SCREEN_HEIGHT*0.75, 3000, 600, arcade.color.BLUE)
        
        self.water_list = arcade.SpriteList()
        water_sprite = ":resources:images/tiles/water.png"
        self.water = arcade.Sprite(water_sprite, SPRITE_SCALING*17)
        self.water.center_x = SCREEN_WIDTH / 2
        self.water.center_y = SCREEN_HEIGHT + 35
        #self.water_list.append(self.water_sprite)

        # A list of all the land sprites
        # at the moment this is just whatever is not water and not the road.

        # Setup road
        self.road_rect = arcade.create_rectangle_filled(SCREEN_WIDTH*0.5, SCREEN_HEIGHT*0.3+15, 3000, 400, arcade.color.BLACK)

        # Death object list
        # A list of all the trucks
        self.death_list = arcade.SpriteList()
        self.death_list.append(self.water)

    def create_turtle(self, index, height_offset, x_min, x_max):
        """ A function that will create a turtle sprite and add it to the turtle list.
        """
        turtle_angle = 180
        turtle_sprite = ":resources:images/topdown_tanks/treeBrown_small.png"
        turtle = arcade.Sprite(turtle_sprite, SPRITE_SCALING*2)
        turtle.center_x = SCREEN_WIDTH
        turtle.center_y = SCREEN_HEIGHT - height_offset
        turtle.angle = turtle_angle
        turtle.change_x = random.randrange(x_min, x_max)
        turtle.index = index
        self.turtle_list.append(turtle)

    def moving_turtles(self, delta_time):
        """ A function that will move all the turtles in the turtle list along the x axis and reset them if they go off screen.
        """

        # Adjust odds based on delta-time
        turtle0_odds = int(90 * (1 / 60 * delta_time))
        turtle1_odds = int(120 * (1 / 60 * delta_time))
        turtle2_odds = int(120 * (1 / 60 * delta_time))
        self.turtle_blocking = [False, False, False]
        
        for found_turtle in self.turtle_list:
            if found_turtle.right > SCREEN_WIDTH-200:
                self.turtle_blocking[found_turtle.index] = True
        #print(self.turtle_blocking)

        # Add turtle 0
        if random.randrange(turtle0_odds+1) == 0:
            if not self.turtle_blocking[0]:
                self.create_turtle(0, 120, 2, 3)
        
        # Add turtle 1
        if random.randrange(turtle1_odds+1) == 0:
            if not self.turtle_blocking[1]:
                self.create_turtle(1, 260, 2, 3)

        # Add turtle 2
        if random.randrange(turtle2_odds+1) == 0:
            if not self.turtle_blocking[2]:
                self.create_turtle(2, 465, 2, 3)

        for turtle in self.turtle_list:
            turtle.center_x -= turtle.change_x
            if turtle.right < 0:
                turtle.remove_from_sprite_lists()

    def create_log(self, index, height_offset, x_min, x_max):
        """ A function that will create a log sprite and add it to the log list.
        """
        log_angle = 180
        log_sprite = ":resources:images/tiles/bridgeB.png"
        log = arcade.Sprite(log_sprite, SPRITE_SCALING*2)
        log.center_x = log.left
        log.center_y = SCREEN_HEIGHT - height_offset
        log.angle = log_angle
        log.change_x = random.randrange(x_min, x_max)
        log.index = index
        self.log_list.append(log)

    def moving_logs(self, delta_time):
        """ A function that will move all the logs in the log list along the x axis and reset them if they go off screen.
        """

        # Adjust odds based on delta-time
        log0_odds = int(250 * (1 / 60) / delta_time)
        log1_odds = int(200 * (1 / 60) / delta_time)
        log2_odds = int(100 * (1 / 60) / delta_time)
        self.log_blocking = [False, False, False]

        for found_log in self.log_list:
            if found_log.left < 100:
                self.log_blocking[found_log.index] = True
        #print(self.log_blocking)

        # Add log0
        if random.randrange(log0_odds+1) == 0:
            if not self.log_blocking[0]:
                self.create_log(0, 140, 1, 2)
        # Add log1
        if random.randrange(log1_odds+1) == 0:
            if not self.log_blocking[1]:
                self.create_log(1, 280, 2, 3)
        # Add log2
        if random.randrange(log2_odds+1) == 0:
            if not self.log_blocking[2]:
                self.create_log(2, 350, 4, 5)
        
        for log in self.log_list:
            log.center_x += log.change_x
            if log.left > SCREEN_WIDTH:
                log.remove_from_sprite_lists()


    def on_draw(self):
        """ Render the screen. """

        # Clear the screen
        self.clear()

        # Draw all the sprites.
        #self.water_rect.draw()
        self.road_rect.draw()
        self.water.draw()
        self.log_list.draw()
        self.turtle_list.draw()
        self.player_list.draw()

    def update_player_speed(self):
        if self.up_pressed and not self.down_pressed:
            self.player_sprite.update_player_texture("jump_c")
            self.player_sprite.moving_y = 1
            self.player_sprite.change_y = MOVEMENT_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.update_player_texture("jump_c")
            self.player_sprite.moving_y = 1
            self.player_sprite.change_y = -MOVEMENT_SPEED
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.update_player_texture("jump_lr")
            self.player_sprite.moving_x = 1
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.update_player_texture("jump_lr")
            self.player_sprite.moving_x = 1
            self.player_sprite.change_x = MOVEMENT_SPEED

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Call update to move the sprite
        # If using a physics engine, call update player to rely on physics engine
        # for movement, and call physics engine here.
        self.player_list.update()
        self.moving_logs(delta_time)
        self.moving_turtles(delta_time)
        #print(f"number of logs = {len(self.log_list)}")
        #print(f"number of turtles = {len(self.turtle_list)}")

        self.player_sprite.landable_collided_sprites = []
        landable_hit_list = arcade.check_for_collision_with_lists(self.player_sprite, [self.log_list, self.turtle_list])
        for l_hit in landable_hit_list:
            #hit.remove_from_sprite_lists()
            self.player_sprite.landable_collided_sprites.append(l_hit)

        self.player_sprite.death_collided_sprites = []
        death_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.death_list)
        for d_hit in death_hit_list:
            self.player_sprite.death_collided_sprites.append(d_hit)

        if self.controller:
            # use bellow to see which button was pressed
            #print(self.controller.buttons)
            # controller Up
            if self.controller.y < (DEAD_ZONE*-1) and self.player_sprite.moving_y == 0 and self.controller_dir_reset:
                print(f"{self.controller.name} - UP")
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
            self.player_sprite.texture_direction = 0
            self.update_player_speed()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
            self.player_sprite.last_x = self.player_sprite.center_x
            self.player_sprite.texture_direction = 1
            self.update_player_speed()
        if key == arcade.key.ESCAPE:
            menu_view = MenuView()
            self.window.show_view(menu_view)
        if key == arcade.key.INSERT:
            for i in self.log_list:
                print(i.right)

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
    debug = DebugWindow()
    mainWindow = MainWindow(debug)
    menuView = MenuView()
    mainWindow.show_view(menuView)
    arcade.run()

if __name__ == "__main__":
    main()