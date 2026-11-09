/**
 * ==============================================================================
 * DỰ ÁN NGHIÊN CỨU TUYẾN SỐ 2 (ĐOẠN THAM LƯƠNG - AN HẠ) VÀ TUYẾN 2S (AN HẠ - KHU ĐÔ THỊ TÂY BẮC)
 * PHIẾU 7B: KHẢO SÁT PHỎNG VẤN HÀNH KHÁCH TẠI BẾN / ĐIỂM DỪNG XE BUÝT
 * CĂN CỨ TÀI LIỆU GỐC: NHIEM VU 7B PHIEU KHAO SAT PHONG VAN HANH KHACH TAI BEN-DIEM DUNG XE BUYT.docx
 * CHUẨN HÓA 100% THEO TÀI LIỆU GỐC — KHÔNG THÊM BỚT ĐÁP ÁN
 * ==============================================================================
 */

function taoFormHanhKhachXeBuyt7B() {
  var formTitle = 'PHIẾU 7B: KHẢO SÁT HÀNH KHÁCH TẠI BẾN / ĐIỂM DỪNG XE BUÝT (MRT2 & MRT2S)';
  var form = FormApp.create(formTitle);

  form.setDescription(
    'DỰ ÁN NGHIÊN CỨU TUYẾN SỐ 2 (ĐOẠN THAM LƯƠNG - AN HẠ) VÀ TUYẾN 2S (AN HẠ - KHU ĐÔ THỊ TÂY BẮC)\n' +
    'PHIẾU KHẢO SÁT PHỎNG VẤN HÀNH KHÁCH TẠI BẾN / ĐIỂM DỪNG XE BUÝT\n\n' +
    '* Lưu ý KSV: Bắt buộc chụp ảnh có địa chỉ, tọa độ trạm dừng / nhà chờ khảo sát để làm minh chứng.\n' +
    '* Đối tượng: Hành khách đang chờ hoặc đi trên các tuyến xe buýt tại điểm khảo sát.\n' +
    '* Thông tin chỉ phục vụ nghiên cứu quy hoạch giao thông đô thị và được bảo mật tuyệt đối.'
  );
  form.setConfirmationMessage('Cảm ơn Anh/Chị đã dành thời gian hoàn thành phiếu khảo sát giao thông Tuyến Metro số 2!');

  // ==========================================================================
  // PHẦN 0: ĐỊNH VỊ VỊ TRÍ TRẠM XE BUÝT & KIỂM SOÁT MẪU
  // ==========================================================================
  form.addSectionHeaderItem().setTitle('0. ĐỊNH VỊ TRẠM XE BUÝT & KIỂM SOÁT MẪU KHẢO SÁT');

  var itemGps = form.addTextItem()
      .setTitle('Tọa độ GPS trạm dừng xe buýt (Kinh độ, Vĩ độ)')
      .setHelpText('Hệ thống WebBridge tự động điền từ GPS điện thoại KSV.')
      .setRequired(true);

  var itemAddress = form.addTextItem()
      .setTitle('Địa chỉ gần nhất của trạm dừng xe buýt khảo sát')
      .setHelpText('Hệ thống tự động tra cứu từ bản đồ số hoặc KSV ghi rõ số nhà, tên đường thực tế.')
      .setRequired(true);

  form.addTextItem()
      .setTitle('Tên trạm xe buýt khảo sát')
      .setHelpText('Ví dụ: Trạm Bến xe Củ Chi, Trạm Ngã tư Ba Sa, Trạm An Sương...')
      .setRequired(true);

  form.addDateItem()
      .setTitle('Ngày phỏng vấn')
      .setRequired(true);

  form.addTimeItem()
      .setTitle('Giờ phỏng vấn')
      .setRequired(true);

  form.addTextItem()
      .setTitle('Họ tên / Mã điều tra viên (KSV)')
      .setHelpText('Nhập mã KSV. Ví dụ: DTV01, DTV02...')
      .setRequired(true);

  form.addTextItem()
      .setTitle('Điểm lên xe / Stop name')
      .setHelpText('Tên trạm hành khách đón/lên xe buýt')
      .setRequired(true);

  form.addTextItem()
      .setTitle('Stop ID')
      .setHelpText('Mã số trạm dừng xe buýt. Ví dụ: Q12-005, BX-01...')
      .setRequired(true);

  form.addTextItem()
      .setTitle('Visum Stop Area No.')
      .setHelpText('Mã vùng trạm Visum (bỏ trống nếu chưa có)');

  form.addTextItem()
      .setTitle('Số hiệu tuyến xe buýt đang khảo sát')
      .setHelpText('Ví dụ: Tuyến 74, Tuyến 13, Tuyến 70-1...')
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('Hướng di chuyển')
      .setChoiceValues(['Lượt đi', 'Lượt về'])
      .setRequired(true);

  form.addTextItem()
      .setTitle('LineRoute')
      .setHelpText('Mã tuyến và hướng. Ví dụ: 74_LuotDi, 13_LuotVe...');

  form.addTextItem()
      .setTitle('Vehicle Journey / Trip ID')
      .setHelpText('Mã chuyến xe (bỏ trống nếu chưa có)');

  form.addTimeItem()
      .setTitle('Giờ xe chạy theo lịch (Scheduled Time)')
      .setHelpText('Bỏ trống nếu không có thông tin lịch trình');

  form.addTimeItem()
      .setTitle('Giờ xe chạy thực tế (Actual Time)')
      .setHelpText('Bỏ trống nếu chưa đến giờ xuất phát');

  form.addTextItem()
      .setTitle('Mã hóa / Kiểm tra (QC)')
      .setHelpText('Dành cho Giám sát viên kiểm tra (bỏ trống nếu chưa có)');

  // ==========================================================================
  // PHẦN A: THÔNG TIN CHUYẾN ĐI (OD VÀ HÀNH TRÌNH PTCC)
  // ==========================================================================
  form.addSectionHeaderItem().setTitle('PHẦN A: THÔNG TIN CHUYẾN ĐI (OD VÀ HÀNH TRÌNH PTCC)');

  form.addTextItem()
      .setTitle('1a. Bạn đang chờ xe buýt nào? Số tuyến')
      .setHelpText('Ghi số hiệu tuyến hành khách đang chờ. Ví dụ: 74')
      .setRequired(true);

  form.addTextItem()
      .setTitle('1b. Điểm dự kiến xuống')
      .setHelpText('Ghi tên trạm dừng hoặc địa điểm hành khách dự kiến sẽ bước xuống xe')
      .setRequired(true);

  form.addTextItem()
      .setTitle('1c. Stop ID điểm xuống')
      .setHelpText('Mã trạm điểm xuống (bỏ trống nếu chưa xác định)');

  // Mục đích gốc (8 mã chuẩn)
  var mucDichList7B = [
    '1 Nhà ở',
    '2 Công việc',
    '3 Kinh doanh',
    '4 Giáo dục',
    '5 Mua sắm',
    '6 Giải trí',
    '7 Thăm người thân',
    '8 Khác'
  ];

  // Câu 2: Xuất phát O
  form.addSectionHeaderItem().setTitle('2. ĐIỂM XUẤT PHÁT THỰC TẾ TRƯỚC KHI TỚI ĐIỂM DỪNG NÀY');

  form.addTextItem()
      .setTitle('2a. Điểm xuất phát: Đường / Khu phố')
      .setHelpText('Ví dụ: Số 123 Lê Lợi')
      .setRequired(true);

  form.addTextItem()
      .setTitle('2a. Điểm xuất phát: Phường / Xã')
      .setRequired(true);

  form.addTextItem()
      .setTitle('2a. Điểm xuất phát: Thành phố / Tỉnh')
      .setRequired(true);

  form.addTextItem()
      .setTitle('2a. Mã vùng / TAZ xuất phát')
      .setHelpText('Bỏ trống nếu chưa xác định');

  form.addMultipleChoiceItem()
      .setTitle('2b. Mục đích tại nơi xuất phát')
      .setChoiceValues(mucDichList7B)
      .setRequired(true);

  // Câu 3: Điểm đến D
  form.addSectionHeaderItem().setTitle('3. ĐIỂM ĐẾN CUỐI CÙNG CỦA CHUYẾN ĐI');

  form.addTextItem()
      .setTitle('3a. Điểm đến cuối cùng: Đường / Khu phố')
      .setHelpText('Ví dụ: 456 Quốc lộ 22')
      .setRequired(true);

  form.addTextItem()
      .setTitle('3a. Điểm đến cuối cùng: Phường / Xã')
      .setRequired(true);

  form.addTextItem()
      .setTitle('3a. Điểm đến cuối cùng: Thành phố / Tỉnh')
      .setRequired(true);

  form.addTextItem()
      .setTitle('3a. Mã vùng / TAZ điểm đến')
      .setHelpText('Bỏ trống nếu chưa xác định');

  form.addMultipleChoiceItem()
      .setTitle('3b. Mục đích tại nơi đến')
      .setChoiceValues(mucDichList7B)
      .setRequired(true);

  // Câu 4: Tiếp cận điểm lên xe
  form.addSectionHeaderItem().setTitle('4. TIẾP CẬN ĐIỂM LÊN XE');

  form.addMultipleChoiceItem()
      .setTitle('4. Tiếp cận điểm lên xe bằng phương thức nào?')
      .setChoiceValues([
        'Đi bộ/xe đạp',
        'Xe máy',
        'Ô tô',
        'Taxi/Grab',
        'Xe buýt khác',
        'Khác'
      ])
      .setRequired(true);

  form.addTextItem()
      .setTitle('4. Thời gian tiếp cận (phút)')
      .setHelpText('Thời gian đi từ điểm xuất phát đến điểm dừng xe buýt. Ví dụ: 5, 10, 15')
      .setRequired(true);

  form.addTextItem()
      .setTitle('4. Chi phí tiếp cận (VNĐ)')
      .setHelpText('Chi phí đi đến điểm dừng. Ghi 0 nếu đi bộ/miễn phí')
      .setRequired(true);

  form.addTimeItem()
      .setTitle('4. Giờ đến điểm dừng')
      .setHelpText('Ví dụ: 07:15')
      .setRequired(true);

  form.addTextItem()
      .setTitle('4. Thời gian chờ thực tế tại điểm dừng (phút)')
      .setHelpText('Số phút đã/đang đứng chờ xe buýt. Ví dụ: 10, 20')
      .setRequired(true);

  // Câu 5: Rời điểm xuống đến điểm cuối
  form.addSectionHeaderItem().setTitle('5. RỜI ĐIỂM XUỐNG ĐẾN ĐIỂM ĐẾN CUỐI CÙNG');

  form.addMultipleChoiceItem()
      .setTitle('5. Từ điểm xuống xe buýt đến đích cuối cùng, bạn đi bằng gì?')
      .setChoiceValues([
        'Đi bộ/xe đạp',
        'Xe máy',
        'Ô tô',
        'Taxi/Grab',
        'Xe buýt khác',
        'Khác'
      ])
      .setRequired(true);

  form.addTextItem()
      .setTitle('5. Thời gian rời trạm đến đích (phút)')
      .setHelpText('Ví dụ: 5, 10, 15')
      .setRequired(true);

  form.addTextItem()
      .setTitle('5. Chi phí rời trạm đến đích (VNĐ)')
      .setHelpText('Ghi 0 nếu đi bộ/miễn phí')
      .setRequired(true);

  // Câu 6: Chặng xe buýt đang khảo sát
  form.addSectionHeaderItem().setTitle('6. CHẶNG XE BUÝT ĐANG KHẢO SÁT');

  form.addTextItem()
      .setTitle('6. Thời gian trên xe (phút)')
      .setHelpText('Thời gian dự kiến ngồi trên chuyến xe buýt này. Ví dụ: 25, 40')
      .setRequired(true);

  form.addTextItem()
      .setTitle('6. Giá vé (VNĐ)')
      .setHelpText('Tiền vé đã trả cho tuyến này. Ví dụ: 6000, 7000')
      .setRequired(true);

  form.addTimeItem()
      .setTitle('6. Giờ đến điểm xuống dự kiến')
      .setHelpText('Ví dụ: 08:15')
      .setRequired(true);

  // Chuyển tuyến & Chặng PTCC
  form.addSectionHeaderItem().setTitle('CÁC CHẶNG CHUYỂN TUYẾN PTCC (NẾU CÓ)');

  form.addTextItem()
      .setTitle('Chặng PTCC 1: Tuyến/Mode, Điểm chuyển/Stop ID, Ghi chú')
      .setHelpText('Ví dụ: Tuyến 74, BX Củ Chi, Đi thẳng');

  form.addTextItem()
      .setTitle('Chặng PTCC 2: Tuyến/Mode, Điểm chuyển/Stop ID, Ghi chú')
      .setHelpText('Bỏ trống nếu không có');

  form.addTextItem()
      .setTitle('Chặng PTCC 3: Tuyến/Mode, Điểm chuyển/Stop ID, Ghi chú')
      .setHelpText('Bỏ trống nếu không có');

  form.addTextItem()
      .setTitle('7. Chuyển tuyến trong TOÀN BỘ chuyến đi: Số lần chuyển')
      .setHelpText('Nhập số: 0 (đi 1 tuyến thẳng), 1, 2, 3...')
      .setRequired(true);

  form.addTextItem()
      .setTitle('8. Tổng thời gian door-to-door dự kiến (phút)')
      .setHelpText('Tổng thời gian từ cửa nhà đến đích cuối cùng. Ví dụ: 45, 60')
      .setRequired(true);

  form.addTextItem()
      .setTitle('8. Tổng chi phí chuyến đi (VNĐ)')
      .setHelpText('Tổng cộng tất cả các chi phí vé + tiếp cận. Ví dụ: 7000, 15000')
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('9. Tần suất thực hiện chuyến đi này')
      .setChoiceValues([
        '≥5 lần/tuần',
        '3–4 lần/tuần',
        '1–2 lần/tuần',
        '<1 lần/tuần'
      ])
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('10. Xe cá nhân có thể sử dụng cho chuyến này')
      .setChoiceValues([
        'Không',
        'Xe máy',
        'Ô tô',
        'Cả hai'
      ])
      .setRequired(true);

  // ==========================================================================
  // PHẦN B: ĐÁNH GIÁ DỊCH VỤ XE BUÝT HIỆN TẠI (CÂU 11)
  // ==========================================================================
  form.addSectionHeaderItem().setTitle('PHẦN B: ĐÁNH GIÁ DỊCH VỤ XE BUÝT HIỆN TẠI');

  var gridItem = form.addGridItem()
      .setTitle('11. Đánh giá dịch vụ xe buýt hiện tại (1 = Rất kém / Rất không hài lòng; 5 = Rất tốt / Rất hài lòng)')
      .setRows([
        'Độ tin cậy',
        'Tần suất/headway',
        'Thời gian đi lại',
        'Thời gian chờ',
        'Sự thoải mái',
        'An toàn',
        'Giá vé'
      ])
      .setColumns(['1', '2', '3', '4', '5'])
      .setRequired(true);

  // ==========================================================================
  // PHẦN C: THÔNG TIN CÁ NHÂN
  // ==========================================================================
  form.addSectionHeaderItem().setTitle('PHẦN C: THÔNG TIN CÁ NHÂN');

  form.addMultipleChoiceItem()
      .setTitle('12. Giới tính')
      .setChoiceValues(['Nam', 'Nữ', 'Khác/không trả lời'])
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('13. Tuổi')
      .setChoiceValues(['<20', '20–29', '30–39', '40–49', '50–59', '≥60'])
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('14. Nghề nghiệp')
      .setChoiceValues([
        'Có việc làm',
        'Tự kinh doanh',
        'Sinh viên',
        'Nội trợ',
        'Nghỉ hưu'
      ])
      .showOtherOption(true) // 'Khác ______'
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('15. Chi tiêu giao thông thông thường/ngày')
      .setChoiceValues([
        '0',
        '<10k',
        '10–<20k',
        '20–<30k',
        '30–<50k',
        '50–<100k',
        '≥100k VNĐ'
      ])
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('16. Thu nhập cá nhân/tháng')
      .setChoiceValues([
        '<5tr',
        '5–<8tr',
        '8–<12tr',
        '12–<20tr',
        '20–<30tr',
        '30–<50tr',
        '≥50tr',
        'Không trả lời'
      ])
      .setRequired(true);

  // ==========================================================================
  // PHẦN D: PHƯƠNG THỨC VẬN CHUYỂN BẰNG METRO TRONG TƯƠNG LAI
  // ==========================================================================
  form.addSectionHeaderItem().setTitle('PHẦN D: PHƯƠNG THỨC VẬN CHUYỂN BẰNG ĐƯỜNG SẮT ĐÔ THỊ (METRO) TRONG TƯƠNG LAI');

  form.addCheckboxItem()
      .setTitle('17. Nếu không thể sử dụng phương tiện hiện tại, bạn có thể sử dụng phương tiện nào khác khi di chuyển từ điểm đầu đến điểm cuối hành trình?')
      .setChoiceValues([
        'Xe hơi riêng',
        'Đi bộ',
        'Đạp xe đạp',
        'Xe ôm/Xe máy công nghệ (Grab)',
        'Taxi/Taxi công nghệ (Grab)',
        'Xe máy',
        'Đường sắt đô thị (Metro)',
        'Xe khác'
      ])
      .setRequired(true);

  form.addSectionHeaderItem()
      .setTitle('GIỚI THIỆU PHƯƠNG THỨC VẬN TẢI METRO')
      .setHelpText(
        'Metro là một hệ thống vận tải đường sắt nội thành với khả năng chuyên chở lớn và thường xuyên. ' +
        'Phương thức vận tải Metro có thể được xây dựng ở dưới mặt đất hoặc ở trên không và vận tốc trung bình là khoảng từ 30-40 km/h.'
      );

  // Câu 18: SP (Stated Preference) — 4 Kịch bản neo để nội suy mô hình Binary Logit
  form.addSectionHeaderItem()
      .setTitle('18. KỊCH BẢN LỰA CHỌN CHUYỂN SANG METRO (SP EXPERIMENT)')
      .setHelpText('Giả định rằng hệ thống Metro đã xây dựng xong và bạn có thể sử dụng các trạm Metro gần nhà. Bạn có chuyển sang Metro với các kịch bản sau không?');

  form.addMultipleChoiceItem()
      .setTitle('Kịch bản 1: Giá vé 7.000 VNĐ | Thời gian GIẢM 15 phút (Đi rất nhanh)')
      .setChoiceValues(['1. Có (Chuyển sang Metro)', '2. Không (Giữ phương tiện hiện tại)'])
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('Kịch bản 2: Giá vé 7.000 VNĐ | Thời gian BẰNG hiện tại (0 phút)')
      .setChoiceValues(['1. Có (Chuyển sang Metro)', '2. Không (Giữ phương tiện hiện tại)'])
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('Kịch bản 3: Giá vé 25.000 VNĐ | Thời gian GIẢM 15 phút (Đi rất nhanh)')
      .setChoiceValues(['1. Có (Chuyển sang Metro)', '2. Không (Giữ phương tiện hiện tại)'])
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('Kịch bản 4: Giá vé 25.000 VNĐ | Thời gian BẰNG hiện tại (0 phút)')
      .setChoiceValues(['1. Có (Chuyển sang Metro)', '2. Không (Giữ phương tiện hiện tại)'])
      .setRequired(true);

  // ==========================================================================
  // CÂU 19: PHÂN 4 BLOCK CỰ LY TIẾP CẬN GA METRO (ĐIỀU HƯỚNG TỰ ĐỘNG)
  // ==========================================================================
  form.addSectionHeaderItem().setTitle(
    '19. PHƯƠNG TIỆN TIẾP CẬN GA METRO THEO KHOẢNG CÁCH\n' +
    'Giả định Metro đã hoạt động, bạn sẽ dùng phương tiện gì để đi đến trạm Metro và từ trạm Metro đến điểm cuối?'
  );

  var itemBlockChoice = form.addMultipleChoiceItem()
      .setTitle('Mã Block Khảo sát Q19 (Hệ thống tự động phân phối)')
      .setHelpText('⚠️ KSV: Chọn đúng Block hiển thị trên màn hình Trợ Lý Định Vị rồi bấm TIẾP')
      .setRequired(true);

  var vehicles7B = [
    '1: Xe hơi riêng',
    '2: Đi bộ',
    '3: Xe đạp',
    '4: Xe ôm / Xe máy công nghệ',
    '5: Taxi / Taxi công nghệ',
    '6: Xe máy',
    '8: Xe buýt',
    '9: Khác'
  ];

  // PAGE END — Trang kết thúc phỏng vấn
  var pageEndForm = form.addPageBreakItem().setTitle('HOÀN THÀNH PHỎNG VẤN 7B');

  // BLOCK 1: (0-150m, 150-300m)
  var pageBlock1 = form.addPageBreakItem().setTitle('Q19. PHƯƠNG TIỆN TIẾP CẬN GA METRO (BLOCK 1)');
  addDistanceGroup7B(form, ['0-150m', '150m-300m'], vehicles7B);
  pageBlock1.setGoToPage(pageEndForm);

  // BLOCK 2: (300m-450m, 450-600m)
  var pageBlock2 = form.addPageBreakItem().setTitle('Q19. PHƯƠNG TIỆN TIẾP CẬN GA METRO (BLOCK 2)');
  addDistanceGroup7B(form, ['300m-450m', '450m-600m'], vehicles7B);
  pageBlock2.setGoToPage(pageEndForm);

  // BLOCK 3: (450m-600m, 600m-1000m) — 450-600m là nút mỏ neo trùng lặp
  var pageBlock3 = form.addPageBreakItem().setTitle('Q19. PHƯƠNG TIỆN TIẾP CẬN GA METRO (BLOCK 3)');
  addDistanceGroup7B(form, ['450m-600m', '600m-1000m'], vehicles7B);
  pageBlock3.setGoToPage(pageEndForm);

  // BLOCK 4: (1000m-2000m, 2000m-3000m)
  var pageBlock4 = form.addPageBreakItem().setTitle('Q19. PHƯƠNG TIỆN TIẾP CẬN GA METRO (BLOCK 4)');
  addDistanceGroup7B(form, ['1000m-2000m', '2000m-3000m'], vehicles7B);
  pageBlock4.setGoToPage(pageEndForm);

  // CẤU HÌNH ĐIỀU HƯỚNG DỰA TRÊN LỰA CHỌN BLOCK
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
  Logger.log(" ĐÃ TẠO THÀNH CÔNG PHIẾU 7B: HÀNH KHÁCH XE BUÝT TẠI TRẠM (MRT2 & MRT2S)!");
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
// HÀM TẠO NHÓM CÂU HỎI THEO CỰ LY (CHO BLOCK Q19 PHIẾU 7B) — HỘP KIỂM CHỌN NHIỀU
// ==============================================================================
function addDistanceGroup7B(form, distances, vehicles) {
  // Q19.1: Từ nhà → Ga Metro
  form.addSectionHeaderItem().setTitle('■ Từ nhà đến trạm Metro');
  distances.forEach(function(dist) {
    form.addCheckboxItem()
        .setTitle('Khoảng cách [' + dist + '] - Phương tiện di chuyển')
        .setHelpText('Giả sử có trạm Metro cách nhà ' + dist + ', anh/chị sẽ đi đến trạm bằng gì?')
        .setChoiceValues(vehicles)
        .setRequired(true);
  });

  // Q19.2: Từ ga Metro → Điểm cuối hành trình
  form.addSectionHeaderItem().setTitle('■ Từ nhà ga Metro đến điểm cuối của hành trình');
  distances.forEach(function(dist) {
    form.addCheckboxItem()
        .setTitle('Khoảng cách [' + dist + '] - Phương tiện di chuyển')
        .setHelpText('Khi xuống ga Metro cách điểm cuối ' + dist + ', anh/chị sẽ đi tiếp bằng gì?')
        .setChoiceValues(vehicles)
        .setRequired(true);
  });
}
