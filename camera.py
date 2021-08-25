from pygame import Rect
from pygame.sprite import Sprite

from singleton import Singleton
from settings import *


class Camera(Singleton):
	"""
		A class to represent the only camera
		Manages level position scrolling
		Can be access via Singleton: Camera.instance
	"""
	def __init__(self, lerp=5,width=XWIN, height=YWIN):
		self.state = Rect(0, 0, width, height)
		self.lerp = lerp
		self.center = height//2
		self.maxheight = self.center

	def reset(self) -> None:
		" Called only when lvl restarts (after player death)"
		self.state.y = 0
		self.maxheight = self.center
	
	def apply_rect(self,rect:Rect) -> Rect:
		" Move given rect relative to camera position"
		return rect.move((0,-self.state.topleft[1]))
	
	def apply(self, target:Sprite) -> Rect:
		" Return new target render position based on current camera position"
		return self.apply_rect(target.rect)
	
	def update(self, target:Rect) -> None:
		" Called each frame to scroll up to maxheight reached by player."
		#updating maxheight
		if(target.y<self.maxheight):
			self.lastheight = self.maxheight
			self.maxheight = target.y
		#calculate scrolling speed required
		speed = ((self.state.y+self.center)-self.maxheight)/self.lerp
		self.state.y-=speed

