#!/usr/bin/env python3
from __future__ import annotations
import argparse, re, subprocess, sys
from pathlib import Path

def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo', default='.')
    ap.add_argument('--collect-tests', action='store_true')
    a=ap.parse_args()
    repo=Path(a.repo).resolve()
    issues=[]
    sev={'BLOCKER':0,'HIGH':0,'MEDIUM':0,'LOW':0}
    def add(s,m): sev[s]+=1; issues.append((s,m))

    r=run(['git','rev-parse','--show-toplevel'], repo)
    if r.returncode!=0: add('BLOCKER','not git repo')
    else:
        top=r.stdout.strip()
        if str(repo)!=top: add('BLOCKER','repo root mismatch')
    if run(['git','rev-parse','--is-inside-work-tree'], repo).stdout.strip()!='true': add('BLOCKER','not inside worktree')
    head=run(['git','rev-parse','HEAD'], repo).stdout.strip()
    if not re.fullmatch(r'[0-9a-f]{40}', head): add('BLOCKER','HEAD not 40-hex lowercase')

    readme=(repo/'README.md').read_text()
    m=re.search(r'tests-(\d+)_PASSING', readme)
    if not m: add('HIGH','README badge missing')
    elif a.collect_tests:
        c=run([sys.executable,'-m','pytest','--collect-only','-q','tests'], repo)
        if c.returncode!=0: add('HIGH','pytest collect failed')
        else:
            m2=re.search(r"collected\s+(\d+)\s+items", c.stdout)
            if m2:
                count=int(m2.group(1))
            else:
                count=0
                for ln in c.stdout.splitlines():
                    m3=re.search(r":\s*(\d+)\s*$", ln)
                    if m3:
                        count += int(m3.group(1))
            badge=int(m.group(1))
            if badge!=count: add('HIGH',f'README badge {badge} != collected {count}')

    doc=(repo/'docs/CRITICAL_RND_FRAMEWORK_TIME_RUPTURE_INFERENCE.md').read_text()
    for needle in ['Runtime implementation boundary','TASK-01','TASK-04','TASK-05','TASK-07','no causal effect']:
        if needle not in doc: add('HIGH',f'doc missing {needle}')

    # simple runtime boundary checks
    rt=(repo/'src/ctios/nctp_runtime.py').read_text()
    if '"status": "stub"' not in rt: add('HIGH','counterfactual stub status missing')

    print('PICL-V1 REPORT')
    for s,m in issues: print(f'[{s}] {m}')
    if sev['BLOCKER'] or sev['HIGH']: return 2
    return 0

if __name__=='__main__':
    raise SystemExit(main())
