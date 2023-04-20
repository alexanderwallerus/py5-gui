import numpy as np

def remap(value, inFrom, inTo, outFrom, outTo):
    if inFrom == inTo:
        # special case where in-values are the same => remap() would zero divide => broadcast center as result
        return (value*0) + ((outFrom + outTo)/2)
    return outFrom + (outTo - outFrom) * ((value - inFrom) / (inTo - inFrom))

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
        self.xi = self.x +20 + left_extra
        self.yi = self.y +10 + up_extra
        self.wi = self.w -30 - left_extra
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

    def find_decimals(self, minn, maxn, decimals=None):
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

        return decimals, form

    def find_ticks(self, p, nums, start, end, horizontal=True, decimals=None):
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
        
        decimals, form = self.find_decimals(minn, maxn, decimals=decimals)

        widest_num = maxn if maxn > np.abs(minn) else minn
        
        if horizontal:
            num_width = p.text_width(f'{widest_num:.{decimals}{form}}') * 1.5
        else:
            num_width = p.text_ascent() * 2.5
        
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
                        self.reset()
                        if to_py5image:
                            p.end_draw()
                            return p
                        return
            if 'order' in plt:
                order = plt['order']

        #-------------------------COLLECT ALL XS AND YS-------------------------
        all_xs = np.array([])
        for plt in self.plots:
            all_xs = np.append(all_xs, plt['xs'])

        if all_xs.shape == (0,):
            print('the plot data is empty')
            self.reset()
            if to_py5image:
                p.end_draw()
                return p
            return
        min_all_xs = np.min(all_xs);    max_all_xs = np.max(all_xs)

        if not y_categorical:
            all_ys = np.array([])
            for plt in self.plots:
                all_ys = np.append(all_ys, plt['ys'])
            min_all_ys = np.min(all_ys);    max_all_ys = np.max(all_ys)
        else:
            all_ys = []
            for plt in self.plots:
                all_ys.extend(plt['ys'])

        #-------------------------CALC DIMENSIONS-------------------------
        p.no_fill();  p.stroke(255)
        p.stroke_weight(1);  p.text_size(14)

        if y_categorical:
            widest_y_label = p.text_width(max(all_ys, key=len))
        else:
            widest_y = max_all_ys if max_all_ys > np.abs(min_all_ys) else min_all_ys
            decimals, form = self.find_decimals(min_all_ys, max_all_ys, decimals=y_decimals)
            widest_y_label = p.text_width(f'{widest_y:.{decimals}{form}}')           
        
        text_height = p.text_ascent() + p.text_descent()
        up_extra = text_height if title else 0
        left_extra = text_height + widest_y_label if ylabel else widest_y_label
        bottom_extra = text_height if xlabel else 0
        self.calc_dimensions(up_extra=up_extra, left_extra=left_extra, bottom_extra=bottom_extra, to_graphics=to_py5image)    

        #-------------------------FIND TICKS-------------------------
        xticks = self.find_ticks(p, all_xs, self.xii, self.rii, decimals=x_decimals)
        
        if y_categorical:
            yticks, ylookup = self.find_categorical_ticks(all_ys, self.yii, self.bii, horizontal=False, order=order)
        else:
            yticks = self.find_ticks(p, all_ys, self.yii, self.bii, horizontal=False, decimals=y_decimals)

        #-------------------------DRAW TEXT-------------------------
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
                if xs.shape != (1,):
                    # at shape == (1,) there are not enough points to draw a line
                    xcoords = remap(xs, min_all_xs, max_all_xs, self.xii, self.rii)
                    ycoords = remap(ys, min_all_ys, max_all_ys, self.bii, self.yii)
                    # ! processing y coords are inverted

                    with p.push_style():
                        set_stroke = self.create_stroke_function(plt, p)
                        p.stroke_weight(plt['stroke weight'])
                        for i in range(1, xs.shape[0]):
                            set_stroke(i)
                            p.line(xcoords[i-1], ycoords[i-1], xcoords[i], ycoords[i],)
        
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