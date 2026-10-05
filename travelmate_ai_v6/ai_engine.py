import math
from collections import Counter
from nlp import tokenize
from knowledge_base import infer_preferences

def tf(tokens):
    c=Counter(tokens);total=max(1,len(tokens));return {w:n/total for w,n in c.items()}
def idf(docs):
    vocab=set(w for d in docs for w in d);n=len(docs)
    return {w:math.log((n+1)/(sum(1 for d in docs if w in d)+1))+1 for w in vocab}
def vector(tokens,m):
    t=tf(tokens);return {w:t.get(w,0)*m[w] for w in m}
def cosine(v1,v2):
    dot=sum(v1[k]*v2[k] for k in v1);n1=math.sqrt(sum(x*x for x in v1.values()));n2=math.sqrt(sum(x*x for x in v2.values()))
    return 0 if not n1 or not n2 else dot/(n1*n2)
def semantic_scores(q,tours):
    qt=tokenize(q);docs=[tokenize(f"{t['name']} {t['location']} {t['type']} {t['transport']} {t['season']} {t['audience']} {t['description']}") for t in tours]
    m=idf([qt]+docs);qv=vector(qt,m)
    return {t["id"]:cosine(qv,vector(d,m)) for t,d in zip(tours,docs)}
def rating_score(t):
    avg=float(t.get("avg_rating") or 0);count=int(t.get("review_count") or 0)
    if not count:return .5
    return min(1,((avg*count+3.5*3)/(count+3))/5)
def rank_tours(query,slots,tours,limit=5):
    inferred,rules=infer_preferences(query,slots.get("type"));sems=semantic_scores(query,tours);out=[]
    for t in tours:
        sem=sems.get(t["id"],0);pref=0;reasons=[]
        if slots.get("location"):
            if slots["location"] in t["location"].lower():pref+=.55;reasons.append("đúng địa điểm")
            else:pref-=.2
        if inferred and t["type"] in inferred:pref+=.45;reasons.append("đúng sở thích")
        bud=.55 if not slots.get("budget") else (1 if t["price"]<=slots["budget"] else .2 if t["price"]<=slots["budget"]*1.1 else 0)
        dur=.55 if not slots.get("days") else (1 if t["days"]==slots["days"] else .65 if abs(t["days"]-slots["days"])==1 else 0)
        tr=.55 if not slots.get("transport") else (1 if t["transport"]==slots["transport"] else 0)
        sea=.55 if not slots.get("season") else (1 if t["season"]==slots["season"] or t["season"]=="quanh năm" else 0)
        grp=.55 if not slots.get("group") else (1 if slots["group"] in t["audience"] else 0)
        rate=rating_score(t)
        score=.30*sem+.20*max(0,min(1,pref))+.12*bud+.10*dur+.08*tr+.08*sea+.05*grp+.07*rate
        if bud==1:reasons.append("trong ngân sách")
        if dur==1:reasons.append("đúng số ngày")
        if tr==1 and slots.get("transport"):reasons.append("đúng phương tiện")
        if sea==1 and slots.get("season"):reasons.append("phù hợp mùa")
        if grp==1 and slots.get("group"):reasons.append("phù hợp nhóm khách")
        if float(t.get("avg_rating") or 0)>=4:reasons.append("được đánh giá cao")
        out.append({"tour":t,"score":score,"semantic_score":sem,"preference_score":max(0,min(1,pref)),
                    "budget_score":bud,"duration_score":dur,"transport_score":tr,"season_score":sea,
                    "group_score":grp,"rating_score":rate,"reasons":reasons})
    out.sort(key=lambda x:x["score"],reverse=True)
    return {"results":out[:limit],"fired_rules":rules,"inferred_types":inferred}
