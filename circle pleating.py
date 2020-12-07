import tkinter.filedialog
from tkinter.filedialog import askopenfile
from tkinter import *
from tkinter.ttk import *
import pathlib


root = Tk()
canvas2 = Canvas(root, width=900, height=600)
canvas2.pack()
canvas2.create_rectangle(200,50,700,550,fill='white',outline="black", width = 2)


boi = Tk()
boi.withdraw()


def file_open(): #includes the other functions, such as displaying the cp
    canvas2.delete('all')
    global filename, tmfile, cpfile, vertices, creases
    file = askopenfile(mode = 'r', filetypes = (("treemaker files","*.tmd5"),("all files","*.*")))
    if file is not None: # asksaveasfile return `None` if dialog closed with "cancel".
        filename = pathlib.Path(file.name).name
        def load_words(filename):
            with open(filename) as word_file:
                valid_words = list(word_file.read().split())
            return valid_words
        tmfile = load_words(filename)
    vertices = ['buffer item'] #because treemaker counts from 1 rather than 0, so the buffer item lines everything up
    creases = ['buffer item']
    makecp()
    displaycp()

def findvertices():
    global vertices
    for x in range(0,len(tmfile)):
        if tmfile[x] == 'vrtx':
            vertices.append((tmfile[x+2],tmfile[x+3]))        
def findcreases():
    findvertices()
    global creases
    for x in range(0,len(tmfile)):
        if tmfile[x] == 'crse':
            mv = int(tmfile[x+8])+0
            if mv==1:  #tm's mountains should be valley
                mv = 3
            elif mv ==3: #edges, like when you cut off the corner
                mv = 1  
            creases.append((vertices[int(tmfile[x+4])],vertices[int(tmfile[x+5])],mv))
            #also need to extract the m/v, or at least axial vs hinge vs ridge
def cp(tm): #converts tm coordinates to .cp coordinates
    return (float(tm)*400)-200
def pyx(tm): #converts tm coordinates to the python coordinates. for now, it is a 300x300 pixel square. this works only for the left
    return (float(tm)*500)+200 #works for both left and right squares
def pyy(tm):
    return 550-(float(tm)*500)
def displaycp():
    global paths, edges, nodes
    paths = []
    edges = []
    nodes = [] #we reset this everytime we import a new .tmd5 file
    canvas2.create_rectangle(200,50,700,550,fill='white',outline="black", width = 2)
    for x in range(1,len(creases)):
        if creases[x][2]==2:
            canvas2.create_line(pyx(creases[x][0][0]),pyy(creases[x][0][1]),pyx(creases[x][1][0]),pyy(creases[x][1][1]),fill="red")
        if creases[x][2]==3:
            canvas2.create_line(pyx(creases[x][0][0]),pyy(creases[x][0][1]),pyx(creases[x][1][0]),pyy(creases[x][1][1]),fill="blue")
        if creases[x][2]==1:
            canvas2.create_line(pyx(creases[x][0][0]),pyy(creases[x][0][1]),pyx(creases[x][1][0]),pyy(creases[x][1][1]),fill="black")
        if creases[x][2]==0:
            canvas2.create_line(pyx(creases[x][0][0]),pyy(creases[x][0][1]),pyx(creases[x][1][0]),pyy(creases[x][1][1]),fill="cyan",width = 0.5)
    
def makecp():
    global cpfile
    cpfile = ["1 -200 -200 -200 200", "1 -200 200 200 200", "1 200 200 200 -200", "1 200 -200 -200 -200"]
    findcreases()
    for x in range(1, len(creases)):
        cpfile.append(str(creases[x][2])+" "+str(cp(creases[x][0][0]))+" "+str(cp(creases[x][0][1]))+" "+str(cp(creases[x][1][0]))+" "+str(cp(creases[x][1][1])))
def file_save():
    filename = tkinter.filedialog.asksaveasfile(mode='w+', defaultextension=".cp",parent = boi)
    if filename is None: # asksaveasfile return `None` if dialog closed with "cancel".
        boi.withdraw()
        return
    for x in range(0,len(cpfile)):
        #print(cp_file[x])
        filename.write(str(cpfile[x])+"\n")
        
    filename.close()
    boi.withdraw()


enter = Button(canvas2,text="Open treemaker file",command=file_open)
enter.place(x=20,y=70)

enter = Button(canvas2,text="extract creases",command=makecp) #relic of the past
#enter.place(x=165,y=200)

enter = Button(canvas2,text="export as .cp file",command=file_save)
enter.place(x=20,y=450)


#=============================================================


def bpify():
    global nodes,edges, scale,mingrid
    canvas2.delete('all')
    #displaycp()
    canvas2.create_rectangle(200,50,700,550,fill='white',outline="black", width = 2)
    scale = float(tmfile[4])
    mingrid=int(1/scale)+1  #the minimum grid size is the reciprocal of the scale value, rounded up
    #perhaps require that the grid be even if there is book symmetry?
    draw_grid(mingrid)
    canvas2.create_text(770,120,text=" Grid size: "+str(mingrid))
    draw_flaps()
    pythas()
    for p in range(0,len(paths)):
        if paths[p].is_too_tight():
            bumpgrid()
            pass
#=======
def pyx2(tm):
        return pyx(tm) #originally there were two squares, but here i combine them
def draw_grid(mingrid):
    position = 1/mingrid
    for x in range(0,mingrid-1):
        canvas2.create_line(pyx2(position), pyy(0), pyx2(position), pyy(1), width = 0.5, fill = "light gray")    #vertical line
        canvas2.create_line(pyx2(0),pyy(position), pyx2(1), pyy(position), width = 0.5, fill = "light gray")    #horizontal line
        position = position+1/mingrid
#========
def draw_flaps():
    find_nodes()
    find_edges()
    assign_flap_lengths()
    approximate_positions(mingrid)
    draw()
class Leaf_node():
    def __init__(self,index,x,y,flaplength):
        self.index = index
        self.x = float(x)
        self.y = float(y)
        self.flaplength = float(flaplength)
        self.paths=[]
    def drawx(self):
        canvas2.create_line(pyx(self.x),pyy(self.y),pyx(self.x-min(self.x,self.y,float(self.flaplength)/mingrid)),pyy(self.y-min(self.x,self.y,float(self.flaplength)/mingrid)),fill='red')  #down and left
        canvas2.create_line(pyx(self.x),pyy(self.y),pyx(self.x+min(1-self.x,self.y,float(self.flaplength)/mingrid)),pyy(self.y-min(1-(self.x),self.y,float(self.flaplength)/mingrid)),fill='red')  #down and right
        canvas2.create_line(pyx(self.x),pyy(self.y),pyx(self.x+min(1-self.x,1-self.y,float(self.flaplength)/mingrid)),pyy(self.y+min(1-(self.x),1-self.y,float(self.flaplength)/mingrid)),fill='red')  #up and right
        canvas2.create_line(pyx(self.x),pyy(self.y),pyx(self.x-min(self.x,1-self.y,float(self.flaplength)/mingrid)),pyy(self.y+min(self.x,1-self.y,float(self.flaplength)/mingrid)),fill='red')  #up and left

def drawxs():
    for n in range(0,len(nodes)):
        nodes[n].drawx()
def find_nodes():
    global nodes
    nodes = []
    for scanner in range(0,len(tmfile)):
        if tmfile[scanner]=="node" and tmfile[scanner+6]=="true":
            nodes.append(Leaf_node(tmfile[scanner+1],tmfile[scanner+2],tmfile[scanner+3],0))#set flap lengths as 0 for now, once it finds the edges, then can assign flap length
class Edge():
    def __init__(self,index,node1,node2,length):
        self.index = index
        self.node1 = node1
        self.node2 = node2
        self.length = length
def find_edges():
    global edges
    edges = []
    for scanner in range(0,len(tmfile)):
        if tmfile[scanner]=="edge":
            edges.append(Edge(tmfile[scanner+1],tmfile[scanner+8],tmfile[scanner+9],tmfile[scanner+2]))
def assign_flap_lengths():  #could be done as a method but i think it works
    for e in range(0,len(edges)): #e is an individual edge
        for n in range(0,len(nodes)): #n is an individual node
            if nodes[n].index==edges[e].node1 or nodes[n].index==edges[e].node2: #if this is one of the edge's nodes
                nodes[n].flaplength = edges[e].length
def approximate_positions(mingrid):
    global approx_nodes
    approx_nodes = nodes[:]
    for n in range(0,len(nodes)): #also could have been done as a method
        approx_nodes[n].x=round(float(approx_nodes[n].x)*mingrid)/mingrid
        approx_nodes[n].y=round(float(approx_nodes[n].y)*mingrid)/mingrid
def draw():
    for n in range(0,len(nodes)):
        canvas2.create_oval(pyx2(approx_nodes[n].x)-1,pyy(approx_nodes[n].y)-1,pyx2(approx_nodes[n].x)+1,pyy(approx_nodes[n].y)+1,fill='black')
        canvas2.create_oval(pyx2(float(approx_nodes[n].x)-(1/mingrid)*float(approx_nodes[n].flaplength)),pyy(float(approx_nodes[n].y)-(1/mingrid)*float(approx_nodes[n].flaplength)),pyx2(float(approx_nodes[n].x)+(1/mingrid)*float(approx_nodes[n].flaplength)),pyy(float(approx_nodes[n].y)+(1/mingrid)*float(approx_nodes[n].flaplength)),outline='gray')

def bumpgrid():
    global mingrid
    mingrid = mingrid+1
    canvas2.delete('all')
    canvas2.create_rectangle(200,50,700,550,fill='white',outline="black", width = 2)
    draw_grid(mingrid)
    canvas2.create_text(770,120,text=" Grid size: "+str(mingrid))
    draw_flaps()
    pythas()

def lowergrid():
    global mingrid
    mingrid = mingrid-1
    canvas2.delete('all')
    canvas2.create_rectangle(200,50,700,550,fill='white',outline="black", width = 2)
    draw_grid(mingrid)
    canvas2.create_text(770,120,text=" Grid size: "+str(mingrid))
    draw_flaps()
    pythas()
        
#=======
    
class Path():
    def __init__(self,index, tmlength,node1, node2): #tmlength is in tree units, and is the minimum length
        self.index = index
        self.node1 = node1
        self.node2 = node2
        self.tmlength = float(tmlength)
        self.find_coordinates()
    def find_coordinates(self):
        for n in range(0,len(nodes)):
            if nodes[n].index == self.node1:
                self.x1 = approx_nodes[n].x
                self.y1 = approx_nodes[n].y
                if self.index not in approx_nodes[n].paths:
                    approx_nodes[n].paths.append(self.index)
                if self.index not in nodes[n].paths:
                    nodes[n].paths.append(self.index)
            if nodes[n].index == self.node2:
                self.x2 = approx_nodes[n].x
                self.y2 = approx_nodes[n].y
                if self.index not in approx_nodes[n].paths:
                    approx_nodes[n].paths.append(self.index)
                if self.index not in nodes[n].paths:
                    nodes[n].paths.append(self.index)
        self.bplength = max(abs(self.x1-self.x2),abs(self.y1-self.y2))
        self.bphypotenuse = ((self.x1-self.x2)**2 + (self.y1-self.y2)**2)**0.5
    def is_too_tight(self):#see if the nodes are too close. draw with red
        if self.bphypotenuse*mingrid < self.tmlength:
            return True
        else:
            return False
    def needs_pytha(self): #see if it needs a pytha
        if self.bplength*mingrid < self.tmlength and self.bphypotenuse*mingrid>self.tmlength:
            return True
        else:
            return False
        
    def is_too_loose(self): #see if the nodes are supposed to be optimal path, but are too loose. draw with green
        pass

def find_paths():
    global paths
    paths = []
    for scanner in range(0,len(tmfile)):
        if tmfile[scanner] == 'path' and tmfile[scanner+6] == "true":
            pathlength = int(tmfile[scanner+15])#the number of nodes on the path. if this number is 3 (the minimum) the next 3 numbers will the the nodes. take the first and last.
            paths.append(Path(tmfile[scanner+1],tmfile[scanner+2],tmfile[scanner+16],tmfile[scanner+15+pathlength]))
            
def pythas():
    find_paths()
    find_pythas()
    #display_pythas()

def find_pythas():
    for x in range(0,len(paths)):
        paths[x].find_coordinates()
        if paths[x].is_too_tight():
            canvas2.create_line(pyx2(paths[x].x1),pyy(paths[x].y1),pyx2(paths[x].x2),pyy(paths[x].y2),fill='red', width = 3)
        if paths[x].needs_pytha():
            canvas2.create_line(pyx2(paths[x].x1),pyy(paths[x].y1),pyx2(paths[x].x2),pyy(paths[x].y2),fill='orange', width = 3)

def display_pythas():
    for p in range(0,len(paths)):
        if paths[p].needs_pytha():
            calculate_pytha(paths[p])
        

def calculate_pytha(path):
    global x,y,flap1,flap2 #it should be fine bc the pythas calculate one at a time
    x = abs(path.x1-path.x2)*mingrid
    y = abs(path.y1-path.y2)*mingrid #because the pytha program runs it in terms of grid units
    if (path.y2-path.y1)/(path.x2-path.x1) < 0:
        needs_to_flip = False
    else:
        needs_to_flip = True  #because we took the abs of the coordinates, we don't know the orientation the pytha needs to be. we'll store this for later
    for n in range(0,len(nodes)):  #go get a flap length
        if nodes[n].index == path.node1:
            flap1 = float(nodes[n].flaplength)
    flap2 = path.tmlength - flap1
    #print(x,y,flapx,flapy)
    show_solution1()
#============================================== start pytha calculation section
def tkx(coordinate):
    return pyx(coordinate)
def tky(coordinate):
    return pyy(coordinate)


#nicecombos = []
#combos = []
#solutions = 0
def overlap():
    global bx,by,ax,ay, nicecombos, combos, solution, area
    bx = x-flap1
    by = y-flap2
    ax = flap2
    ay = flap1
    #canvas2.create_rectangle(tkx(bx),tky(by),tkx(ax),tky(ay),outline="pink",width=2)
    area = abs((ax-bx)*(ay-by))/2
    def factor(area):
        global factor1, factor2, solution, combos, nicecombos
        combos = []
        nicecombos = []
        for x in range(1,int(area)):
            y = area/x
            niceness = abs(x-y)
            if x==int(x) and y==int(y):
                nicecombos.append([niceness,x])
            else:
                combos.append([niceness,x])
        if combos == []:
            x = 0.25
            while combos == []:
                y = area/x
                niceness = abs(x-y)
                combos.append([niceness,x])
                x += 0.25
            
        if nicecombos!=[]:
            factor1 = min(nicecombos)[1]
            solution = nicecombos.index(min(nicecombos))
        else:
            factor1 = min(combos)[1]
            solution = combos.index(min(combos))
        factor2 = area/factor1
        #print(factor1,factor2, combos)
    factor(area)

def rotate():
    global a2x,a2y
    a2x=bx+ay-by
    a2y=by+ax-bx
    canvas2.create_rectangle(tkx(bx),tky(by),tkx(a2x),tky(a2y),outline="purple",width=2)

def cd1():
    global cx,cy,dx,dy,a2x,a2y
    cx = a2x+factor1
    cy= by-factor1
    dx = bx-factor2
    dy = a2y + factor2
    if dy>y:
        gap = dy-y
        dy -= gap
        dx += gap
        cy -= gap
        cx += gap
        a2y -= gap
        a2x += gap
        #print('SHIFTED DOWN')
    if cy<0:
        gap = 0-cy
        dy += gap
        dx -= gap
        cy += gap
        cx -= gap
        a2y+= gap
        a2x-= gap
        #print('SHIFTED UP')
    while a2y >=dy:
        a2y -=1
        a2x +=1
    while a2x >= cx:
        a2y+=1
        a2x-=1
    if abs(cx-dx)>x or abs(cy-dy)>y:
        global solution
        if nicecombos != []:
            del(nicecombos[solution])
        else:
            del(combos[solution])
        solution = 0
        next_solution()
        
    

def parallelogram():
    canvas2.create_line(tkx(a2x),tky(a2y),tkx(cx),tky(cy),fill="red",width=2)
    canvas2.create_line(tkx(a2x),tky(a2y),tkx(dx),tky(dy),fill="red",width=2)
    global b2x,b2y
    b2x = dx + cx-a2x
    b2y = dy + cy-a2y
    canvas2.create_line(tkx(b2x),tky(b2y),tkx(dx),tky(dy),fill="red",width=2)
    canvas2.create_line(tkx(b2x),tky(b2y),tkx(cx),tky(cy),fill="red",width=2)


def arms():
    canvas2.create_line(tkx(bx),tky(by),tkx(bx-5),tky(by-5),fill="red",width=2)
    canvas2.create_line(tkx(ax),tky(ay),tkx(a2x),tky(a2y),fill="red",width=2)
    canvas2.create_line(tkx(ax),tky(ay),tkx(ax+5),tky(ay+5),fill="red",width=2)  
def b():
    canvas2.create_line(tkx(b2x),tky(b2y),tkx(bx),tky(by),fill="red",width=2)
def ridge():
    canvas2.create_line(tkx(0),tky(y),tkx(dx),tky(dy),fill="red",width=2)
    canvas2.create_line(tkx(x),tky(0),tkx(cx),tky(cy),fill="red",width=2)


def show_solution1():
    overlap()
    rotate()
    cd1()
    parallelogram()
    b()
    arms()
    ridge()


def next_solution():
    global solution,factor1,factor2
    if nicecombos!=[]:
        if len(nicecombos) == 1:
            print("only found one solution does not go off grid. This does not mean yours is wrong if you found one.")
        elif solution < len(nicecombos):
            factor1 = nicecombos[solution][1]
            factor2 = area/factor1
            solution += 1
        elif solution >= len(nicecombos):
            solution = 0
            factor1 = nicecombos[solution][1]
            factor2 = area/factor1
    else:
        if len(combos)==1:
            print("you got unlucky lmao")
        elif solution < len(combos):
            factor1 = combos[solution][1]
            factor2 = area/factor1
            solution += 1
        else:
            solution =0
            factor1 = combos[solution][1]
            factor2 = area/factor1
    canvas2.delete("all")
    canvas2.create_rectangle(0,00,600,600,fill="white",outline="white")

    draw_grid(x,y,grid)
    draw_circles(x,y,grid,flap1,flap2)
    draw_boxes(x,y,grid,flap1,flap2)
    draw_axis(x,y,grid)

    rotate()
    cd1()
    parallelogram()
    b()
    arms()
    ridge()
#======================================================= end pytha section

#then start making a bpcpfile
#can also reuse the click detection i set up for the other thing
#the flap nearest to the click now becomes the selected flap. then options to transform the selected flap: move, but also shrink/expand
    #the shrink and expand will need to change the paths

enter = Button(canvas2,text="Approximate to bp",command=bpify)
enter.place(x=720,y=70)
enter = Button(canvas2,text="Increase grid size",command=bumpgrid)
enter.place(x=720,y=130)
enter = Button(canvas2,text="Reduce grid size",command=lowergrid)
enter.place(x=720,y=160)   #maybe an entry box for the grid size?


enter = Button(canvas2,text="Draw ridges",command=drawxs)
enter.place(x=720,y=300)


#for debugging purposes

def print_node(index):
    for n in range(0,len(nodes)):
        if nodes[n].index == index:
            print("index", nodes[n].index)
            print(nodes[n].x, nodes[n].y)
            print("paths:", nodes[n].paths)

def print_path(index):
    for p in range(0,len(paths)):
        if paths[p].index == index:
            print('index', paths[p].index)
            print(paths[p].node1, paths[p].node2)
            print(paths[p].bplength, paths[p].bphypotenuse)
            print('too tight', paths[p].is_too_tight())
            print('needs pytha', paths[p].needs_pytha())



