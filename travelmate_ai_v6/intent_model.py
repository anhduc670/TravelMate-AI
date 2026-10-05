import math
from collections import Counter,defaultdict
from nlp import tokenize

TRAINING_DATA={
"greeting":["xin chào","chào bạn","hello","hi","chào travelmate"],
"find_tour":["tư vấn tour","tìm tour","tôi muốn đi biển","gợi ý chuyến đi","tôi thích đi núi","tôi muốn nghỉ dưỡng","đề xuất tour"],
"ask_price":["giá bao nhiêu","bao nhiêu tiền","chi phí thế nào","tour có đắt không","giá tour"],
"ask_duration":["đi mấy ngày","tour bao lâu","thời gian tour","kéo dài mấy ngày"],
"ask_transport":["đi bằng gì","phương tiện là gì","đi máy bay hay ô tô","di chuyển bằng gì"],
"book_tour":["đặt tour","đăng ký tour","booking tour","tôi muốn đặt","chốt tour"],
"show_bookings":["xem tour đã đặt","lịch sử đặt tour","đơn của tôi","xem booking"],
"thanks":["cảm ơn","thank you","cảm ơn bạn","ok cảm ơn"]
}

class NaiveBayesIntentClassifier:
    def __init__(self):
        self.intent_docs=Counter();self.word_count=defaultdict(Counter);self.total_words=Counter();self.vocab=set();self.total_docs=0;self.fit()
    def fit(self):
        for intent,samples in TRAINING_DATA.items():
            for sample in samples:
                self.total_docs+=1;self.intent_docs[intent]+=1
                for token in tokenize(sample):
                    self.word_count[intent][token]+=1;self.total_words[intent]+=1;self.vocab.add(token)
    def predict(self,text):
        tokens=tokenize(text);V=max(1,len(self.vocab));scores={}
        for intent in TRAINING_DATA:
            score=math.log((self.intent_docs[intent]+1)/(self.total_docs+len(TRAINING_DATA)))
            for token in tokens:
                score+=math.log((self.word_count[intent][token]+1)/(self.total_words[intent]+V))
            scores[intent]=score
        best=max(scores,key=scores.get);vals=sorted(scores.values(),reverse=True)
        margin=vals[0]-vals[1] if len(vals)>1 else 10
        return best,1/(1+math.exp(-margin)),scores
MODEL=NaiveBayesIntentClassifier()
def predict_intent(text):return MODEL.predict(text)
