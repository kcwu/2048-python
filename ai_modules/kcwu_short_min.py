# Copyright 2014 Google Inc. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
# 94*677=63638
class AI:
 i=0
 def getNextMove(s,g):s.i+=1;return('up down '*4+'left right').split()[s.i%10]
