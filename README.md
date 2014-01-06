Dicer
=====

An add on for slicing and running 3d printers from within blender 3d

To see the very original seed of this project the link below.
many of the first commits are simply me(rylan) pulling bits of code that
the wonderful people at Blender Artists posted

http://blenderartists.org/forum/showthread.php?318601-Dicer-a-blender-slicer-for-3d-printing&p=2520986#post2520986


Im setting out some specifically unique goals for Dicer, from the view point of a person that is already knowledgeable they may seem a bit odd but please understand that although Dicer should be built to run any printer, I have Thousands of peachy printer customers that will be using it.

Dew to the fact that the peachy printer is only 100 dollars we have a huge amount of first time users that need an overly simple "one click Print" type of interface, as well as other features.

With that in mind here are some goals

1. once a 3d printer is set up it if you click the print button blender should simply attempt to print the selected object, no questions asked.

2 we need a streaming print mode where the user can modify any part of the print that has not been deposited yet and those modifications will end up in the print. ( you can modifi the object while you are actually printing the object.)

3. menus for selecting different slicers to be used in the back-end ie cura
/ blender internal slicer etc.

4 auto apply all modifiers to the mesh before printing. 

5. Alwase save the resultant gcode file(save the streem) in the running directory. Because gocode is a fairly porable bake of a print job. 

6. save all setting and printer calibrations in a file that can be chosen from a menu

7 Make gcode that when saved to a .gcode file is viewable at http://gcode.ws/

When Dicer can do all this then we have created something great. 
If you would like to help please do! branch us and feel free to acomplish anything you like, see the todo.txt file for guidence :)



