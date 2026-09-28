```python
import streamlit as st
import sqlite3
from datetime import datetime, date

# =========================================================
# CẤU HÌNH
# =========================================================

st.set_page_config(
    page_title="Quản lý phòng khách sạn",
    page_icon="🏨",
    layout="wide"
)

DB_NAME = "hotel_management.db"


# =========================================================
# DATABASE
# =========================================================

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT UNIQUE NOT NULL,
            room_type TEXT NOT NULL,
            price REAL NOT NULL,
            status TEXT DEFAULT 'Trống'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            room_number TEXT NOT NULL,
            check_in TEXT NOT NULL,
            check_out TEXT,
            total REAL DEFAULT 0
        )
    """)

    # Nếu database mới thì tạo dữ liệu mẫu
    cursor.execute("SELECT COUNT(*) FROM rooms")
    count = cursor.fetchone()[0]

    if count == 0:
        sample_rooms = [
            ("101", "Standard", 800000, "Trống"),
            ("102", "Standard", 800000, "Trống"),
            ("103", "Standard", 800000, "Đang ở"),
            ("201", "Deluxe", 1200000, "Trống"),
            ("202", "Deluxe", 1200000, "Đang dọn"),
            ("203", "Deluxe", 1200000, "Đã đặt"),
            ("301", "Suite", 2000000, "Trống"),
            ("302", "Suite", 2000000, "Đang ở"),
        ]

        cursor.executemany("""
            INSERT INTO rooms
            (room_number, room_type, price, status)
            VALUES (?, ?, ?, ?)
        """, sample_rooms)

    conn.commit()
    conn.close()


init_database()


# =========================================================
# HÀM DATABASE
# =========================================================

def get_rooms():
    conn = get_connection()

    rooms = conn.execute("""
        SELECT id, room_number, room_type, price, status
        FROM rooms
        ORDER BY room_number
    """).fetchall()

    conn.close()
    return rooms


def get_guests():
    conn = get_connection()

    guests = conn.execute("""
        SELECT id, name, phone, room_number,
               check_in, check_out, total
        FROM guests
        ORDER BY id DESC
    """).fetchall()

    conn.close()
    return guests


def update_room_status(room_number, status):
    conn = get_connection()

    conn.execute("""
        UPDATE rooms
        SET status = ?
        WHERE room_number = ?
    """, (status, room_number))

    conn.commit()
    conn.close()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🏨 HOTEL MANAGER")

menu = st.sidebar.radio(
    "Chọn chức năng",
    [
        "📊 Tổng quan",
        "🛏️ Quản lý phòng",
        "👤 Khách lưu trú",
        "🛎️ Check-in",
        "🚪 Check-out",
        "➕ Thêm phòng"
    ]
)


# =========================================================
# TỔNG QUAN
# =========================================================

if menu == "📊 Tổng quan":

    st.title("🏨 HỆ THỐNG QUẢN LÝ KHÁCH SẠN")

    rooms = get_rooms()
    guests = get_guests()

    total_rooms = len(rooms)

    empty_rooms = sum(
        1 for room in rooms if room[4] == "Trống"
    )

    occupied_rooms = sum(
        1 for room in rooms if room[4] == "Đang ở"
    )

    cleaning_rooms = sum(
        1 for room in rooms if room[4] == "Đang dọn"
    )

    booked_rooms = sum(
        1 for room in rooms if room[4] == "Đã đặt"
    )

    occupancy = 0

    if total_rooms > 0:
        occupancy = occupied_rooms / total_rooms * 100

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Tổng phòng", total_rooms)
    col2.metric("🟢 Phòng trống", empty_rooms)
    col3.metric("🔴 Đang ở", occupied_rooms)
    col4.metric("🟡 Đang dọn", cleaning_rooms)
    col5.metric("🔵 Đã đặt", booked_rooms)

    st.divider()

    st.subheader("📈 Công suất phòng")

    st.progress(int(occupancy))

    st.write(
        f"**Công suất hiện tại: {occupancy:.1f}%**"
    )

    st.divider()

    st.subheader("🛏️ Tình trạng phòng")

    for room in rooms:

        room_id, room_number, room_type, price, status = room

        if status == "Trống":
            icon = "🟢"

        elif status == "Đang ở":
            icon = "🔴"

        elif status == "Đang dọn":
            icon = "🟡"

        else:
            icon = "🔵"

        st.write(
            f"{icon} **Phòng {room_number}** — "
            f"{room_type} — "
            f"{price:,.0f} VNĐ — "
            f"**{status}**"
        )


# =========================================================
# QUẢN LÝ PHÒNG
# =========================================================

elif menu == "🛏️ Quản lý phòng":

    st.title("🛏️ QUẢN LÝ PHÒNG")

    rooms = get_rooms()

    col1, col2 = st.columns(2)

    with col1:
        search = st.text_input(
            "🔎 Tìm phòng",
            placeholder="Nhập số phòng..."
        )

    with col2:
        filter_status = st.selectbox(
            "📌 Lọc trạng thái",
            [
                "Tất cả",
                "Trống",
                "Đang ở",
                "Đang dọn",
                "Đã đặt"
            ]
        )

    filtered_rooms = rooms

    if search:
        filtered_rooms = [
            r for r in filtered_rooms
            if search.lower() in r[1].lower()
        ]

    if filter_status != "Tất cả":
        filtered_rooms = [
            r for r in filtered_rooms
            if r[4] == filter_status
        ]

    st.write(
        f"Hiển thị **{len(filtered_rooms)} phòng**"
    )

    for room in filtered_rooms:

        room_id, room_number, room_type, price, status = room

        with st.container(border=True):

            col1, col2, col3, col4, col5 = st.columns(
                [1, 2, 2, 2, 2]
            )

            col1.write(f"### {room_number}")

            col2.write(f"**Loại:** {room_type}")

            col3.write(
                f"**Giá:** {price:,.0f} VNĐ"
            )

            col4.write(
                f"**Trạng thái:** {status}"
            )

            with col5:

                new_status = st.selectbox(
                    "Đổi trạng thái",
                    [
                        "Trống",
                        "Đang ở",
                        "Đang dọn",
                        "Đã đặt"
                    ],
                    index=[
                        "Trống",
                        "Đang ở",
                        "Đang dọn",
                        "Đã đặt"
                    ].index(status),
                    key=f"status_{room_number}"
                )

                if new_status != status:

                    update_room_status(
                        room_number,
                        new_status
                    )

                    st.success(
                        f"Đã cập nhật phòng {room_number}"
                    )

                    st.rerun()


# =========================================================
# KHÁCH LƯU TRÚ
# =========================================================

elif menu == "👤 Khách lưu trú":

    st.title("👤 DANH SÁCH KHÁCH LƯU TRÚ")

    guests = get_guests()

    if not guests:

        st.info("Hiện chưa có khách lưu trú.")

    else:

        for guest in guests:

            (
                guest_id,
                name,
                phone,
                room_number,
                check_in,
                check_out,
                total
            ) = guest

            with st.container(border=True):

                col1, col2, col3, col4 = st.columns(4)

                col1.write(
                    f"**👤 {name}**"
                )

                col2.write(
                    f"📞 {phone}"
                )

                col3.write(
                    f"🛏️ Phòng {room_number}"
                )

                col4.write(
                    f"📅 Check-in: {check_in}"
                )

                if check_out:
                    st.write(
                        f"Check-out: {check_out}"
                    )

                if total:
                    st.write(
                        f"💰 Tổng tiền: {total:,.0f} VNĐ"
                    )


# =========================================================
# CHECK-IN
# =========================================================

elif menu == "🛎️ Check-in":

    st.title("🛎️ CHECK-IN KHÁCH")

    rooms = get_rooms()

    available_rooms = [
        r for r in rooms
        if r[4] == "Trống"
    ]

    if not available_rooms:

        st.warning(
            "⚠️ Hiện không có phòng trống."
        )

    else:

        with st.form("checkin_form"):

            name = st.text_input(
                "👤 Tên khách"
            )

            phone = st.text_input(
                "📞 Số điện thoại"
            )

            room_options = [
                f"{r[1]} - {r[2]} - {r[3]:,.0f} VNĐ"
                for r in available_rooms
            ]

            selected_room = st.selectbox(
                "🛏️ Chọn phòng",
                room_options
            )

            check_in = st.date_input(
                "📅 Ngày check-in",
                date.today()
            )

            submit = st.form_submit_button(
                "🛎️ XÁC NHẬN CHECK-IN"
            )

        if submit:

            if not name:

                st.error(
                    "Vui lòng nhập tên khách."
                )

            else:

                room_number = selected_room.split(" - ")[0]

                conn = get_connection()

                conn.execute("""
                    INSERT INTO guests
                    (name, phone, room_number, check_in)
                    VALUES (?, ?, ?, ?)
                """, (
                    name,
                    phone,
                    room_number,
                    check_in.strftime("%d/%m/%Y")
                ))

                conn.execute("""
                    UPDATE rooms
                    SET status = 'Đang ở'
                    WHERE room_number = ?
                """, (room_number,))

                conn.commit()
                conn.close()

                st.success(
                    f"✅ Check-in thành công! "
                    f"Khách {name} nhận phòng {room_number}."
                )


# =========================================================
# CHECK-OUT
# =========================================================

elif menu == "🚪 Check-out":

    st.title("🚪 CHECK-OUT KHÁCH")

    conn = get_connection()

    guests = conn.execute("""
        SELECT id, name, phone, room_number,
               check_in, check_out, total
        FROM guests
        WHERE check_out IS NULL
    """).fetchall()

    conn.close()

    if not guests:

        st.info(
            "Hiện không có khách cần check-out."
        )

    else:

        guest_options = [
            f"{g[0]} - {g[1]} - Phòng {g[3]}"
            for g in guests
        ]

        selected = st.selectbox(
            "👤 Chọn khách",
            guest_options
        )

        guest_id = int(
            selected.split(" - ")[0]
        )

        guest = next(
            g for g in guests
            if g[0] == guest_id
        )

        (
            guest_id,
            name,
            phone,
            room_number,
            check_in,
            check_out,
            old_total
        ) = guest

        st.write(
            f"**Khách:** {name}"
        )

        st.write(
            f"**Phòng:** {room_number}"
        )

        st.write(
            f"**Check-in:** {check_in}"
        )

        check_out_date = st.date_input(
            "📅 Ngày check-out",
            date.today()
        )

        try:

            checkin_date = datetime.strptime(
                check_in,
                "%d/%m/%Y"
            ).date()

            nights = (
                check_out_date - checkin_date
            ).days

            if nights < 1:
                nights = 1

        except:

            nights = 1

        conn = get_connection()

        room = conn.execute("""
            SELECT price
            FROM rooms
            WHERE room_number = ?
        """, (room_number,)).fetchone()

        conn.close()

        price = room[0]

        total = nights * price

        st.info(
            f"🛏️ Số đêm: **{nights}**\n\n"
            f"💰 Tổng tiền phòng: **{total:,.0f} VNĐ**"
        )

        if st.button(
            "🚪 XÁC NHẬN CHECK-OUT",
            type="primary"
        ):

            conn = get_connection()

            conn.execute("""
                UPDATE guests
                SET check_out = ?, total = ?
                WHERE id = ?
            """, (
                check_out_date.strftime("%d/%m/%Y"),
                total,
                guest_id
            ))

            conn.execute("""
                UPDATE rooms
                SET status = 'Đang dọn'
                WHERE room_number = ?
            """, (room_number,))

            conn.commit()
            conn.close()

            st.success(
                f"✅ Check-out thành công cho {name}."
            )

            st.info(
                f"💰 Tổng tiền cần thanh toán: "
                f"{total:,.0f} VNĐ"
            )

            st.rerun()


# =========================================================
# THÊM PHÒNG
# =========================================================

elif menu == "➕ Thêm phòng":

    st.title("➕ THÊM PHÒNG KHÁCH SẠN")

    with st.form("add_room"):

        room_number = st.text_input(
            "🛏️ Số phòng",
            placeholder="Ví dụ: 401"
        )

        room_type = st.selectbox(
            "🏨 Loại phòng",
            [
                "Standard",
                "Superior",
                "Deluxe",
                "Suite",
                "President Suite"
            ]
        )

        price = st.number_input(
            "💰 Giá phòng / đêm",
            min_value=0,
            value=800000,
            step=100000
        )

        submit = st.form_submit_button(
            "➕ THÊM PHÒNG"
        )

    if submit:

        if not room_number:

            st.error(
                "Vui lòng nhập số phòng."
            )

        else:

            try:

                conn = get_connection()

                conn.execute("""
                    INSERT INTO rooms
                    (room_number, room_type, price, status)
                    VALUES (?, ?, ?, 'Trống')
                """, (
                    room_number,
                    room_type,
                    price
                ))

                conn.commit()
                conn.close()

                st.success(
                    f"✅ Đã thêm phòng {room_number}."
                )

            except sqlite3.IntegrityError:

                st.error(
                    "❌ Số phòng này đã tồn tại."
                )


# =========================================================
# FOOTER
# =========================================================

st.sidebar.divider()

st.sidebar.caption(
    "🏨 Hotel Management System"
)

st.sidebar.caption(
    "Streamlit + SQLite"
)
```
