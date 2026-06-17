#! /usr/bin/env python3
# (C) 2022-26: Hans Georg Schaathun <georg@schaathun.net> 

"""
Post-processing functions for images.
"""

import numpy as np
import cv2
import argparse
import matplotlib.pyplot as plt

def imshow(im,title=None):
    plt.imshow(im,cmap="grey", vmin=0, vmax=255)
    if title is not None:
        plt.title( title )
    plt.axis( "off" )

def showImages(ims,size=(1,3),titles=None):
    (x,y) = size
    fig = plt.figure(figsize=(5*y, 5*x))
    fig.tight_layout(pad=0.0)
    for (i,(im,t)) in enumerate(zip(ims,titles)):
        fig.add_subplot(x, y, i+1)
        imshow(im,t)

def imageCompare(im1,im2,title1=None,title2=None):
    showImages( [ im1, imageDiff(im1,im2), im2 ]
               , size=(1,3)
               , titles=[ title1, "Difference", title2 ] )

def imageCoordinate( pt, im ):
    nrows, ncols = im.shape[:2]
    (x,y) = pt
    return (  round(x + ncols/2), round(nrows/2 - y) )

def annotateCircle(im,pt,radius,colour=(0,0,255)):
    """
    Mark a point on an image.
    This is crude and should be extended with different shapes as
    well as text.
    """
    if len(im.shape) == 2:
        im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
    pt = imageCoordinate( pt, im )
    print( "Annotation at", pt, "colour", colour )
    im = cv2.circle(im,center=pt,radius=round(radius),color=colour, thickness=1)
    return im
def annotatePoint(im,pt,colour=(0,0,255)):
    """
    Mark a point on an image.
    This is crude and should be extended with different shapes as
    well as text.
    """
    if len(im.shape) == 2:
        im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
    r = 4
    pt = imageCoordinate( pt, im )
    print( "Annotation at", pt, "colour", colour )
    im = cv2.circle(im,center=pt,radius=r,color=colour, thickness=1)
    im = cv2.circle(im,center=pt,radius=1,color=colour, thickness=-1)
    return im

def centreImage(im):
  """
  Shift an image so that the centre of luminence is the centre of the image.

  Input is the image `im` as a numpy array.

  The return value `(centred,(x,y))` consists of the new, shifted
  image `centred` and the co-ordinates `(x,y)` of the ce3ntre of 
  luminence in the original image, written as normal planar co-ordinatres
  where the x-axis points right and the y-axis points up.
  """

  if len(im.shape) > 2:
     grey = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
  else:
      grey = im
  grey = grey.astype(np.float64)
  m,n = grey.shape
  s = grey.sum()

  if s == 0: 
      centred = im
      pt = (0,0)
  else:
      xcol = np.array(range(m))[:,np.newaxis]
      yrow = np.array(range(n))[np.newaxis,:]
      xs = xcol*grey
      ys = yrow*grey
      xm = xs.sum()/s - m/2
      ym = ys.sum()/s - n/2
      pt = (ym,-xm)
      centred = translateImage(im,pt)

  return (centred,pt)

def translateImage(im,pt):
    (ym,xm) = pt
    R = np.float32( [ [ 1, 0, -ym ], [ 0, 1, xm ] ] )
    if len(im.shape) > 2:
        m,n,_ = im.shape
    else:
        m,n = im.shape
    return cv2.warpAffine(im,R,(n,m))

def crop(im,cropsize=256,verbose=1):
    if verbose: print( f"[crop] cropsize={cropsize}" )
    (m,n) = im.shape[:2]
    if cropsize < min(m,n):
        assert m == n
        c = (m-cropsize)/2
        c1 = int(np.floor(c))
        c2 = int(np.ceil(c))
        if len(im.shape) == 2:
            im = im[c1:-c2,c1:-c2]
        else:
            im = im[c1:-c2,c1:-c2,:]
        assert cropsize == im.shape[0]
        assert cropsize == im.shape[1]
    return im

def drawAxes(im):
  m,n = im.shape[:2]
  if m == 0:
      raise Exception( "Image has zero height." )
  if n == 0:
      raise Exception( "Image has zero width." )
  im[int(round(m/2)),:] = 127
  im[:,(round(n/2))] = 127
  return im

if __name__ == "__main__":
    parser = argparse.ArgumentParser( prog = 'Test Image Centring')
    parser.add_argument('-i', '--infile', default="test.png", help="Input file")
    parser.add_argument('-o', '--oldversion', default="test-old.png", help="Output file using old version")
    parser.add_argument('-n', '--newversion', default="test-new.png", help="Output file using new version")
    parser.add_argument('-R', '--withaxes', default="test-orig.png", help="Output for original image with axes")
    args = parser.parse_args()
    im = cv2.imread( args.infile )
    im1 = centreImage(im,False)[0]
    im2 = centreImage(im,True)[0]
    drawAxes(im)
    drawAxes(im1)
    drawAxes(im2)
    cv2.imwrite( args.oldversion, im1 )
    cv2.imwrite( args.newversion, im2 )
    cv2.imwrite( args.withaxes, im )

def imageDiff(im1,im2):
    return ( (im1.astype(float) - im2.astype(float) + 256)/2 ).astype(np.uint8)

