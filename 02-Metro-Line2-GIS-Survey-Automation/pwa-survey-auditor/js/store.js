// Store & Persistence Manager for FormsMobile (Supabase Cloud + LocalStorage Fallback)

const STORAGE_KEYS = {
  SURVEYS: 'formsmobile_surveys_v1',
  RESPONSES: 'formsmobile_responses_v1',
  SUPABASE_CONFIG: 'formsmobile_supabase_cfg'
};

// Default Pre-configured Supabase Project for User
const DEFAULT_SUPABASE_CONFIG = {
  url: 'https://vfuajeepjklrugpijcbc.supabase.co',
  key: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZmdWFqZWVwamtscnVncGlqY2JjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODUyMTExMTEsImV4cCI6MjEwMDc4NzExMX0.54u0m2FQBmeffWRG4PUVQugdvPc94gTOXBU2RxBdSsA'
};

// Initial Sample Surveys
const INITIAL_SURVEYS = [
  {
    id: 'survey-household-travel',
    title: 'Khảo sát Hộ Gia Đình & Nhu Cầu Di Chuyển Giao Thông',
    description: 'Bảng khảo sát thông tin hộ gia đình, phương tiện sở hữu và nhật ký chuyến đi hàng ngày (File Hộ Gia Đình).',
    themeColor: 'purple',
    isPublished: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    questions: [
      {
        id: 'q_ksv_name',
        title: 'Họ và Tên Người trả lời / KSV',
        type: 'text_short',
        required: true,
        placeholder: 'Nhập họ và tên'
      },
      {
        id: 'q_ksv_code',
        title: 'Mã số KSV / Mã điều tra viên',
        type: 'text_short',
        required: false,
        placeholder: 'Nhập mã số KSV'
      },
      {
        id: 'q_age',
        title: 'Tuổi của Anh/Chị:',
        type: 'single_choice',
        required: true,
        options: ['Dưới 18 tuổi', '18 đến 22 tuổi', '23 đến 35 tuổi', '36 đến 50 tuổi', '51 đến 65 tuổi', 'Trên 65 tuổi']
      },
      {
        id: 'q_gender',
        title: 'Giới tính:',
        type: 'single_choice',
        required: true,
        options: ['Nam', 'Nữ', 'Khác']
      },
      {
        id: 'q_job',
        title: 'Nghề nghiệp của Anh/Chị?',
        type: 'single_choice',
        required: true,
        options: [
          'Học sinh, sinh viên',
          'Nhân viên văn phòng, giáo viên',
          'Chủ tiệm, nhà hàng, khách sạn',
          'Công nhân, thợ thủ công',
          'Nghỉ hưu, nội trợ, giúp việc',
          'Lái xe',
          'Quản lý',
          'Khác'
        ]
      },
      {
        id: 'q_license',
        title: 'Anh/Chị sở hữu bằng lái xe dành cho:',
        type: 'single_choice',
        required: true,
        options: ['Không có bằng lái', 'Xe máy', 'Ô tô', 'Cả hai']
      },
      {
        id: 'q_vehicles_owned',
        title: 'Anh/Chị sở hữu phương tiện nào?',
        type: 'multiple_choice',
        required: true,
        options: ['Xe máy', 'Ô tô', 'Xe đạp', 'Xe đạp điện', 'Không có']
      },
      {
        id: 'q_income',
        title: 'Thu nhập 1 tháng của Anh/Chị:',
        type: 'single_choice',
        required: true,
        options: [
          'Dưới 1 triệu',
          'Từ 1.1-3 triệu',
          'Từ 3.1-6 triệu',
          'Từ 6.1-10 triệu',
          'Từ 10.1-15 triệu',
          'Từ 15.1 – 30 triệu',
          'Từ 30.1-50 triệu',
          'Trên 50 triệu'
        ]
      },
      {
        id: 'q_daily_vehicle',
        title: 'Phương tiện sử dụng hàng ngày của Anh/Chị:',
        type: 'single_choice',
        required: true,
        options: ['Xe máy', 'Ô tô', 'Xe buýt', 'Đi bộ', 'Xe đạp']
      },
      {
        id: 'q_home_address',
        title: 'Địa chỉ nơi ở (Quận, Phường, Tên đường, Số nhà):',
        type: 'text_short',
        required: true,
        placeholder: 'Ví dụ: Võ Oanh, Phường 25, Quận Bình Thạnh'
      },
      {
        id: 'q_work_address',
        title: 'Địa chỉ nơi làm việc / trường học:',
        type: 'text_short',
        required: false,
        placeholder: 'Ví dụ: ĐH Giao Thông Vận Tải, Đường Võ Oanh, Phường 25'
      },
      {
        id: 'q_frequent_address',
        title: 'Địa chỉ hay đến (Vui chơi / Chợ / Siêu thị):',
        type: 'text_short',
        required: false,
        placeholder: 'Ví dụ: Siêu thị Bách Hóa Xanh, Phường 25, Bình Thạnh'
      },
      {
        id: 'q_trip_count',
        title: 'Anh/Chị đã thực hiện bao nhiêu chuyến đi trong ngày hôm qua?',
        type: 'single_choice',
        required: true,
        options: ['1 chuyến', '2 chuyến', '3 chuyến', '4 chuyến', '5 chuyến', 'Trên 5 chuyến']
      },
      {
        id: 'q_trip_details',
        title: 'Nhật ký thông tin các chuyến đi (Nơi đi, Nơi đến, Loại chuyến đi, Phương tiện, Thời gian, Khoảng cách):',
        type: 'text_long',
        required: false,
        placeholder: 'Ví dụ: Chuyến 1: Từ nhà đến chỗ học (Xe máy, 10 phút, 1 km)...'
      },
      {
        id: 'q_future_transport',
        title: 'Anh/Chị có ý định chuyển đổi sang loại hình phương tiện nào khác sau khi các loại hình giao thông thuận tiện hơn?',
        type: 'single_choice',
        required: true,
        options: ['Metro', 'Xe buýt', 'Xe ô tô', 'Xe máy', 'Xe đạp']
      }
    ]
  },
  {
    id: 'survey-sample-1',
    title: 'Đăng ký nhận thông tin chương trình MBA/MHA',
    description: 'Hệ thống sẽ tự động gửi email thông tin tuyển sinh khi có thông báo tuyển sinh mới.',
    themeColor: 'purple',
    isPublished: true,
    createdAt: new Date(Date.now() - 86400000 * 3).toISOString(),
    updatedAt: new Date(Date.now() - 86400000 * 1).toISOString(),
    questions: [
      {
        id: 'q1',
        title: 'Họ và Tên',
        type: 'text_short',
        required: true,
        placeholder: 'Câu trả lời của bạn'
      },
      {
        id: 'q2',
        title: 'Địa chỉ email',
        type: 'text_short',
        required: true,
        placeholder: 'Câu trả lời của bạn'
      },
      {
        id: 'q3',
        title: 'Số điện thoại liên lạc',
        type: 'text_short',
        required: true,
        placeholder: 'Câu trả lời của bạn'
      }
    ]
  },
  {
    id: 'survey-ptcc-6a',
    title: 'Nhiệm vụ 6a – Phiếu Phỏng Vấn Hành Khách PTCC',
    description: 'Khảo sát hành khách sử dụng phương tiện công cộng (xe buýt) tại TP.HCM. Thu thập dữ liệu OD, đánh giá dịch vụ và khả năng chuyển đổi sang Metro.',
    themeColor: 'purple', isPublished: true,
    createdAt: new Date().toISOString(), updatedAt: new Date().toISOString(),
    questions: [
      // ===== A: THÔNG TIN KHẢO SÁT =====
      { id: 'q6a_ma_ks', title: 'Mã khảo sát', type: 'text_short', required: true, placeholder: 'VD: HK-001' },
      { id: 'q6a_ma_dtv', title: 'Mã điều tra viên', type: 'text_short', required: true, placeholder: 'VD: DTV-01' },
      { id: 'q6a_ma_diem', title: 'Mã điểm lấy mẫu / điểm dừng', type: 'text_short', required: true, placeholder: 'VD: DD-BinhThanh-01' },
      { id: 'q6a_ngay', title: 'Ngày khảo sát', type: 'date', required: true },
      { id: 'q6a_loai_ngay', title: 'Loại ngày', type: 'single_choice', required: true, options: ['Ngày thường', 'Thứ Bảy', 'Chủ nhật / Ngày lễ'] },
      { id: 'q6a_tuyen', title: 'Tuyến xe buýt', type: 'text_short', required: true, placeholder: 'VD: Tuyến 01, 19, 53...' },
      { id: 'q6a_huong', title: 'Hướng tuyến', type: 'text_short', required: true, placeholder: 'VD: Bến Thành → Chợ Lớn' },
      { id: 'q6a_gio_pv', title: 'Giờ phỏng vấn', type: 'time', required: true },
      // ===== B: THÔNG TIN CHUYẾN ĐI =====

      { id: 'q6a_diem_di', title: 'Điểm đi thực tế (địa chỉ / phường / quận)', type: 'text_long', required: true, placeholder: 'VD: 268 Lý Thường Kiệt, P.14, Q.10' },
      { id: 'q6a_diem_den', title: 'Điểm đến thực tế (địa chỉ / phường / quận)', type: 'text_long', required: true, placeholder: 'VD: ĐH Bách Khoa, Dĩ An, Bình Dương' },
      { id: 'q6a_muc_dich', title: 'Mục đích chuyến đi', type: 'single_choice', required: true, options: ['Đi làm', 'Đi học', 'Công việc', 'Mua sắm', 'Đưa/đón người', 'Giải trí / ăn uống', 'Khám chữa bệnh', 'Về nhà', 'Khác'] },
      { id: 'q6a_gio_kh', title: 'Thời gian khởi hành toàn hành trình', type: 'time', required: true },
      { id: 'q6a_tong_tg', title: 'Tổng thời gian toàn hành trình (phút)', type: 'text_short', required: true, placeholder: 'VD: 45' },
      // ===== C: CHUỖI CHẶNG PTCC =====

      { id: 'q6a_pt_tiep_can', title: 'Phương thức tiếp cận điểm dừng PTCC đầu tiên', type: 'single_choice', required: true, options: ['Đi bộ', 'Xe máy', 'Xe đạp', 'Xe buýt khác', 'Taxi / Grab', 'Xe ôm', 'Khác'] },
      { id: 'q6a_tg_tiep_can', title: 'Thời gian tiếp cận điểm dừng (phút)', type: 'text_short', required: true, placeholder: 'VD: 10' },
      { id: 'q6a_tg_cho', title: 'Thời gian chờ xe buýt ban đầu (phút)', type: 'text_short', required: true, placeholder: 'VD: 8' },
      { id: 'q6a_so_chang', title: 'Số chặng PTCC trong chuyến đi', type: 'single_choice', required: true, options: ['1 chặng', '2 chặng', '3 chặng', 'Trên 3 chặng'] },
      { id: 'q6a_tong_ve', title: 'Tổng chi phí vé PTCC (VND)', type: 'text_short', required: true, placeholder: 'VD: 7000' },
      // ===== D: KHẢ NĂNG SỬ DỤNG PT KHÁC =====

      { id: 'q6a_pt_khac', title: 'Phương thức có thể sử dụng cho chuyến đi này', type: 'multiple_choice', required: true, options: ['Ô tô', 'Xe máy', 'Xe buýt', 'Metro (nếu có)', 'Taxi / Grab ô tô', 'Xe ôm / xe máy công nghệ', 'Xe đạp', 'Đi bộ'] },
      { id: 'q6a_co_oto', title: 'Có ô tô để sử dụng?', type: 'single_choice', required: true, options: ['Có', 'Không'] },
      { id: 'q6a_co_xemay', title: 'Có xe máy để sử dụng?', type: 'single_choice', required: true, options: ['Có', 'Không'] },
      { id: 'q6a_co_vethang', title: 'Có vé tháng / thẻ PTCC?', type: 'single_choice', required: true, options: ['Có', 'Không'] },
      // ===== E: ĐÁNH GIÁ DỊCH VỤ =====

      { id: 'q6a_danh_gia', title: 'Đánh giá dịch vụ PTCC hiện tại', type: 'grid_single', required: true, rows: ['Thời gian đi lại toàn hành trình', 'Độ tin cậy / đúng giờ', 'Thời gian chờ', 'Mức độ thoải mái', 'Mức độ đông đúc', 'An toàn / an ninh', 'Khả năng tiếp cận trạm dừng', 'Thông tin hành khách', 'Chi phí vé', 'Đánh giá tổng thể'], columns: ['1 ⭐', '2 ⭐', '3 ⭐', '4 ⭐', '5 ⭐'] },
      // ===== F: THÓI QUEN & NGƯỠNG CHẤP NHẬN =====

      { id: 'q6a_tan_suat', title: 'Tần suất sử dụng PTCC', type: 'single_choice', required: true, options: ['Lần đầu / hiếm khi', 'Vài lần / năm', 'Vài lần / tháng', 'Vài lần / tuần', 'Hằng ngày'] },
      { id: 'q6a_tg_dibo', title: 'Thời gian đi bộ chấp nhận được đến trạm dừng', type: 'single_choice', required: true, options: ['≤ 3 phút', '4–5 phút', '6–10 phút', '11–15 phút', '> 15 phút'] },
      { id: 'q6a_tg_cho_cn', title: 'Thời gian chờ / giãn cách chuyến chấp nhận được', type: 'single_choice', required: true, options: ['≤ 5 phút', '6–10 phút', '11–15 phút', '16–20 phút', '21–30 phút', '> 30 phút'] },
      { id: 'q6a_so_chuyen_tuyen', title: 'Số lần chuyển tuyến chấp nhận được', type: 'single_choice', required: true, options: ['0 lần', '1 lần', '2 lần', '≥ 3 lần'] },
      { id: 'q6a_thanh_toan', title: 'Hình thức thanh toán ưu tiên', type: 'multiple_choice', required: true, options: ['Tiền mặt', 'Thẻ PTCC', 'QR / điện thoại', 'Thẻ ngân hàng', 'Vé do cơ quan cấp', 'Khác'] },
      // ===== G: KHẢO SÁT METRO =====

      { id: 'q6a_pt_hien_tai', title: 'Phương tiện hiện tại bạn đang sử dụng', type: 'text_short', required: true, placeholder: 'VD: Xe buýt, Xe máy...' },
      { id: 'q6a_tg_hien_tai', title: 'Thời gian đi lại hiện tại (phút)', type: 'text_short', required: true, placeholder: 'VD: 45' },
      { id: 'q6a_cp_hien_tai', title: 'Chi phí đi lại hiện tại (VND)', type: 'text_short', required: true, placeholder: 'VD: 7000' },
      { id: 'q6a_sp1', title: 'KB1: Metro thời gian TĂNG 15 phút, vé 9.000đ — Chuyển sang Metro?', type: 'single_choice', required: true, options: ['Có', 'Không'] },
      { id: 'q6a_sp2', title: 'KB2: Metro thời gian GIẢM 5 phút, vé 12.000đ — Chuyển sang Metro?', type: 'single_choice', required: true, options: ['Có', 'Không'] },
      { id: 'q6a_sp3', title: 'KB3: Metro thời gian NHƯ HIỆN TẠI, vé 14.000đ — Chuyển sang Metro?', type: 'single_choice', required: true, options: ['Có', 'Không'] },
      { id: 'q6a_sp4', title: 'KB4: Metro thời gian GIẢM 10 phút, vé 18.000đ — Chuyển sang Metro?', type: 'single_choice', required: true, options: ['Có', 'Không'] },
      { id: 'q6a_sp5', title: 'KB5: Metro thời gian GIẢM 15 phút, vé 25.000đ — Chuyển sang Metro?', type: 'single_choice', required: true, options: ['Có', 'Không'] },
      // ===== H: THÔNG TIN KINH TẾ XÃ HỘI =====

      { id: 'q6a_tuoi', title: 'Tuổi', type: 'single_choice', required: true, options: ['Dưới 18', '18–22', '23–35', '36–50', '51–65', 'Trên 65'] },
      { id: 'q6a_gioi_tinh', title: 'Giới tính', type: 'single_choice', required: true, options: ['Nam', 'Nữ', 'Khác / không trả lời'] },
      { id: 'q6a_nghe_nghiep', title: 'Nghề nghiệp', type: 'single_choice', required: true, options: ['Quản lý', 'Văn phòng / giáo viên', 'Công nhân', 'Kinh doanh', 'Lái xe', 'Dịch vụ', 'Học sinh / Sinh viên', 'Nội trợ / hưu trí', 'Khác'] },
      { id: 'q6a_thu_nhap', title: 'Thu nhập cá nhân / tháng', type: 'single_choice', required: true, options: ['Dưới 3 triệu', '3–6 triệu', '6–10 triệu', '10–15 triệu', '15–30 triệu', '30–50 triệu', 'Trên 50 triệu', 'Không trả lời'] },
      { id: 'q6a_bang_lai', title: 'Giấy phép lái xe', type: 'single_choice', required: true, options: ['Xe máy', 'Ô tô', 'Cả hai', 'Không có'] },
      { id: 'q6a_noi_o', title: 'Nơi ở (địa chỉ / phường / quận)', type: 'text_short', required: true, placeholder: 'VD: P.25, Q.Bình Thạnh' },
      { id: 'q6a_noi_lv', title: 'Nơi làm việc / học tập', type: 'text_short', required: true, placeholder: 'VD: KCN Tân Bình, Q.Tân Phú' },
      { id: 'q6a_quy_mo_ho', title: 'Quy mô hộ (số người trong gia đình)', type: 'text_short', required: true, placeholder: 'VD: 4' },
      { id: 'q6a_pt_ho', title: 'Phương tiện của hộ (ô tô, xe máy, xe đạp)', type: 'text_short', required: true, placeholder: 'VD: 2 xe máy, 1 xe đạp' },
      { id: 'q6a_cho_do', title: 'Chỗ đỗ ô tô tại nơi ở', type: 'single_choice', required: true, options: ['Có', 'Không', 'Không áp dụng'] }
    ]
  }
];

// Initial Sample Responses for Demo
const INITIAL_RESPONSES = [
  {
    id: 'resp-demo-1',
    surveyId: 'survey-household-travel',
    submittedAt: new Date(Date.now() - 3600000 * 4).toISOString(),
    answers: {
      'q_ksv_name': 'Nguyễn Văn Anh',
      'q_ksv_code': 'KSV-001',
      'q_age': '23 đến 35 tuổi',
      'q_gender': 'Nam',
      'q_job': 'Nhân viên văn phòng, giáo viên',
      'q_license': 'Xe máy',
      'q_vehicles_owned': ['Xe máy'],
      'q_income': 'Từ 6.1-10 triệu',
      'q_daily_vehicle': 'Xe máy',
      'q_home_address': 'Võ Oanh, Phường 25, Quận Bình Thạnh',
      'q_work_address': 'ĐH Giao Thông Vận Tải TP.HCM',
      'q_frequent_address': 'Siêu thị Bách Hóa Xanh, Phường 25',
      'q_trip_count': '2 chuyến',
      'q_trip_details': 'Chuyến 1: Từ nhà đến trường (Xe máy, 15 phút, 3 km). Chuyến 2: Từ trường về nhà.',
      'q_future_transport': 'Metro'
    }
  },
  {
    id: 'resp-demo-2',
    surveyId: 'survey-household-travel',
    submittedAt: new Date(Date.now() - 3600000 * 10).toISOString(),
    answers: {
      'q_ksv_name': 'Trần Thị Bình',
      'q_ksv_code': 'KSV-002',
      'q_age': '18 đến 22 tuổi',
      'q_gender': 'Nữ',
      'q_job': 'Học sinh, sinh viên',
      'q_license': 'Không có bằng lái',
      'q_vehicles_owned': ['Xe đạp điện'],
      'q_income': 'Dưới 1 triệu',
      'q_daily_vehicle': 'Xe buýt',
      'q_home_address': 'Nguyễn Oanh, Phường 17, Quận Gò Vấp',
      'q_work_address': 'ĐH Giao Thông Vận Tải TP.HCM',
      'q_frequent_address': 'Lotte Mart Gò Vấp',
      'q_trip_count': '3 chuyến',
      'q_trip_details': 'Chuyến 1: Từ nhà đến trường. Chuyến 2: Từ trường đến Lotte Mart. Chuyến 3: Về nhà.',
      'q_future_transport': 'Xe buýt'
    }
  },
  {
    id: 'resp-6a-demo-1',
    surveyId: 'survey-ptcc-6a',
    submittedAt: new Date(Date.now() - 3600000 * 2).toISOString(),
    answers: {
      'q6a_ma_ks': 'HK-001', 'q6a_ma_dtv': 'DTV-01', 'q6a_ma_diem': 'DD-Q1-01',
      'q6a_ngay': '2026-08-22', 'q6a_loai_ngay': 'Ngày thường',
      'q6a_tuyen': 'Tuyến 01', 'q6a_huong': 'Bến Thành → Chợ Lớn', 'q6a_gio_pv': '07:30',
      'q6a_diem_di': '268 Lý Thường Kiệt, P.14, Q.10', 'q6a_diem_den': 'Chợ Bình Tây, Q.6',
      'q6a_muc_dich': 'Đi làm', 'q6a_gio_kh': '07:00', 'q6a_tong_tg': '45',
      'q6a_pt_tiep_can': 'Đi bộ', 'q6a_tg_tiep_can': '8', 'q6a_tg_cho': '10',
      'q6a_so_chang': '1 chặng', 'q6a_tong_ve': '7000',
      'q6a_pt_khac': ['Xe máy', 'Xe buýt'], 'q6a_co_oto': 'Không', 'q6a_co_xemay': 'Có', 'q6a_co_vethang': 'Có',
      'q6a_danh_gia': { 'Thời gian đi lại toàn hành trình': '3 ⭐', 'Độ tin cậy / đúng giờ': '2 ⭐', 'Thời gian chờ': '2 ⭐', 'Mức độ thoải mái': '3 ⭐', 'Mức độ đông đúc': '2 ⭐', 'An toàn / an ninh': '4 ⭐', 'Khả năng tiếp cận trạm dừng': '3 ⭐', 'Thông tin hành khách': '3 ⭐', 'Chi phí vé': '4 ⭐', 'Đánh giá tổng thể': '3 ⭐' },
      'q6a_tan_suat': 'Hằng ngày', 'q6a_tg_dibo': '6–10 phút', 'q6a_tg_cho_cn': '11–15 phút',
      'q6a_so_chuyen_tuyen': '1 lần', 'q6a_thanh_toan': ['Tiền mặt', 'Thẻ PTCC'],
      'q6a_pt_hien_tai': 'Xe buýt', 'q6a_tg_hien_tai': '45', 'q6a_cp_hien_tai': '7000',
      'q6a_sp1': 'Không', 'q6a_sp2': 'Có', 'q6a_sp3': 'Có', 'q6a_sp4': 'Có', 'q6a_sp5': 'Không',
      'q6a_tuoi': '23–35', 'q6a_gioi_tinh': 'Nam', 'q6a_nghe_nghiep': 'Văn phòng / giáo viên',
      'q6a_thu_nhap': '6–10 triệu', 'q6a_bang_lai': 'Xe máy',
      'q6a_noi_o': 'P.14, Q.10', 'q6a_noi_lv': 'Chợ Bình Tây, Q.6',
      'q6a_quy_mo_ho': '4', 'q6a_pt_ho': '2 xe máy', 'q6a_cho_do': 'Không áp dụng'
    }
  },
  {
    id: 'resp-6a-demo-2',
    surveyId: 'survey-ptcc-6a',
    submittedAt: new Date(Date.now() - 3600000 * 4).toISOString(),
    answers: {
      'q6a_ma_ks': 'HK-002', 'q6a_ma_dtv': 'DTV-01', 'q6a_ma_diem': 'DD-GV-03',
      'q6a_ngay': '2026-08-22', 'q6a_loai_ngay': 'Ngày thường',
      'q6a_tuyen': 'Tuyến 19', 'q6a_huong': 'Gò Vấp → Mỹ Tho', 'q6a_gio_pv': '08:15',
      'q6a_diem_di': 'Nguyễn Oanh, P.17, Q.Gò Vấp', 'q6a_diem_den': 'ĐH GTVT TP.HCM, Bình Thạnh',
      'q6a_muc_dich': 'Đi học', 'q6a_gio_kh': '07:30', 'q6a_tong_tg': '35',
      'q6a_pt_tiep_can': 'Đi bộ', 'q6a_tg_tiep_can': '5', 'q6a_tg_cho': '12',
      'q6a_so_chang': '1 chặng', 'q6a_tong_ve': '5000',
      'q6a_pt_khac': ['Xe đạp', 'Xe buýt'], 'q6a_co_oto': 'Không', 'q6a_co_xemay': 'Không', 'q6a_co_vethang': 'Có',
      'q6a_danh_gia': { 'Thời gian đi lại toàn hành trình': '3 ⭐', 'Độ tin cậy / đúng giờ': '3 ⭐', 'Thời gian chờ': '2 ⭐', 'Mức độ thoải mái': '3 ⭐', 'Mức độ đông đúc': '1 ⭐', 'An toàn / an ninh': '4 ⭐', 'Khả năng tiếp cận trạm dừng': '4 ⭐', 'Thông tin hành khách': '2 ⭐', 'Chi phí vé': '5 ⭐', 'Đánh giá tổng thể': '3 ⭐' },
      'q6a_tan_suat': 'Hằng ngày', 'q6a_tg_dibo': '4–5 phút', 'q6a_tg_cho_cn': '6–10 phút',
      'q6a_so_chuyen_tuyen': '0 lần', 'q6a_thanh_toan': ['Thẻ PTCC'],
      'q6a_pt_hien_tai': 'Xe buýt', 'q6a_tg_hien_tai': '35', 'q6a_cp_hien_tai': '5000',
      'q6a_sp1': 'Không', 'q6a_sp2': 'Có', 'q6a_sp3': 'Có', 'q6a_sp4': 'Có', 'q6a_sp5': 'Có',
      'q6a_tuoi': '18–22', 'q6a_gioi_tinh': 'Nữ', 'q6a_nghe_nghiep': 'Học sinh / Sinh viên',
      'q6a_thu_nhap': 'Dưới 3 triệu', 'q6a_bang_lai': 'Không có',
      'q6a_noi_o': 'P.17, Q.Gò Vấp', 'q6a_noi_lv': 'ĐH GTVT TP.HCM',
      'q6a_quy_mo_ho': '5', 'q6a_pt_ho': '3 xe máy, 1 xe đạp', 'q6a_cho_do': 'Không áp dụng'
    }
  },
  {
    id: 'resp-6a-demo-3',
    surveyId: 'survey-ptcc-6a',
    submittedAt: new Date(Date.now() - 3600000 * 6).toISOString(),
    answers: {
      'q6a_ma_ks': 'HK-003', 'q6a_ma_dtv': 'DTV-02', 'q6a_ma_diem': 'DD-BT-02',
      'q6a_ngay': '2026-08-22', 'q6a_loai_ngay': 'Ngày thường',
      'q6a_tuyen': 'Tuyến 53', 'q6a_huong': 'Bình Thạnh → Q.7', 'q6a_gio_pv': '09:00',
      'q6a_diem_di': 'Nguyễn Xí, P.26, Q.Bình Thạnh', 'q6a_diem_den': 'Lotte Mart Q.7',
      'q6a_muc_dich': 'Mua sắm', 'q6a_gio_kh': '08:30', 'q6a_tong_tg': '55',
      'q6a_pt_tiep_can': 'Xe máy', 'q6a_tg_tiep_can': '5', 'q6a_tg_cho': '15',
      'q6a_so_chang': '2 chặng', 'q6a_tong_ve': '14000',
      'q6a_pt_khac': ['Xe máy', 'Taxi / Grab ô tô'], 'q6a_co_oto': 'Không', 'q6a_co_xemay': 'Có', 'q6a_co_vethang': 'Không',
      'q6a_danh_gia': { 'Thời gian đi lại toàn hành trình': '2 ⭐', 'Độ tin cậy / đúng giờ': '2 ⭐', 'Thời gian chờ': '1 ⭐', 'Mức độ thoải mái': '2 ⭐', 'Mức độ đông đúc': '2 ⭐', 'An toàn / an ninh': '3 ⭐', 'Khả năng tiếp cận trạm dừng': '3 ⭐', 'Thông tin hành khách': '2 ⭐', 'Chi phí vé': '3 ⭐', 'Đánh giá tổng thể': '2 ⭐' },
      'q6a_tan_suat': 'Vài lần / tháng', 'q6a_tg_dibo': '≤ 3 phút', 'q6a_tg_cho_cn': '11–15 phút',
      'q6a_so_chuyen_tuyen': '1 lần', 'q6a_thanh_toan': ['Tiền mặt'],
      'q6a_pt_hien_tai': 'Xe buýt', 'q6a_tg_hien_tai': '55', 'q6a_cp_hien_tai': '14000',
      'q6a_sp1': 'Không', 'q6a_sp2': 'Không', 'q6a_sp3': 'Không', 'q6a_sp4': 'Có', 'q6a_sp5': 'Có',
      'q6a_tuoi': '51–65', 'q6a_gioi_tinh': 'Nữ', 'q6a_nghe_nghiep': 'Nội trợ / hưu trí',
      'q6a_thu_nhap': '3–6 triệu', 'q6a_bang_lai': 'Xe máy',
      'q6a_noi_o': 'P.26, Q.Bình Thạnh', 'q6a_noi_lv': 'Nội trợ tại nhà',
      'q6a_quy_mo_ho': '3', 'q6a_pt_ho': '1 xe máy', 'q6a_cho_do': 'Không'
    }
  },
  {
    id: 'resp-6a-demo-4',
    surveyId: 'survey-ptcc-6a',
    submittedAt: new Date(Date.now() - 3600000 * 8).toISOString(),
    answers: {
      'q6a_ma_ks': 'HK-004', 'q6a_ma_dtv': 'DTV-02', 'q6a_ma_diem': 'DD-TP-01',
      'q6a_ngay': '2026-08-22', 'q6a_loai_ngay': 'Ngày thường',
      'q6a_tuyen': 'Tuyến 65', 'q6a_huong': 'Tân Phú → Q.1', 'q6a_gio_pv': '06:45',
      'q6a_diem_di': 'KCN Tân Bình, Q.Tân Phú', 'q6a_diem_den': 'Nguyễn Huệ, Q.1',
      'q6a_muc_dich': 'Đi làm', 'q6a_gio_kh': '06:15', 'q6a_tong_tg': '60',
      'q6a_pt_tiep_can': 'Xe đạp', 'q6a_tg_tiep_can': '10', 'q6a_tg_cho': '8',
      'q6a_so_chang': '1 chặng', 'q6a_tong_ve': '7000',
      'q6a_pt_khac': ['Xe máy'], 'q6a_co_oto': 'Không', 'q6a_co_xemay': 'Có', 'q6a_co_vethang': 'Không',
      'q6a_danh_gia': { 'Thời gian đi lại toàn hành trình': '2 ⭐', 'Độ tin cậy / đúng giờ': '3 ⭐', 'Thời gian chờ': '3 ⭐', 'Mức độ thoải mái': '2 ⭐', 'Mức độ đông đúc': '1 ⭐', 'An toàn / an ninh': '3 ⭐', 'Khả năng tiếp cận trạm dừng': '2 ⭐', 'Thông tin hành khách': '3 ⭐', 'Chi phí vé': '4 ⭐', 'Đánh giá tổng thể': '3 ⭐' },
      'q6a_tan_suat': 'Vài lần / tuần', 'q6a_tg_dibo': '11–15 phút', 'q6a_tg_cho_cn': '16–20 phút',
      'q6a_so_chuyen_tuyen': '0 lần', 'q6a_thanh_toan': ['Tiền mặt', 'QR / điện thoại'],
      'q6a_pt_hien_tai': 'Xe buýt', 'q6a_tg_hien_tai': '60', 'q6a_cp_hien_tai': '7000',
      'q6a_sp1': 'Không', 'q6a_sp2': 'Có', 'q6a_sp3': 'Không', 'q6a_sp4': 'Có', 'q6a_sp5': 'Có',
      'q6a_tuoi': '36–50', 'q6a_gioi_tinh': 'Nam', 'q6a_nghe_nghiep': 'Công nhân',
      'q6a_thu_nhap': '6–10 triệu', 'q6a_bang_lai': 'Xe máy',
      'q6a_noi_o': 'Q.Tân Phú', 'q6a_noi_lv': 'Q.1',
      'q6a_quy_mo_ho': '6', 'q6a_pt_ho': '3 xe máy, 1 xe đạp', 'q6a_cho_do': 'Không'
    }
  },
  {
    id: 'resp-6a-demo-5',
    surveyId: 'survey-ptcc-6a',
    submittedAt: new Date(Date.now() - 3600000 * 10).toISOString(),
    answers: {
      'q6a_ma_ks': 'HK-005', 'q6a_ma_dtv': 'DTV-03', 'q6a_ma_diem': 'DD-Q3-01',
      'q6a_ngay': '2026-08-22', 'q6a_loai_ngay': 'Thứ Bảy',
      'q6a_tuyen': 'Tuyến 01', 'q6a_huong': 'Chợ Lớn → Bến Thành', 'q6a_gio_pv': '10:00',
      'q6a_diem_di': 'Võ Văn Tần, P.5, Q.3', 'q6a_diem_den': 'Aeon Mall Tân Phú',
      'q6a_muc_dich': 'Giải trí / ăn uống', 'q6a_gio_kh': '09:30', 'q6a_tong_tg': '50',
      'q6a_pt_tiep_can': 'Đi bộ', 'q6a_tg_tiep_can': '3', 'q6a_tg_cho': '7',
      'q6a_so_chang': '2 chặng', 'q6a_tong_ve': '14000',
      'q6a_pt_khac': ['Ô tô', 'Taxi / Grab ô tô', 'Xe buýt'], 'q6a_co_oto': 'Có', 'q6a_co_xemay': 'Có', 'q6a_co_vethang': 'Không',
      'q6a_danh_gia': { 'Thời gian đi lại toàn hành trình': '3 ⭐', 'Độ tin cậy / đúng giờ': '3 ⭐', 'Thời gian chờ': '3 ⭐', 'Mức độ thoải mái': '4 ⭐', 'Mức độ đông đúc': '3 ⭐', 'An toàn / an ninh': '4 ⭐', 'Khả năng tiếp cận trạm dừng': '4 ⭐', 'Thông tin hành khách': '3 ⭐', 'Chi phí vé': '3 ⭐', 'Đánh giá tổng thể': '4 ⭐' },
      'q6a_tan_suat': 'Vài lần / tháng', 'q6a_tg_dibo': '≤ 3 phút', 'q6a_tg_cho_cn': '≤ 5 phút',
      'q6a_so_chuyen_tuyen': '1 lần', 'q6a_thanh_toan': ['QR / điện thoại', 'Thẻ ngân hàng'],
      'q6a_pt_hien_tai': 'Ô tô', 'q6a_tg_hien_tai': '30', 'q6a_cp_hien_tai': '50000',
      'q6a_sp1': 'Không', 'q6a_sp2': 'Không', 'q6a_sp3': 'Có', 'q6a_sp4': 'Có', 'q6a_sp5': 'Có',
      'q6a_tuoi': '23–35', 'q6a_gioi_tinh': 'Nữ', 'q6a_nghe_nghiep': 'Kinh doanh',
      'q6a_thu_nhap': '15–30 triệu', 'q6a_bang_lai': 'Cả hai',
      'q6a_noi_o': 'P.5, Q.3', 'q6a_noi_lv': 'Q.Phú Nhuận',
      'q6a_quy_mo_ho': '3', 'q6a_pt_ho': '1 ô tô, 2 xe máy', 'q6a_cho_do': 'Có'
    }
  }
];

function normalizeText(text) {
  if (!text) return '';
  return text.toString().toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[đĐ]/g, "d")
    .trim();
}

class SurveyStore {
  constructor() {
    this.supabaseClient = null;
    // Automatic version bump to inject Nhiệm vụ 6a template & demo responses
    const dataVersion = localStorage.getItem('formsmobile_data_version');
    if (dataVersion !== 'v50_6a_nosec') {
      localStorage.setItem('formsmobile_data_version', 'v50_6a_nosec');
      this.forceInject6aData();
    }
    this.initStore();
    this.initSupabaseFromStorage();
  }

  forceInject6aData() {
    try {
      let surveys = JSON.parse(localStorage.getItem(STORAGE_KEYS.SURVEYS) || '[]');
      const p6a = INITIAL_SURVEYS.find(s => s.id === 'survey-ptcc-6a');
      if (p6a) {
        const idx = surveys.findIndex(s => s.id === 'survey-ptcc-6a');
        if (idx >= 0) surveys[idx] = p6a;
        else surveys.push(p6a);
        localStorage.setItem(STORAGE_KEYS.SURVEYS, JSON.stringify(surveys));
      }

      let resps = JSON.parse(localStorage.getItem(STORAGE_KEYS.RESPONSES) || '[]');
      const demo6aResps = INITIAL_RESPONSES.filter(r => r.surveyId === 'survey-ptcc-6a');
      demo6aResps.forEach(dr => {
        if (!resps.some(r => r.id === dr.id)) {
          resps.push(dr);
        }
      });
      localStorage.setItem(STORAGE_KEYS.RESPONSES, JSON.stringify(resps));
    } catch (e) {
      console.warn('Error injecting 6a template data:', e);
    }
  }

  initStore() {
    let surveys = [];
    try {
      const stored = localStorage.getItem(STORAGE_KEYS.SURVEYS);
      if (stored) {
        surveys = JSON.parse(stored);
      }
    } catch (e) {
      surveys = [];
    }

    if (!Array.isArray(surveys) || surveys.length === 0) {
      surveys = INITIAL_SURVEYS;
    } else {
      INITIAL_SURVEYS.forEach(tmpl => {
        if (!surveys.some(s => s.id === tmpl.id)) {
          surveys.push(tmpl);
        }
      });
    }

    localStorage.setItem(STORAGE_KEYS.SURVEYS, JSON.stringify(surveys));

    // Seed demo responses if localStorage is empty or has no data
    try {
      const storedResps = localStorage.getItem(STORAGE_KEYS.RESPONSES);
      const parsedResps = storedResps ? JSON.parse(storedResps) : [];
      if (!Array.isArray(parsedResps) || parsedResps.length === 0) {
        localStorage.setItem(STORAGE_KEYS.RESPONSES, JSON.stringify(INITIAL_RESPONSES));
      }
    } catch (e) {
      localStorage.setItem(STORAGE_KEYS.RESPONSES, JSON.stringify(INITIAL_RESPONSES));
    }
    if (!localStorage.getItem(STORAGE_KEYS.SUPABASE_CONFIG)) {
      localStorage.setItem(STORAGE_KEYS.SUPABASE_CONFIG, JSON.stringify(DEFAULT_SUPABASE_CONFIG));
    }
  }

  // --- SUPABASE CONFIGURATION ---
  initSupabaseFromStorage() {
    try {
      // Force project's DEFAULT_SUPABASE_CONFIG to ensure cloud sync works everywhere
      localStorage.setItem(STORAGE_KEYS.SUPABASE_CONFIG, JSON.stringify(DEFAULT_SUPABASE_CONFIG));
      if (window.supabase) {
        try {
          this.supabaseClient = window.supabase.createClient(DEFAULT_SUPABASE_CONFIG.url, DEFAULT_SUPABASE_CONFIG.key);
          setTimeout(() => {
            this.syncLocalSurveysToCloud().catch(err => console.warn('Async cloud sync note:', err));
          }, 100);
        } catch (e) {
          console.error('Lỗi khởi tạo Supabase Client:', e);
        }
      }
    } catch (err) {
      console.warn('Lỗi initSupabaseFromStorage:', err);
    }
  }

  async fetchResponsesForSurvey(surveyId) {
    let localResps = this.getResponsesForSurvey(surveyId);
    let targetSurvey = this.getSurveyById(surveyId);
    let targetTitleNorm = targetSurvey ? normalizeText(targetSurvey.title) : '';
    let data = [];

    // 1. Direct REST fetch to Supabase Cloud API filtered specifically by survey_id
    try {
      let offset = 0;
      const limit = 1000;
      let hasMore = true;

      // Query by exact survey_id first
      while (hasMore && offset < 10000) {
        const restRes = await fetch(`${DEFAULT_SUPABASE_CONFIG.url}/rest/v1/responses?survey_id=eq.${encodeURIComponent(surveyId)}&select=*&order=submitted_at.desc`, {
          headers: {
            'apikey': DEFAULT_SUPABASE_CONFIG.key,
            'Authorization': `Bearer ${DEFAULT_SUPABASE_CONFIG.key}`,
            'Range': `${offset}-${offset + limit - 1}`
          }
        });
        if (restRes.ok) {
          const chunk = await restRes.json();
          if (chunk && chunk.length > 0) {
            data = data.concat(chunk);
            if (chunk.length < limit) {
              hasMore = false;
            } else {
              offset += limit;
            }
          } else {
            hasMore = false;
          }
        } else {
          hasMore = false;
        }
      }

      // If no records were matched by exact survey_id, fetch all records and filter by normalized _survey_title matching
      if (data.length === 0 && targetTitleNorm) {
        offset = 0;
        hasMore = true;
        let allData = [];
        while (hasMore && offset < 10000) {
          const restRes = await fetch(`${DEFAULT_SUPABASE_CONFIG.url}/rest/v1/responses?select=*&order=submitted_at.desc`, {
            headers: {
              'apikey': DEFAULT_SUPABASE_CONFIG.key,
              'Authorization': `Bearer ${DEFAULT_SUPABASE_CONFIG.key}`,
              'Range': `${offset}-${offset + limit - 1}`
            }
          });
          if (restRes.ok) {
            const chunk = await restRes.json();
            if (chunk && chunk.length > 0) {
              allData = allData.concat(chunk);
              if (chunk.length < limit) hasMore = false;
              else offset += limit;
            } else {
              hasMore = false;
            }
          } else {
            hasMore = false;
          }
        }

        data = allData.filter(item => {
          if (item.survey_id === surveyId) return true;
          if (item.answers && item.answers._survey_title) {
            return normalizeText(item.answers._survey_title) === targetTitleNorm;
          }
          return false;
        });
      }

      console.log(`Fetched ${data.length} responses for survey [${surveyId}] from Supabase Cloud.`);
    } catch (err) {
      console.warn('Direct REST fetch error:', err);
    }

    // 2. Fallback to Supabase Client SDK if REST fetch didn't return data
    if ((!data || data.length === 0) && this.supabaseClient) {
      try {
        const res = await this.supabaseClient
          .from('responses')
          .select('*')
          .eq('survey_id', surveyId)
          .order('submitted_at', { ascending: false });
        if (!res.error && res.data && res.data.length > 0) {
          data = res.data;
        }
      } catch (e) {
        console.warn('Supabase SDK fetch warning:', e);
      }
    }

    if (data && data.length > 0) {
      const cloudResps = data
        .filter(item => {
          if (item.survey_id === surveyId) return true;
          if (targetTitleNorm && item.answers && item.answers._survey_title) {
            return normalizeText(item.answers._survey_title) === targetTitleNorm;
          }
          return false;
        })
        .map(item => ({
          id: item.id,
          surveyId: item.survey_id || surveyId,
          submittedAt: item.submitted_at,
          answers: item.answers || {}
        }));

      const map = new Map();
      cloudResps.forEach(r => map.set(r.id, r));
      localResps.forEach(r => {
        if (!map.has(r.id)) map.set(r.id, r);
      });

      const merged = Array.from(map.values());
      merged.sort((a, b) => new Date(b.submittedAt) - new Date(a.submittedAt));

      const allResps = this.getAllResponses();
      const otherResps = allResps.filter(r => r.surveyId !== surveyId);

      try {
        // Strip heavy audio proof strings when caching to localStorage to prevent 5MB QuotaExceededError
        const sanitizedForLocal = [...merged, ...otherResps].map(r => {
          if (r && r.answers && r.answers._audioProof) {
            const copy = JSON.parse(JSON.stringify(r));
            delete copy.answers._audioProof;
            return copy;
          }
          return r;
        });
        localStorage.setItem(STORAGE_KEYS.RESPONSES, JSON.stringify(sanitizedForLocal));
      } catch (quotaErr) {
        console.warn('LocalStorage full, skipped saving local cache:', quotaErr);
      }

      return merged;
    }

    return localResps;
  }

  async syncLocalSurveysToCloud() {
    if (!this.supabaseClient) return;
    const surveys = this.getSurveys();
    for (const survey of surveys) {
      try {
        await this.supabaseClient.from('surveys').upsert({
          id: survey.id,
          title: survey.title,
          description: survey.description,
          theme_color: survey.themeColor || 'purple',
          is_published: survey.isPublished !== false,
          questions: survey.questions,
          updated_at: survey.updatedAt || new Date().toISOString()
        });
      } catch (err) {
        console.warn('Sync survey err:', err);
      }
    }
  }

  saveSupabaseConfig(url, key) {
    if (!url || !key) {
      localStorage.removeItem(STORAGE_KEYS.SUPABASE_CONFIG);
      this.supabaseClient = null;
      return false;
    }

    // Always save config to localStorage first
    localStorage.setItem(STORAGE_KEYS.SUPABASE_CONFIG, JSON.stringify({ url, key }));

    // Try to create Supabase client if SDK is available
    if (window.supabase) {
      try {
        this.supabaseClient = window.supabase.createClient(url, key);
      } catch (e) {
        console.warn('Supabase SDK createClient error:', e);
      }
    }

    // Always sync (fetchResponsesForSurvey already uses direct REST fallback)
    this.syncLocalSurveysToCloud().catch(() => {});
    return true;
  }

  getSupabaseConfig() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEYS.SUPABASE_CONFIG)) || DEFAULT_SUPABASE_CONFIG;
    } catch (e) {
      return DEFAULT_SUPABASE_CONFIG;
    }
  }

  isCloudConnected() {
    // Lazy-init: if SDK loaded after constructor ran, create client now
    if (!this.supabaseClient && window.supabase) {
      const cfg = this.getSupabaseConfig();
      if (cfg && cfg.url && cfg.key) {
        try {
          this.supabaseClient = window.supabase.createClient(cfg.url, cfg.key);
        } catch (e) {}
      }
    }
    // Return true if we have valid config (REST fallback always works)
    const cfg = this.getSupabaseConfig();
    return !!(cfg && cfg.url && cfg.key);
  }

  // --- SURVEY CRUD ---
  getSurveys() {
    try {
      const stored = localStorage.getItem(STORAGE_KEYS.SURVEYS);
      if (!stored) {
        localStorage.setItem(STORAGE_KEYS.SURVEYS, JSON.stringify(INITIAL_SURVEYS));
        return INITIAL_SURVEYS;
      }
      const parsed = JSON.parse(stored);
      return (Array.isArray(parsed) && parsed.length > 0) ? parsed : INITIAL_SURVEYS;
    } catch (e) {
      return INITIAL_SURVEYS;
    }
  }

  getSurveyById(id) {
    const surveys = this.getSurveys();
    return surveys.find(s => s.id === id) || null;
  }

  async getSurveyByIdAsync(id) {
    let survey = this.getSurveyById(id);
    if (survey) return survey;

    if (this.supabaseClient) {
      try {
        const { data, error } = await this.supabaseClient
          .from('surveys')
          .select('*')
          .eq('id', id)
          .single();

        if (!error && data) {
          survey = {
            id: data.id,
            title: data.title,
            description: data.description,
            themeColor: data.theme_color || 'purple',
            isPublished: data.is_published !== false,
            questions: data.questions || [],
            createdAt: data.created_at,
            updatedAt: data.updated_at
          };
          const surveys = this.getSurveys();
          if (!surveys.some(s => s.id === survey.id)) {
            surveys.push(survey);
            localStorage.setItem(STORAGE_KEYS.SURVEYS, JSON.stringify(surveys));
          }
          return survey;
        }
      } catch (e) {
        console.warn('Lỗi lấy survey từ Cloud:', e);
      }
    }
    return null;
  }

  async saveSurvey(surveyData) {
    const surveys = this.getSurveys();
    const existingIndex = surveys.findIndex(s => s.id === surveyData.id);

    surveyData.updatedAt = new Date().toISOString();

    if (existingIndex >= 0) {
      surveys[existingIndex] = surveyData;
    } else {
      surveyData.createdAt = surveyData.createdAt || new Date().toISOString();
      surveys.unshift(surveyData);
    }

    localStorage.setItem(STORAGE_KEYS.SURVEYS, JSON.stringify(surveys));

    // Async sync to Supabase Cloud if connected
    if (this.supabaseClient) {
      try {
        await this.supabaseClient.from('surveys').upsert({
          id: surveyData.id,
          title: surveyData.title,
          description: surveyData.description,
          theme_color: surveyData.themeColor || 'purple',
          is_published: surveyData.isPublished !== false,
          questions: surveyData.questions,
          updated_at: surveyData.updatedAt
        });
      } catch (err) {
        console.warn('Đồng bộ Supabase thất bại:', err);
      }
    }

    return surveyData;
  }

  async deleteSurvey(id) {
    let surveys = this.getSurveys();
    surveys = surveys.filter(s => s.id !== id);
    localStorage.setItem(STORAGE_KEYS.SURVEYS, JSON.stringify(surveys));

    // Clean responses
    let responses = this.getAllResponses();
    responses = responses.filter(r => r.surveyId !== id);
    localStorage.setItem(STORAGE_KEYS.RESPONSES, JSON.stringify(responses));

    // Cloud sync
    if (this.supabaseClient) {
      try {
        await this.supabaseClient.from('surveys').delete().eq('id', id);
      } catch (err) {
        console.warn('Lỗi xóa trên Supabase:', err);
      }
    }
  }

  async fetchSurveysFromCloud() {
    let localSurveys = this.getSurveys();
    if (this.supabaseClient) {
      try {
        const { data, error } = await this.supabaseClient
          .from('surveys')
          .select('*')
          .order('updated_at', { ascending: false });

        if (!error && data && data.length > 0) {
          const cloudSurveys = data.map(item => ({
            id: item.id,
            title: item.title,
            description: item.description,
            themeColor: item.theme_color || 'purple',
            isPublished: item.is_published !== false,
            questions: item.questions || [],
            createdAt: item.created_at,
            updatedAt: item.updated_at
          }));

          // Merge local and cloud surveys
          const map = new Map();
          cloudSurveys.forEach(s => map.set(s.id, s));
          localSurveys.forEach(s => {
            if (!map.has(s.id)) map.set(s.id, s);
          });

          const merged = Array.from(map.values());
          localStorage.setItem(STORAGE_KEYS.SURVEYS, JSON.stringify(merged));
          return merged;
        }
      } catch (err) {
        console.warn('Lỗi lấy danh sách khảo sát từ Supabase Cloud:', err);
      }
    }
    return localSurveys;
  }

  // --- RESPONSE LOGIC ---
  getAllResponses() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEYS.RESPONSES)) || [];
    } catch (e) {
      return [];
    }
  }

  getResponsesForSurvey(surveyId) {
    const all = this.getAllResponses();
    return all.filter(r => r.surveyId === surveyId);
  }

  async submitResponse(surveyId, answers) {
    const responses = this.getAllResponses();
    const newResponse = {
      id: 'resp-' + Date.now(),
      surveyId: surveyId,
      submittedAt: new Date().toISOString(),
      answers: answers
    };

    responses.unshift(newResponse);
    localStorage.setItem(STORAGE_KEYS.RESPONSES, JSON.stringify(responses));

    // Cloud sync to Supabase Cloud if connected
    if (this.supabaseClient) {
      try {
        // Ensure survey is present in Supabase first (to prevent foreign key constraint error)
        let surveyObj = this.getSurveyById(surveyId);
        if (!surveyObj) {
          surveyObj = await this.getSurveyByIdAsync(surveyId);
        }
        if (surveyObj) {
          await this.supabaseClient.from('surveys').upsert({
            id: surveyObj.id,
            title: surveyObj.title,
            description: surveyObj.description,
            theme_color: surveyObj.themeColor || 'purple',
            is_published: surveyObj.isPublished !== false,
            questions: surveyObj.questions,
            updated_at: surveyObj.updatedAt || new Date().toISOString()
          });
        }

        // Insert response into Supabase with survey_title for easy filtering
        const { data, error } = await this.supabaseClient.from('responses').insert({
          id: newResponse.id,
          survey_id: surveyId,
          answers: {
            _survey_title: surveyObj ? surveyObj.title : 'Khảo sát',
            ...answers
          },
          submitted_at: newResponse.submittedAt
        });

        if (error) {
          console.error("Supabase insert error details:", error);
        } else {
          console.log("Lưu Supabase thành công!", data);
        }
      } catch (err) {
        console.warn('Lỗi lưu phản hồi lên Supabase:', err);
      }
    }

    return newResponse;
  }

  // --- EXPORT TO CSV ---
  exportToCSV(surveyId) {
    const survey = this.getSurveyById(surveyId);
    const responses = this.getResponsesForSurvey(surveyId);

    if (!survey || responses.length === 0) {
      alert('Chưa có dữ liệu phản hồi để xuất!');
      return;
    }

    // CSV Headers
    const headers = ['STT', 'Mã Phản Hồi', 'Thời Gian Gửi'];
    survey.questions.forEach(q => {
      headers.push(`"${q.title.replace(/"/g, '""')}"`);
    });
    headers.push(
      '"Địa Chỉ Vị Trí (GPS)"',
      '"Vĩ Độ (Lat)"',
      '"Kinh Độ (Lng)"',
      '"Link Google Maps"',
      '"Văn Bản Phỏng Vấn (AI Transcript)"',
      '"File Ghi Âm Bằng Chứng (Audio Proof)"'
    );

    const rows = [headers.join(',')];

    responses.forEach((resp, index) => {
      const rowData = [
        index + 1,
        resp.id,
        new Date(resp.submittedAt).toLocaleString('vi-VN')
      ];

      survey.questions.forEach(q => {
        let val = resp.answers[q.id];
        if (val === undefined || val === null) {
          val = '';
        } else if (Array.isArray(val)) {
          val = val.join('; ');
        } else if (typeof val === 'object') {
          // File Upload: {name, size, dataUrl}
          if (val.name && val.dataUrl) {
            val = val.name + ' (' + (val.size || '') + ')';
          }
          // Grid: {"Hàng 1": "Cột A", "Hàng 2": ["Cột A", "Cột B"]}
          else {
            val = Object.entries(val).map(([row, col]) => {
              if (Array.isArray(col)) {
                return row + ': ' + col.join(', ');
              }
              return row + ': ' + col;
            }).join(' | ');
          }
        }
        rowData.push(`"${String(val).replace(/"/g, '""')}"`);
      });

      // Location fields
      const loc = resp.answers._location || {};
      rowData.push(`"${String(loc.address || '').replace(/"/g, '""')}"`);
      rowData.push(`"${loc.latitude || ''}"`);
      rowData.push(`"${loc.longitude || ''}"`);
      rowData.push(`"${loc.mapsUrl || ''}"`);

      // Audio & Transcript AI fields
      const transcript = resp.answers._aiTranscript || '';
      let audioProofText = '';
      if (resp.answers._audioProof) {
        if (resp.answers._audioProof.startsWith('http')) {
          audioProofText = resp.answers._audioProof;
        } else {
          audioProofText = '[Đã ghi âm bằng chứng - Nghe trực tiếp trên Web App]';
        }
      }
      rowData.push(`"${String(transcript).replace(/"/g, '""')}"`);
      rowData.push(`"${String(audioProofText).replace(/"/g, '""')}"`);

      rows.push(rowData.join(','));
    });

    const csvContent = '\uFEFF' + rows.join('\n'); // UTF-8 BOM for Excel Vietnamese support
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `Khao_sat_${survey.title.replace(/\s+/g, '_')}_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}

window.surveyStore = new SurveyStore();
