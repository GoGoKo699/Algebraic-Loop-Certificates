"""Queries that recheck the experimental proof before consuming its conclusion."""
from alc.schema import DEFAULT_LIMITS, integer
from .checker import decide


def query(problem_document, certificate, low, high, limits=DEFAULT_LIMITS):
    """Count hits in an inclusive interval and locate the next hit after low.

    A no-hit result is returned only after the negative certificate is verified.
    This is not a program-frontend or arbitrary-predicate verification interface.
    """
    low=integer(low,'low',0,limits=limits)
    high=integer(high,'high',low,limits=limits)
    answer=decide(problem_document,certificate,limits)
    if answer['status']=='unreachable':
        first=last=next_hit=None; count=0
    else:
        t,r=answer['first'],answer['period']
        next_hit=t+r*max(0,(low-t+r-1)//r)
        count=0 if next_hit>high else (high-next_hit)//r+1
        first=next_hit if count else None
        last=first+(count-1)*r if count else None
    return {'decision':answer,'interval':{'low':low,'high':high,'inclusive':True,
            'count':count,'first':first,'last':last,'next_at_or_after_low':next_hit}}
