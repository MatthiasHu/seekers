import os

__all__ = [ f[:-3]
            for f in os.listdir(os.path.dirname(__file__))
            if f.endswith(".py")
            and not f.startswith("_")
          ]

print(
  [ f 
    for f in os.listdir(os.path.dirname(__file__))
  ] )
