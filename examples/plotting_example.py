import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import py5gui
import py5
import random

def setup():
    global plt0, plt1, xs, ys0, ys1, scatter_y, scatter_col, vlines, scatter_choice
    py5.size(530, 1000, py5.P2D)
    plt0 = py5gui.Plot(x=10, y= 10, w=500, h=500)
    plt1 = py5gui.Plot( x=10, y=570, w=500, h=200, sketch=py5.get_current_sketch())

    xs = [0]
    ys0 = [0]
    ys1 = [0]

    scatter_y = [0]
    scatter_col = [random.choice([(255, 0, 0), (0, 255, 255)])]
    
    vlines = []
    scatter_choice = [random.choice(['a', 'b', 'c'])]
    py5.frame_rate(300)

def draw():
    global plt0, plt1, xs, ys0, ys1, scatter_y, scatter_col, vlines, scatter_choice
    py5.background(0)

    plt0.plot(xs, ys0, color=(0, 255, 255), stroke_weight=3)
    plt0.plot(xs, ys1, color=(255, 0, 0))
    plt0.scatter(xs, scatter_y, diameter=7, marker='circle')
    plt0.show(title='3 plots', xlabel='x axis', ylabel='y axis')#, ylimit=(-10, None))

    py5gui.legend({'red': (255, 0, 0)}, 100, 485, frame=False)

    legend = py5gui.legend({'graph 0': (0, 255, 255), 'graph 1': (255, 0, 0), 'scatter': (255,)},
                           0, 0, horizontal=False, to_graphics=True, sketch=py5.get_current_sketch())
    py5.image(legend, 10, 485)

    plt1.axvline(vlines, color=(255, 255, 0))
    plt1.scatter(xs, scatter_choice, color=scatter_col, marker='line', stroke_weight=1, order=['a', 'b', 'c', 'd'])
    plt1.show(x_decimals=0, show_outline=True)

    # Plotting with 2 y axis and plotting to py5image example 
    plt2 = py5gui.Plot(x=0, y=0, w=500, h=200)
    plt2.scatter(xs, scatter_choice, color=scatter_col, marker='triangle', y_axis=1)
    plt2.plot(xs, ys0, y_axis=0)
    img = plt2.show(to_py5image=True)
    py5.image(img, 10, 800, 500, 200)

    # py5gui.print_coordinates(py5.get_current_sketch())

    x = float(py5.frame_count)

    xs.append(x)
    ys0.append(ys0[-1] + py5.random(-1., 1.))
    ys1.append(ys1[-1] + py5.random(-1., 1.))
    if random.random() < 0.01:
        vlines.append(x)# + random.uniform(-10, 10))
    scatter_y.append(scatter_y[-1] + py5.random(-1., 1.))
    scatter_col.append(random.choice([(255, 0, 0), (0, 255, 255)]))
    scatter_choice.append(random.choice(['a', 'b', 'c']))


py5.run_sketch()