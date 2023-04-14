import os
import numpy as np

def remap(value, inFrom, inTo, outFrom, outTo):
    if inFrom == inTo:
        # special case where in-values are the same => remap() would zero divide => broadcast center as result
        return (value*0) + ((outFrom + outTo)/2)
    return outFrom + (outTo - outFrom) * ((value - inFrom) / (inTo - inFrom))

class GUI_Element:
    def __init__(self, py5=None, pos=(0,0), label='', w=30, h=30):
        self.x = pos[0]; self.y = pos[1]
        self.label = label
        self.p = py5
        
        self.h = h;     self.w = w
        self.center = (self.x + self.w/2, self.y + self.h/2)
        
        self.fill = (0,);   self.stroke = (127,);   self.pressed_stroke=(255,)
        self.highlight_fill = (32,)
        self.text_fill = (255,);    self.text_stroke = (127,)
        self.stroke_weight = 3
        
    def mouse_in(self):
        return True if self.p.mouse_x > self.x and self.p.mouse_x < self.x+self.w and \
               self.p.mouse_y > self.y and self.p.mouse_y < self.y+self.h else False
               
    def set_style(self, highlight=False, pressed=False):
        self.p.stroke(*self.pressed_stroke) if pressed else self.p.stroke(*self.stroke)
        self.p.fill(*self.highlight_fill) if highlight else self.p.fill(0)
        self.p.stroke_weight(self.stroke_weight)
        self.p.rect_mode(self.p.CENTER)
        self.p.text_align(self.p.CENTER, self.p.CENTER)
        
    def set_text_style(self):
        self.p.fill(*self.text_fill);   self.p.stroke(*self.text_stroke)

class Button(GUI_Element):
    def __init__(self, execute_func=None, func_args=None, func_kwargs=None, **kwargs):
        """You can provide a function to be triggered by this button with execute_func."""
        w = kwargs['py5'].text_width(kwargs['label']) + 30
        self.func_args, self.func_kwargs = func_args, func_kwargs
        super().__init__(**kwargs, w=w)

        self.execute_func = execute_func
        self.prev_mouse_pressed = False
    
    def run(self):
        mouse_in = self.mouse_in()
        
        pressed = False
        if mouse_in and self.p.is_mouse_pressed:
            pressed = True
            if not self.prev_mouse_pressed:
                self.execute_func( *(self.func_args if self.func_args else ()),
                                  **(self.func_kwargs if self.func_kwargs else {}))
        
        with self.p.push_style():
            self.set_style(highlight=mouse_in, pressed=pressed)
            self.p.rect(self.center[0], self.center[1], 
                        self.w-self.stroke_weight, self.h-self.stroke_weight)
            self.set_text_style()
            self.p.text(self.label, self.center[0], self.center[1])
        
        self.prev_mouse_pressed = self.p.is_mouse_pressed

class Text_Input(GUI_Element):
    pass

def print_coordinates(py5=None):
    """"print the currently moused over coordinates"""
    print(f'x: {py5.mouse_x} y: {py5.mouse_y}')

if __name__=='__main__':
    import py5
    
    confirm_click = lambda : print('triggered button')
    print_text = lambda text, end='' : print(f'{text}{end}')
    change_background = lambda : py5.background(py5.random(255), py5.random(255), py5.random(255))
    
    def setup():
        py5.size(500, 500, py5.P2D)
        py5.background(0)
        #instead of using globals, the buttons can be stored within the sketch instance
        py5.get_current_sketch().buttons = [
                    Button(py5=py5, label='simple button', pos=(20, 50),
                           execute_func=confirm_click),
                    Button(py5=py5, label='change background', pos=(50, 0), 
                           execute_func=change_background),
                    Button(py5=py5, label='print to console', pos=(150, 30), 
                           execute_func=print_text,
                           func_args=('first line',), func_kwargs={'end':'\nsecond line :)'})]
        
    def draw():
        [button.run() for button in py5.get_current_sketch().buttons]
        #print_coordinates(py5)
    
    py5.run_sketch()

class Selector(GUI_Element):
    pass

class Toggle(GUI_Element):
    pass

class Slider(GUI_Element):
    pass

class Plot:
    """While matplotlib can be incorporated into py5 sketches with its agg backend, updating its plots is very
       computationally expensive. This class offers a minimal set of plotting functionalities for situations
       where the goal is to avoid matplotlib's performance impact on the larger program."""
    def __init__(self, py5, x, y, w, h):
        self.plots = []     #contains dicts of {'xs', 'ys', 'cols', 'type'}

        self.p = py5
        self.x = x; self.y = y
        self.w = w; self.h = h

        self.graphics = self.p.create_graphics(w, h)

    def calc_dimensions(self, up_extra=0, left_extra=0, bottom_extra=0, to_graphics=False):
        if to_graphics:
            # offset the x and y positions to 0
            self.x = 0
            self.y = 0
        
        # inner sizes:
        self.xi = self.x +80 + left_extra
        self.yi = self.y +10 + up_extra
        self.wi = self.w -100 - left_extra
        self.hi = self.h -50 - up_extra - bottom_extra
        self.ri = self.xi + self.wi        #right inner
        self.bi = self.yi + self.hi        #bottom inner

        #inner inner frame:
        inner_dist = 15
        self.xii = self.xi + inner_dist
        self.yii = self.yi + inner_dist
        self.wii = self.wi - 2*inner_dist
        self.hii = self.hi - 2*inner_dist
        self.rii = self.xii + self.wii
        self.bii = self.yii + self.hii

    #-------------------------DATA ENTRY FUNCTIONS-------------------------

    def plot(self, xs:list, ys:list, color=None, stroke_weight=1):
        if len(xs) == 0 or len(xs) != len(ys):
            return
        self.plots.append({'xs': np.array(xs), 'ys': np.array(ys), 'color': color,
                           'type': 'lines', 'stroke weight': stroke_weight})

    def scatter(self, xs:list, ys:list, color:list=None, diameter=7, 
                order=None, marker='circle', stroke_weight=1, labels=None):
        if len(xs) == 0 or len(xs) != len(ys):
            return
        ys = np.array(ys) if not isinstance(ys[0], str) else ys
        self.plots.append({'xs': np.array(xs), 'ys': ys, 'color': color, 'type': 'scatter',
                           'diameter': diameter, 'marker': marker, 'stroke weight': stroke_weight,
                           'order': order})
    
    def axvline(self, xs:list, color=None, stroke_weight=1):
        if len(xs) == 0:
            return
        self.plots.append({'xs': np.array(xs), 'ys': np.array([]), 'color': color,
                           'type': 'vlines', 'stroke weight': stroke_weight})

    def find_ticks(self, nums, start, end, horizontal=True, decimals=None):
        # TODO: Could add an alternative find_ticks() more resembling matplotlib. If mpl plots data [0.31, ..., 1.67]
        # it won't lerp ticks from A to B, but have ~3-8 ticks (depending on size) like [0.25, 0.75, 0.125, 0.175]
        # => it will np.arange(lower, higher, tick_step) with the lower and upper being min(nums -%tick_step)
        # and max(nums + 1 - %tick_step). The tick_step is in units of .2 or .5 or 1 or 10 or... (also seen .25)
        # depending on the range dealt with to cover 3-8 ticks
        if not horizontal:
            # ! processing y coords are inverted
            start, end = end, start
        nums = np.array(nums)
        # remove duplicates to not end up with multiple axis ticks of the same initial value
        nums = np.unique(nums)
        # find the widest number text
        maxn = np.max(nums);  minn = np.min(nums)
        form = 'f'
        if decimals == None:
            decimals = 0
            diff = maxn - minn
            if diff <= 500:
                decimals = 1
            if diff <= 50:
                decimals = 2
            if diff <= 2:
                decimals = 3
            if diff <= 0.2:
                decimals = 4
            if diff < 0.001 or maxn > 1_000_000 or minn < -1_000_000:
                decimals = 2
                form = 'e'

        widest_num = maxn if maxn > np.abs(minn) else minn
        
        if horizontal:
            num_width = self.p.text_width(f'{widest_num:.{decimals}{form}}') * 1.5
        else:
            num_width = self.p.text_ascent() * 2.5
        
        num_ticks = int(abs(end-start) / num_width)
        if nums.shape[0] < num_ticks:
            # less numbers than ticks exists, put a tick at every number
            tick_positions = np.linspace(start, end, nums.shape[0])
            if nums.shape[0] == 1:
                tick_positions = np.array([(start + end)/2])
            tick_labels = [f'{num:.{decimals}{form}}' for num in np.sort(nums)]
        else:            
            tick_positions = np.linspace(start, end, num_ticks)
            tick_labels = remap(tick_positions, start, end, minn, maxn)
            tick_labels = [f'{tick_label:.{decimals}{form}}' for tick_label in tick_labels]
        return list(zip(tick_positions, tick_labels))

    def find_categorical_ticks(self, labels, start, end, order=None, horizontal=False):
        if not horizontal:
            # ! processing y coords are inverted
            start, end = end, start
        uniques = list(set(labels))
        if order:
            uniques = list(reversed(order))
        tick_positions = np.linspace(start, end, len(uniques))
        if len(uniques) == 1:
            tick_positions = np.array([(start + end)/2])
        tick_lookup = {uniques[i]: tick_positions[i] for i in range(len(uniques))}
        
        return list(zip(tick_positions, uniques)), tick_lookup

    def show(self, x_decimals=None, y_decimals=None, title=None, xlabel=None, ylabel=None, to_py5image=False,
             show_outline=False, show_helper_lines=False):

        if not to_py5image:
            p = self.p
        else:
            p = self.graphics
            p.begin_draw()
            p.background(0)

        #-------------------------NUMERICAL OR CATEGORICAL Y AXIS-------------------------
        y_categorical = None
        order = None
        for plt in self.plots:
            # exclude plots like vlines, which don't have y data
            if len(plt['ys']) != 0:
                if y_categorical == None:
                    # define y_categorical based on the first plt
                    y_categorical = True if isinstance(plt['ys'][0], str) else False
                else:
                    if y_categorical != isinstance(plt['ys'][0], str):
                        print('mixing numerical and categorical y axis data - aborting plot')
                        return
            if 'order' in plt:
                order = plt['order']

        #-------------------------CALC CIMENSIONS AND DRAW TEXT-------------------------
        # TODO: If a calc_label_width function gets modularized from the start of the find_ticks functions, we can already
        # calc the max label width of all_ys from the y ticks functions and can improve the left_extra margin!
        p.no_fill();  p.stroke(255)
        p.stroke_weight(1);  p.text_size(14)

        text_height = p.text_ascent() + p.text_descent()
        up_extra = text_height if title else 0
        left_extra = text_height if ylabel else 0
        bottom_extra = text_height if xlabel else 0
        self.calc_dimensions(up_extra=up_extra, left_extra=left_extra, bottom_extra=bottom_extra, to_graphics=to_py5image)    

        with p.push_style():
            p.text_align(p.CENTER, p.CENTER)
            p.fill(255);    p.stroke(255)
            if title:
                with p.push_style():
                    p.text_size(16)
                    p.text(title, (self.x + (self.x + self.w))/2, self.y+ text_height/2)
            if xlabel:
                p.text(xlabel, (self.xi + self.ri)/2, (self.y+self.h) - text_height)
            if ylabel:
                with p.push_matrix():
                    p.translate(self.x + text_height/2, (self.y + (self.y+self.h))/2)
                    p.rotate(-p.HALF_PI)
                    p.text(ylabel, 0, 0)

        #-------------------------FIND X TICKS-------------------------
        all_xs = np.array([])
        for plt in self.plots:
            all_xs = np.append(all_xs, plt['xs'])

        if all_xs.shape == (0,):
            print('the plot data is empty')
            self.reset()
            return
        min_all_xs = np.min(all_xs);    max_all_xs = np.max(all_xs)
        xticks = self.find_ticks(all_xs, self.xii, self.rii, decimals=x_decimals)
        
        #-------------------------FIND Y TICKS-------------------------
        if not y_categorical:
            all_ys = np.array([])
            for plt in self.plots:
                all_ys = np.append(all_ys, plt['ys'])
            min_all_ys = np.min(all_ys);    max_all_ys = np.max(all_ys)
            yticks = self.find_ticks(all_ys, self.yii, self.bii, horizontal=False, decimals=y_decimals)
        else:
            all_ys = []
            for plt in self.plots:
                all_ys.extend(plt['ys'])
            yticks, ylookup = self.find_categorical_ticks(all_ys, self.yii, self.bii, horizontal=False, order=order)
        
        #-------------------------DRAW PLOT FRAME-------------------------
        if show_outline:
            p.rect(self.x, self.y, self.w-1, self.h-1)
        if show_helper_lines:
                p.rect(self.xii, self.yii, self.wii, self.hii)
        p.rect(self.xi, self.yi, self.wi, self.hi)
        
        with p.push_style():
            p.stroke(255);  p.fill(255)
            p.text_align(p.CENTER, p.TOP)
            # Draw the x ticks
            for xt in xticks:
                p.line(xt[0], self.bi, xt[0], self.bi+5)
                p.text(xt[1], xt[0], self.bi + 10)
            p.text_align(p.RIGHT, p.CENTER)
            for yt in yticks:
                p.line(self.xi, yt[0], self.xi-5, yt[0])
                p.text(yt[1], self.xi -10, yt[0] - p.text_descent())

        #-------------------------DRAW PLOTS-------------------------
        for plt in self.plots:
            xs = plt['xs']
            ys = plt['ys']
            #-------------------------VLINES-------------------------
            if plt['type'] == 'vlines':
                xcoords = remap(xs, min_all_xs, max_all_xs, self.xii, self.rii)
                
                with p.push_style():
                    set_stroke = self.create_stroke_function(plt, p)
                    p.stroke_weight(plt['stroke weight'])
                    for i in range(xs.shape[0]):
                        set_stroke(i)
                        p.line(xcoords[i], self.yii, xcoords[i], self.bii,)
                
            #-------------------------SCATTER-------------------------
            if plt['type'] == 'scatter':
                xcoords = remap(xs, min_all_xs, max_all_xs, self.xii, self.rii)
                if not y_categorical:
                    ycoords = remap(ys, min_all_ys, max_all_ys, self.bii, self.yii)
                else:
                    ycoords = [ylookup[y] for y in ys]

                with p.push_style():
                    # TODO: If plt['labels'] != None: make a lookup dictionary with a rand bright color for each
                    # unique label - use list(set(labels)) to get uniques and provide the lookup as set_fill
                    if plt['marker'] == 'circle':
                        set_fill = self.create_fill_function(plt, p)
                        p.no_stroke()
                        for i in range(xs.shape[0]):
                            set_fill(i)
                            p.circle(xcoords[i], ycoords[i], plt['diameter'])
                    elif plt['marker'] == 'line':
                        set_stroke = self.create_stroke_function(plt, p)
                        p.stroke_weight(plt['stroke weight'])
                        for i in range(xs.shape[0]):
                            set_stroke(i)
                            p.line(xcoords[i], ycoords[i] -5, xcoords[i], ycoords[i] +5)

            #-------------------------GRAPH-------------------------
            if plt['type'] == 'lines' and not y_categorical:
                if xs.shape == (1,):
                    # not enough points to draw a line
                    self.reset()
                else:
                    xcoords = remap(xs, min_all_xs, max_all_xs, self.xii, self.rii)
                    ycoords = remap(ys, min_all_ys, max_all_ys, self.bii, self.yii)
                    # ! processing y coords are inverted

                    with p.push_style():
                        set_stroke = self.create_stroke_function(plt, p)
                        p.stroke_weight(plt['stroke weight'])
                        for i in range(xs.shape[0] -1):
                            set_stroke(i)
                            p.line(xcoords[i], ycoords[i], xcoords[i+1], ycoords[i+1],)
        
        self.reset()
        if to_py5image:
            p.end_draw()
            return p

    def create_fill_function(self, plt, p):
        if not plt['color']:
            set_fill = lambda i: p.fill(255)
        elif self.is_number(plt['color'][0]):
            set_fill = lambda i: p.fill(*plt['color'])
        else:
            # it is a list with a color for every data point
            set_fill = lambda i: p.fill(*plt['color'][i])
        return set_fill

    def create_stroke_function(self, plt, p):
        if not plt['color']:
            set_stroke = lambda i: p.stroke(255)
        elif self.is_number(plt['color'][0]):
            set_stroke = lambda i: p.stroke(*plt['color'])
        else:
            # it is a list with a color for every data point
            set_stroke = lambda i: p.stroke(*plt['color'][i])
        return set_stroke

    def is_number(self, var):
        return isinstance(var, int) or isinstance(var, float)

    def reset(self):
        self.plots = []

def legend(py5, col_lookup:dict, x, y, horizontal=True, to_graphics=False, frame=True):
    p = py5
    with p.push_style():
        p.stroke_weight(1);  p.text_size(14)
        text_height = p.text_ascent() + p.text_descent()
    labels = list(col_lookup.keys())
    colors = list(col_lookup.values())
    label_lengths = [p.text_width(label) for label in labels]
    color_width = 20
    offset = 10
    if horizontal:            
        total_length = sum(label_lengths) + len(labels)*color_width + len(labels)*offset*2
        total_height = text_height
    else:
        total_length = p.text_width(max(labels, key=len)) + color_width + offset*2
        total_height = len(labels) * (text_height)
    if to_graphics:
        x, y = 0, 0
        p = py5.create_graphics(int(total_length), int(total_height))
        p.begin_draw()
    p.push_style()
    p.stroke_weight(1);  p.text_size(14)
    p.text_align(p.LEFT, p.TOP)
    p.fill(0);  p.stroke(255)
    if frame:
        p.rect(x, y, total_length-1, total_height-1)
    p.fill(255)
    with p.push_matrix():
        p.translate(x, y)
        for i in range(len(labels)):
            with p.push_style():
                p.no_stroke(); p.fill(*colors[i])
                p.translate(offset/2, 0)
                p.rect(0, 5, color_width, text_height-10)
            p.translate(color_width + offset, 0)
            p.text(labels[i], 0, -1)
            p.translate(offset/2, 0)
            if horizontal:
                p.translate(label_lengths[i], 0)
            else:
                p.translate(-color_width - 2*offset, text_height)
    p.pop_style()
    if to_graphics:
        p.end_draw()
        return p

class PrintZero:
    """Print zero: An extended print function.
       print0('my text', color=...) can be used as a print() function supporting colors.
       Awailable colors are: white, bright_white, cyan, red, yellow, green, blue, magenta
       
       A call to print0 can also be provided with a priority= and a topic=. If a priority is provided, only a
       print0() call that has a priority <= the priority_threshold or that has a topic among the string list of
       priority_topics will actually get printed.
       This enables using different levels and focus topics of debug information.
       For example print0('mytext', color='red', priority=1) can be used for an important alarm.
       The priority level goes from 1=most important to 3 or above=least important.
       
       You can print0.set_priority_threshold(number) and print0.set_priority_topics(['connection', 'user', ...])
       to define the priority_threshold and priority_topics."""
    
    def __init__(self):
        self.priority_threshold = 2
        self.priority_topics = []
        #Any call to os.system enables printing colors in the command prompt afterwards
        os.system('')
        self.styles = {'white': '\033[37m',
                       'bright_white': '\033[97m',
                       'cyan': '\033[96m',
                       'red': '\033[91m',
                       'yellow': '\033[33m',
                       'green': '\033[92m',
                       'blue': '\033[94m',
                       'magenta': '\033[95m',
                       'reset': '\033[0m'}

    def set_priority_threshold(self, threshold:int):
        """Only print0() with priority <= threshold will be printed"""
        self.priority_threshold = threshold
        return self

    def set_priority_topics(self, topics:tuple|list):
        self.priority_topics = topics
        return self

    def __call__(self, text:str, color:str='white', priority:int=0, topic:str=None):
        if priority <= self.priority_threshold or topic in self.priority_topics:
            print(f'{self.styles[color]}{text}{self.styles["reset"]}')

print0 = PrintZero()