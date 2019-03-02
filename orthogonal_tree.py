import cv2
import numpy as np
class OrthogonalTree:
	ZOOM_LEVEL=5
	NODE_WIDTH=20
	NODE_HEIGHT=20
	NODE_PAD=4
	NODE_IMG=np.ones((512,512,3), np.uint8)*255
	NODE_B_WIDTH=1
	NODE_COLOR=(100,100,100)
	NODE_B_COLOR=(0,0,0)
	LINE_COLOR=(0,0,0)
	LINE_WIDTH=1
	def __init__(self,height,start,end,left=None,right=None,background=np.ones((512,512,3), np.uint8)*255,zoom=1):
		if self.ZOOM_LEVEL>1:
			self.NODE_WIDTH*=self.ZOOM_LEVEL
			self.NODE_HEIGHT*=self.ZOOM_LEVEL
			self.NODE_PAD*=self.ZOOM_LEVEL
			height*=self.ZOOM_LEVEL
			start*=self.ZOOM_LEVEL
			end*=self.ZOOM_LEVEL
		if start == end:
			if left!=None and right!=None and left!=right:
				raise Exception('Not wide enough to have two children')
			if left!=None and left==right:
				right=None
		self.height=height
		self.s=start
		self.t=end
		self.left=left
		self.right=right
		self.NODE_IMG=background
	def set_background(self,background):
		self.NODE_IMG=background
	def draw(self):
		top_left=(self.s-self.NODE_PAD,self.height-self.NODE_PAD)
		bot_right=(self.t+self.NODE_PAD,self.height+self.NODE_PAD)
		if self.left!=None:
			cv2.line(self.NODE_IMG,(self.s,self.height),(self.s,self.left.get_height()),self.LINE_COLOR,self.LINE_WIDTH)
			self.left.set_background(self.NODE_IMG)
			self.left.draw()
		if self.right!=None:
			cv2.line(self.NODE_IMG,(self.t,self.height),(self.t,self.right.get_height()),self.LINE_COLOR,self.LINE_WIDTH)
			self.right.set_background(self.NODE_IMG)
			self.right.draw()
		cv2.rectangle(self.NODE_IMG,top_left,bot_right,self.NODE_COLOR,cv2.FILLED)
		cv2.rectangle(self.NODE_IMG,top_left,bot_right,self.NODE_B_COLOR,self.NODE_B_WIDTH)
	def get_height(self):
		return self.height
	def get_image(self):
		self.draw()
		return self.NODE_IMG
def build_tree(tree):
	if 'root' in tree:
		height,s,t=tree['root']
		right=None
		if 'right' in tree:
			right=build_tree(tree['right'])
		left=None
		if 'left' in tree:
			left=build_tree(tree['left'])
		return OrthogonalTree(height,s,t,left=left,right=right)
sample_tree={'root':(10,20,40),
			'left':{
				'root':(50,20,30),
				'left':{
					'root':(70,20,20)},
				'right':{
					'root':(60,30,30)}
				},
			'right':{
				'root':(30,40,50)}
			}

#tree=OrthogonalTree(10,20,40,left=OrthogonalTree(50,20,30),right=OrthogonalTree(60,40,50))
tree=build_tree(sample_tree)
cv2.imshow('Test',tree.get_image())
cv2.waitKey(0)
cv2.destroyAllWindows()