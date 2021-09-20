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
import settings as config



#return True with a chance of: P(X=True)=1/x
chance = lambda x: not randint(0,x)


class Bonus(Sprite):
	"""
	A class to represent a bonus
	Inherits the Sprite class.
	"""

	WIDTH = 15
	HEIGHT = 15

	def __init__(self, parent:Sprite,color=config.GRAY,
			force=config.PLAYER_BONUS_JUMPFORCE):

		self.parent = parent
		super().__init__(*self._get_inital_pos(),
			Bonus.WIDTH, Bonus.HEIGHT, color)
		self.force = force
	
	def _get_inital_pos(self):
		x = self.parent.rect.centerx - Bonus.WIDTH//2
		y = self.parent.rect.y - Bonus.HEIGHT
		return x,y





class Platform(Sprite):
	"""
	A class to represent a platform.

	Should only be instantiated by a Level instance.
	Can have a bonus spring or broke on player jump.
	Inherits the Sprite class.
	"""
	# (Overriding inherited constructor: Sprite.__init__)
	def __init__(self, x:int, y:int, width:int, height:int,
			initial_bonus=False,breakable=False):

		color = config.PLATFORM_COLOR
		if breakable:color = config.PLATFORM_COLOR_LIGHT
		super().__init__(x,y,width,height,color)

		self.breakable = breakable
		self.__level = Level.instance
		self.__bonus = None
		if initial_bonus:
			self.add_bonus(Bonus)

	# Public getter for __bonus so it remains private
	@property
	def bonus(self):return self.__bonus

	def add_bonus(self,bonus_type:type) -> None:
		""" Safely adds a bonus to the platform.
		:param bonus_type type: the type of bonus to add.
		"""
		assert issubclass(bonus_type,Bonus), "Not a valid bonus type !"
		if not self.__bonus and not self.breakable:
			self.__bonus = bonus_type(self)
	
	def remove_bonus(self) -> None:
		" Safely removes platform's bonus."
		self.__bonus = None

	def onCollide(self) -> None:
		" Called in update if collision with player (safe to overrided)."
		if self.breakable:
			self.__level.remove_platform(self)
		
	# ( Overriding inheritance: Sprite.draw() )
	def draw(self, surface:Surface) -> None:
		""" Like Sprite.draw().
		Also draws the platform's bonus if it has one.
		:param surface pygame.Surface: the surface to draw on.
		"""
		# check if out of screen: should be deleted
		super().draw(surface)
		if self.__bonus:
			self.__bonus.draw(surface)
		if self.camera_rect.y+self.rect.height>config.YWIN:
			self.__level.remove_platform(self)





class Level(Singleton):
	"""
	A class to represent the level.
	
	used to manage updates/generation of platforms.
	Can be access via Singleton: Level.instance.
	(Check Singleton design pattern for more info)
	"""
	
	# constructor called on new instance: Level()
	def __init__(self):
		self.platform_size = config.PLATFORM_SIZE
		self.max_platforms = config.MAX_PLATFORM_NUMBER
		self.distance_min = min(config.PLATFORM_DISTANCE_GAP)
		self.distance_max = max(config.PLATFORM_DISTANCE_GAP)

		self.bonus_platform_chance = config.BONUS_SPAWN_CHANCE
		self.breakable_platform_chance = config.BREAKABLE_PLATFORM_CHANCE

		self.__platforms = []
		self.__to_remove = []

		self.__base_platform = Platform(
			config.HALF_XWIN - self.platform_size[0]//2,# X POS
			config.HALF_YWIN + config.YWIN/3, #           Y POS
			*self.platform_size)#                         SIZE
	

	# Public getter for __platforms so it remains private
	@property
	def platforms(self) -> list:
		return self.__platforms


	async def _generation(self) -> None:
		" Asynchronous management of platforms generation."
		# Check how many platform we need to generate
		nb_to_generate = self.max_platforms - len(self.__platforms)
		for _ in range(nb_to_generate):
			self.create_platform()
		

	def create_platform(self) -> None:
		" Create the first platform or a new one."
		if self.__platforms:
			# Generate a new random platform :
			# x position along screen width
			# y position starting from last platform y pos +random offset
			offset = randint(self.distance_min,self.distance_max)
			self.__platforms.append(Platform(
				randint(0,config.XWIN-self.platform_size[0]),#       X POS
				self.__platforms[-1].rect.y-offset,#                 Y POS
				*self.platform_size, #                               SIZE
				initial_bonus=chance(self.bonus_platform_chance),# HAS A Bonus
				breakable=chance(self.breakable_platform_chance)))#  IS BREAKABLE
		else:
			# (just in case) no platform: add the base one
			self.__platforms.append(self.__base_platform)


	def remove_platform(self,plt:Platform) -> bool:
		""" Removes a platform safely.
		:param plt Platform: the platform to remove
		:return bool: returns true if platoform successfully removed
		"""
		if plt in self.__platforms:
			self.__to_remove.append(plt)
			return True
		return False


	def reset(self) -> None:
		" Called only when game restarts (after player death)."
		self.__platforms = [self.__base_platform]


	def update(self) -> None:
		" Should be called each frame in main game loop for generation."
		for platform in self.__to_remove:
			if platform in self.__platforms:
				self.__platforms.remove(platform)
		self.__to_remove = []
		asyncio.run(self._generation())


	def draw(self,surface:Surface) -> None:
		""" Called each frame in main loop, draws each platform
		:param surface pygame.Surface: the surface to draw on.
		"""
		for platform in self.__platforms:
			platform.draw(surface)