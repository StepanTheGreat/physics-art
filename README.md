# A physics art generator

The secret behind this interesting visualisation is very simple - I don't compute anything. I'm just simulating the balls and color them in the
end. That means that I can run absolutely ANY simulation, and it will always give the image I want.
In this example I also added recording with ffmpeg and cv2 to write video-files directly.

How to use:
The way it works is it should first simulate the balls so it can bind color coordinates for them. Then you re-run the simulation, 
and it will apply the color coordinates to the balls under specific index, from the image you've selected in the constant. 

Here's a simple tutorial:
1. First, put an image you want to use (the program will autoscale it automatically). 
    You can set the size of the image you want to simulate with the SIZE constant (Be aware it will create more balls).
2. Second, you need to record the balls, you can do this by pressing r when running the program. Once it's finished it will tell you.
3. Third and final - you can play the simulation, it will automatically record it and stop whenever you close the program.

## You don't need to re-record the simulation to change the image
For the same environment, the program will use the same texture coordinates. Only change the simulation if you change other constants/variables/functions.
Overall, you can customize it however you want and create actually impressive scenes with colliders.