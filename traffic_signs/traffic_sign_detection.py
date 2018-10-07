#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Usage:
  traffic_sign_detection.py <dirName> <outPath> <pixelMethod> [--windowMethod=<wm>] 
  traffic_sign_detection.py -h | --help
Options:
  --windowMethod=<wm>        Window method       [default: 'None']
"""


from docopt import docopt
import numpy as np
import fnmatch
import os
import sys
import imageio
from candidate_generation_pixel import candidate_generation_pixel
from candidate_generation_window import candidate_generation_window
from evaluation.load_annotations import load_annotations
import evaluation.evaluation_funcs as evalf

'''
Main method from where the sig detection will be executed.
'''

def traffic_sign_detection(directory, output_dir, pixel_method, window_method):

    pixelTP  = 0
    pixelFN  = 0
    pixelFP  = 0
    pixelTN  = 0

    windowTP = 0
    windowFN = 0
    windowFP = 0

    window_precision = 0
    window_accuracy  = 0

    # Load image names in the given directory
    file_names = sorted(fnmatch.filter(os.listdir(directory), '*.jpg'))

    
    for name in file_names:
        base, extension = os.path.splitext(name)

        # Read file
        im = imageio.imread('{}/{}'.format(directory,name))
        print ('{}/{}'.format(directory,name))

        # Candidate Generation (pixel) ######################################
        pixel_candidates = candidate_generation_pixel(im, 'RGB')


        fd = '{}/{}_{}'.format(output_dir, pixel_method, window_method)
        if not os.path.exists(fd):
            os.makedirs(fd)

        out_mask_name = '{}/{}.png'.format(fd, base)
        imageio.imwrite (out_mask_name, np.uint8(np.round(pixel_candidates)))


        if window_method != 'None':
            window_candidates = candidate_generation_window(im, pixel_candidates, window_method)

        # Accumulate pixel performance of the current image #################
        print('{}/{}.png'.format(fd,base))
        pixel_annotation = imageio.imread('{}/mask.{}.png'.format(fd,base)) > 0

        [localPixelTP, localPixelFP, localPixelFN, localPixelTN] = evalf.performance_accumulation_pixel(pixel_candidates, pixel_annotation)
        pixelTP = pixelTP + localPixelTP
        pixelFP = pixelFP + localPixelFP
        pixelFN = pixelFN + localPixelFN
        pixelTN = pixelTN + localPixelTN

        [pixel_precision, pixel_accuracy, pixel_specificity, pixel_sensitivity] = evalf.performance_evaluation_pixel(pixelTP, pixelFP, pixelFN, pixelTN)

        if window_method != 'None':
            # Accumulate object performance of the current image ################
            window_annotationss = load_annotations('{}/gt/gt.{}.txt'.format(directory, base))
            [localWindowTP, localWindowFN, localWindowFP] = evalf.performance_accumulation_window(window_candidates, window_annotationss)
            windowTP = windowTP + localWindowTP
            windowFN = windowFN + localWindowFN
            windowFP = windowFP + localWindowFP


            # Plot performance evaluation
            [window_precision, window_sensitivity, window_accuracy] = evalf.performance_evaluation_window(windowTP, windowFN, windowFP)

    return [pixel_precision, pixel_accuracy, pixel_specificity, pixel_sensitivity, window_precision, window_accuracy]





                
if __name__ == '__main__':
    # read arguments
    args = docopt(__doc__)

    images_dir = args['<dirName>']          # Directory with input images and annotations
                                            # For instance, '../../DataSetDelivered/test'
    output_dir = args['<outPath>']          # Directory where to store output masks, etc. For instance '~/m1-results/week1/test'

    methodMask = args['<pixelMethod>']

    pixel_precision, pixel_accuracy, pixel_specificity, pixel_sensitivity, window_precision, window_accuracy = traffic_sign_detection(images_dir, output_dir, methodMask, 'example1');



    print (pixel_precision, pixel_accuracy, pixel_specificity, pixel_sensitivity, window_precision, window_accuracy)

    
