class ConversationContext:
    def __init__(self):self.reset()
    def reset(self):
        self.slots={"location":None,"type":None,"days":None,"budget":None,"people":None,"transport":None,"season":None,"group":None}
        self.last_intent=None;self.last_recommendations=[]
    def update(self,entities,intent=None):
        for k,v in entities.items():
            if v is not None:self.slots[k]=v
        if intent:self.last_intent=intent
    def summary(self):return dict(self.slots)
    def set_recommendations(self,results):self.last_recommendations=[x["tour"]["id"] for x in results]
    def as_query_text(self):
        s=self.slots;parts=[]
        for k in ("location","type","transport","season","group"):
            if s.get(k):parts.append(str(s[k]))
        if s.get("days"):parts.append(f"{s['days']} ngày")
        if s.get("budget"):parts.append(str(s["budget"]))
        if s.get("people"):parts.append(f"{s['people']} người")
        return " ".join(parts)
