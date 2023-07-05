#!/usr/bin/env python3
from fireflayer import fireflayer

try:
    fireflayer.main()
except Exception as e:
    print('Exception occured')
    if hasattr(e, 'stdout'):
        print(f'stdout was: {e.stdout}')
    if hasattr(e, 'stderr'):
        print(f'stderr was: {e.stderr}')
    raise
