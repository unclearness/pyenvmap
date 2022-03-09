from sympy import degree
from scipy.spatial.transform import Rotation
import numpy as np


def pos01toangle(s, t):
    pass


def genSampleAngle(h, w, l0=0.0, p0=0.0, p1=0.0, r=1.0):
    x, y = np.meshgrid(range(0, w), range(0, h))
    # y, x = y / (h - 1), x / (w - 1)  # TODO:
    #l = (x / (r * np.cos(p1)) + l0) * np.pi
    #p = (y / r + p0) * 2 * np.pi
    #l = np.clip(l, 0, np.pi)
    #p = np.clip(p, 0, 2 * np.pi)
    theta = x * 2 * np.pi / (w - 1)  # - np.pi
    phi = y * np.pi / (h - 1)  # - np.pi / 2
    return theta, phi


def genSampleVector(h, w, l0=0.0, p0=0.0, p1=0.0, r=1.0):
    # image coordinate to angles
    l, p = genSampleAngle(h, w, l0, p0, p1, r)
    print("l", np.min(l), np.max(l))
    print("p", np.min(p), np.max(p))
    x = r * np.cos(l) * np.sin(p)
    y = r * np.sin(l) * np.sin(p)
    z = r * np.cos(p)
    return np.stack([x, y, z], axis=-1)


def samplePixColor(src, sample_vector, l0=0.0, p0=0.0, p1=0.0, r=1.0):
    h, w, c = src.shape
    #sample_angle =  sample_vector
    #l, p = sample_angle
    x, y, z = sample_vector[..., 0], sample_vector[...,
                                                   1], sample_vector[..., 2]
    x
    p = np.arccos(z / r)
    l = np.arctan2(y, x)  # TODO
    #p[np.bitwise_and(x < 0, y >= 0)] += np.pi
    #p[np.bitwise_and(x < 0, y < 0)] -= np.pi
    #p[np.bitwise_and(x == 0, y >= 0)] = np.pi / 2
    #p[np.bitwise_and(x == 0, y < 0)] = -np.pi / 2
    print("l", np.max(l), np.min(l))
    print("p", np.max(p), np.min(p))

    #p[p < 0] += 2 * np.pi

    #p = np.mod(p, 2*np.pi)
    #p = np.clip(p, 0, 2*np.pi)

    x = r*(l / (2 * np.pi)-l0)*np.cos(p1)
    y = r*(p / (np.pi)-p0)

    print("x", np.max(x), np.min(x))
    print("y", np.max(y), np.min(y))

    x = x * (w-1)
    y = y * (h-1)

    #TODO: bilinear
    x, y = np.array(x, dtype=np.int), np.array(y, dtype=np.int)
    # TODO
    #x = np.mod(x, w-1)
    #y = np.mod(y, h-1)
    print(x.shape, y.shape, np.max(x), np.max(y))
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
    for i in range(3):
        print(np.min(v[..., i]), np.max(v[..., i]))
    norm = np.linalg.norm(v, axis=-1)
    print("norm", np.max(norm), np.min(norm))
    saveAngle("org.png", v)
    #R = np.repeat(R, (h, w))
    #print(v.shape, R.shape)
    #v = np.dot(R.T, v.T)
    #v = np.dot(v, R)
    R = Rotation.from_matrix(R)
    v = R.apply(v.reshape(-1, 3)).reshape(h, w, 3)
    saveAngle("rotated.png", v)
    #v = np.einsum('ij,ijk->ij', R, v)[..., None]
    #print(v.shape, R.shape)
    #print(v.shape, R.shape, np.linalg.norm(v, axis=-1), R)
    # print(v)

    #v = np.matmul(R, v)
    # v = np.einsum('BNi,Bi ->BN', R, v)
    dst = samplePixColor(src, v)
    return dst


def rotateByEularXYZ(src, x, y, z):
    rot = Rotation.from_euler('xyz', [x, y, z], degrees=True)
    R = rot.as_matrix()
    return rotateByMatrix(src, R)
