/**
 * ==============================================================================
 * DỰ ÁN: NGHIÊN CỨU TUYẾN SỐ 2 (ĐOẠN THAM LƯƠNG - AN HẠ) VÀ TUYẾN 2S (AN HẠ - KHU ĐÔ THỊ TÂY BẮC)
 * ==============================================================================
 * TÊN BIỂU MẪU: PHIẾU KHẢO SÁT PHÁT SINH – THU HÚT CHUYẾN ĐI TẠI CÁC CÔNG TRÌNH
 * MÃ HIỆU: TG-00 – PHIẾU THÔNG TIN ĐẶC TRƯNG CÔNG TRÌNH (NHIỆM VỤ 8)
 * 
 * ĐẶC ĐIỂM KIẾN TRÚC:
 * 1. Tích hợp định vị WebBridge GPS (2 trường: Tọa độ GPS & Địa chỉ tự động).
 * 2. Cấu trúc CÂY PHÂN NHÁNH THÔNG MINH (LOGIC BRANCHING BLOCKS):
 *    - KSV chọn Loại công trình -> Hệ thống tự động nhảy đến đúng Block đặc thù:
 *      + Block A: Shopping Mall (GLA, Gian hàng, Nhân viên, GFA, Chỗ đỗ xe...)
 *      + Block B: Hospital (Giường bệnh, Lượt khám, Nhân viên y tế, GFA, Chỗ đỗ xe...)
 *      + Block C: Residential (Căn hộ, Dân số, Tỷ lệ lấp đầy, GFA, Chỗ đỗ xe...)
 *      + Block D: Hotel (Phòng khách sạn, Tỷ lệ lấp đầy, Nhân viên, GFA, Chỗ đỗ xe...)
 *      + Block E: School (Học sinh, Giáo viên/NV, PUDO, GFA, Chỗ đỗ xe...)
 *      + Block F: Office (GFA, Nhân viên văn phòng, Tỷ lệ lấp đầy, Chỗ đỗ xe...)
 *    - Mỗi block sau khi hoàn thành tự động chuyển thẳng đến trang NỘP PHIẾU (Submit),
 *      loại bỏ 100% các câu hỏi không liên quan của công trình khác.
 * 
 * HƯỚNG DẪN SỬ DỤNG:
 * 1. Mở https://script.google.com -> New Project.
 * 2. Dán toàn bộ mã này vào file Code.gs.
 * 3. Bấm Run (Chạy) hàm `taoForm_TG00_DacTrungCongTrinh`.
 * 4. Xem Execution Log để lấy link Form và 3 thông số nạp vào WebBridgeGPS.gs.
 * ==============================================================================
 */

function taoForm_TG00_DacTrungCongTrinh() {
  var formTitle = 'TG-00: PHIẾU THÔNG TIN ĐẶC TRƯNG CÔNG TRÌNH (TRIP GENERATION - MRT2 & MRT2S)';
  var form = FormApp.create(formTitle);

  form.setDescription(
    'DỰ ÁN NGHIÊN CỨU TUYẾN SỐ 2 (THAM LƯƠNG - AN HẠ) VÀ TUYẾN 2S (AN HẠ - KĐT TÂY BẮC)\n' +
    'PHIẾU KHẢO SÁT PHÁT SINH – THU HÚT CHUYẾN ĐI TẠI CÁC CÔNG TRÌNH (NHIỆM VỤ 8)\n' +
    'Mục đích: Lập 01 phiếu cho mỗi công trình khảo sát. Thông tin này là cơ sở tính toán Trip Generation Rate.\n' +
    '⚠️ Lưu ý KSV: Bắt buộc chụp ảnh có địa chỉ, tọa độ công trình khảo sát để làm minh chứng.'
  );

  form.setAllowResponseEdits(true);
  form.setProgressBar(true);

  // ==========================================================================
  // PHẦN 0: ĐỊNH VỊ GPS & ĐỊA CHỈ TỰ ĐỘNG (TÍCH HỢP TRỢ LÝ ĐỊNH VỊ WEBBRIDGE)
  // ==========================================================================
  form.addSectionHeaderItem().setTitle('0. ĐỊNH VỊ TỰ ĐỘNG & KIỂM SOÁT THỰC ĐỊA');

  var itemGps = form.addTextItem()
      .setTitle('Tọa độ GPS công trình khảo sát (Kinh độ, Vĩ độ)')
      .setHelpText('Hệ thống WebBridge tự động điền tọa độ GPS từ thiết bị của KSV.')
      .setRequired(true);

  var itemAddress = form.addTextItem()
      .setTitle('Địa chỉ công trình khảo sát (Tra cứu tự động từ bản đồ)')
      .setHelpText('Hệ thống tự động tra cứu từ bản đồ số hoặc KSV ghi rõ số nhà, tên đường thực tế.')
      .setRequired(true);

  // ==========================================================================
  // PHẦN 1: THÔNG TIN CHUNG & HẠ TẦNG GIAO THÔNG CÔNG TRÌNH (BẢNG 1 DOCX)
  // ==========================================================================
  form.addSectionHeaderItem().setTitle('PHẦN 1: THÔNG TIN NHẬN DIỆN & HẠ TẦNG TIẾP CẬN CÔNG TRÌNH');

  form.addTextItem()
      .setTitle('1. Mã công trình')
      .setHelpText('Nhập mã định danh công trình. Ví dụ: TG_MALL_01, TG_HOSP_02, TG_RES_01, TG_OFF_01...')
      .setRequired(true);

  form.addTextItem()
      .setTitle('2. Tên công trình khảo sát')
      .setHelpText('Ghi đầy đủ tên công trình. Ví dụ: TTTM Aeon Mall Tân Phú, Bệnh viện Đa khoa Xuyên Á, Chung cư Moscow Tower...')
      .setRequired(true);

  form.addTextItem()
      .setTitle('3a. Địa chỉ chi tiết: Số nhà & Tên đường')
      .setHelpText('Ví dụ: Số 30 Đường Bờ Bao Tân Thắng')
      .setRequired(true);

  form.addTextItem()
      .setTitle('3b. Địa chỉ chi tiết: Phường / Xã')
      .setHelpText('Ví dụ: Phường Sơn Kỳ')
      .setRequired(true);

  form.addTextItem()
      .setTitle('3c. Địa chỉ chi tiết: Quận / Huyện / Thị xã / TP / Tỉnh')
      .setHelpText('Ví dụ: Quận Tân Phú, TP. Hồ Chí Minh')
      .setRequired(true);

  form.addDateItem()
      .setTitle('4. Ngày khảo sát')
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('5. Thứ trong tuần')
      .setChoiceValues([
        'Thứ Hai',
        'Thứ Ba',
        'Thứ Tư',
        'Thứ Năm',
        'Thứ Sáu',
        'Thứ Bảy',
        'Chủ Nhật'
      ])
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('6. Điều kiện thời tiết trong ngày khảo sát')
      .setChoiceValues([
        '1. Nắng ráo',
        '2. Mưa nhỏ / Rải rác',
        '3. Mưa to / Kéo dài',
        '4. Râm mát / Âm u'
      ])
      .showOtherOption(true)
      .setRequired(true);

  form.addTextItem()
      .setTitle('7. Thời gian hoạt động của công trình (Mở cửa – Đóng cửa)')
      .setHelpText('Ví dụ: 08:00 – 22:00, hoặc 24/24 (đối với Bệnh viện / Chung cư)')
      .setRequired(true);

  form.addTextItem()
      .setTitle('8. Tổng số cổng giao thông tiếp cận công trình')
      .setHelpText('Số lượng lối ra/vào dành cho tất cả phương tiện và người đi bộ. Ví dụ: 2, 4')
      .setRequired(true);

  form.addTextItem()
      .setTitle('9. Số cổng bãi đỗ xe (Cổng In / Out)')
      .setHelpText('Số lượng vị trí kiểm soát xe vào/ra bãi đỗ. Ví dụ: 2, 3')
      .setRequired(true);

  form.addTextItem()
      .setTitle('10. Số điểm PUDO (Pick-up / Drop-off - Đón trả khách)')
      .setHelpText('Số vị trí chuyên dụng cho taxi, xe công nghệ, người nhà dừng đón/trả khách. Ví dụ: 1, 2')
      .setRequired(true);

  form.addTextItem()
      .setTitle('11. Người lập phiếu (Mã / Họ tên KSV)')
      .setHelpText('Ví dụ: KSV01 - Nguyễn Văn A')
      .setRequired(true);

  // ==========================================================================
  // PHẦN 2: PHÂN LOẠI CÔNG TRÌNH & ĐIỀU HƯỚNG BLOCK (BRANCHING SWITCH)
  // ==========================================================================
  form.addSectionHeaderItem().setTitle(
    'PHẦN 2: PHÂN LOẠI CÔNG TRÌNH ĐỂ KÍCH HOẠT BLOCK CHUYÊN BIỆT\n' +
    'Hệ thống sẽ tự động chuyển đến đúng Block đặc trưng phù hợp với loại công trình bạn chọn.'
  );

  var itemLoaiCongTrinh = form.addMultipleChoiceItem()
      .setTitle('12. Lựa chọn loại công trình khảo sát')
      .setHelpText('⚠️ KSV chọn đúng loại công trình thực tế để hệ thống hiển thị đúng bảng chỉ tiêu tương ứng')
      .setRequired(true);

  // ==========================================================================
  // KHỞI TẠO CÁC PAGE BREAK (BLOCKS) & TRANG HOÀN THÀNH
  // ==========================================================================

  // TRANG KẾT THÚC / NỘP PHIẾU (Tất cả các block sẽ chuyển về đây sau khi điền xong)
  var pageEndSubmit = form.addPageBreakItem().setTitle('HOÀN THÀNH PHIẾU KHẢO SÁT TG-00');

  // BLOCK A: SHOPPING MALL
  var pageBlockA = form.addPageBreakItem().setTitle('BLOCK A: ĐẶC TRƯNG TRUNG TÂM THƯƠNG MẠI / SIÊU THỊ (SHOPPING MALL)');
  pageBlockA.setGoToPage(pageEndSubmit);

  form.addSectionHeaderItem().setTitle(
    'QUY MÔ & CHỈ TIÊU TÍNH TRIP RATE - SHOPPING MALL\n' +
    'Khung khảo sát chính khuyến nghị: 07:00–22:00 (Ưu tiên Thứ Bảy để bắt đúng profile mua sắm / giải trí)'
  );

  form.addTextItem()
      .setTitle('A1. GLA – Tổng diện tích sàn cho thuê (m²)')
      .setHelpText('⭐ CHỈ TIÊU CHUẨN HÓA CHÍNH: Phục vụ tính chuyến / 1.000 m² GLA. Ví dụ: 45000')
      .setRequired(true);

  form.addTextItem()
      .setTitle('A2. GFA – Tổng diện tích sàn xây dựng (m²)')
      .setHelpText('Tổng diện tích sàn toàn bộ công trình. Ví dụ: 80000')
      .setRequired(true);

  form.addTextItem()
      .setTitle('A3. Số lượng gian hàng / đơn vị thuê (đơn vị)')
      .setHelpText('Tổng số quầy, gian hàng, cửa hàng thương mại. Ví dụ: 150')
      .setRequired(true);

  form.addTextItem()
      .setTitle('A4. Số nhân viên làm việc tại TTTM (người)')
      .setHelpText('Tổng nhân viên ban quản lý, bảo vệ, bán hàng, vệ sinh... Ví dụ: 600')
      .setRequired(true);

  form.addTextItem()
      .setTitle('A5. Tỷ lệ lấp đầy gian hàng thương mại (%)')
      .setHelpText('Ước tính phần trăm diện tích/gian hàng đang hoạt động. Ví dụ: 90%')
      .setRequired(true);

  form.addTextItem()
      .setTitle('A6. Số chỗ đỗ xe máy quy hoạch / thực tế (chỗ)')
      .setHelpText('Tổng sức chứa bãi đỗ xe máy. Ví dụ: 3000')
      .setRequired(true);

  form.addTextItem()
      .setTitle('A7. Số chỗ đỗ ô tô quy hoạch / thực tế (chỗ)')
      .setHelpText('Tổng sức chứa bãi đỗ xe ô tô. Ví dụ: 500')
      .setRequired(true);

  form.addTextItem()
      .setTitle('A8. Nguồn số liệu & Ghi chú bổ sung (Mall)')
      .setHelpText('Ghi rõ nguồn: Ban Quản lý TTTM cung cấp / Hồ sơ cấp phép / Khảo sát đếm thực tế');

  // BLOCK B: HOSPITAL
  var pageBlockB = form.addPageBreakItem().setTitle('BLOCK B: ĐẶC TRƯNG BỆNH VIỆN / CƠ SỞ Y TẾ (HOSPITAL)');
  pageBlockB.setGoToPage(pageEndSubmit);

  form.addSectionHeaderItem().setTitle(
    'QUY MÔ & CHỈ TIÊU TÍNH TRIP RATE - HOSPITAL\n' +
    'Khung khảo sát chính khuyến nghị: 07:00–09:00 và 16:30–18:30 (Bổ sung giữa ngày nếu lưu lượng khám lớn)'
  );

  form.addTextItem()
      .setTitle('B1. Số giường bệnh nội trú theo thiết kế / thực tế (giường)')
      .setHelpText('⭐ CHỈ TIÊU CHUẨN HÓA CHÍNH: Phục vụ tính chuyến / 100 giường bệnh. Ví dụ: 500')
      .setRequired(true);

  form.addTextItem()
      .setTitle('B2. Lượt khám ngoại trú trung bình (lượt / ngày)')
      .setHelpText('Số lượt bệnh nhân đến khám trong ngày bình thường. Ví dụ: 1200')
      .setRequired(true);

  form.addTextItem()
      .setTitle('B3. GFA – Tổng diện tích sàn xây dựng (m²)')
      .setHelpText('Tổng diện tích sàn khu khám, điều trị nội trú, kỹ thuật... Ví dụ: 35000')
      .setRequired(true);

  form.addTextItem()
      .setTitle('B4. Số nhân viên y tế + Cán bộ nhân viên bệnh viện (người)')
      .setHelpText('Tổng số bác sĩ, y tá, điều dưỡng, hành chính, hậu cần... Ví dụ: 450')
      .setRequired(true);

  form.addTextItem()
      .setTitle('B5. Tỷ lệ lấp đầy / sử dụng giường bệnh bình quân (%)')
      .setHelpText('Tỷ lệ công suất giường bệnh nội trú. Ví dụ: 85%')
      .setRequired(true);

  form.addTextItem()
      .setTitle('B6. Số chỗ đỗ xe máy quy hoạch / thực tế (chỗ)')
      .setHelpText('Bãi xe bệnh nhân, thân nhân và nhân viên. Ví dụ: 1500')
      .setRequired(true);

  form.addTextItem()
      .setTitle('B7. Số chỗ đỗ ô tô quy hoạch / thực tế (chỗ)')
      .setHelpText('Bãi đỗ ô tô bệnh nhân và xe cấp cứu. Ví dụ: 100')
      .setRequired(true);

  form.addTextItem()
      .setTitle('B8. Nguồn số liệu & Ghi chú bổ sung (Hospital)')
      .setHelpText('Ghi rõ nguồn: Phòng Kế hoạch tổng hợp / Ban Giám đốc cung cấp / Báo cáo thường niên');

  // BLOCK C: RESIDENTIAL
  var pageBlockC = form.addPageBreakItem().setTitle('BLOCK C: ĐẶC TRƯNG KHU DÂN CƯ / CHUNG CƯ / CĂN HỘ (RESIDENTIAL)');
  pageBlockC.setGoToPage(pageEndSubmit);

  form.addSectionHeaderItem().setTitle(
    'QUY MÔ & CHỈ TIÊU TÍNH TRIP RATE - RESIDENTIAL\n' +
    'Khung khảo sát chính khuyến nghị: 07:00–22:00, ngày thường (Nhận dạng outbound AM và inbound PM)'
  );

  form.addTextItem()
      .setTitle('C1. Tổng số căn hộ (căn)')
      .setHelpText('⭐ CHỈ TIÊU CHUẨN HÓA CHÍNH: Phục vụ tính chuyến / 100 căn hộ. Ví dụ: 850')
      .setRequired(true);

  form.addTextItem()
      .setTitle('C2. Dân số cư trú thực tế ước tính (người)')
      .setHelpText('Số cư dân đang sinh sống thực tế tại chung cư/khu dân cư. Ví dụ: 2600')
      .setRequired(true);

  form.addTextItem()
      .setTitle('C3. GFA – Tổng diện tích sàn xây dựng (m²)')
      .setHelpText('Tổng diện tích sàn toàn bộ khối căn hộ và tiện ích. Ví dụ: 65000')
      .setRequired(true);

  form.addTextItem()
      .setTitle('C4. Tỷ lệ lấp đầy căn hộ (%)')
      .setHelpText('Tỷ lệ căn hộ đã có cư dân vào ở trên tổng số căn hộ bàn giao. Ví dụ: 90%')
      .setRequired(true);

  form.addTextItem()
      .setTitle('C5. Số nhân viên ban quản lý & vận hành chung cư (người)')
      .setHelpText('Bảo vệ, kỹ thuật, lao công, lễ tân... Ví dụ: 45');

  form.addTextItem()
      .setTitle('C6. Số chỗ đỗ xe máy quy hoạch / thực tế (chỗ)')
      .setHelpText('Sức chứa hầm hoặc bãi xe máy cư dân. Ví dụ: 1800')
      .setRequired(true);

  form.addTextItem()
      .setTitle('C7. Số chỗ đỗ ô tô quy hoạch / thực tế (chỗ)')
      .setHelpText('Sức chứa ô tô hầm hoặc bãi đỗ ngoài trời. Ví dụ: 250')
      .setRequired(true);

  form.addTextItem()
      .setTitle('C8. Nguồn số liệu & Ghi chú bổ sung (Residential)')
      .setHelpText('Ghi rõ nguồn: Ban Quản lý chung cư / Chủ đầu tư cung cấp');

  // BLOCK D: HOTEL
  var pageBlockD = form.addPageBreakItem().setTitle('BLOCK D: ĐẶC TRƯNG KHÁCH SẠN / LƯU TRÚ DU LỊCH (HOTEL)');
  pageBlockD.setGoToPage(pageEndSubmit);

  form.addSectionHeaderItem().setTitle(
    'QUY MÔ & CHỈ TIÊU TÍNH TRIP RATE - HOTEL\n' +
    'Khung khảo sát chính khuyến nghị: 07:00–09:00 và 16:30–18:30 (Ghi chú riêng nếu có đoàn khách/sự kiện)'
  );

  form.addTextItem()
      .setTitle('D1. Tổng số phòng khách sạn (phòng)')
      .setHelpText('⭐ CHỈ TIÊU CHUẨN HÓA CHÍNH: Phục vụ tính chuyến / 100 phòng khách sạn. Ví dụ: 250')
      .setRequired(true);

  form.addTextItem()
      .setTitle('D2. Tỷ lệ lấp đầy phòng bình quân (%)')
      .setHelpText('Tỷ lệ kín phòng trung bình trong thời gian gần đây. Ví dụ: 75%')
      .setRequired(true);

  form.addTextItem()
      .setTitle('D3. GFA – Tổng diện tích sàn xây dựng (m²)')
      .setHelpText('Tổng diện tích sàn lưu trú, hội nghị, nhà hàng... Ví dụ: 20000')
      .setRequired(true);

  form.addTextItem()
      .setTitle('D4. Số nhân viên khách sạn (người)')
      .setHelpText('Tổng số nhân viên lễ tân, buồng phòng, bếp, bảo vệ... Ví dụ: 120')
      .setRequired(true);

  form.addTextItem()
      .setTitle('D5. Số chỗ đỗ xe máy quy hoạch / thực tế (chỗ)')
      .setHelpText('Bãi xe máy cho khách và nhân viên. Ví dụ: 200')
      .setRequired(true);

  form.addTextItem()
      .setTitle('D6. Số chỗ đỗ ô tô quy hoạch / thực tế (chỗ)')
      .setHelpText('Sức chứa bãi đỗ ô tô khách lưu trú và xe đưa đón khách. Ví dụ: 50')
      .setRequired(true);

  form.addTextItem()
      .setTitle('D7. Ghi chú đoàn khách / sự kiện hội nghị / Nguồn số liệu (Hotel)')
      .setHelpText('Ghi chú nếu ngày khảo sát có sự kiện tiệc cưới, hội nghị hoặc đoàn khách du lịch lớn');

  // BLOCK E: SCHOOL
  var pageBlockE = form.addPageBreakItem().setTitle('BLOCK E: ĐẶC TRƯNG TRƯỜNG HỌC / CƠ SỞ GIÁO DỤC (SCHOOL)');
  pageBlockE.setGoToPage(pageEndSubmit);

  form.addSectionHeaderItem().setTitle(
    'QUY MÔ & CHỈ TIÊU TÍNH TRIP RATE - SCHOOL\n' +
    'Khung khảo sát chính khuyến nghị: 07:00–09:00 và 16:30–18:30 (PUDO nên khảo sát chi tiết ở giờ đưa/đón học sinh)'
  );

  form.addTextItem()
      .setTitle('E1. Tổng số học sinh / sinh viên (học sinh)')
      .setHelpText('⭐ CHỈ TIÊU CHUẨN HÓA CHÍNH: Phục vụ tính chuyến / 100 học sinh. Ví dụ: 1800')
      .setRequired(true);

  form.addTextItem()
      .setTitle('E2. Số giáo viên + Cán bộ nhân viên nhà trường (người)')
      .setHelpText('Tổng số giáo viên giảng dạy và cán bộ văn phòng, bảo vệ, tạp vụ... Ví dụ: 110')
      .setRequired(true);

  form.addTextItem()
      .setTitle('E3. GFA – Tổng diện tích sàn xây dựng (m²)')
      .setHelpText('Tổng diện tích phòng học, thư viện, nhà thi đấu, hiệu bộ... Ví dụ: 18000')
      .setRequired(true);

  form.addTextItem()
      .setTitle('E4. Đặc điểm khu vực đón trả học sinh (PUDO)')
      .setHelpText('Mô tả cách thức phụ huynh đón trả: Trong sân trường / Có vịnh đỗ xe trước cổng / Dừng đỗ tràn ra lòng đường...')
      .setRequired(true);

  form.addTextItem()
      .setTitle('E5. Số chỗ đỗ xe máy quy hoạch / thực tế (chỗ)')
      .setHelpText('Bãi đỗ xe máy giáo viên và học sinh/sinh viên (nếu có). Ví dụ: 600')
      .setRequired(true);

  form.addTextItem()
      .setTitle('E6. Số chỗ đỗ ô tô quy hoạch / thực tế (chỗ)')
      .setHelpText('Bãi đỗ ô tô giáo viên / xe buýt đưa đón học sinh. Ví dụ: 25')
      .setRequired(true);

  form.addTextItem()
      .setTitle('E7. Nguồn số liệu & Ghi chú bổ sung (School)')
      .setHelpText('Ghi rõ nguồn: Ban Giám hiệu / Phòng Hành chính nhà trường cung cấp');

  // BLOCK F: OFFICE
  var pageBlockF = form.addPageBreakItem().setTitle('BLOCK F: ĐẶC TRƯNG TÒA NHÀ VĂN PHÒNG (OFFICE)');
  pageBlockF.setGoToPage(pageEndSubmit);

  form.addSectionHeaderItem().setTitle(
    'QUY MÔ & CHỈ TIÊU TÍNH TRIP RATE - OFFICE\n' +
    'Khung khảo sát chính khuyến nghị: 07:00–20:00, ngày thường (Tập trung AM inbound và PM outbound)'
  );

  form.addTextItem()
      .setTitle('F1. GFA – Tổng diện tích sàn xây dựng (m²)')
      .setHelpText('⭐ CHỈ TIÊU CHUẨN HÓA CHÍNH: Phục vụ tính chuyến / 1.000 m² GFA. Ví dụ: 25000')
      .setRequired(true);

  form.addTextItem()
      .setTitle('F2. Số lượng nhân viên văn phòng làm việc tại tòa nhà (người)')
      .setHelpText('Tổng số nhân sự làm việc thường xuyên trong tòa nhà. Ví dụ: 1500')
      .setRequired(true);

  form.addTextItem()
      .setTitle('F3. Tỷ lệ lấp đầy diện tích văn phòng (%)')
      .setHelpText('Tỷ lệ diện tích sàn văn phòng đã được cho thuê / sử dụng. Ví dụ: 88%')
      .setRequired(true);

  form.addTextItem()
      .setTitle('F4. Số công ty / đơn vị thuê văn phòng (đơn vị)')
      .setHelpText('Tổng số doanh nghiệp, tổ chức đang thuê/đặt trụ sở. Ví dụ: 25');

  form.addTextItem()
      .setTitle('F5. Số chỗ đỗ xe máy quy hoạch / thực tế (chỗ)')
      .setHelpText('Sức chứa bãi đỗ xe máy hầm/ngoài trời. Ví dụ: 1200')
      .setRequired(true);

  form.addTextItem()
      .setTitle('F6. Số chỗ đỗ ô tô quy hoạch / thực tế (chỗ)')
      .setHelpText('Sức chứa hầm đỗ ô tô nhân viên & khách giao dịch. Ví dụ: 80')
      .setRequired(true);

  form.addTextItem()
      .setTitle('F7. Nguồn số liệu & Ghi chú bổ sung (Office)')
      .setHelpText('Ghi rõ nguồn: Ban Quản lý tòa nhà văn phòng cung cấp');

  // ==========================================================================
  // CẤU HÌNH ĐIỀU HƯỚNG DỰA TRÊN LOẠI CÔNG TRÌNH (PAGE NAVIGATION)
  // ==========================================================================
  itemLoaiCongTrinh.setChoices([
    itemLoaiCongTrinh.createChoice('1. Shopping Mall (Trung tâm thương mại / Siêu thị lớn)', pageBlockA),
    itemLoaiCongTrinh.createChoice('2. Hospital (Bệnh viện / Cơ sở khám chữa bệnh)', pageBlockB),
    itemLoaiCongTrinh.createChoice('3. Residential (Khu dân cư / Chung cư / Căn hộ)', pageBlockC),
    itemLoaiCongTrinh.createChoice('4. Hotel (Khách sạn / Cơ sở lưu trú du lịch)', pageBlockD),
    itemLoaiCongTrinh.createChoice('5. School (Trường học / Cơ sở giáo dục đào tạo)', pageBlockE),
    itemLoaiCongTrinh.createChoice('6. Office (Tòa nhà văn phòng / Trụ sở làm việc)', pageBlockF)
  ]);

  // ==========================================================================
  // NỘI DUNG TRANG HOÀN THÀNH (PAGE END)
  // ==========================================================================
  form.addSectionHeaderItem().setTitle(
    'CẢM ƠN BẠN ĐÃ HOÀN THÀNH PHIẾU KHẢO SÁT TG-00!\n' +
    'Khảo sát viên vui lòng kiểm tra lại toàn bộ thông tin đã nhập và hình ảnh minh chứng trước khi bấm nút GỬI (SUBMIT).'
  );

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
  Logger.log(" ĐÃ TẠO THÀNH CÔNG PHIẾU TG-00: ĐẶC TRƯNG CÔNG TRÌNH (NHIỆM VỤ 8)!");
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
