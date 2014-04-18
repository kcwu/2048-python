# 94*461=43334
class AI:
 i=0
 def getNextMove(s,g):s.i+=1;return('down left right'+' up'*7).split()[s.i%10]
