import arcade

class Wall(arcade.Sprite):
    def __init__(self, width, height, color, center_x, center_y):
        super().__init__(hit_box_algorithm="Simple")  # Use the Simple hitbox algorithm
        self.texture = arcade.make_soft_square_texture(width, color, outer_alpha=255)
        self.width = width
        self.height = height
        self.center_x = center_x
        self.center_y = center_y

        # Define the hitbox for the wall (rectangle)
        self.set_hit_box([
            (-width / 2, -height / 2),
            (width / 2, -height / 2),
            (width / 2, height / 2),
            (-width / 2, height / 2)
        ])
    
    def get_lines(self):
        """
        Returns the edges of the wall as line segments.
        """
        left = self.center_x - self.width / 2
        right = self.center_x + self.width / 2
        top = self.center_y + self.height / 2
        bottom = self.center_y - self.height / 2
        return [
            [(left, bottom), (left, top)],  # Left edge
            [(left, top), (right, top)],   # Top edge
            [(right, top), (right, bottom)],  # Right edge
            [(right, bottom), (left, bottom)],  # Bottom edge
        ]
