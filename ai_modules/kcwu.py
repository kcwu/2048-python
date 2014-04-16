#!/usr/bin/env python
import time
import random
import math
import array

KEY_LEFT = 'left'
KEY_UP = 'up'
KEY_RIGHT = 'right'
KEY_DOWN = 'down'

INF = 100000000

moves = [KEY_DOWN, KEY_LEFT, KEY_UP, KEY_RIGHT]
moves_LR = [ KEY_LEFT, KEY_RIGHT ]
moves_UD = [ KEY_UP, KEY_DOWN ]
range4 = range(4)
range3 = range(3)

to_idx = dict((2**i, i) for i in range(16))
to_idx[None] = 0


def clone(grid):
    return [row[:] for row in grid]

class AI(object):
    def __init__(self):
        self.total_node = 0
        self.total_time = 0
        self.eval_count = 0
        self.table = {}

    def emptyGrid(self):
        return [[None,None,None,None],[None,None,None,None],
                [None,None,None,None],[None,None,None,None]]

    def rotateLeft(self, grid):
        g = grid
        return [
                [g[3][0], g[2][0], g[1][0], g[0][0]],
                [g[3][1], g[2][1], g[1][1], g[0][1]],
                [g[3][2], g[2][2], g[1][2], g[0][2]],
                [g[3][3], g[2][3], g[1][3], g[0][3]],
                ]

    def rotateRight(self, grid):
        g = grid
        return [
                [g[0][3], g[1][3], g[2][3], g[3][3]],
                [g[0][2], g[1][2], g[2][2], g[3][2]],
                [g[0][1], g[1][1], g[2][1], g[3][1]],
                [g[0][0], g[1][0], g[2][0], g[3][0]],
                ]

    def flip(self, grid):
        return [grid[3][::-1], grid[2][::-1], grid[1][::-1], grid[0][::-1]]

    def encode(self, grid):
        a = array.array('h')
        for x in range4:
            for y in range4:
                if grid[x][y]:
                    a.append(grid[x][y])
                else:
                    a.append(0)
        return a.tostring()

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

        if rot == 3:
            grid = self.rotateRight(grid)
        elif rot == 2:
            grid = self.flip(grid)
        else:
            for i in xrange(rot):
                grid = self.rotateLeft(grid)

        for r in range4:
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
                    out[oc][r] = out[ic][r]
                    oc += 1
                    break
                if out[ic][r] == out[ic+1][r]:
                    out[oc][r] = 2*out[ic][r]
                    ic += 1
                else:
                    out[oc][r] = out[ic][r]
                ic += 1
                oc += 1
            while oc < 4:
                out[oc][r] = None
                oc += 1

        if rot == 3:
            out = self.rotateLeft(out)
        elif rot == 2:
            out = self.flip(out)
        else:
            for i in xrange(rot):
                out = self.rotateRight(out)


        return out

    def show(self, grid):
        for x in range(4):
            for y in range(4):
                if grid[x][y]:
                    print '%4d' % grid[x][y],
                else:
                    print '   .',
            print


    def canMove(self, grid, direction):
      return grid != self.move(grid, direction)

    def eval_monotone(self, grid):
      L = R = U = D = 0
      LR = UD = 0
      for x in range4:
        m = 0
        for y in range3:
          if grid[x][y] and grid[x][y] >= grid[x][y+1]:
            m += 1
            # 26090
            #L += m
            # 29281
            L += m ** 2
          else:
            # 20585
            #L -= abs(to_idx[grid[x][y]] - to_idx[grid[x][y+1]]) ** 2
            # 26090
            L -= abs((grid[x][y] or 0)- (grid[x][y+1] or 0)) * 1.5
            m = 0

        m = 0
        for y in range3:
          if grid[x][y] <= grid[x][y+1] and grid[x][y+1]:
            m += 1
            R += m ** 2
          else:
            #R -= abs(to_idx[grid[x][y]] - to_idx[grid[x][y+1]]) ** 2
            R -= abs((grid[x][y] or 0)- (grid[x][y+1] or 0)) * 1.5
            m = 0

      LR += max(L, R)
      L = R = 0

      for y in range4:
        m = 0
        for x in range3:
          if grid[x][y] and grid[x][y] >= grid[x+1][y]:
            m += 1
            U += m ** 2
          else:
            #U -= abs(to_idx[grid[x][y]] - to_idx[grid[x+1][y]]) ** 2
            U -= abs((grid[x][y] or 0)- (grid[x+1][y] or 0)) * 1.5
            m = 0

        m = 0
        for x in range3:
          if grid[x][y] <= grid[x+1][y] and grid[x+1][y]:
            m += 1
            D += m ** 2
          else:
            #D -= abs(to_idx[grid[x][y]] - to_idx[grid[x+1][y]]) ** 2
            D -= abs((grid[x][y] or 0)- (grid[x+1][y] or 0)) * 1.5
            m = 0

      UD += max(U, D)
      U = D = 0

      return LR + UD

    def eval_smoothness(self, grid):
        score_smooth = 0
        for x in range4:
            for y in range4:
                s = INF
                if x > 0: s = min(s, abs((grid[x][y] or 2) - (grid[x-1][y] or 2)))
                if y > 0: s = min(s, abs((grid[x][y] or 2) - (grid[x][y-1] or 2)))
                if x < 3: s = min(s, abs((grid[x][y] or 2) - (grid[x+1][y] or 2)))
                if y < 3: s = min(s, abs((grid[x][y] or 2) - (grid[x][y+1] or 2)))
                score_smooth -= s
        return score_smooth

    def eval_free(self, grid):
      free = 0
      for i in range4:
        for j in range4:
          if grid[i][j] is None:
            free += 1
      return -(16-free)**2

    def eval(self, grid):
      key = self.encode(grid)
      if key in self.table:
        return self.table[key]

      self.eval_count += 1

      score_monotone = self.eval_monotone(grid)
      score_smooth = self.eval_smoothness(grid)
      score_free = self.eval_free(grid)


      score = 0
      score += score_smooth
      score += score_monotone
      score += score_free

      self.table[key] = score
      return score

    def search_max(self, grid, depth, a, b, moves):
      for m in moves:
        g2 = self.move(grid, m)
        if g2 == grid:
          continue
        score = self.search_min(g2, depth - 1, a, b)
        #print 'search_max', m, score
        if score >= b:
          return b
        if score > a:
          a = score


      return a

    def search_min(self, grid, depth, a, b):
      if depth == 0:
        return self.eval(grid)

      key = self.encode(grid), depth
      if key in self.table:
        return self.table[key]

      #g = clone(grid)
      #assert g == grid
      #print '=' * 30
      #self.show(grid)
      for i in range4:
        for j in range4:
          if grid[i][j] is not None:
            continue

          for v in (2, 4):
            grid[i][j] = v
            score = self.search_max(grid, depth, a, b, moves)
            if score <= a:
              grid[i][j] = None
              return a
            if score < b:
              b = score

          grid[i][j] = None

      self.table[key] = b
      return b

    def reset(self):
      self.eval_count = 0
      self.table = {}

    def getNextMove(self, grid):
      best_score = -INF
      best_move = random.choice(moves)
      self.reset()

      t0 = time.time()
      for m in moves:
        #print 'move', m
        g2 = self.move(grid, m)
        if g2 == grid:
          continue
        #print grid
        #print g2
        score = self.search_min(g2, 3-1, -INF, INF)

        #print score, m
        if score > best_score:
          best_score = score
          best_move = m
        #print '-'
      t1 = time.time()

      self.total_time += t1 - t0
      self.total_node += self.eval_count
      print 't=%.2fs, node=%d, total_node=%d, %fnps' % (
          t1-t0, self.eval_count, self.total_node, self.total_node/self.total_time)

      return best_move


# vim:sw=4:expandtab
