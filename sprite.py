from pygame import Surface,Rect
from camera import Camera
from settings import *


class Sprite:
	"""
		A class to represent a sprite.
		Used for displaying.
		Image generated with given color and size.
	"""
	# default constructor (must be called if overrided by inheritance)
	def __init__(self,x:int,y:int,w:int,h:int,color:tuple):
		self.__color = color
		self._image = Surface((w,h))
		self._image.fill(self.color)
		self._image = self._image.convert()
		self.rect = Rect(x,y,w,h)
		self.camera_rect = self.rect.copy()

	@property
	def image(self) -> Surface:
		return self._image
	@property
	def color(self) -> tuple:
		return self.__color

	@color.setter
	def color(self, new:tuple) -> None:
		" Called when Sprite.__setattr__('color',x)"
		assert isinstance(new,tuple) and len(new)==3,"Value is not a color"
		self.__color = new
		#update image surface
		self._image.fill(self.color)
	
    
	def draw(self, surface:Surface) -> None:
		" Render method,Should be called every frame after update."
		# If camera instancied: calculate render positon
		if Camera.instance:
			self.camera_rect = Camera.instance.apply(self)
			surface.blit(self._image,self.camera_rect)
		else:
			surface.blit(self._image,self.rect)