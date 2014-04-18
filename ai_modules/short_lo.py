# 98*476=46648
class AI:
 i=0
 def getNextMove(s,g):s.i+=1;return'left right up up up up up down'.split()[s.i%8]
