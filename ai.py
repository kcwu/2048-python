#!/usr/bin/env python

KEY_LEFT = 'left'
KEY_UP = 'up'
KEY_RIGHT = 'right'
KEY_DOWN = 'down'

def clone(grid):
    return [row[:] for row in grid]

class AI(object):

  def __init__(self):
    self.lastMove = 0
    self.wantDown = False

  def emptyGrid(self):
    out = list()
    for x in xrange(4):
      col = list()
      for y in xrange(4):
        col.append(None)
      out.append(col)
    return out

  def rotateLeft(self, grid):
    out = self.emptyGrid()
    for c in xrange(4):
      for r in xrange(4):
        out[r][3-c] = grid[c][r]
    return out

  def rotateRight(self, grid):
    out = self.emptyGrid()
    for c in xrange(4):
      for r in xrange(4):
        out[3-r][c] = grid[c][r]
    return out


  def move(self, grid, direction):
    out = self.emptyGrid()

    if direction == KEY_UP:
      rot = 1
    elif direction == KEY_RIGHT:
      rot = 2
    elif direction == KEY_DOWN:
      rot = 3
    else:
      rot = 0

    for i in xrange(rot):
      grid = self.rotateLeft(grid)

    for r in xrange(4):
      oc = 0
      ic = 0
      while ic < 4:
        if grid[ic][r] is None:
          ic += 1
          continue
        out[oc][r] = grid[ic][r]
        oc += 1
        ic += 1

      ic = 0
      oc = 0
      while ic < 4:
        if out[ic][r] is None:
          break
        if ic == 3:
          break
        if out[ic][r] == out[ic+1][r]:
          out[oc][r] *= 2
          ic += 1
        else:
          out[oc][r] = out[ic][r]
        ic += 1
        oc += 1

    for i in xrange(rot):
      out = self.rotateRight(out)

    return out


  def canMove(self, grid, direction):
    return grid != self.move(grid, direction)

  def getNextMove(self, grid):
    if ((self.lastMove == KEY_UP and None in grid[0]) or
        (self.lastMove == KEY_LEFT and self.canMove(grid, KEY_DOWN))):
      self.wantDown = True
    elif self.lastMove == KEY_DOWN:
      self.wantDown = False
    if self.wantDown:
      seq = [KEY_DOWN, KEY_LEFT, KEY_UP, KEY_RIGHT]
    else:
      seq = [KEY_LEFT, KEY_DOWN, KEY_UP, KEY_RIGHT]
    for d in seq:
      if self.canMove(grid, d):
        self.lastMove = d
        return d
