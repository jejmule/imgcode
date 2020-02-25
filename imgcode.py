# imgcode v0.3 08/04/2019
# utility for CNC lasers image etching
# developed by M. "Vidmo" Widomski
# github.com/vidmo91
# hackaday.io/vidmo91
#
# correct execution command: python imgcode.py image_path output_file_path x_offset_mm y_offset_mm output_image_horizontal_size_mm pixel_size_mm feedrate max_laser_power number_of_colours
# e.g. of correct execution commands:
# python .\imgcode.py "C:\lena.png" test.nc 0 0 10 0.5 100 1000 2
# python .\imgcode.py lena.png test.nc 0 0 10 0.2 220 255 5
#
# requirements contains list of modules I had it working on
#
# todo:
#
# check and correct variable types, round floats
# add some GUI maybe?
#
#
#
#

# Copyright 2019 M.Widomski
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np
import matplotlib
import matplotlib.pyplot
import scipy.ndimage as ndimage
import imageio
import PIL.Image
import sys
import colorama
colorama.init()

print("\n\n"+colorama.Fore.CYAN+"imgcode - simple image etching gcode generator"+colorama.Fore.RESET+"\n\n")
# uncoment for berry veautiful splash screen
# print(colorama.Fore.GREEN+"\t           _         __"+"\n"+"\t \\    / | | \\  |\\/| |  |"+"\n"+"\t  \\  /  | |  | |  | |  |"+"\n"+"\t   \\/   | |_/  |  | |__|\n \t\tpresents \n"+colorama.Fore.RED+"\t\timgcode"+colorama.Fore.RESET+"\n"+"\t"+colorama.Back.LIGHTCYAN_EX+colorama.Fore.RED+"mmmh... those aesthetics!!!"+colorama.Back.RESET+colorama.Fore.RESET+"\n\t"+colorama.Back.LIGHTCYAN_EX+colorama.Fore.RED+"  just berry veautiful!!!  "+colorama.Back.RESET+colorama.Fore.RESET+"\n\n")



def fileDialog(fileName):
    try:
        f = open(fileName, 'r')
        f.close
    except:
        print(fileName+" it is")
        f = open(fileName, 'w')
        f.close
    else:
        answer = input(
            fileName+" exists, do you want to overwrite it? (Y/n): ")
        if (answer == 'y')or(answer == 'Y')or(answer == ''):
            f = open(fileName, 'w')
            print(fileName+' will be overwritten')
            f.close
        elif answer == 'n'or(answer == 'N'):
            raise NameError("Specify right path next time")
        else:
            raise NameError("wrong answer")
    return f

def px2str(pixel,pixel_size,offset) : 
    return str(round(pixel*pixel_size+offset,4))

if len(sys.argv) != 10:

    print(colorama.Fore.RED+'Number of arguments:', len(sys.argv), 'arguments. (required 10 arguments)')
    print('Argument List:', str(sys.argv))
    print("correct execution command: ")
    print("python imgcode.py image_path output_file_path x_offset_mm y_offset_mm output_image_horizontal_size_mm pixel_size_mm feedrate max_laser_power number_of_colours")
    print("e.g. python .\\imgcode.py lena.png test.nc 0 0 10 0.2 100 255 5")
    print("e.g. python .\\imgcode.py \"C:\\Documents\\laser files\\lena.png\" \"C:\\laser files\\out files\\output_gcode.nc\" 0 0 10 0.2 100 255 5"+colorama.Fore.RESET)
    raise NameError("wrong execution command")
print("so far so good, now parsing values...")

# imread and convert to 8bit grayscale
try:
    img = imageio.imread(sys.argv[1], as_gray=True, pilmode="RGB")
    print("image loaded...")
except:
    raise NameError("Something is wrong with image. Probably path")
# imag = imag.astype(np.uint8)

# open text file for writing:
f = fileDialog(sys.argv[2])

# parsing values
try:
    x_offset_mm = float(sys.argv[3])
    y_offset_mm = float(sys.argv[4])
    output_image_horizontal_size_mm = float(sys.argv[5])
    pixel_size_mm = float(sys.argv[6])
    feedrate = int(sys.argv[7])
    max_laser_power = float(sys.argv[8])
    number_of_colours = int(sys.argv[9])
    print("parameters look OK...")
except:
    raise NameError("Some of parameters are not numbers")

print("processing...")
# reseize image
y_size_input = len(img)
x_size_input = len(img[0])

# scale calculation
x_size_output = output_image_horizontal_size_mm/pixel_size_mm
scale = x_size_output/x_size_input
# reseize image
img = PIL.Image.fromarray(img,)
img = img.resize((int(scale*x_size_input), int(scale*y_size_input)))
img = np.asarray(img)

# image size calculation
y_size_output = len(img)
x_size_output = len(img[0])

# negative for laser etching
img=np.subtract(255,img)

# set max value of image colour to number of colours
number_of_colours -= 1
img = np.rint(np.multiply(img, number_of_colours/255))

# apply uniform filter to smooth power over etchs
#img = ndimage.filters.uniform_filter1d(img,10,axis=1)

#save preview
img_out=np.empty((x_size_output,y_size_output))
img_out=np.rint(np.multiply(img, 255/number_of_colours))
img_out = img_out.astype(np.uint8)
imageio.imwrite('out_img.png',img_out)

#convert to feedrates
img = np.multiply(img, max_laser_power/number_of_colours)

# display preview before processing - requires closing plot window before proceeding
# img2=np.subtract(number_of_colours,img)
# matplotlib.pyplot.imshow(img2, cmap='gray')
# matplotlib.pyplot.show()

# flip up-down for simplicity
img=np.flip(img,0)

#Gcode processing
f.write("( imgcode generated code )\n")
f.write("( developed by M. \"Vidmo\" Widomski )\n")
f.write("(  github.com/vidmo91 )\n")
f.write("(  hackaday.io/vidmo91 )\n")
f.write(" \n")


f.write("F"+str(feedrate)+"\n")
f.write("M92 \n") #add your G-CODE file header here
f.write("G64 R90 \n\n") #keep accelerating through G1 code with an angle between line of 90° : between X and Z segments

#compute acceleration distance to operate G1 movement at constant speed
acc = 500 # mm/s
acc_dst_mm = 0.5 * (feedrate/60)**2 / acc #dst to accelerate in mm
acc_dst_px = int(np.ceil(acc_dst_mm / pixel_size_mm)) #dst to accelerate in px, rounded to the next greater integer

#Pad image with one 0 in each side of the x axis to get a 0->power transition on each line
#img = np.pad(img,((0,0),(acc_dst_px,acc_dst_px)),mode='constant')
#x_offset_mm -= acc_dst_px * pixel_size_mm

#scan to generate g code
f.write("M3 \n")
for y in range(y_size_output):
    prev_power = 0
    line = img[y,:]
    if np.sum(line) > 0:    #line is not empty, sum of power is greater than 0
        power_on = np.nonzero(line) #index where the power is not null
        start = power_on[0][0] -1 #index before the line power is switch on
        stop = power_on[0][-1] + 1 #first index after the line where power is off
        
        # G0 Fast move to next beginning of line. The acceleration distance is taken into account
        if y%2 == 0 : #even line
            f.write("G0 X"+px2str(start-acc_dst_px,pixel_size_mm,x_offset_mm)+" Y"+px2str(y,pixel_size_mm,y_offset_mm)+" Z0 \n")
            #add 0 to the end of the line(needed to switch off the laser)
            line = np.append(line,0)
            interval = np.arange(start,stop+1,step=1)
        else : #odd line, revert the interval
            f.write("G0 X"+px2str(stop+acc_dst_px,pixel_size_mm,x_offset_mm)+" Y"+px2str(y,pixel_size_mm,y_offset_mm)+" Z0 \n")
            #add 0 to the beginnig of the line
            line = np.insert(line,0,0)
            interval = np.arange(stop,start-1,step=-1)
        
        # G1 Engrave, the engraving power is controlled using Z axis and the step/dir to pwm board to peform onflight processing
        # Using G64 "look ahead feed" in mach3 or eding CNC, the machine accelerate through colinear lines
        for x in interval :
            if (prev_power != line[x] or line[x] != line[x+1]) : #power change
                f.write("G1 X"+px2str(x,pixel_size_mm,x_offset_mm))
                f.write(" Z"+str('{:.6f}'.format(line[x]))+"\n")
                prev_power = line[x]
        
        # G1 to the end of the line to deccelerate on this small G1 section
        if y%2 == 0 : #even line
            f.write("G1 X"+px2str(stop+acc_dst_px,pixel_size_mm,x_offset_mm)+"\n")
        else : #odd line, revert the interval
            f.write("G1 X"+px2str(start-acc_dst_px,pixel_size_mm,x_offset_mm)+"\n")
            
f.write("M5 \n")        
f.close()

#input("everything done, press ENTER to exit, goodbye!")
print(colorama.Fore.GREEN+"\neverything done, buh bye!\n")
input("press ENTER to exit")
