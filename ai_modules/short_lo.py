# 93*484=45012
class AI:
 i=0
 def getNextMove(s,g):s.i+=1;return('down left right'+' up'*5).split()[s.i%8]
