import numpy as np
import py5

def remap(value, inFrom, inTo, outFrom, outTo):
    if inFrom == inTo:
        # special case where in-values are the same => remap() would zero divide => broadcast center as result
        return (value*0) + ((outFrom + outTo)/2)
    return outFrom + (outTo - outFrom) * ((value - inFrom) / (inTo - inFrom))

class Plot:
    """While matplotlib can be incorporated into py5 sketches with its agg backend, updating its plots is very
       computationally expensive. This class offers a minimal set of plotting functionalities for situations
       where the goal is to avoid matplotlib's performance impact on the larger program.
       
       .plot(), .scatter() and .axvline() can be used to enter xs and ys data, which will be plotted together
       upon the following call to .show(). by default .plot(), .scatter(). and .axvline will use the left y_axis=0, but you
       can use y_axis=1 to have their data be plotted on a secondary y axis, to keep track of different ranges of numerical 
       results, or even mix numerical and categorical data in the same plot."""
    def __init__(self, x, y, w, h, sketch:py5.Sketch=None):
        self.plots = []     #contains dicts of {'xs', 'ys', 'cols', 'type'}

        if sketch == None:
            self.s = py5.get_current_sketch()
        else:
            self.s = sketch
        
        self.move(x, y, w, h)

        self.graphics = self.s.create_graphics(w, h)

    def calc_dimensions(self, up_extra=0, left_extra=0, bottom_extra=0, right_extra=0, to_graphics=False):
        if to_graphics:
            # offset the x and y positions to 0
            self.x = 0
            self.y = 0
        
        # inner sizes:
        self.xi = self.x +20 + left_extra
        self.yi = self.y +10 + up_extra
        self.wi = self.w -30 - left_extra - right_extra
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

    def move(self, x:int=0, y:int=0, w:int=500, h:int=200):
        """update the position and size of the plot.
        When only rendering to a py5image x and y can be ignored.

        Args:
            x (int): upper left x position
            y (int): upper left y position
            w (int): width
            h (int): height
        """
        self.x, self.y, self.w, self.h = x, y, w, h

    #-------------------------DATA ENTRY FUNCTIONS-------------------------

    def plot(self, xs:list, ys:list, color=None, stroke_weight=1, y_axis=0):
        if len(xs) == 0 or len(xs) != len(ys):
            return
        self.plots.append({'xs': np.array(xs), 'ys': np.array(ys), 'color': color,
                           'type': 'lines', 'stroke weight': stroke_weight, 'y axis': y_axis})
        return self

    def scatter(self, xs:list, ys:list, color:list=None, diameter=7, 
                order=None, marker='circle', stroke_weight=1, y_axis=0):
        if len(xs) == 0 or len(xs) != len(ys):
            return
        ys = np.array(ys) if not isinstance(ys[0], str) else ys
        self.plots.append({'xs': np.array(xs), 'ys': ys, 'color': color, 'type': 'scatter',
                           'diameter': diameter, 'marker': marker, 'stroke weight': stroke_weight,
                           'order': order, 'y axis': y_axis})
        return self
    
    def axvline(self, xs:list, color=None, stroke_weight=1, y_axis=0):
        if len(xs) == 0:
            return
        self.plots.append({'xs': np.array(xs), 'ys': [], 'color': color,
                           'type': 'vlines', 'stroke weight': stroke_weight, 'y axis': y_axis})
        return self

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

    def tick_pos_labels(self, p, nums, start, end, horizontal=True, decimals=None, ylimit:tuple=(None, None)):
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
        if ylimit[0] is not None:
            minn = ylimit[0]
        if ylimit[1] is not None:
            maxn = ylimit[1]
        if ylimit[0] is not None or ylimit[1] is not None:
            # create numbers in the range filling the required ylimit
            nums = np.linspace(minn, maxn, 30)
        
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

    def tick_pos_labels_categorical(self, labels, start, end, order=None, horizontal=False):
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

    def check_categorical_numerical(self, plots):
        plotable = True
        categorical = None
        order = None
        for plt in plots:
            # exclude plots like vlines, which don't have y data
            if len(plt['ys']) != 0:
                if categorical == None:
                    # define y_categorical based on the first plt
                    categorical = True if isinstance(plt['ys'][0], str) else False
                else:
                    if categorical != isinstance(plt['ys'][0], str):
                        print('mixing numerical and categorical y axis data - aborting plot')
                        plotable = False
                        self.reset()
                       
            if 'order' in plt:
                order = plt['order']
        if categorical == None and len(plots) > 0:
            # no y data encountered, i.e. a vlines only plot => simulate y data
            categorical = True
            for plt in plots:
                plt['ys'] = ['' for x in plt['xs']]
        return categorical, order, plotable


    def show(self, x_decimals=None, title=None, xlabel=None, ylabel=None, y_decimals=None,
             ylimit=(None, None), autoscale_in_ylimits=(False,False), to_py5image=False, 
             y_decimals_1=None, ylimit_1=(None, None), autoscale_in_ylimits_1=(False,False),  
             empty_warning=True, show_outline=False, show_helper_lines=False):
        """If to_py5image=True, this function will not draw onto the plot's py5 instance, but instead return a py5_graphics
        object with the plot, which can be used as an image, when the plot doesn't need to be updated every frame.
        .show() can also draw a title, xlabel, and ylabel if provided with a string argument.
        .show() can further be provided with x_decimals= and y_decimals= for overriding the shown decimal places, and with a
        ylimit=(lower, upper) to only plot numerical data above and/or below a certain min, max value pair.
        ylimit=(-7, None) for example would only plot data points with a y of -7 or higher.
        autoscale_in_ylimits (default:(False,False)): when using ylimit and/or ylimit_1 reenable autoscaling within those limits."""
        if not to_py5image:
            p = self.s
        else:
            p = self.graphics
            p.begin_draw()
            p.background(0)

        multi_y = [plt['y axis'] == 1 for plt in self.plots]
        multi_y = True if True in multi_y else False
                
        ylimits_as_minmax = [True if (ylimit[0] is not None) and (not autoscale_in_ylimits[0]) else False,
                             True if (ylimit[1] is not None) and (not autoscale_in_ylimits[1]) else False]
        
        ylimits_as_minmax_1 = [True if (ylimit_1[0] is not None) and (not autoscale_in_ylimits_1[0]) else False,
                               True if (ylimit_1[1] is not None) and (not autoscale_in_ylimits_1[1]) else False]


        #-------------------------NUMERICAL OR CATEGORICAL Y AXIS-------------------------

        plotable = [True, True]
        plots = [plt for plt in self.plots if plt['y axis'] == 0]
        y_categorical, order, plotable[0] = self.check_categorical_numerical(plots)

        if multi_y:
            plots_1 = [plt for plt in self.plots if plt['y axis'] == 1]
            y_categorical_1, order_1, plotable[1] = self.check_categorical_numerical(plots_1)
        
        if False in plotable:
            if to_py5image:
                p.end_draw()
                return p
            return

        #-------------------------COLLECT ALL XS AND YS-------------------------
        
        all_xs = np.array([])
        if not y_categorical:
            all_ys = np.array([])
            for plt in plots:
                # if ylimits exist, min/max out data points.
                if ylimit[0] is not None:
                    plt['ys'] = np.maximum(plt['ys'], ylimit[0])
                    # could mask out these data points like this; but would need another plotable check for if all data is filtered out
                    # mask = plt['ys'] >= ylimit[0]
                    # plt['ys'] = plt['ys'][mask]
                    # plt['xs'] = plt['xs'][mask]
                if ylimit[1] is not None:
                    plt['ys'] = np.minimum(plt['ys'], ylimit[1])
                all_xs = np.append(all_xs, plt['xs'])
                all_ys = np.append(all_ys, plt['ys'])           
        else:
            all_ys = []
            for plt in plots:
                all_ys.extend(plt['ys'])
                all_xs = np.append(all_xs, plt['xs'])

        all_xs_1 = np.array([])
        if multi_y:
            if not y_categorical_1:
                all_ys_1 = np.array([])
                for plt in plots_1:
                    if ylimit_1[0]:
                        plt['ys'] = np.maximum(plt['ys'], ylimit_1[0])
                    if ylimit_1[1]:
                        plt['ys'] = np.minimum(plt['ys'], ylimit_1[1])
                    all_xs_1 = np.append(all_xs_1, plt['xs'])
                    all_ys_1 = np.append(all_ys_1, plt['ys'])
            else:
                all_ys_1 = []
                for plt in plots_1:
                    all_xs_1 = np.append(all_xs_1, plt['xs'])
                    all_ys_1.extend(plt['ys'])

        # test if data exists before continuing further
        total_xs = np.concatenate((all_xs, all_xs_1))       
        if total_xs.shape == (0,):
            if empty_warning:
                print('the plot data is empty')
            self.reset()
            if to_py5image:
                p.end_draw()
                return p
            return
        
        min_all_xs = np.min(total_xs);    max_all_xs = np.max(total_xs)
        if not y_categorical:
            min_all_ys = np.min(all_ys);    max_all_ys = np.max(all_ys)
            if ylimits_as_minmax[0]:
                min_all_ys = ylimit[0]
            if ylimits_as_minmax[1]:
                max_all_ys = ylimit[1]
        if multi_y and not y_categorical_1:
            min_all_ys_1 = np.min(all_ys_1);    max_all_ys_1 = np.max(all_ys_1)
            if ylimits_as_minmax_1[0]:
                min_all_ys_1 = ylimit_1[0]
            if ylimits_as_minmax_1[1]:
                max_all_ys_1 = ylimit_1[1]

        #-------------------------CALC DIMENSIONS-------------------------
        p.no_fill();  p.stroke(255)
        p.stroke_weight(1);  p.text_size(14)

        if y_categorical:
            widest_y_label = p.text_width(max(all_ys, key=len))
        else:
            decimals, form = self.find_decimals(min_all_ys, max_all_ys, decimals=y_decimals)
            widest_y_label = max(p.text_width(f'{min_all_ys:.{decimals}{form}}'),
                                 p.text_width(f'{max_all_ys:.{decimals}{form}}'))
        
        text_height = p.text_ascent() + p.text_descent()
        up_extra = text_height if title else 0
        left_extra = text_height + widest_y_label if ylabel else widest_y_label
        bottom_extra = text_height if xlabel else 0
        right_extra = 0

        if multi_y:
            if y_categorical_1:
                widest_y_label_1 = p.text_width(max(all_ys_1, key=len))
            else:
                decimals_1, form_1 = self.find_decimals(min_all_ys_1, max_all_ys_1, decimals=y_decimals_1)
                widest_y_label_1 = max(p.text_width(f'{min_all_ys_1:.{decimals_1}{form_1}}'),
                                       p.text_width(f'{max_all_ys_1:.{decimals_1}{form_1}}'))
            right_extra += widest_y_label_1 + 2

        self.calc_dimensions(up_extra=up_extra, left_extra=left_extra, bottom_extra=bottom_extra, 
                             right_extra=right_extra, to_graphics=to_py5image)    

        #-------------------------FIND TICKS-------------------------
        total_xs = np.concatenate((all_xs, all_xs_1))
        xticks = self.tick_pos_labels(p, total_xs, self.xii, self.rii, decimals=x_decimals)
        
        ylookup, ylookup_1 = None, None
        min_max_y = [min_all_ys if ylimits_as_minmax[0] else None, max_all_ys if ylimits_as_minmax[1] else None]
        if y_categorical:
            yticks, ylookup = self.tick_pos_labels_categorical(all_ys, self.yii, self.bii, horizontal=False, order=order)
        else:
            yticks = self.tick_pos_labels(p, all_ys, self.yii, self.bii, horizontal=False, decimals=y_decimals, ylimit=min_max_y)
        
        if multi_y:
            min_max_y_1 = [min_all_ys_1 if ylimits_as_minmax_1[0] else None, max_all_ys_1 if ylimits_as_minmax_1[1] else None]
            if y_categorical_1:
                yticks_1, ylookup_1 = self.tick_pos_labels_categorical(all_ys_1, self.yii, self.bii, horizontal=False, order=order_1)
            else:
                yticks_1 = self.tick_pos_labels(p, all_ys_1, self.yii, self.bii, horizontal=False, decimals=y_decimals_1, ylimit=min_max_y_1)

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
            if multi_y:
                p.text_align(p.LEFT, p.CENTER)
                for yt in yticks_1:
                    p.line(self.ri, yt[0], self.ri+5, yt[0])
                    p.text(yt[1], self.ri +10, yt[0] - p.text_descent())

        #-------------------------DRAW PLOTS-------------------------
        
        if multi_y:
            y_info = {'categorical': True, 'lookup': ylookup_1} if y_categorical_1 else \
                     {'categorical': False, 'min': min_all_ys_1, 'max': max_all_ys_1}
            self.draw_plots(p, plots_1, min_all_xs, max_all_xs, y_info)
        y_info = {'categorical': True, 'lookup': ylookup} if y_categorical else \
                 {'categorical': False, 'min': min_all_ys, 'max': max_all_ys}
        self.draw_plots(p, plots, min_all_xs, max_all_xs, y_info)

        self.reset()
        if to_py5image:
            p.end_draw()
            return p

    def draw_plots(self, p, plots, min_all_xs, max_all_xs, y_info):
        """Draw all provided plots. """
        if y_info['categorical']:
            get_y_coords = lambda ys: [y_info['lookup'][y] for y in ys]
        else:
            get_y_coords = lambda ys: remap(ys, y_info['min'], y_info['max'], self.bii, self.yii)
            # ! processing y coords are inverted

        for plt in plots:
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
                ycoords = get_y_coords(ys)

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
                    elif plt['marker'] == 'cross':
                        set_stroke = self.create_stroke_function(plt, p)
                        p.stroke_weight(plt['stroke weight'])
                        for i in range(xs.shape[0]):
                            set_stroke(i)
                            p.line(xcoords[i] -3, ycoords[i] -3, xcoords[i] +3, ycoords[i] +3)
                            p.line(xcoords[i] -3, ycoords[i] +3, xcoords[i] +3, ycoords[i] -3)
                    elif plt['marker'] == 'square':
                        set_fill = self.create_fill_function(plt, p)
                        p.no_stroke()
                        p.rect_mode(p.CENTER)
                        for i in range(xs.shape[0]):
                            set_fill(i)
                            p.rect(xcoords[i], ycoords[i], plt['diameter'], plt['diameter'])
                    elif plt['marker'] == 'triangle':
                        set_fill = self.create_fill_function(plt, p)
                        p.no_stroke()
                        p.rect_mode(p.CENTER)
                        for i in range(xs.shape[0]):
                            set_fill(i)
                            p.triangle(xcoords[i]-3, ycoords[i]+3, xcoords[i], ycoords[i]-3, xcoords[i]+3, ycoords[i]+3,)
                    else:
                        # The marker is a custom character/text
                        set_fill = self.create_fill_function(plt, p)
                        p.no_stroke()
                        p.text_align(p.CENTER, p.CENTER)
                        for i in range(xs.shape[0]):
                            set_fill(i)
                            p.text(plt['marker'], xcoords[i], ycoords[i])            

            #-------------------------GRAPH-------------------------
            if plt['type'] == 'lines':
                if xs.shape != (1,):
                    # at shape == (1,) there are not enough points to draw a line
                    xcoords = remap(xs, min_all_xs, max_all_xs, self.xii, self.rii)
                    ycoords = get_y_coords(ys)   

                    with p.push_style():
                        set_stroke = self.create_stroke_function(plt, p)
                        p.stroke_weight(plt['stroke weight'])
                        for i in range(1, xs.shape[0]):
                            set_stroke(i)
                            p.line(xcoords[i-1], ycoords[i-1], xcoords[i], ycoords[i],)

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

def legend(col_lookup:dict, x, y, horizontal=True, to_graphics=False, frame=True, sketch:py5.Sketch=None):
    if sketch == None:
        s = py5.get_current_sketch()
    else:
        s = sketch
    
    with s.push_style():
        s.stroke_weight(1);  s.text_size(14)
        text_height = s.text_ascent() + s.text_descent()
        labels = list(col_lookup.keys())
        colors = list(col_lookup.values())
        label_lengths = [s.text_width(label) for label in labels]
        color_width = 20
        offset = 10
        if horizontal:
            total_length = sum(label_lengths) + len(labels)*color_width + len(labels)*offset*2
            total_height = text_height
        else:
            total_length = s.text_width(max(labels, key=len)) + color_width + offset*2
            total_height = len(labels) * (text_height)
    if to_graphics:
        x, y = 0, 0
        s = sketch.create_graphics(int(total_length), int(total_height))
        s.begin_draw()
    s.push_style()
    s.stroke_weight(1);  s.text_size(14)
    s.text_align(s.LEFT, s.TOP)
    s.fill(0);  s.stroke(255)
    if frame:
        s.rect(x, y, total_length-1, total_height-1)
    s.fill(255)
    with s.push_matrix():
        s.translate(x, y)
        for i in range(len(labels)):
            with s.push_style():
                s.no_stroke(); s.fill(*colors[i])
                s.translate(offset/2, 0)
                s.rect(0, 5, color_width, text_height-10)
            s.translate(color_width + offset, 0)
            s.text(labels[i], 0, 0)
            s.translate(offset/2, 0)
            if horizontal:
                s.translate(label_lengths[i], 0)
            else:
                s.translate(-color_width - 2*offset, text_height)
    s.pop_style()
    if to_graphics:
        s.end_draw()
        return s