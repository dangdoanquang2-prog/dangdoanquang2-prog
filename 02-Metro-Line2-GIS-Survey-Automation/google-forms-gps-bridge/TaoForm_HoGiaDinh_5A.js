// ==============================================================================================
// DỰ ÁN: KHẢO SÁT NHU CẦU ĐI LẠI HỘ GIA ĐÌNH / CÁ NHÂN XUNG QUANH GA METRO MRT2S (BÁN KÍNH 1000M)
// TÀI LIỆU CĂN CỨ: NHIEM VU 5A PHONG VAN HO GIA DINH-R1000m.docx
// PHIÊN BẢN: v2 — Đã hiệu chỉnh SP 4 pivot + Block phân nhánh Q20 theo chuẩn formkhaosat
// ==============================================================================================
//
// HƯỚNG DẪN SỬ DỤNG NHANH:
// 1. Mở trình duyệt, truy cập: https://script.google.com và bấm "Dự án mới" (New project).
// 2. Xóa toàn bộ nội dung mặc định trong file Mã.gs (Code.gs), dán toàn bộ mã nguồn này vào.
// 3. Tại thanh công cụ bên trên, chọn hàm "taoFormHoGiaDinh5A" và bấm "Chạy" (Run).
// 4. Cấp quyền truy cập Google Form cho Script khi được hỏi.
// 5. Mở tab "Nhật ký thực thi" (Execution Log) để lấy link Form và các Entry ID.
// 6. (Tùy chọn WebBridge GPS): Triển khai Web App để KSV tự động bắt GPS + xoay tua Block.
// ==============================================================================================

function taoFormHoGiaDinh5A() {
  var form = FormApp.create('PHIẾU 5A: KHẢO SÁT NHU CẦU ĐI LẠI HỘ GIA ĐÌNH / CÁ NHÂN (MRT2S - R1000M)');
  
  form.setDescription(
    'KHẢO SÁT NHU CẦU ĐI LẠI HỘ GIA ĐÌNH / CÁ NHÂN XUNG QUANH GA ĐƯỜNG SẮT MRT2S – BÁN KÍNH 1000M\n\n' +
    '* Lưu ý KSV: Chụp ảnh có địa chỉ, tọa độ nhà dân được khảo sát làm minh chứng.\n' +
    '* Ghi nhận toàn bộ chuyến đi của NGÀY HÔM QUA của người được chọn, kể cả đi bộ, đưa/đón, về nhà và các chuyến ngắn.\n' +
    '* Không giới hạn số chuyến. Phiếu có 4 bản ghi chuyến đi.\n' +
    '* Thông tin chỉ phục vụ nghiên cứu phát triển mạng lưới Metro và được bảo mật tuyệt đối.'
  );
  form.setConfirmationMessage('Cảm ơn Quý hộ gia đình và Anh/Chị đã hoàn thành phiếu phỏng vấn khảo sát giao thông Metro 2!');

  // ==========================================================================
  // PHẦN 0: ĐỊNH VỊ VÀ KIỂM SOÁT MẪU
  // ==========================================================================
  form.addSectionHeaderItem().setTitle('0. ĐỊNH VỊ & KIỂM SOÁT MẪU KHẢO SÁT');

  var itemGps = form.addTextItem()
      .setTitle('Tọa độ GPS nhà dân (Kinh độ, Vĩ độ)')
      .setHelpText('Hệ thống WebBridge tự động điền từ GPS điện thoại KSV. Có thể sửa lại nếu cần.')
      .setRequired(true);

  var itemAddress = form.addTextItem()
      .setTitle('Địa chỉ khảo sát thực tế (Số nhà, Đường, Phường/Xã, Quận/Huyện, Tỉnh/TP)')
      .setHelpText('Hệ thống tự động tra cứu từ bản đồ số. KSV đối soát và nhập chính xác số nhà thực tế.')
      .setRequired(true);

  form.addTextItem()
      .setTitle('Mã hộ gia đình (HH_ID)')
      .setHelpText('Quy ước: Mã ga + Số thứ tự hộ. Ví dụ: S23_HH001, S23_HH002...')
      .setRequired(true);

  form.addTextItem()
      .setTitle('Mã cá nhân người trả lời (P_ID)')
      .setHelpText('Quy ước: P01, P02... tương ứng với số thứ tự thành viên trong hộ')
      .setRequired(true);

  form.addTextItem()
      .setTitle('Họ tên / Mã điều tra viên (KSV)')
      .setHelpText('Nhập mã số KSV được cấp. Ví dụ: DTV01, DTV02...')
      .setRequired(true);

  form.addDateItem()
      .setTitle('Ngày phỏng vấn')
      .setRequired(true);

  form.addDateItem()
      .setTitle('Ngày nhật ký hành trình (Ngày hôm qua)')
      .setHelpText('Ngày thực hiện các chuyến đi được ghi nhận trong phiếu')
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('Loại ngày của nhật ký hành trình')
      .setChoiceValues([
        'Ngày thường (Thứ Hai đến Thứ Sáu)',
        'Thứ Bảy',
        'Chủ Nhật / Ngày lễ'
      ])
      .setRequired(true);

  form.addTextItem()
      .setTitle('Tên ga MRT2S mục tiêu (Trong bán kính 1000m)')
      .setHelpText('Ví dụ: Ga Ba Sa (S23), Ga Củ Chi (S24), Ga An Hạ (S22)...')
      .setRequired(true);

  // ==========================================================================
  // PHẦN I: ĐẶC ĐIỂM HỘ GIA ĐÌNH
  // ==========================================================================
  form.addSectionHeaderItem().setTitle('I. ĐẶC ĐIỂM HỘ GIA ĐÌNH');

  form.addTextItem()
      .setTitle('1a. Quy mô hộ: Tổng số nhân khẩu sống chung trong hộ')
      .setHelpText('Nhập số nguyên. Ví dụ: 4, 5')
      .setRequired(true);

  form.addTextItem()
      .setTitle('1b. Số người từ 6 tuổi trở lên')
      .setHelpText('Nhập số nguyên. Ví dụ: 3, 4')
      .setRequired(true);

  form.addTextItem()
      .setTitle('1c. Số người đang đi làm')
      .setHelpText('Nhập số người có thu nhập/việc làm trong hộ')
      .setRequired(true);

  form.addTextItem()
      .setTitle('1d. Số học sinh / sinh viên trong hộ')
      .setHelpText('Nhập số lượng đang đi học')
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('2. Tổng thu nhập hộ gia đình hàng tháng')
      .setChoiceValues([
        '< 10 triệu VNĐ',
        '10 – 20 triệu VNĐ',
        '20 – 30 triệu VNĐ',
        '30 – 50 triệu VNĐ',
        '50 – 80 triệu VNĐ',
        '> 80 triệu VNĐ',
        'Không trả lời'
      ])
      .setRequired(true);

  form.addTextItem()
      .setTitle('3a. Số lượng Ô TÔ hộ gia đình sở hữu')
      .setHelpText('Nhập số lượng xe. Ghi 0 nếu không có.')
      .setRequired(true);

  form.addTextItem()
      .setTitle('3b. Số lượng XE MÁY hộ gia đình sở hữu')
      .setHelpText('Nhập số lượng xe. Ghi 0 nếu không có.')
      .setRequired(true);

  form.addTextItem()
      .setTitle('3c. Số lượng XE ĐẠP truyền thống sở hữu')
      .setHelpText('Nhập số lượng xe. Ghi 0 nếu không có.')
      .setRequired(true);

  form.addTextItem()
      .setTitle('3d. Số lượng XE ĐẠP ĐIỆN / XE MÁY ĐIỆN sở hữu')
      .setHelpText('Nhập số lượng xe. Ghi 0 nếu không có.')
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('4a. Chỗ đỗ ô tô tại nơi ở')
      .setChoiceValues([
        'Có chỗ đỗ riêng trong nhà/khuôn viên',
        'Có chỗ gửi/đỗ xe ngoài trời lân cận',
        'Không có chỗ đỗ',
        'Không áp dụng (Hộ không sở hữu ô tô)'
      ])
      .setRequired(true);

  form.addTextItem()
      .setTitle('4b. Chi phí đỗ/gửi xe ô tô hàng tháng (VNĐ)')
      .setHelpText('Ghi số tiền (Ví dụ: 1500000). Ghi 0 nếu đỗ miễn phí hoặc không áp dụng.');

  form.addMultipleChoiceItem()
      .setTitle('5. Loại hình nhà ở của hộ gia đình')
      .setChoiceValues([
        'Nhà riêng / nhà phố liền kề',
        'Căn hộ chung cư',
        'Nhà trọ / phòng thuê',
        'Ký túc xá / tập thể'
      ])
      .showOtherOption(true)
      .setRequired(true);

  form.addTextItem()
      .setTitle('6. Số lượng vé tháng / thẻ phương tiện công cộng (Xe buýt, Metro) đang dùng trong hộ')
      .setHelpText('Nhập số lượng vé/thẻ. Ghi 0 nếu không có ai sử dụng.')
      .setRequired(true);

  // ==========================================================================
  // PHẦN II: DANH SÁCH THÀNH VIÊN HỘ GIA ĐÌNH
  // ==========================================================================
  form.addSectionHeaderItem()
      .setTitle('II. DANH SÁCH THÀNH VIÊN HỘ GIA ĐÌNH')
      .setHelpText('Ghi nhận tất cả thành viên sống chung trong hộ. TV1 là Chủ hộ/Đại diện, các thành viên tiếp theo bỏ qua nếu hộ ít người.');

  themThongTinThanhVien(form, 1, true);
  themThongTinThanhVien(form, 2, false);
  themThongTinThanhVien(form, 3, false);
  themThongTinThanhVien(form, 4, false);
  themThongTinThanhVien(form, 5, false);
  themThongTinThanhVien(form, 6, false);

  // ==========================================================================
  // PHẦN III: THÔNG TIN NGƯỜI ĐƯỢC CHỌN PHỎNG VẤN (NGƯỜI GHI NHẬT KÝ)
  // ==========================================================================
  form.addSectionHeaderItem().setTitle('III. THÔNG TIN NGƯỜI ĐƯỢC CHỌN (GHI NHẬT KÝ CHUYẾN ĐI)');

  form.addTextItem()
      .setTitle('7a. Tuổi của người trả lời')
      .setHelpText('Ví dụ: 28, 35, 52')
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('7b. Giới tính')
      .setChoiceValues(['Nam', 'Nữ', 'Khác / Không trả lời'])
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('8. Nghề nghiệp chính hiện tại')
      .setChoiceValues([
        'Quản lý / Lãnh đạo',
        'Văn phòng / Chuyên viên / Giáo viên',
        'Công nhân / Lao động kỹ thuật',
        'Kinh doanh / Buôn bán',
        'Lái xe / Nhân viên giao vận',
        'Dịch vụ / Nhà hàng / Khách sạn',
        'Học sinh / Sinh viên',
        'Nội trợ / Hưu trí / Tự do'
      ])
      .showOtherOption(true)
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('9. Giấy phép lái xe (GPLX)')
      .setChoiceValues([
        'Chỉ có GPLX Xe máy',
        'Chỉ có GPLX Ô tô',
        'Có cả hai (Xe máy & Ô tô)',
        'Không có GPLX'
      ])
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('10a. Anh/chị có sẵn xe Ô TÔ riêng để tự do sử dụng không?')
      .setChoiceValues(['Có', 'Không'])
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('10b. Anh/chị có sẵn XE MÁY riêng để tự do sử dụng không?')
      .setChoiceValues(['Có', 'Không'])
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('11. Mức thu nhập cá nhân hàng tháng')
      .setChoiceValues([
        '< 3 triệu VNĐ',
        '3 – 6 triệu VNĐ',
        '6 – 10 triệu VNĐ',
        '10 – 15 triệu VNĐ',
        '15 – 30 triệu VNĐ',
        '30 – 50 triệu VNĐ',
        '> 50 triệu VNĐ',
        'Không trả lời'
      ])
      .setRequired(true);

  form.addTextItem()
      .setTitle('12a. Nơi làm việc / Học tập thường xuyên (Tên cơ quan, Địa chỉ chi tiết)')
      .setHelpText('Ghi rõ: Tên công ty/trường, Số nhà, Đường, Phường/Xã, Quận/Huyện')
      .setRequired(true);

  form.addTextItem()
      .setTitle('12b. Mã TAZ hoặc Tọa độ GPS nơi làm việc/học tập (nếu xác định được)')
      .setHelpText('Gợi ý: Tra bảng TAZ hoặc bỏ trống nếu chưa có');

  form.addTextItem()
      .setTitle('13a. Số ngày có mặt làm việc/học tập tại cơ quan trong tuần')
      .setHelpText('Ví dụ: 5 ngày/tuần, 6 ngày/tuần')
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('13b. Ngày hôm qua anh/chị có làm việc / học tập từ xa tại nhà không?')
      .setChoiceValues([
        'Có (Làm việc/học online tại nhà hoàn toàn)',
        'Không (Có đi đến cơ quan hoặc đi ra ngoài)'
      ])
      .setRequired(true);

  // ==========================================================================
  // PHẦN IV: TỔNG QUAN NGÀY NHẬT KÝ
  // ==========================================================================
  form.addSectionHeaderItem().setTitle('IV. TỔNG QUAN NGÀY NHẬT KÝ (24 GIỜ QUA)');

  form.addMultipleChoiceItem()
      .setTitle('14. Ngày hôm qua anh/chị có ra khỏi nhà không?')
      .setChoiceValues(['Có', 'Không'])
      .setRequired(true);

  form.addTextItem()
      .setTitle('15. Tổng số chuyến đi đã thực hiện trong ngày hôm qua')
      .setHelpText('Tính tất cả các lần đi lại (kể cả đi bộ, đưa đón, đi chợ, về nhà). Nhập số: 1, 2, 3, 4...')
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('16. Lý do không ra khỏi nhà (Nếu câu 14 chọn KHÔNG)')
      .setChoiceValues([
        'Làm việc / học trực tuyến tại nhà',
        'Bị ốm / điều trị bệnh',
        'Ngày nghỉ / không có việc cần đi',
        'Thời tiết xấu (mưa bão/ngập)',
        'Không có nhu cầu đi lại',
        'Không áp dụng (Có ra khỏi nhà)'
      ])
      .showOtherOption(true);

  form.addMultipleChoiceItem()
      .setTitle('17. Phương thức di chuyển thường ngày hay sử dụng nhất')
      .setChoiceValues([
        'Xe máy cá nhân',
        'Xe hơi cá nhân',
        'Xe đạp',
        'Xe đạp điện',
        'Đi bộ',
        'Xe buýt đô thị',
        'Xe ôm / Xe máy công nghệ (GrabBike, BeBike...)',
        'Taxi / Ô tô công nghệ (GrabCar, Xanh SM, Taxi...)',
        'Tàu điện Metro'
      ])
      .showOtherOption(true)
      .setRequired(true);

  // ==========================================================================
  // PHẦN V: NHẬT KÝ CHUYẾN ĐI 24 GIỜ (4 CHUYẾN ĐI)
  // ==========================================================================
  themCauHoiChuyenDi(form, 1, true);
  themCauHoiChuyenDi(form, 2, false);
  themCauHoiChuyenDi(form, 3, false);
  themCauHoiChuyenDi(form, 4, false);

  // ==========================================================================
  // PHẦN VI: PHƯƠNG THỨC ĐƯỜNG SẮT ĐÔ THỊ (METRO) TRONG TƯƠNG LAI
  // ==========================================================================
  form.addSectionHeaderItem()
      .setTitle('VI. PHƯƠNG THỨC VẬN CHUYỂN BẰNG ĐƯỜNG SẮT ĐÔ THỊ (METRO)')
      .setHelpText(
        'Metro là một hệ thống vận tải đường sắt nội thành với khả năng chuyên chở lớn và thường xuyên. ' +
        'Phương thức vận tải Metro có thể được xây dựng ở dưới mặt đất hoặc ở trên không và vận tốc trung bình ' +
        'của phương thức vận tải Metro là khoảng từ 30-40 km/h.'
      );

  // ===================== CÂU 18: ƯỚC TÍNH PHƯƠNG TIỆN KHÁC (CHUẨN FORM KHẢO SÁT) =====================
  form.addCheckboxItem()
      .setTitle('18. Nếu anh/chị đi từ điểm xuất phát đến điểm đến bằng các phương tiện khác, ước tính thời gian và chi phí:')
      .setHelpText('Tích chọn tất cả các phương tiện anh/chị có thể sử dụng (Thời gian và chi phí sẽ được tính toán tự động bằng mô hình)')
      .setChoiceValues([
        '1. Xe hơi riêng',
        '2. Đi bộ',
        '3. Đạp xe đạp',
        '4. Xe ôm / Xe máy công nghệ (Grab)',
        '5. Taxi / Taxi công nghệ (Grab)',
        '6. Xe máy',
        '7. Xe buýt',
        '8. Đường sắt đô thị (Metro)',
        '9. Xe khác'
      ])
      .setRequired(true);

  // ===================== CÂU 19: SP PIVOT — 4 KỊCH BẢN NỘI SUY =====================
  form.addGridItem()
      .setTitle('19. Giả định Metro đã hoạt động, anh/chị có chọn chuyển sang Metro không?')
      .setHelpText(
        'Giả định hệ thống Metro đã hoàn thành và có trạm Metro gần nhà bạn.\n' +
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
    '20. PHƯƠNG TIỆN & CHI PHÍ TIẾP CẬN GA METRO THEO KHOẢNG CÁCH\n' +
    'Giả định Metro đã hoạt động, bạn sẽ dùng phương tiện gì để đi đến trạm Metro và từ trạm Metro đến điểm cuối?'
  );

  var itemBlockChoice = form.addMultipleChoiceItem()
      .setTitle('Mã Block Khảo sát Q20 (Hệ thống tự động phân phối)')
      .setHelpText('⚠️ KSV: Chọn đúng Block hiển thị trên màn hình Trợ Lý Định Vị rồi bấm TIẾP')
      .setRequired(true);

  var vehicles = ['1: Xe hơi riêng', '2: Đi bộ', '3: Xe đạp', '4: Xe ôm/xe máy công nghệ', '5: Taxi/Taxi công nghệ', '6: Xe máy', '8: Xe buýt', '9: Khác'];

  // PAGE END — Trang kết thúc phỏng vấn (tất cả Block nhảy về đây)
  var pageEndForm = form.addPageBreakItem().setTitle('HOÀN THÀNH PHỎNG VẤN');

  // BLOCK 1: (0-150m, 150m-300m)
  var pageBlock1 = form.addPageBreakItem().setTitle('Q20. PHƯƠNG TIỆN VÀ CHI PHÍ TIẾP CẬN GA METRO (BLOCK 1)');
  addDistanceGroup(form, ['0-150m', '150m-300m'], vehicles);
  pageBlock1.setGoToPage(pageEndForm);

  // BLOCK 2: (300m-450m, 450m-600m)
  var pageBlock2 = form.addPageBreakItem().setTitle('Q20. PHƯƠNG TIỆN VÀ CHI PHÍ TIẾP CẬN GA METRO (BLOCK 2)');
  addDistanceGroup(form, ['300m-450m', '450m-600m'], vehicles);
  pageBlock2.setGoToPage(pageEndForm);

  // BLOCK 3: (450m-600m, 600m-1000m) — 450-600m là nút mỏ neo trùng lặp
  var pageBlock3 = form.addPageBreakItem().setTitle('Q20. PHƯƠNG TIỆN VÀ CHI PHÍ TIẾP CẬN GA METRO (BLOCK 3)');
  addDistanceGroup(form, ['450m-600m', '600m-1000m'], vehicles);
  pageBlock3.setGoToPage(pageEndForm);

  // BLOCK 4: (1000m-2000m, 2000m-3000m)
  var pageBlock4 = form.addPageBreakItem().setTitle('Q20. PHƯƠNG TIỆN VÀ CHI PHÍ TIẾP CẬN GA METRO (BLOCK 4)');
  addDistanceGroup(form, ['1000m-2000m', '2000m-3000m'], vehicles);
  pageBlock4.setGoToPage(pageEndForm);

  // CẤU HÌNH ĐIỀU HƯỚNG TỰ ĐỘNG DỰA TRÊN LỰA CHỌN BLOCK
  itemBlockChoice.setChoices([
    itemBlockChoice.createChoice('Block 1', pageBlock1),
    itemBlockChoice.createChoice('Block 2', pageBlock2),
    itemBlockChoice.createChoice('Block 3', pageBlock3),
    itemBlockChoice.createChoice('Block 4', pageBlock4)
  ]);

  // ==========================================================================
  // TỰ ĐỘNG TRÍCH XUẤT PREFILLED PARAMETERS (ENTRY IDs)
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
  Logger.log(" ĐÃ TẠO THÀNH CÔNG PHIẾU 5A KHẢO SÁT HỘ GIA ĐÌNH (MRT2S - R1000M)!");
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
// 1. HÀM TẠO KHỐI CÂU HỎI CHO 1 THÀNH VIÊN HỘ GIA ĐÌNH (PHẦN II)
// ==============================================================================
function themThongTinThanhVien(form, i, batBuoc) {
  var header = '--- Thành viên ' + i;
  if (i === 1) {
    header += ' (Chủ hộ / Người đại diện) ---';
  } else {
    header += ' (Bỏ qua nếu hộ không có thành viên này) ---';
  }
  form.addSectionHeaderItem().setTitle(header);

  form.addTextItem()
      .setTitle('TV' + i + ': Tuổi')
      .setHelpText('Nhập số tuổi. Ví dụ: 45, 18...')
      .setRequired(batBuoc);

  form.addMultipleChoiceItem()
      .setTitle('TV' + i + ': Giới tính')
      .setChoiceValues(['Nam', 'Nữ'])
      .setRequired(batBuoc);

  form.addMultipleChoiceItem()
      .setTitle('TV' + i + ': Quan hệ với chủ hộ')
      .setChoiceValues(i === 1 ? [
        'Chủ hộ'
      ] : [
        'Vợ / Chồng',
        'Con',
        'Bố / Mẹ',
        'Anh / Chị / Em',
        'Ông / Bà / Cháu',
        'Khác'
      ])
      .setRequired(batBuoc);

  form.addMultipleChoiceItem()
      .setTitle('TV' + i + ': Nghề nghiệp chính')
      .setChoiceValues([
        'Văn phòng / Cơ quan / Chuyên viên',
        'Sản xuất / Công nhân / Lao động',
        'Kinh doanh / Buôn bán / Dịch vụ',
        'Lái xe / Nhân viên giao vận',
        'Học sinh / Sinh viên',
        'Hưu trí / Nội trợ',
        'Tự do / Khác'
      ])
      .showOtherOption(true)
      .setRequired(batBuoc);

  form.addCheckboxItem()
      .setTitle('TV' + i + ': Giấy phép lái xe, Phương tiện & Nhật ký')
      .setHelpText('Tích chọn các điều kiện ĐÚNG với thành viên này (có thể chọn nhiều)')
      .setChoiceValues([
        'Có GPLX Mô tô (Xe máy)',
        'Có GPLX Ô tô',
        'Có sẵn Ô tô / Xe máy riêng để tự do sử dụng',
        'Là người được chọn ghi nhật ký chuyến đi trong phiếu này (P_ID)'
      ]);
}

// ==============================================================================
// 2. HÀM TẠO KHỐI CÂU HỎI CHO 1 CHUYẾN ĐI (TRIP DIARY RECORD) — ĐẦY ĐỦ
// ==============================================================================
function themCauHoiChuyenDi(form, soThuTu, batBuoc) {
  var n = soThuTu;
  var req = batBuoc;
  var header = 'V. NHẬT KÝ HÀNH TRÌNH - CHUYẾN ĐI SỐ ' + n;
  if (!req) {
    header += ' (Bỏ qua nếu không có chuyến đi này)';
  }
  form.addSectionHeaderItem().setTitle(header);

  // --- Giờ đi, Giờ đến ---
  form.addTimeItem()
      .setTitle('Chuyến ' + n + ': Giờ đi')
      .setHelpText('Ví dụ: 07:15')
      .setRequired(req);

  form.addTimeItem()
      .setTitle('Chuyến ' + n + ': Giờ đến')
      .setHelpText('Ví dụ: 08:00')
      .setRequired(req);

  // --- Điểm đi (O) ---
  form.addTextItem()
      .setTitle('Chuyến ' + n + ': Địa chỉ điểm đi (O)')
      .setHelpText('Ghi số nhà, tên đường, phường/xã hoặc tên địa danh')
      .setRequired(req);

  form.addTextItem()
      .setTitle('Chuyến ' + n + ': O_TAZ')
      .setHelpText('Mã vùng giao thông điểm đi. Để trống nếu chưa xác định');

  // --- Điểm đến (D) ---
  form.addTextItem()
      .setTitle('Chuyến ' + n + ': Địa chỉ điểm đến (D)')
      .setHelpText('Ghi số nhà, tên đường, phường/xã hoặc tên địa danh')
      .setRequired(req);

  form.addTextItem()
      .setTitle('Chuyến ' + n + ': D_TAZ')
      .setHelpText('Mã vùng giao thông điểm đến. Để trống nếu chưa xác định');

  // --- Mục đích ---
  form.addMultipleChoiceItem()
      .setTitle('Chuyến ' + n + ': Mục đích chính')
      .setChoiceValues([
        '1. Đi làm', '2. Đi học', '3. Công việc', '4. Mua sắm',
        '5. Đưa/đón', '6. Giải trí/ăn uống', '7. Khám chữa bệnh',
        '8. Về nhà', '9. Khác'
      ])
      .setRequired(req);

  // --- Phương thức chính (10 loại, tách Xe đạp và Xe đạp điện) ---
  form.addMultipleChoiceItem()
      .setTitle('Chuyến ' + n + ': Phương thức di chuyển chính')
      .setChoiceValues([
        '1. Ô tô', '2. Xe máy', '3. Xe đạp', '4. Xe đạp điện',
        '5. Đi bộ', '6. Xe buýt', '7. Metro',
        '8. Taxi/Grab', '9. Xe ôm/xe máy công nghệ', '10. Khác'
      ])
      .setRequired(req);

  // --- Vai trò / Số người trên xe ---
  form.addMultipleChoiceItem()
      .setTitle('Chuyến ' + n + ': Vai trò trên phương tiện đường bộ')
      .setChoiceValues([
        'Người lái xe',
        'Hành khách',
        'Không áp dụng (Đi bộ / PTCC)'
      ]);

  form.addTextItem()
      .setTitle('Chuyến ' + n + ': Số người trên xe (kể cả người trả lời)')
      .setHelpText('Ví dụ: 1, 2, 4');

  // --- Cự ly và Thời gian (TÁCH RIÊNG 2 TRƯỜNG) ---
  form.addTextItem()
      .setTitle('Chuyến ' + n + ': Cự ly ước tính (km)')
      .setHelpText('Ví dụ: 5.5, 12, 25');

  form.addTextItem()
      .setTitle('Chuyến ' + n + ': Tổng thời gian di chuyển (phút)')
      .setHelpText('Ví dụ: 20, 35, 45');

  // --- TIẾP CẬN PTCC ---
  form.addSectionHeaderItem().setTitle('--- Thông tin PTCC cho Chuyến ' + n + ' (Bỏ qua nếu không đi PTCC) ---');

  form.addTextItem()
      .setTitle('Chuyến ' + n + ': Tiếp cận PTCC (Phương thức đến trạm, Thời gian phút, Khoảng cách mét)')
      .setHelpText('Ví dụ: Đi bộ, 5 phút, 300m');

  form.addTextItem()
      .setTitle('Chuyến ' + n + ': Thời gian chờ PTCC ban đầu (phút)')
      .setHelpText('Ví dụ: 10');

  // --- CHẶNG PTCC 1 ---
  form.addTextItem()
      .setTitle('Chuyến ' + n + ': Chặng PTCC 1 (Tuyến, Điểm lên, Điểm xuống)')
      .setHelpText('Ví dụ: Tuyến 70-1, Lên: Ngã 3 Ba Sa, Xuống: Bến xe Củ Chi');

  // --- CHẶNG PTCC 2 ---
  form.addTextItem()
      .setTitle('Chuyến ' + n + ': Chặng PTCC 2 (Tuyến, Lên, Xuống)')
      .setHelpText('Bỏ trống nếu không chuyển tuyến');

  // --- CHẶNG PTCC 3 / CHUYỂN TUYẾN ---
  form.addTextItem()
      .setTitle('Chuyến ' + n + ': Chặng PTCC 3 (Tuyến, Lên, Xuống) + Tổng số lần chuyển tuyến')
      .setHelpText('Bỏ trống nếu không có. Ghi thêm tổng số lần chuyển tuyến');

  // --- RỜI PTCC ---
  form.addTextItem()
      .setTitle('Chuyến ' + n + ': Rời PTCC (Phương thức, Thời gian phút, Khoảng cách mét)')
      .setHelpText('Ví dụ: Đi bộ, 3 phút, 200m');

  // --- CHI PHÍ BÓC TÁCH ---
  form.addTextItem()
      .setTitle('Chuyến ' + n + ': Chi phí - Giá vé (VNĐ)')
      .setHelpText('Tiền vé xe buýt, Metro... Ghi 0 nếu không có');

  form.addTextItem()
      .setTitle('Chuyến ' + n + ': Chi phí - Nhiên liệu (VNĐ)')
      .setHelpText('Tiền xăng dầu. Ghi 0 nếu không áp dụng');

  form.addTextItem()
      .setTitle('Chuyến ' + n + ': Chi phí - Đỗ xe (VNĐ)')
      .setHelpText('Phí gửi/đỗ xe. Ghi 0 nếu không có');

  form.addTextItem()
      .setTitle('Chuyến ' + n + ': Chi phí - Phí đường / Cầu đường (VNĐ)')
      .setHelpText('Phí cầu đường, BOT... Ghi 0 nếu không có');

  form.addTextItem()
      .setTitle('Chuyến ' + n + ': Chi phí - Khác (VNĐ)')
      .setHelpText('Phí phát sinh khác. Ghi 0 nếu không có');

  // --- NGƯỜI ĐI CÙNG ---
  form.addTextItem()
      .setTitle('Chuyến ' + n + ': Số người đi cùng (không tính người trả lời)')
      .setHelpText('Ví dụ: 0, 1, 2, 3');

  form.addTextItem()
      .setTitle('Chuyến ' + n + ': Trong đó số người cùng hộ gia đình')
      .setHelpText('Ví dụ: 0, 1, 2');

  // --- DỮ LIỆU / QC ---
  form.addMultipleChoiceItem()
      .setTitle('Chuyến ' + n + ': Mức độ chính xác')
      .setChoiceValues(['Chính xác', 'Ước tính']);

  form.addCheckboxItem()
      .setTitle('Chuyến ' + n + ': Nguồn thông tin')
      .setChoiceValues(['Nhớ lại', 'GPS/ứng dụng', 'Vé/biên nhận']);

  // --- GHI CHÚ ---
  form.addTextItem()
      .setTitle('Chuyến ' + n + ': Ghi chú thêm (nếu có)')
      .setHelpText('Ví dụ: Kẹt xe tại ngã tư, trời mưa to...');
}

// ==============================================================================
// 3. HÀM TẠO NHÓM CÂU HỎI THEO CỰ LY (CHO BLOCK Q20) — 2 CHIỀU ĐI + VỀ (CHỌN NHIỀU, NỘI SUY TG & CP)
// ==============================================================================
function addDistanceGroup(form, distances, vehicles) {
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


