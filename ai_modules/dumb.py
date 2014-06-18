#!/usr/bin/env python
# Copyright 2014 Google Inc. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

seq = ['left', 'up', 'right', 'down']

class AI(object):
  def __init__(self):
    self.last = 0

  def getNextMove(self, grid):
    self.last = self.last + 1
    if self.last >= 4:
      self.last = 0
    return seq[self.last]
