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


from random import randint
from pygame import Surface
import asyncio

from singleton import Singleton
from sprite import Sprite
from settings import *



#return True with a chance of: P(X=True)=1/x
chance = lambda x: not randint(0,x)


class Platform(Sprite):
	"""
		A class to represent a platform
		Spawned by the Level
		Can have a bonus spring or broke on player jump
	"""
	# (Overriding inheritance Sprite.__init__ constructor)
	def __init__(self,*args,spring=False,breakable=False):
		color = PLATFORM_COLOR_LIGHT if breakable else PLATFORM_COLOR
		super().__init__(*args,color)

		self.level = Level.instance
		self.breakable = breakable
		self.spring = None
		if spring and not self.breakable:
			pos = (self.rect.centerx-7,
				self.rect.y-15)
			self.spring = Sprite(*pos,15,15,GRAY)

	def onCollide(self):
		" Called in update if collision with player (safe to overrided)"
		if self.breakable:
			self.level.remove_platform(self)
		
	def draw(self, surface:Surface) -> None:
		" Called by Level in Level.update to draw sprite each frame"
		# check if out of screen: should be deleted
		super().draw(surface)
		if self.spring:self.spring.draw(surface)
		if self.camera_rect.y+self.rect.height>YWIN:
			self.level.remove_platform(self)




class Level(Singleton):
	"""
		A class to represent the level
		used to manage updates/generation of platforms
		Can be access via Singleton: Level.instance
		(Check Singleton design pattern for more info)
	"""
	# constructor called on new instance: Level()
	def __init__(self):
		self.platform_size = (PLATFORM_WIDTH,PLATFORM_HEIGHT)
		self.max_platforms = PLATFORM_NUMBER
		self.distance_min = 50
		self.distance_max = 210

		self.spring_platform_chance = 10
		self.breakable_platform_chance = 12

		self.__platforms = []
		self.__to_remove = []

		self.__base_platform = Platform(
			HALF_XWIN - self.platform_size[0]//2,# X POS
			HALF_YWIN + YWIN/3, #                  Y POS
			*self.platform_size)#                  SIZE
	

	# A public getter for __platforms so it remains private
	@property
	def platforms(self) -> list:
		return self.__platforms


	async def _generation(self) -> None:
		# Check how many platform we need to generate
		nb_to_generate = self.max_platforms - len(self.__platforms)
		for _ in range(nb_to_generate):
			self.create_platform()
		

	def create_platform(self) -> None:
		" Create the first platform or a new one"
		if self.__platforms:
			# Generate a new random platform :
			# x position along screen width
			# y position starting from last platform y pos +random offset
			offset = randint(self.distance_min,self.distance_max)

			self.__platforms.append(Platform(
				randint(0,XWIN-self.platform_size[0]),#             X POS
				self.__platforms[-1].rect.y-offset,#                 Y POS
				*self.platform_size, #                              SIZE
				spring=chance(self.spring_platform_chance),#        HAS A SPRING
				breakable=chance(self.breakable_platform_chance)))# IS BREAKABLE
		else:
			# (just in case) no platform: add the base one
			self.__platforms.append(self.__base_platform)


	def remove_platform(self,plt:Platform) -> bool:
		" A method to remove a platform safely return true if success"
		if plt in self.__platforms:
			self.__to_remove.append(plt)
			return True
		return False


	def reset(self) -> None:
		" Called only when lvl restarts (after player death)"
		self.__platforms = [self.__base_platform]


	def update(self) -> None:
		" Called each frame in main loop for generation "
		for platform in self.__to_remove:
			if platform in self.__platforms:
				self.__platforms.remove(platform)
		self.__to_remove = []
		asyncio.run(self._generation())


	def draw(self,surface:Surface) -> None:
		" Called in main loop to draw each world platform"
		for platform in self.__platforms:
			platform.draw(surface)