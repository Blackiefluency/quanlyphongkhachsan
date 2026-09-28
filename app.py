import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import plotly.express as px
import os

# ============================================================
# CẤU HÌNH TRANG
# ============================================================

st.set_page_config(
    page_title="Hotel Management System",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS GIAO DIỆN
# ============================================================

st.markdown("""
<style>
    .main {
        background-color: #f5f7fa;
    }

    .hotel-title {
        font-size: 32px;
        font-weight: 700;
        color: #17365D;
        margin-bottom: 5px;
    }

    .hotel-subtitle {
        color: #6b7280;
        font-size: 15px;
        margin-bottom: 25px;
    }

    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
    }

    .metric-title {
        color: #6b7280;
        font-size: 14px;
    }

    .metric-value {
        color: #17365D;
        font-size: 28px;
        font-weight: bold;
    }

    .section-title {
        font-size: 22px;
        font-weight: 700;
        color: #17365D;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    div[data-testid="stSidebar"] {
        background-color: #17365D;
    }

    div[data-testid="stSidebar"] * {
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# DỮ LIỆU MẪU
# ============================================================

ROOM_DATA = [
    [501, "Deluxe", 2, 1800000, "Available", "Clean", ""],
    [502, "Deluxe", 2, 1800000, "Occupied", "Clean", ""],
    [503, "Deluxe", 2, 1800000, "Reserved", "Clean", ""],
    [504, "Deluxe", 2, 1800000, "Available", "Dirty", ""],
    [505, "Premier", 2, 2200000, "Occupied", "Clean", ""],
    [506, "Premier", 3, 2200000, "Available", "Clean", ""],
    [507, "Premier", 3, 2200000, "Maintenance", "Out of Order", ""],
    [508, "Suite", 4, 3500000, "Occupied", "Clean", ""],

    [601, "Deluxe", 2, 1800000, "Available", "Clean", ""],
    [602, "Deluxe", 2, 1800000, "Occupied", "Clean", ""],
    [603, "Premier", 3, 2200000, "Reserved", "Clean", ""],
    [604, "Premier", 3, 2200000, "Available", "Clean", ""],
    [605, "Suite", 4, 3500000, "Occupied", "Clean", ""],
    [606, "Suite", 4, 3500000, "Available", "Dirty", ""],

    [701, "Deluxe", 2, 1800000, "Occupied", "Clean", ""],
    [702, "Deluxe", 2, 1800000, "Available", "Clean", ""],
    [703, "Premier", 3, 2200000, "Reserved", "Clean", ""],
    [704, "Premier", 3, 2200000, "Available", "Clean", ""],
    [705, "Suite", 4, 3500000, "Occupied", "Clean", ""],
    [706, "Suite", 4, 3500000, "Available", "Clean", ""],
]

ROOM_COLUMNS = [
    "Room",
    "Room Type",
    "Capacity",
    "Price",
    "Status",
    "Housekeeping",
    "Image"
]

CUSTOMER_DATA = [
    ["CUS001", "Nguyễn Minh Anh", "0901234567", "Vietnam", "minhanh@email.com", "VIP", "images/guest_01.jpg"],
    ["CUS002", "Trần Hoàng Nam", "0912345678", "Vietnam", "hoangnam@email.com", "Regular", "images/guest_02.jpg"],
    ["CUS003", "Lê Thu Hà", "0923456789", "Vietnam", "thuha@email.com", "Regular", "images/guest_03.jpg"],
    ["CUS004", "John Smith", "+1 202 555 0101", "USA", "johnsmith@email.com", "VIP", "images/guest_04.jpg"],
    ["CUS005", "Emma Wilson", "+44 7700 900123", "UK", "emma@email.com", "Regular", "images/guest_05.jpg"],
    ["CUS006", "Phạm Quốc Bảo", "0934567890", "Vietnam", "quocbao@email.com", "Regular", "images/guest_06.jpg"],
]

CUSTOMER_COLUMNS = [
    "Customer ID",
    "Full Name",
    "Phone",
    "Nationality",
    "Email",
    "Customer Type",
    "Image"
]

BOOKING_DATA = [
    ["BK001", "CUS001", "Nguyễn Minh Anh", 502, "Deluxe",
     date(2026, 9, 27), date(2026, 9, 30), 3, 1800000, "Checked-in"],

    ["BK002", "CUS002", "Trần Hoàng Nam", 505, "Premier",
     date(2026, 9, 28), date(2026, 10, 1), 3, 2200000, "Checked-in"],

    ["BK003", "CUS003", "Lê Thu Hà", 503, "Deluxe",
     date(2026, 10, 2), date(2026, 10, 5), 3, 1800000, "Reserved"],

    ["BK004", "CUS004", "John Smith", 508, "Suite",
     date(2026, 9, 26), date(2026, 9, 29), 3, 3500000, "Checked-out"],

    ["BK005", "CUS005", "Emma Wilson", 603, "Premier",
     date(2026, 10, 5), date(2026, 10, 8), 3, 2200000, "Reserved"],

    ["BK006", "CUS006", "Phạm Quốc Bảo", 701, "Deluxe",
     date(2026, 9, 25), date(2026, 9, 27), 2, 1800000, "Checked-out"],
]

BOOKING_COLUMNS = [
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

HOUSEKEEPING_DATA = [
    [501, "Deluxe", "Clean", "Lan", "09:00", "Completed"],
    [502, "Deluxe", "Clean", "Mai", "09:15", "Completed"],
    [503, "Deluxe", "Clean", "Hương", "09:30", "Completed"],
    [504, "Deluxe", "Dirty", "Lan", "10:00", "In Progress"],
    [505, "Premier", "Clean", "Mai", "10:15", "Completed"],
    [506, "Premier", "Clean", "Hương", "10:30", "Completed"],
    [507, "Premier", "Out of Order", "Lan", "N/A", "Maintenance"],
    [508, "Suite", "Clean", "Mai", "11:00", "Completed"],
]

HOUSEKEEPING_COLUMNS = [
    "Room",
    "Room Type",
    "Room Status",
    "Assigned Staff",
    "Time",
    "Cleaning Status"
]


# ============================================================
# SESSION STATE
# ============================================================

if "rooms" not in st.session_state:
    st.session_state.rooms = pd.DataFrame(ROOM_DATA, columns=ROOM_COLUMNS)

if "customers" not in st.session_state:
    st.session_state.customers = pd.DataFrame(
        CUSTOMER_DATA,
        columns=CUSTOMER_COLUMNS
    )

if "bookings" not in st.session_state:
    st.session_state.bookings = pd.DataFrame(
        BOOKING_DATA,
        columns=BOOKING_COLUMNS
    )

if "housekeeping" not in st.session_state:
    st.session_state.housekeeping = pd.DataFrame(
        HOUSEKEEPING_DATA,
        columns=HOUSEKEEPING_COLUMNS
    )


rooms = st.session_state.rooms
customers = st.session_state.customers
bookings = st.session_state.bookings
housekeeping = st.session_state.housekeeping


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🏨 HOTEL SYSTEM")
    st.markdown("---")

    menu = st.radio(
        "MENU",
        [
            "📊 Dashboard",
            "🛏️ Quản lý phòng",
            "👤 Quản lý khách hàng",
            "📅 Quản lý đặt phòng",
            "🧹 Housekeeping",
            "💰 Doanh thu",
        ]
    )

    st.markdown("---")
    st.caption("Hotel Management System")
    st.caption("Demo Version 1.0")


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="hotel-title">🏨 HOTEL MANAGEMENT SYSTEM</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="hotel-subtitle">'
    'Hệ thống quản lý phòng và vận hành khách sạn'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# DASHBOARD
# ============================================================

if menu == "📊 Dashboard":

    st.markdown(
        '<div class="section-title">📊 Tổng quan khách sạn</div>',
        unsafe_allow_html=True
    )

    total_rooms = len(rooms)
    available_rooms = len(
        rooms[rooms["Status"] == "Available"]
    )
    occupied_rooms = len(
        rooms[rooms["Status"] == "Occupied"]
    )
    reserved_rooms = len(
        rooms[rooms["Status"] == "Reserved"]
    )

    occupancy_rate = (
        occupied_rooms / total_rooms * 100
        if total_rooms > 0 else 0
    )

    revenue = (
        bookings["Nights"] * bookings["Price/Night"]
    ).sum()

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("🏨 Tổng số phòng", total_rooms)

    with col2:
        st.metric("🟢 Phòng trống", available_rooms)

    with col3:
        st.metric("🔴 Đang có khách", occupied_rooms)

    with col4:
        st.metric("🟡 Đã đặt", reserved_rooms)

    with col5:
        st.metric(
            "📈 Công suất",
            f"{occupancy_rate:.1f}%"
        )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### Trạng thái phòng")

        status_count = (
            rooms["Status"]
            .value_counts()
            .reset_index()
        )

        status_count.columns = [
            "Status",
            "Number"
        ]

        fig = px.pie(
            status_count,
            names="Status",
            values="Number",
            hole=0.45,
            title="Room Status"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        st.markdown("### Loại phòng")

        room_type = (
            rooms["Room Type"]
            .value_counts()
            .reset_index()
        )

        room_type.columns = [
            "Room Type",
            "Number"
        ]

        fig2 = px.bar(
            room_type,
            x="Room Type",
            y="Number",
            title="Số lượng phòng theo loại"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    st.markdown("---")

    st.markdown("### 📋 Tình trạng phòng hiện tại")

    display_rooms = rooms[
        [
            "Room",
            "Room Type",
            "Capacity",
            "Price",
            "Status",
            "Housekeeping"
        ]
    ].copy()

    display_rooms["Price"] = display_rooms["Price"].apply(
        lambda x: f"{x:,.0f} VNĐ"
    )

    st.dataframe(
        display_rooms,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# QUẢN LÝ PHÒNG
# ============================================================

elif menu == "🛏️ Quản lý phòng":

    st.markdown(
        '<div class="section-title">🛏️ Quản lý phòng</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        room_search = st.text_input(
            "🔎 Tìm phòng",
            placeholder="VD: 501"
        )

    with col2:
        room_status_filter = st.selectbox(
            "Trạng thái",
            ["Tất cả", "Available", "Occupied", "Reserved", "Maintenance"]
        )

    with col3:
        room_type_filter = st.selectbox(
            "Loại phòng",
            ["Tất cả", "Deluxe", "Premier", "Suite"]
        )

    filtered_rooms = rooms.copy()

    if room_search:
        filtered_rooms = filtered_rooms[
            filtered_rooms["Room"]
            .astype(str)
            .str.contains(room_search)
        ]

    if room_status_filter != "Tất cả":
        filtered_rooms = filtered_rooms[
            filtered_rooms["Status"] == room_status_filter
        ]

    if room_type_filter != "Tất cả":
        filtered_rooms = filtered_rooms[
            filtered_rooms["Room Type"] == room_type_filter
        ]

    st.dataframe(
        filtered_rooms,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.markdown("### ➕ Cập nhật trạng thái phòng")

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
        new_hk_status = st.selectbox(
            "Housekeeping",
            [
                "Clean",
                "Dirty",
                "Out of Order"
            ]
        )

    if st.button(
        "💾 Cập nhật phòng",
        use_container_width=True
    ):

        idx = rooms.index[
            rooms["Room"] == selected_room
        ]

        st.session_state.rooms.loc[
            idx, "Status"
        ] = new_status

        st.session_state.rooms.loc[
            idx, "Housekeeping"
        ] = new_hk_status

        st.success(
            f"Đã cập nhật phòng {selected_room}!"
        )

        st.rerun()


# ============================================================
# QUẢN LÝ KHÁCH HÀNG
# ============================================================

elif menu == "👤 Quản lý khách hàng":

    st.markdown(
        '<div class="section-title">👤 Quản lý khách hàng</div>',
        unsafe_allow_html=True
    )

    st.info(
        "🖼️ Cột Image đã được tạo sẵn. "
        "Bạn có thể thay đường dẫn bằng ảnh khách sau."
    )

    search_customer = st.text_input(
        "🔎 Tìm khách hàng",
        placeholder="Nhập tên, số điện thoại hoặc mã khách..."
    )

    customer_type = st.selectbox(
        "Loại khách",
        ["Tất cả", "VIP", "Regular"]
    )

    filtered_customers = customers.copy()

    if search_customer:

        mask = (
            filtered_customers["Full Name"]
            .str.contains(
                search_customer,
                case=False,
                na=False
            )
            |
            filtered_customers["Phone"]
            .str.contains(
                search_customer,
                case=False,
                na=False
            )
            |
            filtered_customers["Customer ID"]
            .str.contains(
                search_customer,
                case=False,
                na=False
            )
        )

        filtered_customers = filtered_customers[mask]

    if customer_type != "Tất cả":
        filtered_customers = filtered_customers[
            filtered_customers["Customer Type"] == customer_type
        ]

    st.dataframe(
        filtered_customers,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.markdown("### ➕ Thêm khách hàng")

    with st.form("add_customer_form"):

        col1, col2 = st.columns(2)

        with col1:
            customer_id = st.text_input(
                "Mã khách hàng",
                "CUS007"
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

            ctype = st.selectbox(
                "Loại khách",
                ["Regular", "VIP"]
            )

        image_path = st.text_input(
            "🖼️ Đường dẫn ảnh khách",
            "images/guest_07.jpg"
        )

        submit = st.form_submit_button(
            "➕ Thêm khách hàng",
            use_container_width=True
        )

        if submit:

            if not full_name or not phone:
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
                        ctype,
                        image_path
                    ]],
                    columns=CUSTOMER_COLUMNS
                )

                st.session_state.customers = pd.concat(
                    [
                        st.session_state.customers,
                        new_customer
                    ],
                    ignore_index=True
                )

                st.success(
                    "Đã thêm khách hàng thành công!"
                )

                st.rerun()


# ============================================================
# QUẢN LÝ ĐẶT PHÒNG
# ============================================================

elif menu == "📅 Quản lý đặt phòng":

    st.markdown(
        '<div class="section-title">📅 Quản lý đặt phòng</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        booking_search = st.text_input(
            "🔎 Tìm booking",
            placeholder="BK001 / tên khách..."
        )

    with col2:
        booking_status = st.selectbox(
            "Trạng thái booking",
            [
                "Tất cả",
                "Reserved",
                "Checked-in",
                "Checked-out",
                "Cancelled"
            ]
        )

    filtered_bookings = bookings.copy()

    if booking_search:

        mask = (
            filtered_bookings["Booking ID"]
            .str.contains(
                booking_search,
                case=False,
                na=False
            )
            |
            filtered_bookings["Customer"]
            .str.contains(
                booking_search,
                case=False,
                na=False
            )
        )

        filtered_bookings = filtered_bookings[mask]

    if booking_status != "Tất cả":

        filtered_bookings = filtered_bookings[
            filtered_bookings["Status"] == booking_status
        ]

    display_booking = filtered_bookings.copy()

    display_booking["Check-in"] = display_booking[
        "Check-in"
    ].astype(str)

    display_booking["Check-out"] = display_booking[
        "Check-out"
    ].astype(str)

    display_booking["Total"] = (
        display_booking["Nights"]
        * display_booking["Price/Night"]
    )

    display_booking["Price/Night"] = display_booking[
        "Price/Night"
    ].apply(lambda x: f"{x:,.0f} VNĐ")

    display_booking["Total"] = display_booking[
        "Total"
    ].apply(lambda x: f"{x:,.0f} VNĐ")

    st.dataframe(
        display_booking,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.markdown("### ➕ Tạo đặt phòng mới")

    with st.form("booking_form"):

        col1, col2, col3 = st.columns(3)

        with col1:

            new_booking_id = st.text_input(
                "Booking ID",
                "BK007"
            )

            customer_list = customers[
                "Full Name"
            ].tolist()

            selected_customer = st.selectbox(
                "Khách hàng",
                customer_list
            )

        with col2:

            available_room_list = rooms[
                rooms["Status"] == "Available"
            ]["Room"].tolist()

            if available_room_list:

                selected_room_booking = st.selectbox(
                    "Phòng",
                    available_room_list
                )

            else:

                st.warning(
                    "Không có phòng trống."
                )

                selected_room_booking = None

        with col3:

            check_in = st.date_input(
                "Ngày check-in",
                date.today()
            )

            check_out = st.date_input(
                "Ngày check-out",
                date.today() + timedelta(days=1)
            )

        submit_booking = st.form_submit_button(
            "📅 Tạo booking",
            use_container_width=True
        )

        if submit_booking:

            if selected_room_booking is None:
                st.error("Không có phòng để đặt.")

            elif check_out <= check_in:
                st.error(
                    "Ngày check-out phải sau ngày check-in."
                )

            else:

                customer_row = customers[
                    customers["Full Name"]
                    == selected_customer
                ].iloc[0]

                room_row = rooms[
                    rooms["Room"]
                    == selected_room_booking
                ].iloc[0]

                nights = (
                    check_out - check_in
                ).days

                new_booking = pd.DataFrame(
                    [[
                        new_booking_id,
                        customer_row["Customer ID"],
                        selected_customer,
                        selected_room_booking,
                        room_row["Room Type"],
                        check_in,
                        check_out,
                        nights,
                        room_row["Price"],
                        "Reserved"
                    ]],
                    columns=BOOKING_COLUMNS
                )

                st.session_state.bookings = pd.concat(
                    [
                        st.session_state.bookings,
                        new_booking
                    ],
                    ignore_index=True
                )

                idx = st.session_state.rooms.index[
                    st.session_state.rooms["Room"]
                    == selected_room_booking
                ]

                st.session_state.rooms.loc[
                    idx,
                    "Status"
                ] = "Reserved"

                st.success(
                    "Đã tạo booking thành công!"
                )

                st.rerun()


# ============================================================
# HOUSEKEEPING
# ============================================================

elif menu == "🧹 Housekeeping":

    st.markdown(
        '<div class="section-title">🧹 Housekeeping</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Tổng phòng",
            len(housekeeping)
        )

    with col2:
        completed = len(
            housekeeping[
                housekeeping["Cleaning Status"]
                == "Completed"
            ]
        )

        st.metric(
            "Đã hoàn thành",
            completed
        )

    with col3:
        pending = len(
            housekeeping[
                housekeeping["Cleaning Status"]
                != "Completed"
            ]
        )

        st.metric(
            "Cần xử lý",
            pending
        )

    st.markdown("---")

    st.dataframe(
        housekeeping,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.markdown("### 🧹 Cập nhật tình trạng vệ sinh")

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
            "Nhân viên",
            "Lan"
        )

    if st.button(
        "💾 Cập nhật Housekeeping",
        use_container_width=True
    ):

        idx = housekeeping.index[
            housekeeping["Room"] == hk_room
        ]

        st.session_state.housekeeping.loc[
            idx,
            "Cleaning Status"
        ] = hk_status

        st.session_state.housekeeping.loc[
            idx,
            "Assigned Staff"
        ] = hk_staff

        st.success(
            f"Đã cập nhật Housekeeping phòng {hk_room}"
        )

        st.rerun()


# ============================================================
# DOANH THU
# ============================================================

elif menu == "💰 Doanh thu":

    st.markdown(
        '<div class="section-title">💰 Quản lý doanh thu</div>',
        unsafe_allow_html=True
    )

    revenue_df = bookings.copy()

    revenue_df["Revenue"] = (
        revenue_df["Nights"]
        * revenue_df["Price/Night"]
    )

    total_revenue = revenue_df["Revenue"].sum()

    average_booking = revenue_df["Revenue"].mean()

    total_nights = revenue_df["Nights"].sum()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "💰 Tổng doanh thu",
            f"{total_revenue:,.0f} VNĐ"
        )

    with col2:
        st.metric(
            "📅 Tổng số đêm",
            f"{total_nights} đêm"
        )

    with col3:
        st.metric(
            "🧾 Doanh thu TB/booking",
            f"{average_booking:,.0f} VNĐ"
        )

    st.markdown("---")

    st.markdown("### 📊 Doanh thu theo loại phòng")

    revenue_by_type = (
        revenue_df
        .groupby("Room Type")["Revenue"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        revenue_by_type,
        x="Room Type",
        y="Revenue",
        text_auto=".2s",
        title="Doanh thu theo loại phòng"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown("### 📋 Chi tiết doanh thu")

    display_revenue = revenue_df[
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
    ].apply(lambda x: f"{x:,.0f} VNĐ")

    st.dataframe(
        display_revenue,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "🏨 Hotel Management System | "
    "Demo application built with Streamlit"
)
