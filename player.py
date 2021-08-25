from math import copysign
from pygame.math import Vector2
from pygame.locals import KEYDOWN,KEYUP,K_LEFT,K_RIGHT
from pygame.sprite import collide_rect
from pygame.event import Event

from sprite import Sprite
from settings import *


#Return the sign of a number: getsign(-5)-> -1
getsign = lambda x : copysign(1, x)

class Player(Sprite):
	"""
		A class to represent the player
		Manages player's physics (movement...)
	"""
	# (Overriding Sprite.__init__ constructor)
	def __init__(self,*args):
		#calling default Sprite constructor
		super().__init__(*args)
		self.__startrect = self.rect.copy()
		self.__maxvelocity = Vector2(PLAYER_MAX_SPEED,100)
		self.__startspeed = 1.5

		self._velocity = Vector2()
		self._input = 0
		self._jumpforce = PLAYER_JUMPFORCE

		self.gravity = GRAVITY
		self.accel = .5
		self.deccel = .6
		self.dead = False
	

	def _fix_velocity(self) -> None:
		" Called in Player.update(), set player's velocity between max/min"
		self._velocity.y = min(self._velocity.y,self.__maxvelocity.y)
		self._velocity.y = round(max(self._velocity.y,-self.__maxvelocity.y),2)
		self._velocity.x = min(self._velocity.x,self.__maxvelocity.x)
		self._velocity.x = round(max(self._velocity.x,-self.__maxvelocity.x),2)


	def reset(self) -> None:
		" Called only when lvl restarts (after player death)"
		self._velocity = Vector2()
		self.rect = self.__startrect.copy()
		self.camera_rect = self.__startrect.copy()
		self.dead = False


	def handle_event(self,event:Event) -> None:
		" Called in main loop foreach user input event"
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


	def collide(self,platform:Sprite) -> bool:
		" Called by lvl foreach platform to check for y-axis collisions"
		if collide_rect(self,platform):
			#if falling and colliding: isGrounded should jump
			if self._velocity.y > .5:
				self.rect.bottom = platform.rect.top
				return True
		return False


	def update(self) -> None:
		" Called each frame for position and velocity updates"
		#Check if player out of screen: should be dead
		if self.camera_rect.y>YWIN*2:
			self.dead = True
			return
		#Velocity update (apply gravity, input acceleration)
		self._velocity.y += self.gravity
		if self._input:
			self._velocity.x += self._input*self.accel
		elif self._velocity.x:
			self._velocity.x -= getsign(self._velocity.x)*self.deccel
			self._velocity.x = round(self._velocity.x)
		self._fix_velocity()

		#Position Update (block x-axis to get out of screen)
		self.rect.x = (self.rect.x+self._velocity.x)%(XWIN-self.rect.width)
		self.rect.y += self._velocity.y