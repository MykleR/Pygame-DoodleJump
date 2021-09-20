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


from math import copysign
from pygame.math import Vector2
from pygame.locals import KEYDOWN,KEYUP,K_LEFT,K_RIGHT
from pygame.sprite import collide_rect
from pygame.event import Event

from singleton import Singleton
from sprite import Sprite
from level import Level
import settings as config



#Return the sign of a number: getsign(-5)-> -1
getsign = lambda x : copysign(1, x)

class Player(Sprite, Singleton):
	"""
	A class to represent the player.
	
	Manages player's input,physics (movement...).
	Can be access via Singleton: Player.instance.
	(Check Singleton design pattern for more info).
	"""
	# (Overriding Sprite.__init__ constructor)
	def __init__(self,*args):
		#calling default Sprite constructor
		Sprite.__init__(self,*args)
		self.__startrect = self.rect.copy()
		self.__maxvelocity = Vector2(config.PLAYER_MAX_SPEED,100)
		self.__startspeed = 1.5

		self._velocity = Vector2()
		self._input = 0
		self._jumpforce = config.PLAYER_JUMPFORCE
		self._bonus_jumpforce = config.PLAYER_BONUS_JUMPFORCE

		self.gravity = config.GRAVITY
		self.accel = .5
		self.deccel = .6
		self.dead = False
	

	def _fix_velocity(self) -> None:
		""" Set player's velocity between max/min.
		Should be called in Player.update().
		"""
		self._velocity.y = min(self._velocity.y,self.__maxvelocity.y)
		self._velocity.y = round(max(self._velocity.y,-self.__maxvelocity.y),2)
		self._velocity.x = min(self._velocity.x,self.__maxvelocity.x)
		self._velocity.x = round(max(self._velocity.x,-self.__maxvelocity.x),2)


	def reset(self) -> None:
		" Called only when game restarts (after player death)."
		self._velocity = Vector2()
		self.rect = self.__startrect.copy()
		self.camera_rect = self.__startrect.copy()
		self.dead = False


	def handle_event(self,event:Event) -> None:
		""" Called in main loop foreach user input event.
		:param event pygame.Event: user input event
		"""
		# Check if start moving
		if event.type == KEYDOWN:
			# Moves player only on x-axis (left/right)
			if event.key == K_LEFT:
				self._velocity.x=-self.__startspeed
				self._input = -1
			elif event.key == K_RIGHT:
				self._velocity.x=self.__startspeed
				self._input = 1
		#Check if stop moving
		elif event.type == KEYUP:
			if (event.key== K_LEFT and self._input==-1) or (
					event.key==K_RIGHT and self._input==1):
				self._input = 0
	

	def jump(self,force:float=None) -> None:
		if not force:force = self._jumpforce
		self._velocity.y = -force


	def onCollide(self, obj:Sprite) -> None:
		self.rect.bottom = obj.rect.top
		self.jump()
	

	def collisions(self) -> None:
		""" Checks for collisions with level.
		Should be called in Player.update().
		"""
		lvl = Level.instance
		if not lvl: return
		for platform in lvl.platforms:
			# check falling and colliding <=> isGrounded ?
			if self._velocity.y > .5:
				# check collisions with platform's spring bonus
				if platform.bonus and collide_rect(self,platform.bonus):
					self.onCollide(platform.bonus)
					self.jump(platform.bonus.force)

				# check collisions with platform
				if collide_rect(self,platform):
					self.onCollide(platform)
					platform.onCollide()


	def update(self) -> None:
		""" For position and velocity updates.
		Should be called each frame.
		"""
		#Check if player out of screen: should be dead
		if self.camera_rect.y>config.YWIN*2:
			self.dead = True
			return
		#Velocity update (apply gravity, input acceleration)
		self._velocity.y += self.gravity
		if self._input: # accelerate
			self._velocity.x += self._input*self.accel
		elif self._velocity.x: # deccelerate
			self._velocity.x -= getsign(self._velocity.x)*self.deccel
			self._velocity.x = round(self._velocity.x)
		self._fix_velocity()

		#Position Update (prevent x-axis to be out of screen)
		self.rect.x = (self.rect.x+self._velocity.x)%(config.XWIN-self.rect.width)
		self.rect.y += self._velocity.y

		self.collisions()