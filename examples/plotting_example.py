import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import py5gui
import py5
import random

def setup():
    global plt0, plt1, xs, ys0, ys1, scatter_y, scatter_col, vlines, scatter_choice
    py5.size(530, 800, py5.P2D)
    plt0 = py5gui.Plot(py5=py5.get_current_sketch(), x= 10, y= 10, w=500, h=500)
    plt1 = py5gui.Plot(py5=py5.get_current_sketch(), x= 10, y=570, w=500, h=200)

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
    plt0.scatter(xs, scatter_y, diameter=7)
    plt0.show(title='3 plots', xlabel='x axis', ylabel='y axis')
    plt0.legend({'graph 0': (0, 255, 255), 'graph 1': (255, 0, 0), 'scatter': (255,)},
                10, 465, horizontal=False)

    plt1.axvline(vlines, color=(255, 255, 0))
    plt1.scatter(xs, scatter_choice, color=scatter_col)#, order=['a', 'b', 'c', 'd'])
    plt1.show(x_decimals=0, show_outline=True)

    # # Plotting to py5image Example 
    # plt0.plot(xs, ys1, color=(255, 0, 0))
    # img = plt0.show(to_py5image=True)
    # py5.image(img, 10, 480, 110, 70)

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