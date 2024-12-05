from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv
import os

# Load API Key từ file .env
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://172.16.102.51:5000"}})
socketio = SocketIO(app, cors_allowed_origins="http://172.16.102.51:5000", async_mode="threading")

# Lưu trữ trạng thái đặt phòng cho từng người dùng
user_booking = {}

# Route chính để render giao diện
@app.route("/")
def index():
    return render_template("index.html")

# Xử lý tin nhắn từ người dùng
@socketio.on("send_message")
def handle_message(data):
    user_message = data["message"].lower()
    user_id = request.sid  # ID duy nhất cho từng kết nối người dùng

    # Khởi tạo trạng thái đặt phòng cho người dùng nếu chưa tồn tại
    if user_id not in user_booking:
        user_booking[user_id] = {
            "location": None,
            "room_type": None,
            "booking_time": None,
        }

    booking_state = user_booking[user_id]

    # Xử lý các tin nhắn từ nút gợi ý
    if user_message in ["đặt phòng", "ưu đãi", "dịch vụ", "thời tiết"]:
        if user_message == "đặt phòng":
            response = "Bạn muốn đặt phòng ở đâu? Ví dụ: Hà Nội, Đà Nẵng."
        elif user_message == "ưu đãi":
            response = (
                "Hiện tại chúng tôi có khuyến mãi:\n"
                "- Giảm giá 20% cho phòng đôi tại Hà Nội từ 9-15/12/2024.\n"
                "Bạn có muốn đặt ngay không?"
            )
        elif user_message == "dịch vụ":
            response = (
                "Các dịch vụ đi kèm:\n"
                "- Xe đưa đón sân bay (200,000 VND)\n"
                "- Thuê xe máy (150,000 VND/ngày).\n"
                "Bạn muốn sử dụng dịch vụ nào?"
            )
        elif user_message == "thời tiết":
            response = (
                "Dự báo thời tiết ngày mai tại Hồ Chí Minh: Nắng, nhiệt độ từ 28-34°C.\n"
                "Bạn có muốn đặt phòng ở đây không?"
            )

    # Xử lý các bước đặt phòng
    elif "chào" in user_message or "hello" in user_message:
        response = "Chào bạn! Tôi có thể giúp gì cho bạn hôm nay?"

    elif booking_state["location"] is None:
        booking_state["location"] = user_message
        response = "Bạn muốn đặt loại phòng nào (ví dụ: đơn, đôi, hoặc gia đình)?"

    elif booking_state["room_type"] is None:
        booking_state["room_type"] = user_message
        response = "Bạn muốn đặt vào ngày nào và mấy giờ?"

    elif booking_state["booking_time"] is None:
        try:
            booking_time = datetime.strptime(user_message, "%d/%m/%Y %H:%M")
            if booking_time > datetime.now():
                booking_state["booking_time"] = booking_time
                response = (
                    "Đặt phòng thành công! Thông tin chi tiết:\n"
                    f"- Địa điểm: {booking_state['location']}\n"
                    f"- Loại phòng: {booking_state['room_type']}\n"
                    f"- Thời gian: {booking_state['booking_time'].strftime('%d/%m/%Y %H:%M')}"
                )
            else:
                response = "Ngày đặt phòng không hợp lệ. Vui lòng chọn ngày trong tương lai."
        except ValueError:
            response = "Vui lòng nhập ngày và giờ theo định dạng: dd/mm/yyyy hh:mm."

    # Tính năng: Gợi ý địa điểm du lịch
    elif "địa điểm" in user_message or "du lịch" in user_message:
        response = (
            "Gợi ý địa điểm nổi bật: \n"
            "- Nhà thờ Đức Bà\n"
            "- Dinh Độc Lập\n"
            "- Phố đi bộ Nguyễn Huệ\n"
            "Bạn có muốn biết thêm nhà hàng nổi tiếng không?"
        )

    # Tính năng: Hủy đặt phòng
    elif "hủy" in user_message or "cancel" in user_message:
        user_booking[user_id] = {
            "location": None,
            "room_type": None,
            "booking_time": None,
        }
        response = "Đặt phòng của bạn đã được hủy. Nếu cần hỗ trợ thêm, hãy cho tôi biết!"

    # Tính năng: Đánh giá dịch vụ
    elif "đánh giá" in user_message or "feedback" in user_message:
        response = (
            "Cảm ơn bạn đã sử dụng dịch vụ của chúng tôi!\n"
            "Bạn có thể đánh giá trải nghiệm (1-5 sao)."
        )

    # Xử lý yêu cầu không xác định
    else:
        response = (
            "Tôi chưa hiểu yêu cầu của bạn. Bạn có thể thử các lựa chọn sau:\n"
            "- Nhập 'đặt phòng' để bắt đầu đặt phòng.\n"
            "- Nhập 'ưu đãi' để xem khuyến mãi.\n"
            "- Nhập 'dịch vụ' để xem các dịch vụ đi kèm.\n"
            "- Nhập 'thời tiết' để cập nhật thời tiết."
        )

    # Gửi phản hồi lại cho người dùng
    emit("receive_message", {"message": response}, room=user_id)

# Chạy ứng dụng
if __name__ == "__main__":
    socketio.run(app, host="172.16.102.51", port=5000)
