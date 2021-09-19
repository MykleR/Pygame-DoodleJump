# -*- coding: utf-8 -*-
"""
	CopyLeft 2021 Michael Rouves

	This file is part of Pygame-DoodleJump.
	Pygame-DoodleJump is free software: you can redistribute it and/or modify
	it under the terms of the GNU Affero General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	Pygame-DoodleJump is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
	GNU Affero General Public License for more details.

	You should have received a copy of the GNU Affero General Public License
	along with Pygame-DoodleJump. If not, see <https://www.gnu.org/licenses/>.
"""


from pygame import Surface,Rect
from camera import Camera



class Sprite:
	"""
	A class to represent a sprite.
	
	Used for pygame displaying.
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

	# Public getters for _image & __color so they remain private
	@property
	def image(self) -> Surface:
		return self._image
	@property
	def color(self) -> tuple:
		return self.__color

	@color.setter
	def color(self, new:tuple) -> None:
		" Called when Sprite.__setattr__('color',x)."
		assert isinstance(new,tuple) and len(new)==3,"Value is not a color"
		self.__color = new
		#update image surface
		self._image.fill(self.color)
	

	def draw(self, surface:Surface) -> None:
		""" Render method,Should be called every frame after update.
		:param surface pygame.Surface: the surface to draw on.
		"""
		# If camera instancied: calculate render positon
		if Camera.instance:
			self.camera_rect = Camera.instance.apply(self)
			surface.blit(self._image,self.camera_rect)
		else:
			surface.blit(self._image,self.rect)