#!/usr/bin/python3
# -*- coding: utf-8 -*-

from tetris_model import BOARD_DATA, Shape
import math
from datetime import datetime
import numpy as np


class TetrisAI(object):
    def __init__(self):
        self.dropDist0 = {}
        self.dropDist1 = {}

    def nextMove(self):
        t1 = datetime.now()
        if BOARD_DATA.currentShape == Shape.shapeNone:
            return None

        currentDirection = BOARD_DATA.currentDirection
        currentY = BOARD_DATA.currentY
        _, _, minY, _ = BOARD_DATA.nextShape.getBoundingOffsets(0)
        nextY = -minY

        # print("=======")
        strategy = None
        if BOARD_DATA.currentShape.shape in (Shape.shapeI, Shape.shapeZ, Shape.shapeS):
            d0Range = (0, 1)
        elif BOARD_DATA.currentShape.shape == Shape.shapeO:
            d0Range = (0,)
        else:
            d0Range = (0, 1, 2, 3)

        if BOARD_DATA.nextShape.shape in (Shape.shapeI, Shape.shapeZ, Shape.shapeS):
            d1Range = (0, 1)
        elif BOARD_DATA.nextShape.shape == Shape.shapeO:
            d1Range = (0,)
        else:
            d1Range = (0, 1, 2, 3)

        for d0 in d0Range:
            minX, maxX, _, _ = BOARD_DATA.currentShape.getBoundingOffsets(d0)
            for x0 in range(-minX, BOARD_DATA.width - maxX):
                board = self.calcStep1Board(d0, x0)
                for d1 in d1Range:
                    minX, maxX, _, _ = BOARD_DATA.nextShape.getBoundingOffsets(d1)
                    for x1 in range(-minX, BOARD_DATA.width - maxX):
                        score = self.calculateScore(np.copy(board), d0, x0, d1, x1)
                        if not strategy or strategy[2] < score:
                            strategy = (d0, x0, score)
        print(datetime.now() - t1)
        return strategy

    # def calcDropDist(self, data, shape, direction, x0):
    #     res = []
    #     for x, y in shape.getCoords(direction, x0, 0):
    #         yy = 0
    #         while yy + y < BOARD_DATA.height and (yy + y < 0 or data[(y + yy), x] == Shape.shapeNone):
    #             yy += 1
    #         yy -= 1
    #         res.append[yy]
    #     return res

    def calcStep1Board(self, d0, x0):
        board = np.array(BOARD_DATA.getData()).reshape((BOARD_DATA.height, BOARD_DATA.width))
        self.dropDown(board, BOARD_DATA.currentShape, d0, x0)
        return board

    def dropDown(self, data, shape, direction, x0):
        dy = BOARD_DATA.height - 1
        for x, y in shape.getCoords(direction, x0, 0):
            yy = 0
            while yy + y < BOARD_DATA.height and (yy + y < 0 or data[(y + yy), x] == Shape.shapeNone):
                yy += 1
            yy -= 1
            if yy < dy:
                dy = yy
        for x, y in shape.getCoords(direction, x0, 0):
            data[(y + dy), x] = shape.shape

    def calculateScore(self, step1Board, d0, x0, d1, x1):
        # print("calculateScore")
        t1 = datetime.now()
        width = BOARD_DATA.width
        height = BOARD_DATA.height

        self.dropDown(step1Board, BOARD_DATA.nextShape, d1, x1)
        # print(datetime.now() - t1)

        # Term 2: max height
        # Term 3: vertical holes
        # Term 5: roof roughness
        # maxHeight = 0
        # roofY = [0] * width
        # vHoles, vBlocks = 0, 0
        # for x in range(width):
        #     vHoleFlag = False
        #     tmpHoles, tmpBlocks = 0, 0
        #     for y in range(height):
        #         if step1Board[y, x] != Shape.shapeNone:
        #             if not vHoleFlag:
        #                 roofY[x] = height - y
        #                 if height - y > maxHeight:
        #                     maxHeight = height - y
        #             else:
        #                 tmpBlocks += 1
        #             vHoleFlag = True
        #         else:
        #             if vHoleFlag:
        #                 tmpHoles += 1
        #     if tmpHoles > 0:
        #         vBlocks += tmpBlocks
        #     vHoles += tmpHoles
        # print(datetime.now() - t1)

        # Term 1: lines to be removed
        fullLines, nearFullLines = 0, 0
        roofY = [0] * width
        holeCandidates = [0] * width
        holeConfirm = [0] * width
        vHoles, vBlocks = 0, 0
        for y in range(height - 1, -1, -1):
            hasHole = False
            hasBlock = False
            for x in range(width):
                if step1Board[y, x] == Shape.shapeNone:
                    hasHole = True
                    holeCandidates[x] += 1
                else:
                    hasBlock = True
                    roofY[x] = height - y
                    if holeCandidates[x] > 0:
                        holeConfirm[x] += holeCandidates[x]
                        holeCandidates[x] = 0
                    if holeConfirm[x] > 0:
                        vBlocks += 1
            if not hasHole and hasBlock:
                fullLines += 1
        vHoles = sum([x ** .7 for x in holeConfirm])
        maxHeight = max(roofY) - fullLines
        # print(datetime.now() - t1)

        roofDy = [roofY[i] - roofY[i+1] for i in range(len(roofY) - 1)]

        if len(roofY) <= 0:
            stdY = 0
        else:
            stdY = math.sqrt(sum([y ** 2 for y in roofY]) / len(roofY) - (sum(roofY) / len(roofY)) ** 2)
        if len(roofDy) <= 0:
            stdDY = 0
        else:
            stdDY = math.sqrt(sum([y ** 2 for y in roofDy]) / len(roofDy) - (sum(roofDy) / len(roofDy)) ** 2)

        absDy = sum([abs(x) for x in roofDy])
        # print(datetime.now() - t1)

        score = fullLines * 1.8 - vHoles * 1.0 - vBlocks * 0.5 - maxHeight ** 2 * 0.02 \
            - stdY * 0.0 - stdDY * 0.1 - absDy * 0.1
        # print(score, fullLines, vHoles, vBlocks, maxHeight, stdY, stdDY, absDy, roofY, d0, x0, d1, x1)
        return score


TETRIS_AI = TetrisAI()

