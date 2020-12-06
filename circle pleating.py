import tkinter.filedialog
from tkinter.filedialog import askopenfile
from tkinter import *
from tkinter.ttk import *
import pathlib


root = Tk()
canvas2 = Canvas(root, width=900, height=500)
canvas2.pack()
canvas2.create_rectangle(50,100,350,400,fill='white',outline="black")
canvas2.create_rectangle(400,100,700,400,fill='white',outline="black")


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
    return (float(tm)*300)+50 #works for both left and right squares
def pyy(tm):
    return 400-(float(tm)*300)
def displaycp():
    global paths, edges, nodes
    paths = []
    edges = []
    nodes = [] #we reset this everytime we import a new .tmd5 file
    canvas2.create_rectangle(50,100,350,400,fill='white',outline="black")
    canvas2.create_rectangle(400,100,700,400,fill='white',outline="black")
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
enter.place(x=120,y=50)

enter = Button(canvas2,text="extract creases",command=makecp)
#enter.place(x=165,y=200)

enter = Button(canvas2,text="export as .cp file",command=file_save)
enter.place(x=125,y=420)


#=============================================================


def bpify():
    global nodes,edges, scale,mingrid
    canvas2.delete('all')
    displaycp()
    scale = float(tmfile[4])
    mingrid=int(1/scale)+1  #the minimum grid size is the reciprocal of the scale value, rounded up
    #perhaps require that the grid be even if there is book symmetry?
    draw_grid(mingrid)
    canvas2.create_text(600,85,text=" Grid size: "+str(mingrid))
    draw_flaps()
    pythas()
#=======
def pyx2(tm):
        return (float(tm)*300)+400
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
        self.x = x
        self.y = y
        self.flaplength = flaplength
    def example(self):
        self.x =+ 2
        self.y =+ 1
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
    displaycp() #on the left side
    draw_grid(mingrid)
    canvas2.create_text(600,85,text=" Grid size: "+str(mingrid))
    draw_flaps()
    pythas()
    
#=======
    
class Path():
    def __init__(self,index, tmlength,node1, node2): #tmlength is in units, and is the minimum length
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
            if nodes[n].index == self.node2:
                self.x2 = approx_nodes[n].x
                self.y2 = approx_nodes[n].y
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
            paths.append(Path(tmfile[scanner+1],tmfile[scanner+2],tmfile[scanner+15],tmfile[scanner+16]))
            
def pythas():
    find_paths()
    find_pythas()

def find_pythas():
    for x in range(0,len(paths)):
        paths[x].find_coordinates()
        if paths[x].is_too_tight():
            canvas2.create_line(pyx2(paths[x].x1),pyy(paths[x].y1),pyx2(paths[x].x2),pyy(paths[x].y2),fill='red')
        if paths[x].needs_pytha():
            canvas2.create_line(pyx2(paths[x].x1),pyy(paths[x].y1),pyx2(paths[x].x2),pyy(paths[x].y2),fill='orange')
    
     #i think i had some similar detection thing in the boxpleater. flap lengths and coordinates--you might need the paths in order to deal with rivers though.
        #its annoying bc paths don't list which nodes are associated, but perhaps the nodes list which paths are associated with it?

#then start making a bpcpfile
#can also reuse the click detection i set up for the other thing

enter = Button(canvas2,text="Approximate to bp",command=bpify)
enter.place(x=400,y=50)
enter = Button(canvas2,text="Increase grid size",command=bumpgrid)
enter.place(x=550,y=50)




