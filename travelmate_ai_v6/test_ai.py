from database import init_db,get_all_tours
from context_manager import ConversationContext
from recommender import analyze_message,recommend_from_context
from itinerary_engine import itinerary_text
from evaluation import evaluate

init_db()
ctx=ConversationContext()
for q in ["Tôi thích biển","3 ngày thôi","ngân sách 4 triệu","đi bằng máy bay"]:
    intent,conf,e,_=analyze_message(q,ctx)
    print(q,intent,round(conf,3),e,ctx.summary())
r=recommend_from_context("đi bằng máy bay",ctx,3)
for x in r["results"]:print(x["tour"]["name"],round(x["score"],3))
print(itinerary_text(get_all_tours()[0])[:400])
ev=evaluate()
print("accuracy",round(ev["accuracy"],3),"errors",len(ev["errors"]))
