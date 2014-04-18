# 86*621=53406
class AI:
 i=0
 def getNextMove(s,g):s.i+=1;return['left','right','up','down'][s.i%4]
