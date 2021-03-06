import numpy as np
import cv2
from lib import utils

class UIWarp():
    def __init__(self, npx, scale):
        self.npx = npx
        self.scale = scale
        self.img = np.zeros((npx, npx, 3), np.uint8)
        self.mask = np.zeros((npx, npx, 1), np.uint8)
        self.init_width = 24
        self.width = int(self.init_width * self.scale)
        self.points1 = []
        self.points2 = []
        self.widths  = []
        self.ims = []
        self.activeId = -1
        self.im = None

    def CropPatch(self, pnt, width):
        [x_c,y_c] = pnt
        w =  width / 2.0
        x1 = int(np.clip(x_c-w, 0, self.npx-1))
        y1 = int(np.clip(y_c-w, 0, self.npx-1))
        x2 = int(np.clip(x_c+w, 0, self.npx-1))
        y2 = int(np.clip(y_c+w, 0, self.npx-1))
        return [x1,y1,x2,y2]

    def AddPoint(self, pos, im):
        x_c = int(np.round(pos.x()/self.scale))
        y_c=  int(np.round(pos.y()/self.scale))
        pnt = (x_c, y_c)
        print('add point (%d,%d)'%pnt)
        self.points1.append(pnt)
        self.points2.append(pnt)
        self.widths.append(self.width)

        self.im = cv2.resize(im, (self.npx, self.npx))#*255).astype(np.uint8)
        self.ims.append(self.im.copy())
        self.activeId = len(self.points1) - 1
        print('set active id =%d'%self.activeId)

    # def ActivePoint(self):
    #     pnt = self.points2[self.activeId]
    #     return (pnt[0]* self.scale, pnt[1]*self.scale)

    def StartPoint(self):
        print 'start point, activeId', self.activeId
        print 'points1', self.points1
        if self.activeId >= 0 and self.points1:
            return self.points1[self.activeId]
        else:
            return None

    def update(self, pos):
        self.img = np.zeros((self.npx, self.npx, 3), np.uint8)
        self.mask = np.zeros((self.npx, self.npx, 1), np.uint8)

        print('uiWarp: update %d'%self.activeId)
        if self.activeId >= 0:
            x_c = int(np.round(pos.x()/self.scale))
            y_c=  int(np.round(pos.y()/self.scale))
            pnt = (x_c, y_c)
            self.points2[self.activeId] = pnt

        count = 0
        for pnt1, pnt2 in zip(self.points1, self.points2):
            w = int(max(1, self.width / self.scale))
            [x1,y1,x2,y2] = self.CropPatch(pnt1, w)
            im = self.ims[count]
            patch = im[y1:y2,x1:x2,:].copy()
            utils.print_numpy(patch)
            [x1,y1,x2,y2] = self.CropPatch(pnt2, w)
            self.img[y1:y2,x1:x2,:] = patch
            self.mask[y1:y2,x1:x2,:] = 255
            print('point pair %d' %count)
            count += 1
            print('point1: %d,%d'%pnt1)
            print('point2: %d,%d'%pnt2)

        utils.CVShow(self.img, 'warp input image')
        utils.CVShow(self.mask, 'warp image mask')


    def get_constraints(self):
        return self.img, self.mask

    def get_edge_constraints(self):
        img = np.zeros((self.npx, self.npx, 3), np.uint8)
        mask = np.zeros((self.npx, self.npx, 1), np.uint8)
        return img, mask


    def update_width(self, d):
        self.width = min(256, max(32, self.width + d * 4 * self.scale))
        if self.activeId >= 0:
            self.widths[self.activeId] = self.width
            print('update width %d, active id =%d'%(self.width, self.activeId))
            # self.im = cv2.resize(im, (self.npx, self.npx))
            # w = int(max(1, self.width / self.scale))
            # [x1,y1,x2,y2] = self.CropPatch(self.points1[self.activeId], w)
            # patch = self.im[x1:y1,x2:y2,:].copy()
            # self.ims[self.activeId] = patch
        return self.width

    def reset(self):
        self.activeId = -1
        self.points1 = []
        self.points2 = []
        self.widths = []
        self.ims = []
        self.width = int(self.init_width * self.scale)
        self.img = np.zeros((self.npx, self.npx, 3), np.uint8)
        self.mask = np.zeros((self.npx, self.npx, 1), np.uint8)
