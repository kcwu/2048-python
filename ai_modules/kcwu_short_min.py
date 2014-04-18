# 94*677=63638
class AI:
 i=0
 def getNextMove(s,g):s.i+=1;return('up down '*4+'left right').split()[s.i%10]
