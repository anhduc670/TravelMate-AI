from database import get_all_tours,get_tour
from nlp import extract_entities
from intent_model import predict_intent
from ai_engine import rank_tours

def money(v):return f"{int(v):,}".replace(",",".")+" VNĐ"

def analyze_message(text,context):
    e=extract_entities(text);intent,conf,raw=predict_intent(text)
    if any(e[k] is not None for k in ("location","type","days","budget","transport","season","group")) and intent in ("greeting","thanks"):
        intent="find_tour"
    context.update(e,intent)
    return intent,conf,e,raw

def recommend_from_context(text,context,limit=5):
    r=rank_tours(text+" "+context.as_query_text(),context.summary(),get_all_tours(),limit)
    context.set_recommendations(r["results"]);return r

def build_recommendation_answer(r,context):
    s=context.summary();parts=[]
    for k,label in (("location","địa điểm"),("type","loại"),("transport","phương tiện"),("season","mùa"),("group","nhóm")):
        if s.get(k):parts.append(f"{label} {s[k]}")
    if s.get("days"):parts.append(f"{s['days']} ngày")
    if s.get("budget"):parts.append("ngân sách "+money(s["budget"]))
    lines=[]
    if parts:lines.append("Tôi đang nhớ: "+", ".join(parts)+".")
    lines.append("\nCác tour phù hợp nhất:")
    for i,item in enumerate(r["results"][:3],1):
        t=item["tour"];reason=", ".join(item["reasons"]) if item["reasons"] else "phù hợp tổng thể"
        lines.append(f"{i}. {t['name']} - {t['days']} ngày - {money(t['price'])}\n   AI {item['score']*100:.1f}% | {reason}")
    return "\n".join(lines)

def answer_non_recommendation(intent,context):
    if intent=="greeting":return "Xin chào! Hãy mô tả chuyến đi mong muốn."
    if intent=="thanks":return "Rất vui được hỗ trợ bạn."
    if intent=="show_bookings":return "Bạn mở mục Tour đã đặt ở menu."
    if not context.last_recommendations:return None
    t=get_tour(context.last_recommendations[0])
    if intent=="ask_price":return f"{t['name']} có giá {money(t['price'])}/người."
    if intent=="ask_duration":return f"{t['name']} kéo dài {t['days']} ngày."
    if intent=="ask_transport":return f"Phương tiện chính của {t['name']}: {t['transport']}."
    if intent=="book_tour":return f"Đã chọn {t['name']}. Bạn có thể bấm Đặt tour."
    return None


def missing_information_prompt(context):
    """Return a natural follow-up question when recommendation context is too sparse."""
    s = context.summary()

    # Strongest signals first
    if not s.get("type") and not s.get("location"):
        return "Bạn thích kiểu du lịch nào: biển, núi, nghỉ dưỡng, khám phá hay văn hóa?"

    if not s.get("days"):
        return "Bạn dự kiến đi khoảng bao nhiêu ngày?"

    if not s.get("budget"):
        return "Ngân sách dự kiến của bạn khoảng bao nhiêu triệu đồng?"

    if not s.get("people"):
        return "Bạn đi khoảng bao nhiêu người?"

    # Nice-to-have fields after core slots are filled
    if not s.get("transport"):
        return "Bạn ưu tiên đi bằng máy bay hay ô tô?"

    return None

def enough_information_for_recommendation(context):
    s = context.summary()
    core = [
        bool(s.get("type") or s.get("location")),
        bool(s.get("days")),
        bool(s.get("budget"))
    ]
    return sum(core) >= 2
