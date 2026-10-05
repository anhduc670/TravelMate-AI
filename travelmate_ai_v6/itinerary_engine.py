LOCATION_SPOTS = {
    "Đà Nẵng":["Biển Mỹ Khê","Bà Nà Hills","Cầu Rồng","Phố cổ Hội An"],
    "Đà Lạt":["Hồ Xuân Hương","Quảng trường Lâm Viên","Langbiang","Vườn hoa"],
    "Phú Quốc":["Bãi Sao","Hòn Thơm","Grand World","Chợ đêm Phú Quốc"],
    "Sapa":["Bản Cát Cát","Fansipan","Nhà thờ đá","Đèo Ô Quy Hồ"],
    "Nha Trang":["Bãi biển Nha Trang","Hòn Mun","Tháp Bà Ponagar","VinWonders"],
    "Hà Giang":["Đồng Văn","Mã Pí Lèng","Cột cờ Lũng Cú","Dinh Vua Mèo"],
    "Hạ Long":["Vịnh Hạ Long","Hang Sửng Sốt","Đảo Ti Tốp","Bãi Cháy"],
    "Mộc Châu":["Đồi chè","Thác Dải Yếm","Rừng thông Bản Áng","Cầu kính"],
    "Huế":["Đại Nội","Chùa Thiên Mụ","Lăng Khải Định","Sông Hương"],
    "Cần Thơ":["Chợ nổi Cái Răng","Bến Ninh Kiều","Miệt vườn","Nhà cổ Bình Thủy"],
    "Quy Nhơn":["Kỳ Co","Eo Gió","Ghềnh Ráng","Tháp Đôi"],
    "Vũng Tàu":["Bãi Sau","Tượng Chúa Kitô","Hải đăng","Hồ Mây"]
}

def generate_itinerary(tour):
    spots = LOCATION_SPOTS.get(tour["location"], [
        "Điểm tham quan trung tâm","Danh thắng nổi bật","Khu ẩm thực","Khu mua sắm"
    ])
    days = int(tour["days"])
    result=[]
    idx=0
    for day in range(1,days+1):
        if day==1:
            morning=f"Di chuyển đến {tour['location']} bằng {tour['transport']}, nhận phòng và nghỉ ngơi."
        else:
            morning=f"Tham quan {spots[idx % len(spots)]}."; idx+=1
        afternoon=f"Tham quan {spots[idx % len(spots)]}, chụp ảnh và trải nghiệm địa phương."; idx+=1
        if day==days:
            evening="Mua đặc sản, tổng kết chuyến đi và chuẩn bị trở về."
        else:
            evening=f"Ăn tối, khám phá ẩm thực và tự do tham quan {tour['location']}."
        result.append({
            "day":day,
            "morning":morning,
            "afternoon":afternoon,
            "evening":evening
        })
    return result

def itinerary_text(tour):
    rows=generate_itinerary(tour)
    lines=[f"LỊCH TRÌNH AI - {tour['name']}\n"]
    for r in rows:
        lines += [
            f"NGÀY {r['day']}",
            f"  Sáng: {r['morning']}",
            f"  Chiều: {r['afternoon']}",
            f"  Tối: {r['evening']}",
            ""
        ]
    return "\n".join(lines)
