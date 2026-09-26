"""Command-line producer, checker, and verified time-window consumer."""
from __future__ import annotations
import argparse
import json
import sys
from .schema import Invalid, ResourceLimit, dump_new, load


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog='python -m alc')
    sub = parser.add_subparsers(dest='command', required=True)
    prod = sub.add_parser('produce', help='bounded reference search; writes candidate certificates only')
    prod.add_argument('--problem', required=True)
    prod.add_argument('--output', required=True)
    prod.add_argument('--max-steps', type=int, default=10_000)
    for name in ('verify', 'query'):
        p = sub.add_parser(name)
        p.add_argument('--problem', required=True)
        p.add_argument('--certificate', required=True)
        if name == 'query':
            p.add_argument('--from', dest='start', type=int, default=0)
            p.add_argument('--through', type=int, required=True)
            p.add_argument('--schedule', nargs=2, type=int, metavar=('RESIDUE', 'PERIOD'))
    args = parser.parse_args(argv)
    try:
        problem = load(args.problem)
        if args.command == 'produce':
            from .producer import produce
            result = produce(problem, args.max_steps)
            if result['status'] != 'candidate':
                print(json.dumps(result, sort_keys=True))
                return 4
            dump_new(args.output, result.pop('certificate'))
            result['output'] = args.output
        else:
            from .checker import verify
            hits = verify(problem, load(args.certificate))
            result = hits.as_dict()
            if args.command == 'query':
                from .consumer import intersect_schedule, window
                result['window'] = window(hits, args.start, args.through)
                if args.schedule:
                    combined = intersect_schedule(hits, *args.schedule)
                    result['intersection_with_supplied_schedule'] = (
                        None if combined is None else {'first': combined[0], 'period': combined[1]})
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except ResourceLimit as exc:
        print(json.dumps({'status': 'resource_limit', 'reason': str(exc), 'certified': False}))
        return 2
    except Invalid as exc:
        print(json.dumps({'status': 'invalid', 'reason': str(exc), 'certified': False}))
        return 1
    except (OSError, ValueError) as exc:
        print(json.dumps({'status': 'input_or_io_error', 'reason': str(exc), 'certified': False}))
        return 3


if __name__ == '__main__':
    sys.exit(main())
