import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from app_legacy import App as LegacyApp
from database import (
    init_db, authenticate, register_user, dashboard_stats,
    unread_notification_count, get_all_tours, is_favorite,
    toggle_favorite, save_ai_history
)
from context_manager import ConversationContext
from recommender import (
    analyze_message, answer_non_recommendation,
    recommend_from_context, build_recommendation_answer,
    missing_information_prompt, enough_information_for_recommendation,
    money
)

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

BG = ("#F7F9FC", "#0F172A")
CARD = ("#FFFFFF", "#111827")
CARD_ALT = ("#F8FAFC", "#172033")
TEXT = ("#111827", "#F8FAFC")
MUTED = ("#6B7280", "#94A3B8")
SIDEBAR = ("#111827", "#0B1120")
PRIMARY = "#4F46E5"
PRIMARY_HOVER = "#4338CA"
SOFT = ("#EEF2FF", "#1E293B")
BORDER = ("#E5E7EB", "#263244")
SUCCESS = "#059669"
WARNING = "#D97706"
DANGER = "#DC2626"


class App(LegacyApp):
    """
    Modern UI shell for TravelMate AI.
    All business logic / AI / database features from v5.2 are preserved
    through inheritance from app_legacy.App.
    """

    def __init__(self):
        # LegacyApp.__init__ will initialize database, styles and call
        # self.show_login(). Because of polymorphism, the modern login below
        # is used automatically.
        super().__init__()
        self.title("TravelMate AI v6 — Modern UI")
        self.geometry("1500x900")
        self.minsize(1180, 720)
        self.appearance_mode = "light"
        self.nav_buttons = {}
        self.active_nav = None

    # -------------------- LOGIN --------------------
    def show_login(self):
        self.clear()
        self.user = None
        self.ctx.reset()

        root = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        root.pack(fill="both", expand=True)

        visual = ctk.CTkFrame(root, fg_color=PRIMARY, corner_radius=0)
        visual.pack(side="left", fill="both", expand=True)

        panel = ctk.CTkFrame(root, fg_color=CARD, corner_radius=0, width=530)
        panel.pack(side="right", fill="y")
        panel.pack_propagate(False)

        branding = ctk.CTkFrame(visual, fg_color="transparent")
        branding.place(relx=.5, rely=.5, anchor="center")

        ctk.CTkLabel(
            branding, text="✦",
            text_color="#C7D2FE",
            font=ctk.CTkFont(size=52, weight="bold")
        ).pack()

        ctk.CTkLabel(
            branding, text="TRAVELMATE AI",
            text_color="white",
            font=ctk.CTkFont(size=38, weight="bold")
        ).pack(pady=(4, 6))

        ctk.CTkLabel(
            branding,
            text="Trợ lý du lịch thông minh bằng AI",
            text_color="#E0E7FF",
            font=ctk.CTkFont(size=17)
        ).pack()

        ctk.CTkLabel(
            branding,
            text="Tư vấn • So sánh • Lập lịch trình\nĐặt tour • Đánh giá • Học máy",
            justify="left",
            text_color="#E0E7FF",
            font=ctk.CTkFont(size=13)
        ).pack(pady=(26, 0))

        form = ctk.CTkFrame(panel, fg_color="transparent")
        form.place(relx=.5, rely=.5, anchor="center", relwidth=.78)

        ctk.CTkLabel(
            form, text="Chào mừng trở lại 👋",
            text_color=TEXT,
            font=ctk.CTkFont(size=27, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            form,
            text="Đăng nhập để tiếp tục hành trình cùng TravelMate AI",
            text_color=MUTED,
            font=ctk.CTkFont(size=11)
        ).pack(anchor="w", pady=(5, 26))

        ctk.CTkLabel(form, text="Tên đăng nhập", text_color=TEXT).pack(anchor="w")
        username = ctk.CTkEntry(
            form, height=44, corner_radius=10,
            placeholder_text="Nhập username"
        )
        username.pack(fill="x", pady=(6, 14))

        ctk.CTkLabel(form, text="Mật khẩu", text_color=TEXT).pack(anchor="w")
        password = ctk.CTkEntry(
            form, height=44, corner_radius=10,
            show="•", placeholder_text="Nhập mật khẩu"
        )
        password.pack(fill="x", pady=(6, 18))

        def login():
            user = authenticate(username.get(), password.get())
            if not user:
                messagebox.showerror("Đăng nhập", "Sai tài khoản hoặc mật khẩu.")
                return
            self.user = user
            self.ctx.reset()
            self.show_main()

        ctk.CTkButton(
            form, text="ĐĂNG NHẬP",
            command=login,
            height=46, corner_radius=10,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(fill="x")

        ctk.CTkButton(
            form,
            text="Tạo tài khoản khách hàng mới",
            command=self.show_register,
            height=40,
            fg_color="transparent",
            text_color=PRIMARY,
            hover_color=SOFT
        ).pack(fill="x", pady=(8, 20))

        demo = ctk.CTkFrame(form, fg_color=SOFT, corner_radius=12)
        demo.pack(fill="x")

        ctk.CTkLabel(
            demo, text="Tài khoản demo",
            text_color=TEXT,
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(anchor="w", padx=14, pady=(10, 4))

        ctk.CTkLabel(
            demo,
            text="Khách hàng: khachhang / 123456\nAdmin: admin / admin123",
            justify="left",
            text_color=MUTED,
            font=ctk.CTkFont(size=10)
        ).pack(anchor="w", padx=14, pady=(0, 10))

        password.bind("<Return>", lambda e: login())

    def show_register(self):
        self.clear()

        root = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        root.pack(fill="both", expand=True)

        card = ctk.CTkFrame(root, fg_color=CARD, corner_radius=20)
        card.place(relx=.5, rely=.5, anchor="center", width=530, height=650)

        ctk.CTkLabel(
            card, text="Tạo tài khoản",
            text_color=TEXT,
            font=ctk.CTkFont(size=27, weight="bold")
        ).pack(anchor="w", padx=46, pady=(38, 4))

        ctk.CTkLabel(
            card, text="Đăng ký tài khoản khách hàng mới",
            text_color=MUTED
        ).pack(anchor="w", padx=46, pady=(0, 24))

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=46)

        def field(label, show=None, placeholder=""):
            ctk.CTkLabel(body, text=label, text_color=TEXT).pack(anchor="w")
            e = ctk.CTkEntry(
                body, height=42, corner_radius=9,
                show=show, placeholder_text=placeholder
            )
            e.pack(fill="x", pady=(5, 13))
            return e

        full_name = field("Họ và tên", placeholder="Nguyễn Văn A")
        username = field("Tên đăng nhập", placeholder="username")
        password = field("Mật khẩu", show="•", placeholder="Tối thiểu 6 ký tự")
        confirm = field("Nhập lại mật khẩu", show="•")

        def submit():
            if password.get() != confirm.get():
                messagebox.showerror("Đăng ký", "Mật khẩu nhập lại không khớp.")
                return
            ok, msg = register_user(full_name.get(), username.get(), password.get())
            if ok:
                messagebox.showinfo("Đăng ký", msg)
                self.show_login()
            else:
                messagebox.showerror("Đăng ký", msg)

        ctk.CTkButton(
            body, text="ĐĂNG KÝ",
            command=submit,
            height=44, corner_radius=10,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            font=ctk.CTkFont(weight="bold")
        ).pack(fill="x", pady=(4, 8))

        ctk.CTkButton(
            body,
            text="← Quay lại đăng nhập",
            command=self.show_login,
            fg_color="transparent",
            text_color=PRIMARY,
            hover_color=SOFT
        ).pack(fill="x")

    # -------------------- MAIN SHELL --------------------
    def show_main(self):
        self.clear()

        shell = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        shell.pack(fill="both", expand=True)

        self.sidebar = ctk.CTkFrame(
            shell, fg_color=SIDEBAR,
            width=255, corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.main = ctk.CTkFrame(shell, fg_color=BG, corner_radius=0)
        self.main.pack(side="left", fill="both", expand=True)

        self._modern_sidebar()
        self._modern_topbar()

        self.content = ctk.CTkFrame(
            self.main, fg_color=BG, corner_radius=0
        )
        self.content.pack(fill="both", expand=True)

        self.page = None
        self.dashboard()

    def _modern_sidebar(self):
        header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header.pack(fill="x", padx=18, pady=(20, 14))

        ctk.CTkLabel(
            header, text="✦",
            text_color="#A5B4FC",
            font=ctk.CTkFont(size=26, weight="bold")
        ).pack(side="left")

        brand = ctk.CTkFrame(header, fg_color="transparent")
        brand.pack(side="left", padx=(8, 0))

        ctk.CTkLabel(
            brand, text="TravelMate AI",
            text_color="white",
            font=ctk.CTkFont(size=17, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            brand, text="Modern UI v6",
            text_color="#94A3B8",
            font=ctk.CTkFont(size=9)
        ).pack(anchor="w")

        userbox = ctk.CTkFrame(
            self.sidebar, fg_color="#1F2937",
            corner_radius=12
        )
        userbox.pack(fill="x", padx=14, pady=(0, 14))

        avatar = (self.user["full_name"][:1] or "U").upper()
        ctk.CTkLabel(
            userbox, text=avatar,
            width=36, height=36,
            fg_color=PRIMARY, corner_radius=18,
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10, pady=10)

        uinfo = ctk.CTkFrame(userbox, fg_color="transparent")
        uinfo.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            uinfo, text=self.user["full_name"],
            text_color="white",
            font=ctk.CTkFont(size=10, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            uinfo,
            text="Quản trị viên" if self.user["role"] == "admin" else "Khách hàng",
            text_color="#94A3B8",
            font=ctk.CTkFont(size=9)
        ).pack(anchor="w")

        menu = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color="transparent",
            scrollbar_button_color="#263244",
            scrollbar_button_hover_color="#334155"
        )
        menu.pack(fill="both", expand=True, padx=8)

        self.nav_buttons = {}

        def nav(key, text, command):
            btn = ctk.CTkButton(
                menu, text=text,
                command=lambda: self._navigate(key, command),
                anchor="w",
                height=38, corner_radius=9,
                fg_color="transparent",
                hover_color="#1F2937",
                text_color="#E5E7EB",
                font=ctk.CTkFont(size=10, weight="bold")
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[key] = btn

        nav("dashboard", "⌂   Tổng quan", self.dashboard)
        nav("chat", "✦   Chatbot AI", self.chatbot)
        nav("tours", "▦   Khám phá tour", self.tour_cards)
        nav("favorites", "♥   Tour yêu thích", self.favorites_page)
        nav("compare", "⇄   So sánh tour", self.compare_page)
        nav("itinerary", "☷   Lịch trình AI", self.itinerary_page)
        nav("budget", "₫   Tính ngân sách", self.budget_page)
        nav("history", "⌛   Lịch sử AI", self.history_page)
        nav("bookings", "✓   Tour đã đặt", self.bookings)
        nav("reviews", "★   Đánh giá tour", self.review_page)
        nav("notifications", "●   Thông báo", self.notifications_page)

        ctk.CTkLabel(
            menu, text="AI & MÔ HÌNH",
            text_color="#64748B",
            font=ctk.CTkFont(size=8, weight="bold")
        ).pack(anchor="w", padx=10, pady=(14, 4))

        nav("eval", "AI   Đánh giá mô hình", self.model_evaluation)
        nav("recoeval", "◎   Đánh giá hệ gợi ý", self.recommendation_evaluation_page)
        nav("explain", "?   AI hoạt động thế nào?", self.ai_explain_page)

        if self.user["role"] == "admin":
            ctk.CTkLabel(
                menu, text="QUẢN TRỊ",
                text_color="#64748B",
                font=ctk.CTkFont(size=8, weight="bold")
            ).pack(anchor="w", padx=10, pady=(14, 4))

            nav("admin_tours", "⚙   Quản lý tour", self.admin_tours)
            nav("admin_bookings", "▣   Quản lý đơn", self.admin_bookings)
            nav("customers", "♟   Quản lý khách", self.admin_customers)
            nav("analytics", "▥   Thống kê", self.admin_analytics)
            nav("export", "⇩   Xuất báo cáo", self.export_report_page)

        ctk.CTkButton(
            self.sidebar,
            text="⇥   Đăng xuất",
            command=self.show_login,
            height=40, corner_radius=9,
            fg_color="transparent",
            hover_color="#3F1D2A",
            text_color="#FCA5A5",
            anchor="w"
        ).pack(fill="x", padx=12, pady=14)

    def _modern_topbar(self):
        top = ctk.CTkFrame(
            self.main, fg_color=CARD,
            height=66, corner_radius=0
        )
        top.pack(fill="x")
        top.pack_propagate(False)

        left = ctk.CTkFrame(top, fg_color="transparent")
        left.pack(side="left", padx=24, pady=10)

        ctk.CTkLabel(
            left,
            text="Travel smarter with AI",
            text_color=TEXT,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text="Tư vấn tour cá nhân hóa theo nhu cầu của bạn",
            text_color=MUTED,
            font=ctk.CTkFont(size=9)
        ).pack(anchor="w")

        right = ctk.CTkFrame(top, fg_color="transparent")
        right.pack(side="right", padx=18, pady=12)

        count = unread_notification_count(self.user["id"])
        ctk.CTkButton(
            right, text=f"🔔 {count}",
            command=self.notifications_page,
            width=70, height=36,
            corner_radius=10,
            fg_color=SOFT,
            text_color=TEXT,
            hover_color=("#E0E7FF", "#334155")
        ).pack(side="left", padx=5)

        self.theme_btn = ctk.CTkButton(
            right, text="☾ Tối",
            command=self.toggle_theme,
            width=78, height=36,
            corner_radius=10,
            fg_color=SOFT,
            text_color=TEXT,
            hover_color=("#E0E7FF", "#334155")
        )
        self.theme_btn.pack(side="left", padx=5)

    def toggle_theme(self):
        self.appearance_mode = (
            "dark" if self.appearance_mode == "light" else "light"
        )
        ctk.set_appearance_mode(self.appearance_mode)
        self.theme_btn.configure(
            text="☀ Sáng" if self.appearance_mode == "dark" else "☾ Tối"
        )
        self.image_cache.clear()

    def _navigate(self, key, command):
        self.active_nav = key
        for k, btn in self.nav_buttons.items():
            btn.configure(
                fg_color=PRIMARY if k == key else "transparent"
            )
        command()

    # -------------------- PAGE HEADER --------------------
    def new_page(self, title, subtitle=""):
        if self.page:
            self.page.destroy()

        self.page = ctk.CTkFrame(
            self.content, fg_color=BG,
            corner_radius=0
        )
        self.page.pack(fill="both", expand=True)

        header = ctk.CTkFrame(
            self.page, fg_color="transparent"
        )
        header.pack(fill="x", padx=28, pady=(20, 14))

        ctk.CTkLabel(
            header, text=title,
            text_color=TEXT,
            font=ctk.CTkFont(size=25, weight="bold")
        ).pack(anchor="w")

        if subtitle:
            ctk.CTkLabel(
                header, text=subtitle,
                text_color=MUTED,
                font=ctk.CTkFont(size=10)
            ).pack(anchor="w", pady=(3, 0))

        return self.page

    def _stat_card(self, master, title, value, icon, color):
        card = ctk.CTkFrame(
            master, fg_color=CARD,
            corner_radius=16,
            border_width=1,
            border_color=BORDER
        )
        card.pack(side="left", fill="both", expand=True, padx=5)

        ctk.CTkLabel(
            card, text=icon,
            width=34, height=34,
            corner_radius=10,
            fg_color=color,
            text_color="white",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=16, pady=(14, 6))

        ctk.CTkLabel(
            card, text=str(value),
            text_color=TEXT,
            font=ctk.CTkFont(size=19, weight="bold")
        ).pack(anchor="w", padx=16)

        ctk.CTkLabel(
            card, text=title,
            text_color=MUTED,
            font=ctk.CTkFont(size=9)
        ).pack(anchor="w", padx=16, pady=(2, 14))

    # -------------------- DASHBOARD --------------------
    def dashboard(self):
        p = self.new_page(
            "Tổng quan",
            "TravelMate AI v6 — giao diện hiện đại, AI đa nhiệm"
        )

        hero = ctk.CTkFrame(
            p, fg_color=PRIMARY,
            corner_radius=18
        )
        hero.pack(fill="x", padx=28, pady=(0, 14))

        h = ctk.CTkFrame(hero, fg_color="transparent")
        h.pack(fill="x", padx=24, pady=22)

        ctk.CTkLabel(
            h,
            text=f"Xin chào, {self.user['full_name']} 👋",
            text_color="white",
            font=ctk.CTkFont(size=21, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            h,
            text="Hãy để AI giúp bạn tìm chuyến đi phù hợp nhất.",
            text_color="#E0E7FF",
            font=ctk.CTkFont(size=11)
        ).pack(anchor="w", pady=(4, 12))

        ctk.CTkButton(
            h,
            text="Bắt đầu với Chatbot AI →",
            command=lambda: self._navigate("chat", self.chatbot),
            width=190, height=38,
            corner_radius=10,
            fg_color="white",
            text_color=PRIMARY,
            hover_color="#EEF2FF",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w")

        stats_data = dashboard_stats()
        stats = ctk.CTkFrame(p, fg_color="transparent")
        stats.pack(fill="x", padx=23, pady=(0, 14))

        self._stat_card(stats, "Tour đang hoạt động", stats_data["tours"], "✈", PRIMARY)
        self._stat_card(stats, "Tổng đơn", stats_data["bookings"], "▣", "#0891B2")
        self._stat_card(stats, "Khách hàng", stats_data["users"], "♟", "#7C3AED")
        self._stat_card(stats, "Đánh giá TB", f"{stats_data['avg_rating']:.1f} ★", "★", WARNING)

        quick = ctk.CTkFrame(
            p, fg_color=CARD,
            corner_radius=16,
            border_width=1,
            border_color=BORDER
        )
        quick.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        ctk.CTkLabel(
            quick, text="Truy cập nhanh",
            text_color=TEXT,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=18, pady=(16, 10))

        grid = ctk.CTkFrame(quick, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=13, pady=(0, 14))

        actions = [
            ("✦", "Chatbot AI", "Tư vấn bằng ngôn ngữ tự nhiên", "chat", self.chatbot),
            ("▦", "Khám phá tour", "Xem và đặt các tour nổi bật", "tours", self.tour_cards),
            ("⇄", "So sánh", "So sánh 2–3 tour cùng lúc", "compare", self.compare_page),
            ("☷", "Lịch trình AI", "AI tự tạo lịch trình theo ngày", "itinerary", self.itinerary_page),
            ("₫", "Ngân sách", "Ước tính tổng chi phí chuyến đi", "budget", self.budget_page),
            ("★", "Đánh giá", "Chấm sao và phản hồi sau tour", "reviews", self.review_page)
        ]

        for i, (icon, title, desc, key, command) in enumerate(actions):
            card = ctk.CTkFrame(
                grid, fg_color=CARD_ALT,
                corner_radius=13
            )
            card.grid(
                row=i // 3, column=i % 3,
                sticky="nsew", padx=5, pady=5
            )
            grid.grid_columnconfigure(i % 3, weight=1)
            grid.grid_rowconfigure(i // 3, weight=1)

            ctk.CTkLabel(
                card, text=icon,
                width=38, height=38,
                corner_radius=10,
                fg_color=SOFT,
                text_color=PRIMARY,
                font=ctk.CTkFont(size=15, weight="bold")
            ).pack(anchor="w", padx=14, pady=(13, 8))

            ctk.CTkLabel(
                card, text=title,
                text_color=TEXT,
                font=ctk.CTkFont(size=11, weight="bold")
            ).pack(anchor="w", padx=14)

            ctk.CTkLabel(
                card, text=desc,
                text_color=MUTED,
                wraplength=240,
                justify="left",
                font=ctk.CTkFont(size=9)
            ).pack(anchor="w", padx=14, pady=(3, 10))

            ctk.CTkButton(
                card, text="Mở →",
                command=lambda k=key, c=command: self._navigate(k, c),
                height=30,
                fg_color="transparent",
                text_color=PRIMARY,
                hover_color=SOFT,
                anchor="w"
            ).pack(fill="x", padx=10, pady=(0, 10))

    # -------------------- MODERN CHATBOT --------------------
    def chatbot(self):
        p = self.new_page(
            "Chatbot AI",
            "Hội thoại nhiều lượt, tự hỏi lại khi thiếu thông tin và giải thích kết quả"
        )

        body = ctk.CTkFrame(p, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        chat_card = ctk.CTkFrame(
            body, fg_color=CARD,
            corner_radius=16,
            border_width=1,
            border_color=BORDER
        )
        chat_card.pack(side="left", fill="both", expand=True)

        analysis_card = ctk.CTkFrame(
            body, fg_color=CARD,
            width=360, corner_radius=16,
            border_width=1, border_color=BORDER
        )
        analysis_card.pack(side="left", fill="y", padx=(12, 0))
        analysis_card.pack_propagate(False)

        chat = ctk.CTkScrollableFrame(
            chat_card, fg_color="transparent"
        )
        chat.pack(fill="both", expand=True, padx=12, pady=(12, 5))

        def bubble(text, mine=False):
            wrap = ctk.CTkFrame(chat, fg_color="transparent")
            wrap.pack(fill="x", pady=4)

            box = ctk.CTkFrame(
                wrap,
                fg_color=PRIMARY if mine else CARD_ALT,
                corner_radius=14
            )
            box.pack(
                side="right" if mine else "left",
                padx=6
            )

            ctk.CTkLabel(
                box, text=text,
                text_color="white" if mine else TEXT,
                wraplength=570,
                justify="left",
                font=ctk.CTkFont(size=10)
            ).pack(padx=13, pady=9)

        bubble(
            "Xin chào! Bạn có thể nói: "
            "“Tôi thích biển, đi 3 ngày, ngân sách 4 triệu”."
        )

        inputbar = ctk.CTkFrame(
            chat_card, fg_color=CARD_ALT,
            corner_radius=12
        )
        inputbar.pack(fill="x", padx=12, pady=(5, 12))

        entry = ctk.CTkEntry(
            inputbar,
            height=42,
            corner_radius=10,
            placeholder_text="Nhập yêu cầu du lịch..."
        )
        entry.pack(
            side="left", fill="x",
            expand=True, padx=(10, 6), pady=10
        )

        analysis = ctk.CTkTextbox(
            analysis_card,
            fg_color=CARD_ALT,
            corner_radius=12,
            wrap="word"
        )
        analysis.pack(
            fill="both", expand=True,
            padx=12, pady=(12, 8)
        )
        analysis.insert(
            "end",
            "PHÂN TÍCH AI\n\n"
            "Intent, Entity, Context và điểm gợi ý "
            "sẽ xuất hiện tại đây."
        )
        analysis.configure(state="disabled")

        chips = ctk.CTkFrame(
            analysis_card, fg_color="transparent"
        )
        chips.pack(fill="x", padx=12, pady=(0, 8))

        def fill(text):
            entry.delete(0, "end")
            entry.insert(0, text)

        for text in ["Tour biển", "3 ngày", "4 triệu", "Đi máy bay"]:
            ctk.CTkButton(
                chips, text=text,
                command=lambda x=text: fill(x),
                height=28,
                corner_radius=8,
                fg_color=SOFT,
                text_color=PRIMARY,
                hover_color=("#E0E7FF", "#334155")
            ).pack(fill="x", pady=2)

        def send():
            q = entry.get().strip()
            if not q:
                return

            bubble(q, mine=True)
            entry.delete(0, "end")

            intent, conf, entities, _ = analyze_message(q, self.ctx)
            non = answer_non_recommendation(intent, self.ctx)
            result = None

            if non and intent in (
                "greeting", "thanks", "show_bookings",
                "ask_price", "ask_duration",
                "ask_transport", "book_tour"
            ):
                response = non
            else:
                follow_up = missing_information_prompt(self.ctx)

                if (
                    not enough_information_for_recommendation(self.ctx)
                    and follow_up
                ):
                    response = follow_up
                else:
                    result = recommend_from_context(q, self.ctx, 5)
                    response = build_recommendation_answer(
                        result, self.ctx
                    )
                    if follow_up:
                        response += (
                            "\n\nĐể lọc chính xác hơn: "
                            + follow_up
                        )

            bubble(response)

            top_id = top_score = None
            if result and result["results"]:
                top_id = result["results"][0]["tour"]["id"]
                top_score = result["results"][0]["score"]

            save_ai_history(
                self.user["id"], q,
                intent, response,
                top_id, top_score
            )

            analysis.configure(state="normal")
            analysis.delete("1.0", "end")
            analysis.insert(
                "end",
                f"INTENT\n{intent}\n\n"
                f"CONFIDENCE\n{conf:.3f}\n\n"
                "ENTITY\n"
            )

            for k, v in entities.items():
                analysis.insert("end", f"{k}: {v}\n")

            analysis.insert("end", "\nCONTEXT\n")
            for k, v in self.ctx.summary().items():
                analysis.insert("end", f"{k}: {v}\n")

            if result:
                analysis.insert("end", "\nTOP SCORES\n")
                for x in result["results"][:5]:
                    analysis.insert(
                        "end",
                        f"{x['tour']['name']}: "
                        f"{x['score']:.3f}\n"
                    )
            analysis.configure(state="disabled")

        ctk.CTkButton(
            inputbar,
            text="Gửi",
            command=send,
            width=78,
            height=42,
            corner_radius=10,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER
        ).pack(
            side="right",
            padx=(0, 10), pady=10
        )

        ctk.CTkButton(
            analysis_card,
            text="Xóa ngữ cảnh",
            command=lambda: (
                self.ctx.reset(),
                bubble("Đã xóa ngữ cảnh hội thoại.")
            ),
            height=36,
            fg_color="transparent",
            border_width=1,
            border_color=BORDER,
            text_color=TEXT,
            hover_color=SOFT
        ).pack(fill="x", padx=12, pady=(0, 12))

        entry.bind("<Return>", lambda e: send())
        entry.focus()

    # -------------------- MODERN TOUR CARDS --------------------
    def tour_cards(self):
        p = self.new_page(
            "Khám phá tour",
            "Tìm kiếm, lọc, yêu thích và đặt tour"
        )

        toolbar = ctk.CTkFrame(
            p, fg_color=CARD,
            corner_radius=14,
            border_width=1,
            border_color=BORDER
        )
        toolbar.pack(fill="x", padx=28, pady=(0, 12))

        query = tk.StringVar()
        search = ctk.CTkEntry(
            toolbar,
            textvariable=query,
            height=40,
            corner_radius=10,
            placeholder_text="Tìm theo tên tour hoặc địa điểm..."
        )
        search.pack(
            side="left", fill="x",
            expand=True, padx=12, pady=12
        )

        tour_type = tk.StringVar(value="Tất cả")
        type_box = ctk.CTkComboBox(
            toolbar,
            variable=tour_type,
            values=[
                "Tất cả", "Biển", "Núi", "Nghỉ dưỡng",
                "Khám phá", "Văn hóa", "Miền Tây"
            ],
            width=170, height=40
        )
        type_box.pack(
            side="left", padx=(0, 12), pady=12
        )

        scroll = ctk.CTkScrollableFrame(
            p, fg_color="transparent"
        )
        scroll.pack(
            fill="both", expand=True,
            padx=22, pady=(0, 20)
        )

        def render(*_):
            for w in scroll.winfo_children():
                w.destroy()

            q = query.get().strip().lower()
            selected_type = tour_type.get()

            items = []
            for t in get_all_tours():
                if (
                    q
                    and q not in t["name"].lower()
                    and q not in t["location"].lower()
                ):
                    continue
                if (
                    selected_type != "Tất cả"
                    and t["type"] != selected_type
                ):
                    continue
                items.append(t)

            for i, t in enumerate(items):
                card = ctk.CTkFrame(
                    scroll, fg_color=CARD,
                    corner_radius=16,
                    border_width=1,
                    border_color=BORDER
                )
                card.grid(
                    row=i // 3,
                    column=i % 3,
                    sticky="nsew",
                    padx=6, pady=6
                )
                scroll.grid_columnconfigure(i % 3, weight=1)

                img = self.load_tour_image(
                    t, (330, 165)
                )
                if img:
                    ctk.CTkLabel(
                        card, text="", image=img
                    ).pack(
                        padx=8, pady=(8, 0)
                    )

                body = ctk.CTkFrame(
                    card, fg_color="transparent"
                )
                body.pack(
                    fill="both", expand=True,
                    padx=14, pady=12
                )

                ctk.CTkLabel(
                    body, text=t["name"],
                    text_color=TEXT,
                    wraplength=290,
                    justify="left",
                    font=ctk.CTkFont(
                        size=13, weight="bold"
                    )
                ).pack(anchor="w")

                ctk.CTkLabel(
                    body,
                    text=(
                        f"📍 {t['location']}  •  "
                        f"{t['days']} ngày  •  "
                        f"{t['transport']}"
                    ),
                    text_color=MUTED,
                    font=ctk.CTkFont(size=9)
                ).pack(anchor="w", pady=(5, 0))

                ctk.CTkLabel(
                    body,
                    text=(
                        f"★ {float(t['avg_rating']):.1f} "
                        f"({t['review_count']} đánh giá)"
                    ),
                    text_color="#B45309",
                    font=ctk.CTkFont(
                        size=9, weight="bold"
                    )
                ).pack(anchor="w", pady=(4, 0))

                ctk.CTkLabel(
                    body, text=money(t["price"]),
                    text_color=PRIMARY,
                    font=ctk.CTkFont(
                        size=14, weight="bold"
                    )
                ).pack(anchor="w", pady=(6, 9))

                actions = ctk.CTkFrame(
                    body, fg_color="transparent"
                )
                actions.pack(fill="x")

                fav_text = (
                    "♥"
                    if is_favorite(
                        self.user["id"], t["id"]
                    )
                    else "♡"
                )

                ctk.CTkButton(
                    actions,
                    text=fav_text,
                    width=42, height=34,
                    fg_color=SOFT,
                    text_color=DANGER,
                    hover_color=("#FEE2E2", "#3F1D2A"),
                    command=lambda tid=t["id"]:
                        self._modern_toggle_favorite(
                            tid, render
                        )
                ).pack(side="left")

                ctk.CTkButton(
                    actions,
                    text="Chi tiết",
                    width=80, height=34,
                    fg_color=SOFT,
                    text_color=PRIMARY,
                    hover_color=("#E0E7FF", "#334155"),
                    command=lambda tid=t["id"]:
                        self.tour_detail(tid)
                ).pack(side="left", padx=6)

                ctk.CTkButton(
                    actions,
                    text="Đặt ngay",
                    height=34,
                    fg_color=PRIMARY,
                    hover_color=PRIMARY_HOVER,
                    command=lambda tid=t["id"]:
                        self.open_booking(tid)
                ).pack(side="right")

        search.bind("<KeyRelease>", render)
        type_box.configure(command=lambda _: render())
        render()

    def _modern_toggle_favorite(self, tour_id, refresh):
        added = toggle_favorite(
            self.user["id"], tour_id
        )
        refresh()
        messagebox.showinfo(
            "Yêu thích",
            "Đã thêm vào yêu thích."
            if added else
            "Đã bỏ khỏi yêu thích."
        )


if __name__ == "__main__":
    App().mainloop()
