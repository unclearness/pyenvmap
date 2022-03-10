from scipy.spatial.transform import Rotation
from scipy import interpolate
import numpy as np


def genSampleAngle(h, w):
    x, y = np.meshgrid(range(0, w), range(0, h))
    phi = x / (w-1) * 2 * np.pi
    # phi = (x+0.5) / w * 2 * np.pi
    theta = y / (h-1) * np.pi
    # theta = (y+0.5) / h * np.pi
    return phi, theta


def genSampleVector(h, w):
    # image coordinate to angles
    phi, theta = genSampleAngle(h, w)
    x = np.cos(phi) * np.sin(theta)
    y = np.sin(phi) * np.sin(theta)
    z = np.cos(theta)
    return np.stack([x, y, z], axis=-1)

# https://stackoverflow.com/questions/12729228/simple-efficient-bilinear-interpolation-of-images-in-numpy-and-python


def bilinear_interpolate(im, x, y):
    x = np.asarray(x)
    y = np.asarray(y)

    x0 = np.floor(x).astype(int)
    x1 = x0 + 1
    y0 = np.floor(y).astype(int)
    y1 = y0 + 1

    # x0 = np.clip(x0, 0, im.shape[1]-1)
    # x1 = np.clip(x1, 0, im.shape[1]-1)

    # Interpolation for x should be circular
    # TODO: Really correct?
    x0_ = x0
    x1_ = x1
    x0 = np.mod(x0, im.shape[1])
    x1 = np.mod(x1, im.shape[1])

    y0 = np.clip(y0, 0, im.shape[0]-1)
    y1 = np.clip(y1, 0, im.shape[0]-1)

    Ia = im[y0, x0]
    Ib = im[y1, x0]
    Ic = im[y0, x1]
    Id = im[y1, x1]

    wa = (x1_-x) * (y1-y)
    wb = (x1_-x) * (y-y0)
    wc = (x-x0_) * (y1-y)
    wd = (x-x0_) * (y-y0)

    # return (Ia.T*wa).T + (Ib.T*wb).T + (Ic.T*wc).T + (Id.T*wd).T
    return wa*Ia + wb*Ib + wc*Ic + wd*Id


def samplePixColor(src, sample_vector, bilinear=False):
    h, w, c = src.shape
    sample_vector = np.clip(sample_vector, -1, 1)
    x, y, z = sample_vector[..., 0], sample_vector[...,
                                                   1], sample_vector[..., 2]
    theta = np.arccos(z)
    phi = np.arctan2(y, x)

    theta = np.clip(theta, 0, np.pi)
    phi = np.mod(phi, 2 * np.pi)

    x = phi / (2 * np.pi)
    y = theta / np.pi

    x = x * (w - 1)
    #x = x * w - 0.5
    y = y * (h - 1)
    # y = y * h - 0.5

    # TODO: Should 3D coordinates instead of image coordinates are considered?
    if bilinear:
        dst = []
        for i in range(c):
            dst.append(bilinear_interpolate(src[..., i], x, y))
        dst = np.stack(dst, axis=-1).astype(src.dtype)
    else:
        # Nearest Neighbor
        x, y = np.array(np.round(x), dtype=np.int), np.array(
            np.round(y), dtype=np.int)
        dst = src[y, x]

    return dst


def colorizeAngle(angle):
    return ((np.clip(angle + 1.0 / 2.0, 0, 1)) * 255).astype(np.uint8)


def saveAngle(path, angle):
    color_angle = colorizeAngle(angle)
    import cv2
    cv2.imwrite(path, color_angle)


def rotateByMatrix(src, R):
    if len(src.shape) == 2:
        src = src.reshape(-1, 1)
    elif len(src.shape) != 3:
        raise Exception()
    h, w, c = src.shape
    v = genSampleVector(h, w)  # (H, W, (X,Y,Z))
    # saveAngle("org.png", v)

    R = Rotation.from_matrix(R)
    v = R.apply(v.reshape(-1, 3)).reshape(h, w, 3)
    # saveAngle("rotated.png", v)

    dst = samplePixColor(src, v)
    return dst


def rotateByEularXYZ(src, x, y, z):
    rot = Rotation.from_euler('xyz', [x, y, z], degrees=True)
    R = rot.as_matrix()
    return rotateByMatrix(src, R)
