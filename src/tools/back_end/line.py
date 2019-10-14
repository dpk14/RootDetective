class Curve:

    def __init__(self, x_vec, y_vec):
        self.x_vec = x_vec
        self.y_vec = y_vec
        self.initialize_map()
        self.range = len(x_vec)

    def initialize_map(self):
        self.x_y_map = {}
        for index in range(len(self.x_vec)):
            x = self.x_vec[index]
            y = (self.y_vec[index],)
            if x not in self.x_y_map:
                self.x_y_map[x]=tuple(y)
            else:
                y_tuple = self.x_y_map[x]
                y_tuple+=y
                self.x_y_map[x]=y_tuple


    def has_y(self, y):
        return y in self.y_vec

    def has_x(self, x):
        return x in self.x_vec

    def has_point(self, x, y):
        return self.has_x(x) and self.has_y(y)

    def get_y_at(self, x):
        return self.x_y_map[x]

    def has_point_close_to(self, x, y, error):
        y_tuple = self.get_y_at(x)
        for sample in y_tuple:
            if y - error < sample < y + error:
                return True
        return False
