RULES=[
("R1",["săn mây","mát mẻ","mát lạnh"],"Núi","Săn mây/khí hậu mát phù hợp tour núi."),
("R2",["yên tĩnh","thư giãn","resort"],"Nghỉ dưỡng","Nhu cầu thư giãn phù hợp tour nghỉ dưỡng."),
("R3",["tắm biển","biển","hải sản","san hô","đảo"],"Biển","Từ khóa biển phù hợp tour biển."),
("R4",["phượt","mạo hiểm","khám phá"],"Khám phá","Nhu cầu phiêu lưu phù hợp tour khám phá."),
("R5",["lịch sử","văn hóa","di tích","cố đô"],"Văn hóa","Quan tâm lịch sử/văn hóa."),
("R6",["sông nước","chợ nổi","miệt vườn"],"Miền Tây","Sở thích sông nước.")
]
def infer_preferences(text,current_type=None):
    text=text.lower();types=[current_type] if current_type else [];fired=[]
    for name,keys,typ,reason in RULES:
        if any(k in text for k in keys):
            fired.append({"name":name,"infer_type":typ,"reason":reason})
            if typ not in types:types.append(typ)
    return types,fired
