import cv2
import numpy as np
default={"CELL_WIDTH":50, "CELL_HEIGHT":5,
"CELL_H_PAD":0.4, "CELL_V_PAD":0.8, 
"NODE_B_WIDTH":1, "NODE_COLOR":(100,100,100),"NODE_B_COLOR":(0,0,0),
"LINE_COLOR":(0,0,0),"LINE_WIDTH":3}
CELL_WIDTH=20
CELL_HEIGHT=4
CELL_H_PAD=0.4
CELL_V_PAD=0.6
OFFSET_H=int(CELL_WIDTH*CELL_H_PAD*2)
OFFSET_V=int(CELL_HEIGHT*CELL_V_PAD*2)
NODE_B_WIDTH=1
NODE_COLOR=(100,100,100)
NODE_B_COLOR=(0,0,0)
LINE_COLOR=(0,0,0)
LINE_WIDTH=1
def arr(A):
	return np.array(A)
def make_canvas(w,h):
	return np.ones((h*CELL_HEIGHT+2*OFFSET_V,w*CELL_WIDTH+2*OFFSET_H,3), np.uint8)*255
def rescale(coor):
	if type(coor)==tuple:
		return (rescaleH(coor[0]),rescaleV(coor[1]))
	if type(coor)==np.ndarray:
		return (rescaleH(coor[0]),rescaleV(coor[1]))
def rescaleH(coor):
	t=int(coor*1.*CELL_WIDTH+OFFSET_H)
	return int(t)
def rescaleV(coor):
	t=int(coor*1.*CELL_HEIGHT+OFFSET_V)
	return int(t)
def add_padding(top_left,bot_right):
	top_left=arr(top_left)-arr([CELL_H_PAD,CELL_V_PAD])
	bot_right=arr(bot_right)+arr([CELL_H_PAD,CELL_V_PAD])
	return rescale(top_left),rescale(bot_right)
def make_image(root,IMG=None):
	if (IMG is None):
		w,h=root.dims#juan?
		IMG=make_canvas(w,h)
	top_left=(root.start,root.height)
	bot_right=(root.end,root.height)

	top_left,bot_right=add_padding(top_left,bot_right)
	for c in root.children:
		start=(c.incoming,root.height)
		end=(c.incoming,c.height)
		start,end = rescale(start),rescale(end)

		cv2.line(IMG,start,end,LINE_COLOR,LINE_WIDTH)
		make_image(c,IMG)
	cv2.rectangle(IMG,top_left,bot_right,NODE_COLOR,cv2.FILLED)
	cv2.rectangle(IMG,top_left,bot_right,NODE_B_COLOR,NODE_B_WIDTH)
	return IMG
def save_img(root,name):
	img=make_image(root)
	cv2.imwrite(str(name)+'.png',img)
def show(root):
	img=make_image(root)
	cv2.imshow("Tree",img)
	cv2.waitKey(0)
	cv2.destroyAllWindows()