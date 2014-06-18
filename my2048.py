#!/usr/bin/env python
# Copyright 2014 Google Inc. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import imp
import os
import sys
import time
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from telemetry.core import browser_finder
from telemetry.core import browser_options

HAS_SCOREBOARD = False
if HAS_SCOREBOARD:
  from scoreboard import ScoreBoard

KEY_CODE = {'left': 37,
            'up': 38,
            'right': 39,
            'down': 40}

ITERATION = 1

LOAD_DELAY = 5
START_DELAY = 1
END_DELAY = 0.5
MOVE_DELAY = 0.01

class DummyScoreBoard(object):
  def logMsg(self, msg):
    pass

  def addAI(self, aiName):
    pass

  def setScore(self, aiName, idx, score):
    pass

scoreboard = DummyScoreBoard()

class AIError(Exception):
  def __init__(self, msg, score=0, maxCell=2):
    self.msg = msg
    self.score = score
    self.maxCell = maxCell

def logMsg(msg):
  scoreboard.logMsg(msg)
  print msg

class GameManager(object):
  def __init__(self, tab, name):
    self.player = None
    self.lastScore = 0
    self.tab = tab
    self.tab.Navigate('http://gabrielecirulli.github.io/2048/')
    time.sleep(LOAD_DELAY) # Wait for game to load

    self.tab.ExecuteJavaScript('''
      s = new LocalStorageManager();
      document.tagName='xxx';
      fk = function fireKey(key)
      {
        var eventObj = document.createEvent("Events");
        eventObj.initEvent("keydown", true, true);
        eventObj.which = key;
        document.dispatchEvent(eventObj);
      }
      sc = document.getElementsByClassName('score-container')[0];
      kp = document.getElementsByClassName('keep-playing-button')[0];
      gi = document.getElementsByClassName('game-intro')[0]
    ''')
    self.setPlayer(name)

  def setPlayer(self, name):
    self.player = name
    self.tab.ExecuteJavaScript('gi.innerHTML="%s"' % name)

  def getGameState(self):
    return self.tab.EvaluateJavaScript('s.getGameState()')

  def getGrid(self):
    gs = self.getGameState()
    if gs is None:
      return None
    raw_grid = gs['grid']['cells']
    grid = list()
    for i in xrange(4):
      col = [int(x['value']) if x else None for x in raw_grid[i]]
      grid.append(col)
    return grid

  def getMaxCell(self):
    grid = self.getGrid()
    return max([max(grid[i]) for i in xrange(4)])

  def getScore(self):
    return self.tab.EvaluateJavaScript('parseInt(sc.childNodes[0].data)')

  def isLost(self):
    return self.getGameState() is None

  def isWin(self):
    gs = self.getGameState()
    if gs is None:
      return False
    return self.getGameState()['won']  

  def isOver(self):
    gs = self.getGameState()
    if gs is None:
      return True
    return self.getGameState()['over']

  def pressKey(self, key):
    kc = KEY_CODE[key]
    s = ['%s:' % self.player]
    for d in ['left', 'right', 'up', 'down']:
      if key == d:
        s.append('<font color=red>%s</font>' % d)
      else:
        s.append(d)
    self.tab.ExecuteJavaScript('gi.innerHTML="%s"' % ' '.join(s))
    self.tab.ExecuteJavaScript('fk(%d);' % kc)
    self.getScore()

  def keepGoing(self):
    self.tab.ExecuteJavaScript('kp.click()')

  def clearGame(self):
    self.tab.ExecuteJavaScript('s.clearGameState()')


def enumerateAIs():
  filename, pathname, _ = imp.find_module('ai_modules')
  me = os.path.realpath(sys.argv[0])
  if filename:
    raise ImportError('Not a package: %r', 'ai_modules')
  # Use a set because some may be both source and compiled.
  ais = set([os.path.splitext(module)[0]
             for module in os.listdir(pathname)
             if module.endswith('.py') and module != '__init__.py'])
  ret = list()
  for m in ais:
    ret.append((m, imp.load_source(m, "%s/ai_modules/%s.py" %
                                      (os.path.dirname(me), m))))
  return ret


def play(tab, ai):
  gm = GameManager(tab, ai[0])
  try:
    aiInstance = ai[1].AI()
  except: # pylint:disable=W0702
    raise AIError('Failed to create AI')
  time.sleep(START_DELAY)
  last_grid = None
  maxCell = 2
  stale_steps = 0

  while not gm.isOver():
    grid = gm.getGrid()

    if grid == last_grid:
      stale_steps += 1
    else:
      last_grid = grid
      maxCell = max([max(grid[i]) for i in xrange(4)])
      stale_steps = 0

    if stale_steps >= 10:
      score = gm.getScore()
      gm.clearGame()
      raise AIError('Stale. Ending game.', score, maxCell)

    print '%s playing...' % ai[0]
    print 'Current score: %d grid: %r' % (gm.getScore(), grid)
    try:
      nextKey = aiInstance.getNextMove(grid)
    except: # pylint:disable=W0702
      score = gm.getScore()
      gm.clearGame()
      logging.exception('AI threw exception. Ending game. Final score: %d',
                        score)
      raise AIError('AI threw exception. Ending game.', score, maxCell)
    print '    AI pressed %s' % nextKey
    if nextKey not in KEY_CODE:
      score = gm.getScore()
      gm.clearGame()
      raise AIError('Invalid key %s. Ending game.' % nextKey, score, maxCell)
    gm.pressKey(nextKey)
    time.sleep(MOVE_DELAY)
    if gm.isWin():
      gm.keepGoing()
  time.sleep(END_DELAY)
  score = gm.getScore()
  print 'Final score: %d' % score
  return score, maxCell


def waitStart(tab):
  while tab.EvaluateJavaScript('window.started') == 0:
    time.sleep(0.1)


def Main():
  global scoreboard
  scores = dict()
  maxCell = dict()
  options = browser_options.BrowserFinderOptions()
  parser = options.CreateParser('telemetry_perf_test.py')
  options, _ = parser.parse_args(['--browser=system'])

  browser_to_create = browser_finder.FindBrowser(options)
  assert browser_to_create

  with browser_to_create.Create() as b:
    ai_list = enumerateAIs()
    for ai in ai_list:
      scores[ai[0]] = list()
      maxCell[ai[0]] = 2

    if HAS_SCOREBOARD:
      scoreboard = ScoreBoard(b.tabs.New(), ITERATION)

      for ai in ai_list:
        scoreboard.addAI(ai[0])

      waitStart(scoreboard.tab)

    b.tabs[0].Activate()

    for iteration in xrange(ITERATION):
      for ai in ai_list:
        try:
          s, mc = play(b.tabs[0], ai)
        except AIError, err:
          s = err.score
          mc = err.maxCell
          logMsg("%s(%d): %s" % (ai[0], iteration + 1, err.msg))
        if mc > maxCell[ai[0]]:
          maxCell[ai[0]] = mc
          scoreboard.setScore(ai[0], ITERATION + 1, mc)
        scores[ai[0]].append(s)
        scoreboard.setScore(ai[0], iteration, s)
    if ITERATION > 2:
      for ai in ai_list:
        avg = ((sum(scores[ai[0]]) - max(scores[ai[0]]) - min(scores[ai[0]])) /
               (ITERATION - 2))
        scoreboard.setScore(ai[0], ITERATION, avg)
        print "%s avg = %d\n" % (ai[0], avg)
    if HAS_SCOREBOARD:
      time.sleep(10000)


if __name__ == '__main__':
  Main()
