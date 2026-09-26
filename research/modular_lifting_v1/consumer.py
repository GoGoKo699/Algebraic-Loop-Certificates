"""Consequences of reverified modular certificates, not arbitrary program claims."""
from alc.schema import Invalid
from .lifting import decide


def query(document,certificate,low,high):
    if any(type(v) is not int or v<0 for v in (low,high)) or low>high:
        raise Invalid('nonnegative inclusive bounds low <= high required')
    result=decide(document,certificate)
    if result['status']=='unreachable':
        return {'count':0,'first_in_window':None,'last_in_window':None,
                'next_at_or_after_low':None,
                'point_guard_loop':{'terminates':False,'body_executions':None}}
    t,r=result['first'],result['period']
    start=t+r*max(0,(low-t+r-1)//r)
    count=0 if start>high else (high-start)//r+1
    return {'count':count,'first_in_window':start if count else None,
            'last_in_window':start+(count-1)*r if count else None,
            'next_at_or_after_low':start,
            'point_guard_loop':{'terminates':True,'body_executions':t}}
