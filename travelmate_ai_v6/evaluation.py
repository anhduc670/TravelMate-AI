from intent_model import predict_intent

TEST_DATA=[
("xin chào bạn","greeting"),("hello travelmate","greeting"),("hi chatbot","greeting"),("chào nhé","greeting"),
("gợi ý tour biển","find_tour"),("tìm chuyến đi phù hợp","find_tour"),("tôi muốn nghỉ dưỡng","find_tour"),("tư vấn chỗ đi chơi","find_tour"),
("tour này bao nhiêu tiền","ask_price"),("cho tôi biết giá tour","ask_price"),("chi phí chuyến này","ask_price"),("tour có đắt không","ask_price"),
("tour đi mấy ngày","ask_duration"),("chuyến kéo dài bao lâu","ask_duration"),("thời lượng tour","ask_duration"),("đi trong bao lâu","ask_duration"),
("đi bằng phương tiện gì","ask_transport"),("tour dùng xe gì","ask_transport"),("có đi máy bay không","ask_transport"),("di chuyển bằng gì","ask_transport"),
("tôi muốn đặt tour","book_tour"),("đặt chuyến này giúp tôi","book_tour"),("đăng ký tour","book_tour"),("booking tour này","book_tour"),
("xem tour đã đặt","show_bookings"),("lịch sử booking","show_bookings"),("đơn của tôi","show_bookings"),("tôi đã đặt gì","show_bookings"),
("cảm ơn bạn","thanks"),("thank you","thanks"),("ok cảm ơn","thanks"),("cảm ơn travelmate","thanks")
]
LABELS=["greeting","find_tour","ask_price","ask_duration","ask_transport","book_tour","show_bookings","thanks"]

def evaluate():
    matrix={a:{p:0 for p in LABELS} for a in LABELS};errors=[];correct=0
    for text,actual in TEST_DATA:
        pred,conf,_=predict_intent(text);matrix[actual][pred]+=1
        if pred==actual:correct+=1
        else:errors.append((text,actual,pred,conf))
    metrics={}
    for label in LABELS:
        tp=matrix[label][label]
        fp=sum(matrix[a][label] for a in LABELS if a!=label)
        fn=sum(matrix[label][p] for p in LABELS if p!=label)
        precision=tp/(tp+fp) if tp+fp else 0
        recall=tp/(tp+fn) if tp+fn else 0
        f1=2*precision*recall/(precision+recall) if precision+recall else 0
        metrics[label]=(precision,recall,f1)
    n=len(TEST_DATA)
    return {
        "accuracy":correct/n,
        "macro_precision":sum(x[0] for x in metrics.values())/len(metrics),
        "macro_recall":sum(x[1] for x in metrics.values())/len(metrics),
        "macro_f1":sum(x[2] for x in metrics.values())/len(metrics),
        "matrix":matrix,"metrics":metrics,"labels":LABELS,"errors":errors,"total":n
    }


RECOMMENDATION_TESTS = [
    ("Tôi thích biển, 3 ngày, ngân sách 4 triệu", ["Đà Nẵng - Hội An", "Quy Nhơn - Kỳ Co Eo Gió"]),
    ("Tôi muốn săn mây, đi khoảng 3 ngày", ["Sapa - Fansipan", "Mộc Châu Săn Mây"]),
    ("Tôi thích nghỉ dưỡng yên tĩnh 3 ngày", ["Đà Lạt Mộng Mơ"]),
    ("Tôi muốn khám phá vùng núi 4 ngày", ["Hà Giang Hùng Vĩ"]),
    ("Tôi thích lịch sử và văn hóa khoảng 3 ngày", ["Cố Đô Huế"]),
    ("Tôi muốn đi miền Tây 2 ngày", ["Miền Tây Sông Nước"]),
    ("Đi biển 2 ngày ngân sách dưới 3 triệu", ["Vũng Tàu Cuối Tuần", "Vịnh Hạ Long"]),
    ("Tôi muốn tour biển 4 ngày khoảng 5 triệu", ["Nha Trang Biển Xanh"]),
    ("Tôi muốn đi Phú Quốc 4 ngày", ["Phú Quốc Thiên Đường Biển"]),
    ("Tôi muốn đi Quy Nhơn 3 ngày", ["Quy Nhơn - Kỳ Co Eo Gió"]),
    ("Tôi muốn đi Đà Nẵng 3 ngày", ["Đà Nẵng - Hội An"]),
    ("Tôi muốn đi Sapa 3 ngày", ["Sapa - Fansipan"]),
    ("Tôi muốn đi Đà Lạt thư giãn", ["Đà Lạt Mộng Mơ"]),
    ("Tôi muốn đi Hạ Long 2 ngày", ["Vịnh Hạ Long"]),
    ("Tôi muốn đi Mộc Châu 2 ngày", ["Mộc Châu Săn Mây"]),
    ("Tôi thích biển và hải sản, 3 ngày", ["Đà Nẵng - Hội An", "Quy Nhơn - Kỳ Co Eo Gió"]),
    ("Tôi muốn phượt, khám phá, 4 ngày", ["Hà Giang Hùng Vĩ"]),
    ("Tôi thích sông nước, chợ nổi", ["Miền Tây Sông Nước"]),
    ("Tôi muốn tour văn hóa, di tích", ["Cố Đô Huế"]),
    ("Tôi thích resort, biển đảo, 4 ngày", ["Phú Quốc Thiên Đường Biển"])
]

def evaluate_recommendation_system():
    from database import get_all_tours
    from ai_engine import rank_tours
    from nlp import extract_entities

    tours = get_all_tours()
    total = len(RECOMMENDATION_TESTS)
    top1_ok = 0
    top3_ok = 0
    rows = []

    for query, expected_names in RECOMMENDATION_TESTS:
        slots = extract_entities(query)
        result = rank_tours(query, slots, tours, limit=5)
        names = [x["tour"]["name"] for x in result["results"]]
        top1 = names[0] if names else ""
        top3 = names[:3]

        ok1 = top1 in expected_names
        ok3 = any(name in expected_names for name in top3)

        top1_ok += int(ok1)
        top3_ok += int(ok3)

        rows.append({
            "query": query,
            "expected": ", ".join(expected_names),
            "top1": top1,
            "top3": " | ".join(top3),
            "top1_ok": ok1,
            "top3_ok": ok3
        })

    return {
        "total": total,
        "top1_accuracy": top1_ok / total if total else 0,
        "top3_accuracy": top3_ok / total if total else 0,
        "rows": rows
    }
