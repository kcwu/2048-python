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

class AI(object):
    def __init__(self):
        self.total_node = 0
        self.total_time = 0
        self.eval_count = 0
        self.table = {}
        self.move_table = {}
        self.move_table_r = {}
        self.idx_to_row = []
        self.row_to_idx = {}
        self.build_move_table()

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
            return tmp
        if rot == 1:
            pass
        elif rot == 0:
            grid = self.rotateRight(grid)
        elif rot == 3:
            grid = self.flip(grid)
        elif rot == 2:
            grid = self.rotateLeft(grid)

        out = [
                self.move_table[grid[0]],
                self.move_table[grid[1]],
                self.move_table[grid[2]],
                self.move_table[grid[3]],
                ]
        if rot == 0:
            out = self.rotateLeft(out)
        elif rot == 3:
            out = self.flip(out)
        elif rot == 2:
            out = self.rotateRight(out)

        return out

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

    def search_drop_and_move(self, grid, depth):
        if depth == 0:
            return self.eval(grid)

        key = self.encode(grid), depth
        if key in self.table:
            return self.table[key]

        score_keeper = [[{},{},{},{}], [{},{},{},{}], [{},{},{},{}], [{},{},{},{}]]
        for direction in range4:
            moved = [0]*4 # TODO
            is_moved = [0]*4
            num_blank = 0
            for i in range4:
                moved[i] = self.move_table[grid[i]]
                is_moved[i] = moved[i] != grid[i]
            total_can_move = is_moved.count(True)

            for moving in range4:
                row = grid[moving]
                other_can_move = total_can_move - (is_moved[moving] and 1)

                x = 0
                while x < 4:
                    # skip non-blank
                    if row[x] is not None:
                        x += 1
                        continue

                    # found first blank now
                    for v, p in ((2, 0.9), (4, 0.1)):
                        drop_row = row[:x] + (v,) + row[x+1:]
                        next_row = self.move_table[drop_row]
                        this_can_move = drop_row != next_row
                        next_grid = moved[:moving] + [next_row] + moved[moving+1:]

                        if p not in score_keeper[moving][x]:
                            score_keeper[moving][x][p] = [-INF]
                        if not (this_can_move or other_can_move) and (x == 3 or row[x+1] is not None):
                            continue
                        score = self.search_drop_and_move(next_grid, depth-1)
                        if this_can_move or other_can_move:
                            score_keeper[moving][x][p].append(score)
                        x2 = x + 1
                        while x2 < 4 and row[x2] is None:
                            if p not in score_keeper[moving][x2]:
                                score_keeper[moving][x2][p] = []
                            score_keeper[moving][x2][p].append(score)
                            x2 += 1

                        
                    # next round
                    while x < 4 and row[x] is None:
                        x += 1

            grid = self.rotateRight(grid)
            score_keeper = self.rotateRight(score_keeper)

        scores = []
        for x in range4:
            for y in range4:
                cell = score_keeper[x][y]
                if not cell:
                    continue
                cell_score = 0
                for p, vs in cell.items():
                    if vs:
                        score = max(vs)
                    else:
                        score = -INF
                    cell_score += score * p
                scores.append(cell_score)

        if scores:
            avg_score = sum(scores) / len(scores)
        else:
            avg_score = -INF


        self.table[key] = avg_score
        return avg_score

    def search_max(self, grid, depth, moves):
      best_score = -INF
      for m in moves:
        g2 = self.move(grid, m)
        if g2 == grid:
          continue
        score = self.search_min(g2, depth - 1)
        #print 'search_max', m, score
        if score > best_score:
          best_score = score


      return best_score

    def search_min(self, grid, depth):
      if depth == 0:
        return self.eval(grid)

      key = self.encode(grid), depth
      if key in self.table:
        return self.table[key]

      scores = []
      for i in range4:
        for j in range4:
          if grid[i][j] is not None:
            continue

          tmp = list(grid[i])
          tmp[j] = 2
          grid[i] = tuple(tmp)
          s2 = self.search_max(grid, depth, moves)
          tmp[j] = 4
          grid[i] = tuple(tmp)
          s4 = self.search_max(grid, depth, moves)
          tmp[j] = None
          grid[i] = tuple(tmp)

          score = s2 * 0.9 + s4 * 0.1
          scores.append(score)
      if scores:
          b = sum(scores) / len(scores)
      else:
          assert 0
          b = INF

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
      grid = map(tuple, grid)
      for m in moves:
        #print 'move', m
        g2 = self.move(grid, m)
        if g2 == grid:
          continue
        #print grid
        #print g2
        score = s1 = self.search_min(g2, 3-1)
        #score = s2 = self.search_drop_and_move(g2, 3-1)

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


# vim:sw=4:expandtab:softtabstop=4
