import numpy

try:
    print "Attempting to import scipy.  If you experience a bus error at this step, it is likely because of a bad scipy install"
    import scipy
    import scipy.fftpack
    fft2 = scipy.fftpack.fft2
    ifft2 = scipy.fftpack.ifft2
except ImportError:
    fft2 = numpy.fft.fft2
    ifft2 = numpy.fft.ifft2

def convolve(im1,im2):
    """
    Convolve two images, assuming image 1 is the larger of the two

    Options:
    """
    shape1 = im1.shape
    shape2 = im2.shape
    newshape = numpy.array(shape1)+numpy.array(shape2)
    centerx, centery = newshape/2.
    quarter1x, quarter1y = centerx - shape1[0]/2.,centery - shape1[1]/2.
    quarter3x, quarter3y = centerx + shape1[0]/2.,centery + shape1[1]/2.
    bigim1 = numpy.zeros(newshape,dtype=numpy.float64)
    bigim2 = numpy.zeros(newshape,dtype=numpy.float64)
    bigim1[:im1.shape[0],:im1.shape[1]] = im1
    bigim2[:im2.shape[0],:im2.shape[1]] = im2 
    imfft1 = fft2(bigim1)
    imfft2 = fft2(bigim2)
    fftmult = imfft1*imfft2

    rifft = (ifft2( fftmult )).real
    result = rifft[ quarter1x:quarter3x, quarter1y:quarter3y ] 
    return result

def smooth(image,kernelwidth=3,kerneltype='gaussian'):
    """
    Returns a smoothed image using a gaussian, boxcar, or tophat kernel

    Options: 
    kerneltype - gaussian, boxcar, or tophat.  
        For a gaussian, uses a gaussian with sigma = kernelwidth (in pixels) out to 9-sigma
        A boxcar is a kernelwidth x kernelwidth square 
        A tophat is a flat circle with radius = kernelwidth
    """

    if kerneltype == 'gaussian':
        gp = 9 # gaussian precision in n_sigma
        xx,yy = numpy.indices([numpy.ceil(kernelwidth*gp),numpy.ceil(kernelwidth*gp)])
        rr = numpy.sqrt((xx-kernelwidth*gp/2.)**2+(yy-kernelwidth*gp/2.)**2)
        kernel = numpy.exp(-(rr**2)/(2*kernelwidth**2)) / (kernelwidth**2 * (2*numpy.pi))
#        if kernelwidth != numpy.round(kernelwidth):
#            print "Rounding kernel width to %i pixels" % numpy.round(kernelwidth)
#            kernelwidth = numpy.round(kernelwidth)

    if kerneltype == 'boxcar':
        print "Using boxcar kernel size %i" % numpy.ceil(kernelwidth)
        kernel = numpy.ones([numpy.ceil(kernelwidth),numpy.ceil(kernelwidth)],dtype='float64') / kernelwidth**2
    elif kerneltype == 'tophat':
        kernel = numpy.zeros(image.shape,dtype='float64')
        xx,yy = numpy.indices(image.shape)
        rr = numpy.sqrt((xx-image.shape[0]/2.)**2+(yy-image.shape[1]/2.)**2)
        kernel[rr<kernelwidth] = 1.0
        # normalize
        kernel /= kernel.sum()
    elif kerneltype == 'brickwall':
        print "Smoothing with a %f pixel brick wall filter" % kernelwidth
        xx,yy = numpy.indices(image.shape)
        rr = numpy.sqrt((xx-image.shape[0]/2.)**2+(yy-image.shape[1]/2.)**2)
        kernel = numpy.sinc(rr/kernelwidth) 
        kernel /= kernel.sum()

    bad = (image != image)
    temp = image.copy()
    temp[bad] = 0
    temp = convolve(temp,kernel)
    temp[bad] = image[bad]

    return temp
