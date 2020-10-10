import pygame,sys, os, random
from pygame.locals import *

pygame.init()


#CONST
COLORS = [
	pygame.Color(255,255,255), # white 00
	pygame.Color(0,0,0), # black 01
	pygame.Color(255,0,0), # red 02
	pygame.Color(0,255,0), # green 03
	pygame.Color(0,0,255), # blue 04
	pygame.Color(110,110,110), # grey 05
	pygame.Color(182,210,45), # Doddle 06
	pygame.Color(78,180,255), # blue Sky 07
	pygame.Color(50,50,50), # dark grey 08
	pygame.Color(120,120,120), # light grey 09
	pygame.Color(131,252,107), # light green 10
	pygame.Color(87,189,68), # dark green 11
	pygame.Color(175,230,165), # breackable platform 12
	pygame.Color(248,248,248), # blanc casser 13
]
FONTS = [
	pygame.font.Font(None, 32),
	pygame.font.Font(None, 64),
]
FPS = 60
XWIN, YWIN = 640,700
HALF_WIDTH = int(XWIN/2)
HALF_HEIGHT = int(YWIN/2)

DISPLAY = (XWIN, YWIN)
DEPTH = 32
FLAGS = 0
CAMERA_SLACK = 30

#DISPLAY
window = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)
clock = pygame.time.Clock()

#Classes
class World:
	def __init__(self,startX,startY,colors,colorsBonus):
		self.widthPlatform = 80
		self.heightPlatform = 10
		self.colorPlatforms = colors
	
		self.colorsBonus = colorsBonus
		self.widthBonus = 12
		self.heightBonus = 12
	
		self.bonusSpawnChance = 13
		self.platformChanceBroken = 10
	
		self.minY = self.heightPlatform + 30
		self.maxY = 100
		self.startX,self.startY = startX,startY
	
		self.platforms = [Block(startX - 50,startY + 50,self.widthPlatform,self.heightPlatform,self.colorPlatforms[0])]
		self.bonuses = []
	
	def update(self,camera):
		#Update platforms and bonuses arrays
		for p in self.platforms:
			if camera.apply(p).y > YWIN or camera.apply(p).y < -400:
				self.platforms.remove(p)
	
		for b in self.bonuses:
			if camera.apply(b).y > YWIN or camera.apply(b).y < -400:
				self.bonuses.remove(b)
	
		self.generate(camera)
	
	def generate(self,camera):
		if len(self.platforms) > 0:
			#  --generating all platform settings--
			#chopsing X position
			x = random.randint(0,XWIN-self.widthPlatform)
			#choosing Y position
			y = self.platforms[-1].rect.y - random.randint(self.minY,self.maxY)
			for i in range(len(self.platforms)):
				if i > 0 and self.platforms[-i].canJump:
					y = self.platforms[-i].rect.y - random.randint(self.minY,self.maxY)
					if y+self.heightPlatform < camera.apply(self.platforms[-1]).y or y > self.heightPlatform + camera.apply(self.platforms[-1]).y:
						break
					else:
						y -= self.heightPlatform*2
						break
			rect = Rect(x,y,self.widthPlatform,self.heightPlatform)#futur platform rect
			#random choice of the platform type
			breack,randomBonus,randomCanJump = random.randint(0,self.platformChanceBroken),random.randint(0,self.bonusSpawnChance),random.randint(0,6)
			breackable,haveBonus,canJump = False,False,True
			color = self.colorPlatforms[0]
			
			#can't jump on it
			if randomCanJump == 1 and self.platforms[-1].canJump:
				canJump = False
				color = self.colorPlatforms[2]
				breackable = True
			#can jump on it but destroy after collision
			elif breack == 1:
				color = self.colorPlatforms[1]
				breackable = True
			#have a bonus on it
			if randomBonus == 1 and breackable == False:
				haveBonus = True

			#create platform
			if camera.apply_rect(rect).y > -400:
				self.platforms.append(Block(x,y,self.widthPlatform,self.heightPlatform,color,breackable,canJump))
				if haveBonus:
					x = self.platforms[-1].rect.x + random.randint(0,self.widthPlatform-self.widthBonus)
					y = self.platforms[-1].rect.y - self.heightBonus
					self.bonuses.append(Bonus(x,y,self.widthBonus,self.heightBonus,40,self.colorsBonus[0]))
	
		else:
			self.platforms = [Block(self.startX - 50,self.startY + 50,self.widthPlatform,self.heightPlatform,self.colorPlatforms[0])]


class Camera(object):
	def __init__(self, camera_func, width, height,speed):
		self.camera_func = camera_func
		self.state = Rect(0, 0, width, height)
		self.lerpSpeed = speed
	
	def apply(self, target):
		return target.rect.move(self.state.topleft)
	
	def apply_rect(self,rect):
		return rect.move(self.state.topleft)
	
	def update(self, target):
		self.lerpSpeed = int(((HALF_HEIGHT-70) - self.apply(target).y) / 8)
		if self.apply(target).y < HALF_HEIGHT-70:
			self.state.y += self.lerpSpeed

class Block(pygame.sprite.Sprite):

	def __init__(self,x,y,w,h,color,breackable=False,canJump=True):
		self.image = pygame.Surface((w,h))
		self.image.fill(color)
		self.rect = Rect(x, y, w, h)
		self.breackable = breackable
		self.canJump = canJump

class Bonus(pygame.sprite.Sprite):
	def __init__(self,x,y,w,h,addForce,color,duration=1):
		self.rect = Rect(x,y,w,h)
	
		self.color = color
		self.image = pygame.Surface((w,h))
		self.image.fill(self.color)
	
		self.addForce = -addForce
		self.duration = duration

class Player(pygame.sprite.Sprite):
	def __init__(self,x,y,sx,sy,w,h,jumpforce,color,gravity=True,gravVelocity=0.5,mass=1):
		self.sx, self.sy = sx,sy
		self.accelRight,self.accelLeft,self.decceler = False,False,False
		self.accelVelocity = 0.5 / mass
		self.deccelVelocity = 0.6 / mass
		self.rect = Rect(x,y,w,h)
	
		self.color = color
		self.image = pygame.Surface((w,h))
		self.image.fill(self.color)
	
		self.isGrounded = False
		self.maxSpeedX,self.maxSpeedY = 12,25
		self.jumpforce = jumpforce
		self.gravity = gravity
		self.mass = mass
		self.gravVelocity = gravVelocity * mass
	
		self.events = [0,0,0]
		self.score = 0
		self.dead = False
	
	def collide(self,sx,sy,colliders,bonuses):
		for p in colliders:
			if pygame.sprite.collide_rect(self, p):
				#if sx > 0:
				#    self.rect.right = p.rect.left
				#if sx < 0:
				#    self.rect.left = p.rect.right
				if sy > -0.5:
					if p.breackable:
						colliders.remove(p)
					if p.canJump:
						self.rect.bottom = p.rect.top
						self.isGrounded = True
						self.sy = 0
				#if sy < 0:
				#    self.sy = 0.1
				#    self.rect.top = p.rect.bottom
		for b in bonuses:
			if pygame.sprite.collide_rect(self, b):
				if sy > -1:
					self.sy = b.addForce
					if b.duration > 1:
						for i in range(b.duration):
							self.sy += b.addForce
	
	
	def update(self,blocks,bonuses,camera):
		self.score = camera.state.y
		self.isGrounded = False
		
		if self.accelRight and self.sx < self.maxSpeedX:
			self.sx += self.accelVelocity
		if self.accelLeft and self.sx > -self.maxSpeedX:
			self.sx -= self.accelVelocity
		if self.decceler:
			if self.sx == 0:
				self.decceler = False
			if self.sx > 0:
				self.sx -= self.deccelVelocity
			if self.sx < 0:
				self.sx += self.deccelVelocity
			
	
		if camera.apply(self).y > YWIN:
			#self.isGrounded = True
			#self.rect.y = YWIN - self.rect.height
			self.dead = True
	
		if self.gravity:
			if self.isGrounded == False:
				self.sy += self.gravVelocity
				if self.sy > self.maxSpeedY:
					self.sy = self.maxSpeedY
	
		self.rect.left = (self.rect.left + self.sx)%XWIN
	
		self.rect.top += self.sy
		self.collide(0,self.sy,blocks,bonuses)
	
	def draw(self,surface,camera=None):
		if camera != None:
			surface.blit(self.image,camera.apply(self))
		else:
			surface.blit(self.image,self.rect)

# ALL KIND OF CAMERA.
def simple_camera(camera, target_rect):
	l, t, _, _ = target_rect
	_, _, w, h = camera
	return Rect(0, -t+HALF_HEIGHT, w, h)


#Variables
camera = Camera(simple_camera, XWIN, YWIN,6.5)
player = Player(300,550,0,0,25,30,12,COLORS[6])
world = World(player.rect.x,player.rect.y,[COLORS[11],COLORS[10],COLORS[12]],[COLORS[9]])

#Functions
def text(x,y,font,color,text,surface):
	text = font.render(text,True,color)
	surface.blit(text,(x,y))

def taskManager(player):
	if player.events[0] == 1:
		player.accelLeft = True
		player.accelRight = False
		player.decceler = False
	elif player.events[1] == 1:
		player.accelRight = True
		player.accelLeft = False
		player.decceler = False
	else:
		player.decceler = True
		player.accelLeft = False
		player.accelRight = False

	player.events[2] = 1
	if player.events[2] == 1 and player.isGrounded:
		player.events[2] = 0
		player.isGrounded = False
		player.rect.y -= int(player.rect.height/2)
		player.sy = -player.jumpforce

def eventManager(event,player):
	if event.type == QUIT:
		pygame.quit()
		sys.exit()
	elif event.type == KEYDOWN:
		if event.key == K_ESCAPE:
			pygame.quit()
			sys.exit()
		if event.key == K_RETURN and player.dead:
			player.dead = False
			player.__init__(300,550,0,0,25,30,12,COLORS[6])
			world.__init__(player.rect.x,player.rect.y,[COLORS[11],COLORS[10],COLORS[12]],[COLORS[9]])
			camera.__init__(simple_camera, XWIN, YWIN,6.5)
		if event.key == K_LEFT:
			player.sx = -1.5
			player.events[0] = 1
			player.events[1] = 0
		if event.key == K_RIGHT:
			player.sx = 1.5
			player.events[1] = 1
			player.events[0] = 0
		if event.key == K_SPACE:
			player.events[2] = 1
	elif event.type == KEYUP:
		if event.key == K_LEFT:
			player.events[0] = 0
		if event.key == K_RIGHT:
			player.events[1] = 0

loopGame = True

#Main Game Loop
while loopGame:
	for event in pygame.event.get():
		eventManager(event,player)
	taskManager(player)
	
	camera.update(player)
	world.update(camera)
	
	window.fill(COLORS[13])
	for b in world.platforms:
		window.blit(b.image,camera.apply(b))
	for b in world.bonuses:
		window.blit(b.image,camera.apply(b))
	if player.dead == False:
		text(25,10,FONTS[0],COLORS[1],str(int(player.score*0.02646))+" m",window)
		player.update(world.platforms,world.bonuses,camera)
		player.draw(window,camera)
	else:
		text(190,200,FONTS[1],COLORS[2],"GAME OVER",window)
		text(200,300,FONTS[1],COLORS[1],"SCORE: "+str(int(player.score*0.02646))+" m",window)
	
	pygame.display.update()
	clock.tick(FPS)
	
