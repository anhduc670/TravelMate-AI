import sqlite3
import hashlib
import uuid
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "travelmate_ai_v5.db"

SAMPLE_TOURS = [
    ("Đà Nẵng - Hội An", "Đà Nẵng", "Biển", 3, 3500000, "máy bay", "mùa hè", "gia đình,cặp đôi,bạn bè", "default.ppm",
     "Biển Mỹ Khê, Bà Nà Hills, phố cổ Hội An, ẩm thực, nghỉ dưỡng, check-in."),
    ("Đà Lạt Mộng Mơ", "Đà Lạt", "Nghỉ dưỡng", 3, 3000000, "máy bay", "quanh năm", "cặp đôi,gia đình,bạn bè", "default.ppm",
     "Khí hậu mát mẻ, yên tĩnh, hồ Xuân Hương, Langbiang, vườn hoa, cafe và nghỉ dưỡng."),
    ("Phú Quốc Thiên Đường Biển", "Phú Quốc", "Biển", 4, 6000000, "máy bay", "mùa khô", "cặp đôi,gia đình", "default.ppm",
     "Biển đảo, resort, nghỉ dưỡng, cáp treo Hòn Thơm, san hô và hải sản."),
    ("Sapa - Fansipan", "Sapa", "Núi", 3, 4000000, "ô tô", "mùa đông", "cặp đôi,bạn bè", "default.ppm",
     "Núi cao, săn mây, khí hậu mát lạnh, bản Cát Cát, Fansipan và văn hóa vùng cao."),
    ("Nha Trang Biển Xanh", "Nha Trang", "Biển", 4, 4500000, "máy bay", "mùa hè", "gia đình,cặp đôi,bạn bè", "default.ppm",
     "Tắm biển, tham quan đảo, lặn biển, vui chơi, hải sản và nghỉ dưỡng."),
    ("Hà Giang Hùng Vĩ", "Hà Giang", "Khám phá", 4, 3800000, "ô tô", "mùa thu", "bạn bè,một mình", "default.ppm",
     "Phượt, khám phá, cao nguyên đá Đồng Văn, đèo Mã Pí Lèng, núi và văn hóa vùng cao."),
    ("Vịnh Hạ Long", "Hạ Long", "Biển", 2, 2800000, "ô tô", "mùa hè", "gia đình,cặp đôi", "default.ppm",
     "Du thuyền, vịnh biển, hang động, hải sản và nghỉ dưỡng ngắn ngày."),
    ("Mộc Châu Săn Mây", "Mộc Châu", "Núi", 2, 2200000, "ô tô", "mùa xuân", "cặp đôi,bạn bè", "default.ppm",
     "Săn mây, đồi chè, thác Dải Yếm, hoa, núi, khí hậu mát mẻ và thiên nhiên."),
    ("Cố Đô Huế", "Huế", "Văn hóa", 3, 3200000, "máy bay", "mùa xuân", "gia đình,cặp đôi", "default.ppm",
     "Lịch sử, văn hóa, Đại Nội, chùa Thiên Mụ, lăng tẩm và ẩm thực cung đình."),
    ("Miền Tây Sông Nước", "Cần Thơ", "Miền Tây", 2, 2000000, "máy bay", "quanh năm", "gia đình,bạn bè", "default.ppm",
     "Chợ nổi Cái Răng, miệt vườn, sông nước, ẩm thực và trải nghiệm miền Tây."),
    ("Quy Nhơn - Kỳ Co Eo Gió", "Quy Nhơn", "Biển", 3, 3900000, "máy bay", "mùa hè", "cặp đôi,bạn bè", "default.ppm",
     "Kỳ Co, Eo Gió, biển đẹp, hải sản, check-in và nghỉ dưỡng."),
    ("Vũng Tàu Cuối Tuần", "Vũng Tàu", "Biển", 2, 1800000, "ô tô", "quanh năm", "gia đình,bạn bè", "default.ppm",
     "Biển, nghỉ dưỡng cuối tuần, hải sản và tham quan thành phố biển.")
]

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS tours(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            type TEXT NOT NULL,
            days INTEGER NOT NULL,
            price INTEGER NOT NULL,
            transport TEXT NOT NULL,
            season TEXT NOT NULL DEFAULT 'quanh năm',
            audience TEXT NOT NULL DEFAULT 'gia đình,bạn bè,cặp đôi',
            image_path TEXT NOT NULL DEFAULT 'default.ppm',
            description TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS bookings(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_code TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            tour_id INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            adults INTEGER NOT NULL DEFAULT 1,
            children INTEGER NOT NULL DEFAULT 0,
            people INTEGER NOT NULL DEFAULT 1,
            departure_date TEXT,
            note TEXT,
            total_price INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Chờ xác nhận',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(tour_id) REFERENCES tours(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS reviews(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tour_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            comment TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, tour_id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(tour_id) REFERENCES tours(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS favorites(
            user_id INTEGER NOT NULL,
            tour_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(user_id, tour_id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(tour_id) REFERENCES tours(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS ai_history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            query TEXT NOT NULL,
            intent TEXT,
            response TEXT,
            top_tour_id INTEGER,
            top_score REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(top_tour_id) REFERENCES tours(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS notifications(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            is_read INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    c.execute("SELECT COUNT(*) c FROM tours")
    if c.fetchone()["c"] == 0:
        c.executemany("""
            INSERT INTO tours(
                name, location, type, days, price, transport,
                season, audience, image_path, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, SAMPLE_TOURS)

    c.execute("SELECT id FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("""
            INSERT INTO users(full_name, username, password, role)
            VALUES (?, ?, ?, 'admin')
        """, ("Quản trị viên", "admin", hash_password("admin123")))

    c.execute("SELECT id FROM users WHERE username='khachhang'")
    if not c.fetchone():
        c.execute("""
            INSERT INTO users(full_name, username, password, role)
            VALUES (?, ?, ?, 'user')
        """, ("Khách hàng demo", "khachhang", hash_password("123456")))

    conn.commit()
    conn.close()

def authenticate(username, password):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username.strip(), hash_password(password))
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def register_user(full_name, username, password):
    full_name, username = full_name.strip(), username.strip()
    if not full_name or not username or not password:
        return False, "Vui lòng nhập đầy đủ thông tin."
    if len(password) < 6:
        return False, "Mật khẩu tối thiểu 6 ký tự."
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users(full_name,username,password) VALUES (?,?,?)",
            (full_name, username, hash_password(password))
        )
        conn.commit()
        return True, "Đăng ký thành công."
    except sqlite3.IntegrityError:
        return False, "Tên đăng nhập đã tồn tại."
    finally:
        conn.close()

def _tour_select():
    return """
        SELECT t.*,
               COALESCE(AVG(r.rating),0) AS avg_rating,
               COUNT(r.id) AS review_count
        FROM tours t
        LEFT JOIN reviews r ON r.tour_id=t.id
    """

def get_all_tours(active_only=True):
    conn = get_connection()
    sql = _tour_select()
    if active_only:
        sql += " WHERE t.active=1 "
    sql += " GROUP BY t.id ORDER BY t.id DESC"
    rows = conn.execute(sql).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_tour(tour_id):
    conn = get_connection()
    row = conn.execute(_tour_select() + " WHERE t.id=? GROUP BY t.id", (tour_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def add_tour(name, location, tour_type, days, price, transport, season, audience, image_path, description):
    conn = get_connection()
    conn.execute("""
        INSERT INTO tours(
            name,location,type,days,price,transport,season,audience,image_path,description
        ) VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (name,location,tour_type,days,price,transport,season,audience,image_path,description))
    conn.commit()
    conn.close()

def update_tour(tour_id, name, location, tour_type, days, price, transport, season, audience, image_path, description):
    conn = get_connection()
    conn.execute("""
        UPDATE tours SET
            name=?,location=?,type=?,days=?,price=?,transport=?,
            season=?,audience=?,image_path=?,description=?
        WHERE id=?
    """, (name,location,tour_type,days,price,transport,season,audience,image_path,description,tour_id))
    conn.commit()
    conn.close()

def delete_tour(tour_id):
    conn = get_connection()
    conn.execute("UPDATE tours SET active=0 WHERE id=?", (tour_id,))
    conn.commit()
    conn.close()

def make_booking_code():
    return "TM" + datetime.now().strftime("%Y%m%d") + uuid.uuid4().hex[:6].upper()

def create_booking(user_id, tour_id, customer_name, phone, adults, children, departure_date, note=""):
    tour = get_tour(tour_id)
    if not tour:
        return None
    adults = max(1, int(adults))
    children = max(0, int(children))
    people = adults + children
    total = int(tour["price"] * adults + tour["price"] * 0.6 * children)
    code = make_booking_code()

    conn = get_connection()
    conn.execute("""
        INSERT INTO bookings(
            booking_code,user_id,tour_id,customer_name,phone,
            adults,children,people,departure_date,note,total_price
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (code,user_id,tour_id,customer_name,phone,adults,children,people,departure_date,note,total))
    conn.commit()
    conn.close()
    add_notification(user_id, "Đặt tour thành công", f"Đơn {code} đã được tạo và đang chờ xác nhận.")
    return code

def get_user_bookings(user_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT b.*, t.name AS tour_name, t.location
        FROM bookings b
        JOIN tours t ON t.id=b.tour_id
        WHERE b.user_id=?
        ORDER BY b.id DESC
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_bookings():
    conn = get_connection()
    rows = conn.execute("""
        SELECT b.*, t.name AS tour_name, u.username
        FROM bookings b
        JOIN tours t ON t.id=b.tour_id
        JOIN users u ON u.id=b.user_id
        ORDER BY b.id DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_booking_status(booking_id, status):
    conn = get_connection()
    row = conn.execute("SELECT user_id, booking_code FROM bookings WHERE id=?", (booking_id,)).fetchone()
    conn.execute("UPDATE bookings SET status=? WHERE id=?", (status, booking_id))
    conn.commit()
    conn.close()
    if row:
        add_notification(row["user_id"], "Cập nhật đơn tour", f"Đơn {row['booking_code']} đã chuyển sang trạng thái: {status}.")

def cancel_user_booking(booking_id, user_id):
    conn = get_connection()
    row = conn.execute("""
        SELECT status, booking_code FROM bookings
        WHERE id=? AND user_id=?
    """, (booking_id,user_id)).fetchone()
    if not row:
        conn.close()
        return False, "Không tìm thấy đơn."
    if row["status"] != "Chờ xác nhận":
        conn.close()
        return False, "Chỉ có thể hủy đơn đang chờ xác nhận."
    conn.execute("UPDATE bookings SET status='Đã hủy' WHERE id=? AND user_id=?", (booking_id,user_id))
    conn.commit()
    conn.close()
    add_notification(user_id, "Đã hủy đơn", f"Đơn {row['booking_code']} đã được hủy.")
    return True, "Hủy đơn thành công."

def save_review(user_id, tour_id, rating, comment):
    conn = get_connection()
    conn.execute("""
        INSERT INTO reviews(user_id,tour_id,rating,comment)
        VALUES (?,?,?,?)
        ON CONFLICT(user_id,tour_id) DO UPDATE SET
            rating=excluded.rating,
            comment=excluded.comment,
            created_at=CURRENT_TIMESTAMP
    """, (user_id,tour_id,rating,comment))
    conn.commit()
    conn.close()

def get_reviews(tour_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT r.*,u.full_name
        FROM reviews r JOIN users u ON u.id=r.user_id
        WHERE r.tour_id=? ORDER BY r.id DESC
    """, (tour_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def toggle_favorite(user_id, tour_id):
    conn = get_connection()
    row = conn.execute("SELECT 1 FROM favorites WHERE user_id=? AND tour_id=?", (user_id,tour_id)).fetchone()
    if row:
        conn.execute("DELETE FROM favorites WHERE user_id=? AND tour_id=?", (user_id,tour_id))
        state = False
    else:
        conn.execute("INSERT INTO favorites(user_id,tour_id) VALUES (?,?)", (user_id,tour_id))
        state = True
    conn.commit()
    conn.close()
    return state

def is_favorite(user_id, tour_id):
    conn = get_connection()
    row = conn.execute("SELECT 1 FROM favorites WHERE user_id=? AND tour_id=?", (user_id,tour_id)).fetchone()
    conn.close()
    return bool(row)

def get_favorites(user_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT t.*, COALESCE(AVG(r.rating),0) AS avg_rating, COUNT(r.id) AS review_count
        FROM favorites f
        JOIN tours t ON t.id=f.tour_id
        LEFT JOIN reviews r ON r.tour_id=t.id
        WHERE f.user_id=? AND t.active=1
        GROUP BY t.id
        ORDER BY f.created_at DESC
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_ai_history(user_id, query, intent, response, top_tour_id=None, top_score=None):
    conn = get_connection()
    conn.execute("""
        INSERT INTO ai_history(user_id,query,intent,response,top_tour_id,top_score)
        VALUES (?,?,?,?,?,?)
    """, (user_id,query,intent,response,top_tour_id,top_score))
    conn.commit()
    conn.close()

def get_ai_history(user_id, limit=100):
    conn = get_connection()
    rows = conn.execute("""
        SELECT h.*, t.name AS top_tour_name
        FROM ai_history h
        LEFT JOIN tours t ON t.id=h.top_tour_id
        WHERE h.user_id=?
        ORDER BY h.id DESC
        LIMIT ?
    """, (user_id,limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def clear_ai_history(user_id):
    conn = get_connection()
    conn.execute("DELETE FROM ai_history WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def add_notification(user_id, title, message):
    conn = get_connection()
    conn.execute("INSERT INTO notifications(user_id,title,message) VALUES (?,?,?)", (user_id,title,message))
    conn.commit()
    conn.close()

def get_notifications(user_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM notifications
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 100
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def mark_notifications_read(user_id):
    conn = get_connection()
    conn.execute("UPDATE notifications SET is_read=1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def unread_notification_count(user_id):
    conn = get_connection()
    n = conn.execute("SELECT COUNT(*) c FROM notifications WHERE user_id=? AND is_read=0", (user_id,)).fetchone()["c"]
    conn.close()
    return n

def dashboard_stats():
    conn = get_connection()
    tours = conn.execute("SELECT COUNT(*) c FROM tours WHERE active=1").fetchone()["c"]
    bookings = conn.execute("SELECT COUNT(*) c FROM bookings").fetchone()["c"]
    users = conn.execute("SELECT COUNT(*) c FROM users WHERE role='user'").fetchone()["c"]
    revenue = conn.execute("SELECT COALESCE(SUM(total_price),0) s FROM bookings WHERE status='Đã xác nhận'").fetchone()["s"]
    avg_rating = conn.execute("SELECT COALESCE(AVG(rating),0) a FROM reviews").fetchone()["a"]
    conn.close()
    return {"tours":tours,"bookings":bookings,"users":users,"revenue":revenue,"avg_rating":avg_rating}

def booking_status_stats():
    conn = get_connection()
    rows = conn.execute("SELECT status,COUNT(*) count FROM bookings GROUP BY status ORDER BY count DESC").fetchall()
    conn.close()
    return [(r["status"],r["count"]) for r in rows]

def top_tour_stats(limit=6):
    conn = get_connection()
    rows = conn.execute("""
        SELECT t.name, COUNT(b.id) AS count,
               COALESCE(SUM(CASE WHEN b.status='Đã xác nhận' THEN b.total_price ELSE 0 END),0) AS revenue
        FROM tours t
        LEFT JOIN bookings b ON b.tour_id=t.id
        GROUP BY t.id
        ORDER BY count DESC,revenue DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def revenue_by_month(limit=6):
    conn = get_connection()
    rows = conn.execute("""
        SELECT substr(created_at,1,7) AS month,
               COALESCE(SUM(total_price),0) AS revenue
        FROM bookings
        WHERE status='Đã xác nhận'
        GROUP BY substr(created_at,1,7)
        ORDER BY month DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return list(reversed([(r["month"], r["revenue"]) for r in rows]))

def tour_type_stats():
    conn = get_connection()
    rows = conn.execute("""
        SELECT t.type, COUNT(b.id) AS count
        FROM tours t
        LEFT JOIN bookings b ON b.tour_id=t.id
        GROUP BY t.type
        ORDER BY count DESC
    """).fetchall()
    conn.close()
    return [(r["type"],r["count"]) for r in rows]

def get_users_summary():
    conn = get_connection()
    rows = conn.execute("""
        SELECT u.id,u.full_name,u.username,u.created_at,
               COUNT(b.id) AS booking_count,
               COALESCE(SUM(CASE WHEN b.status='Đã xác nhận' THEN b.total_price ELSE 0 END),0) AS total_spent
        FROM users u
        LEFT JOIN bookings b ON b.user_id=u.id
        WHERE u.role='user'
        GROUP BY u.id
        ORDER BY booking_count DESC,u.id DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]
