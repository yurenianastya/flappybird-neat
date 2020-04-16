import pygame
import time
import os
import random
import neat
pygame.font.init()

WIN_WIDTH = 480
WIN_HEIGHT = 600
FLOOR = 530
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)
DRAW_LINES = False

WINDOW = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT)) 
pygame.display.set_caption("Flappy Bird")

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png"))) for x in range(1,4)]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")).convert_alpha())
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")).convert_alpha())
BG_IMG =  pygame.transform.scale(pygame.image.load(os.path.join("imgs","bg.png")).convert_alpha(), (600, 900))

gen = 0

class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROTATION_VELOCITY = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.velocity = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.velocity = -10.5
        self.tick_count = 0
        self.height = self.y
    
    def move(self):
        self.tick_count += 1

        displacement = self.velocity*(self.tick_count) + 0.5*(3)*(self.tick_count)**2  
        
        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16

        if displacement < 0:
            displacement -= 2
        
        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROTATION_VELOCITY
    
    def draw(self, window):
        self.img_count += 1

        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
        
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        blitRotateCenter(window, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 200
    VELOCITY = 5

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 325)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VELOCITY

    def draw(self, window):
        window.blit(self.PIPE_TOP, (self.x, self.top))
        window.blit(self.PIPE_BOTTOM, (self.x, self.bottom))
    
    def collide(self, bird, window):
        bird_mask = bird.get_mask()
        topmask = pygame.mask.from_surface(self.PIPE_TOP)
        bottommask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        topoffset = (self.x - bird.x, self.top - round(bird.y))
        bottomofffset = (self.x - bird.x, self.bottom - round(bird.y))

        bottom_point = bird_mask.overlap(bottommask, bottomofffset)
        top_point = bird_mask.overlap(topmask, topoffset)

        if top_point or bottom_point:
            return True
        
        return False

class Base:
    VELOCITY = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
    
    def move(self):
        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
    
    def draw(self, window):
        window.blit(self.IMG, (self.x1, self.y))
        window.blit(self.IMG, (self.x2, self.y))

def blitRotateCenter(surf, image, topleft, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rectangle = rotated_image.get_rect(center=image.get_rect(topleft = topleft).center)
    surf.blit(rotated_image, new_rectangle.topleft)


def draw_window(window, birds, pipes, base, score, gen, pipe_ind):
    if gen == 0:
        gen = 1
    window.blit(BG_IMG, (0, 0))
    
    for pipe in pipes:
        pipe.draw(window)

    base.draw(window)

    for bird in birds:
        if DRAW_LINES:
            try:
                pygame.draw.line(window, (255,0,0), (bird.x+ bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                pygame.draw.line(window, (255,0,0), (bird.x+ bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
            except:
                pass
        bird.draw(window)

    score_stat = STAT_FONT.render("Score: " + str(score), 1, (0, 153, 0))
    window.blit(score_stat, (WIN_WIDTH - 10 - score_stat.get_width(), 10))

    score_stat = STAT_FONT.render("Gens: " + str(gen-1),1,(0, 153, 0))
    window.blit(score_stat, (10, 10))

    score_stat = STAT_FONT.render("Alive: " + str(len(birds)),1,(0, 153, 0))
    window.blit(score_stat, (10, 50))

    pygame.display.update()


def eval_genomes(genomes, config):

    global WINDOW, gen
    window = WINDOW
    gen += 1

    nets = []
    ge = []
    birds = []

    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        genome.fitness = 0
        ge.append(genome)


    base = Base(FLOOR)
    pipes = [Pipe(700)]
    clock = pygame.time.Clock()
    score = 0

    run = True
    while run and len(birds) > 0:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:   
                run = False
                pygame.quit()
                quit()
                break

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1

        for x, bird in enumerate(birds):
            ge[x].fitness += 0.1
            bird.move()

            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height),
             abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.jump()

        base.move()

        add_pipe = False
        removelist = []
        for pipe in pipes:
            pipe.move()
            for bird in birds:
                if pipe.collide(bird, window):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                removelist.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            for genome in ge:
                genome.fitness += 5
            pipes.append(Pipe(WIN_WIDTH))
        
        for r in removelist:
            pipes.remove(r)

        for bird in birds:
            if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))
        
        draw_window(WINDOW, birds, pipes, base, score, gen, pipe_ind)

def run(config_file):
    config = neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,
    neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    statistics = neat.StatisticsReporter()
    population.add_reporter(statistics)
    winner = population.run(eval_genomes, 50)
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt") 
    run(config_path)