"""Exploratory mixed execution/clarification policies and a tiny exact reference."""
from collections import Counter
from functools import lru_cache
from itertools import combinations


def run_joint(worlds,execute,respond,question_cost=1.0,policy='certificate'):
    state=list(range(len(worlds)));known={};questions=0;trace=[]
    while True:
        unknown=[i for i in state if i not in known]
        if not unknown and len({known[i] for i in state})==1:
            return {'answer':known[state[0]],'executions':len(known),'questions':questions,'cost':len(known)+question_cost*questions,'trace':trace}
        qs=[q for q in range(len(worlds[0])) if len({worlds[i][q] for i in state})>1]
        labeled=[i for i in state if i in known]
        conflicts=[(i,j) for i,j in combinations(labeled,2) if known[i]!=known[j]]
        eligible=[q for q in qs if any(worlds[i][q]!=worlds[j][q] for i,j in conflicts)]
        if policy=='ask_first':eligible=qs
        action=None
        if eligible:
            def gain(q):
                parts=[[i for i in state if worlds[i][q]==z] for z in sorted({worlds[i][q] for i in state})]
                if policy in ['ask_first','witness_split']:
                    return len(state)-sum(len(p)**2/len(state) for p in parts)
                # Unresolved certificate obligations: each unknown surviving
                # vertex and each pair not yet certified equal. A question
                # covers obligations whose vertices cannot survive its response.
                def burden(s):
                    return sum(i not in known for i in s)+sum(not(i in known and j in known and known[i]==known[j]) for i,j in combinations(s,2))
                return burden(state)-sum(len(p)/len(state)*burden(p) for p in parts)
            q=max(eligible,key=lambda q:(gain(q),-q))
            if policy in ['ask_first','witness_split'] or not unknown:action=('ask',q)
            else:
                counts=Counter(known[i] for i in labeled)
                # Explicit empirical label-frequency heuristic with one unit
                # of mass for a new class. This is not a calibrated prior.
                expected_same=sum(c*c for c in counts.values())/(len(labeled)+1)
                execution_gain=1+expected_same
                if gain(q)/question_cost>=execution_gain:action=('ask',q)
        if action is None:
            if not unknown:raise ValueError('unidentifiable')
            action=('execute',unknown[0])
        if action[0]=='execute':known[action[1]]=execute(action[1])
        else:
            q=action[1];z=respond(q);state=[i for i in state if worlds[i][q]==z];questions+=1
            if not state:raise ValueError('unsupported response')
        trace.append(action)


def tiny_optimal(worlds,question_cost=1.0,witness_gate=True):
    """Bayes optimum for independent fair binary answer labels, uniform worlds.

    No claimed transfer of this explicit artificial prior to SQL workloads.
    Returns expected cost and cache size for the initial unlabelled state.
    """
    @lru_cache(None)
    def solve(state,zeros,ones):
        known=set(zeros)|set(ones)
        if len(known)==len(state) and (not zeros or not ones):return 0.0
        choices=[]
        for i in state:
            if i not in known:
                choices.append(1+0.5*solve(state,tuple(sorted(zeros+(i,))),ones)+0.5*solve(state,zeros,tuple(sorted(ones+(i,)))))
        for q in range(len(worlds[0])):
            groups={}
            for i in state:groups.setdefault(worlds[i][q],[]).append(i)
            if len(groups)==1:continue
            if witness_gate and not any(worlds[i][q]!=worlds[j][q] for i in zeros for j in ones):continue
            value=question_cost
            for group in groups.values():
                g=tuple(group)
                value+=len(g)/len(state)*solve(g,tuple(i for i in zeros if i in g),tuple(i for i in ones if i in g))
            choices.append(value)
        return min(choices)
    value=solve(tuple(range(len(worlds))),(),())
    return {'expected_cost':value,'states':solve.cache_info().currsize}
