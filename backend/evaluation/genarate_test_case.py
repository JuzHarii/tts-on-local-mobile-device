import random
import os

# 1. Nhóm câu dài về Khoa học & Công nghệ (Academic/Technical)
tech_long = [
    "Sự kết hợp giữa trí tuệ nhân tạo và điện toán đám mây đã tạo ra một cuộc cách mạng trong việc xử lý dữ liệu lớn, giúp các doanh nghiệp tối ưu hóa quy trình vận hành và cắt giảm chi phí một cách đáng kể.",
    "Trong bối cảnh biến đổi khí hậu đang diễn ra ngày càng phức tạp, việc phát triển các nguồn năng lượng tái tạo như điện mặt trời và điện gió không chỉ là xu hướng mà còn là yêu cầu cấp thiết để bảo vệ môi trường xanh.",
    "Các nhà khoa học tại viện nghiên cứu công nghệ vừa công bố một đột phá mới trong lĩnh vực vật liệu bán dẫn, mở ra cơ hội sản xuất các loại chip máy tính có tốc độ xử lý nhanh gấp hàng trăm lần so với hiện nay.",
    "Mạng di động thế hệ thứ năm không chỉ đơn thuần là sự nâng cấp về tốc độ truyền tải mà còn là nền tảng quan trọng cho hệ sinh thái vạn vật kết nối và các hệ thống điều khiển giao thông thông minh trong tương lai.",
    "Việc tích hợp các mô hình ngôn ngữ lớn vào hệ thống trợ lý ảo đã giúp cho giao tiếp giữa người và máy trở nên tự nhiên hơn, xóa bỏ rào cản về mặt ngôn ngữ và nâng cao trải nghiệm người dùng trên toàn cầu."
]

# 2. Nhóm câu dài về Kinh tế & Xã hội (News/Economics)
news_long = [
    "Theo báo cáo mới nhất từ Tổng cục Thống kê, nền kinh tế Việt Nam đang có những dấu hiệu phục hồi tích cực với chỉ số sản xuất công nghiệp tăng trưởng ổn định bất chấp những biến động không ngừng của thị trường tài chính quốc tế.",
    "Chính phủ vừa ban hành nghị định mới nhằm khuyến khích các startup khởi nghiệp trong lĩnh vực công nghệ xanh, đồng thời tháo gỡ những khó khăn về mặt pháp lý để thu hút thêm nguồn vốn đầu tư trực tiếp từ nước ngoài.",
    "Tại hội nghị thượng đỉnh về phát triển bền vững, các nhà lãnh đạo đã thảo luận về việc thiết lập một khung pháp lý chung cho việc quản lý rác thải nhựa đại dương và bảo tồn đa dạng sinh học tại các vùng biển nhiệt đới.",
    "Việc mở rộng các tuyến đường cao tốc Bắc Nam không chỉ rút ngắn thời gian di chuyển giữa các tỉnh thành mà còn thúc đẩy giao thương hàng hóa, tạo động lực mạnh mẽ cho sự phát triển kinh tế của các vùng sâu vùng xa.",
    "Sự thay đổi trong hành vi tiêu dùng của giới trẻ đang thúc đẩy các nền tảng thương mại điện tử phải liên tục đổi mới, từ việc cá nhân hóa giao diện người dùng đến việc tích hợp các phương thức thanh toán không tiền mặt hiện đại."
]

# 3. Nhóm câu dài có cấu trúc phức tạp (Số liệu, ngày tháng, tên riêng)
complex_struct = [
    "Vào ngày {d} tháng {m} năm {y}, dự án có tổng mức đầu tư lên đến {p} tỷ đồng đã chính thức được khởi công tại khu kinh tế trọng điểm với sự tham gia của hơn {s} chuyên gia hàng đầu đến từ nhiều quốc gia.",
    "Theo kết quả khảo sát tại số {s} đường Lê Văn Sỹ, quận Tân Bình, có tới {s} phần trăm người dân ủng hộ việc chuyển đổi sang sử dụng xe buýt điện để giảm thiểu ô nhiễm tiếng ồn và khí thải trong khu vực nội đô.",
    "Số điện thoại tổng đài hỗ trợ kỹ thuật 09{n} sẽ trực tuyến liên tục hai mươi tư trên bảy để tiếp nhận và xử lý mọi phản ánh của khách hàng về tình trạng gián đoạn dịch vụ internet trong điều kiện thời tiết khắc nghiệt.",
    "Chuyến bay mã hiệu VN-{p} dự kiến sẽ hạ cánh lúc {h} giờ {m} phút sáng mai, tuy nhiên hành khách cần lưu ý theo dõi bảng điện tử để cập nhật thông tin mới nhất nếu có sự thay đổi do ảnh hưởng của áp thấp nhiệt đới.",
]

test_cases = []

while len(test_cases) < 1000:
    choice = random.random()
    if choice < 0.35:
        s = random.choice(tech_long)
    elif choice < 0.70:
        s = random.choice(news_long)
    else:
        p = random.choice(complex_struct)
        s = p.format(
            d=random.randint(1, 31), m=random.randint(1, 12), y=random.randint(2024, 2030),
            n=random.randint(1000000, 9999999), s=random.randint(10, 99),
            p=random.randint(100, 999), h=random.randint(0, 23)
        )
    
    # Thêm một chút biến tấu để các câu không bị lặp lại hoàn toàn
    suffix = [" ", " thực sự là một bài toán khó.", " mang lại nhiều suy ngẫm.", " cần được xem xét kỹ lưỡng.", " trong giai đoạn hiện nay."]
    if s not in test_cases:
        test_cases.append(s + random.choice(suffix))

# Ghi file
file_path = "evaluation/test_case.txt"
os.makedirs("evaluation", exist_ok=True)
with open(file_path, "w", encoding="utf-8") as f:
    for line in test_cases[:1000]:
        f.write(line.strip() + "\n")

print(f"Hoàn thành tạo 1000 câu dài tại {file_path}")