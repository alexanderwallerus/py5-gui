import os
from .utils.plot import Plot, legend    # the relative . is important for a pip install to find modules relative to the parent package (from py5gui.utils.plot import... would also work)
import time
import py5
from typing import Callable

font_loaded, font = False, None

# global list of text_input elements to be used for the key event
text_inputs = []
# global list of all existing elements. If they all belong to the same sketch you can run them all with
# the global .run() function
elements = []
organizers = []

# the py5 sketch instance to be used by default. It can either be set through use_sketch(sketch) when using 
# py5 class mode or be infered when using py5 module mode
s = None

def remap(value, inFrom, inTo, outFrom, outTo):
    if inFrom == inTo:
        # special case where in-values are the same => remap() would zero divide => broadcast center as result
        return (value*0) + ((outFrom + outTo)/2)
    return outFrom + (outTo - outFrom) * ((value - inFrom) / (inTo - inFrom))

def use_sketch(sketch:py5.Sketch):
    """Set the default sketch to be used for subsequently created elements 
    and hook the UI into the sketch's key_pressed for Text_Input elements.
    Notably Text_Input elements will also require your sketch to possess a def key_pressed(key_event): function.
    This can function can be empty i.e. - pass - but it has to exist for the Text_Input to hook into it.
    
    This function is only needed when using py5 in class mode. In module mode the single py5 instance
    will automatically be utilized for created elements.
    
    This function allows you to leave out the sketch= argument for created elements in class mode.
    When using py5 in class mode provide the instance you want to connnect to 
    (typically self in def setup()) as an argument.

    Args:
        sketch (py5.Sketch, optional): he py5 sketch to be used when in class mode, so typically this argument is self. Defaults to None.
    """

    global s
    s = sketch
    s._add_post_hook('key_pressed', 'key_reading_hook', forward_key)

def forward_key(sketch:py5.Sketch):
    global text_inputs
    key, key_code = sketch.key, sketch.key_code
    for text_input in text_inputs:
        text_input.process_key(key, key_code)

def run():
    global elements
    for e in elements:
        e.run()
    for o in organizers:
        o.draw()

class Element:
    def __init__(self, sketch:py5.Sketch=None, pos:tuple=(0,0), label:str='', w:int=30, h:int=30):
        """A general ui element parent class

        Args:
            sketch (py5.Sketch, optional): the sketch to be used for the element. If none is provided it will
                - in py5 module mode use the single existing py5 sketch
                - in class mode use the sketch that has been set with use_sketch(). Defaults to None.
            pos (tuple, optional): the left top xy position of the created element. Defaults to (0,0).
            label (str, optional): label. Defaults to ''.
            w (int, optional): the width of the element. You may not always know this at time of creation, i.e. when you 
                want the width to fit the text_width of a text you create in the element's def __init__().
                For this case elements possess a update_width(new_width) function to update the width. Defaults to 30.
            h (int, optional): the height of the element. Defaults to 30.
        """
        global s, elements

        if sketch is None:
            if s is None:
                self.s = py5.get_current_sketch()
                self.s._add_post_hook('key_pressed', 'key_reading_hook', forward_key)
            else:
                self.s = s
        else:
            self.s = sketch
        
        self.label = label
        self.h = h;     self.w = w
        self.update_xy(x=pos[0], y=pos[1])
        
        self.fill = (0,);   self.stroke = (127,);   self.pressed_stroke=(255,)
        self.highlight_fill = (32,)
        self.text_fill = (255,);    self.text_stroke = (127,)
        self.stroke_weight = 3

        global font_loaded, font
        if not font_loaded:
            # only create and load the font the first time it is needed
            font_path = os.path.abspath(os.path.join(__file__, '..', 'fonts', 'roboto',  'Roboto-Regular.ttf'))
            font = self.s.create_font(font_path, 12)
            font_loaded = True
        self.font = font
        font_loaded = True

        elements.append(self)
    
    def update_xy(self, x=None, y=None):
        """update the center when changing the xy"""
        self.x = x
        self.y = y
        self.center = (self.x + self.w/2, self.y + self.h/2)

    def update_width(self, w=30):
        self.w = w
        self.center = (self.x + self.w/2, self.y + self.h/2)    
    
    def mouse_in(self):
        return True if self.s.mouse_x > self.x and self.s.mouse_x < self.x+self.w and \
               self.s.mouse_y > self.y and self.s.mouse_y < self.y+self.h else False
               
    def set_style(self, highlight=False, pressed=False, align_left=False):
        self.s.stroke(*self.pressed_stroke) if pressed else self.s.stroke(*self.stroke)
        self.s.fill(*self.highlight_fill) if highlight else self.s.fill(0)
        self.s.stroke_weight(self.stroke_weight)
        self.s.text_font(self.font)
        self.s.rect_mode(self.s.CENTER)
        if align_left:
            self.s.text_align(self.s.LEFT, self.s.CENTER)
        else:
            self.s.text_align(self.s.CENTER, self.s.CENTER)
        
    def set_text_style(self):
        self.s.fill(*self.text_fill);   self.s.stroke(*self.text_stroke)

class Button(Element):
    def __init__(self, on_click:Callable=None, func_args:list=None, func_kwargs:dict=None, **kwargs):
        """A clickable button that can trigger functions

        Args:
            pos (tuple, optional): the left top (x, y) position of the created element. Defaults to (0,0).
                Optional when used within the context of a Row() or Col().
            on_click (Callable, optional): A function to be triggered upon clicking the button. Defaults to None.
            func_args (list, optional): extra arguments for the provided on_click functions. Defaults to None.
            func_kwargs (dict, optional): extra keyword arguments for the provided on_click functions. Defaults to None.
        """
        
        self.func_args, self.func_kwargs = func_args, func_kwargs
        super().__init__(**kwargs)
        self.update_width(self.s.text_width(self.label) + 30)

        self.on_click = on_click
        self.prev_mouse_pressed = False
    
    def run(self):
        mouse_in = self.mouse_in()
        
        pressed = False
        if mouse_in and self.s.is_mouse_pressed:
            pressed = True
            if not self.prev_mouse_pressed:
                self.on_click( *(self.func_args if self.func_args else ()),
                                  **(self.func_kwargs if self.func_kwargs else {}))
        
        with self.s.push_style():
            self.set_style(highlight=mouse_in, pressed=pressed)
            self.s.rect(self.center[0], self.center[1], 
                        self.w-self.stroke_weight, self.h-self.stroke_weight)
            self.set_text_style()
            self.s.text(self.label, self.center[0], self.center[1])
        
        self.prev_mouse_pressed = self.s.is_mouse_pressed

class Slider(Element):
    def __init__(self, min:float=0.0, max:float=1.0, value:float=None, width:int=150,
                 on_change:Callable=None, label:str=None, step_decimals:int=None, 
                 func_args:list=None, func_kwargs:dict=None, **kwargs):
        """Slider Element

        Args:
            pos (tuple, optional): the left top (x, y) position of the created element. Defaults to (0,0).
                Optional when used within the context of a Row() or Col().
            min (float, optional): minimal slider end. Defaults to 0.0.
            max (float, optional): maximal slider end. Defaults to 1.0.
            value (float, optional): starting slider value - (min+max)/2 at default. Defaults to None.
            width (int, optional): pixel width of the slider. Defaults to 150.
            on_change (Callable, optional): You can provide a function that accepts at least one argument here. Every time you finish a
            slider drag this function will be run - The function's first argument is provided with the slider value. Defaults to None.
            label (str, optional): a text description visible in the slider. Defaults to None.
            step_decimals (int, optional): 
                step_decimals allows you to decide a have the slider only lock onto specific steps in your min-max range,
                i.e. for step_decimals at 0: 0, 1, 2... at 1: 0.0, 0.1, 0.2,..., 
                at 2: 0.00, 0.01, 0.02,... at -1: 0, 10, 100,... at -2: 0, 100, 10000... and so on'''. Defaults to None.
            func_args (list, optional): extra arguments for the on_change function. Defaults to None.
            func_kwargs (dict, optional): keyword arguments for the on_change function. Defaults to None.
        """
        super().__init__(h=20, **kwargs)
        if value is None:
            self.value_ = (max + min) / 2
        else:
            self.value_ = value
        self.min, self.max = min, max
        self.update_width(width)
        self.isDragged = False
        self.on_change, self.func_args, self.func_kwargs = on_change, func_args, func_kwargs

        self.label = None
        self.knob_height = self.h
        self.label = label
        if self.label is not None:
            self.h = self.h *1.6
            while self.s.text_width(self.label) >= self.w - 1.5*self.knob_height:
                self.label = self.label[:-1]
        self.step_decimals = step_decimals

    def run(self):
        with self.s.push_style():
            if(not self.isDragged and self.s.is_mouse_pressed):
                if(self.s.mouse_x >= self.x and self.s.mouse_x <= self.x + self.w and
                self.s.mouse_y >= self.y-10 and self.s.mouse_y <= self.y + 24):
                    self.isDragged = True
            if(self.isDragged and not self.s.is_mouse_pressed):
                self.isDragged = False
                if self.on_change is not None:
                    self.on_change(self.value_, *(self.func_args if self.func_args else ()),
                                               **(self.func_kwargs if self.func_kwargs else {}))
            if(self.isDragged):
                newVal = self.s.remap(self.s.mouse_x, self.x, self.x + self.w,
                                self.min, self.max)
                self.value_ = float(self.s.constrain(newVal, self.min, self.max))
                if not self.step_decimals is None:
                    self.value_ = round(self.value_, self.step_decimals)

            self.set_style(highlight=self.mouse_in(), pressed=self.isDragged)
            # subtract half heights from both edges that only the knob will cover when at the edge
            self.s.rect(self.center[0], self.center[1], self.w-self.knob_height, self.h, 8)
            elliPos = self.s.remap(self.value_, self.min, self.max, 
                                   self.x+self.knob_height/2, self.x+self.w-self.knob_height/2)
            self.s.ellipse(elliPos, self.y + self.h - self.knob_height/2, self.knob_height, self.knob_height)

            self.set_text_style()
            self.s.text(f'{self.value_:.5g}', self.center[0], self.y + self.h - self.knob_height/2)
            if self.label is not None:
                self.s.fill(192)
                self.s.text_align(self.s.RIGHT, self.s.TOP)
                self.s.text(self.label, self.x+self.w-15, self.y+2)

    def update_value(self, value):
        self.value_ = float(value)
        if not self.step_decimals is None:
            self.value_ = round(self.value_, self.step_decimals)

    value:float = property(fget=lambda self : self.value_, fset=update_value)

class Text_Input(Element):
    def __init__(self, w:int=150, on_enter:Callable=None, label:str='enter input', default:str='', 
                 func_args:list=None, func_kwargs:dict=None, use_hook:bool=True, **kwargs):
        """Text Input field. Click to select and write a text input.
        
        IMPORTANT: For the Text_Input element to read your key presses your sketch requires a def key_pressed(key_event): function.
        This function just has to be defined - can be a stub or empty like:   def key_pressed(key_event): pass   
        
        You can provide a function to be triggered when pressing enter with on_enter.
        This function will receive the written input text as its first argument

        Args:
            pos (tuple, optional): the left top (x, y) position of the created element. Defaults to (0,0).
                Optional when used within the context of a Row() or Col().
            w (int, optional): width of the element. Defaults to 150.
            on_enter (Callable, optional): A function to run when pressing enter with at least one argument.
                This first argument will be provided with the current input field content upon execution. Defaults to None.
            label (str, optional): a prompt description for the requested input. Defaults to 'enter input'.
            default (str, optional): the starting input. Defaults to ''.
            func_args (list, optional): Extra arguments to use for your on_enter function. The current input field content will be added as
                a first argument. Defaults to None.
            func_kwargs (dict, optional): Extra keyword arguments to use for your on_enter function. Defaults to None.
            use_hook (bool, optional): When use_hook=False your writing speed will be limited by the set framerate, which typically 
                will be below accustomed keyboard writing speed instead of hooking to the immediate key_pressed function. Defaults to True.
        """
        
        super().__init__(label=label, **kwargs, w=w)
        self.active = False
        self.input = str(default)
        self.execute_func, self.func_args, self.func_kwargs = on_enter, func_args, func_kwargs
        
        # use_hook = True allows running a text input within draw() without need for a key_pressed() function
        self.use_hook = use_hook
        self.prev_key_pressed = False
        self.cursor = len(self.input)
        
        global text_inputs
        text_inputs.append(self)

    def run(self):
        mouse_in = self.mouse_in()
        pressed = False
        if self.s.is_mouse_pressed:
            if mouse_in: 
                pressed = True
                self.active = True
            else:
                self.active = False

        if not self.use_hook:
            self.read_sketch()

        with self.s.push_style():
            self.set_style(highlight=mouse_in, pressed=pressed, align_left=True)
            self.s.rect(self.center[0], self.center[1], 
                        self.w-self.stroke_weight, self.h-self.stroke_weight)
            self.set_text_style()
            self.s.rect_mode(self.s.CORNER)
            self.s.text(self.input, self.x+7, self.y, self.w-15, self.h)

            if self.active and time.time() % 1.5 > 0.75:
                cursor_offset = self.s.text_width(self.input[0:self.cursor])
                text_height = self.s.text_ascent() + self.s.text_descent()
                self.s.line(self.x+8+cursor_offset, self.center[1] - text_height/2,
                            self.x+8+cursor_offset, self.center[1] + text_height/2)
            
            if self.input == '':
                self.s.fill(127)
            else:
                self.s.fill(64)
            self.s.text_align(self.s.RIGHT)
            self.s.text(self.label, self.x+self.w-7, self.center[1])

    def read_sketch(self):
        """Alternative to approach to the callback to be run within the frame loop. This doesn't require a callback
        from the sketche's def key_pressed() through connect_keyboard(key_event) or a hook but can only read one key press
        per frame.
        """
        if self.active:
            if not self.prev_key_pressed and self.s.is_key_pressed:
                self.process_key(self.s.key, self.s.key_code)
        self.prev_key_pressed = self.s.is_key_pressed

    def process_key(self, key_char, key_code):
        if self.active:
            if key_char == '\n':
                if not self.execute_func is None:
                    self.execute_func(self.input, *(self.func_args if self.func_args else ()),
                                            **(self.func_kwargs if self.func_kwargs else {}))
            elif key_code == 37:
                # left arrow
                self.cursor = max(self.cursor - 1, 0)
            elif key_code == 39:
                # right arrow
                self.cursor = min(self.cursor + 1, len(self.input))
            elif key_code == 8 and self.cursor != 0:
                # backspace
                self.input = self.input[0:self.cursor-1] + self.input[self.cursor:]
                self.cursor = max(self.cursor - 1, 0)
            elif key_code == 127 or key_code == 147:
                # delete
                self.input = self.input[0:self.cursor] + self.input[self.cursor+1:]
            elif key_char.isprintable():
                    # self.input += key_char
                    self.input = self.input[0:self.cursor] + key_char + self.input[self.cursor:]
                    self.cursor = min(self.cursor + 1, len(self.input))

    def update_value(self, value):   self.input = str(value)
    value:str = property(fget=lambda self : self.input, fset=update_value)

def connect_keyboard(key_event):
    """Alternative to use_sketch() that can be called from a sketch's def key_pressed() for forwarding key presses
    to Text_Input elements.

    # Example:
    def key_pressed(e):
        ui.connect_keyboard_ui(e)
    """

    # An alternatives to this approach could be checking p.key within the input's .run() which makes it loose keys
    # that are typed faster than its framerate, or using from pynput.keyboard import Key, Listener which seems
    # to come with a small performance impact (~300 hz in a 2700hz to 2400hz example) The pynput approach
    # should still be implemented as an alternative for less performance critical applications
    global text_inputs
    for text_input in text_inputs:
        text_input.process_key(key_event.key, key_event.key_code)

class Toggle(Element):
    def __init__(self, value:bool=False, labels:str|list[str,str]='', 
                 on_click:Callable=None, func_args:list=None, func_kwargs:dict=None, **kwargs):
        """A True/False toggle that will switch upon click. You can get or override the current value
        with the toggle.value variable.

        Args:
            pos (tuple, optional): the left top (x, y) position of the created element. Defaults to (0,0).
                Optional when used within the context of a Row() or Col().
            value (bool, optional): Starting Value. Defaults to False.
            labels (str | list[str,str], optional): The two label alternatives the toggle will show depending
            on its state. If only a string is provided this string will always be shown instead. Defaults to ''.
            on_click (Callable, optional): You can provide a function that accepts at least one argument here. Every time toggle click
            this function will be run - The function's first argument is provided with the new toggle value. Defaults to None.
            func_args (list, optional): extra arguments for the on_change function. Defaults to None.
            func_kwargs (dict, optional): keyword arguments for the on_change function. Defaults to None.
        """
        super().__init__(**kwargs)

        if type(labels) == str:
            w = self.s.text_width(labels) + 30
            self.single_label = True
        else:
            w = max(self.s.text_width(labels[0]), self.s.text_width(labels[1])) + 30
            self.single_label = False
        self.update_width(w)
        self.on_click, self.func_args, self.func_kwargs = on_click, func_args, func_kwargs
        self.prev_mouse_pressed = False

        self.labels = labels
        self.value = value

    def run(self):
        mouse_in = self.mouse_in()
        
        pressed = False
        if mouse_in and self.s.is_mouse_pressed:
            pressed = True
            if not self.prev_mouse_pressed:
                self.value = not self.value
                if not self.on_click is None:
                    self.on_click(self.value, *(self.func_args if self.func_args else ()),
                                            **(self.func_kwargs if self.func_kwargs else {}))

        with self.s.push_style():
            self.set_style(highlight=mouse_in, pressed=pressed)
            if self.value:
                self.s.stroke(63,127,127)
            else:
                self.s.stroke(127,63,63)
            self.s.rect(self.center[0], self.center[1], 
                        self.w-self.stroke_weight, self.h-self.stroke_weight)
            self.set_text_style()
            if self.single_label:
                self.s.fill(127,192,192) if self.value else self.s.fill(192,127,127)
                self.s.text(self.labels, self.center[0], self.center[1])
            elif self.value:
                self.s.fill(127,192,192)
                self.s.text(self.labels[1], self.center[0], self.center[1])
            else:
                self.s.fill(192,127,127)
                self.s.text(self.labels[0], self.center[0], self.center[1])
        
        self.prev_mouse_pressed = self.s.is_mouse_pressed

class Text(Element):
    # TODO
    def __init__(self, text='', w=100, h=20, **kwargs):
        super().__init__(w=w, h=h, **kwargs)
        pass

    def run():
        pass

class Minimal_Base(Element):
    # TODO
    pass

class Selector(Element):
    pass

def connect_keyboard(key_event):
    """A key_event forwarding function to be used within your sketch's def key_pressed().
    This allows text_inputs to read the keyboard.
    Example:

    def key_pressed(e):
        ui.connect_keyboard_ui(e)
    """

    # An alternatives to this approach could be checking p.key within the input's .run() which makes it loose keys
    # that are typed faster than its framerate, or using from pynput.keyboard import Key, Listener which seems
    # to come with a small performance impact (~300 hz in a 2700hz to 2400hz example) The pynput approach
    # should still be implemented as an alternative for less performance critical applications
    global text_inputs
    for text_input in text_inputs:
        text_input.process_key(key_event)

class Organizer:
    def __init__(self, sketch:py5.Sketch=None, pos:tuple[int,int]=(0,0), max_w=None, max_h=None):
        # TODO: add invisible borders argument, consider skip first spacer argument
        
        if sketch is None:
            if s is None:
                self.s = py5.get_current_sketch()
                self.s._add_post_hook('key_pressed', 'key_reading_hook', forward_key)
            else:
                self.s = s
        else:
            self.s = sketch

        self.spacer_height = 10
        self.spacer_width = 10
        self.elements = []
        self.x, self.y = pos[0], pos[1]
        self.w, self.h = None, None
        self.max_w, self.max_h = max_w, max_h
        self.update_xy(pos[0], pos[1])

        global organizers
        organizers.append(self)

    def update_xy(self, x=None, y=None):
        self.x = x
        self.y = y

    def run(self):
        for element in self.elements:
            element.run()
        self.draw()

    def draw(self):
        with self.s.push_style():
            self.s.stroke(127,);      self.s.no_fill();     self.s.stroke_weight(1)
            self.s.rect(self.x, self.y, self.w, self.h)

    def add(self, element:Element):
        self.elements.append(element)
        return element

    def __enter__(self):
        return self # makes the "with Col() as col" work

    def __exit__(self, *args):
        pass

    # def __del__(self):
    #     print('running del')
    #     for i in reversed(range(len(self.elements))):
    #         print(f'deleting {i}')
    #         del self.elements[i]
    #     # super().__del__()

class Col(Organizer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.offset_h = self.y + self.spacer_height/2
    
    def add(self, element:Element|Organizer):
        if isinstance(element, Organizer) and element.h == None:
            print(f'organizer {element} is still incomplete lacking height and won\'t be added')
            return
        if self.max_h == None or self.offset_h + element.h + self.spacer_height/2 < self.y + self.max_h:
            if self.max_w != None and element.w + self.spacer_width > self.max_w:
                print(f'the column width is limited: {self.max_w}, {element} is too wide and won\'t be added')
                return
            self.elements.append(element)
            element.update_xy(self.x + self.spacer_width/2, self.offset_h)
            self.offset_h += element.h + self.spacer_height
            return element
        else:
            print(f'{element} doesn\'t fit in the column and won\'t be added')

    def __exit__(self, *args):
        self.organize_elements()

    def organize_elements(self):
        if self.max_w != None:
            self.w = self.max_w
        else:
            # no width provided, fit it to contained elements
            max_w = 0
            for e in self.elements:
                max_w = max(max_w, e.w)
            self.w = max_w + self.spacer_width
        if self.max_h != None:
            self.h = self.max_h
        else:
            self.h = self.offset_h - self.y - self.spacer_width/2

    def update_xy(self, x=None, y=None):
        super().update_xy(x, y)
        # update elements after movement
        offset_h = self.y + self.spacer_height/2
        for element in self.elements:
            element.update_xy(self.x + self.spacer_width/2, offset_h)
            offset_h += element.h + self.spacer_height

class Row(Organizer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.offset_w = self.x + self.spacer_width/2
    
    def add(self, element:Element|Organizer):
        if isinstance(element, Organizer) and element.w == None:
            print(f'organizer {element} is still incomplete lacking width and won\'t be added')
            return
        if self.max_w == None or self.offset_w + element.w + self.spacer_width/2 < self.x + self.max_w:
            if self.max_h != None and element.h + self.spacer_height > self.max_h:
                print(f'the row height is limited: {self.max_h}, {element} is too high and won\'t be added')
                return
            self.elements.append(element)
            element.update_xy(self.offset_w, self.y + self.spacer_height/2)
            self.offset_w += element.w + self.spacer_width
            return element
        else:
            print(f'{element} doesn\'t fit in the row and won\'t be added')
      
    def __exit__(self, *args):
        self.organize_elements()
    
    def organize_elements(self):
        if self.max_h != None:
            self.h = self.max_h
        else:
            # no height provided, fit it to contained elements
            max_h = 0
            for e in self.elements:
                max_h = max(max_h, e.h)
            self.h = max_h + self.spacer_height
        if self.max_w != None:
            self.w = self.max_w
        else:
            self.w = self.offset_w - self.x - self.spacer_height/2

    def update_xy(self, x=None, y=None):
        super().update_xy(x, y)
        # update elements after movement
        offset_w = self.x + self.spacer_width/2
        for element in self.elements:
            element.update_xy(offset_w, self.y + self.spacer_height/2)
            offset_w += element.w + self.spacer_width


def print_coordinates(sketch:py5.Sketch=None):
    """"print the currently moused over coordinates"""
    print(f'x: {sketch.mouse_x} y: {sketch.mouse_y}')

if __name__ == '__main__':
    pass

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