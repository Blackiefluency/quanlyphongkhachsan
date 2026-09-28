import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import date, timedelta
import os

# =========================================================
# 1. CẤU HÌNH MYSQL AIVEN
# =========================================================

# =========================================================
# THAY 5 THÔNG TIN NÀY BẰNG THÔNG TIN MYSQL CỦA AIVEN
# =========================================================

DB_HOST = "mysql-14622fa8-caithitramy2005-ebf3.h.aivencloud.com"
DB_PORT = 12969
DB_USER = "avnadmin"
DB_PASSWORD = "AVNS_BYxAanXYvtLHbkSc-i0"
DB_NAME = "defaultdb"

# Aiven MySQL thường yêu cầu SSL
DB_SSL_VERIFY = False

# Nếu bạn có file CA certificate của Aiven:
# DB_SSL_CA = "ca.pem"
# Nếu chưa có thì để None
DB_SSL_CA = None


# =========================================================
# 2. CẤU HÌNH STREAMLIT
# =========================================================

st.set_page_config(
    page_title="Hotel Management System",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# 3. CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #f5f7fa;
}

.hotel-title {
    font-size: 32px;
    font-weight: bold;
    color: #17365D;
}

.hotel-subtitle {
    color: #6b7280;
    margin-bottom: 20px;
}

.card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
}

.room-card {
    padding: 18px;
    border-radius: 12px;
    background-color: white;
    border: 1px solid #e5e7eb;
    margin-bottom: 10px;
}

div[data-testid="stMetric"] {
    background-color: white;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# 4. KẾT NỐI MYSQL AIVEN
# =========================================================

def get_db_connection():
    """
    Tạo kết nối đến MySQL Aiven.
    """

    try:

        config = {
            "host": DB_HOST,
            "port": DB_PORT,
            "user": DB_USER,
            "password": DB_PASSWORD,
            "database": DB_NAME,
            "connection_timeout": 15,
            "autocommit": True
        }

        # Aiven thường sử dụng SSL
        if DB_SSL_CA:
            config["ssl_ca"] = DB_SSL_CA
            config["ssl_verify_cert"] = True
        else:
            config["ssl_disabled"] = False
            config["ssl_verify_cert"] = DB_SSL_VERIFY

        connection = mysql.connector.connect(**config)

        return connection

    except Error as e:

        st.error(
            "❌ Không thể kết nối MySQL Aiven.\n\n"
            f"Chi tiết lỗi: {e}"
        )

        return None


# =========================================================
# 5. HÀM CHẠY SQL
# =========================================================

def execute_query(query, params=None, fetch=False):

    connection = get_db_connection()

    if connection is None:
        return None

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute(query, params or ())

        if fetch:
            result = cursor.fetchall()
        else:
            connection.commit()
            result = True

        return result

    except Error as e:

        st.error(f"❌ Database Error: {e}")

        try:
            connection.rollback()
        except:
            pass

        return None

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# 6. TẠO DATABASE TABLES
# =========================================================

def initialize_database():

    connection = get_db_connection()

    if connection is None:
        return False

    cursor = None

    try:

        cursor = connection.cursor()

        # -------------------------------------------------
        # BẢNG PHÒNG
        # -------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                room_number INT PRIMARY KEY,
                room_type VARCHAR(50) NOT NULL,
                capacity INT NOT NULL,
                price DECIMAL(15,2) NOT NULL,
                status VARCHAR(30) NOT NULL,
                housekeeping VARCHAR(30) NOT NULL
            )
        """)

        # -------------------------------------------------
        # BẢNG KHÁCH HÀNG
        # -------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id VARCHAR(30) PRIMARY KEY,
                full_name VARCHAR(150) NOT NULL,
                phone VARCHAR(50) NOT NULL,
                nationality VARCHAR(80),
                email VARCHAR(150),
                customer_type VARCHAR(30),
                image_path VARCHAR(255)
            )
        """)

        # -------------------------------------------------
        # BẢNG BOOKING
        # -------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id VARCHAR(30) PRIMARY KEY,
                customer_id VARCHAR(30) NOT NULL,
                room_number INT NOT NULL,
                check_in DATE NOT NULL,
                check_out DATE NOT NULL,
                nights INT NOT NULL,
                price_per_night DECIMAL(15,2) NOT NULL,
                status VARCHAR(30) NOT NULL,

                FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id),

                FOREIGN KEY (room_number)
                REFERENCES rooms(room_number)
            )
        """)

        # -------------------------------------------------
        # BẢNG HOUSEKEEPING
        # -------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS housekeeping (
                id INT AUTO_INCREMENT PRIMARY KEY,
                room_number INT NOT NULL,
                room_type VARCHAR(50),
                room_status VARCHAR(50),
                assigned_staff VARCHAR(100),
                cleaning_time VARCHAR(20),
                cleaning_status VARCHAR(50),

                UNIQUE(room_number),

                FOREIGN KEY (room_number)
                REFERENCES rooms(room_number)
            )
        """)

        connection.commit()

        # =================================================
        # KIỂM TRA DATABASE ĐÃ CÓ DỮ LIỆU CHƯA
        # =================================================

        cursor.execute("SELECT COUNT(*) FROM rooms")

        room_count = cursor.fetchone()[0]

        # =================================================
        # NẾU CHƯA CÓ -> THÊM DATA DEMO
        # =================================================

        if room_count == 0:

            rooms = [
                (501, "Deluxe", 2, 1800000, "Available", "Clean"),
                (502, "Deluxe", 2, 1800000, "Occupied", "Clean"),
                (503, "Deluxe", 2, 1800000, "Reserved", "Clean"),
                (504, "Deluxe", 2, 1800000, "Available", "Dirty"),

                (505, "Premier", 2, 2200000, "Occupied", "Clean"),
                (506, "Premier", 3, 2200000, "Available", "Clean"),
                (507, "Premier", 3, 2200000, "Maintenance", "Out of Order"),
                (508, "Suite", 4, 3500000, "Occupied", "Clean"),

                (601, "Deluxe", 2, 1800000, "Available", "Clean"),
                (602, "Deluxe", 2, 1800000, "Occupied", "Clean"),
                (603, "Premier", 3, 2200000, "Reserved", "Clean"),
                (604, "Premier", 3, 2200000, "Available", "Clean"),
                (605, "Suite", 4, 3500000, "Occupied", "Clean"),
                (606, "Suite", 4, 3500000, "Available", "Dirty"),

                (701, "Deluxe", 2, 1800000, "Occupied", "Clean"),
                (702, "Deluxe", 2, 1800000, "Available", "Clean"),
                (703, "Premier", 3, 2200000, "Reserved", "Clean"),
                (704, "Premier", 3, 2200000, "Available", "Clean"),
                (705, "Suite", 4, 3500000, "Occupied", "Clean"),
                (706, "Suite", 4, 3500000, "Available", "Clean")
            ]

            cursor.executemany("""
                INSERT INTO rooms
                (
                    room_number,
                    room_type,
                    capacity,
                    price,
                    status,
                    housekeeping
                )
                VALUES (%s,%s,%s,%s,%s,%s)
            """, rooms)

            # -------------------------------------------------
            # KHÁCH HÀNG DEMO
            # -------------------------------------------------

            customers = [
                (
                    "CUS001",
                    "Nguyễn Minh Anh",
                    "0901234567",
                    "Vietnam",
                    "minhanh@email.com",
                    "VIP",
                    "images/guest_01.jpg"
                ),
                (
                    "CUS002",
                    "Trần Hoàng Nam",
                    "0912345678",
                    "Vietnam",
                    "hoangnam@email.com",
                    "Regular",
                    "images/guest_02.jpg"
                ),
                (
                    "CUS003",
                    "Lê Thu Hà",
                    "0923456789",
                    "Vietnam",
                    "thuha@email.com",
                    "Regular",
                    "images/guest_03.jpg"
                ),
                (
                    "CUS004",
                    "John Smith",
                    "+1 202 555 0101",
                    "USA",
                    "john@email.com",
                    "VIP",
                    "images/guest_04.jpg"
                ),
                (
                    "CUS005",
                    "Emma Wilson",
                    "+44 7700 900123",
                    "UK",
                    "emma@email.com",
                    "Regular",
                    "images/guest_05.jpg"
                )
            ]

            cursor.executemany("""
                INSERT INTO customers
                (
                    customer_id,
                    full_name,
                    phone,
                    nationality,
                    email,
                    customer_type,
                    image_path
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, customers)

            # -------------------------------------------------
            # BOOKING DEMO
            # -------------------------------------------------

            bookings = [
                (
                    "BK001",
                    "CUS001",
                    502,
                    date(2026, 9, 27),
                    date(2026, 9, 30),
                    3,
                    1800000,
                    "Checked-in"
                ),
                (
                    "BK002",
                    "CUS002",
                    505,
                    date(2026, 9, 28),
                    date(2026, 10, 1),
                    3,
                    2200000,
                    "Checked-in"
                ),
                (
                    "BK003",
                    "CUS003",
                    503,
                    date(2026, 10, 2),
                    date(2026, 10, 5),
                    3,
                    1800000,
                    "Reserved"
                ),
                (
                    "BK004",
                    "CUS004",
                    508,
                    date(2026, 9, 26),
                    date(2026, 9, 29),
                    3,
                    3500000,
                    "Checked-out"
                ),
                (
                    "BK005",
                    "CUS005",
                    603,
                    date(2026, 10, 5),
                    date(2026, 10, 8),
                    3,
                    2200000,
                    "Reserved"
                )
            ]

            cursor.executemany("""
                INSERT INTO bookings
                (
                    booking_id,
                    customer_id,
                    room_number,
                    check_in,
                    check_out,
                    nights,
                    price_per_night,
                    status
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, bookings)

            # -------------------------------------------------
            # HOUSEKEEPING DEMO
            # -------------------------------------------------

            housekeeping = [
                (501, "Deluxe", "Clean", "Lan", "09:00", "Completed"),
                (502, "Deluxe", "Clean", "Mai", "09:15", "Completed"),
                (503, "Deluxe", "Clean", "Hương", "09:30", "Completed"),
                (504, "Deluxe", "Dirty", "Lan", "10:00", "In Progress"),
                (505, "Premier", "Clean", "Mai", "10:15", "Completed"),
                (506, "Premier", "Clean", "Hương", "10:30", "Completed"),
                (507, "Premier", "Out of Order", "Lan", "N/A", "Maintenance"),
                (508, "Suite", "Clean", "Mai", "11:00", "Completed")
            ]

            cursor.executemany("""
                INSERT INTO housekeeping
                (
                    room_number,
                    room_type,
                    room_status,
                    assigned_staff,
                    cleaning_time,
                    cleaning_status
                )
                VALUES (%s,%s,%s,%s,%s,%s)
            """, housekeeping)

            connection.commit()

        return True

    except Error as e:

        st.error(
            f"❌ Không thể khởi tạo database: {e}"
        )

        return False

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# 7. LOAD DATA
# =========================================================

def load_rooms():

    data = execute_query("""
        SELECT
            room_number AS Room,
            room_type AS `Room Type`,
            capacity AS Capacity,
            price AS Price,
            status AS Status,
            housekeeping AS Housekeeping
        FROM rooms
        ORDER BY room_number
    """, fetch=True)

    if data is None:
        return pd.DataFrame(
            columns=[
                "Room",
                "Room Type",
                "Capacity",
                "Price",
                "Status",
                "Housekeeping"
            ]
        )

    return pd.DataFrame(data)


def load_customers():

    data = execute_query("""
        SELECT
            customer_id AS `Customer ID`,
            full_name AS `Full Name`,
            phone AS Phone,
            nationality AS Nationality,
            email AS Email,
            customer_type AS `Customer Type`,
            image_path AS Image
        FROM customers
        ORDER BY full_name
    """, fetch=True)

    if data is None:
        return pd.DataFrame()

    return pd.DataFrame(data)


def load_bookings():

    data = execute_query("""
        SELECT
            b.booking_id AS `Booking ID`,
            b.customer_id AS `Customer ID`,
            c.full_name AS Customer,
            b.room_number AS Room,
            r.room_type AS `Room Type`,
            b.check_in AS `Check-in`,
            b.check_out AS `Check-out`,
            b.nights AS Nights,
            b.price_per_night AS `Price/Night`,
            b.status AS Status
        FROM bookings b

        INNER JOIN customers c
            ON b.customer_id = c.customer_id

        INNER JOIN rooms r
            ON b.room_number = r.room_number

        ORDER BY b.check_in DESC
    """, fetch=True)

    if data is None:
        return pd.DataFrame()

    return pd.DataFrame(data)


def load_housekeeping():

    data = execute_query("""
        SELECT
            room_number AS Room,
            room_type AS `Room Type`,
            room_status AS `Room Status`,
            assigned_staff AS `Assigned Staff`,
            cleaning_time AS Time,
            cleaning_status AS `Cleaning Status`
        FROM housekeeping
        ORDER BY room_number
    """, fetch=True)

    if data is None:
        return pd.DataFrame()

    return pd.DataFrame(data)


# =========================================================
# 8. KHỞI TẠO DATABASE
# =========================================================

if "database_initialized" not in st.session_state:

    with st.spinner("🔄 Đang kết nối MySQL Aiven..."):

        success = initialize_database()

    if not success:

        st.stop()

    st.session_state.database_initialized = True


# =========================================================
# 9. SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🏨 HOTEL MANAGEMENT")

    st.markdown("---")

    menu = st.radio(
        "CHỨC NĂNG",
        [
            "📊 Dashboard",
            "🛏️ Quản lý phòng",
            "👤 Quản lý khách hàng",
            "📅 Đặt phòng",
            "🧹 Housekeeping",
            "💰 Doanh thu"
        ]
    )

    st.markdown("---")

    st.success("🟢 MySQL Aiven Connected")

    st.info(
        "Hệ thống quản lý khách sạn\n\n"
        "Database: MySQL Aiven"
    )


# =========================================================
# 10. HEADER
# =========================================================

st.markdown(
    '<div class="hotel-title">🏨 HOTEL MANAGEMENT SYSTEM</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="hotel-subtitle">'
    'Hệ thống quản lý phòng, khách hàng, đặt phòng và Housekeeping'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# 11. DASHBOARD
# =========================================================

if menu == "📊 Dashboard":

    st.header("📊 Tổng quan khách sạn")

    rooms = load_rooms()
    bookings = load_bookings()
    customers = load_customers()

    total_rooms = len(rooms)

    available = len(
        rooms[rooms["Status"] == "Available"]
    )

    occupied = len(
        rooms[rooms["Status"] == "Occupied"]
    )

    reserved = len(
        rooms[rooms["Status"] == "Reserved"]
    )

    maintenance = len(
        rooms[rooms["Status"] == "Maintenance"]
    )

    occupancy = 0

    if total_rooms > 0:

        occupancy = occupied / total_rooms * 100

    if len(bookings) > 0:

        revenue = (
            bookings["Nights"] *
            bookings["Price/Night"]
        ).sum()

    else:

        revenue = 0

    # KPI

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "🏨 Tổng phòng",
        total_rooms
    )

    col2.metric(
        "🟢 Phòng trống",
        available
    )

    col3.metric(
        "🔴 Đang có khách",
        occupied
    )

    col4.metric(
        "🟡 Đã đặt",
        reserved
    )

    col5.metric(
        "📈 Công suất",
        f"{occupancy:.1f}%"
    )

    st.markdown("---")

    # BIỂU ĐỒ

    st.subheader("📊 Trạng thái phòng")

    chart_data = pd.DataFrame(
        {
            "Số phòng": [
                available,
                occupied,
                reserved,
                maintenance
            ]
        },
        index=[
            "Available",
            "Occupied",
            "Reserved",
            "Maintenance"
        ]
    )

    st.bar_chart(chart_data)

    st.markdown("---")

    st.subheader("🛏️ Danh sách phòng")

    dashboard_rooms = rooms.copy()

    if len(dashboard_rooms) > 0:

        dashboard_rooms["Price"] = (
            dashboard_rooms["Price"]
            .apply(
                lambda x: f"{x:,.0f} VNĐ"
            )
        )

    st.dataframe(
        dashboard_rooms,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.subheader("💰 Doanh thu hiện tại")

    st.success(
        f"Tổng doanh thu dự kiến: "
        f"{revenue:,.0f} VNĐ"
    )


# =========================================================
# 12. QUẢN LÝ PHÒNG
# =========================================================

elif menu == "🛏️ Quản lý phòng":

    st.header("🛏️ Quản lý phòng")

    rooms = load_rooms()

    col1, col2, col3 = st.columns(3)

    with col1:

        search_room = st.text_input(
            "🔎 Tìm số phòng",
            placeholder="VD: 501"
        )

    with col2:

        status_filter = st.selectbox(
            "Trạng thái",
            [
                "Tất cả",
                "Available",
                "Occupied",
                "Reserved",
                "Maintenance"
            ]
        )

    with col3:

        type_filter = st.selectbox(
            "Loại phòng",
            [
                "Tất cả",
                "Deluxe",
                "Premier",
                "Suite"
            ]
        )

    filtered = rooms.copy()

    if search_room:

        filtered = filtered[
            filtered["Room"]
            .astype(str)
            .str.contains(
                search_room,
                case=False,
                na=False
            )
        ]

    if status_filter != "Tất cả":

        filtered = filtered[
            filtered["Status"] ==
            status_filter
        ]

    if type_filter != "Tất cả":

        filtered = filtered[
            filtered["Room Type"] ==
            type_filter
        ]

    filtered_display = filtered.copy()

    if len(filtered_display) > 0:

        filtered_display["Price"] = (
            filtered_display["Price"]
            .apply(
                lambda x: f"{x:,.0f} VNĐ"
            )
        )

    st.dataframe(
        filtered_display,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.subheader("🔧 Cập nhật phòng")

    if len(rooms) > 0:

        col1, col2, col3 = st.columns(3)

        with col1:

            selected_room = st.selectbox(
                "Chọn phòng",
                rooms["Room"].tolist()
            )

        with col2:

            new_status = st.selectbox(
                "Trạng thái mới",
                [
                    "Available",
                    "Occupied",
                    "Reserved",
                    "Maintenance"
                ]
            )

        with col3:

            new_hk = st.selectbox(
                "Housekeeping",
                [
                    "Clean",
                    "Dirty",
                    "Out of Order"
                ]
            )

        if st.button(
            "💾 Lưu thay đổi",
            use_container_width=True
        ):

            result = execute_query(
                """
                UPDATE rooms

                SET
                    status = %s,
                    housekeeping = %s

                WHERE room_number = %s
                """,
                (
                    new_status,
                    new_hk,
                    selected_room
                )
            )

            if result:

                st.success(
                    f"Đã cập nhật phòng {selected_room}"
                )

                st.rerun()


# =========================================================
# 13. QUẢN LÝ KHÁCH HÀNG
# =========================================================

elif menu == "👤 Quản lý khách hàng":

    st.header("👤 Quản lý khách hàng")

    customers = load_customers()

    st.info(
        "🖼️ Cột Image đã được chuẩn bị sẵn. "
        "Bạn có thể chèn ảnh khách vào thư mục images."
    )

    search_customer = st.text_input(
        "🔎 Tìm khách hàng",
        placeholder="Nhập tên hoặc số điện thoại..."
    )

    customer_type_filter = st.selectbox(
        "Loại khách",
        [
            "Tất cả",
            "VIP",
            "Regular"
        ]
    )

    filtered_customer = customers.copy()

    if search_customer:

        mask = (
            filtered_customer["Full Name"]
            .astype(str)
            .str.contains(
                search_customer,
                case=False,
                na=False
            )
            |
            filtered_customer["Phone"]
            .astype(str)
            .str.contains(
                search_customer,
                case=False,
                na=False
            )
        )

        filtered_customer = (
            filtered_customer[mask]
        )

    if customer_type_filter != "Tất cả":

        filtered_customer = (
            filtered_customer[
                filtered_customer["Customer Type"]
                == customer_type_filter
            ]
        )

    # -----------------------------------------------------
    # HIỂN THỊ KHÁCH
    # -----------------------------------------------------

    for _, customer in filtered_customer.iterrows():

        col1, col2, col3 = st.columns(
            [1, 4, 2]
        )

        with col1:

            image_path = customer["Image"]

            if (
                image_path
                and os.path.exists(image_path)
            ):

                st.image(
                    image_path,
                    width=100
                )

            else:

                st.markdown("### 👤")

                st.caption(
                    "Chưa có ảnh"
                )

        with col2:

            st.markdown(
                f"### {customer['Full Name']}"
            )

            st.write(
                f"**Mã khách:** "
                f"{customer['Customer ID']}"
            )

            st.write(
                f"**SĐT:** "
                f"{customer['Phone']}"
            )

            st.write(
                f"**Quốc tịch:** "
                f"{customer['Nationality']}"
            )

            st.write(
                f"**Email:** "
                f"{customer['Email']}"
            )

        with col3:

            if (
                customer["Customer Type"]
                == "VIP"
            ):

                st.success("⭐ VIP")

            else:

                st.info("Regular")

        st.divider()

    # -----------------------------------------------------
    # THÊM KHÁCH
    # -----------------------------------------------------

    st.subheader("➕ Thêm khách hàng")

    with st.form("customer_form"):

        col1, col2 = st.columns(2)

        with col1:

            customer_id = st.text_input(
                "Mã khách hàng"
            )

            full_name = st.text_input(
                "Họ và tên"
            )

            phone = st.text_input(
                "Số điện thoại"
            )

        with col2:

            nationality = st.text_input(
                "Quốc tịch",
                "Vietnam"
            )

            email = st.text_input(
                "Email"
            )

            customer_type = st.selectbox(
                "Loại khách",
                [
                    "Regular",
                    "VIP"
                ]
            )

        image_path = st.text_input(
            "🖼️ Đường dẫn ảnh",
            "images/guest_06.jpg"
        )

        submit_customer = (
            st.form_submit_button(
                "➕ Thêm khách"
            )
        )

        if submit_customer:

            if (
                customer_id == ""
                or full_name == ""
                or phone == ""
            ):

                st.error(
                    "Vui lòng nhập mã khách, "
                    "họ tên và số điện thoại."
                )

            else:

                # Kiểm tra ID trùng

                check = execute_query(
                    """
                    SELECT customer_id
                    FROM customers
                    WHERE customer_id = %s
                    """,
                    (customer_id,),
                    fetch=True
                )

                if check:

                    st.error(
                        "❌ Mã khách hàng đã tồn tại."
                    )

                else:

                    result = execute_query(
                        """
                        INSERT INTO customers
                        (
                            customer_id,
                            full_name,
                            phone,
                            nationality,
                            email,
                            customer_type,
                            image_path
                        )

                        VALUES
                        (%s,%s,%s,%s,%s,%s,%s)
                        """,
                        (
                            customer_id,
                            full_name,
                            phone,
                            nationality,
                            email,
                            customer_type,
                            image_path
                        )
                    )

                    if result:

                        st.success(
                            "✅ Đã thêm khách hàng!"
                        )

                        st.rerun()


# =========================================================
# 14. ĐẶT PHÒNG
# =========================================================

elif menu == "📅 Đặt phòng":

    st.header("📅 Quản lý đặt phòng")

    bookings = load_bookings()

    rooms = load_rooms()

    customers = load_customers()

    booking_search = st.text_input(
        "🔎 Tìm booking hoặc tên khách"
    )

    booking_status = st.selectbox(
        "Trạng thái",
        [
            "Tất cả",
            "Reserved",
            "Checked-in",
            "Checked-out"
        ]
    )

    filtered_booking = bookings.copy()

    if booking_search:

        mask = (
            filtered_booking["Booking ID"]
            .astype(str)
            .str.contains(
                booking_search,
                case=False,
                na=False
            )
            |
            filtered_booking["Customer"]
            .astype(str)
            .str.contains(
                booking_search,
                case=False,
                na=False
            )
        )

        filtered_booking = (
            filtered_booking[mask]
        )

    if booking_status != "Tất cả":

        filtered_booking = (
            filtered_booking[
                filtered_booking["Status"]
                == booking_status
            ]
        )

    display_booking = (
        filtered_booking.copy()
    )

    if len(display_booking) > 0:

        display_booking["Total"] = (
            display_booking["Nights"]
            * display_booking["Price/Night"]
        )

        display_booking["Price/Night"] = (
            display_booking["Price/Night"]
            .apply(
                lambda x:
                f"{x:,.0f} VNĐ"
            )
        )

        display_booking["Total"] = (
            display_booking["Total"]
            .apply(
                lambda x:
                f"{x:,.0f} VNĐ"
            )
        )

    st.dataframe(
        display_booking,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.subheader("➕ Tạo đặt phòng mới")

    available_rooms = rooms[
        rooms["Status"] == "Available"
    ]

    if len(available_rooms) == 0:

        st.warning(
            "Hiện tại không có phòng trống."
        )

    elif len(customers) == 0:

        st.warning(
            "Chưa có khách hàng."
        )

    else:

        with st.form("booking_form"):

            col1, col2 = st.columns(2)

            with col1:

                booking_id = st.text_input(
                    "Booking ID"
                )

                customer_name = (
                    st.selectbox(
                        "Khách hàng",
                        customers[
                            "Full Name"
                        ].tolist()
                    )
                )

                room_number = (
                    st.selectbox(
                        "Phòng",
                        available_rooms[
                            "Room"
                        ].tolist()
                    )
                )

            with col2:

                check_in = st.date_input(
                    "Check-in",
                    date.today()
                )

                check_out = st.date_input(
                    "Check-out",
                    date.today()
                    + timedelta(days=1)
                )

            create_booking = (
                st.form_submit_button(
                    "📅 Tạo booking"
                )
            )

            if create_booking:

                if booking_id == "":

                    st.error(
                        "Vui lòng nhập Booking ID."
                    )

                elif check_out <= check_in:

                    st.error(
                        "Ngày check-out phải sau "
                        "check-in."
                    )

                else:

                    # Kiểm tra booking ID

                    booking_exists = (
                        execute_query(
                            """
                            SELECT booking_id
                            FROM bookings
                            WHERE booking_id = %s
                            """,
                            (booking_id,),
                            fetch=True
                        )
                    )

                    if booking_exists:

                        st.error(
                            "❌ Booking ID đã tồn tại."
                        )

                    else:

                        customer_row = (
                            customers[
                                customers["Full Name"]
                                == customer_name
                            ].iloc[0]
                        )

                        room_row = (
                            rooms[
                                rooms["Room"]
                                == room_number
                            ].iloc[0]
                        )

                        nights = (
                            check_out -
                            check_in
                        ).days

                        # -------------------------------------------------
                        # INSERT BOOKING
                        # -------------------------------------------------

                        result = execute_query(
                            """
                            INSERT INTO bookings
                            (
                                booking_id,
                                customer_id,
                                room_number,
                                check_in,
                                check_out,
                                nights,
                                price_per_night,
                                status
                            )

                            VALUES
                            (%s,%s,%s,%s,%s,%s,%s,%s)
                            """,
                            (
                                booking_id,
                                customer_row[
                                    "Customer ID"
                                ],
                                room_number,
                                check_in,
                                check_out,
                                nights,
                                room_row["Price"],
                                "Reserved"
                            )
                        )

                        if result:

                            # -------------------------------------------------
                            # CẬP NHẬT PHÒNG
                            # -------------------------------------------------

                            execute_query(
                                """
                                UPDATE rooms

                                SET status = 'Reserved'

                                WHERE room_number = %s
                                """,
                                (room_number,)
                            )

                            st.success(
                                "✅ Đã tạo booking thành công!"
                            )

                            st.rerun()


# =========================================================
# 15. HOUSEKEEPING
# =========================================================

elif menu == "🧹 Housekeeping":

    st.header("🧹 Quản lý Housekeeping")

    housekeeping = (
        load_housekeeping()
    )

    col1, col2, col3 = st.columns(3)

    completed = len(
        housekeeping[
            housekeeping["Cleaning Status"]
            == "Completed"
        ]
    )

    in_progress = len(
        housekeeping[
            housekeeping["Cleaning Status"]
            == "In Progress"
        ]
    )

    maintenance = len(
        housekeeping[
            housekeeping["Cleaning Status"]
            == "Maintenance"
        ]
    )

    col1.metric(
        "✅ Hoàn thành",
        completed
    )

    col2.metric(
        "🔄 Đang xử lý",
        in_progress
    )

    col3.metric(
        "🔧 Bảo trì",
        maintenance
    )

    st.markdown("---")

    st.dataframe(
        housekeeping,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.subheader(
        "🔧 Cập nhật Housekeeping"
    )

    if len(housekeeping) > 0:

        col1, col2, col3 = st.columns(3)

        with col1:

            hk_room = st.selectbox(
                "Phòng",
                housekeeping[
                    "Room"
                ].tolist()
            )

        with col2:

            hk_status = st.selectbox(
                "Trạng thái",
                [
                    "Completed",
                    "In Progress",
                    "Pending",
                    "Maintenance"
                ]
            )

        with col3:

            hk_staff = st.text_input(
                "Nhân viên phụ trách",
                "Lan"
            )

        if st.button(
            "💾 Cập nhật",
            use_container_width=True
        ):

            result = execute_query(
                """
                UPDATE housekeeping

                SET
                    cleaning_status = %s,
                    assigned_staff = %s

                WHERE room_number = %s
                """,
                (
                    hk_status,
                    hk_staff,
                    hk_room
                )
            )

            if result:

                st.success(
                    f"Đã cập nhật phòng {hk_room}"
                )

                st.rerun()


# =========================================================
# 16. DOANH THU
# =========================================================

elif menu == "💰 Doanh thu":

    st.header("💰 Quản lý doanh thu")

    bookings = load_bookings()

    if len(bookings) == 0:

        st.info(
            "Chưa có dữ liệu doanh thu."
        )

    else:

        revenue_data = (
            bookings.copy()
        )

        revenue_data["Revenue"] = (
            revenue_data["Nights"]
            * revenue_data["Price/Night"]
        )

        total_revenue = (
            revenue_data["Revenue"]
            .sum()
        )

        total_nights = (
            revenue_data["Nights"]
            .sum()
        )

        average_revenue = (
            total_revenue /
            len(revenue_data)
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "💰 Tổng doanh thu",
            f"{total_revenue:,.0f} VNĐ"
        )

        col2.metric(
            "🌙 Tổng số đêm",
            f"{total_nights} đêm"
        )

        col3.metric(
            "🧾 TB/Booking",
            f"{average_revenue:,.0f} VNĐ"
        )

        st.markdown("---")

        st.subheader(
            "📊 Doanh thu theo loại phòng"
        )

        revenue_by_type = (
            revenue_data
            .groupby("Room Type")["Revenue"]
            .sum()
        )

        st.bar_chart(
            revenue_by_type
        )

        st.markdown("---")

        st.subheader(
            "📋 Chi tiết doanh thu"
        )

        display_revenue = (
            revenue_data[
                [
                    "Booking ID",
                    "Customer",
                    "Room",
                    "Room Type",
                    "Nights",
                    "Revenue",
                    "Status"
                ]
            ].copy()
        )

        display_revenue["Revenue"] = (
            display_revenue["Revenue"]
            .apply(
                lambda x:
                f"{x:,.0f} VNĐ"
            )
        )

        st.dataframe(
            display_revenue,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# 17. FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "🏨 Hotel Management System | "
    "Streamlit + MySQL Aiven"
)
