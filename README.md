2048-python
===========
This is my 2048 puzzle AI module written in python for an office fun event.

The time limit of *every* move is 0.1 seconds.

Variants
--------
There are five variants:
- kcwu.py
  Normal version. 
- kcwu2.py
  Based on kcwu.py, multi-process.
- kcwu_short.py
  Based on kcwu.py, optimized for maximize (average_score/code_size).
- kcwu_short2.py
  Based on kcwu2.py, optimized for maximize (average_score/code_size).
- kcwu_short_min.py
  Optimized for minimize (average_score*code_size).

Algorithm
---------
- Search: expectiminimax. It can search 3 steps ahead using expectiminimax.
- Eval: inspired from the stackoverflow article, combined with monotoneness, smoothness, and number of blank tile.
  + Weighting of these scores are tuned by hand. I don't know the reason of those magic numbers ;)
- Optimization:
  + Cut some 4 tile since the probability is low
  + Caching score for search node and eval node.
  + Because python is slow, I put some efforts to optimize for speed and the code is then ugly.

Test result
-----------
Result of 100 runs (single thread version):
- average 85458
- median 79396
- max 175484
- average speed: 17 ms/step

License and copyright
---------------------
BSD license.
The copyright is owned by Google Inc. but this is not official product.

