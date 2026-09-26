"""JSON command-line entrypoint. Every consumer rechecks its certificate."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from . import InvalidCertificate, VerificationLimit, count_interval, first_at_least, verify
from .producers import produce


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError('Duplicate JSON key: ' + key)
        out[key] = value
    return out


def load(path):
    p = Path(path)
    if p.stat().st_size > 4 * 1024 * 1024:
        raise VerificationLimit('JSON input exceeds four MiB.')
    return json.loads(p.read_text(encoding='utf-8'), object_pairs_hook=unique_object)


def main():
    parser = argparse.ArgumentParser(prog='python -m alc')
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('produce', help='Bounded reference producer; UNKNOWN is possible.')
    p.add_argument('instance'); p.add_argument('--output', required=True)
    p.add_argument('--max-steps', type=int, default=100000)
    p.add_argument('--max-trial-work', type=int, default=100000)
    for name in ('check', 'query'):
        p = sub.add_parser(name)
        p.add_argument('instance'); p.add_argument('certificate')
        if name == 'query':
            p.add_argument('--low', type=int, required=True)
            p.add_argument('--high', type=int, required=True)
    args = parser.parse_args()
    try:
        instance = load(args.instance)
        if args.command == 'produce':
            if Path(args.output).exists():
                raise FileExistsError('Refusing to overwrite existing output: ' + args.output)
            result = produce(instance, args.max_steps, args.max_trial_work)
            if result['status'] == 'unknown':
                print(json.dumps(result, indent=2, sort_keys=True))
                return 3
            cert = result['certificate']
            summary = verify(instance, cert)
            with open(args.output, 'x', encoding='utf-8') as f:
                json.dump(cert, f, indent=2, sort_keys=True); f.write('\n')
            result = dict(status='verified', summary=summary.as_dict(), metrics=result['metrics'])
        else:
            summary = verify(instance, load(args.certificate))
            result = dict(status='verified', summary=summary.as_dict())
            if args.command == 'query':
                result['query'] = dict(low=args.low, high=args.high,
                    count=count_interval(summary, args.low, args.high),
                    next_at_or_after_low=first_at_least(summary, args.low))
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except VerificationLimit as exc:
        print(json.dumps(dict(status='resource_limit', reason=str(exc))), file=sys.stderr)
        return 3
    except (InvalidCertificate, ValueError, OSError, RecursionError) as exc:
        print(json.dumps(dict(status='rejected', reason=str(exc))), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
