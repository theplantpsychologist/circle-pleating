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
            vertices.append([tmfile[x+2],tmfile[x+3]])        
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
            creases.append([vertices[int(tmfile[x+4])],vertices[int(tmfile[x+5])],mv])
            #also need to extract the m/v, or at least axial vs hinge vs ridge
def cp(tm): #converts tm coordinates to .cp coordinates
    return (float(tm)*400)-200
def pyx(tm): #converts tm coordinates into python (tk) coordinates
    return (float(tm)*500)+200 
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
            canvas2.create_line(pyx(creases[x][0][0]),pyy(creases[x][0][1]),pyx(creases[x][1][0]),pyy(creases[x][1][1]),fill="red",width =2)
        if creases[x][2]==3:
            canvas2.create_line(pyx(creases[x][0][0]),pyy(creases[x][0][1]),pyx(creases[x][1][0]),pyy(creases[x][1][1]),fill="blue",width =2)
        if creases[x][2]==1:
            canvas2.create_line(pyx(creases[x][0][0]),pyy(creases[x][0][1]),pyx(creases[x][1][0]),pyy(creases[x][1][1]),fill="black",width =2)
        if creases[x][2]==0:
            canvas2.create_line(pyx(creases[x][0][0]),pyy(creases[x][0][1]),pyx(creases[x][1][0]),pyy(creases[x][1][1]),fill="cyan",width = 0.5)
    
def makecp():
    global cpfile
    cpfile = ["1 -200 -200 -200 200", "1 -200 200 200 200", "1 200 200 200 -200", "1 200 -200 -200 -200"]
    findcreases()
    no_mv = True #by default we're just gonna make everything m
    for x in range(1,len(creases)):
        if creases[x][2] ==2:
            no_mv = False
    if no_mv:
        for x in range(1,len(creases)):
            creases[x][2] = 2
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


def bpify():  #make this one do all the initial things that shouldn't be done again
    global nodes,edges, scale,mingrid, cpfile
    canvas2.delete('all')
    cpfile = ["1 -200 -200 -200 200", "1 -200 200 200 200", "1 200 200 200 -200", "1 200 -200 -200 -200"]
    #displaycp()
    canvas2.create_rectangle(200,50,700,550,fill='white',outline="black", width = 2)
    scale = float(tmfile[4])
    mingrid=int(1/scale)+1  #the minimum grid size is the reciprocal of the scale value, rounded up
    #perhaps require that the grid be even if there is book symmetry?
    draw_grid(mingrid)
    canvas2.create_text(770,121,text=" Grid size: "+str(mingrid))
    canvas2.create_text(780,105,text=" Relative efficiency: "+str(round(((1/mingrid)/scale)*100)/100))
    draw_flaps()
    pythas(True)
    '''for p in range(0,len(paths)):
        if paths[p].is_too_tight():
            initialbumpgrid()
            pass'''
    refresh() #idk why but this is needed
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
def draw_flaps(): #only used for the first time, the initial extraction and whatnot
    find_nodes()
    find_edges()
    assign_flap_lengths() #connect the edges and nodes
    approximate_positions(mingrid)
    draw()
    drawhinges()

class Leaf_node():
    def __init__(self,index,x,y,flaplength):
        self.index = index
        self.x = float(x)
        self.y = float(y)
        self.flaplength = float(flaplength)
        self.paths=[]
        self.has_pytha_ur = self.has_pytha_ul = self.has_pytha_dl = self.has_pytha_dr = False #ul = upper left, dr = down right, etc
    def drawx(self):
        if not self.has_pytha_dl:
            canvas2.create_line(pyx(self.x),pyy(self.y),pyx(self.x-min(self.x,self.y,float(self.flaplength)/mingrid)),pyy(self.y-min(self.x,self.y,float(self.flaplength)/mingrid)),fill='red',width = 2)  #down and left
            cpfile.append("2 "+str(cp(self.x))+" "+str(cp(self.y))+" "+str(cp(self.x-min(self.x,self.y,float(self.flaplength)/mingrid)))+" "+str(cp(self.y-min(self.x,self.y,float(self.flaplength)/mingrid))))
        if not self.has_pytha_dr:
            canvas2.create_line(pyx(self.x),pyy(self.y),pyx(self.x+min(1-self.x,self.y,float(self.flaplength)/mingrid)),pyy(self.y-min(1-(self.x),self.y,float(self.flaplength)/mingrid)),fill='red', width = 2)  #down and right
            cpfile.append("2 "+str(cp(self.x))+" "+str(cp(self.y))+" "+str(cp(self.x+min(1-self.x,self.y,float(self.flaplength)/mingrid)))+" "+str(cp(self.y-min(1-self.x,self.y,float(self.flaplength)/mingrid))))
        if not self.has_pytha_ur:
            canvas2.create_line(pyx(self.x),pyy(self.y),pyx(self.x+min(1-self.x,1-self.y,float(self.flaplength)/mingrid)),pyy(self.y+min(1-(self.x),1-self.y,float(self.flaplength)/mingrid)),fill='red', width = 2)  #up and right
            cpfile.append("2 "+str(cp(self.x))+" "+str(cp(self.y))+" "+str(cp(self.x+min(1-self.x,1-self.y,float(self.flaplength)/mingrid)))+" "+str(cp(self.y+min(1-self.x,1-self.y,float(self.flaplength)/mingrid))))
        if not self.has_pytha_ul:
            canvas2.create_line(pyx(self.x),pyy(self.y),pyx(self.x-min(self.x,1-self.y,float(self.flaplength)/mingrid)),pyy(self.y+min(self.x,1-self.y,float(self.flaplength)/mingrid)),fill='red', width = 2)  #up and left
            cpfile.append("2 "+str(cp(self.x))+" "+str(cp(self.y))+" "+str(cp(self.x-min(self.x,1-self.y,float(self.flaplength)/mingrid)))+" "+str(cp(self.y+min(self.x,1-self.y,float(self.flaplength)/mingrid))))
    def drawhinge(self):
        self.flaplength = float(self.flaplength)
        if not self.has_pytha_ur:
            canvas2.create_line(pyx(self.x),pyy(min(1,self.y+self.flaplength/mingrid)),pyx(min(1,self.x+self.flaplength/mingrid)),pyy(min(1,self.y+self.flaplength/mingrid)),fill='blue',width=2)
            canvas2.create_line(pyx(min(self.x+self.flaplength/mingrid,1)),pyy(self.y),pyx(min(self.x+self.flaplength/mingrid,1)),pyy(min(1,self.y+self.flaplength/mingrid)),fill='blue',width=2)
            cpfile.append("3 "+str(cp(self.x))+' '+str(cp(min(1,self.y+self.flaplength/mingrid)))+' '+str(cp(min(1,self.x+self.flaplength/mingrid)))+' '+str(cp(min(1,self.y+self.flaplength/mingrid))))
            cpfile.append("3 "+str(cp(min(self.x+self.flaplength/mingrid,1)))+' '+str(cp(self.y))+' '+str(cp(min(self.x+self.flaplength/mingrid,1)))+' '+str(cp(min(1,self.y+self.flaplength/mingrid))))

        if not self.has_pytha_ul:
            canvas2.create_line(pyx(self.x),pyy(min(1,self.y+self.flaplength/mingrid)),pyx(max(0,self.x-self.flaplength/mingrid)),pyy(min(1,self.y+self.flaplength/mingrid)),fill='blue',width=2)
            canvas2.create_line(pyx(max(0,self.x-self.flaplength/mingrid)),pyy(self.y),pyx(max(0,self.x-self.flaplength/mingrid)),pyy(min(1,self.y+self.flaplength/mingrid)),fill='blue',width=2)
            cpfile.append("3 "+str(cp(self.x))+' '+str(cp(min(1,self.y+self.flaplength/mingrid)))+' '+str(cp(max(0,self.x-self.flaplength/mingrid)))+' '+str(cp(min(1,self.y+self.flaplength/mingrid))))
            cpfile.append("3 "+str(cp(max(0,self.x-self.flaplength/mingrid)))+' '+str(cp(self.y))+' '+str(cp(max(0,self.x-self.flaplength/mingrid)))+' '+str(cp(min(1,self.y+self.flaplength/mingrid))))

        if not self.has_pytha_dr:
            canvas2.create_line(pyx(self.x),pyy(max(0,self.y-self.flaplength/mingrid)),pyx(min(1,self.x+self.flaplength/mingrid)),pyy(max(0,self.y-self.flaplength/mingrid)),fill='blue',width=2)
            canvas2.create_line(pyx(min(1,self.x+self.flaplength/mingrid)),pyy(self.y),pyx(min(1,self.x+self.flaplength/mingrid)),pyy(max(0,self.y-self.flaplength/mingrid)),fill='blue',width=2)
            cpfile.append("3 "+str(cp(self.x))+' '+str(cp(max(0,self.y-self.flaplength/mingrid)))+' '+str(cp(min(1,self.x+self.flaplength/mingrid)))+' '+str(cp(max(0,self.y-self.flaplength/mingrid))))
            cpfile.append("3 "+str(cp(min(self.x+self.flaplength/mingrid,1)))+' '+str(cp(self.y))+' '+str(cp(min(self.x+self.flaplength/mingrid,1)))+' '+str(cp(max(0,self.y-self.flaplength/mingrid))))

        if not self.has_pytha_dl:
            canvas2.create_line(pyx(self.x),pyy(max(0,self.y-self.flaplength/mingrid)),pyx(max(0,self.x-self.flaplength/mingrid)),pyy(max(0,self.y-self.flaplength/mingrid)),fill='blue',width=2)
            canvas2.create_line(pyx(max(0,self.x-self.flaplength/mingrid)),pyy(self.y),pyx(max(0,self.x-self.flaplength/mingrid)),pyy(max(0,self.y-self.flaplength/mingrid)),fill='blue',width=2)
            cpfile.append("3 "+str(cp(self.x))+' '+str(cp(max(0,self.y-self.flaplength/mingrid)))+' '+str(cp(max(0,self.x-self.flaplength/mingrid)))+' '+str(cp(max(0,self.y-self.flaplength/mingrid))))
            cpfile.append("3 "+str(cp(max(0,self.x-self.flaplength/mingrid)))+' '+str(cp(self.y))+' '+str(cp(max(0,self.x-self.flaplength/mingrid)))+' '+str(cp(max(0,self.y-self.flaplength/mingrid))))

def drawxs():
    for n in range(0,len(nodes)):
        nodes[n].drawx()
def drawhinges():
    for n in range(0,len(nodes)):
        nodes[n].drawhinge()
'''        if not nodes[n].has_pytha_:dl
        
        if not nodes[n].has_pytha_:dr'''


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
        approx_nodes[n].x=round(float(nodes[n].x)*mingrid)/mingrid
        approx_nodes[n].y=round(float(nodes[n].y)*mingrid)/mingrid
def draw():
    for n in range(0,len(nodes)):
        canvas2.create_oval(pyx2(approx_nodes[n].x)-1,pyy(approx_nodes[n].y)-1,pyx2(approx_nodes[n].x)+1,pyy(approx_nodes[n].y)+1,fill='black')
        canvas2.create_oval(pyx2(float(approx_nodes[n].x)-(1/mingrid)*float(approx_nodes[n].flaplength)),pyy(float(approx_nodes[n].y)-(1/mingrid)*float(approx_nodes[n].flaplength)),pyx2(float(approx_nodes[n].x)+(1/mingrid)*float(approx_nodes[n].flaplength)),pyy(float(approx_nodes[n].y)+(1/mingrid)*float(approx_nodes[n].flaplength)),outline='gray')

def initialbumpgrid(): #nvm this, it's kinda complicated
    global mingrid, cpfile,selectednode
    mingrid = mingrid+1
    canvas2.delete('all')
    global cpfile
    cpfile = ["1 -200 -200 -200 200", "1 -200 200 200 200", "1 200 200 200 -200", "1 200 -200 -200 -200"]
    canvas2.create_rectangle(200,50,700,550,fill='white',outline="black", width = 2)
    draw_grid(mingrid)
    canvas2.create_text(770,120,text=" Grid size: "+str(mingrid))
    canvas2.create_text(780,105,text=" Relative efficiency: "+str(round(((1/mingrid)/scale)*100)/100))
    draw_flaps()
    pythas(False)

def bumpgrid():
    global mingrid
    mingrid = mingrid+1
    refresh()
    canvas2.delete(cursor)

def lowergrid():
    global mingrid, selectednode
    mingrid = mingrid-1
    refresh()
    canvas2.delete(cursor)
#======================================
def refresh():
    canvas2.delete('all')
    global cpfile
    cpfile = ["1 -200 -200 -200 200", "1 -200 200 200 200", "1 200 200 200 -200", "1 200 -200 -200 -200"]
    draw_grid(mingrid)
    #cursor = canvas2.create_oval(pyx(selectednode.x-selectednode.flaplength/mingrid), pyy(selectednode.y-selectednode.flaplength/mingrid),pyx(selectednode.x+selectednode.flaplength/mingrid), pyy(selectednode.y+selectednode.flaplength/mingrid),width = 3,outline="black")
    canvas2.create_text(770,120,text=" Grid size: "+str(mingrid))
    canvas2.create_text(780,105,text=" Relative efficiency: "+str(round(((1/mingrid)/scale)*100)/100))
    approximate_positions(mingrid)
    draw()
    for n in range(0,len(nodes)):
        nodes[n].has_pytha_ur = nodes[n].has_pytha_ul = nodes[n].has_pytha_dl = nodes[n].has_pytha_dr = False #ul = upper left, dr = down right, etc
    find_pythas()
    display_pythas()
    drawxs()
    drawhinges()
    if selectednode != None:
        cursor = canvas2.create_oval(pyx(selectednode.x-selectednode.flaplength/mingrid), pyy(selectednode.y-selectednode.flaplength/mingrid),pyx(selectednode.x+selectednode.flaplength/mingrid), pyy(selectednode.y+selectednode.flaplength/mingrid),width = 3,outline="black")
    canvas2.create_rectangle(200,50,700,550,outline="black", width = 2)
    cpfile.append("1 -200 -200 -200 200")
    cpfile.append("1 -200 200 200 200")
    cpfile.append("1 200 200 200 -200")
    cpfile.append("1 200 -200 -200 -200")


def reset():
    global mingrid, selectednode
    canvas2.delete('all')
    global cpfile
    cpfile = ["1 -200 -200 -200 200", "1 -200 200 200 200", "1 200 200 200 -200", "1 200 -200 -200 -200"]
    canvas2.create_rectangle(200,50,700,550,fill='white',outline="black", width = 2)
    draw_grid(mingrid)
    canvas2.create_text(770,120,text=" Grid size: "+str(mingrid))
    canvas2.create_text(780,105,text=" Relative efficiency: "+str(round(((1/mingrid)/scale)*100)/100))
    selectednode = None
    draw_flaps()
    pythas(False) 
    
def key(event):
    #print ("pressed", repr(event.char))
    pass
selectednode = None
def moveflap(event):
    global selectednode
    if selectednode != None and (abs(event.x-selectednode.x)>30 or abs(event.y-selectednode.y)>30) and event.x<710 and event.x>190 and event.y<560 and event.y>40:
        selectednode.x = tmx(event.x)
        selectednode.y = tmy(event.y)
        refresh()
        #selectednode = None
            
cursor = canvas2.create_line(0,0,0,0) #buffer, to be deleted soon 
def selectnode(event):
    #frame.focus_set()
    global cursor, vertexx, vertexy, selectednode
    vertexx = event.x
    vertexy = event.y
    canvas2.delete(cursor)
    for n in range(0,len(nodes)):
        if abs(vertexx-pyx(approx_nodes[n].x))<20 and abs(vertexy-pyy(approx_nodes[n].y))<20:            
            selectednode = nodes[n]
            selectednode.flaplength = float(selectednode.flaplength)
            cursor = canvas2.create_oval(pyx(selectednode.x-selectednode.flaplength/mingrid), pyy(selectednode.y-selectednode.flaplength/mingrid),pyx(selectednode.x+selectednode.flaplength/mingrid), pyy(selectednode.y+selectednode.flaplength/mingrid),width = 3,outline="black")
            '''
        if abs(vertexx-pyx(approx_nodes[n].x))<5 and abs(vertexy-pyy(approx_nodes[n].y))<5 and nodes[n] == selectednode:
            canvas2.delete(cursor) #will deselect if you double click on the selected node 
            selectednode = None'''
                
def growflap():
    global cursor
    selectednode.flaplength = selectednode.flaplength +1
    for p in range(0,len(paths)):
        if paths[p].index in selectednode.paths:
            paths[p].tmlength +=1
    refresh()
    cursor = canvas2.create_oval(pyx(selectednode.x-selectednode.flaplength/mingrid), pyy(selectednode.y-selectednode.flaplength/mingrid),pyx(selectednode.x+selectednode.flaplength/mingrid), pyy(selectednode.y+selectednode.flaplength/mingrid),width = 3,outline="black")

def shrinkflap():
    global cursor
    selectednode.flaplength = selectednode.flaplength -1
    for p in range(0,len(paths)):
        if paths[p].index in selectednode.paths:
            paths[p].tmlength -=1
    refresh()
    cursor = canvas2.create_oval(pyx(selectednode.x-selectednode.flaplength/mingrid), pyy(selectednode.y-selectednode.flaplength/mingrid),pyx(selectednode.x+selectednode.flaplength/mingrid), pyy(selectednode.y+selectednode.flaplength/mingrid),width = 3,outline="black")

'''    recent = canvas2.create_line(vertexx,vertexy,event.x,event.y,fill="red",width=2)
    lines.append(recent)

'''
def click(event):
    selectnode(event)
    moveflap(event)
    '''if not selectnode(event):
        #moveflap(event)
        print('move')'''
    
canvas2.bind("<Key>", key)
canvas2.bind("<Button-1>", click)

enter = Button(canvas2,text="Grow selected flap",command=growflap)
enter.place(x=720,y=300)
enter = Button(canvas2,text="Shrink selected flap",command=shrinkflap)
enter.place(x=720,y=330)
#======================================

def gt(a,b):
    return (a+0.000001>b)
def ls(a,b):
    return(a+0.000001<b)
def eq(a,b):
    return(abs(a-b)<0.000001)
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
        if ls(self.bphypotenuse*mingrid,self.tmlength):
            return True
        else:
            return False
    def needs_pytha(self): #see if it needs a pytha
        if ls(self.bplength*mingrid,self.tmlength) and gt(self.bphypotenuse*mingrid,self.tmlength):
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
            
def pythas(exception):
    find_paths()
    #if find_pythas() and not exception: #don't raise if it's on the first go
    find_pythas()
    if selectednode != None:
        cursor = canvas2.create_oval(pyx(selectednode.x-selectednode.flaplength/mingrid), pyy(selectednode.y-selectednode.flaplength/mingrid),pyx(selectednode.x+selectednode.flaplength/mingrid), pyy(selectednode.y+selectednode.flaplength/mingrid),width = 3,outline="black")
    display_pythas()
    drawxs()

def find_pythas(): #will test if there are any that overlap
    faulty = False
    for x in range(0,len(paths)):
        paths[x].find_coordinates()
        if paths[x].is_too_tight():
            canvas2.create_line(pyx2(paths[x].x1),pyy(paths[x].y1),pyx2(paths[x].x2),pyy(paths[x].y2),fill='purple', width = 4)
            faulty = True
        #if paths[x].needs_pytha():
            #canvas2.create_line(pyx2(paths[x].x1),pyy(paths[x].y1),pyx2(paths[x].x2),pyy(paths[x].y2),fill='orange', width = 2)
    return faulty

def display_pythas():
    for p in range(0,len(paths)):
        if paths[p].needs_pytha():
            calculate_pytha(paths[p])
        

def calculate_pytha(path):
    '''for n in range(0,len(nodes)):
        nodes[n].has_pytha_ur = nodes[n].has_pytha_ul = nodes[n].has_pytha_dl = nodes[n].has_pytha_dr = False #ul = upper left, dr = down right, etc'''
    global x,y,flap1,flap2, flipper, bruh2 #it should be fine bc the pythas calculate one at a time
    x = abs(path.x1-path.x2)*mingrid
    y = abs(path.y1-path.y2)*mingrid #because the pytha program runs it in terms of grid units
    if (path.y2-path.y1)/(path.x2-path.x1) < 0:
        flipper = 1 #multiplying by 1 will not flip it
    else:
        flipper = -1  #because we took the abs of the coordinates, we don't know the orientation the pytha needs to be. we'll store this for later
    for n in range(0,len(nodes)):  #go get a flap length
        if nodes[n].index == path.node1:
            flap1 = float(nodes[n].flaplength)
            bruh1 = n #we're gonna cop this for later, need to mark these nodes
        if nodes[n].index == path.node2:
            bruh2 = n
            #maybe cop the flap length here too, for when we get rivers and pythas that aren't as tight as they could be    
    flap2 = path.tmlength - flap1
    global tkx,tky
    tkx = lambda coordinate: pyx(flipper*coordinate/mingrid+flipper*min(flipper*path.x2,flipper*path.x1)) #this will move the pytha into place, need to use the min
    tky = lambda coordinate: pyy(coordinate/mingrid+min(path.y1,path.y2))
    show_solution1()
    if nodes[bruh1].x > nodes[bruh2].x and nodes[bruh1].y > nodes[bruh2].y: 
        nodes[bruh1].has_pytha_dl = nodes[bruh2].has_pytha_ur = True
    if nodes[bruh1].x < nodes[bruh2].x and nodes[bruh1].y < nodes[bruh2].y:
        nodes[bruh1].has_pytha_ur = nodes[bruh2].has_pytha_dl = True
    if nodes[bruh1].x > nodes[bruh2].x and nodes[bruh1].y < nodes[bruh2].y:
        nodes[bruh1].has_pytha_ul = nodes[bruh2].has_pytha_dr = True        
    if nodes[bruh1].x < nodes[bruh2].x and nodes[bruh1].y > nodes[bruh2].y:
        nodes[bruh1].has_pytha_dr = nodes[bruh2].has_pytha_ul = True

        
#============================================== start pytha calculation section


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
    #canvas2.create_rectangle(tkx(bx),tky(by),tkx(a2x),tky(a2y),outline="purple",width=2)

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
    '''
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
        next_solution()'''
        
def tmx(py):
    return (py-200)/500
def tmy(py):
    return (550-py)/500
    
def cptmx(tk): #converts the custom tk into treemaker, then into cp
    return cp(tmx(tk))
def cptmy(tk):
    return cp(tmy(tk))

def pyx(tm): #converts tm coordinates into python (tk) coordinates
    return (float(tm)*500)+200 
def pyy(tm):
    return 550-(float(tm)*500)

def parallelogram():
    canvas2.create_line(tkx(a2x),tky(a2y),tkx(cx),tky(cy),fill="red",width=2)
    canvas2.create_line(tkx(a2x),tky(a2y),tkx(dx),tky(dy),fill="red",width=2)
    cpfile.append("2 "+str(cptmx(tkx(a2x)))+" "+str(cptmy(tky(a2y)))+" "+str(cptmx(tkx(cx)))+' '+str(cptmy(tky(cy))))
    cpfile.append("2 "+str(cptmx(tkx(a2x)))+" "+str(cptmy(tky(a2y)))+" "+str(cptmx(tkx(dx)))+' '+str(cptmy(tky(dy))))

    global b2x,b2y
    b2x = dx + cx-a2x
    b2y = dy + cy-a2y
    canvas2.create_line(tkx(b2x),tky(b2y),tkx(dx),tky(dy),fill="red",width=2)
    canvas2.create_line(tkx(b2x),tky(b2y),tkx(cx),tky(cy),fill="red",width=2)
    cpfile.append("2 "+str(cptmx(tkx(b2x)))+" "+str(cptmy(tky(b2y)))+" "+str(cptmx(tkx(cx)))+' '+str(cptmy(tky(cy))))
    cpfile.append("2 "+str(cptmx(tkx(b2x)))+" "+str(cptmy(tky(b2y)))+" "+str(cptmx(tkx(dx)))+' '+str(cptmy(tky(dy))))



def arms():
    #canvas2.create_line(tkx(bx),tky(by),tkx(bx-5),tky(by-5),fill="red",width=2)
    global ay, ax
    flap2 = float(nodes[bruh2].flaplength)
    ay +=(ax-flap2)
    ax = flap2
    canvas2.create_line(tkx(ax),tky(ay),tkx(a2x),tky(a2y),fill="red",width=2)
    cpfile.append("2 "+str(cptmx(tkx(ax)))+" "+str(cptmy(tky(ay)))+" "+str(cptmx(tkx(a2x)))+' '+str(cptmy(tky(a2y))))

    #canvas2.create_line(tkx(ax),tky(ay),tkx(ax+5),tky(ay+5),fill="red",width=2)  
def b():
    canvas2.create_line(tkx(b2x),tky(b2y),tkx(bx),tky(by),fill="red",width=2)
    cpfile.append("2 "+str(cptmx(tkx(b2x)))+" "+str(cptmy(tky(b2y)))+" "+str(cptmx(tkx(bx)))+' '+str(cptmy(tky(by))))

def ridge():
    canvas2.create_line(tkx(0),tky(y),tkx(dx),tky(dy),fill="red",width=2)
    canvas2.create_line(tkx(x),tky(0),tkx(cx),tky(cy),fill="red",width=2)
    cpfile.append("2 "+str(cptmx(tkx(0)))+" "+str(cptmy(tky(y)))+" "+str(cptmx(tkx(dx)))+' '+str(cptmy(tky(dy))))
    cpfile.append("2 "+str(cptmx(tkx(x)))+" "+str(cptmy(tky(0)))+" "+str(cptmx(tkx(cx)))+' '+str(cptmy(tky(cy))))


def hinges():
    global ey, ex, hx, hy
    canvas2.create_line(tkx(x),tky(flap1),tkx(ax),tky(ay),fill="blue",width=2)
    canvas2.create_line(tkx(x-flap1),tky(0),tkx(bx),tky(by),fill="blue",width=2)
    if ax >= a2x:
        ey = ay
        ex = a2x+ ((ay-a2y)/(cy-a2y))*(cx-a2x)
    if ax <= a2x:
        ex = ax
        ey = a2y+ ((a2x-ax)/(a2x-dx))*(dy-a2y)
        
    if bx <= b2x:
        fy = by
        fx = b2x- ((by-b2y)/(dy-b2y))*(b2x-dx)
    if bx >= b2x:
        fx = bx
        fy = b2y- ((b2x-bx)/(b2x-cx))*(b2y-cy)
    
    canvas2.create_line(tkx(ex),tky(ey),tkx(ax),tky(ay),fill="blue",width=2)
    canvas2.create_line(tkx(fx),tky(fy),tkx(bx),tky(by),fill="blue",width=2)
    canvas2.create_line(tkx(fx),tky(fy),tkx(ex),tky(ey),fill="blue",width=2)

def hinges2(): #after arms shifts point a
    global gy, gx, hx, hy
    flap2 = float(nodes[bruh2].flaplength)
    canvas2.create_line(tkx(flap2),tky(y),tkx(ax),tky(ay),fill="blue",width=2)
    #cpfile.append("3 "+str(cptmx(tkx(flap2)))+" "+str(cptmy(y))+" "+str(cptmx(ax))+' '+str(cptmy(ay)))

    if ax >= a2x:
        gy = ay
        gx = a2x+ ((ay-a2y)/(cy-a2y))*(cx-a2x)
    if ax <= a2x:
        gx = ax
        gy = a2y+ ((a2x-ax)/(a2x-dx))*(dy-a2y)
        
    if bx<=b2x:
        hy = y-flap2
        hx = b2x- (((y-b2y)-(y-flap2))/(dy-b2y))*(b2x-dx)
    if bx>b2x: #if b is in front of b2, find h by using the reflection over the b-b2 line
        iy = y-flap2
        ix = bx-( iy-by)
        hy = by+ (b2y-by)*( (cx-ix)/(cx-b2x))
        hx = ix
        canvas2.create_line(tkx(0),tky(y-flap2),tkx(ix),tky(iy),fill = 'blue', width = 2)
        canvas2.create_line(tkx(ix),tky(iy),tkx(hx),tky(hy),fill='blue', width = 2)
        #cpfile.append("3 "+str(cptmx(tkx(ix)))+" "+str(cptmy(iy))+" "+str(cptmx(hx))+' '+str(cptmy(hy)))
        #cpfile.append("3 "+str(cptmx(tkx(ix)))+" "+str(cptmy(iy))+" "+str(cptmx(0))+' '+str(cptmy(y-flap2)))


    
    canvas2.create_line(tkx(gx),tky(gy),tkx(ax),tky(ay),fill="blue",width=2)
    #canvas2.create_line(tkx(hx),tky(hy),tkx(bx),tky(by),fill="blue",width=2)
    canvas2.create_line(tkx(hx),tky(hy),tkx(gx),tky(gy),fill="blue",width=2)

    #canvas2.create_line(tkx(0),tky(y-flap2),tkx(bx-((y-flap2)-b2y)),tky(y-flap2),fill="blue",width=2)  
    canvas2.create_line(tkx(0),tky(y-flap2),tkx(hx),tky(y-flap2),fill="blue",width=2)

    
def show_solution1():
    overlap()
    rotate()
    cd1()
    parallelogram()
    b()
    ridge()
    hinges()
    arms()
    hinges2()
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
    #canvas2.delete("all")
    canvas2.create_rectangle(0,00,600,600,fill="white",outline="white")

    #draw_grid(x,y,grid)
    #draw_circles(x,y,grid,flap1,flap2)
    #draw_boxes(x,y,grid,flap1,flap2)
    #draw_axis(x,y,grid)

    rotate()
    cd1()
    parallelogram()
    b()
    hinges()
    arms()
    hinges2()
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
enter = Button(canvas2,text="Decrease grid size",command=lowergrid)
enter.place(x=720,y=160)   #maybe an entry box for the grid size?
enter = Button(canvas2,text="Reset layout",command=reset)
enter.place(x=720,y=220)

enter = Button(canvas2,text="Draw ridges",command=drawxs)
#enter.place(x=720,y=300)


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


'''you can test for rivers by checking what edges are on the paths. can also just take path length and subtract the flaps'''
