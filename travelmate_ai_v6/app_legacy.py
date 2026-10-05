import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from datetime import date
import shutil, uuid, csv, os, webbrowser

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE=True
except ImportError:
    PIL_AVAILABLE=False

from database import *
from context_manager import ConversationContext
from recommender import *
from itinerary_engine import itinerary_text
from evaluation import evaluate, evaluate_recommendation_system

BG="#F7F9FC";SIDEBAR="#111827";SIDEBAR_HOVER="#1F2937";CARD="#FFFFFF";TEXT="#111827";MUTED="#6B7280"
PRIMARY="#4F46E5";PRIMARY_2="#6366F1";SUCCESS="#059669";DANGER="#DC2626";WARNING="#D97706";BORDER="#E5E7EB";SOFT="#EEF2FF"
ASSET_DIR=Path(__file__).resolve().parent/"assets"

class App(tk.Tk):
    def __init__(self):
        super().__init__();init_db()
        self.title("TravelMate AI v5.2 Pro")
        self.geometry("1450x850");self.minsize(1200,720);self.configure(bg=BG)
        self.user=None;self.page=None;self.ctx=ConversationContext();self.image_cache={}
        s=ttk.Style(self)
        try:s.theme_use("clam")
        except tk.TclError:pass
        s.configure("Treeview",rowheight=30,font=("Segoe UI",10))
        s.configure("Treeview.Heading",font=("Segoe UI",10,"bold"))
        s.configure("TEntry",padding=7);s.configure("TCombobox",padding=6)
        self.show_login()

    def clear(self):
        for w in self.winfo_children():w.destroy()

    def load_tour_image(self,tour,size=(320,160)):
        filename=tour.get("image_path") or "default.ppm";key=(filename,size)
        if key in self.image_cache:return self.image_cache[key]
        path=ASSET_DIR/filename
        if not path.exists():path=ASSET_DIR/"default.ppm"
        try:
            if PIL_AVAILABLE:
                img=Image.open(path).convert("RGB").resize(size)
                photo=ImageTk.PhotoImage(img)
            else:
                photo=tk.PhotoImage(file=str(path))
            self.image_cache[key]=photo;return photo
        except Exception:
            try:
                photo=tk.PhotoImage(file=str(ASSET_DIR/"default.ppm"));self.image_cache[key]=photo;return photo
            except:return None

    def import_image(self,path):
        if not path:return None
        src=Path(path);ext=src.suffix.lower()
        if ext not in (".png",".jpg",".jpeg",".gif",".ppm"):raise ValueError("Chỉ hỗ trợ PNG/JPG/JPEG/GIF/PPM.")
        name=f"tour_{uuid.uuid4().hex[:12]}{ext}";shutil.copy2(src,ASSET_DIR/name);return name

    # ---------------- AUTH ----------------
    def show_login(self):
        self.clear();self.user=None;self.ctx.reset()
        out=tk.Frame(self,bg=BG);out.pack(fill="both",expand=True)
        card=tk.Frame(out,bg=CARD,highlightthickness=1,highlightbackground=BORDER)
        card.place(relx=.5,rely=.5,anchor="center",width=500,height=570)
        tk.Label(card,text="TRAVELMATE AI v5",bg=CARD,fg=PRIMARY,font=("Segoe UI",28,"bold")).pack(pady=(42,6))
        tk.Label(card,text="AI Travel Assistant • Full Edition",bg=CARD,fg=MUTED,font=("Segoe UI",10)).pack(pady=(0,30))
        form=tk.Frame(card,bg=CARD);form.pack(fill="x",padx=62)
        tk.Label(form,text="Tên đăng nhập",bg=CARD,fg=TEXT,font=("Segoe UI",10,"bold")).pack(anchor="w")
        user=ttk.Entry(form);user.pack(fill="x",pady=(6,15))
        tk.Label(form,text="Mật khẩu",bg=CARD,fg=TEXT,font=("Segoe UI",10,"bold")).pack(anchor="w")
        pwd=ttk.Entry(form,show="*");pwd.pack(fill="x",pady=(6,20))
        def login():
            u=authenticate(user.get(),pwd.get())
            if not u:messagebox.showerror("Đăng nhập","Sai tài khoản hoặc mật khẩu.");return
            self.user=u;self.ctx.reset();self.show_main()
        pwd.bind("<Return>",lambda e:login())
        tk.Button(form,text="ĐĂNG NHẬP",command=login,bg=PRIMARY,fg="white",bd=0,font=("Segoe UI",11,"bold"),pady=10).pack(fill="x")
        tk.Button(form,text="Tạo tài khoản mới",command=self.show_register,bg=CARD,fg=PRIMARY,bd=0).pack(pady=15)
        info=tk.Frame(card,bg=CARD)
        info.pack(side="bottom",pady=18)
        tk.Label(info,text="Admin: admin / admin123",bg=CARD,fg=MUTED,font=("Segoe UI",9)).pack()
        tk.Label(info,text="Khách hàng: khachhang / 123456",bg=CARD,fg=MUTED,font=("Segoe UI",9,"bold")).pack(pady=(4,0))

    def show_register(self):
        self.clear();out=tk.Frame(self,bg=BG);out.pack(fill="both",expand=True)
        card=tk.Frame(out,bg=CARD);card.place(relx=.5,rely=.5,anchor="center",width=500,height=600)
        tk.Label(card,text="TẠO TÀI KHOẢN",bg=CARD,fg=PRIMARY,font=("Segoe UI",22,"bold")).pack(pady=(35,25))
        form=tk.Frame(card,bg=CARD);form.pack(fill="x",padx=58)
        def field(label,show=None):
            tk.Label(form,text=label,bg=CARD,fg=TEXT,font=("Segoe UI",10,"bold")).pack(anchor="w")
            e=ttk.Entry(form,show=show);e.pack(fill="x",pady=(5,13));return e
        name=field("Họ và tên");username=field("Tên đăng nhập");pwd=field("Mật khẩu","*");confirm=field("Nhập lại","*")
        def sub():
            if pwd.get()!=confirm.get():messagebox.showerror("Đăng ký","Mật khẩu không khớp.");return
            ok,msg=register_user(name.get(),username.get(),pwd.get())
            if ok:messagebox.showinfo("Đăng ký",msg);self.show_login()
            else:messagebox.showerror("Đăng ký",msg)
        tk.Button(form,text="ĐĂNG KÝ",command=sub,bg=PRIMARY,fg="white",bd=0,pady=10).pack(fill="x")
        tk.Button(form,text="← Quay lại",command=self.show_login,bg=CARD,fg=PRIMARY,bd=0).pack(pady=10)

    # ---------------- LAYOUT ----------------
    def show_main(self):
        self.clear()
        sb=tk.Frame(self,bg=SIDEBAR,width=250);sb.pack(side="left",fill="y");sb.pack_propagate(False)
        self.content=tk.Frame(self,bg=BG);self.content.pack(side="left",fill="both",expand=True)
        tk.Label(sb,text="TravelMate AI",bg=SIDEBAR,fg="white",font=("Segoe UI",20,"bold")).pack(anchor="w",padx=20,pady=(22,3))
        tk.Label(sb,text="v5 • "+self.user["full_name"],bg=SIDEBAR,fg="#9CA3AF",font=("Segoe UI",9)).pack(anchor="w",padx=20,pady=(0,18))
        def nav(t,c):
            btn=tk.Button(
                sb,text=t,command=c,anchor="w",
                bg=SIDEBAR,fg="#E5E7EB",bd=0,
                activebackground=SIDEBAR_HOVER,activeforeground="white",
                font=("Segoe UI",9,"bold"),padx=20,pady=9,cursor="hand2"
            )
            btn.bind("<Enter>",lambda e,b=btn:b.configure(bg=SIDEBAR_HOVER,fg="white"))
            btn.bind("<Leave>",lambda e,b=btn:b.configure(bg=SIDEBAR,fg="#E5E7EB"))
            return btn
        nav("⌂  Tổng quan",self.dashboard).pack(fill="x")
        nav("✦  Chatbot AI",self.chatbot).pack(fill="x")
        nav("▦  Khám phá tour",self.tour_cards).pack(fill="x")
        nav("♥  Tour yêu thích",self.favorites_page).pack(fill="x")
        nav("⇄  So sánh tour",self.compare_page).pack(fill="x")
        nav("☷  Lịch trình AI",self.itinerary_page).pack(fill="x")
        nav("₫  Tính ngân sách",self.budget_page).pack(fill="x")
        nav("⌛  Lịch sử AI",self.history_page).pack(fill="x")
        nav("✓  Tour đã đặt",self.bookings).pack(fill="x")
        nav("★  Đánh giá tour",self.review_page).pack(fill="x")
        nav("🔔  Thông báo",self.notifications_page).pack(fill="x")
        nav("AI  Đánh giá mô hình",self.model_evaluation).pack(fill="x")
        nav("◎  Đánh giá hệ gợi ý",self.recommendation_evaluation_page).pack(fill="x")
        nav("◎  AI hoạt động thế nào?",self.ai_explain_page).pack(fill="x")
        if self.user["role"]=="admin":
            tk.Label(sb,text="QUẢN TRỊ",bg=SIDEBAR,fg="#6B7280",font=("Segoe UI",8,"bold")).pack(anchor="w",padx=20,pady=(12,3))
            nav("⚙  Quản lý tour",self.admin_tours).pack(fill="x")
            nav("▣  Quản lý đơn",self.admin_bookings).pack(fill="x")
            nav("♟  Quản lý khách",self.admin_customers).pack(fill="x")
            nav("▥  Thống kê",self.admin_analytics).pack(fill="x")
            nav("⇩  Xuất báo cáo",self.export_report_page).pack(fill="x")
        tk.Button(sb,text="⇥  Đăng xuất",command=self.show_login,bg=SIDEBAR,fg="#FCA5A5",bd=0,anchor="w",
                  font=("Segoe UI",9,"bold"),padx=20,pady=10).pack(side="bottom",fill="x")
        self.dashboard()

    def new_page(self,title,subtitle=""):
        if self.page:self.page.destroy()
        self.page=tk.Frame(self.content,bg=BG)
        self.page.pack(fill="both",expand=True)

        h=tk.Frame(self.page,bg=BG)
        h.pack(fill="x",padx=30,pady=(22,14))

        title_row=tk.Frame(h,bg=BG)
        title_row.pack(fill="x")

        accent=tk.Frame(title_row,bg=PRIMARY,width=6,height=34)
        accent.pack(side="left",padx=(0,12))
        accent.pack_propagate(False)

        tk.Label(
            title_row,text=title,bg=BG,fg=TEXT,
            font=("Segoe UI",22,"bold")
        ).pack(side="left")

        if subtitle:
            tk.Label(
                h,text=subtitle,bg=BG,fg=MUTED,
                font=("Segoe UI",10)
            ).pack(anchor="w",padx=18,pady=(4,0))

        return self.page

    # ---------------- DASHBOARD ----------------
    def dashboard(self):
        p=self.new_page("Tổng quan","TravelMate AI v5.1 Pro - trợ lý du lịch AI đa nhiệm")
        s=dashboard_stats();row=tk.Frame(p,bg=BG);row.pack(fill="x",padx=28,pady=4)
        data=[("Tour",s["tours"]),("Đơn",s["bookings"]),("Khách",s["users"]),("Doanh thu",money(s["revenue"])),("Điểm TB",f"{s['avg_rating']:.1f} ★")]
        for i,(lab,val) in enumerate(data):
            c=tk.Frame(row,bg=CARD,padx=15,pady=15,highlightthickness=1,highlightbackground=BORDER)
            c.grid(row=0,column=i,sticky="nsew",padx=(0 if i==0 else 7,0));row.grid_columnconfigure(i,weight=1)
            tk.Label(c,text=lab,bg=CARD,fg=MUTED,font=("Segoe UI",9)).pack(anchor="w")
            tk.Label(c,text=str(val),bg=CARD,fg=TEXT,font=("Segoe UI",16,"bold")).pack(anchor="w",pady=(5,0))
        hero=tk.Frame(p,bg=PRIMARY,padx=24,pady=18)
        hero.pack(fill="x",padx=28,pady=(12,0))
        tk.Label(hero,text="Lập kế hoạch chuyến đi thông minh hơn",bg=PRIMARY,fg="white",
                 font=("Segoe UI",17,"bold")).pack(anchor="w")
        tk.Label(hero,text="Hỏi tự nhiên → AI phân tích → Gợi ý → So sánh → Lịch trình → Đặt tour",
                 bg=PRIMARY,fg="#E0E7FF",font=("Segoe UI",10)).pack(anchor="w",pady=(4,0))

        box=tk.Frame(p,bg=CARD,padx=24,pady=20,highlightthickness=1,highlightbackground=BORDER);box.pack(fill="both",expand=True,padx=28,pady=15)
        tk.Label(box,text="Các tác vụ chính",bg=CARD,fg=TEXT,font=("Segoe UI",17,"bold")).pack(anchor="w")
        txt=("Chatbot AI • Gợi ý tour • Yêu thích • So sánh • Lịch trình AI • Tính ngân sách\n"
             "Đặt/hủy tour • Đánh giá sao • Lịch sử AI • Thông báo • Đánh giá mô hình\n"
             "Admin: quản lý tour/ảnh • đơn • khách hàng • thống kê nâng cao")
        tk.Label(box,text=txt,bg=CARD,fg=MUTED,justify="left",font=("Segoe UI",11)).pack(anchor="w",pady=12)
        tk.Button(box,text="Bắt đầu với Chatbot AI →",command=self.chatbot,bg=PRIMARY,fg="white",bd=0,padx=18,pady=9).pack(anchor="w")

    # ---------------- CHATBOT ----------------
    def chatbot(self):
        p=self.new_page("Chatbot AI","Hội thoại nhiều lượt + giải thích điểm + lưu lịch sử")
        body=tk.Frame(p,bg=BG);body.pack(fill="both",expand=True,padx=28,pady=(0,20))
        left=tk.Frame(body,bg=CARD,highlightthickness=1,highlightbackground=BORDER);left.pack(side="left",fill="both",expand=True)
        right=tk.Frame(body,bg=CARD,width=430,highlightthickness=1,highlightbackground=BORDER);right.pack(side="left",fill="y",padx=(12,0));right.pack_propagate(False)
        chat=tk.Text(left,wrap="word",bg=CARD,bd=0,padx=18,pady=18,state="disabled");chat.pack(fill="both",expand=True)
        inp=tk.Frame(left,bg=CARD);inp.pack(fill="x",padx=14,pady=14);entry=ttk.Entry(inp);entry.pack(side="left",fill="x",expand=True)
        ana=tk.Text(right,wrap="word",bg="#F8FAFC",bd=0,padx=12,pady=12,state="disabled");ana.pack(fill="both",expand=True,padx=12,pady=12)
        def append(s,m):
            chat.configure(state="normal");chat.insert("end",f"{s}: {m}\n\n");chat.configure(state="disabled");chat.see("end")
        append("TravelMate AI","Xin chào! Ví dụ: Tôi thích biển, 3 ngày, 4 triệu, mùa hè.")
        def send():
            q=entry.get().strip()
            if not q:return
            entry.delete(0,"end");append("Bạn",q)

            intent,conf,ent,_=analyze_message(q,self.ctx)
            non=answer_non_recommendation(intent,self.ctx)
            result=None

            if non and intent in ("greeting","thanks","show_bookings","ask_price","ask_duration","ask_transport","book_tour"):
                response=non
            else:
                follow_up=missing_information_prompt(self.ctx)

                # Ask for missing core information before ranking.
                if not enough_information_for_recommendation(self.ctx) and follow_up:
                    response=follow_up
                else:
                    result=recommend_from_context(q,self.ctx,5)
                    response=build_recommendation_answer(result,self.ctx)

                    # If core info is enough but another useful field is missing,
                    # append one optional follow-up question after recommendations.
                    if follow_up:
                        response += "\n\nĐể lọc chính xác hơn: " + follow_up

            append("TravelMate AI",response)

            top_id=top_score=None
            if result and result["results"]:
                top_id=result["results"][0]["tour"]["id"]
                top_score=result["results"][0]["score"]

            save_ai_history(self.user["id"],q,intent,response,top_id,top_score)

            ana.configure(state="normal")
            ana.delete("1.0","end")
            ana.insert("end", f"Intent: {intent}\nConfidence: {conf:.3f}\n\nEntities:\n")
            for k,v in ent.items():
                ana.insert("end", f"{k}: {v}\n")
            ana.insert("end", "\nContext:\n")
            for k,v in self.ctx.summary().items():
                ana.insert("end", f"{k}: {v}\n")
            if result:
                ana.insert("end", "\nTop scores:\n")
                for x in result["results"][:5]:
                    ana.insert("end", f"{x['tour']['name']}: {x['score']:.3f}\n")
            ana.configure(state="disabled")
        tk.Button(inp,text="Gửi",command=send,bg=PRIMARY,fg="white",bd=0,padx=18,pady=8).pack(side="left",padx=(8,0))
        tk.Button(right,text="Xóa ngữ cảnh",command=lambda:(self.ctx.reset(),append("TravelMate AI","Đã xóa ngữ cảnh.")),
                  bg="#EEF2FF",fg=PRIMARY,bd=0,pady=7).pack(fill="x",padx=12,pady=(0,12))
        entry.bind("<Return>",lambda e:send());entry.focus_set()

    # ---------------- TOURS/CARDS ----------------
    def tour_cards(self):
        p=self.new_page("Khám phá tour","Tìm kiếm, lọc, yêu thích và đặt tour")
        toolbar=tk.Frame(p,bg=BG);toolbar.pack(fill="x",padx=28,pady=(0,10))
        q=tk.StringVar();search=ttk.Entry(toolbar,textvariable=q);search.pack(side="left",fill="x",expand=True)
        typ=tk.StringVar(value="Tất cả");cb=ttk.Combobox(toolbar,textvariable=typ,state="readonly",width=17,values=["Tất cả","Biển","Núi","Nghỉ dưỡng","Khám phá","Văn hóa","Miền Tây"]);cb.pack(side="left",padx=(10,0))
        canvas=tk.Canvas(p,bg=BG,highlightthickness=0);scroll=ttk.Scrollbar(p,orient="vertical",command=canvas.yview);holder=tk.Frame(canvas,bg=BG)
        holder.bind("<Configure>",lambda e:canvas.configure(scrollregion=canvas.bbox("all")));canvas.create_window((0,0),window=holder,anchor="nw");canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left",fill="both",expand=True,padx=(28,0),pady=(0,20));scroll.pack(side="right",fill="y",padx=(0,18),pady=(0,20))
        def render(*_):
            for w in holder.winfo_children():w.destroy()
            query=q.get().lower().strip();selected=typ.get();lst=[]
            for t in get_all_tours():
                if query and query not in t["name"].lower() and query not in t["location"].lower():continue
                if selected!="Tất cả" and t["type"]!=selected:continue
                lst.append(t)
            for idx,t in enumerate(lst):
                r,c=divmod(idx,3);card=tk.Frame(holder,bg=CARD,width=330,height=365,highlightthickness=1,highlightbackground=BORDER)
                card.grid(row=r,column=c,padx=(0,14),pady=(0,14));card.grid_propagate(False)
                img=self.load_tour_image(t,(320,160))
                if img:tk.Label(card,image=img,bg=CARD).pack()
                body=tk.Frame(card,bg=CARD,padx=13,pady=9);body.pack(fill="both",expand=True)
                tk.Label(body,text=t["name"],bg=CARD,fg=TEXT,font=("Segoe UI",11,"bold"),wraplength=290,justify="left").pack(anchor="w")
                tk.Label(body,text=f"{t['location']} • {t['days']} ngày • {t['transport']}",bg=CARD,fg=MUTED,font=("Segoe UI",9)).pack(anchor="w",pady=(4,0))
                tk.Label(body,text=f"★ {float(t['avg_rating']):.1f} ({t['review_count']})",bg=CARD,fg="#B45309",font=("Segoe UI",9,"bold")).pack(anchor="w",pady=(3,0))
                tk.Label(body,text=money(t["price"]),bg=CARD,fg=PRIMARY,font=("Segoe UI",12,"bold")).pack(anchor="w",pady=(5,6))
                actions=tk.Frame(body,bg=CARD);actions.pack(fill="x")
                fav="♥" if is_favorite(self.user["id"],t["id"]) else "♡"
                tk.Button(actions,text=fav,command=lambda tid=t["id"]:self._toggle_fav(tid,render),bg="#FFF7ED",fg=DANGER,bd=0,padx=10,pady=6).pack(side="left")
                tk.Button(actions,text="Chi tiết",command=lambda tid=t["id"]:self.tour_detail(tid),bg="#EEF2FF",fg=PRIMARY,bd=0,padx=9,pady=6).pack(side="left",padx=5)
                tk.Button(actions,text="Đặt tour",command=lambda tid=t["id"]:self.open_booking(tid),bg=PRIMARY,fg="white",bd=0,padx=11,pady=6).pack(side="right")
        search.bind("<KeyRelease>",render);cb.bind("<<ComboboxSelected>>",render);render()

    def _toggle_fav(self,tid,refresh=None):
        state=toggle_favorite(self.user["id"],tid)
        messagebox.showinfo("Yêu thích","Đã thêm vào yêu thích." if state else "Đã bỏ khỏi yêu thích.")
        if refresh:refresh()

    def favorites_page(self):
        p=self.new_page("Tour yêu thích","Danh sách tour bạn đã lưu")
        tours=get_favorites(self.user["id"])
        f=tk.Frame(p,bg=CARD,highlightthickness=1,highlightbackground=BORDER);f.pack(fill="both",expand=True,padx=28,pady=(0,20))
        if not tours:
            tk.Label(f,text="Chưa có tour yêu thích.",bg=CARD,fg=MUTED,font=("Segoe UI",11)).pack(expand=True);return
        for t in tours:
            row=tk.Frame(f,bg="#F8FAFC",padx=14,pady=11);row.pack(fill="x",padx=15,pady=(12,0))
            tk.Label(row,text=t["name"],bg="#F8FAFC",fg=TEXT,font=("Segoe UI",11,"bold")).pack(side="left")
            tk.Label(row,text=f"{t['days']} ngày • {money(t['price'])}",bg="#F8FAFC",fg=MUTED).pack(side="left",padx=15)
            tk.Button(row,text="Bỏ ♥",command=lambda tid=t["id"]: (toggle_favorite(self.user["id"],tid),self.favorites_page()),bg=DANGER,fg="white",bd=0,padx=10,pady=5).pack(side="right")
            tk.Button(row,text="Chi tiết",command=lambda tid=t["id"]:self.tour_detail(tid),bg=PRIMARY,fg="white",bd=0,padx=10,pady=5).pack(side="right",padx=6)

    def tour_detail(self,tid):
        t=get_tour(tid)
        if not t:return
        w=tk.Toplevel(self);w.title(t["name"]);w.geometry("760x720");w.configure(bg=CARD)
        img=self.load_tour_image(t,(640,320))
        if img:tk.Label(w,image=img,bg=CARD).pack(pady=(15,8))
        tk.Label(w,text=t["name"],bg=CARD,fg=TEXT,font=("Segoe UI",18,"bold")).pack()
        tk.Label(w,text=f"{t['location']} • {t['type']} • {t['days']} ngày • {t['transport']} • {t['season']}",bg=CARD,fg=MUTED).pack(pady=4)
        tk.Label(w,text=money(t["price"]),bg=CARD,fg=PRIMARY,font=("Segoe UI",15,"bold")).pack()
        tk.Label(w,text=t["description"],bg=CARD,fg=TEXT,wraplength=680,justify="left").pack(anchor="w",padx=35,pady=10)
        btn=tk.Frame(w,bg=CARD);btn.pack(fill="x",padx=35,pady=8)
        tk.Button(btn,text="♥ Yêu thích",command=lambda:self._toggle_fav(tid),bg="#FFF7ED",fg=DANGER,bd=0,padx=14,pady=8).pack(side="left")
        tk.Button(btn,text="Lịch trình AI",command=lambda:self.show_itinerary(tid),bg=WARNING,fg="white",bd=0,padx=14,pady=8).pack(side="left",padx=8)
        tk.Button(btn,text="Đặt tour",command=lambda:self.open_booking(tid),bg=PRIMARY,fg="white",bd=0,padx=16,pady=8).pack(side="right")

    # ---------------- COMPARE ----------------
    def compare_page(self):
        p=self.new_page("So sánh tour","Chọn 2–3 tour để so sánh")
        body=tk.Frame(p,bg=BG);body.pack(fill="both",expand=True,padx=28,pady=(0,20))
        left=tk.Frame(body,bg=CARD,width=360,highlightthickness=1,highlightbackground=BORDER);left.pack(side="left",fill="y");left.pack_propagate(False)
        right=tk.Frame(body,bg=CARD,highlightthickness=1,highlightbackground=BORDER);right.pack(side="left",fill="both",expand=True,padx=(12,0))
        tours=get_all_tours();lb=tk.Listbox(left,selectmode="multiple",font=("Segoe UI",10))
        lb.pack(fill="both",expand=True,padx=12,pady=12)
        for t in tours:lb.insert("end",f"{t['name']} | {money(t['price'])}")
        tree_holder=tk.Frame(right,bg=CARD);tree_holder.pack(fill="both",expand=True,padx=12,pady=12)
        def compare():
            idx=list(lb.curselection())
            if len(idx)<2 or len(idx)>3:messagebox.showwarning("So sánh","Hãy chọn từ 2 đến 3 tour.");return
            for w in tree_holder.winfo_children():w.destroy()
            selected=[tours[i] for i in idx]
            cols=("field",)+tuple(f"t{i}" for i in range(len(selected)))
            tree=ttk.Treeview(tree_holder,columns=cols,show="headings")
            tree.heading("field",text="Tiêu chí");tree.column("field",width=150)
            for i,t in enumerate(selected):
                tree.heading(f"t{i}",text=t["name"]);tree.column(f"t{i}",width=190)
            rows=[
                ("Địa điểm",[t["location"] for t in selected]),("Loại",[t["type"] for t in selected]),
                ("Số ngày",[t["days"] for t in selected]),("Giá",[money(t["price"]) for t in selected]),
                ("Phương tiện",[t["transport"] for t in selected]),("Mùa",[t["season"] for t in selected]),
                ("Đánh giá",[f"{float(t['avg_rating']):.1f} ★" for t in selected])
            ]
            for label,vals in rows:tree.insert("", "end", values=(label,*vals))
            tree.pack(fill="both",expand=True)
        tk.Button(left,text="SO SÁNH",command=compare,bg=PRIMARY,fg="white",bd=0,pady=9).pack(fill="x",padx=12,pady=(0,12))

    # ---------------- ITINERARY ----------------
    def itinerary_page(self):
        p=self.new_page("Lịch trình AI","Chọn tour để tạo lịch trình tự động theo số ngày")
        top=tk.Frame(p,bg=BG);top.pack(fill="x",padx=28,pady=(0,10))
        tours=get_all_tours();names=[t["name"] for t in tours];var=tk.StringVar(value=names[0] if names else "")
        cb=ttk.Combobox(top,textvariable=var,state="readonly",values=names);cb.pack(side="left",fill="x",expand=True)
        text=tk.Text(p,wrap="word",bg=CARD,fg=TEXT,bd=0,font=("Segoe UI",10),padx=18,pady=18);text.pack(fill="both",expand=True,padx=28,pady=(0,20))
        def gen():
            if not tours:return
            t=next((x for x in tours if x["name"]==var.get()),tours[0]);content=itinerary_text(t)
            text.delete("1.0","end");text.insert("1.0",content)
        tk.Button(top,text="Tạo lịch trình",command=gen,bg=WARNING,fg="white",bd=0,padx=16,pady=8).pack(side="left",padx=(10,0));gen()

    def show_itinerary(self,tid):
        t=get_tour(tid);w=tk.Toplevel(self);w.title("Lịch trình AI");w.geometry("720x650")
        txt=tk.Text(w,wrap="word",font=("Segoe UI",10),padx=18,pady=18);txt.pack(fill="both",expand=True)
        txt.insert("1.0",itinerary_text(t));txt.configure(state="disabled")

    # ---------------- BUDGET ----------------
    def budget_page(self):
        p=self.new_page("Tính ngân sách","Ước tính tổng chi phí tour + chi tiêu phát sinh")
        box=tk.Frame(p,bg=CARD,padx=28,pady=24,highlightthickness=1,highlightbackground=BORDER);box.pack(fill="x",padx=28,pady=(0,20))
        tours=get_all_tours();names=[t["name"] for t in tours]
        def label(s):tk.Label(box,text=s,bg=CARD,fg=TEXT,font=("Segoe UI",10,"bold")).pack(anchor="w")
        label("Tour");tour_var=tk.StringVar(value=names[0] if names else "");ttk.Combobox(box,textvariable=tour_var,state="readonly",values=names).pack(fill="x",pady=(5,12))
        label("Người lớn");ad=ttk.Spinbox(box,from_=1,to=20);ad.set("1");ad.pack(anchor="w",pady=(5,12))
        label("Trẻ em (60% giá tour)");ch=ttk.Spinbox(box,from_=0,to=20);ch.set("0");ch.pack(anchor="w",pady=(5,12))
        label("Chi tiêu phát sinh / người / ngày");extra=ttk.Entry(box);extra.insert(0,"300000");extra.pack(fill="x",pady=(5,12))
        result=tk.Label(box,text="",bg=CARD,fg=SUCCESS,font=("Segoe UI",13,"bold"),justify="left");result.pack(anchor="w",pady=10)
        def calc():
            try:a=int(ad.get());c=int(ch.get());x=int(extra.get())
            except:messagebox.showerror("Ngân sách","Giá trị không hợp lệ.");return
            t=next((z for z in tours if z["name"]==tour_var.get()),tours[0])
            base=int(t["price"]*a+t["price"]*.6*c);personal=x*(a+c)*t["days"];total=base+personal
            result.config(text=f"Tiền tour: {money(base)}\nPhát sinh dự kiến: {money(personal)}\nTỔNG DỰ KIẾN: {money(total)}")
        tk.Button(box,text="TÍNH NGÂN SÁCH",command=calc,bg=PRIMARY,fg="white",bd=0,pady=9).pack(fill="x");calc()

    # ---------------- HISTORY ----------------
    def history_page(self):
        p=self.new_page("Lịch sử tư vấn AI","Các câu hỏi và tour từng được AI đề xuất")
        top=tk.Frame(p,bg=BG);top.pack(fill="x",padx=28,pady=(0,10))
        f=tk.Frame(p,bg=CARD);f.pack(fill="both",expand=True,padx=28,pady=(0,20))
        cols=("id","query","intent","top","score","date");tree=ttk.Treeview(f,columns=cols,show="headings")
        for k,l,w in [("id","ID",45),("query","Câu hỏi",330),("intent","Intent",110),("top","Top tour",230),("score","Điểm",80),("date","Thời gian",160)]:
            tree.heading(k,text=l);tree.column(k,width=w)
        tree.pack(fill="both",expand=True,padx=12,pady=12)
        for h in get_ai_history(self.user["id"]):
            tree.insert("", "end", values=(h["id"],h["query"],h["intent"],h["top_tour_name"] or "",f"{(h['top_score'] or 0)*100:.1f}%",h["created_at"]))
        tk.Button(top,text="Xóa lịch sử",command=lambda:(clear_ai_history(self.user["id"]),self.history_page()),bg=DANGER,fg="white",bd=0,padx=14,pady=7).pack(side="right")

    # ---------------- BOOKING ----------------
    def open_booking(self,tid):
        t=get_tour(tid)
        if not t:return
        w=tk.Toplevel(self);w.title("Đặt tour");w.geometry("540x650");w.configure(bg=CARD);w.transient(self);w.grab_set()
        tk.Label(w,text="ĐẶT TOUR",bg=CARD,fg=PRIMARY,font=("Segoe UI",18,"bold")).pack(anchor="w",padx=28,pady=(24,4))
        tk.Label(w,text=t["name"],bg=CARD,fg=TEXT,font=("Segoe UI",13,"bold")).pack(anchor="w",padx=28,pady=(0,15))
        form=tk.Frame(w,bg=CARD);form.pack(fill="x",padx=28)
        def field(label,default=""):
            tk.Label(form,text=label,bg=CARD,fg=TEXT,font=("Segoe UI",9,"bold")).pack(anchor="w")
            e=ttk.Entry(form);e.insert(0,default);e.pack(fill="x",pady=(4,10));return e
        name=field("Họ tên",self.user["full_name"]);phone=field("Số điện thoại")
        dep=field("Ngày khởi hành (YYYY-MM-DD)",str(date.today()))
        tk.Label(form,text="Người lớn",bg=CARD).pack(anchor="w");ad=ttk.Spinbox(form,from_=1,to=30);ad.set("1");ad.pack(anchor="w",pady=(4,10))
        tk.Label(form,text="Trẻ em",bg=CARD).pack(anchor="w");ch=ttk.Spinbox(form,from_=0,to=30);ch.set("0");ch.pack(anchor="w",pady=(4,10))
        tk.Label(form,text="Yêu cầu đặc biệt",bg=CARD).pack(anchor="w");note=tk.Text(form,height=4);note.pack(fill="x",pady=(4,12))
        total=tk.Label(form,bg=CARD,fg=SUCCESS,font=("Segoe UI",11,"bold"));total.pack(anchor="w",pady=5)
        def upd(*_):
            try:a=int(ad.get());c=int(ch.get());total.config(text="Tổng dự kiến: "+money(t["price"]*a+t["price"]*.6*c))
            except:pass
        ad.bind("<KeyRelease>",upd);ch.bind("<KeyRelease>",upd);upd()
        def submit():
            try:a=int(ad.get());c=int(ch.get())
            except:messagebox.showerror("Đặt tour","Số lượng không hợp lệ.");return
            ph=phone.get().strip()
            if len(ph)<9 or not ph.replace("+","").isdigit():messagebox.showerror("Đặt tour","SĐT không hợp lệ.");return
            code=create_booking(self.user["id"],tid,name.get().strip(),ph,a,c,dep.get().strip(),note.get("1.0","end").strip())
            messagebox.showinfo("Thành công",f"Đặt tour thành công.\nMã đơn: {code}");w.destroy()
        tk.Button(form,text="XÁC NHẬN ĐẶT TOUR",command=submit,bg=PRIMARY,fg="white",bd=0,pady=10).pack(fill="x",pady=10)

    def bookings(self):
        p=self.new_page("Tour đã đặt","Theo dõi đơn và tự hủy khi còn chờ xác nhận")
        f=tk.Frame(p,bg=CARD);f.pack(fill="both",expand=True,padx=28,pady=(0,20))
        cols=("id","code","tour","people","departure","total","status");tree=ttk.Treeview(f,columns=cols,show="headings")
        for k,l,w in [("id","ID",45),("code","Mã đơn",130),("tour","Tour",250),("people","Người",65),("departure","Khởi hành",100),("total","Tổng",130),("status","Trạng thái",130)]:
            tree.heading(k,text=l);tree.column(k,width=w)
        tree.pack(fill="both",expand=True,padx=12,pady=12)
        for b in get_user_bookings(self.user["id"]):
            tree.insert("", "end", values=(b["id"],b["booking_code"],b["tour_name"],b["people"],b["departure_date"] or "",money(b["total_price"]),b["status"]))
        def cancel():
            s=tree.selection()
            if not s:messagebox.showwarning("Hủy đơn","Chọn đơn.");return
            ok,msg=cancel_user_booking(int(tree.item(s[0],"values")[0]),self.user["id"])
            (messagebox.showinfo if ok else messagebox.showerror)("Hủy đơn",msg);self.bookings()
        tk.Button(f,text="Hủy đơn đã chọn",command=cancel,bg=DANGER,fg="white",bd=0,padx=14,pady=7).pack(anchor="e",padx=12,pady=(0,12))

    # ---------------- REVIEW ----------------
    def review_page(self):
        p=self.new_page("Đánh giá tour","Đánh giá 1–5 sao; điểm sao ảnh hưởng hệ gợi ý")
        f=tk.Frame(p,bg=CARD);f.pack(fill="both",expand=True,padx=28,pady=(0,20))
        confirmed=[b for b in get_user_bookings(self.user["id"]) if b["status"]=="Đã xác nhận"]
        if not confirmed:
            tk.Label(f,text="Chưa có tour đã xác nhận để đánh giá.",bg=CARD,fg=MUTED,font=("Segoe UI",11)).pack(expand=True);return
        for b in confirmed:
            row=tk.Frame(f,bg="#F8FAFC",padx=14,pady=11);row.pack(fill="x",padx=15,pady=(12,0))
            tk.Label(row,text=b["tour_name"],bg="#F8FAFC",fg=TEXT,font=("Segoe UI",11,"bold")).pack(side="left")
            tk.Button(row,text="Đánh giá",command=lambda tid=b["tour_id"]:self.open_review(tid),bg=WARNING,fg="white",bd=0,padx=12,pady=6).pack(side="right")

    def open_review(self,tid):
        t=get_tour(tid);w=tk.Toplevel(self);w.title("Đánh giá");w.geometry("480x420");w.configure(bg=CARD);w.grab_set()
        tk.Label(w,text=t["name"],bg=CARD,fg=TEXT,font=("Segoe UI",15,"bold")).pack(anchor="w",padx=28,pady=(25,15))
        form=tk.Frame(w,bg=CARD);form.pack(fill="x",padx=28)
        tk.Label(form,text="Số sao",bg=CARD).pack(anchor="w");rating=ttk.Combobox(form,state="readonly",values=[1,2,3,4,5]);rating.set(5);rating.pack(fill="x",pady=(5,12))
        tk.Label(form,text="Nhận xét",bg=CARD).pack(anchor="w");comment=tk.Text(form,height=7);comment.pack(fill="x",pady=(5,15))
        def save():
            save_review(self.user["id"],tid,int(rating.get()),comment.get("1.0","end").strip());messagebox.showinfo("Cảm ơn","Đã lưu đánh giá.");w.destroy()
        tk.Button(form,text="GỬI ĐÁNH GIÁ",command=save,bg=WARNING,fg="white",bd=0,pady=10).pack(fill="x")

    # ---------------- NOTIFICATIONS ----------------
    def notifications_page(self):
        p=self.new_page("Thông báo",f"Bạn có {unread_notification_count(self.user['id'])} thông báo chưa đọc")
        mark_notifications_read(self.user["id"])
        f=tk.Frame(p,bg=CARD);f.pack(fill="both",expand=True,padx=28,pady=(0,20))
        items=get_notifications(self.user["id"])
        if not items:tk.Label(f,text="Chưa có thông báo.",bg=CARD,fg=MUTED).pack(expand=True);return
        for n in items:
            row=tk.Frame(f,bg="#F8FAFC",padx=14,pady=10);row.pack(fill="x",padx=14,pady=(10,0))
            tk.Label(row,text=n["title"],bg="#F8FAFC",fg=TEXT,font=("Segoe UI",10,"bold")).pack(anchor="w")
            tk.Label(row,text=n["message"],bg="#F8FAFC",fg=MUTED,wraplength=800,justify="left").pack(anchor="w",pady=(3,0))
            tk.Label(row,text=n["created_at"],bg="#F8FAFC",fg="#9CA3AF",font=("Segoe UI",8)).pack(anchor="e")

    # ---------------- MODEL EVAL ----------------
    def model_evaluation(self):
        p=self.new_page("Đánh giá mô hình AI","Accuracy / Precision / Recall / F1 / Confusion Matrix + câu dự đoán sai")
        r=evaluate();row=tk.Frame(p,bg=BG);row.pack(fill="x",padx=28,pady=(0,10))
        for i,(lab,val) in enumerate([("Accuracy",r["accuracy"]),("Macro Precision",r["macro_precision"]),("Macro Recall",r["macro_recall"]),("Macro F1",r["macro_f1"])]):
            c=tk.Frame(row,bg=CARD,padx=15,pady=14);c.grid(row=0,column=i,sticky="nsew",padx=(0 if i==0 else 7,0));row.grid_columnconfigure(i,weight=1)
            tk.Label(c,text=lab,bg=CARD,fg=MUTED).pack(anchor="w");tk.Label(c,text=f"{val*100:.1f}%",bg=CARD,fg=TEXT,font=("Segoe UI",17,"bold")).pack(anchor="w")
        body=tk.Frame(p,bg=CARD);body.pack(fill="both",expand=True,padx=28,pady=(0,20))
        txt=tk.Text(body,wrap="none",font=("Consolas",9),bg="#F8FAFC",bd=0);txt.pack(fill="both",expand=True,padx=12,pady=12)
        txt.insert("end","Intent                 Precision  Recall     F1\n"+"-"*55+"\n")
        for lab in r["labels"]:
            pr,re,f1=r["metrics"][lab];txt.insert("end",f"{lab:<22} {pr:<10.3f} {re:<10.3f} {f1:.3f}\n")
        txt.insert("end","\nCÁC CÂU DỰ ĐOÁN SAI\n"+"-"*55+"\n")
        if not r["errors"]:txt.insert("end","Không có lỗi trên bộ test hiện tại.\n")
        for text,actual,pred,conf in r["errors"]:txt.insert("end",f"- {text}\n  actual={actual}, predicted={pred}, confidence={conf:.3f}\n")
        txt.configure(state="disabled")

    # ---------------- ADMIN TOUR ----------------
    def admin_tours(self):
        p=self.new_page("Quản lý tour","CRUD tour + chọn ảnh từ máy")
        top=tk.Frame(p,bg=BG);top.pack(fill="x",padx=28,pady=(0,10))
        f=tk.Frame(p,bg=CARD);f.pack(fill="both",expand=True,padx=28,pady=(0,20))
        cols=("id","name","location","type","days","price","image");tree=ttk.Treeview(f,columns=cols,show="headings")
        for k,l,w in [("id","ID",45),("name","Tên tour",260),("location","Địa điểm",110),("type","Loại",100),("days","Ngày",55),("price","Giá",120),("image","Ảnh",200)]:
            tree.heading(k,text=l);tree.column(k,width=w)
        tree.pack(fill="both",expand=True,padx=12,pady=12)
        def reload():
            for x in tree.get_children():tree.delete(x)
            for t in get_all_tours():tree.insert("", "end", values=(t["id"],t["name"],t["location"],t["type"],t["days"],money(t["price"]),t["image_path"]))
        def dialog(edit_id=None):
            t=get_tour(edit_id) if edit_id else None;w=tk.Toplevel(self);w.title("Sửa tour" if t else "Thêm tour");w.geometry("620x760");w.configure(bg=CARD);w.grab_set()
            bottom=tk.Frame(w,bg=CARD);bottom.pack(side="bottom",fill="x",padx=24,pady=14)
            save_btn=tk.Button(bottom,text="LƯU THÔNG TIN",bg=PRIMARY,fg="white",bd=0,pady=10);save_btn.pack(fill="x")
            canvas=tk.Canvas(w,bg=CARD,highlightthickness=0);scroll=ttk.Scrollbar(w,orient="vertical",command=canvas.yview);canvas.pack(side="left",fill="both",expand=True);scroll.pack(side="right",fill="y")
            form=tk.Frame(canvas,bg=CARD);wid=canvas.create_window((0,0),window=form,anchor="nw")
            form.bind("<Configure>",lambda e:canvas.configure(scrollregion=canvas.bbox("all")));canvas.bind("<Configure>",lambda e:canvas.itemconfigure(wid,width=e.width));canvas.configure(yscrollcommand=scroll.set)
            inner=tk.Frame(form,bg=CARD);inner.pack(fill="both",expand=True,padx=28,pady=20)
            def ef(label,value=""):
                tk.Label(inner,text=label,bg=CARD,fg=TEXT,font=("Segoe UI",9,"bold")).pack(anchor="w");e=ttk.Entry(inner);e.insert(0,str(value));e.pack(fill="x",pady=(4,8));return e
            name=ef("Tên tour",t["name"] if t else "");loc=ef("Địa điểm",t["location"] if t else "");typ=ef("Loại",t["type"] if t else "")
            days=ef("Số ngày",t["days"] if t else "");price=ef("Giá",t["price"] if t else "");transport=ef("Phương tiện",t["transport"] if t else "")
            season=ef("Mùa",t["season"] if t else "quanh năm");aud=ef("Nhóm khách",t["audience"] if t else "gia đình,bạn bè")
            image_var=tk.StringVar(value=t["image_path"] if t else "default.ppm")
            tk.Label(inner,text="Ảnh tour",bg=CARD,fg=TEXT,font=("Segoe UI",9,"bold")).pack(anchor="w");ir=tk.Frame(inner,bg=CARD);ir.pack(fill="x",pady=(4,8))
            ttk.Entry(ir,textvariable=image_var,state="readonly").pack(side="left",fill="x",expand=True);preview=tk.Label(inner,bg="#F8FAFC");preview.pack(pady=5)
            def refresh():
                img=self.load_tour_image({"image_path":image_var.get()},(300,150));preview.configure(image=img);preview.image=img
            def choose():
                path=filedialog.askopenfilename(filetypes=[("Images","*.png *.jpg *.jpeg *.gif *.ppm")])
                if path:
                    try:image_var.set(self.import_image(path));self.image_cache.clear();refresh()
                    except Exception as ex:messagebox.showerror("Ảnh",str(ex))
            tk.Button(ir,text="Chọn ảnh...",command=choose,bg="#EEF2FF",fg=PRIMARY,bd=0,padx=10).pack(side="left",padx=(8,0));refresh()
            tk.Label(inner,text="Mô tả",bg=CARD).pack(anchor="w");desc=tk.Text(inner,height=5);desc.pack(fill="x",pady=(4,12))
            if t:desc.insert("1.0",t["description"])
            def save():
                try:d=int(days.get());pr=int(price.get())
                except:messagebox.showerror("Lỗi","Số ngày/giá không hợp lệ.");return
                args=(name.get().strip(),loc.get().strip(),typ.get().strip(),d,pr,transport.get().strip(),season.get().strip(),aud.get().strip(),image_var.get().strip() or "default.ppm",desc.get("1.0","end").strip())
                if t:update_tour(t["id"],*args)
                else:add_tour(*args)
                self.image_cache.clear();messagebox.showinfo("Thành công","Đã lưu tour.");w.destroy();reload()
            save_btn.configure(command=save)
        def edit():
            s=tree.selection()
            if s:dialog(int(tree.item(s[0],"values")[0]))
        def hide():
            s=tree.selection()
            if s and messagebox.askyesno("Xác nhận","Ẩn tour?"):delete_tour(int(tree.item(s[0],"values")[0]));reload()
        tk.Button(top,text="+ Thêm tour",command=lambda:dialog(),bg=PRIMARY,fg="white",bd=0,padx=14,pady=7).pack(side="left")
        tk.Button(top,text="Sửa",command=edit,bg=CARD,fg=TEXT,bd=0,padx=14,pady=7).pack(side="left",padx=7)
        tk.Button(top,text="Ẩn",command=hide,bg=DANGER,fg="white",bd=0,padx=14,pady=7).pack(side="left");reload()

    # ---------------- ADMIN BOOKING ----------------
    def admin_bookings(self):
        p=self.new_page("Quản lý đơn","Xác nhận / hủy đơn và gửi thông báo cho khách")
        f=tk.Frame(p,bg=CARD);f.pack(fill="both",expand=True,padx=28,pady=(0,20))
        cols=("id","code","user","tour","departure","total","status");tree=ttk.Treeview(f,columns=cols,show="headings")
        for k,l,w in [("id","ID",45),("code","Mã",125),("user","User",100),("tour","Tour",230),("departure","Khởi hành",100),("total","Tổng",130),("status","Trạng thái",125)]:
            tree.heading(k,text=l);tree.column(k,width=w)
        tree.pack(fill="both",expand=True,padx=12,pady=12);ctl=tk.Frame(f,bg=CARD);ctl.pack(fill="x",padx=12,pady=(0,12))
        def reload():
            for x in tree.get_children():tree.delete(x)
            for b in get_all_bookings():tree.insert("", "end", values=(b["id"],b["booking_code"],b["username"],b["tour_name"],b["departure_date"] or "",money(b["total_price"]),b["status"]))
        def status(v):
            s=tree.selection()
            if not s:return
            update_booking_status(int(tree.item(s[0],"values")[0]),v);reload()
        tk.Button(ctl,text="Xác nhận",command=lambda:status("Đã xác nhận"),bg=SUCCESS,fg="white",bd=0,padx=14,pady=7).pack(side="left")
        tk.Button(ctl,text="Hủy",command=lambda:status("Đã hủy"),bg=DANGER,fg="white",bd=0,padx=14,pady=7).pack(side="left",padx=7)
        tk.Button(ctl,text="Chờ",command=lambda:status("Chờ xác nhận"),bg=WARNING,fg="white",bd=0,padx=14,pady=7).pack(side="left");reload()

    # ---------------- ADMIN CUSTOMERS ----------------
    def admin_customers(self):
        p=self.new_page("Quản lý khách hàng","Theo dõi tài khoản, số đơn và tổng chi tiêu")
        f=tk.Frame(p,bg=CARD);f.pack(fill="both",expand=True,padx=28,pady=(0,20))
        cols=("id","name","username","bookings","spent","created");tree=ttk.Treeview(f,columns=cols,show="headings")
        for k,l,w in [("id","ID",50),("name","Họ tên",220),("username","Tài khoản",150),("bookings","Số đơn",80),("spent","Đã chi",150),("created","Ngày tạo",170)]:
            tree.heading(k,text=l);tree.column(k,width=w)
        tree.pack(fill="both",expand=True,padx=12,pady=12)
        for u in get_users_summary():tree.insert("", "end", values=(u["id"],u["full_name"],u["username"],u["booking_count"],money(u["total_spent"]),u["created_at"]))

    # ---------------- ANALYTICS ----------------
    def admin_analytics(self):
        p=self.new_page("Thống kê nâng cao","Đơn, doanh thu, loại tour và top tour")
        body=tk.Frame(p,bg=BG);body.pack(fill="both",expand=True,padx=28,pady=(0,20))
        canvases=[]
        datasets=[("Đơn theo trạng thái",booking_status_stats()),("Top tour",[(x["name"],x["count"]) for x in top_tour_stats(6)]),
                  ("Doanh thu theo tháng",[(m,int(v/1000000)) for m,v in revenue_by_month(6)]),("Loại tour phổ biến",tour_type_stats())]
        for i,(title,data) in enumerate(datasets):
            f=tk.Frame(body,bg=CARD,highlightthickness=1,highlightbackground=BORDER);f.grid(row=i//2,column=i%2,sticky="nsew",padx=(0 if i%2==0 else 7,7 if i%2==0 else 0),pady=(0,12))
            body.grid_rowconfigure(i//2,weight=1);body.grid_columnconfigure(i%2,weight=1)
            tk.Label(f,text=title,bg=CARD,fg=TEXT,font=("Segoe UI",12,"bold")).pack(anchor="w",padx=12,pady=(12,4))
            c=tk.Canvas(f,bg=CARD,highlightthickness=0,height=270);c.pack(fill="both",expand=True,padx=10,pady=8);self.draw_bar(c,data);c.bind("<Configure>",lambda e,cc=c,dd=data:self.draw_bar(cc,dd))
    def draw_bar(self,c,data):
        c.update_idletasks();w=max(430,c.winfo_width());h=max(250,c.winfo_height());c.delete("all")
        if not data:c.create_text(w/2,h/2,text="Chưa có dữ liệu",fill=MUTED);return
        mx=max(v for _,v in data) or 1;left=50;bottom=h-55;top=25;slot=(w-left-20)/len(data);bw=max(25,min(65,slot*.55))
        c.create_line(left,top,left,bottom,fill="#CBD5E1");c.create_line(left,bottom,w-20,bottom,fill="#CBD5E1")
        for i,(lab,val) in enumerate(data):
            x=left+slot*i+slot/2;bh=(bottom-top-30)*(val/mx)
            c.create_rectangle(x-bw/2,bottom-bh,x+bw/2,bottom,fill=PRIMARY,outline="")
            c.create_text(x,bottom-bh-11,text=str(val),fill=TEXT,font=("Segoe UI",8,"bold"))
            show=lab if len(lab)<=13 else lab[:11]+"…";c.create_text(x,bottom+17,text=show,fill=MUTED,font=("Segoe UI",7))


    # ---------------- AI EXPLAIN ----------------
    def ai_explain_page(self):
        p=self.new_page(
            "AI hoạt động thế nào?",
            "Minh họa toàn bộ pipeline xử lý từ câu người dùng đến tour được đề xuất"
        )

        body=tk.Frame(p,bg=BG)
        body.pack(fill="both",expand=True,padx=28,pady=(0,20))

        left=tk.Frame(body,bg=CARD,highlightthickness=1,highlightbackground=BORDER)
        left.pack(side="left",fill="both",expand=True,padx=(0,7))

        right=tk.Frame(body,bg=CARD,highlightthickness=1,highlightbackground=BORDER)
        right.pack(side="left",fill="both",expand=True,padx=(7,0))

        tk.Label(
            left,text="Pipeline AI",
            bg=CARD,fg=TEXT,font=("Segoe UI",15,"bold")
        ).pack(anchor="w",padx=20,pady=(18,12))

        steps=[
            ("1","Câu hỏi người dùng","Ngôn ngữ tự nhiên"),
            ("2","Entity Extraction","Địa điểm, số ngày, ngân sách, người, mùa..."),
            ("3","Naive Bayes Intent","Nhận diện mục đích câu hỏi"),
            ("4","Conversation Context","Nhớ thông tin nhiều lượt"),
            ("5","Expert Rules IF–THEN","Suy diễn sở thích"),
            ("6","TF-IDF","Biểu diễn câu hỏi và tour thành vector"),
            ("7","Cosine Similarity","Đo độ tương đồng nội dung"),
            ("8","Weighted Scoring","Kết hợp ngân sách, ngày, sở thích, rating..."),
            ("9","Ranking + Explainable AI","Xếp hạng và giải thích kết quả")
        ]

        for no,title,desc in steps:
            row=tk.Frame(left,bg="#F8FAFC",padx=12,pady=10)
            row.pack(fill="x",padx=18,pady=(0,8))
            badge=tk.Label(
                row,text=no,bg=PRIMARY,fg="white",
                width=3,font=("Segoe UI",9,"bold")
            )
            badge.pack(side="left",padx=(0,10))
            txt=tk.Frame(row,bg="#F8FAFC")
            txt.pack(side="left",fill="x",expand=True)
            tk.Label(txt,text=title,bg="#F8FAFC",fg=TEXT,font=("Segoe UI",10,"bold")).pack(anchor="w")
            tk.Label(txt,text=desc,bg="#F8FAFC",fg=MUTED,font=("Segoe UI",9),wraplength=430,justify="left").pack(anchor="w")

        tk.Label(
            right,text="Công thức chấm điểm",
            bg=CARD,fg=TEXT,font=("Segoe UI",15,"bold")
        ).pack(anchor="w",padx=20,pady=(18,12))

        formula=(
            "Score = 0.30 × Semantic\\n"
            "      + 0.20 × Preference\\n"
            "      + 0.12 × Budget\\n"
            "      + 0.10 × Duration\\n"
            "      + 0.08 × Transport\\n"
            "      + 0.08 × Season\\n"
            "      + 0.05 × Group\\n"
            "      + 0.07 × Rating"
        )

        tk.Label(
            right,text=formula,bg="#F8FAFC",fg=PRIMARY,
            justify="left",font=("Consolas",12,"bold"),
            padx=18,pady=18
        ).pack(fill="x",padx=18)

        tk.Label(
            right,text="Ví dụ demo",
            bg=CARD,fg=TEXT,font=("Segoe UI",13,"bold")
        ).pack(anchor="w",padx=20,pady=(18,8))

        demo=(
            'Người dùng: "Tôi thích biển, 3 ngày, khoảng 4 triệu"\\n\\n'
            "→ type = Biển\\n"
            "→ days = 3\\n"
            "→ budget = 4.000.000\\n"
            "→ Intent = find_tour\\n"
            "→ TF-IDF/Cosine so sánh với từng tour\\n"
            "→ Weighted Score\\n"
            "→ Xếp hạng + giải thích lý do"
        )

        tk.Label(
            right,text=demo,bg=CARD,fg=MUTED,
            justify="left",wraplength=460,font=("Segoe UI",10)
        ).pack(anchor="w",padx=20)

    # ---------------- RECOMMENDER EVALUATION ----------------
    def recommendation_evaluation_page(self):
        p=self.new_page(
            "Đánh giá hệ gợi ý",
            "Top-1 Accuracy và Top-3 Accuracy trên bộ tình huống tư vấn mẫu"
        )
        r=evaluate_recommendation_system()

        cards=tk.Frame(p,bg=BG)
        cards.pack(fill="x",padx=28,pady=(0,12))

        data=[
            ("Số tình huống",r["total"]),
            ("Top-1 Accuracy",f"{r['top1_accuracy']*100:.1f}%"),
            ("Top-3 Accuracy",f"{r['top3_accuracy']*100:.1f}%")
        ]

        for i,(lab,val) in enumerate(data):
            c=tk.Frame(cards,bg=CARD,padx=18,pady=15,highlightthickness=1,highlightbackground=BORDER)
            c.grid(row=0,column=i,sticky="nsew",padx=(0 if i==0 else 8,0))
            cards.grid_columnconfigure(i,weight=1)
            tk.Label(c,text=lab,bg=CARD,fg=MUTED,font=("Segoe UI",9)).pack(anchor="w")
            tk.Label(c,text=str(val),bg=CARD,fg=TEXT,font=("Segoe UI",18,"bold")).pack(anchor="w",pady=(5,0))

        f=tk.Frame(p,bg=CARD,highlightthickness=1,highlightbackground=BORDER)
        f.pack(fill="both",expand=True,padx=28,pady=(0,20))

        cols=("query","expected","top1","top3","ok1","ok3")
        tree=ttk.Treeview(f,columns=cols,show="headings")
        specs=[
            ("query","Câu hỏi",280),("expected","Tour mong đợi",240),
            ("top1","Top 1",220),("top3","Top 3",340),
            ("ok1","Top1",60),("ok3","Top3",60)
        ]
        for k,l,w in specs:
            tree.heading(k,text=l);tree.column(k,width=w)
        tree.pack(fill="both",expand=True,padx=12,pady=12)

        for row in r["rows"]:
            tree.insert("", "end", values=(
                row["query"],row["expected"],row["top1"],row["top3"],
                "✓" if row["top1_ok"] else "✗",
                "✓" if row["top3_ok"] else "✗"
            ))

    # ---------------- EXPORT REPORTS ----------------
    def export_report_page(self):
        p=self.new_page(
            "Xuất báo cáo",
            "Xuất dữ liệu quản trị và kết quả AI ra CSV để mở bằng Excel"
        )

        box=tk.Frame(p,bg=CARD,padx=26,pady=24,highlightthickness=1,highlightbackground=BORDER)
        box.pack(fill="x",padx=28,pady=(0,20))

        tk.Label(
            box,text="Báo cáo có thể xuất",
            bg=CARD,fg=TEXT,font=("Segoe UI",16,"bold")
        ).pack(anchor="w")

        tk.Label(
            box,
            text=(
                "• Danh sách tour\\n"
                "• Danh sách đơn đặt tour\\n"
                "• Khách hàng\\n"
                "• Kết quả đánh giá mô hình Intent\\n"
                "• Kết quả đánh giá hệ gợi ý Top-1 / Top-3"
            ),
            bg=CARD,fg=MUTED,justify="left",
            font=("Segoe UI",10)
        ).pack(anchor="w",pady=(10,18))

        status=tk.Label(box,text="",bg=CARD,fg=SUCCESS,font=("Segoe UI",10,"bold"))
        status.pack(anchor="w",pady=(8,0))

        def save_csv(filename,headers,rows):
            folder=filedialog.askdirectory(title="Chọn thư mục lưu báo cáo")
            if not folder:
                return None
            path=Path(folder)/filename
            with open(path,"w",newline="",encoding="utf-8-sig") as f:
                writer=csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
            status.config(text=f"Đã xuất: {path}")
            return path

        def export_tours():
            tours=get_all_tours()
            rows=[[
                t["id"],t["name"],t["location"],t["type"],t["days"],t["price"],
                t["transport"],t["season"],t["audience"],t["avg_rating"],t["review_count"]
            ] for t in tours]
            save_csv(
                "travelmate_tours.csv",
                ["ID","Tên tour","Địa điểm","Loại","Số ngày","Giá","Phương tiện","Mùa","Nhóm khách","Rating","Số đánh giá"],
                rows
            )

        def export_bookings():
            rows=[[
                b["booking_code"],b["username"],b["tour_name"],b["people"],
                b["departure_date"],b["total_price"],b["status"],b["created_at"]
            ] for b in get_all_bookings()]
            save_csv(
                "travelmate_bookings.csv",
                ["Mã đơn","Tài khoản","Tour","Số người","Khởi hành","Tổng tiền","Trạng thái","Ngày tạo"],
                rows
            )

        def export_users():
            rows=[[
                u["id"],u["full_name"],u["username"],u["booking_count"],u["total_spent"],u["created_at"]
            ] for u in get_users_summary()]
            save_csv(
                "travelmate_customers.csv",
                ["ID","Họ tên","Tài khoản","Số đơn","Tổng chi","Ngày tạo"],
                rows
            )

        def export_ai():
            r=evaluate()
            rows=[]
            for lab in r["labels"]:
                pr,re_,f1=r["metrics"][lab]
                rows.append([lab,pr,re_,f1])
            save_csv(
                "travelmate_intent_metrics.csv",
                ["Intent","Precision","Recall","F1"],
                rows
            )

        def export_rec():
            r=evaluate_recommendation_system()
            rows=[[
                x["query"],x["expected"],x["top1"],x["top3"],x["top1_ok"],x["top3_ok"]
            ] for x in r["rows"]]
            save_csv(
                "travelmate_recommendation_eval.csv",
                ["Câu hỏi","Mong đợi","Top1","Top3","Top1 đúng","Top3 đúng"],
                rows
            )

        buttons=[
            ("Xuất danh sách tour",export_tours),
            ("Xuất đơn đặt tour",export_bookings),
            ("Xuất khách hàng",export_users),
            ("Xuất đánh giá Intent",export_ai),
            ("Xuất đánh giá hệ gợi ý",export_rec)
        ]

        grid=tk.Frame(box,bg=CARD)
        grid.pack(fill="x")

        for i,(label,cmd) in enumerate(buttons):
            tk.Button(
                grid,text=label,command=cmd,
                bg=PRIMARY if i<3 else PRIMARY_2,
                fg="white",bd=0,
                font=("Segoe UI",9,"bold"),
                padx=14,pady=9,cursor="hand2"
            ).grid(row=i//2,column=i%2,sticky="ew",padx=(0 if i%2==0 else 6,6 if i%2==0 else 0),pady=5)
            grid.grid_columnconfigure(i%2,weight=1)

if __name__=="__main__":
    App().mainloop()
