import pymunk as mnk
import pygame as pg
import cv2, ffmpeg, os
import random

random.seed(100)

INPUT = "example.jpg"
FFMPEG_CONVERT = True
SIZE = 128+64
W, H = SIZE*4, SIZE*4
FPS = 60

BALLS_PER_FRAME= 20
BALL_COOLDOWN = int(0.01*FPS)
FINAL_WAIT = int(10*FPS)

UNTIL = int((SIZE**2)*0.32)

SPAWN_FN = lambda: pg.Vector2(random.randint(W//2-W//20, W//2+W//20), 0)

class Ball:
    R = W//SIZE
    id: int
    pos: pg.Vector2
    rgb: tuple[int, int, int]
    body: mnk.Body
    shape: mnk.Poly
    def __init__(self, id: int, space: mnk.Space, pos: pg.Vector2, rgb = (40, 40, 40)):
        self.id = id
        self.pos = pos
        self.rgb = rgb
        self.body = mnk.Body(50.0, 1.0)
        self.body.position = (pos.x, pos.y)
        self.shape = mnk.Circle(self.body, self.R)
        self.shape.elasticity = 0.95
        space.add(self.body, self.shape)

    def logic(self):
        self.pos.x = self.body.position[0]
        self.pos.y = self.body.position[1]

    def draw(self, screen):
        pg.draw.circle(screen, self.rgb, (self.pos.x, self.pos.y), self.R)

screen = pg.display.set_mode((W, H))
clock = pg.time.Clock()

img = pg.image.load(INPUT).convert()
img = pg.transform.smoothscale(img, (SIZE, SIZE))

space = mnk.Space()
space.gravity = (0, 100)

walls = [
    mnk.Segment(space.static_body, (W, 0), (W, H), 0),  # Right border
    mnk.Segment(space.static_body, (0, H), (0, 0), 0),     # Left border
    mnk.Segment(space.static_body, (W, H), (0, H), 0),  # Bottom border
]
for wall in walls:
    space.add(wall)

balls = []
next_ball = 1
ball_id = 0
ended = False
final_wait = FINAL_WAIT

record_new = None
while record_new == None:
    i = input("Record or play? (P to play, R for record): ").lower()
    if i and i[0] in ("p", "r"):
        record_new = i[0] == "r"
    else:
        print("Incorrect response")
print()

if record_new:
    while 1:
        next_ball -= 1

        enough_balls = len(balls) >= UNTIL
        need_to_wait = final_wait > 0
        if next_ball <= 0 and not enough_balls:
            next_ball = BALL_COOLDOWN
            for _ in range(BALLS_PER_FRAME):
                balls.append(Ball(
                    ball_id, 
                    space, 
                    SPAWN_FN(),
                    (0, 0, 0)
                ))
                ball_id += 1
            print(f"{round(ball_id/UNTIL*100, 2)}%")
        elif enough_balls and need_to_wait:
            final_wait -= 1
            print(f"Waiting for balls to stabilize: {final_wait} frames")
        elif enough_balls and not need_to_wait:
            data = bytes([])
            balls.sort(key=lambda x: x.id)
            for ball in balls:
                x = round((ball.pos.x/ball.R))
                x = min(max(x, 0), SIZE-1)
                bx = int(x/SIZE*255)

                y = round((ball.pos.y)/ball.R)
                y = min(max(y, 0), SIZE-1)
                by = int(y/SIZE*255)

                rgb = img.get_at((x, y))
                data += bytes([bx, by])

            with open("colors.bin", "wb") as file:
                file.write(data)
            print("Done writing!")
            break

        space.step(1/FPS)
        for ball in balls:
            ball.logic()
else:
    colors = []
    with open("colors.bin", "rb") as file:
        colors = file.read()

    run = True
    output = cv2.VideoWriter("output.avi", cv2.VideoWriter_fourcc(*"MJPG"), FPS, (W, H))
    out_surf = pg.Surface((W, H)).convert()

    while run:
        clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
        next_ball -= 1
        if next_ball <= 0 and len(balls) < UNTIL:
            next_ball = BALL_COOLDOWN
            for _ in range(BALLS_PER_FRAME):
                col_ind = ball_id*2
                xb, yb = (colors[col_ind], colors[col_ind+1])
                color = img.get_at((int(xb/255*SIZE), int(yb/255*SIZE)))[:3]
                balls.append(Ball(
                    ball_id, 
                    space, 
                    SPAWN_FN(),
                    color
                ))
                ball_id += 1

        space.step(1/FPS)

        out_surf.fill((0, 0, 0))
        for ball in balls:
            ball.logic()
            ball.draw(out_surf)
        screen.blit(out_surf, (0, 0))

        arr = pg.surfarray.array3d(out_surf)
        arr = arr.transpose([1, 0, 2])
        cv_img = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        output.write(cv_img)

        pg.display.flip()
    pg.quit()
    output.release()
    if FFMPEG_CONVERT:
        ffmpeg.input("output.avi").output("output.mp4", 
            codec='libx264', 
            crf=23, 
            acodec='aac', 
            strict='experimental', 
            audio_bitrate='192k', 
            channels=2
        ).run()
        os.remove("output.avi")
        
