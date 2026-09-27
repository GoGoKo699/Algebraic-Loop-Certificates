"""Check preserved native observations against the frozen source generator.

This validates transcription consistency, corpus identity and summaries; it
DOES NOT reproduce a native run or certify the soundness of a solver verdict.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from audits.invariant_validation_v1.gate import cases,formula


def check():
    document=json.loads((Path(__file__).with_name('native_observations.json')).read_text())
    names=['case','expected','raw_status','raw_elapsed_ns','raw_input_sha256',
           'decomposed_status','decomposed_elapsed_ns','decomposed_input_sha256','decomposed_obligations']
    if document['columns']!=names or len(document['rows'])!=len(cases()):
        raise AssertionError('Unexpected preserved corpus.')
    summary={route:{'valid_proved':0,'invalid_detected':0,'unknown':0} for route in ('raw','decomposed')}
    seen=set()
    for spec,raw in zip(cases(),document['rows']):
        if len(raw)!=len(names):raise AssertionError('Malformed result row.')
        row=dict(zip(names,raw))
        if row['case']!=spec['name'] or row['expected']!=spec['expected'] or row['case'] in seen:
            raise AssertionError('Frozen case changed, reordered or duplicated.')
        seen.add(row['case'])
        for route,decomposed in (('raw',False),('decomposed',True)):
            text,obligations=formula(spec,decomposed)
            if hashlib.sha256(text.encode()).hexdigest()!=row[route+'_input_sha256']:
                raise AssertionError('Measured input differs from frozen generator.')
            status=row[route+'_status'];ns=row[route+'_elapsed_ns']
            if type(ns) is not int or ns<0:raise AssertionError('Invalid measured duration.')
            if status not in ('sat','unsat','unknown'):raise AssertionError('Unrecorded outcome category.')
            if status=='unknown':summary[route]['unknown']+=1
            elif status!=spec['expected']:raise AssertionError('Conclusive native result contradicts control.')
            else:summary[route]['valid_proved' if status=='unsat' else 'invalid_detected']+=1
            if decomposed and row['decomposed_obligations']!=obligations:
                raise AssertionError('Decomposed obligations changed.')
    expected={'raw':{'valid_proved':10,'invalid_detected':9,'unknown':1},
              'decomposed':{'valid_proved':4,'invalid_detected':10,'unknown':6}}
    if summary!=expected:raise AssertionError('Published summary differs from recorded observations.')
    return summary


if __name__=='__main__':
    print(json.dumps(check(),indent=2,sort_keys=True))
    print('Recorded native-data consistency only; no new native execution or formal proof replay.')
