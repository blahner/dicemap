# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 13:44:08 2021

@author: Ben3
"""

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os
import skimage.io
import skimage.util

def factor(num):
    factors = []
    for i in range(1, num+1):
        if(num % i) == 0:
            factors.append(i)
    return factors

def RGB2Gray(im):
    assert(im.shape[2] == 3) #3 dimensions
    red_channel = im[:,:,0]
    green_channel = im[:,:,1]
    blue_channel = im[:,:,2]
    imgGray = 0.2989 * red_channel + 0.5870 * green_channel + 0.1140 * blue_channel
    return imgGray

def DiceMap(im, cuts, dice):
    hidx = np.arange(0,im.shape[0],cuts[0])
    widx = np.arange(0,im.shape[1],cuts[1])
    densemap = np.zeros((len(hidx),len(widx)))
    for hcount,h in enumerate(hidx):
        for wcount,w in enumerate(widx):
            d = im[h:h+cuts[0],w:w+cuts[0]]
            densemap[hcount,wcount] = d.sum()/(cuts[0]*cuts[1])
    
    bins = np.linspace(min(densemap.ravel()),max(densemap.ravel()), 7)
    montage_list = []    
    for val in densemap.ravel():
        if (val <= bins[1]) & (val >= bins[0]):
            montage_list.append(dice['one'])
        if (val <= bins[2]) & (val > bins[1]):
            montage_list.append(dice['two'])
        if (val <= bins[3]) & (val > bins[2]):
            montage_list.append(dice['three'])
        if (val <= bins[4]) & (val > bins[3]):
            montage_list.append(dice['four'])
        if (val <= bins[5]) & (val > bins[4]):
            montage_list.append(dice['five'])
        if (val <= bins[6]) & (val > bins[5]):
            montage_list.append(dice['six'])
            
    return montage_list, densemap.shape


root = "D:\\PYTHON\\dice_project\\"

im_obj = Image.open(os.path.join(root, "images", "joker_playingcard.jpg"))
im_obj_bw = im_obj.convert('1')


im = np.array(im_obj)
im_bw = np.array(im_obj_bw)
print(sorted(list(set(factor(im_bw.shape[0])) & set(factor(im_bw.shape[1])))))
cuts = (9,9)


#imGray = RGB2Gray(im)

dicelabels = ['one','two','three','four','five','six']
dice = {}
for dl in dicelabels:
    im_obj = Image.open(os.path.join(root, "images", "dice", dl + ".gif"))
    im_obj_bw = im_obj.convert('1')
    dice[dl] = np.array(np.array(im_obj_bw))[38:208,75:245]


montage_list, shape = DiceMap(im_bw, cuts, dice)

m = skimage.util.montage(montage_list, grid_shape=shape, padding_width=0, multichannel=False)
plt.imshow(m,cmap="Greys")
plt.axis('off')
plt.show()