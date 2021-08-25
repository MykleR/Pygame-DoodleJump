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

from singleton import Singleton
from sprite import Sprite
from player import Player
from settings import *


#return True with a chance of P(True)=1/x
chance = lambda x: not randint(0,x)


class Platform(Sprite):
	"""
		A class to represent a platform
		Spawned by the Level
		Can have a bonus spring or broke on player jump
	"""
	# (Overriding Sprite.__init__ constructor)
	def __init__(self,level,*args,spring=False,breakable=False):
		color = PLATFORM_COLOR_LIGHT if breakable else PLATFORM_COLOR
		super().__init__(*args,color)

		self.level = level
		self.breakable = breakable
		self.spring = None
		if spring and not self.breakable:
			pos = (self.rect.centerx-7,
				self.rect.y-15)
			self.spring = Sprite(*pos,15,15,GRAY)

	def onCollide(self,player:Player):
		player.jump()
		if self.breakable:
			self.level._platforms.remove(self)

	def draw(self, surface:Surface) -> None:
		super().draw(surface)
		if self.spring:self.spring.draw(surface)




class Level(Singleton):
	"""
		A class to represent the level
		used to manage updates/generation of platforms
		Can be access via Singleton: Level.instance
	"""
	# constructor
	def __init__(self):
		self.platform_width = PLATFORM_WIDTH
		self.platform_height = PLATFORM_HEIGHT
		self.max_platforms = PLATFORM_NUMBER
		self.distance_min = 50
		self.distance_max = 210

		self.spring_platform_chance = 10
		self.breakable_platform_chance = 12

		self._platforms = []
		self.__base_platform = Platform(self,
			XWIN/2-self.platform_width//2,
			YWIN/2+YWIN/3,self.platform_width,
			self.platform_height)
	

	def _generate(self) -> None:
		" Create a the first or a new platform based on last one"
		if self._platforms:
			#Add a new platform sprite:
			#random x position along screen width
			#random y position starting from last platform position
			self._platforms.append(Platform(self,
				randint(0,XWIN-self.platform_width),
				self._platforms[-1].rect.y-randint(self.distance_min,self.distance_max),
				self.platform_width,
				self.platform_height,
				spring=chance(self.spring_platform_chance),
				breakable=chance(self.breakable_platform_chance)))
		else:#no platform so add the base one
			self._platforms.append(self.__base_platform)


	def reset(self) -> None:
		" Called only when lvl restarts (after player death)"
		self._platforms = []
		self._generate()


	def update(self,player:Player) -> None:
		" Called each frame in main loop for generation and collision "
		for platform in self._platforms:
			#check if platform out of screen: should be deleted
			if platform.camera_rect.y+platform.rect.height>YWIN:
				self._platforms.remove(platform)
				continue
			#check collisions with player
			if player.collide(platform):
				platform.onCollide(player)
			#check collisions with platform's spring bonus
			if platform.spring and player.collide(platform.spring):
				player.jump(50)
		
		#check if ther is room for a new platform and generate it
		if len(self._platforms)<self.max_platforms:
			self._generate()
	

	def draw(self,surface:Surface) -> None:
		" Called in main loop to draw each world platform"
		for platform in self._platforms:
			platform.draw(surface)