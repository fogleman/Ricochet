import generator
import json
import ricochet
import wx

WIDTH = 7
HEIGHT = 7

NORTH = 0x01
EAST =  0x02
SOUTH = 0x04
WEST =  0x08
ROBOT = 0x10

REVERSE = {
    NORTH: SOUTH,
    SOUTH: NORTH,
    EAST:  WEST,
    WEST:  EAST,
}

XREVERSE = {
    NORTH: NORTH,
    SOUTH: SOUTH,
    EAST:  WEST,
    WEST:  EAST,
}

YREVERSE = {
    NORTH: SOUTH,
    SOUTH: NORTH,
    EAST:  EAST,
    WEST:  WEST,
}

DIRECTION = {
    NORTH: (0, -1),
    SOUTH: (0, 1),
    EAST:  (1, 0),
    WEST:  (-1, 0),
}

class Model(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.robots = [-1] * 4
        self.tokens = [-1] * 4
        self.grid = [0] * (self.width * self.height)
        self.walls = 0
        self.moves = -1
        for y in xrange(self.height):
            for x in xrange(self.width):
                index = self.index(x, y)
                if x == 0:
                    self.set_wall(index, WEST)
                if x == self.width - 1:
                    self.set_wall(index, EAST)
                if y == 0:
                    self.set_wall(index, NORTH)
                if y == self.height - 1:
                    self.set_wall(index, SOUTH)
    def __str__(self):
        return self.get_json()
    def get_json(self):
        data = {
            'width': self.width,
            'height': self.height,
            'grid': self.grid,
            'robots': self.robots,
            'tokens': self.tokens,
            'moves': self.moves,
        }
        return json.dumps(data)
    def save(self, path):
        with open(path, 'wb') as fp:
            fp.write(self.get_json())
    def load(self, path):
        with open(path, 'rb') as fp:
            data = json.loads(fp.read())
        self.width = data['width']
        self.height = data['height']
        self.grid = data['grid']
        self.robots = data['robots']
        self.tokens = data['tokens']
        #self.moves = data['moves']
    def index(self, x, y):
        return y * self.width + x
    def xy(self, index):
        x = index % self.width
        y = index / self.width
        return (x, y)
    def get_mask(self, index):
        mask = self.grid[index]
        if self.has_robot(index):
            mask |= ROBOT
        return mask
    def has_robot(self, index):
        return any(robot == index for robot in self.robots)
    def set_wall(self, index, wall):
        self.grid[index] |= wall
    def unset_wall(self, index, wall):
        self.grid[index] &= ~wall
    def has_wall(self, index, wall):
        return bool(self.grid[index] & wall)
    def toggle_wall(self, index, wall, toggle_neighbor=True):
        x, y = self.xy(index)
        if x == 0 and wall == WEST:
            return
        if y == 0 and wall == NORTH:
            return
        if x == self.width - 1 and wall == EAST:
            return
        if y == self.height - 1 and wall == SOUTH:
            return
        if self.has_wall(index, wall):
            self.unset_wall(index, wall)
            if toggle_neighbor:
                self.walls -= 1
        else:
            self.set_wall(index, wall)
            if toggle_neighbor:
                self.walls += 1
        if toggle_neighbor:
            neighbor = self.neighbor(index, wall)
            if neighbor is not None:
                self.toggle_wall(neighbor, REVERSE[wall], False)
    def toggle_walls(self, index, wall, mirror_x=False, mirror_y=False, mirror_xy=False):
        self.toggle_wall(index, wall)
        if mirror_x:
            x, y = self.xy(index)
            mx = self.width - x - 1
            self.toggle_wall(self.index(mx, y), XREVERSE[wall])
        if mirror_y:
            x, y = self.xy(index)
            my = self.height - y - 1
            self.toggle_wall(self.index(x, my), YREVERSE[wall])
        if mirror_xy or (mirror_x and mirror_y):
            x, y = self.xy(index)
            mx = self.width - x - 1
            my = self.height - y - 1
            self.toggle_wall(self.index(mx, my), REVERSE[wall])
    def neighbor(self, index, direction):
        x, y = self.xy(index)
        dx, dy = DIRECTION[direction]
        x, y = x + dx, y + dy
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return None
        return self.index(x, y)

class View(wx.Panel):
    def __init__(self, parent, model):
        super(View, self).__init__(parent, style=wx.WANTS_CHARS)
        self.model = model
        self.origin = (0, 0)
        self.size = 0
        self.selection = -1
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
    def index_from_coords(self, x, y):
        model = self.model
        ox, oy = self.origin
        i, j = (x - ox) / self.size, (y - oy) / self.size
        if i < 0 or j < 0 or i >= model.width or j >= model.height:
            return None
        return model.index(i, j)
    def move_selection(self, direction):
        if self.selection < 0:
            return
        model = self.model
        x, y = model.xy(self.selection)
        dx, dy = DIRECTION[direction]
        x, y = x + dx, y + dy
        if x < 0 or y < 0 or x >= model.width or y >= model.height:
            return
        self.selection = model.index(x, y)
    def on_size(self, event):
        event.Skip()
        self.Refresh()
    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        model = self.model
        w, h = self.GetClientSize()
        p = 25
        self.size = size = min((w - p * 2) / model.width, (h - p * 2) / model.height)
        self.origin = (w - size * model.width) / 2, (h - size * model.height) / 2
        stroke = size / 10
        dc.SetDeviceOrigin(*self.origin)
        colors = [
            wx.RED,
            wx.GREEN,
            wx.BLUE,
            wx.Colour(255, 255, 0),
        ]
        for j in xrange(model.height):
            for i in xrange(model.width):
                index = model.index(i, j)
                if index in model.tokens:
                    dc.SetBrush(wx.Brush(colors[model.tokens.index(index)]))
                else:
                    dc.SetBrush(wx.WHITE_BRUSH)
                x, y = i * size, j * size
                dc.DrawRectangle(x, y, size + 1, size + 1)
                dc.SetBrush(wx.BLACK_BRUSH)
                if model.has_wall(index, NORTH):
                    dc.DrawRectangle(x, y, size + 1, stroke)
                if model.has_wall(index, SOUTH):
                    dc.DrawRectangle(x, y + size - stroke + 1, size + 1, stroke)
                if model.has_wall(index, EAST):
                    dc.DrawRectangle(x + size - stroke + 1, y, stroke, size + 1)
                if model.has_wall(index, WEST):
                    dc.DrawRectangle(x, y, stroke, size + 1)
                for ordinal, cell in enumerate(model.robots):
                    if cell != index:
                        continue
                    dc.SetBrush(wx.Brush(colors[ordinal]))
                    dc.DrawCircle(x + size / 2, y + size / 2, size / 3)
                if index == self.selection:
                    dc.SetPen(wx.BLACK_PEN)
                    dc.DrawLine(x + size / 2, y + size / 4, x + size / 2, y + size * 3 / 4)
                    dc.DrawLine(x + size / 4, y + size / 2, x + size * 3 / 4, y + size / 2)
    def on_key_down(self, event):
        code = event.GetKeyCode()
        model = self.model
        if code >= 32 and code < 128:
            key = chr(code)
            if self.selection >= 0:
                if key == 'W':
                    model.toggle_wall(self.selection, NORTH)
                if key == 'S':
                    model.toggle_wall(self.selection, SOUTH)
                if key == 'D':
                    model.toggle_wall(self.selection, EAST)
                if key == 'A':
                    model.toggle_wall(self.selection, WEST)
            if key in '1234':
                index = int(key) - 1
                model.robots[index] = self.selection
            if key in '5678':
                index = int(key) - 5
                model.tokens[index] = self.selection
            if key == 'C':
                def callback(depth, nodes, inner, hits):
                    print 'Depth: %d, Nodes: %d (%d inner, %d hits)' % (depth, nodes, inner, hits)
                path = ricochet.search(model, callback)
                model.moves = len(path)
                print ', '.join(''.join(x) for x in path)
            if key == 'J':
                dialog = wx.FileDialog(self.GetParent(), wildcard='*.json', style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
                if dialog.ShowModal() == wx.ID_OK:
                    model.save(dialog.GetPath())
            if key == 'K':
                dialog = wx.FileDialog(self.GetParent(), wildcard='*.json', style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
                if dialog.ShowModal() == wx.ID_OK:
                    model.load(dialog.GetPath())
            if key == 'G':
                self.model = generator.generate(model)
        if code == wx.WXK_ESCAPE:
            self.GetParent().Close()
        directions = {
            wx.WXK_UP: NORTH,
            wx.WXK_DOWN: SOUTH,
            wx.WXK_LEFT: WEST,
            wx.WXK_RIGHT: EAST,
        }
        if code in directions:
            self.move_selection(directions[code])
        sizes = [wx.WXK_F4, wx.WXK_F5, wx.WXK_F6, wx.WXK_F7]
        if code in sizes:
            size = sizes.index(code) + 4
            self.model = Model(size, size)
        self.Refresh()
    def on_left_down(self, event):
        x, y = event.GetPosition()
        self.selection = self.index_from_coords(x, y)
        self.Refresh()

class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None, -1, 'Editor')
        View(self, Model(WIDTH, HEIGHT))

def main():
    app = wx.PySimpleApp()
    frame = Frame()
    frame.SetClientSize((600, 600))
    frame.Center()
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
