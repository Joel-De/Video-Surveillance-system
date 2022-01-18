# Video-Surveillance-system


The following is a video surveilance system that uses Artifical Inteligence to track and record all instances of human activity.

![Sample](https://user-images.githubusercontent.com/71618484/149887253-4ce2c641-f17d-4794-b283-2571f1c982b0.JPG)

The complete system can be split into 3 parts:

1. 3-Axis Camera Gimbal
2. Custom Computer vision AI models
3. SQL Database interface


1. 3 - Axis Camera Gimbal

The 3 Axis Gimbal, which was designed to be compatable with common hobby servo motors, provides the system the ability to look around a given location, increasing the theoretical field of view by over 180 degrees in both the z and x rotation axis. This system is controled via an arduino, which communicates to the software on the host via serial communication using a custom protocol to transmit instructions.

2.  Computer vision AI models

The AI within the overall system is the heard of what makes the system inteligent, allowing it detect humans, and then follow them in real time. This model is trained using a custom dataset designed to maximize performance on unseen data, as well as uses a system that supports transfer learning (Can be found under the Object Detection repository). This model is specifically optimized to have high performance on mid to low tier hardware, removing the requirement for high tier hardware often needed for advanced computer vision.

3. SQL Database interface


All the information collected, ie. Instances of detected humans that have been tracked until out of view are encoded, and then saved to an SQL database from where they can be viewed later with the included utility. The database records all critical information such as the time and date of the occurunce, which will all be recorded upon dumping its contents.

