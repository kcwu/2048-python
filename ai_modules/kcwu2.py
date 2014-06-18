#!/usr/bin/env python
# Copyright 2014 Google Inc. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import time
import random
import math
import array
import multiprocessing

search_depth = 4
KEY_LEFT = 'left'
KEY_UP = 'up'
KEY_RIGHT = 'right'
KEY_DOWN = 'down'

INF = 100000000

moves = [KEY_DOWN, KEY_LEFT, KEY_UP, KEY_RIGHT]
range4 = range(4)
range3 = range(3)

to_idx = dict((2**i, i) for i in range(16))
to_idx[None] = 0

def move_row(row):
    out = [None, None, None, None]
    oc = 0
    ic = 0
    while ic < 4:
        if row[ic] is None:
            ic += 1
            continue
        out[oc] = row[ic]
        oc += 1
        ic += 1

    ic = 0
    oc = 0
    while ic < 4:
        if out[ic] is None:
            break
        if ic == 3:
            out[oc] = out[ic]
            oc += 1
            break
        if out[ic] == out[ic+1]:
            out[oc] = 2*out[ic]
            ic += 1
        else:
            out[oc] = out[ic]
        ic += 1
        oc += 1
    while oc < 4:
        out[oc] = None
        oc += 1
    return out

def worker(job_q, reply_q):
    instance = AI(False)
    reply_q.put('ready')

    while True:
        try:
            cmd, job = job_q.get()
            if cmd == 'quit':
                break
            grid, depth, nodep = job
        except EOFError:
            break

        key = instance.encode(grid), depth
        value = instance.search_min(grid, depth, nodep)
        reply_q.put((key, value))

        instance.table = {}


class AI(object):
    def __init__(self, root=True):
        self.parallel = 30
        self.processes = []

        self.total_node = 0
        self.total_eval = 0
        self.total_time = 0
        self.eval_count = 0
        self.node_count = 0
        self.table = {}
        self.move_table = {}
        self.move_table_r = {}
        self.idx_to_row = []
        self.row_to_idx = {}
        self.build_move_table()
        self.build_eval_monotone_table()


        if root:
            self.parallel_start()

    def build_eval_monotone_table(self):
        self.eval_monotine_table = {}
        for idx, row in enumerate(self.idx_to_row):
            L = R = 0
            m = 0
            for y in range3:
              if row[y] and row[y] >= row[y+1]:
                m += 1
                L += m ** 2 * 4
              else:
                L -= abs((row[y] or 0)- (row[y+1] or 0)) * 1.5
                m = 0

            m = 0
            for y in range3:
              if row[y] <= row[y+1] and row[y+1]:
                m += 1
                R += m ** 2 * 4
              else:
                R -= abs((row[y] or 0)- (row[y+1] or 0)) * 1.5
                m = 0
            self.eval_monotine_table[row] = L, R



    def build_move_table(self):
        # assume max cell is 32768
        max_cell = 2**15
        values = [None] + [2**x for x in range(1, 16)]
        assert len(values) == 16
        idx = 0
        for a in values:
            for b in values:
                for c in values:
                    for d in values:
                        row = a, b, c, d
                        self.idx_to_row.append(row)
                        self.row_to_idx[row] = idx
                        idx += 1

        for idx, row in enumerate(self.idx_to_row):
            row_moved = tuple(move_row(row))
            if max(row_moved) > max_cell:
                self.move_table[idx] = -1
            else:
                self.move_table[idx] = self.row_to_idx[row_moved]

            self.move_table[row] = row_moved
            self.move_table_r[row] = tuple(move_row(row[::-1])[::-1])

    def rotateLeft(self, grid):
        g = grid
        return [
                (g[3][0], g[2][0], g[1][0], g[0][0]),
                (g[3][1], g[2][1], g[1][1], g[0][1]),
                (g[3][2], g[2][2], g[1][2], g[0][2]),
                (g[3][3], g[2][3], g[1][3], g[0][3]),
                ]

    def rotateRight(self, grid):
        g = grid
        return [
                (g[0][3], g[1][3], g[2][3], g[3][3]),
                (g[0][2], g[1][2], g[2][2], g[3][2]),
                (g[0][1], g[1][1], g[2][1], g[3][1]),
                (g[0][0], g[1][0], g[2][0], g[3][0]),
                ]

    def flip(self, grid):
        return [grid[3][::-1], grid[2][::-1], grid[1][::-1], grid[0][::-1]]

    def encode(self, grid):
        return grid[0]+grid[1]+grid[2]+grid[3]

    def move(self, grid, direction):
        if direction == KEY_UP:
            rot = 1
        elif direction == KEY_RIGHT:
            rot = 2
        elif direction == KEY_DOWN:
            rot = 3
        else:
            rot = 0

        if rot == 3:
            tmp = [
                self.move_table_r[grid[0]],
                self.move_table_r[grid[1]],
                self.move_table_r[grid[2]],
                self.move_table_r[grid[3]],
                ]
            return tmp, (tmp != grid)
        if rot == 0:
            grid = self.rotateRight(grid)
        elif rot == 2:
            grid = self.rotateLeft(grid)

        out = [
                self.move_table[grid[0]],
                self.move_table[grid[1]],
                self.move_table[grid[2]],
                self.move_table[grid[3]],
                ]

        return out, (out != grid)

    def show(self, grid):
        for y in range(4):
            for x in range(4):
                if grid[x][y]:
                    print '%4d' % grid[x][y],
                else:
                    print '   .',
            print


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
            L += m ** 2 * 4
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
            R += m ** 2 * 4
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
            U += m ** 2 * 4
          else:
            #U -= abs(to_idx[grid[x][y]] - to_idx[grid[x+1][y]]) ** 2
            U -= abs((grid[x][y] or 0)- (grid[x+1][y] or 0)) * 1.5
            m = 0

        m = 0
        for x in range3:
          if grid[x][y] <= grid[x+1][y] and grid[x+1][y]:
            m += 1
            D += m ** 2 * 4
          else:
            #D -= abs(to_idx[grid[x][y]] - to_idx[grid[x+1][y]]) ** 2
            D -= abs((grid[x][y] or 0)- (grid[x+1][y] or 0)) * 1.5
            m = 0

      UD += max(U, D)

      return LR + UD

    def eval_monotone(self, grid):
        L = R = U = D = 0
        LR = UD = 0
        for x in range4:
            Lt, Rt = self.eval_monotine_table[grid[x]]
            L += Lt
            R += Rt
        LR = max(L, R)

        grid = self.rotateRight(grid)
        for x in range4:
            Ut, Dt = self.eval_monotine_table[grid[x]]
            U += Ut
            D += Dt
        UD = max(U, D)
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

    def eval_smoothness(self, grid):
        a00, a01, a02, a03 = grid[0]
        a10, a11, a12, a13 = grid[1]
        a20, a21, a22, a23 = grid[2]
        a30, a31, a32, a33 = grid[3]

        a00 = a00 or 2
        a01 = a01 or 2
        a02 = a02 or 2
        a03 = a03 or 2
        a10 = a10 or 2
        a11 = a11 or 2
        a12 = a12 or 2
        a13 = a13 or 2
        a20 = a20 or 2
        a21 = a21 or 2
        a22 = a22 or 2
        a23 = a23 or 2
        a30 = a30 or 2
        a31 = a31 or 2
        a32 = a32 or 2
        a33 = a33 or 2

        score_smooth = 0
        score_smooth -= min(abs(a00-a01), abs(a00-a10))
        score_smooth -= min([abs(a01-a00), abs(a01-a11), abs(a01-a02)])
        score_smooth -= min([abs(a02-a01), abs(a02-a12), abs(a02-a03)])
        score_smooth -= min(abs(a03-a02), abs(a03-a13))

        score_smooth -= min([abs(a10-a00), abs(a10-a11), abs(a10-a20)])
        score_smooth -= min([abs(a11-a01), abs(a11-a10), abs(a11-a12), abs(a11-a21)])
        score_smooth -= min([abs(a12-a02), abs(a12-a11), abs(a12-a13), abs(a12-a22)])
        score_smooth -= min([abs(a13-a03), abs(a13-a12), abs(a13-a23)])

        score_smooth -= min([abs(a20-a10), abs(a20-a21), abs(a20-a30)])
        score_smooth -= min([abs(a21-a11), abs(a21-a20), abs(a21-a22), abs(a21-a31)])
        score_smooth -= min([abs(a22-a12), abs(a22-a21), abs(a22-a23), abs(a22-a32)])
        score_smooth -= min([abs(a23-a13), abs(a23-a22), abs(a23-a33)])

        score_smooth -= min(abs(a30-a31), abs(a30-a20))
        score_smooth -= min([abs(a31-a30), abs(a31-a21), abs(a31-a32)])
        score_smooth -= min([abs(a32-a31), abs(a32-a22), abs(a32-a33)])
        score_smooth -= min(abs(a33-a32), abs(a33-a23))

        return score_smooth


    def eval_free(self, grid):
        free = grid[0].count(None) + grid[1].count(None) + grid[2].count(None) + grid[3].count(None)
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

    def search_max(self, grid, depth, nodep):
      key = self.encode(grid), depth, 1
      if key in self.table:
        return self.table[key]

      best_score = -INF
      self.node_count += 1
      for m in moves:
        g2, moved = self.move(grid, m)
        if not moved:
          continue
        score = self.search_min(g2, depth - 1, nodep)
        #print 'search_max', m, score
        if score > best_score:
          best_score = score

      self.table[key] = best_score
      return best_score

    def search_min(self, grid, depth, nodep):
      if depth == 0:
        return self.eval(grid)
      self.node_count += 1

      key = self.encode(grid), depth
      if key in self.table:
        return self.table[key]

      blank_count = grid[0].count(None) + grid[1].count(None) + grid[2].count(None) + grid[3].count(None)

      scores = []
      for i in range4:
        for j in range4:
          if grid[i][j] is not None:
            continue

          tmp = list(grid[i])
          score = 0
          all_p = 0
          for v, p in ((2, 0.9), (4, 0.1)):
              if blank_count > 4 and p * nodep*0.9 < 0.01: # XXX hardcode for search_depth
                  continue
              tmp[j] = v
              grid[i] = tuple(tmp)
              score += p * self.search_max(grid, depth, p*nodep)
              all_p += p
          tmp[j] = None
          grid[i] = tuple(tmp)

          if all_p == 0:
              score = self.eval(grid)
          else:
              score /= all_p
          scores.append(score)

      b = sum(scores) / len(scores)
      self.table[key] = b
      return b

    def reset(self):
      self.eval_count = 0
      self.node_count = 0
      self.table = {}

    def gen_job3(self, grid, depth, nodep):
      for m in moves:
        g2, moved = self.move(grid, m)
        if not moved:
          continue
        key = self.encode(g2), depth - 1
        job = g2, depth - 1, nodep
        if key in self.job_table:
            continue
        self.job_table.add(key)
        yield job

    def gen_job2(self, grid, depth, nodep):
        blank_count = grid[0].count(None) + grid[1].count(None) + grid[2].count(None) + grid[3].count(None)


        scores = []
        for i in range4:
          for j in range4:
            if grid[i][j] is not None:
              continue

            tmp = list(grid[i])
            for v, p in ((2, 0.9), (4, 0.1)):
                if blank_count > 4 and p * nodep*0.9 < 0.01: # XXX hardcode for search_depth
                    continue
                tmp[j] = v
                grid[i] = tuple(tmp)
                for job in self.gen_job3(grid, depth, p*nodep):
                    yield job
            tmp[j] = None
            grid[i] = tuple(tmp)

    def gen_job(self, grid):
        for m in moves:
            g2, moved = self.move(grid, m)
            if not moved:
                continue
            for job in self.gen_job2(g2, search_depth-1, 1.0):
                yield job

    def parallel_start(self):
        if self.processes:
            return

        self.manager = multiprocessing.Manager()
        self.job_q = self.manager.Queue()
        self.reply_q = self.manager.Queue()
        self.processes = []
        for i in range(self.parallel):
            p = multiprocessing.Process(target=worker, args=(self.job_q, self.reply_q))
            self.processes.append(p)
            p.start()

        # wait all ready
        for i in range(self.parallel):
            self.reply_q.get()
            print 'ready', i

    def parallel_stop(self):
        if not self.processes:
            return
        for i in range(self.parallel):
            self.job_q.put(('quit', 0))
        for p in self.processes:
            p.join()
        self.job_q = None
        self.reply_q = None
        self.manager.shutdown()
        self.manager = None
        self.processes = []

    def parallel_run(self, grid):
        self.parallel_start()

        job_count = 0
        self.job_table = set()
        #t0 = time.time()
        for job in self.gen_job(grid):
            job_count += 1
            self.job_q.put(('job', job))
        #t1 = time.time()
        #print 'gen jobs', t1-t0

        #t0 = time.time()
        for i in range(job_count):
            key, value = self.reply_q.get()
            self.table[key] = value
        #t1 = time.time()
        #print 'get results', t1-t0

    def getNextMove(self, grid):
      best_score = -INF-1
      best_move = 'left'
      self.reset()

      t0 = time.time()
      grid = map(tuple, grid)

      self.parallel_run(grid)

      #s0 = time.time()
      for m in moves:
        #print 'move', m
        g2, moved = self.move(grid, m)
        if not moved:
          continue
        #print grid
        #print g2
        score = self.search_min(g2, search_depth-1, 1.0)

        # round to avoid the instability of floating point numbers
        score = round(score, 6)

        #print score, m
        if score > best_score:
          best_score = score
          best_move = m
        #print '-'
      t1 = time.time()
      #print 'main loop', t1-s0

      self.total_time += t1 - t0
      self.total_eval += self.eval_count
      self.total_node += self.node_count
      print 't=%.2fs, eval=%d, node=%d, total_eval=%d, total_node=%d, %fnps' % (
          t1-t0, self.eval_count, self.node_count, self.total_eval, self.total_node, (self.total_node+self.total_eval)/self.total_time)

      return best_move
    def __del__(self):
        self.parallel_stop()


# vim:sw=4:expandtab:softtabstop=4
