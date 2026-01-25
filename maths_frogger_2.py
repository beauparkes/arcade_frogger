import arcade
import arcade.gui
import pyglet
import random
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, FONT_TITLE_1, FONT_BODY_1,
    DEFAULT_LINE_HEIGHT, TITLE_FONT_SIZE, DEFAULT_FONT_SIZE, FONT_COLOUR_GREEN,
    FONT_COLOUR_RED, SPRITE_SCALING, STARTING_LIVES, MOVEMENT_SPEED,
    MOVEMENT_LIMIT_X, MOVEMENT_LIMIT_Y, DEAD_ZONE, BACKGROUND_COLOR,
    MENU_BACKGROUND_COLOR, END_GAME_BACKGROUND_COLOR
)


def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]


class Controllers:
    """
    Manages game controllers using pyglet. Handles connection, disconnection,
    and status updates for up to two controllers.
    """
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
    """
    Debug window for development purposes. Currently not well implemented.
    Provides a smaller window for debugging the game.
    """
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
    """
    Main application window. Handles the primary game display and debug window toggling.
    """
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
    """
    Manages the main menu view. Handles user interface for selecting game options
    like players, mode, difficulty, and starting the game. Integrates controller support.
    """
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
        arcade.set_background_color(MENU_BACKGROUND_COLOR)

        # Setup menu button layouts
        self.red_style = {
            "font_name": FONT_BODY_1,
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
            "font_name": FONT_BODY_1,
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
            "font_name": FONT_TITLE_1,
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
            font_name=FONT_TITLE_1,
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
            font_name=FONT_TITLE_1,
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
            font_name=FONT_TITLE_1,
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
            font_name=FONT_TITLE_1,
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
            font_name=FONT_TITLE_1,
            text_color=FONT_COLOUR_RED,
        )
        
        self.controller_1_text = arcade.gui.UILabel(
            text=self.controller_1_status_text,
            #size_hint=(100, 50),
            width=500,
            align="center",
            font_size=12,
            font_name=FONT_TITLE_1,
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
            if child.child is not event.source:
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
        if self.controllers.has_update:

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
        game_view.setup()
        self.window.show_view(game_view)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.ENTER or key == arcade.key.RETURN:
            self.startGame(None)


class Player(arcade.Sprite):
    """
    Represents the player character (frog). Handles movement, collision detection,
    scoring, lives, and player-specific game logic.
    """
    def __init__(self, scale, window):
        super().__init__()
        self.scale = scale
        self.moving_x = False
        self.moving_y = False
        self.in_motion = False
        self.destination_x = 0
        self.destination_y = 0
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
        self.last_rest = [0,0]
        self.landable_collided_sprites = arcade.SpriteList()
        self.unlandable_sprites = arcade.SpriteList()
        self.collide_offset = "none"
        self.death_collided_sprites = []
        self.window = window
        self.game_view = None
        self.pre_collider = None
        self.score = 0
        self.lives = STARTING_LIVES
        self.answer = None
        self.answer_texts = None
        self.answer_list = None


    def move(self, direction=None):

        if direction and self.in_motion:
            return
        if direction and not self.in_motion:
            self.in_motion = True
            # check if blocked by unlandable sprite
            self.last_pos = [self.center_x, self.center_y]
            self.collide_offset = "none"

            # Temporarily move to new position
            if direction == "left":
                if not self.moving_x:
                    self.destination_x = self.center_x - MOVEMENT_LIMIT_X
                self.moving_x = True
                self.texture_direction = 0
                self.update_player_texture("jump_lr")
                if self.moving_y:
                    self.set_position(self.destination_x, self.center_y - MOVEMENT_LIMIT_Y)
                else:
                    self.set_position(self.center_x - MOVEMENT_LIMIT_X, self.center_y)
            if direction == "right":
                if not self.moving_x:
                    self.destination_x = self.center_x + MOVEMENT_LIMIT_X
                self.moving_x = True
                self.texture_direction = 1
                self.update_player_texture("jump_lr")
                if self.moving_y:
                    self.set_position(self.destination_x, self.center_y - MOVEMENT_LIMIT_Y)
                else:
                    self.set_position(self.center_x + MOVEMENT_LIMIT_X, self.center_y)
            if direction == "up":
                if not self.moving_y:
                    self.destination_y = self.center_y + MOVEMENT_LIMIT_Y
                self.moving_y = True
                self.update_player_texture("jump_c")
                if self.moving_x:
                    self.set_position(self.destination_x, self.center_y + MOVEMENT_LIMIT_Y)
                else:
                    self.set_position(self.center_x, self.center_y + MOVEMENT_LIMIT_Y)
            if direction == "down":
                if not self.moving_y:
                    self.destination_y = self.center_y - MOVEMENT_LIMIT_Y
                self.moving_y = True
                self.update_player_texture("jump_c")
                if self.moving_x:
                    self.set_position(self.destination_x, self.center_y - MOVEMENT_LIMIT_Y)
                else:
                    self.set_position(self.center_x, self.center_y - MOVEMENT_LIMIT_Y)

            unlandable_hit_list = arcade.check_for_collision_with_list(self, self.unlandable_sprites)
            print(unlandable_hit_list)

            if unlandable_hit_list:
                print("hit unlandable")
                self.set_position(self.last_pos[0], self.last_pos[1])  # Revert position
                self.change_x = 0
                self.change_y = 0
                self.moving_x = False
                self.moving_y = False
                self.in_motion = False
                self.update_player_texture("idle")
                return
            else:
                self.set_position(self.last_pos[0], self.last_pos[1])  # Revert to start movement
                if direction == "left":
                    self.change_x = -MOVEMENT_SPEED
                if direction == "right":
                    self.change_x = MOVEMENT_SPEED
                if direction == "up":
                    self.change_y = MOVEMENT_SPEED
                if direction == "down":
                    self.change_y = -MOVEMENT_SPEED
                print("no unlandable")


        print("moving")
        self.center_x += self.change_x
        self.center_y += self.change_y

        if abs(self.center_y - self.last_pos[1]) >= MOVEMENT_LIMIT_Y and self.change_y != 0:
            self.change_y = 0
            self.update_player_texture("idle")
            self.last_y = 0
            self.moving_y = False
            self.in_motion = False
            if self.bottom <= 0:
                self.bottom = 0
            elif self.top >= SCREEN_HEIGHT:
                self.top = SCREEN_HEIGHT
        if abs(self.center_x - self.last_pos[0]) >= MOVEMENT_LIMIT_X and self.change_x != 0:
            self.change_x = 0
            self.update_player_texture("idle")
            self.last_x = 0
            self.moving_x = False
            self.in_motion = False
            if self.left <= 0:
                self.left = 0
            elif self.right >= SCREEN_WIDTH:
                self.right = SCREEN_WIDTH

        
    def not_moving(self):
        # if death return to end game view
        print(self.answer)
        print("not moving")
        if self.death_collided_sprites and not self.landable_collided_sprites:
            #self.texture = self.frog_dead_pair[0]
            self.center_x = SCREEN_WIDTH / 2
            self.bottom =  MOVEMENT_LIMIT_Y -5
            self.lives -= 1
            return
        if self.lives <= 0:
            print(self.lives)
            print("game over")
            end_game = EndGame()
            self.window.show_view(end_game)
            return

        answer_hit = arcade.check_for_collision_with_list(self, self.answer_list)
        for a_hit in answer_hit:
            if a_hit.value == self.answer:
                self.center_x = SCREEN_WIDTH / 2
                self.bottom =  MOVEMENT_LIMIT_Y -5
                self.score += 10
                print("Correct Answer!")
                # Generate new question
                self.value1 = random.randint(1,10)
                self.value2 = random.randint(1,10)
                self.operator = random.choice(['+', '-', '*'])
                self.answer = eval(f"{self.value1} {self.operator} {self.value2}")
                self.fake_answer1 = self.answer + random.choice([-3, -2, -1, 1, 2, 3])
                self.fake_answer2 = self.answer + random.choice([-3, -2, -1, 1, 2, 3])
                self.fake_answer3 = self.answer + random.choice([-3, -2, -1, 1, 2, 3])
                self.possible_answers = [self.answer, self.fake_answer1, self.fake_answer2, self.fake_answer3]
                random.shuffle(self.possible_answers)
                # Update answer texts and values
                for i in range(4):
                    self.answer_texts[i].text = str(self.possible_answers[i])
                    self.answer_list[i].value = self.possible_answers[i]
                # Update game's question values
                self.game_view.game.value1 = self.value1
                self.game_view.game.value2 = self.value2
                self.game_view.game.operator = self.operator
            else:
                self.center_x = SCREEN_WIDTH / 2
                self.bottom =  MOVEMENT_LIMIT_Y -5
                self.lives -= 1
                print("Wrong Answer!")
                if self.lives <= 0:
                    end_game = EndGame()
                    self.window.show_view(end_game)
                else:
                    self.center_x = SCREEN_WIDTH / 2
                    self.bottom =  MOVEMENT_LIMIT_Y -5

        if not self.landable_collided_sprites:
            print("not on a landable")
            self.collide_offset = "none"
            return
        print("on a landable")
        if self.collide_offset == "none":
            self.collide_offset =  self.center_x - self.landable_collided_sprites[0].center_x
        else:
            self.set_position(self.landable_collided_sprites[0].center_x + self.collide_offset, self.center_y)
        self.last_rest = [self.center_x, self.center_y]

    def update(self):
        # Move the player
        # Remove these lines if physics engine is moving player.
        if self.change_x  == 0 and self.change_y == 0:
            self.not_moving()
        else:
            self.move()


    def update_player_texture(self, texture_state):
        if texture_state == "idle":
            self.texture = self.frog_idle_pair[self.texture_direction]
        if texture_state == "jump_lr":
            self.texture = self.frog_jump_lr_pair[self.texture_direction]
        if texture_state == "jump_c":
            self.texture = self.frog_jump_c_pair[self.texture_direction]
        if texture_state == "dead":
            self.texture = self.frog_dead_pair[self.texture_direction]


class Level:
    """
    Manages all game level elements, including sprite lists for logs, turtles,
    cars, separators, death zones, and answers. Handles level setup and updates.
    """
    def __init__(self):
        self.log_list = arcade.SpriteList()
        self.turtle_list = arcade.SpriteList()
        self.car_list = arcade.SpriteList()
        self.truck_list = arcade.SpriteList()
        self.separator_list = arcade.SpriteList()
        self.death_list = arcade.SpriteList()
        self.answer_list = arcade.SpriteList()
        self.answer_texts = []
        self.land_rect = None
        self.water = None
        self.road_rect = None
        self.setup()

    def setup(self):
        # Setup land
        self.land_rect = arcade.create_rectangle_filled(SCREEN_WIDTH*0.5, SCREEN_HEIGHT*0.75, 3000, 600, arcade.color.GREEN)
        
        # Setup water sprite
        water_sprite = ":resources:images/tiles/water.png"
        self.water = arcade.Sprite(filename=water_sprite, scale=SPRITE_SCALING*16.8, image_width=128, image_height=53)
        self.water.center_x = SCREEN_WIDTH / 2
        self.water.center_y = SCREEN_HEIGHT - 286
        self.death_list.append(self.water)

        # Setup road
        self.road_rect = arcade.create_rectangle_filled(SCREEN_WIDTH*0.5, SCREEN_HEIGHT*0.3+15, 3000, 400, arcade.color.BLACK)

        # Setup separators
        for index in range(3):
            offset = 280
            offsets = [-offset, 0, offset]
            self.create_seperator(index, 32, offsets[index])

    def create_seperator(self, index, height_offset, x_offset):
        separator_sprite = ":resources:images/topdown_tanks/tileSand2.png"
        separator = arcade.Sprite(filename=separator_sprite, scale=SPRITE_SCALING*2, image_width=64, image_height=64)
        separator.center_x = (SCREEN_WIDTH/2) + x_offset
        separator.center_y = SCREEN_HEIGHT - height_offset
        separator.index = index
        self.separator_list.append(separator)

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
        turtle1_odds = int(70 * (1 / 60 * delta_time))
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
        log1_odds = int(120 * (1 / 60) / delta_time)
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
    

    def create_answers(self, possible_answers):
        """ A function that will create answer sprites and add them to the answer list.
        """
        for i in range(4):
            answer_sprite = ":resources:images/tiles/boxCrate.png"  # Use a dummy texture
            answer = arcade.Sprite(answer_sprite, scale=SPRITE_SCALING)
            answer.center_x = 100 + (280 * i)
            answer.center_y = SCREEN_HEIGHT - 30
            answer.alpha = 0  # Make invisible
            answer.value = possible_answers[i]
            self.answer_list.append(answer)

            # Also create the text for drawing
            text = arcade.Text(
                str(possible_answers[i]), 
                start_x = 100 + (280 * i),
                start_y = SCREEN_HEIGHT - 30,
                color=arcade.color.WHITE, 
                font_size=DEFAULT_FONT_SIZE, 
                font_name=FONT_BODY_1,
                anchor_x="center", # Center the text horizontally
                anchor_y="center"  # Center the text vertically
            )
            self.answer_texts.append(text)

    def update(self, delta_time):
        self.moving_logs(delta_time)
        self.moving_turtles(delta_time)


class UI:
    """
    Manages user interface elements, including GUI components and layout.
    Currently minimal but designed for extensibility.
    """
    def __init__(self, player):
        self.player = player
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.ui_layout = arcade.gui.UIBoxLayout(vertical=False, space_between=10)
        self.setup()

    def setup(self):
        # Create a widget to hold the main_layout widget, that will center the buttons
        self.manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="center_x",
            anchor_y="center_y",
            child=self.ui_layout)
        )

    def draw(self):
        self.manager.draw()


class Game:
    """
    Central manager for game state. Orchestrates level, player, UI, and game logic,
    including collisions, updates, and scoring.
    """
    def __init__(self, players, mode, difficulty, controllers):
        self.players = players
        self.mode = mode
        self.difficulty = difficulty
        self.controllers = controllers
        self.level = Level()
        self.player = Player(SPRITE_SCALING, None)  # Window will be set later
        self.ui = UI(self.player)
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)
        self.god_mode = False
        self.value1 = random.randint(1,10)
        self.value2 = random.randint(1,10)
        self.operator = random.choice(['+', '-', '*'])
        self.answer = eval(f"{self.value1} {self.operator} {self.value2}")
        self.fake_answer1 = self.answer + random.choice([-3, -2, -1, 1, 2, 3])
        self.fake_answer2 = self.answer + random.choice([-3, -2, -1, 1, 2, 3])
        self.fake_answer3 = self.answer + random.choice([-3, -2, -1, 1, 2, 3])
        self.possible_answers = [self.answer, self.fake_answer1, self.fake_answer2, self.fake_answer3]
        random.shuffle(self.possible_answers)
        self.setup_game()

    def setup_game(self):
        self.player.center_x = SCREEN_WIDTH / 2
        self.player.bottom = MOVEMENT_LIMIT_Y + 5
        self.player.answer_list = self.level.answer_list
        self.player.answer = self.answer
        self.player.answer_texts = self.level.answer_texts
        self.level.create_answers(self.possible_answers)
        for i in range(4):
            self.level.answer_texts[i].text = str(self.possible_answers[i])
            self.level.answer_list[i].value = self.possible_answers[i]
        self.player.unlandable_sprites = self.level.separator_list

    def update(self, delta_time):
        self.player_list.update()
        self.level.update(delta_time)
        self.player.landable_collided_sprites = []
        landable_hit_list = arcade.check_for_collision_with_list(self.player, self.level.log_list) + arcade.check_for_collision_with_list(self.player, self.level.turtle_list)
        for l_hit in landable_hit_list:
            self.player.landable_collided_sprites.append(l_hit)

        if not self.god_mode:
            self.player.death_collided_sprites = []
            death_hit_list = arcade.check_for_collision_with_list(self.player, self.level.death_list)
            for d_hit in death_hit_list:
                self.player.death_collided_sprites.append(d_hit)

    def draw(self):
        self.level.road_rect.draw()
        self.level.water.draw()
        self.level.separator_list.draw()
        self.level.log_list.draw()
        self.level.turtle_list.draw()
        self.player_list.draw()
        self.level.answer_list.draw()
        for text in self.level.answer_texts:
            text.draw()
        self.ui.draw()
        arcade.draw_text(
            f"Solve: {self.value1} {self.operator} {self.value2}",
            start_x=0, start_y= 0,
            width=SCREEN_WIDTH,
            font_size=40,
            align="center",
            color=arcade.color.BLACK
        )
        arcade.draw_text(
            f"P1 Score: {self.player.score} Lives: {self.player.lives}",
            start_x=-380, start_y= 0,
            width=SCREEN_WIDTH,
            font_size=20,
            align="center",
            color=arcade.color.BLACK
        )


class GameView(arcade.View):
    """
    Main game view. Handles drawing, input, and delegates game logic to the Game instance.
    Manages user interactions and rendering.
    """
    def __init__(self, players, mode, difficulty, controllers):
        """
        Initializer
        
        """
        # Call the parent class initializer
        super().__init__()

        # Set the background color
        arcade.set_background_color(BACKGROUND_COLOR)

        # menu class varaibles
        self.players = players
        self.mode = mode
        self.difficulty = difficulty
        self.controllers = controllers

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.controller_dir_reset = True

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

        self.game = None

    def setup(self):
        self.game = Game(self.players, self.mode, self.difficulty, self.controllers)
        self.game.player.window = self.window
        self.game.player.game_view = self

    def on_draw(self):
        """ Render the screen. """

        # Clear the screen
        self.clear()

        self.game.draw()

    def on_update(self, delta_time):
        """ Movement and game logic """

        self.game.update(delta_time)

        if self.controller:
            # use bellow to see which button was pressed
            #print(self.controller.buttons)
            # controller Up
            if self.controller.y < (DEAD_ZONE*-1) and not self.game.player.moving_y and self.controller_dir_reset:
                print(f"{self.controller.name} - UP")
                self.up_pressed = True
                self.game.player.last_y = self.game.player.center_y
                self.controller_dir_reset = False

            # controller Down
            if self.controller.y > DEAD_ZONE and not self.game.player.moving_y and self.controller_dir_reset:
                self.down_pressed = True
                self.game.player.last_y = self.game.player.center_y
                self.controller_dir_reset = False

            # controller Right
            if self.controller.x > DEAD_ZONE and not self.game.player.moving_x and self.controller_dir_reset:
                self.right_pressed = True
                self.game.player.last_x = self.game.player.center_x
                self.controller_dir_reset = False

            # controller Left
            if self.controller.x < (DEAD_ZONE*-1) and not self.game.player.moving_x and self.controller_dir_reset:
                self.left_pressed = True
                self.game.player.last_x = self.game.player.center_x
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
            self.game.player.move("up")
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
            self.game.player.move("down")
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
            self.game.player.move("left")
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
            self.game.player.move("right")
        if key == arcade.key.ESCAPE:
            menu_view = MenuView()
            self.window.show_view(menu_view)
        if key == arcade.key.DELETE:
            end_game = EndGame()
            self.window.show_view(end_game)
        if key == arcade.key.G and modifiers == arcade.key.MOD_SHIFT:
            self.game.god_mode = not self.game.god_mode
            if self.game.god_mode:
                print("GOD MODE ON~")
                self.game.player.color = arcade.color.GOLD
            else:
                print("GOD MODE OFF~")
                self.game.player.color = arcade.color.WHITE

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


class EndGame(arcade.View):
    """
    Displays the end game screen with options to return to main menu or try again.
    Handles game over state.
    """
    def __init__(self):
        super().__init__()
        # Setup base background colour
        arcade.set_background_color(END_GAME_BACKGROUND_COLOR)
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Create all layouts
        self.main_layout = arcade.gui.UIBoxLayout(vertical=True, space_between=10)
        self.options_layout = arcade.gui.UIBoxLayout(vertical=True, space_between=10)

        # Create tile text
        self.title_layout = arcade.gui.UILabel(
            text=SCREEN_TITLE,
            size_hint=(300, 50),
            align="center",
            font_size=TITLE_FONT_SIZE,
            font_name=FONT_TITLE_1,
        )
        # Add title to manager
        self.manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="center_x",
            anchor_y="top",
            align_y=-25,
            child=self.title_layout)
        )

        # Create game over label
        end_game_text = arcade.gui.UILabel(
            text="Game Over",
            size_hint=(300, 50),
            align="center",
            font_size=TITLE_FONT_SIZE + 30,
            font_name=FONT_TITLE_1,
        )

        # Setup menu button layouts
        self.red_style = {
            "font_name": FONT_BODY_1,
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
            "font_name": FONT_BODY_1,
            "font_size": DEFAULT_FONT_SIZE,
            "font_color": arcade.color.BLACK,
            "border_width": 5, "border_color": None,
            "bg_color": arcade.color.GREEN,
            # Used if button is pressed
            "bg_color_pressed": arcade.color.WHITE,
            "border_color_pressed": arcade.color.GREEN_YELLOW,
            # also used when hovered
            "font_color_pressed": arcade.color.RED,
        }

        # Add options label to layout
        self.options_layout.add(end_game_text.with_space_around(bottom=0))
        #self.main_layout.add(self.options_layout.with_space_around(bottom=0))
        # Add player layout to main layout
        #self.main_layout.add(self.player_layout)

        # Add mainmenu button to options layout
        main_menu_button = arcade.gui.UIFlatButton(text="Main Menu", width=200, style=self.red_style)
        return_red_style = dict(self.red_style)
        return_red_style["bg_color"] = arcade.color.BALL_BLUE
        main_menu_button._style = return_red_style
        main_menu_button.on_click = self.main_screen_button

        try_again_button = arcade.gui.UIFlatButton(text="Try Again", width=200, style=self.red_style)
        green_style = dict(self.green_style)
        green_style["bg_color"] = arcade.color.GREEN_YELLOW
        try_again_button._style = green_style
        try_again_button.on_click = self.try_again_button

        self.options_layout.add(main_menu_button.with_space_around(bottom=0))
        self.options_layout.add(try_again_button.with_space_around(bottom=0))
        self.main_layout.add(self.options_layout.with_space_around(bottom=20))

        # Create a widget to hold the main_layout widget, that will center the buttons
        self.manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="center_x",
            anchor_y="center_y",
            child=self.main_layout)
        )

    def on_draw(self):
        """Draw the menu."""
        self.clear()
        size = self.window.get_size()
        arcade.draw_rectangle_filled(size[0]/2, size[1], size[0], 180, arcade.color.DARK_IMPERIAL_BLUE)
        arcade.draw_rectangle_filled(size[0]/2, 0, size[0], 150, arcade.color.DARK_IMPERIAL_BLUE)
        self.manager.draw()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.ESCAPE:
            self.main_screen()

        if key == arcade.key.ENTER or key == arcade.key.RETURN:
            self.try_again(None)

    def main_screen_button(self, event):
        self.main_screen()

    def try_again_button(self, event):
        self.try_again(event)
    
    def main_screen(self):
        menu_view = MenuView()
        self.window.show_view(menu_view)

    def try_again(self, event):
        game_view = GameView(1, "endless", "easy", Controllers())
        game_view.setup()
        self.window.show_view(game_view)


def main():
    """Startup"""
    debug = DebugWindow()
    mainWindow = MainWindow(debug)
    menuView = MenuView()
    mainWindow.show_view(menuView)
    arcade.run()

if __name__ == "__main__":
    main()