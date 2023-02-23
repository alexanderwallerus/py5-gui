class GUI_Element:
    def __init__(self, py5=None, pos=(0,0), label='', w=30):
        self.x = pos[0]; self.y = pos[1]
        self.label = label
        self.p = py5
        
        self.h = 30;     self.w = w+30
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
    def __init__(self, execute_func=None, **kwargs):
        """You can provide a function to be triggered by this button with execute_func."""
        w = kwargs['py5'].text_width(kwargs['label'])
        super().__init__(**kwargs, w=w)

        self.execute_func = execute_func
        self.prev_mouse_pressed = False
    
    def run(self):
        mouse_in = self.mouse_in()
        
        pressed = False
        if mouse_in and self.p.is_mouse_pressed:
            pressed = True
            if not self.prev_mouse_pressed:
                self.execute_func()             
        
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
    
    print_text = lambda : print('triggered button')
    change_background = lambda : py5.background(py5.random(255), py5.random(255), py5.random(255))
    
    def setup():
        py5.size(500, 500, py5.P2D)
        py5.background(0)
        #instead of using globals, the buttons can be stored within the sketch instance
        py5.get_current_sketch().buttons = [
                    Button(py5=py5, label='change background', pos=(50, 0), 
                           execute_func=change_background),
                    Button(py5=py5, label='print to console', pos=(150, 30), 
                           execute_func=print_text)]          
        
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