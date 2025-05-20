
from turtle import *
import turtle

bgcolor('black')
colormode(255)
shape('circle')
shapesize(3)
pensize(2)
#hideturtle()
turtle.speed(0)
color('black')
pencolor('white')
pd()
turtle.degrees(360)
colors = [
    (255, 0 ,255),    # 0 - magenta
    (0, 255, 255),    # 1 - cyan
    ]

def meta_stamp(depth):
    if depth == 0:
        return
    stamp()
    fd(60)
    stamp()
    fd(60)
    stamp()
    back(120)
    rt(60)
    meta_stamp(depth-2)



lt(90)
meta_stamp(12)

done()
