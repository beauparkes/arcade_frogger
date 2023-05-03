import arcade
import random

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_MATH = 0.25

class Player(arcade.Sprite):
    def __init__(self, filename, scale):
        super().__init__(filename, scale)
        self.score = 0

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Check for out-of-bounds
        if self.left < 0:
            self.left = 0
        elif self.right > SCREEN_WIDTH:
            self.right = SCREEN_WIDTH
        if self.bottom < 0:
            self.bottom = 0
        elif self.top > SCREEN_HEIGHT:
            self.top = SCREEN_HEIGHT

class Math(arcade.Sprite):
    def __init__(self, filename, scale):
        super().__init__(filename, scale)
        self.text = ""

    def update(self):
        self.center_y -= 5

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Math Frogger")
        arcade.set_background_color(arcade.color.WHITE)

        # Set up the player
        self.player = Player(":resources:images/enemies/frog.png", SPRITE_SCALING_PLAYER)
        self.player.center_x = SCREEN_WIDTH // 2
        self.player.bottom = 0

        # Set up the math problems
        self.maths = arcade.SpriteList()
        self.math_text = arcade.create_text_sprite(
            "",
            start_x=0,
            start_y=0,
            color=arcade.color.BLACK,
            font_size=14
            )
        
        # Add new math problems
        for i in range(5):
            math_operator = random.choice(["+", "-", "*", "/"])
            num1 = random.randint(1, 10)
            num2 = random.randint(1, 10)
            if math_operator == "+":
                result = num1 + num2
            elif math_operator == "-":
                result = num1 - num2
            elif math_operator == "*":
                result = num1 * num2
            elif math_operator == "/":
                result = num1 / num2
            math_problem = str(num1) + math_operator + str(num2) + "="
            math_sprite = Math(":resources:images/enemies/frog_move.png", SPRITE_SCALING_MATH)
            math_sprite.center_x = random.randint(0, SCREEN_WIDTH)
            math_sprite.top = SCREEN_HEIGHT + 100 + i * 50
            math_sprite.text = math_problem + str(result)
            self.maths.append(math_sprite)

        arcade.run()

    def on_draw(self):
        arcade.start_render()

        # Draw the player, math problems, and math text
        self.player.draw()
        self.maths.draw()
        arcade.render_text(self.math_text, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20,
                            anchor_x="center")

        # Draw the score
        score_text = f"Score: {self.player.score}"
        arcade.render_text(score_text, 10, SCREEN_HEIGHT - 20)

    def on_update(self, delta_time):
        self.player.update()
        self.maths.update()

        # Check for collisions
        math_hit_list = arcade.check_for_collision_with_list(self.player, self.maths)
        for math_sprite in math_hit_list:
            self.player.score += 1
            self.maths.remove(math_sprite)

        # Update math text
        math_text = ""
        for math_sprite in self.maths:
            math_text += math_sprite.text + "\n"
        self.math_text = arcade.create_text_sprite(
            math_text,
            start_x=0,
            start_y=0,
            color=arcade.color.BLACK,
            font_size=14,
            anchor_x="center")

        # Add new math problems if necessary
        if len(self.maths) < 5:
            math_operator = random.choice(["+", "-", "*", "/"])
            num1 = random.randint(1, 10)
            num2 = random.randint(1, 10)
            if math_operator == "+":
                result = num1 + num2
            elif math_operator == "-":
                result = num1 - num2
            elif math_operator == "*":
                result = num1 * num2
            elif math_operator == "/":
                result = num1 / num2
            math_problem = str(num1) + math_operator + str(num2) + "="
            math_sprite = Math(":resources:images/enemies/frog_move.png", SPRITE_SCALING_MATH)
            math_sprite.center_x = random.randint(0, SCREEN_WIDTH)
            math_sprite.top = SCREEN_HEIGHT + 100
            math_sprite.text = math_problem + str(result)
            self.maths.append(math_sprite)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.player.change_x = -5
        elif key == arcade.key.RIGHT:
            self.player.change_x = 5
        elif key == arcade.key.UP:
            self.player.change_y = 5
        elif key == arcade.key.DOWN:
            self.player.change_y = -5

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player.change_x = 0
        elif key == arcade.key.UP or key == arcade.key.DOWN:
            self.player.change_y = 0

def main():
    MyGame()

if __name__ == "__main__":
    main()

