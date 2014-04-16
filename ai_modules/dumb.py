#!/usr/bin/env python

seq = ['left', 'up', 'right', 'down']

class AI(object):
  def __init__(self):
    self.last = 0

  def getNextMove(self, grid):
    self.last = self.last + 1
    if self.last >= 4:
      self.last = 0
    return seq[self.last]
