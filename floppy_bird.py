import pygame
from pygame.locals import *
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 864
screen_height = 936

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Floppy Bird')


#define font
font = pygame.font.SysFont('impact', 60)

#define colors
white = (255, 255, 255)

# define game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150 #adds gap between pipe
pipe_frequency = 1500 #milliseconds of how much it shows up
last_pipe = pygame.time.get_ticks() - pipe_frequency #check when the last pipe was created and compare to current pipe
score = 0
pass_pipe = False # bird hasnt passed the pipe, cant increase counter


#load images
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')
button_img = pygame.image.load('img/restart.png')


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0 
    return score #return the score back into the reset game function instead of local variable


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = [] #list of sprites for animation of bird
        self.index = 0
        self.counter = 0 #controls speed in which animation runs
        for num in range(1, 4):
            img = pygame.image.load(f'img/bird{num}.png') #loads in all fo the images from bird1-bird3
            self.images.append(img) #assign image into the list
        self.image = self.images[self.index] #will take the first image at index 0 
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):

        if flying == True:
            #gravity
            self.vel += 0.5 #increase the velocity every iteration so the bird accelerates downwards w/ gravity
            if self.vel > 8: # add a limit so the vel doesnt go to infinity
                self.vel = 8 #resets once it hits 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel) #add to y coordinate of the bird, it will fall down to ground 

        if game_over == False:
            #jump
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False: #function looks for mouse clicks and returns a list. we want left click, so index 0
                self.clicked = True #keeps it so bird doesnt keep going off screen when clicked
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0: #function looks for mouse release
                self.clicked = False

            #handle the animation
            self.counter += 1
            flap_cooldown = 10

            if self.counter > flap_cooldown: #once iterated five times, ready to move on to the next one
                self.counter = 0 #reset counter
                self.index += 1 #update animation, this cant exceed the number of images we have
                if self.index >= len(self.images):
                    self.index = 0 #reset the index back to zero once we exceed the length of the list = number of images we have (3)
            self.image = self.images[self.index] #update the image since we updated the index

            #rotate the bird as it falls
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2) #image at the 0 index is rotated, clockwise
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90) #anti-clockwise, faces ground



class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')
        self.rect = self.image.get_rect() #gets the image and places a rectangle around it
        #position 1 is from the top, -1 is from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x,y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self): #want pipes to move left, reduce x coordinate w/ every iteration
        self.rect.x -= scroll_speed
        if self.rect.right < 0: # check if right hand side of rect has gone out of screen
            self.kill() # deletes the pipes so they dont stay in memory


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):

        action = False #false until two conditions are met
        
        #get mouse position, can't click without it
        pos = pygame.mouse.get_pos()

        #check if mouse is over the button through a collision
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1: #returns small list of mouse buttons
                action = True
        #draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action
    
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))

bird_group.add(flappy)

#create restart button instance
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)

run = True
while run:

    clock.tick(fps)

    # draw background
    screen.blit(bg, (0,0))

    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)


    #draw the ground
    screen.blit(ground_img, (ground_scroll, 768))

    #check the score
    if len(pipe_group) > 0: #whether the sprite has passed the left hand of the particular pipe its passed through
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
            and pass_pipe == False: #is the bird within the pipe's zone?
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False


    draw_text(str(score), font, white, int(screen_width / 2), 20)

    #look for collision
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0: #looks for collision btwn two groups
        game_over = True
    #check if bird has hit the ground
    if flappy.rect.bottom >= 768:
        game_over = True
        flying = False


    if game_over == False and flying == True: # if the game isnt over and the user has clicked the mouse, game starts

        #generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100) # random height w/ random library, within range of -100 and 100
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2)+ pipe_height, 1)
            pipe_group.add(btm_pipe) #add top and bttm to pipe group
            pipe_group.add(top_pipe)
            last_pipe = time_now #last time the pipe was created is right now, need to update the variable

        # draw and scroll the ground
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

        pipe_group.update()


    #check for game over and reset
    if game_over == True:
        if button.draw() == True:
            game_over = False #reset the game over
            score = reset_game() #since reset_game is returning the score


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True

    pygame.display.update()

pygame.quit()
