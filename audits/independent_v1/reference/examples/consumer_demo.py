"""Read two certificates, verify them, then answer queries without simulation."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from alc import verify, synchronize, count_interval, first_at_least

root = Path(__file__).resolve().parent

def checked(name):
    return verify(json.loads((root/(name+'.json')).read_text()),
                  json.loads((root/(name+'.certificate.json')).read_text()))

fib = checked('fibonacci')
clock = checked('affine')
both = synchronize(fib, clock)
horizon = 10**30
print(json.dumps(dict(fibonacci=fib.as_dict(), clock=clock.as_dict(),
    simultaneous=both.as_dict(), through_horizon=horizon,
    fibonacci_hits=count_interval(fib, 0, horizon),
    simultaneous_hits=count_interval(both, 0, horizon),
    next_simultaneous_hit=first_at_least(both, horizon)), indent=2, sort_keys=True))
