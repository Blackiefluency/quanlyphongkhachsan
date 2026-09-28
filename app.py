import streamlit as st
import pandas as pd
from datetime import date, timedelta
import os

# =========================================================
# 1. CẤU HÌNH APP
# =========================================================

st.set_page_config(
    page_title="Hotel Management System",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. CSS
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

</style>
""", unsafe_allow_html=True)


# =========================================================
# 3. DỮ LIỆU PHÒNG MẪU
# =========================================================

room_data = [
    [501, "Deluxe", 2, 1800000, "Available", "Clean"],
    [502, "Deluxe", 2, 1800000, "Occupied", "Clean"],
    [503, "Deluxe", 2, 1800000, "Reserved", "Clean"],
    [504, "Deluxe", 2, 1800000, "Available", "Dirty"],

    [505, "Premier", 2, 2200000, "Occupied", "Clean"],
    [506, "Premier", 3, 2200000, "Available", "Clean"],
    [507, "Premier", 3, 2200000, "Maintenance", "Out of Order"],
    [508, "Suite", 4, 3500000, "Occupied", "Clean"],

    [601, "Deluxe", 2, 1800000, "Available", "Clean"],
    [602, "Deluxe", 2, 1800000, "Occupied", "Clean"],
    [603, "Premier", 3, 2200000, "Reserved", "Clean"],
    [604, "Premier", 3, 2200000, "Available", "Clean"],
    [605, "Suite", 4, 3500000, "Occupied", "Clean"],
    [606, "Suite", 4, 3500000, "Available", "Dirty"],

    [701, "Deluxe", 2, 1800000, "Occupied", "Clean"],
    [702, "Deluxe", 2, 1800000, "Available", "Clean"],
    [703, "Premier", 3, 2200000, "Reserved", "Clean"],
    [704, "Premier", 3, 2200000, "Available", "Clean"],
    [705, "Suite", 4, 3500000, "Occupied", "Clean"],
    [706, "Suite", 4, 3500000, "Available", "Clean"],
]

room_columns = [
    "Room",
    "Room Type",
    "Capacity",
    "Price",
    "Status",
    "Housekeeping"
]


# =========================================================
# 4. DỮ LIỆU KHÁCH HÀNG
# =========================================================

customer_data = [
    [
        "CUS001",
        "Nguyễn Minh Anh",
        "0901234567",
        "Vietnam",
        "minhanh@email.com",
        "VIP",
        "images/guest_01.jpg"
    ],
    [
        "CUS002",
        "Trần Hoàng Nam",
        "0912345678",
        "Vietnam",
        "hoangnam@email.com",
        "Regular",
        "images/guest_02.jpg"
    ],
    [
        "CUS003",
        "Lê Thu Hà",
        "0923456789",
        "Vietnam",
        "thuha@email.com",
        "Regular",
        "images/guest_03.jpg"
    ],
    [
        "CUS004",
        "John Smith",
        "+1 202 555 0101",
        "USA",
        "john@email.com",
        "VIP",
        "images/guest_04.jpg"
    ],
    [
        "CUS005",
        "Emma Wilson",
        "+44 7700 900123",
        "UK",
        "emma@email.com",
        "Regular",
        "images/guest_05.jpg"
    ],
]

customer_columns = [
    "Customer ID",
    "Full Name",
    "Phone",
    "Nationality",
    "Email",
    "Customer Type",
    "Image"
]


# =========================================================
# 5. DỮ LIỆU ĐẶT PHÒNG
# =========================================================

booking_data = [
    [
        "BK001",
        "CUS001",
        "Nguyễn Minh Anh",
        502,
        "Deluxe",
        date(2026, 9, 27),
        date(2026, 9, 30),
        3,
        1800000,
        "Checked-in"
    ],
    [
        "BK002",
        "CUS002",
        "Trần Hoàng Nam",
        505,
        "Premier",
        date(2026, 9, 28),
        date(2026, 10, 1),
        3,
        2200000,
        "Checked-in"
    ],
    [
        "BK003",
        "CUS003",
        "Lê Thu Hà",
        503,
        "Deluxe",
        date(2026, 10, 2),
        date(2026, 10, 5),
        3,
        1800000,
        "Reserved"
    ],
    [
        "BK004",
        "CUS004",
        "John Smith",
        508,
        "Suite",
        date(2026, 9, 26),
        date(2026, 9, 29),
        3,
        3500000,
        "Checked-out"
    ],
    [
        "BK005",
        "CUS005",
        "Emma Wilson",
        603,
        "Premier",
        date(2026, 10, 5),
        date(2026, 10, 8),
        3,
        2200000,
        "Reserved"
    ],
]

booking_columns = [
    "Booking ID",
    "Customer ID",
    "Customer",
    "Room",
    "Room Type",
    "Check-in",
    "Check-out",
    "Nights",
    "Price/Night",
    "Status"
]


# =========================================================
# 6. DỮ LIỆU HOUSEKEEPING
# =========================================================

housekeeping_data = [
    [501, "Deluxe", "Clean", "Lan", "09:00", "Completed"],
    [502, "Deluxe", "Clean", "Mai", "09:15", "Completed"],
    [503, "Deluxe", "Clean", "Hương", "09:30", "Completed"],
    [504, "Deluxe", "Dirty", "Lan", "10:00", "In Progress"],
    [505, "Premier", "Clean", "Mai", "10:15", "Completed"],
    [506, "Premier", "Clean", "Hương", "10:30", "Completed"],
    [507, "Premier", "Out of Order", "Lan", "N/A", "Maintenance"],
    [508, "Suite", "Clean", "Mai", "11:00", "Completed"],
]

housekeeping_columns = [
    "Room",
    "Room Type",
    "Room Status",
    "Assigned Staff",
    "Time",
    "Cleaning Status"
]


# =========================================================
# 7. SESSION STATE
# =========================================================

if "rooms" not in st.session_state:
    st.session_state.rooms = pd.DataFrame(
        room_data,
        columns=room_columns
    )

if "customers" not in st.session_state:
    st.session_state.customers = pd.DataFrame(
        customer_data,
        columns=customer_columns
    )

if "bookings" not in st.session_state:
    st.session_state.bookings = pd.DataFrame(
        booking_data,
        columns=booking_columns
    )

if "housekeeping" not in st.session_state:
    st.session_state.housekeeping = pd.DataFrame(
        housekeeping_data,
        columns=housekeeping_columns
    )


# =========================================================
# 8. SIDEBAR
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

    st.info(
        "Hệ thống quản lý khách sạn\n\n"
        "Demo Version 1.0"
    )


# =========================================================
# 9. HEADER
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
# 10. DASHBOARD
# =========================================================

if menu == "📊 Dashboard":

    st.header("📊 Tổng quan khách sạn")

    rooms = st.session_state.rooms
    bookings = st.session_state.bookings
    customers = st.session_state.customers

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

    revenue = (
        bookings["Nights"]
        * bookings["Price/Night"]
    ).sum()

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

    # BIỂU ĐỒ KHÔNG DÙNG PLOTLY

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

    dashboard_rooms["Price"] = dashboard_rooms[
        "Price"
    ].apply(
        lambda x: f"{x:,.0f} VNĐ"
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
# 11. QUẢN LÝ PHÒNG
# =========================================================

elif menu == "🛏️ Quản lý phòng":

    st.header("🛏️ Quản lý phòng")

    rooms = st.session_state.rooms

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
                search_room
            )
        ]

    if status_filter != "Tất cả":

        filtered = filtered[
            filtered["Status"]
            == status_filter
        ]

    if type_filter != "Tất cả":

        filtered = filtered[
            filtered["Room Type"]
            == type_filter
        ]

    filtered_display = filtered.copy()

    filtered_display["Price"] = filtered_display[
        "Price"
    ].apply(
        lambda x: f"{x:,.0f} VNĐ"
    )

    st.dataframe(
        filtered_display,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.subheader("🔧 Cập nhật phòng")

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

        index = st.session_state.rooms.index[
            st.session_state.rooms["Room"]
            == selected_room
        ]

        st.session_state.rooms.loc[
            index,
            "Status"
        ] = new_status

        st.session_state.rooms.loc[
            index,
            "Housekeeping"
        ] = new_hk

        st.success(
            f"Đã cập nhật phòng {selected_room}"
        )

        st.rerun()


# =========================================================
# 12. QUẢN LÝ KHÁCH HÀNG
# =========================================================

elif menu == "👤 Quản lý khách hàng":

    st.header("👤 Quản lý khách hàng")

    customers = st.session_state.customers

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
            .str.contains(
                search_customer,
                case=False,
                na=False
            )
            |
            filtered_customer["Phone"]
            .str.contains(
                search_customer,
                case=False,
                na=False
            )
        )

        filtered_customer = filtered_customer[
            mask
        ]

    if customer_type_filter != "Tất cả":

        filtered_customer = filtered_customer[
            filtered_customer["Customer Type"]
            == customer_type_filter
        ]

    # Hiển thị khách

    for _, customer in filtered_customer.iterrows():

        col1, col2, col3 = st.columns(
            [1, 4, 2]
        )

        with col1:

            image_path = customer["Image"]

            if os.path.exists(image_path):

                st.image(
                    image_path,
                    width=100
                )

            else:

                st.markdown(
                    "### 👤"
                )

                st.caption(
                    "Chưa có ảnh"
                )

        with col2:

            st.markdown(
                f"### {customer['Full Name']}"
            )

            st.write(
                f"**Mã khách:** {customer['Customer ID']}"
            )

            st.write(
                f"**SĐT:** {customer['Phone']}"
            )

            st.write(
                f"**Quốc tịch:** {customer['Nationality']}"
            )

            st.write(
                f"**Email:** {customer['Email']}"
            )

        with col3:

            if customer["Customer Type"] == "VIP":

                st.success("⭐ VIP")

            else:

                st.info("Regular")

        st.divider()

    # THÊM KHÁCH

    st.subheader("➕ Thêm khách hàng")

    with st.form("customer_form"):

        col1, col2 = st.columns(2)

        with col1:

            customer_id = st.text_input(
                "Mã khách hàng",
                "CUS006"
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
                ["Regular", "VIP"]
            )

        image_path = st.text_input(
            "🖼️ Đường dẫn ảnh",
            "images/guest_06.jpg"
        )

        submit_customer = st.form_submit_button(
            "➕ Thêm khách"
        )

        if submit_customer:

            if full_name == "" or phone == "":

                st.error(
                    "Vui lòng nhập họ tên và số điện thoại."
                )

            else:

                new_customer = pd.DataFrame(
                    [[
                        customer_id,
                        full_name,
                        phone,
                        nationality,
                        email,
                        customer_type,
                        image_path
                    ]],
                    columns=customer_columns
                )

                st.session_state.customers = pd.concat(
                    [
                        st.session_state.customers,
                        new_customer
                    ],
                    ignore_index=True
                )

                st.success(
                    "Đã thêm khách hàng!"
                )

                st.rerun()


# =========================================================
# 13. ĐẶT PHÒNG
# =========================================================

elif menu == "📅 Đặt phòng":

    st.header("📅 Quản lý đặt phòng")

    bookings = st.session_state.bookings
    rooms = st.session_state.rooms
    customers = st.session_state.customers

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
            .str.contains(
                booking_search,
                case=False,
                na=False
            )
            |
            filtered_booking["Customer"]
            .str.contains(
                booking_search,
                case=False,
                na=False
            )
        )

        filtered_booking = filtered_booking[
            mask
        ]

    if booking_status != "Tất cả":

        filtered_booking = filtered_booking[
            filtered_booking["Status"]
            == booking_status
        ]

    display_booking = filtered_booking.copy()

    display_booking["Total"] = (
        display_booking["Nights"]
        * display_booking["Price/Night"]
    )

    display_booking["Price/Night"] = display_booking[
        "Price/Night"
    ].apply(
        lambda x: f"{x:,.0f} VNĐ"
    )

    display_booking["Total"] = display_booking[
        "Total"
    ].apply(
        lambda x: f"{x:,.0f} VNĐ"
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

    else:

        with st.form("booking_form"):

            col1, col2 = st.columns(2)

            with col1:

                booking_id = st.text_input(
                    "Booking ID",
                    "BK006"
                )

                customer_name = st.selectbox(
                    "Khách hàng",
                    customers["Full Name"].tolist()
                )

                room_number = st.selectbox(
                    "Phòng",
                    available_rooms["Room"].tolist()
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

            create_booking = st.form_submit_button(
                "📅 Tạo booking"
            )

            if create_booking:

                if check_out <= check_in:

                    st.error(
                        "Ngày check-out phải sau check-in."
                    )

                else:

                    customer_row = customers[
                        customers["Full Name"]
                        == customer_name
                    ].iloc[0]

                    room_row = rooms[
                        rooms["Room"]
                        == room_number
                    ].iloc[0]

                    nights = (
                        check_out - check_in
                    ).days

                    new_booking = pd.DataFrame(
                        [[
                            booking_id,
                            customer_row["Customer ID"],
                            customer_name,
                            room_number,
                            room_row["Room Type"],
                            check_in,
                            check_out,
                            nights,
                            room_row["Price"],
                            "Reserved"
                        ]],
                        columns=booking_columns
                    )

                    st.session_state.bookings = pd.concat(
                        [
                            st.session_state.bookings,
                            new_booking
                        ],
                        ignore_index=True
                    )

                    index = st.session_state.rooms.index[
                        st.session_state.rooms["Room"]
                        == room_number
                    ]

                    st.session_state.rooms.loc[
                        index,
                        "Status"
                    ] = "Reserved"

                    st.success(
                        "Đã tạo booking thành công!"
                    )

                    st.rerun()


# =========================================================
# 14. HOUSEKEEPING
# =========================================================

elif menu == "🧹 Housekeeping":

    st.header("🧹 Quản lý Housekeeping")

    housekeeping = st.session_state.housekeeping

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

    st.subheader("🔧 Cập nhật Housekeeping")

    col1, col2, col3 = st.columns(3)

    with col1:

        hk_room = st.selectbox(
            "Phòng",
            housekeeping["Room"].tolist()
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
        "💾 Cập nhật"
    ):

        index = st.session_state.housekeeping.index[
            st.session_state.housekeeping["Room"]
            == hk_room
        ]

        st.session_state.housekeeping.loc[
            index,
            "Cleaning Status"
        ] = hk_status

        st.session_state.housekeeping.loc[
            index,
            "Assigned Staff"
        ] = hk_staff

        st.success(
            f"Đã cập nhật phòng {hk_room}"
        )

        st.rerun()


# =========================================================
# 15. DOANH THU
# =========================================================

elif menu == "💰 Doanh thu":

    st.header("💰 Quản lý doanh thu")

    bookings = st.session_state.bookings

    revenue_data = bookings.copy()

    revenue_data["Revenue"] = (
        revenue_data["Nights"]
        * revenue_data["Price/Night"]
    )

    total_revenue = revenue_data[
        "Revenue"
    ].sum()

    total_nights = revenue_data[
        "Nights"
    ].sum()

    average_revenue = 0

    if len(revenue_data) > 0:

        average_revenue = (
            total_revenue
            / len(revenue_data)
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

    display_revenue = revenue_data[
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

    display_revenue["Revenue"] = display_revenue[
        "Revenue"
    ].apply(
        lambda x: f"{x:,.0f} VNĐ"
    )

    st.dataframe(
        display_revenue,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# 16. FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "🏨 Hotel Management System | "
    "Streamlit Demo"
)
