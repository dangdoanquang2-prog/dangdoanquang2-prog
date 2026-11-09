// ==============================================================================================
// DỰ ÁN: NGHIÊN CỨU TUYẾN SỐ 2 (ĐOẠN THAM LƯƠNG - AN HẠ) VÀ TUYẾN 2S (AN HẠ - KHU ĐÔ THỊ TÂY BẮC)
// TÀI LIỆU CĂN CỨ: NHIEM VU 7A PHIEU PHONG VAN NGUOI SU DUNG XE MAY VA O TO.docx
// PHIÊN BẢN: v1.0 — Đầy đủ sàng lọc P1, O-D ma trận, SP 4 pivot, 4 Block phân nhánh Q20 & WebBridge GPS
// ==============================================================================================
//
// HƯỚNG DẪN SỬ DỤNG NHANH:
// 1. Mở trình duyệt, truy cập: https://script.google.com và bấm "Dự án mới" (New project).
// 2. Xóa toàn bộ nội dung mặc định trong file Mã.gs (Code.gs), dán toàn bộ mã nguồn này vào.
// 3. Tại thanh công cụ bên trên, chọn hàm "taoFormXeMayOTo7A" và bấm "Chạy" (Run).
// 4. Cấp quyền truy cập Google Form cho Script khi được hỏi.
// 5. Mở tab "Nhật ký thực thi" (Execution Log) để lấy link Form và các Entry ID.
// 6. (Tùy chọn WebBridge GPS Trạm Xăng): Triển khai Web App để KSV tự động bắt GPS trạm xăng + xoay tua Block.
// ==============================================================================================

function taoFormXeMayOTo7A() {
  var form = FormApp.create('PHIẾU 7A: PHỎNG VẤN NGƯỜI SỬ DỤNG XE MÁY VÀ Ô TÔ (MRT2 & MRT2S)');

  form.setDescription(
    'DỰ ÁN NGHIÊN CỨU TUYẾN SỐ 2 (ĐOẠN THAM LƯƠNG - AN HẠ) VÀ TUYẾN 2S (AN HẠ - KHU ĐÔ THỊ TÂY BẮC)\n' +
    'PHIẾU 7A: KHẢO SÁT NGƯỜI SỬ DỤNG XE MÁY VÀ Ô TÔ TẠI TRẠM XĂNG DẦU / ĐIỂM DỪNG\n\n' +
    '* Lưu ý KSV: Bắt buộc chụp ảnh có địa chỉ, tọa độ cửa hàng xăng dầu khảo sát để làm minh chứng.\n' +
    '* Đối tượng: Người đang điều khiển hoặc là hành khách đi trên Xe máy và Ô tô.\n' +
    '* Thông tin chỉ phục vụ nghiên cứu quy hoạch giao thông đô thị và được bảo mật tuyệt đối.'
  );
  form.setConfirmationMessage('Cảm ơn Anh/Chị đã dành thời gian hoàn thành phiếu khảo sát giao thông Tuyến Metro số 2!');

  // ==========================================================================
  // PHẦN 0: ĐỊNH VỊ TRẠM XĂNG & KIỂM SOÁT MẪU
  // ==========================================================================
  form.addSectionHeaderItem().setTitle('0. ĐỊNH VỊ TRẠM XĂNG DẦU & KIỂM SOÁT MẪU KHẢO SÁT');

  var itemGps = form.addTextItem()
      .setTitle('Tọa độ GPS trạm xăng dầu (Kinh độ, Vĩ độ)')
      .setHelpText('Hệ thống WebBridge tự động điền từ GPS điện thoại KSV. Có thể sửa lại nếu cần.')
      .setRequired(true);

  var itemAddress = form.addTextItem()
      .setTitle('Địa chỉ thực tế của trạm xăng dầu khảo sát')
      .setHelpText('Hệ thống tự động tra cứu từ bản đồ số. KSV đối soát và nhập chính xác số nhà, tên đường thực tế.')
      .setRequired(true);

  form.addTextItem()
      .setTitle('Tên cửa hàng / Trạm xăng dầu khảo sát')
      .setHelpText('Ví dụ: Cửa hàng xăng dầu Petrolimex Số 14, Cây xăng Ba Sa, Cây xăng An Hạ...')
      .setRequired(true);

  form.addTextItem()
      .setTitle('Hướng khảo sát')
      .setHelpText('Ghi rõ: Từ [Điểm A] đến [Điểm B]. Ví dụ: Từ Củ Chi về Tham Lương')
      .setRequired(true);

  form.addTextItem()
      .setTitle('Site / Link / Screenline ID')
      .setHelpText('Mã trạm hoặc mã mặt cắt khảo sát do Trưởng nhóm quy định. Ví dụ: SL01, SL02...')
      .setRequired(true);

  form.addDateItem()
      .setTitle('Ngày phỏng vấn')
      .setRequired(true);

  form.addTimeItem()
      .setTitle('Giờ phỏng vấn')
      .setRequired(true);

  form.addTextItem()
      .setTitle('Khoảng thời gian lấy mẫu (Time Interval)')
      .setHelpText('Ví dụ: 06:00 - 08:00, 08:00 - 10:00, 16:00 - 18:00...')
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('Chu kỳ lấy mẫu (Interval)')
      .setChoiceValues(['15 phút', '30 phút', 'Khác'])
      .showOtherOption(true)
      .setRequired(true);

  form.addTextItem()
      .setTitle('Họ tên / Mã điều tra viên (KSV)')
      .setHelpText('Nhập mã KSV. Ví dụ: DTV01, DTV02...')
      .setRequired(true);

  form.addTextItem()
      .setTitle('Mã kiểm tra / Mã hóa (QC)')
      .setHelpText('Dành cho Giám sát viên kiểm tra (bỏ trống nếu chưa có)');

  // ==========================================================================
  // CÂU HỎI SÀNG LỌC P1 (ĐIỀU HƯỚNG DỪNG PHỎNG VẤN NẾU CHỌN "KHÁC")
  // ==========================================================================
  var pageEndScreening = form.addPageBreakItem().setTitle('KẾT THÚC PHỎNG VẤN (KHÔNG ĐÚNG ĐỐI TƯỢNG)');
  form.addSectionHeaderItem().setTitle('Cảm ơn bạn! Phiếu phỏng vấn này chỉ áp dụng cho người đi Xe máy và Ô tô.');

  var pagePartA = form.addPageBreakItem().setTitle('PHẦN A: THÔNG TIN CHUYẾN ĐI VÀ O-D');

  var itemScreening = form.addMultipleChoiceItem()
      .setTitle('Câu hỏi sàng lọc P1. Bạn đang thực hiện chuyến đi này bằng:')
      .setHelpText('⚠️ Chỉ phỏng vấn người đi Xe máy hoặc Ô tô. Nếu là phương tiện khác sẽ dừng phỏng vấn.')
      .setRequired(true);

  itemScreening.setChoices([
    itemScreening.createChoice('1. Xe máy', pagePartA),
    itemScreening.createChoice('2. Ô tô', pagePartA),
    itemScreening.createChoice('3. Khác (Dừng phỏng vấn)', pageEndScreening)
  ]);

  // ==========================================================================
  // PHẦN A: THÔNG TIN CHUYẾN ĐI VÀ MA TRẬN O-D
  // ==========================================================================
  // (Đã tạo pagePartA ở trên)
  var mucDichList = [
    '1. Nhà ở',
    '2. Công việc / Nơi làm việc',
    '3. Kinh doanh / Giao dịch',
    '4. Giáo dục / Đi học',
    '5. Mua sắm / Chợ / Siêu thị',
    '6. Giải trí / Ăn uống / Gặp gỡ',
    '7. Thăm thân / Khám bệnh / Cá nhân',
    '8. Khác'
  ];

  form.addSectionHeaderItem().setTitle('1. ĐIỂM XUẤT PHÁT THỰC TẾ CỦA CHUYẾN ĐI (ORIGIN)');

  form.addTextItem()
      .setTitle('1a. Điểm xuất phát: Số nhà / Tên đường / Khu phố')
      .setHelpText('Ghi rõ địa chỉ nơi bạn vừa bắt đầu xuất phát')
      .setRequired(true);

  form.addTextItem()
      .setTitle('1b. Điểm xuất phát: Phường / Xã')
      .setRequired(true);

  form.addTextItem()
      .setTitle('1c. Điểm xuất phát: Thành phố / Tỉnh')
      .setRequired(true);

  form.addTextItem()
      .setTitle('1d. Mã vùng / TAZ xuất phát (O_TAZ)')
      .setHelpText('Bỏ trống nếu chưa xác định mã TAZ');

  form.addMultipleChoiceItem()
      .setTitle('1e. Mục đích tại nơi xuất phát')
      .setChoiceValues(mucDichList)
      .showOtherOption(true)
      .setRequired(true);

  form.addSectionHeaderItem().setTitle('2. ĐIỂM ĐẾN CUỐI CÙNG CỦA CHUYẾN ĐI (DESTINATION)');

  form.addTextItem()
      .setTitle('2a. Điểm đến cuối cùng: Số nhà / Tên đường / Khu phố')
      .setHelpText('Ghi rõ địa chỉ điểm đến cuối cùng của chuyến đi này')
      .setRequired(true);

  form.addTextItem()
      .setTitle('2b. Điểm đến cuối cùng: Phường / Xã')
      .setRequired(true);

  form.addTextItem()
      .setTitle('2c. Điểm đến cuối cùng: Thành phố / Tỉnh')
      .setRequired(true);

  form.addTextItem()
      .setTitle('2d. Mã vùng / TAZ điểm đến (D_TAZ)')
      .setHelpText('Bỏ trống nếu chưa xác định mã TAZ');

  form.addMultipleChoiceItem()
      .setTitle('2e. Mục đích tại nơi đến')
      .setChoiceValues(mucDichList)
      .showOtherOption(true)
      .setRequired(true);

  form.addSectionHeaderItem().setTitle('3. THỜI GIAN, QUÃNG ĐƯỜNG & VAI TRÒ');

  form.addTimeItem()
      .setTitle('3a. Giờ xuất phát khỏi điểm đi')
      .setHelpText('Ví dụ: 07:15')
      .setRequired(true);

  form.addTimeItem()
      .setTitle('3b. Giờ đến nơi dự kiến / thực tế')
      .setHelpText('Ví dụ: 08:00')
      .setRequired(true);

  form.addTextItem()
      .setTitle('3c. Tổng thời gian chuyến đi (Phút)')
      .setHelpText('Thời gian đi từ điểm đi đến điểm đến. Ví dụ: 25, 45, 60')
      .setRequired(true);

  form.addTextItem()
      .setTitle('3d. Quãng đường ước tính chuyến đi (km)')
      .setHelpText('Cự ly chuyến đi. Ví dụ: 8.5, 12, 25')
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('4a. Vai trò trên xe trong chuyến đi này')
      .setChoiceValues(['1. Người lái xe', '2. Hành khách ngồi sau / đi cùng'])
      .setRequired(true);

  form.addTextItem()
      .setTitle('4b. Số người thực tế ngồi trên xe (Kể cả người trả lời)')
      .setHelpText('Ví dụ: 1 người (đi một mình), 2 người, 4 người...')
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('5. Tần suất thực hiện chuyến đi này')
      .setChoiceValues([
        '≥ 5 lần / tuần (Hàng ngày)',
        '3 – 4 lần / tuần',
        '1 – 2 lần / tuần',
        '< 1 lần / tuần (Thỉnh thoảng / Lần đầu)'
      ])
      .setRequired(true);

  form.addSectionHeaderItem().setTitle('6. BÓC TÁCH CHI PHÍ CỦA CHÍNH CHUYẾN ĐI NÀY');

  form.addTextItem()
      .setTitle('6a. Chi phí: Nhiên liệu xăng dầu (VNĐ)')
      .setHelpText('Ước tính tiền xăng cho chuyến đi này. Ví dụ: 15000, 30000. Ghi 0 nếu không tính được')
      .setRequired(true);

  form.addTextItem()
      .setTitle('6b. Chi phí: Gửi/đỗ xe (VNĐ)')
      .setHelpText('Tiền gửi xe tại điểm đến. Ghi 0 nếu đỗ xe miễn phí')
      .setRequired(true);

  form.addTextItem()
      .setTitle('6c. Chi phí: Phí đường bộ / Cầu đường / Toll / BOT (VNĐ)')
      .setHelpText('Tiền phí qua trạm BOT nếu có. Ghi 0 nếu không có')
      .setRequired(true);

  form.addTextItem()
      .setTitle('6d. Chi phí: Khác (VNĐ)')
      .setHelpText('Chi phí phát sinh khác. Ghi 0 nếu không có');

  form.addTextItem()
      .setTitle('6e. Tổng chi phí cho chuyến đi này (VNĐ)')
      .setHelpText('Tổng cộng tất cả các khoản chi phí. Ví dụ: 25000, 50000')
      .setRequired(true);

  // ==========================================================================
  // PHẦN B: KHẢ NĂNG SỬ DỤNG PHƯƠNG TIỆN VÀ LỰA CHỌN PHƯƠNG THỨC
  // ==========================================================================
  form.addSectionHeaderItem().setTitle('PHẦN B: KHẢ NĂNG SỬ DỤNG PHƯƠNG TIỆN & LỰA CHỌN PHƯƠNG THỨC');

  form.addMultipleChoiceItem()
      .setTitle('7a. Giấy phép lái xe (GPLX)')
      .setChoiceValues([
        '1. Chỉ có GPLX Xe máy',
        '2. Chỉ có GPLX Ô tô',
        '3. Có cả hai (Xe máy & Ô tô)',
        '4. Không có GPLX'
      ])
      .setRequired(true);

  form.addTextItem()
      .setTitle('7b. Số lượng xe Ô TÔ sở hữu trong hộ gia đình')
      .setHelpText('Ghi số lượng. Nhập 0 nếu không có')
      .setRequired(true);

  form.addTextItem()
      .setTitle('7c. Số lượng XE MÁY sở hữu trong hộ gia đình')
      .setHelpText('Ghi số lượng. Nhập 0 nếu không có')
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('8a. Anh/chị có sẵn xe Ô TÔ riêng để tự do sử dụng không?')
      .setChoiceValues(['Có', 'Không'])
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('8b. Anh/chị có sẵn XE MÁY riêng để tự do sử dụng không?')
      .setChoiceValues(['Có', 'Không'])
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('9. Anh/chị có luôn sử dụng xe máy / ô tô cho chuyến đi này không?')
      .setChoiceValues(['1. Luôn luôn', '2. Đôi khi', '3. Hiếm khi'])
      .setRequired(true);

  form.addCheckboxItem()
      .setTitle('10. Tại sao bạn sử dụng xe máy / ô tô cho chuyến này? (Có thể chọn nhiều)')
      .setChoiceValues([
        '1. Thuận tiện (Đi từ cửa đến cửa, linh hoạt dừng đỗ)',
        '2. Tiết kiệm thời gian đi lại (Nhanh chóng)',
        '3. Thoải mái, chủ động lịch trình cá nhân',
        '4. Cảm thấy an toàn hơn phương tiện khác',
        '5. Chi phí thấp / Phù hợp túi tiền',
        '6. Phải chở theo hàng hóa / Đồ đạc cồng kềnh',
        '7. Đi cùng gia đình / Trẻ nhỏ / Đưa đón người thân',
        '8. Không có phương tiện công cộng thay thế thuận tiện'
      ])
      .showOtherOption(true)
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('11. Nếu không thể dùng phương tiện hiện tại, bạn sẽ chọn phương thức nào?')
      .setChoiceValues([
        '1. Xe máy (đi nhờ / làm hành khách ngồi sau)',
        '2. Ô tô (đi nhờ / làm hành khách)',
        '3. Xe buýt đô thị',
        '4. Taxi / Xe công nghệ (Grab, Be, Xanh SM...)',
        '5. Đi bộ / Đi xe đạp',
        '6. Không thực hiện chuyến đi này nữa'
      ])
      .showOtherOption(true)
      .setRequired(true);

  form.addCheckboxItem()
      .setTitle('12. Tại sao bạn không sử dụng xe buýt cho chuyến đi này? (Có thể chọn nhiều)')
      .setChoiceValues([
        '1. Không có tuyến xe buýt thuận tiện / Trạm dừng quá xa',
        '2. Xe buýt không đủ tin cậy / Tần suất thấp / Chờ đợi lâu',
        '3. Thời gian đi xe buýt quá lâu so với xe cá nhân',
        '4. Xe buýt không thoải mái / Đông đúc / Khó có chỗ ngồi',
        '5. Lo ngại về an ninh / An toàn trên xe buýt',
        '6. Giá vé xe buýt không hấp dẫn',
        '7. Bất tiện khi thời tiết mưa gió / Nắng nóng',
        '8. Phải chuyển tuyến nhiều lần'
      ])
      .showOtherOption(true)
      .setRequired(true);

  // ==========================================================================
  // PHẦN C: THÔNG TIN CÁ NHÂN
  // ==========================================================================
  form.addSectionHeaderItem().setTitle('PHẦN C: THÔNG TIN CÁ NHÂN NGƯỜI ĐƯỢC PHỎNG VẤN');

  form.addMultipleChoiceItem()
      .setTitle('13. Giới tính')
      .setChoiceValues(['Nam', 'Nữ', 'Khác / Không trả lời'])
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('14. Độ tuổi')
      .setChoiceValues([
        '< 20 tuổi',
        '20 – 29 tuổi',
        '30 – 39 tuổi',
        '40 – 49 tuổi',
        '50 – 59 tuổi',
        '≥ 60 tuổi'
      ])
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('15. Nghề nghiệp chính hiện tại')
      .setChoiceValues([
        '1. Có việc làm (Văn phòng / Công chức / Chuyên viên)',
        '2. Lao động kỹ thuật / Công nhân sản xuất',
        '3. Tự kinh doanh / Buôn bán / Dịch vụ',
        '4. Lái xe / Nhân viên giao vận',
        '5. Học sinh / Sinh viên',
        '6. Nội trợ / Chăm sóc gia đình',
        '7. Nghỉ hưu',
        '8. Tự do / Khác'
      ])
      .showOtherOption(true)
      .setRequired(true);

  form.addTextItem()
      .setTitle('16a. Chi tiêu giao thông cá nhân hàng tháng: Tiền xăng dầu (VNĐ)')
      .setHelpText('Ước tính số tiền xăng hàng tháng. Ví dụ: 500000')
      .setRequired(true);

  form.addTextItem()
      .setTitle('16b. Chi tiêu giao thông hàng tháng: Tiền gửi/đỗ xe (VNĐ)')
      .setHelpText('Ví dụ: 150000. Ghi 0 nếu không mất phí')
      .setRequired(true);

  form.addTextItem()
      .setTitle('16c. Chi tiêu giao thông hàng tháng: Bảo dưỡng, sửa chữa xe (VNĐ)')
      .setHelpText('Ví dụ: 200000. Ghi 0 nếu không có')
      .setRequired(true);

  form.addTextItem()
      .setTitle('16d. Chi tiêu giao thông hàng tháng: Chi phí khác (VNĐ)')
      .setHelpText('Ví dụ: Phí cầu đường BOT... Ghi 0 nếu không có');

  form.addMultipleChoiceItem()
      .setTitle('17. Mức thu nhập cá nhân hàng tháng')
      .setChoiceValues([
        '< 5 triệu VNĐ',
        '5 – < 8 triệu VNĐ',
        '8 – < 12 triệu VNĐ',
        '12 – < 20 triệu VNĐ',
        '20 – < 30 triệu VNĐ',
        '30 – < 50 triệu VNĐ',
        '≥ 50 triệu VNĐ',
        'Không trả lời'
      ])
      .setRequired(true);

  // ==========================================================================
  // PHẦN D: PHƯƠNG THỨC ĐƯỜNG SẮT ĐÔ THỊ (METRO) TRONG TƯƠNG LAI
  // ==========================================================================
  form.addSectionHeaderItem()
      .setTitle('PHẦN D: PHƯƠNG THỨC VẬN CHUYỂN BẰNG ĐƯỜNG SẮT ĐÔ THỊ (METRO) TRONG TƯƠNG LAI')
      .setHelpText(
        'Metro là một hệ thống vận tải đường sắt nội thành với khả năng chuyên chở lớn và thường xuyên. ' +
        'Phương thức vận tải Metro có thể được xây dựng ở dưới mặt đất hoặc ở trên không và vận tốc trung bình ' +
        'của phương thức vận tải Metro là khoảng từ 30-40 km/h.'
      );

  // ===================== CÂU 18: ƯỚC TÍNH PHƯƠNG TIỆN KHÁC (CHUẨN FORM KHẢO SÁT) =====================
  form.addCheckboxItem()
      .setTitle('18. Nếu anh/chị đi từ điểm xuất phát đến điểm đến bằng các phương tiện khác, ước tính phương tiện có thể sử dụng:')
      .setHelpText('Tích chọn tất cả các phương tiện anh/chị có thể sử dụng (Thời gian và chi phí sẽ được tính toán tự động bằng mô hình)')
      .setChoiceValues([
        '1. Đi bộ',
        '2. Đạp xe đạp',
        '3. Xe ôm / Xe máy công nghệ (Grab, Be)',
        '4. Taxi / Taxi công nghệ (Grab, Xanh SM)',
        '5. Xe buýt đô thị',
        '6. Đường sắt đô thị (Metro)',
        '7. Xe khác'
      ])
      .setRequired(true);

  // ===================== CÂU 19: SP PIVOT — 4 KỊCH BẢN NỘI SUY =====================
  form.addGridItem()
      .setTitle('19. Giả định Metro đã hoạt động, anh/chị có chọn chuyển sang Metro không?')
      .setHelpText(
        'Giả định hệ thống Metro đã hoàn thành và có trạm Metro thuận tiện cho hành trình này.\n' +
        'Đọc từng dòng giá vé và thời gian, hỏi chọn CÓ hoặc KHÔNG.'
      )
      .setRows([
        'Giá vé 7.000 VNĐ | Thời gian GIẢM 15 phút so với hiện nay (Đi rất nhanh)',
        'Giá vé 7.000 VNĐ | Thời gian BẰNG phương tiện hiện nay (0 phút)',
        'Giá vé 25.000 VNĐ | Thời gian GIẢM 15 phút so với hiện nay (Đi rất nhanh)',
        'Giá vé 25.000 VNĐ | Thời gian BẰNG phương tiện hiện nay (0 phút)'
      ])
      .setColumns(['CÓ', 'KHÔNG'])
      .setRequired(true);

  // ===================== CÂU 20: 4 BLOCK PHÂN NHÁNH TIẾP CẬN GA METRO =====================
  form.addSectionHeaderItem().setTitle(
    '20. PHƯƠNG TIỆN TIẾP CẬN GA METRO THEO KHOẢNG CÁCH\n' +
    'Giả định Metro đã hoạt động, bạn sẽ dùng phương tiện gì để đi đến trạm Metro và từ trạm Metro đến điểm cuối?'
  );

  var itemBlockChoice = form.addMultipleChoiceItem()
      .setTitle('Mã Block Khảo sát Q20 (Hệ thống tự động phân phối)')
      .setHelpText('⚠️ KSV: Chọn đúng Block hiển thị trên màn hình Trợ Lý Định Vị rồi bấm TIẾP')
      .setRequired(true);

  var vehicles = [
    '1: Xe hơi riêng',
    '2: Đi bộ',
    '3: Xe đạp',
    '4: Xe ôm / Xe máy công nghệ',
    '5: Taxi / Taxi công nghệ',
    '6: Xe máy cá nhân',
    '8: Xe buýt gom',
    '9: Khác'
  ];

  // PAGE END — Trang kết thúc phỏng vấn (tất cả Block nhảy về đây)
  var pageEndForm = form.addPageBreakItem().setTitle('HOÀN THÀNH PHỎNG VẤN 7A');

  // BLOCK 1: (0-150m, 150m-300m)
  var pageBlock1 = form.addPageBreakItem().setTitle('Q20. PHƯƠNG TIỆN TIẾP CẬN GA METRO (BLOCK 1)');
  addDistanceGroup7A(form, ['0-150m', '150m-300m'], vehicles);
  pageBlock1.setGoToPage(pageEndForm);

  // BLOCK 2: (300m-450m, 450m-600m)
  var pageBlock2 = form.addPageBreakItem().setTitle('Q20. PHƯƠNG TIỆN TIẾP CẬN GA METRO (BLOCK 2)');
  addDistanceGroup7A(form, ['300m-450m', '450m-600m'], vehicles);
  pageBlock2.setGoToPage(pageEndForm);

  // BLOCK 3: (450m-600m, 600m-1000m) — 450-600m là nút mỏ neo trùng lặp
  var pageBlock3 = form.addPageBreakItem().setTitle('Q20. PHƯƠNG TIỆN TIẾP CẬN GA METRO (BLOCK 3)');
  addDistanceGroup7A(form, ['450m-600m', '600m-1000m'], vehicles);
  pageBlock3.setGoToPage(pageEndForm);

  // BLOCK 4: (1000m-2000m, 2000m-3000m)
  var pageBlock4 = form.addPageBreakItem().setTitle('Q20. PHƯƠNG TIỆN TIẾP CẬN GA METRO (BLOCK 4)');
  addDistanceGroup7A(form, ['1000m-2000m', '2000m-3000m'], vehicles);
  pageBlock4.setGoToPage(pageEndForm);

  // CẤU HÌNH ĐIỀU HƯỚNG TỰ ĐỘNG DỰA TRÊN LỰA CHỌN BLOCK
  itemBlockChoice.setChoices([
    itemBlockChoice.createChoice('Block 1', pageBlock1),
    itemBlockChoice.createChoice('Block 2', pageBlock2),
    itemBlockChoice.createChoice('Block 3', pageBlock3),
    itemBlockChoice.createChoice('Block 4', pageBlock4)
  ]);

  // ==========================================================================
  // TỰ ĐỘNG TRÍCH XUẤT PREFILLED PARAMETERS (CHỈ 2 TRƯỜNG GPS & ĐỊA CHỈ)
  // ==========================================================================
  var response = form.createResponse();
  response.withItemResponse(itemGps.createResponse("GPS_TEST"));
  response.withItemResponse(itemAddress.createResponse("ADDR_TEST"));
  var prefilledUrl = response.toPrefilledUrl();

  var matchGps = prefilledUrl.match(/entry\.\d+=(?=GPS_TEST)/);
  var matchAddr = prefilledUrl.match(/entry\.\d+=(?=ADDR_TEST)/);

  var entryGps = matchGps ? matchGps[0].replace('=', '') : 'entry.GPS_ID';
  var entryAddr = matchAddr ? matchAddr[0].replace('=', '') : 'entry.ADDR_ID';

  // Lưu cấu hình vào ScriptProperties
  PropertiesService.getScriptProperties().setProperties({
    'FORM_BASE_URL': form.getPublishedUrl() + "?usp=pp_url",
    'ENTRY_GPS': entryGps,
    'ENTRY_ADDRESS': entryAddr,
    'FORM_EDIT_URL': form.getEditUrl()
  });

  // ==========================================================================
  // IN THÔNG TIN HOÀN THÀNH RA LOG (ĐỂ DÁN VÀO WEBBRIDGE GPS)
  // ==========================================================================
  Logger.log("==================================================================");
  Logger.log(" ĐÃ TẠO THÀNH CÔNG PHIẾU 7A: PHỎNG VẤN XE MÁY & Ô TÔ (MRT2 & MRT2S)!");
  Logger.log("==================================================================");
  Logger.log("📝 Link Chỉnh Sửa Form: " + form.getEditUrl());
  Logger.log("📋 Link Điền Form: " + form.getPublishedUrl());
  Logger.log("");
  Logger.log(">>> COPY 3 THÔNG SỐ DƯỚI ĐÂY DÁN VÀO FILE WebBridgeGPS.gs <<<");
  Logger.log("1. FORM_BASE_URL: " + form.getPublishedUrl() + "?usp=pp_url");
  Logger.log("2. ENTRY_GPS: " + entryGps);
  Logger.log("3. ENTRY_ADDRESS: " + entryAddr);
  Logger.log("==================================================================");
}

// ==============================================================================
// HÀM TẠO NHÓM CÂU HỎI THEO CỰ LY (CHO BLOCK Q20 PHIẾU 7A) — HỘP KIỂM CHỌN NHIỀU
// ==============================================================================
function addDistanceGroup7A(form, distances, vehicles) {
  // Q20.1: Từ nhà → Ga Metro
  form.addSectionHeaderItem().setTitle('■ Từ nhà đến trạm Metro');
  distances.forEach(function(dist) {
    form.addCheckboxItem()
        .setTitle('Khoảng cách [' + dist + '] - Phương tiện di chuyển')
        .setHelpText('Giả sử có trạm Metro cách nhà ' + dist + ', anh/chị sẽ đi đến trạm bằng gì?')
        .setChoiceValues(vehicles)
        .setRequired(true);
  });

  // Q20.2: Từ ga Metro → Điểm cuối hành trình
  form.addSectionHeaderItem().setTitle('■ Từ nhà ga Metro đến điểm cuối của hành trình');
  distances.forEach(function(dist) {
    form.addCheckboxItem()
        .setTitle('Khoảng cách [' + dist + '] - Phương tiện di chuyển')
        .setHelpText('Khi xuống ga Metro cách điểm cuối ' + dist + ', anh/chị sẽ đi tiếp bằng gì?')
        .setChoiceValues(vehicles)
        .setRequired(true);
  });
}
