# -*- coding: utf-8 -*-
"""
Created on Sun Oct 10 18:13:57 2021

@author: Ben3
"""

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os
import skimage.io
import skimage.util
from scipy import interpolate
from scipy.spatial import distance
import math
from tqdm import tqdm

def factor(num):
    factors = []
    for i in range(1, num+1):
        if(num % i) == 0:
            factors.append(i)
    return factors

def crop(im, newSize=(-1, -1, -1, -1)):
    #crop image to a default or specified size. (-1, -1, -1, -1) denotes defualt
    #default cropping is each axis is rounded down to nearest hundred and cropped from both ends.
    #Rough way to give each image the maximum number of common factors for different granularity in
    #dice coverage while keeping as much of the (centered) image as possible
    if newSize == (-1, -1, -1, -1):
        i = math.floor(im.shape[0]/100) * 100
        j = math.floor(im.shape[1]/100) * 100
        i_delta = im.shape[0]-i
        j_delta = im.shape[1]-j
        i1 = int(i_delta/2)
        i2 = int(i1 + i)
        j1 = int(j_delta/2)
        j2 = int(j1 + j)
        return im[i1:i2,j1:j2]
    else:
        return im[newSize[0]:newSize[1], newSize[2]:newSize[3]]

def DiceMap(im, cut, dice):
    #replace every cut of the original image with the dice with the highest similarity
    hidx = np.arange(0,im.shape[0],cut)
    widx = np.arange(0,im.shape[1],cut)
    
    diceshape = dice['one white'].shape
    
    x = np.arange(cut)
    y = np.arange(cut)

    xnew = np.linspace(0,cut,diceshape[0])
    ynew = np.linspace(0,cut,diceshape[0])
    labels = ['one','two','three','four','five','six']
    materials_white = dict.fromkeys(labels,0)
    materials_black = dict.fromkeys(labels,0)

    montage_list = []
    for hcount,h in enumerate(tqdm(hidx)):
        for wcount,w in enumerate(widx):
            z = im[h:h+cut,w:w+cut]
            f = interpolate.interp2d(x, y, z, kind='linear')
            znew = f(xnew,ynew)
            
            best_dist = 999999999
            best_label = []
            for label, val in dice.items():
                dist = distance.euclidean(val.astype(int).ravel(), znew.ravel())
                if dist < best_dist:
                    best_dist = dist
                    best_label = label
            split = best_label.split(' ')
            num = split[0]
            col = split[1]
            if 'rot' in num:
                num = num.replace('rot','') #remove the rot if there
            if col == 'black':
                materials_black[num] += 1
            elif col == 'white':
                materials_white[num] += 1
            montage_list.append(dice[best_label])
    materials = (materials_white, materials_black)
    return montage_list, (len(hidx),len(widx)), materials
    
    
root = "XXX" #your path here
image_fname = 'dice_pic.jpg' #filename of the image you want to convert to dice

template_obj = Image.open(os.path.join(root, "images", image_fname))
template_obj_bw = template_obj.convert('1')
template_bw = crop(np.array(template_obj_bw))
print(template_bw.shape)
pixel_choices = sorted(list(set(factor(template_bw.shape[0])) & set(factor(template_bw.shape[1]))))[1:] #don't include 1
print(pixel_choices)
cut = -1
while cut not in pixel_choices:
    cut = int(input("Enter the number of pixels you want to replace with a single (square) die. Choose from numbers above: \n"))
    if cut not in pixel_choices:
        print("Not a valid input")
    
#prepare template die
dicelabelstmp = ['one','two','three','four','five','six']
dicetmp = {}
for dl in dicelabelstmp:
    im_obj = Image.open(os.path.join(root, "images", "dice_templates", dl + ".gif"))
    im_obj_bw = im_obj.convert('1')
    dicetmp[dl] = np.array(np.array(im_obj_bw))[43:205,79:241] #[38:208,75:245]

dice = {}
dicelabels = {'one': 'one', 'two': 'two', 'tworot': "two", 'three': 'three', 'threerot': 'three', 'four': 'four', 'five':'five', 'six':'six', 'sixrot':'six'}
colors = ['black','white'] #color of dice background
for newlabel, arraylabel in dicelabels.items():
    arr = dicetmp[arraylabel]
    if 'rot' in newlabel:
        arr = np.rot90(arr)
    for color in colors:
        #the dice arrays are black background by default
        if color == 'white':
            dice[newlabel + ' ' + color] = ~arr
        elif color == 'black':
            dice[newlabel + ' ' + color] = arr
    
montage_list, shape, materials = DiceMap(template_bw, cut, dice)
print("Size of dice portrait using (very small) 5mm die: ", round(shape[0]*0.005*3.28084,2), "x", round(shape[1]*0.005*3.28084,2), "feet")
print("Size of dice portrait using (standard) 16mm die: ", round(shape[0]*0.016*3.28084,2), "x", round(shape[1]*0.016*3.28084,2), "feet")

print(materials[0])
print("Total number of white die needed:", sum(materials[0].values()))
print(materials[1])
print("Total number of black die needed:", sum(materials[1].values()))

m = skimage.util.montage(montage_list, grid_shape=shape, padding_width=0, multichannel=False)
plt.imshow(template_bw,cmap="Greys")
plt.axis('off')
plt.show()
plt.imshow(m,cmap="Greys")
plt.axis('off')
plt.show()