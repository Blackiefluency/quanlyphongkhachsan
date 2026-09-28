```python
import streamlit as st
import sqlite3
from datetime import datetime, date
from pathlib import Path

# ============================================================
# CẤU HÌNH APP
# ============================================================

st.set_page_config(
    page_title="Hotel Management System",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_FILE = "hotel.db"
LOGO_FILE = "logo.png"


# ============================================================
# CSS - GIAO DIỆN
# ============================================================

st.markdown("""
<style>

    /* Toàn trang */
    .main {
        background-color: #f7f8fa;
    }

    /* Tiêu đề */
    .main-title {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .sub-title {
        color: #6b7280;
        margin-bottom: 25px;
    }

    /* Card */
    .dashboard-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    /* Room card */
    .room-card {
        background: white;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        margin-bottom: 10px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    /* Nút */
    .stButton > button {
        border-radius: 8px;
    }

    /* Status */
    .status-text {
        font-weight: 600;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# DATABASE
# ============================================================

def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():

    conn = get_connection()
    cursor = conn.cursor()

    # Bảng phòng
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT UNIQUE NOT NULL,
            room_type TEXT NOT NULL,
            price REAL NOT NULL,
            floor INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Trống'
        )
    """)

    # Bảng khách
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            id_number TEXT,
            room_number TEXT NOT NULL,
            check_in TEXT NOT NULL,
            expected_check_out TEXT,
            actual_check_out TEXT,
            nights INTEGER DEFAULT 1,
            room_charge REAL DEFAULT 0,
            service_charge REAL DEFAULT 0,
            total REAL DEFAULT 0,
            status TEXT DEFAULT 'Đang ở'
        )
    """)

    # Bảng dịch vụ
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_id INTEGER,
            room_number TEXT,
            service_name TEXT,
            quantity INTEGER DEFAULT 1,
            price REAL DEFAULT 0,
            total REAL DEFAULT 0,
            service_date TEXT
        )
    """)

    # Bảng lịch sử trạng thái phòng
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS room_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT,
            old_status TEXT,
            new_status TEXT,
            changed_at TEXT
        )
    """)

    # Tạo dữ liệu mẫu nếu database chưa có phòng
    cursor.execute("SELECT COUNT(*) FROM rooms")
    room_count = cursor.fetchone()[0]

    if room_count == 0:

        sample_rooms = [
            ("501", "Standard", 800000, 5, "Trống"),
            ("502", "Standard", 800000, 5, "Đang ở"),
            ("503", "Standard", 800000, 5, "Đang dọn"),
            ("504", "Standard", 800000, 5, "Trống"),

            ("601", "Superior", 1000000, 6, "Trống"),
            ("602", "Superior", 1000000, 6, "Đã đặt"),
            ("603", "Superior", 1000000, 6, "Đang ở"),
            ("604", "Superior", 1000000, 6, "Trống"),

            ("701", "Deluxe", 1300000, 7, "Trống"),
            ("702", "Deluxe", 1300000, 7, "Đang ở"),
            ("703", "Deluxe", 1300000, 7, "Trống"),
            ("704", "Deluxe", 1300000, 7, "Bảo trì"),

            ("801", "Suite", 2000000, 8, "Trống"),
            ("802", "Suite", 2000000, 8, "Đã đặt"),
            ("803", "Suite", 2000000, 8, "Trống"),
            ("804", "Suite", 2000000, 8, "Đang dọn"),
        ]

        cursor.executemany("""
            INSERT INTO rooms
            (room_number, room_type, price, floor, status)
            VALUES (?, ?, ?, ?, ?)
        """, sample_rooms)

    conn.commit()
    conn.close()


init_database()


# ============================================================
# HÀM DATABASE - PHÒNG
# ============================================================

def get_rooms():

    conn = get_connection()

    rooms = conn.execute("""
        SELECT *
        FROM rooms
        ORDER BY floor, room_number
    """).fetchall()

    conn.close()

    return rooms


def get_room(room_number):

    conn = get_connection()

    room = conn.execute("""
        SELECT *
        FROM rooms
        WHERE room_number = ?
    """, (room_number,)).fetchone()

    conn.close()

    return room


def add_room(room_number, room_type, price, floor, status="Trống"):

    conn = get_connection()

    conn.execute("""
        INSERT INTO rooms
        (room_number, room_type, price, floor, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        room_number,
        room_type,
        price,
        floor,
        status
    ))

    conn.commit()
    conn.close()


def update_room(
    room_id,
    room_number,
    room_type,
    price,
    floor,
    status
):

    conn = get_connection()

    conn.execute("""
        UPDATE rooms
        SET room_number = ?,
            room_type = ?,
            price = ?,
            floor = ?,
            status = ?
        WHERE id = ?
    """, (
        room_number,
        room_type,
        price,
        floor,
        status,
        room_id
    ))

    conn.commit()
    conn.close()


def delete_room(room_id):

    conn = get_connection()

    conn.execute("""
        DELETE FROM rooms
        WHERE id = ?
    """, (room_id,))

    conn.commit()
    conn.close()


def change_room_status(room_number, new_status):

    conn = get_connection()

    room = conn.execute("""
        SELECT status
        FROM rooms
        WHERE room_number = ?
    """, (room_number,)).fetchone()

    if room:

        old_status = room["status"]

        conn.execute("""
            UPDATE rooms
            SET status = ?
            WHERE room_number = ?
        """, (
            new_status,
            room_number
        ))

        conn.execute("""
            INSERT INTO room_history
            (room_number, old_status, new_status, changed_at)
            VALUES (?, ?, ?, ?)
        """, (
            room_number,
            old_status,
            new_status,
            datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        ))

    conn.commit()
    conn.close()


# ============================================================
# HÀM DATABASE - KHÁCH
# ============================================================

def get_active_guests():

    conn = get_connection()

    guests = conn.execute("""
        SELECT *
        FROM guests
        WHERE status = 'Đang ở'
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return guests


def get_all_guests():

    conn = get_connection()

    guests = conn.execute("""
        SELECT *
        FROM guests
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return guests


def get_guest(guest_id):

    conn = get_connection()

    guest = conn.execute("""
        SELECT *
        FROM guests
        WHERE id = ?
    """, (guest_id,)).fetchone()

    conn.close()

    return guest


# ============================================================
# FORMAT TIỀN
# ============================================================

def money(value):

    if value is None:
        value = 0

    return f"{value:,.0f} VNĐ"


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # Logo
    if Path(LOGO_FILE).exists():

        st.image(
            LOGO_FILE,
            width=180
        )

    else:

        st.markdown(
            "# 🏨"
        )

    st.markdown(
        "## HOTEL MANAGEMENT"
    )

    st.caption(
        "Hệ thống quản lý phòng khách sạn"
    )

    st.divider()

    menu = st.radio(
        "MENU",
        [
            "📊 Tổng quan",
            "🛏️ Quản lý phòng",
            "🗺️ Sơ đồ phòng",
            "🛎️ Check-in",
            "🚪 Check-out",
            "👥 Khách lưu trú",
            "🧹 Housekeeping",
            "💰 Doanh thu",
            "➕ Thêm phòng"
        ]
    )

    st.divider()

    st.caption(
        "Streamlit + SQLite"
    )


# ============================================================
# LẤY DỮ LIỆU
# ============================================================

rooms = get_rooms()
active_guests = get_active_guests()
all_guests = get_all_guests()


# ============================================================
# TRANG TỔNG QUAN
# ============================================================

if menu == "📊 Tổng quan":

    st.markdown(
        '<div class="main-title">'
        '📊 Tổng quan khách sạn'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">'
        'Theo dõi tình trạng phòng và hoạt động lưu trú'
        '</div>',
        unsafe_allow_html=True
    )

    # Thống kê
    total_rooms = len(rooms)

    empty_rooms = sum(
        1 for r in rooms
        if r["status"] == "Trống"
    )

    occupied_rooms = sum(
        1 for r in rooms
        if r["status"] == "Đang ở"
    )

    booked_rooms = sum(
        1 for r in rooms
        if r["status"] == "Đã đặt"
    )

    cleaning_rooms = sum(
        1 for r in rooms
        if r["status"] == "Đang dọn"
    )

    maintenance_rooms = sum(
        1 for r in rooms
        if r["status"] == "Bảo trì"
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "🏨 Tổng phòng",
        total_rooms
    )

    col2.metric(
        "🟢 Trống",
        empty_rooms
    )

    col3.metric(
        "🔴 Đang ở",
        occupied_rooms
    )

    col4.metric(
        "🔵 Đã đặt",
        booked_rooms
    )

    col5.metric(
        "🧹 Đang dọn",
        cleaning_rooms
    )

    st.divider()

    # Công suất
    if total_rooms > 0:
        occupancy = occupied_rooms / total_rooms * 100
    else:
        occupancy = 0

    st.subheader("📈 Công suất phòng")

    st.progress(
        int(occupancy)
    )

    st.write(
        f"**Công suất hiện tại: {occupancy:.1f}%**"
    )

    st.divider()

    # Thống kê nhanh
    c1, c2, c3 = st.columns(3)

    c1.metric(
        "👥 Khách đang ở",
        len(active_guests)
    )

    total_revenue = sum(
        g["total"] or 0
        for g in all_guests
    )

    c2.metric(
        "💰 Tổng doanh thu",
        money(total_revenue)
    )

    c3.metric(
        "⚠️ Phòng bảo trì",
        maintenance_rooms
    )

    st.divider()

    # Danh sách phòng
    st.subheader("🛏️ Tình trạng phòng")

    for room in rooms:

        status = room["status"]

        if status == "Trống":
            icon = "🟢"

        elif status == "Đang ở":
            icon = "🔴"

        elif status == "Đã đặt":
            icon = "🔵"

        elif status == "Đang dọn":
            icon = "🟡"

        else:
            icon = "⚫"

        st.write(
            f"{icon} **Phòng {room['room_number']}** — "
            f"{room['room_type']} — "
            f"{money(room['price'])} — "
            f"**{status}**"
        )


# ============================================================
# QUẢN LÝ PHÒNG
# ============================================================

elif menu == "🛏️ Quản lý phòng":

    st.title("🛏️ Quản lý phòng")

    st.write(
        "Tìm kiếm, cập nhật và quản lý tình trạng phòng."
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        search = st.text_input(
            "🔎 Tìm số phòng",
            placeholder="Ví dụ: 501"
        )

    with col2:

        status_filter = st.selectbox(
            "📌 Trạng thái",
            [
                "Tất cả",
                "Trống",
                "Đã đặt",
                "Đang ở",
                "Đang dọn",
                "Bảo trì"
            ]
        )

    with col3:

        type_filter = st.selectbox(
            "🏨 Loại phòng",
            [
                "Tất cả",
                "Standard",
                "Superior",
                "Deluxe",
                "Suite",
                "President Suite"
            ]
        )

    filtered_rooms = list(rooms)

    if search:

        filtered_rooms = [
            r for r in filtered_rooms
            if search.lower()
            in r["room_number"].lower()
        ]

    if status_filter != "Tất cả":

        filtered_rooms = [
            r for r in filtered_rooms
            if r["status"] == status_filter
        ]

    if type_filter != "Tất cả":

        filtered_rooms = [
            r for r in filtered_rooms
            if r["room_type"] == type_filter
        ]

    st.write(
        f"Hiển thị **{len(filtered_rooms)} phòng**"
    )

    st.divider()

    for room in filtered_rooms:

        with st.container(border=True):

            col1, col2, col3, col4, col5 = st.columns(
                [1, 2, 2, 2, 2]
            )

            col1.markdown(
                f"### 🛏️ {room['room_number']}"
            )

            col2.write(
                f"**Loại phòng**\n\n"
                f"{room['room_type']}"
            )

            col3.write(
                f"**Tầng**\n\n"
                f"{room['floor']}"
            )

            col4.write(
                f"**Giá phòng**\n\n"
                f"{money(room['price'])}"
            )

            with col5:

                new_status = st.selectbox(
                    "Trạng thái",
                    [
                        "Trống",
                        "Đã đặt",
                        "Đang ở",
                        "Đang dọn",
                        "Bảo trì"
                    ],
                    index=[
                        "Trống",
                        "Đã đặt",
                        "Đang ở",
                        "Đang dọn",
                        "Bảo trì"
                    ].index(room["status"]),
                    key=f"status_{room['id']}"
                )

                if new_status != room["status"]:

                    change_room_status(
                        room["room_number"],
                        new_status
                    )

                    st.success(
                        "Đã cập nhật trạng thái."
                    )

                    st.rerun()


# ============================================================
# SƠ ĐỒ PHÒNG
# ============================================================

elif menu == "🗺️ Sơ đồ phòng":

    st.title("🗺️ Sơ đồ phòng khách sạn")

    floors = sorted(
        list(set(
            r["floor"]
            for r in rooms
        ))
    )

    floor_options = ["Tất cả"] + [
        str(f) for f in floors
    ]

    selected_floor = st.selectbox(
        "Chọn tầng",
        floor_options
    )

    display_rooms = list(rooms)

    if selected_floor != "Tất cả":

        display_rooms = [
            r for r in rooms
            if str(r["floor"]) == selected_floor
        ]

    st.divider()

    cols = st.columns(4)

    for index, room in enumerate(display_rooms):

        with cols[index % 4]:

            status = room["status"]

            if status == "Trống":

                st.success(
                    f"### 🟢 {room['room_number']}\n\n"
                    f"**{room['room_type']}**\n\n"
                    f"{money(room['price'])}\n\n"
                    f"**Trống**"
                )

            elif status == "Đang ở":

                st.error(
                    f"### 🔴 {room['room_number']}\n\n"
                    f"**{room['room_type']}**\n\n"
                    f"**Đang ở**"
                )

            elif status == "Đã đặt":

                st.info(
                    f"### 🔵 {room['room_number']}\n\n"
                    f"**{room['room_type']}**\n\n"
                    f"**Đã đặt**"
                )

            elif status == "Đang dọn":

                st.warning(
                    f"### 🟡 {room['room_number']}\n\n"
                    f"**{room['room_type']}**\n\n"
                    f"**Đang dọn**"
                )

            else:

                st.markdown(
                    f"""
                    <div style="
                        padding:20px;
                        border-radius:10px;
                        background:#eeeeee;
                        margin-bottom:15px;
                    ">
                    <h3>⚫ {room['room_number']}</h3>
                    <b>{room['room_type']}</b>
                    <br><br>
                    <b>Bảo trì</b>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.divider()

    st.markdown(
        """
        🟢 **Trống** &nbsp;&nbsp;
        🔵 **Đã đặt** &nbsp;&nbsp;
        🔴 **Đang ở** &nbsp;&nbsp;
        🟡 **Đang dọn** &nbsp;&nbsp;
        ⚫ **Bảo trì**
        """
    )


# ============================================================
# CHECK-IN
# ============================================================

elif menu == "🛎️ Check-in":

    st.title("🛎️ Check-in khách")

    available_rooms = [
        r for r in rooms
        if r["status"] == "Trống"
    ]

    if not available_rooms:

        st.warning(
            "⚠️ Hiện tại không có phòng trống."
        )

    else:

        with st.form("checkin_form"):

            st.subheader(
                "Thông tin khách"
            )

            col1, col2 = st.columns(2)

            with col1:

                guest_name = st.text_input(
                    "👤 Họ và tên *"
                )

                phone = st.text_input(
                    "📞 Số điện thoại"
                )

            with col2:

                id_number = st.text_input(
                    "🪪 CCCD / Passport"
                )

                room_options = [
                    f"{r['room_number']} - "
                    f"{r['room_type']} - "
                    f"{money(r['price'])}"
                    for r in available_rooms
                ]

                selected_room = st.selectbox(
                    "🛏️ Chọn phòng *",
                    room_options
                )

            st.subheader(
                "Thông tin lưu trú"
            )

            col3, col4 = st.columns(2)

            with col3:

                checkin_date = st.date_input(
                    "Ngày check-in",
                    date.today()
                )

            with col4:

                checkout_date = st.date_input(
                    "Ngày dự kiến check-out",
                    date.today()
                )

            submit = st.form_submit_button(
                "🛎️ XÁC NHẬN CHECK-IN",
                type="primary"
            )

        if submit:

            if not guest_name.strip():

                st.error(
                    "❌ Vui lòng nhập họ tên khách."
                )

            elif checkout_date < checkin_date:

                st.error(
                    "❌ Ngày check-out không hợp lệ."
                )

            else:

                room_number = selected_room.split(" - ")[0]

                nights = (
                    checkout_date - checkin_date
                ).days

                if nights < 1:
                    nights = 1

                room = get_room(room_number)

                room_charge = (
                    nights * room["price"]
                )

                conn = get_connection()

                conn.execute("""
                    INSERT INTO guests
                    (
                        name,
                        phone,
                        id_number,
                        room_number,
                        check_in,
                        expected_check_out,
                        nights,
                        room_charge,
                        service_charge,
                        total,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, 'Đang ở')
                """, (
                    guest_name.strip(),
                    phone,
                    id_number,
                    room_number,
                    checkin_date.strftime("%d/%m/%Y"),
                    checkout_date.strftime("%d/%m/%Y"),
                    nights,
                    room_charge,
                    room_charge
                ))

                conn.commit()
                conn.close()

                change_room_status(
                    room_number,
                    "Đang ở"
                )

                st.success(
                    f"✅ Check-in thành công! "
                    f"{guest_name} - Phòng {room_number}"
                )

                st.info(
                    f"Tiền phòng dự kiến: "
                    f"**{money(room_charge)}**"
                )


# ============================================================
# CHECK-OUT
# ============================================================

elif menu == "🚪 Check-out":

    st.title("🚪 Check-out khách")

    active_guests = get_active_guests()

    if not active_guests:

        st.info(
            "Hiện không có khách đang lưu trú."
        )

    else:

        guest_options = [
            f"{g['id']} - "
            f"{g['name']} - "
            f"Phòng {g['room_number']}"
            for g in active_guests
        ]

        selected = st.selectbox(
            "👤 Chọn khách",
            guest_options
        )

        guest_id = int(
            selected.split(" - ")[0]
        )

        guest = get_guest(guest_id)

        st.divider()

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Khách",
            guest["name"]
        )

        col2.metric(
            "Phòng",
            guest["room_number"]
        )

        col3.metric(
            "Số đêm",
            guest["nights"]
        )

        st.divider()

        checkout_date = st.date_input(
            "📅 Ngày check-out",
            date.today()
        )

        room_charge = guest["room_charge"] or 0
        service_charge = guest["service_charge"] or 0

        st.write(
            f"Tiền phòng: **{money(room_charge)}**"
        )

        st.write(
            f"Tiền dịch vụ: **{money(service_charge)}**"
        )

        total = room_charge + service_charge

        st.subheader(
            f"💰 Tổng thanh toán: {money(total)}"
        )

        if st.button(
            "🚪 XÁC NHẬN CHECK-OUT",
            type="primary"
        ):

            conn = get_connection()

            conn.execute("""
                UPDATE guests
                SET actual_check_out = ?,
                    total = ?,
                    status = 'Đã trả phòng'
                WHERE id = ?
            """, (
                checkout_date.strftime("%d/%m/%Y"),
                total,
                guest_id
            ))

            conn.commit()
            conn.close()

            change_room_status(
                guest["room_number"],
                "Đang dọn"
            )

            st.success(
                f"✅ Check-out thành công cho "
                f"{guest['name']}."
            )

            st.info(
                f"💰 Khách cần thanh toán: "
                f"**{money(total)}**"
            )

            st.rerun()


# ============================================================
# KHÁCH LƯU TRÚ
# ============================================================

elif menu == "👥 Khách lưu trú":

    st.title("👥 Quản lý khách lưu trú")

    search_guest = st.text_input(
        "🔎 Tìm kiếm",
        placeholder="Tên khách / số điện thoại / số phòng"
    )

    guests = get_all_guests()

    if search_guest:

        keyword = search_guest.lower()

        guests = [
            g for g in guests
            if keyword in g["name"].lower()
            or keyword in (g["phone"] or "").lower()
            or keyword in g["room_number"].lower()
        ]

    if not guests:

        st.info(
            "Không tìm thấy khách."
        )

    else:

        for guest in guests:

            with st.container(border=True):

                col1, col2, col3, col4 = st.columns(4)

                col1.write(
                    f"**👤 {guest['name']}**"
                )

                col2.write(
                    f"📞 {guest['phone'] or '—'}"
                )

                col3.write(
                    f"🛏️ Phòng {guest['room_number']}"
                )

                if guest["status"] == "Đang ở":

                    col4.success(
                        "Đang ở"
                    )

                else:

                    col4.info(
                        "Đã trả phòng"
                    )

                st.write(
                    f"Check-in: "
                    f"{guest['check_in']}"
                )

                if guest["expected_check_out"]:

                    st.write(
                        f"Dự kiến check-out: "
                        f"{guest['expected_check_out']}"
                    )

                if guest["actual_check_out"]:

                    st.write(
                        f"Check-out thực tế: "
                        f"{guest['actual_check_out']}"
                    )

                st.write(
                    f"💰 Tổng: "
                    f"**{money(guest['total'])}**"
                )


# ============================================================
# HOUSEKEEPING
# ============================================================

elif menu == "🧹 Housekeeping":

    st.title("🧹 Housekeeping")

    cleaning = [
        r for r in rooms
        if r["status"] == "Đang dọn"
    ]

    maintenance = [
        r for r in rooms
        if r["status"] == "Bảo trì"
    ]

    col1, col2 = st.columns(2)

    col1.metric(
        "🧹 Phòng đang dọn",
        len(cleaning)
    )

    col2.metric(
        "⚫ Phòng bảo trì",
        len(maintenance)
    )

    st.divider()

    st.subheader(
        "🧹 Phòng cần vệ sinh"
    )

    if not cleaning:

        st.success(
            "Không có phòng đang chờ vệ sinh."
        )

    else:

        for room in cleaning:

            with st.container(border=True):

                col1, col2, col3 = st.columns(3)

                col1.write(
                    f"### 🧹 {room['room_number']}"
                )

                col2.write(
                    room["room_type"]
                )

                with col3:

                    if st.button(
                        "✅ Hoàn tất vệ sinh",
                        key=f"clean_{room['id']}"
                    ):

                        change_room_status(
                            room["room_number"],
                            "Trống"
                        )

                        st.success(
                            f"Phòng {room['room_number']} "
                            f"đã sẵn sàng bán."
                        )

                        st.rerun()

    st.divider()

    st.subheader(
        "⚫ Phòng bảo trì"
    )

    if not maintenance:

        st.info(
            "Không có phòng bảo trì."
        )

    else:

        for room in maintenance:

            with st.container(border=True):

                col1, col2 = st.columns(2)

                col1.write(
                    f"Phòng {room['room_number']} "
                    f"- {room['room_type']}"
                )

                with col2:

                    if st.button(
                        "🔧 Hoàn tất bảo trì",
                        key=f"maintenance_{room['id']}"
                    ):

                        change_room_status(
                            room["room_number"],
                            "Trống"
                        )

                        st.success(
                            "Phòng đã trở lại trạng thái trống."
                        )

                        st.rerun()


# ============================================================
# DOANH THU
# ============================================================

elif menu == "💰 Doanh thu":

    st.title("💰 Doanh thu")

    guests = get_all_guests()

    total_room_revenue = sum(
        g["room_charge"] or 0
        for g in guests
    )

    total_service_revenue = sum(
        g["service_charge"] or 0
        for g in guests
    )

    total_revenue = sum(
        g["total"] or 0
        for g in guests
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "🛏️ Tiền phòng",
        money(total_room_revenue)
    )

    col2.metric(
        "🛎️ Dịch vụ",
        money(total_service_revenue)
    )

    col3.metric(
        "💰 Tổng doanh thu",
        money(total_revenue)
    )

    st.divider()

    st.subheader(
        "📋 Chi tiết"
    )

    completed = [
        g for g in guests
        if g["status"] == "Đã trả phòng"
    ]

    if not completed:

        st.info(
            "Chưa có dữ liệu doanh thu."
        )

    else:

        for guest in completed:

            st.write(
                f"👤 **{guest['name']}** | "
                f"Phòng **{guest['room_number']}** | "
                f"{guest['actual_check_out']} | "
                f"**{money(guest['total'])}**"
            )


# ============================================================
# THÊM / QUẢN LÝ PHÒNG
# ============================================================

elif menu == "➕ Thêm phòng":

    st.title("➕ Thêm phòng")

    tab1, tab2 = st.tabs(
        [
            "➕ Thêm phòng mới",
            "⚙️ Chỉnh sửa phòng"
        ]
    )

    # --------------------------------------------------------
    # THÊM PHÒNG
    # --------------------------------------------------------

    with tab1:

        with st.form("add_room_form"):

            col1, col2 = st.columns(2)

            with col1:

                room_number = st.text_input(
                    "Số phòng *",
                    placeholder="Ví dụ: 901"
                )

                room_type = st.selectbox(
                    "Loại phòng",
                    [
                        "Standard",
                        "Superior",
                        "Deluxe",
                        "Suite",
                        "President Suite"
                    ]
                )

            with col2:

                floor = st.number_input(
                    "Tầng",
                    min_value=1,
                    max_value=100,
                    value=9,
                    step=1
                )

                price = st.number_input(
                    "Giá phòng / đêm",
                    min_value=0,
                    value=800000,
                    step=100000
                )

            submit = st.form_submit_button(
                "➕ THÊM PHÒNG",
                type="primary"
            )

        if submit:

            if not room_number.strip():

                st.error(
                    "❌ Vui lòng nhập số phòng."
                )

            else:

                try:

                    add_room(
                        room_number.strip(),
                        room_type,
                        price,
                        floor
                    )

                    st.success(
                        f"✅ Đã thêm phòng "
                        f"{room_number}."
                    )

                    st.rerun()

                except sqlite3.IntegrityError:

                    st.error(
                        "❌ Số phòng này đã tồn tại."
                    )

    # --------------------------------------------------------
    # CHỈNH SỬA
    # --------------------------------------------------------

    with tab2:

        if rooms:

            room_choices = [
                f"{r['room_number']} - {r['room_type']}"
                for r in rooms
            ]

            selected_room = st.selectbox(
                "Chọn phòng",
                room_choices
            )

            selected_number = selected_room.split(" - ")[0]

            room = get_room(
                selected_number
            )

            with st.form(
                f"edit_room_{room['id']}"
            ):

                new_number = st.text_input(
                    "Số phòng",
                    value=room["room_number"]
                )

                new_type = st.selectbox(
                    "Loại phòng",
                    [
                        "Standard",
                        "Superior",
                        "Deluxe",
                        "Suite",
                        "President Suite"
                    ],
                    index=[
                        "Standard",
                        "Superior",
                        "Deluxe",
                        "Suite",
                        "President Suite"
                    ].index(room["room_type"])
                )

                new_floor = st.number_input(
                    "Tầng",
                    min_value=1,
                    max_value=100,
                    value=room["floor"]
                )

                new_price = st.number_input(
                    "Giá phòng",
                    min_value=0,
                    value=float(room["price"]),
                    step=100000.0
                )

                new_status = st.selectbox(
                    "Trạng thái",
                    [
                        "Trống",
                        "Đã đặt",
                        "Đang ở",
                        "Đang dọn",
                        "Bảo trì"
                    ],
                    index=[
                        "Trống",
                        "Đã đặt",
                        "Đang ở",
                        "Đang dọn",
                        "Bảo trì"
                    ].index(room["status"])
                )

                col1, col2 = st.columns(2)

                with col1:

                    update = st.form_submit_button(
                        "💾 LƯU THAY ĐỔI",
                        type="primary"
                    )

                with col2:

                    delete = st.form_submit_button(
                        "🗑️ XÓA PHÒNG"
                    )

            if update:

                try:

                    update_room(
                        room["id"],
                        new_number,
                        new_type,
                        new_price,
                        new_floor,
                        new_status
                    )

                    st.success(
                        "✅ Đã cập nhật phòng."
                    )

                    st.rerun()

                except sqlite3.IntegrityError:

                    st.error(
                        "❌ Số phòng mới đã tồn tại."
                    )

            if delete:

                delete_room(
                    room["id"]
                )

                st.success(
                    f"Đã xóa phòng {selected_number}."
                )

                st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.sidebar.divider()

st.sidebar.caption(
    f"© {datetime.now().year} Hotel Management System"
)
```
