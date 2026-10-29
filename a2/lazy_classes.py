"""Candidate algorithm: exact EC2 decisions with incrementally discovered labels.

This module is an exploratory prototype, not an established novelty claim.
Only the execution callback can reveal a world's answer to the policy.
"""
from collections import Counter
from itertools import combinations
import random


def run_lazy(worlds, execute, respond, acquisition='comparison', seed=0, bound='independent'):
    worlds=tuple(tuple(w) for w in worlds)
    if not worlds:raise ValueError('empty candidate universe')
    state=list(range(len(worlds)));known={};asked=[];trace=[]
    rng=random.Random(seed)
    while True:
        unknown=[i for i in state if i not in known]
        if not unknown and len({known[i] for i in state})==1:
            return {'answer':known[state[0]],'executions':len(known),'questions':len(asked),'asked':asked,'trace':trace}
        qs=[q for q in range(len(worlds[0])) if len({worlds[i][q] for i in state})>1]
        if not qs:
            if unknown:
                i=unknown[0];known[i]=execute(i);trace.append({'execute':i});continue
            raise ValueError('Different answers but no separating question')
        n=len(state)
        counts={q:Counter(worlds[i][q] for i in state) for q in qs}
        pairs=list(combinations(state,2))
        # n times expected edge-cut coefficient; uniform-prior normalization
        # is shared by all questions, so all comparison bounds are integers.
        coef={q:[n if worlds[i][q]!=worlds[j][q] else n-counts[q][worlds[i][q]] for i,j in pairs] for q in qs}
        status=[int(known[i]!=known[j]) if i in known and j in known else None for i,j in pairs]
        midpoint={q:sum(c*(1 if s is None else 2*s) for c,s in zip(coef[q],status)) for q in qs}
        best=max(qs,key=lambda q:(midpoint[q],-q))
        certified=True
        for rival in qs:
            if rival==best:continue
            diffs=[a-b for a,b in zip(coef[best],coef[rival])]
            if bound=='independent':
                lower=sum(d*s if s is not None else min(0,d) for d,s in zip(diffs,status))
            elif bound=='partition':
                # Each unknown answer can equal at most one known answer class.
                # Optimize its entire star to known vertices jointly. Treat
                # unknown-unknown edges independently as a sound relaxation.
                by_unknown={i:{} for i in unknown}
                lower=0
                for (i,j),d,s in zip(pairs,diffs,status):
                    if s is not None:lower+=d*s
                    elif i not in known and j not in known:lower+=min(0,d)
                    else:
                        u,k=(i,j) if i not in known else (j,i)
                        label=known[k]
                        by_unknown[u][label]=by_unknown[u].get(label,0)+d
                for groups in by_unknown.values():
                    total=sum(groups.values())
                    lower+=min([total]+[total-v for v in groups.values()])
            else:raise ValueError(bound)
            if lower<0 or (lower==0 and rival<best):certified=False;break
        # A ranking certificate is not a stopping certificate. Require an
        # observed disagreement to avoid asking on an unseen constant function.
        conflict=any(s==1 for s in status)
        if certified and conflict:
            z=respond(best)
            state=[i for i in state if worlds[i][best]==z]
            if not state:raise ValueError('Response outside candidate universe')
            asked.append(best);trace.append({'ask':best,'response':z,'remaining':len(state)})
            continue
        if not unknown:raise AssertionError('Complete labels must certify a maximizer')
        if acquisition=='random':chosen=rng.choice(unknown)
        elif acquisition=='fixed':chosen=unknown[0]
        elif acquisition=='comparison':
            impacts={i:0 for i in unknown}
            for index,(i,j) in enumerate(pairs):
                if status[index] is not None:continue
                weight=sum(abs(coef[best][index]-coef[r][index]) for r in qs if r!=best)
                # Labeling one endpoint only reveals an edge if the other
                # endpoint is already labeled. Use this realized impact first.
                if i in impacts:impacts[i]+=weight*(1 if j in known else 0)
                if j in impacts:impacts[j]+=weight*(1 if i in known else 0)
            chosen=max(unknown,key=lambda i:(impacts[i],-i))
        else:raise ValueError(acquisition)
        known[chosen]=execute(chosen);trace.append({'execute':chosen})
