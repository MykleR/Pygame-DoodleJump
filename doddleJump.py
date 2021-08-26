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


import pygame, sys

from camera import Camera
from player import Player
from level import Level
from settings import *




if __name__ == "__main__":
	# ============= Init =============

	# Window / Render
	window = pygame.display.set_mode(DISPLAY,FLAGS)
	clock = pygame.time.Clock()

	# Instances
	camera = Camera()
	lvl = Level()
	player = Player(
		XWIN/2-PLAYER_SIZE[0]/2,# X POS
		YWIN/2+YWIN/4,#  Y POS
		*PLAYER_SIZE,#   SIZE
		PLAYER_COLOR#    COLOR
	)

	# User Interface
	gameover_txt = LARGE_FONT.render("Game Over",1,GRAY)
	gameover_rect = gameover_txt.get_rect(center=(HALF_XWIN,HALF_YWIN))
	score = 0
	score_txt = SMALL_FONT.render(str(score)+" m",1,GRAY)
	score_pos = pygame.math.Vector2(10,10)

	# ============= MAIN LOOP =============
	loop = True
	while loop:
		# ---------- User Events ----------
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					loop=False
				if event.key == pygame.K_RETURN and player.dead:
					camera.reset()
					lvl.reset()
					player.reset()

			player.handle_event(event)
		
		# ----------- Update -----------
		player.update()
		lvl.update(player)
		if not player.dead:
			camera.update(player.rect)
			#calculate score and update UI
			score=-camera.state.y//50
			score_txt = SMALL_FONT.render(str(score)+" m",1,GRAY)

		# ----------- Display -----------
		window.fill(WHITE)
		lvl.draw(window)
		player.draw(window)

		# User Interface
		if player.dead:
			window.blit(gameover_txt,gameover_rect)
		window.blit(score_txt,score_pos)

		pygame.display.update()
		clock.tick(FPS)#max loop/s

