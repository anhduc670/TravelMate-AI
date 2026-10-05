import re

STOP_WORDS = {
    "tôi","mình","muốn","đi","du","lịch","tour","một","có","khoảng",
    "với","và","là","ở","cho","được","nơi","nào","đó","thì","của",
    "giúp","tư","vấn","hãy","biết","còn","thế","này","nhé"
}

LOCATIONS = ["đà nẵng","đà lạt","phú quốc","sapa","sa pa","nha trang","hà giang","hạ long","mộc châu","huế","cần thơ","quy nhơn","vũng tàu"]

TYPE_SYNONYMS = {
    "Biển":["biển","tắm biển","đảo","hải sản","lặn biển","san hô"],
    "Núi":["núi","leo núi","săn mây","vùng cao","mát lạnh"],
    "Nghỉ dưỡng":["nghỉ dưỡng","thư giãn","yên tĩnh","resort","chill"],
    "Khám phá":["khám phá","phượt","mạo hiểm","trải nghiệm","cung đường"],
    "Văn hóa":["văn hóa","lịch sử","di tích","cố đô","lăng tẩm"],
    "Miền Tây":["miền tây","sông nước","chợ nổi","miệt vườn"]
}
TRANSPORT_KEYWORDS={"máy bay":["máy bay","bay"],"ô tô":["ô tô","xe khách","đường bộ"]}
SEASON_KEYWORDS={"mùa xuân":["mùa xuân","xuân"],"mùa hè":["mùa hè","hè"],"mùa thu":["mùa thu","thu"],"mùa đông":["mùa đông","đông"],"mùa khô":["mùa khô"]}
GROUP_KEYWORDS={"gia đình":["gia đình","bố mẹ","trẻ em","con nhỏ"],"cặp đôi":["cặp đôi","người yêu","hai người"],"bạn bè":["bạn bè","nhóm bạn","team"],"một mình":["một mình","solo"]}

def normalize_text(text):
    return re.sub(r"\s+"," ",text.lower().strip())

def tokenize(text):
    words=re.findall(r"[a-zA-ZÀ-ỹ0-9]+",normalize_text(text),flags=re.UNICODE)
    return [w for w in words if w not in STOP_WORDS and len(w)>1]

def extract_entities(text):
    t=normalize_text(text)
    r={"location":None,"type":None,"days":None,"budget":None,"people":None,"transport":None,"season":None,"group":None}
    for loc in LOCATIONS:
        if loc in t:r["location"]="sapa" if loc=="sa pa" else loc;break
    for typ,words in TYPE_SYNONYMS.items():
        if any(w in t for w in words):r["type"]=typ;break
    for k,words in TRANSPORT_KEYWORDS.items():
        if any(w in t for w in words):r["transport"]=k;break
    for k,words in SEASON_KEYWORDS.items():
        if any(w in t for w in words):r["season"]=k;break
    for k,words in GROUP_KEYWORDS.items():
        if any(w in t for w in words):r["group"]=k;break
    m=re.search(r"(\d+)\s*(ngày|đêm)",t)
    if m:r["days"]=int(m.group(1))
    m=re.search(r"(\d+)\s*(người|khách)",t)
    if m:r["people"]=int(m.group(1))
    m=re.search(r"(\d+(?:[.,]\d+)?)\s*(triệu|tr)",t)
    if m:r["budget"]=int(float(m.group(1).replace(",","."))*1_000_000)
    return r
