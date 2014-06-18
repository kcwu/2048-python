# Copyright 2014 Google Inc. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from multiprocessing import *
import sys
range4 = range(4)

job_table = {}
def rotateRight(grid):
    return [[grid[r][3-c] for r in range4] for c in range4]

def move_row(row):
    out = [x for x in row if x]
    ic = oc = 0
    while out[ic:]:
        if out[ic+1:] and out[ic] == out[ic+1]:
            out[oc] = 2*out[ic]
            ic += 1
        else:
            out[oc] = out[ic]
        ic += 1
        oc += 1
    out[oc:]=[None]*(4-oc)
    return out

def move(grid, rot):
    for i in range(rot):
        grid = rotateRight(grid)
    out = map(move_row, grid)
    return out, out != grid

def eval_monotone_L(grid):
  L = 0
  for x in range4:
    m = 0
    for y in range(3):
      A = grid[x][y] or 0
      B = grid[x][y+1] or 0
      if A and A >= B:
        m += 1
        L += m ** 2 * 4
      else:
        L -= abs(A- B) * 1.5
        m = 0
  return L

def eval_monotone_LR(grid):
  return max(eval_monotone_L(grid), eval_monotone_L(rotateRight(rotateRight(grid))))

def eval_smoothness(grid):
    return -sum( min([1e8]+[abs((grid[x][y] or 2) - (grid[x+a][y+b] or 2)) for a, b in((-1,0),(0,-1),(1,0),(0,1)) if 0 <= x+a <4 and 0<=y+b<4]) for x in range4 for y in range4)

def EVAL(grid):
  return eval_monotone_LR(grid) + eval_monotone_LR(rotateRight(grid))+ eval_smoothness(grid) \
     -(16-sum(r.count(None) for r in grid))**2

def encode(grid):
    return tuple(grid[0]+grid[1]+grid[2]+grid[3])
def search_max(grid, depth, nodep):
    return max([search_min(move(grid,m)[0], depth-1, nodep) for m in range4 if move(grid,m)[1]]+[-1e8])

table = {}
def worker(jq, rq):
    while 1:
        grid, depth, nodep = jq.get()

        table.clear()
        rq.put((
            (encode(grid), depth)
            ,search_min(grid, depth, nodep)))
        

def search_min(grid, depth, nodep):
  if depth == 0:
      return EVAL(grid)

  key = encode(grid), depth
  if key in table:
    return table[key]

  scores = []
  for i in range4:
    row = grid[i]
    for j in range4:
      if not row[j]:
          score = 0
          for v, p in ((2, .9), (4, .1)):
                  row[j] = v
                  score += p * search_max(grid, depth, p*nodep)
          row[j] = None

          scores.append(score)

  b = sum(scores) / len(scores)
  table[key] = b
  return b

def gen_job3(grid, depth, nodep, jq):
  for m in range4:
    g2, moved = move(grid, m)
    key = encode(g2), depth - 1
    if moved and key not in job_table:
        job_table[key] = 1
        jq.put((g2, depth - 1, nodep))

def gen_job2(grid, depth, nodep, jq):
    for i in range4:
      row = grid[i]
      for j in range4:
        if not row[j]:

            for v, p in ((2, .9), (4, .1)):
                    row[j] = v
                    gen_job3(grid, depth, p*nodep, jq)
            row[j] = None

class AI:
    def __init__(self):
        self.mg = Manager()
        self.jq = self.mg.Queue()
        self.rq = self.mg.Queue()
        self.pp = []
        for i in range(30):
            p = Process(target=worker, args=(self.jq, self.rq))
            self.pp.append(p)
            p.start()
    def __del__(self):
        for i in range(30):
            self.jq.put(0)

    def getNextMove(self, grid):
      table.clear()
      job_table.clear()
      for m in range4:
          move(grid, m)[1] and gen_job2(move(grid,m)[0], 2, 1, self.jq)

      for i in job_table:
          key, value = self.rq.get()
          table[key] = value
      return ['up','left','down','right'][max((search_min(move(grid,m)[0],2,1),m) for m in range4 if move(grid,m)[1])[1]]

# vim:sw=4:expandtab:softtabstop=4
