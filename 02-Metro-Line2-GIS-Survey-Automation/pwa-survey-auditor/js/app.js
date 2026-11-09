const { createApp, ref, reactive, computed, onMounted, watch } = Vue;

const app = createApp({
  setup() {
    // --- STATE ---
    const currentView = ref('home'); // 'home' | 'editor' | 'viewer' | 'analytics'
    const activeSurveyId = ref(null);
    const surveys = ref([]);
    const isMobilePreview = ref(false); // Toggle mobile phone frame mockup for desktop
    const themeMode = ref(localStorage.getItem('formsmobile_theme') || 'light'); // Default to 'light' (Google Forms Classic Purple)
    const notification = ref({ show: false, message: '', type: 'success' });
    const shareModal = reactive({ show: false, survey: null, qrUrl: '' });
    
    // --- SUPABASE CLOUD MODAL STATE ---
    const supabaseModal = reactive({
      show: false,
      url: '',
      key: '',
      isConnected: false
    });

    // --- EDITOR STATE ---
    const currentSurvey = reactive({
      id: '',
      title: '',
      description: '',
      themeColor: 'purple',
      isPublished: true,
      questions: []
    });

    // --- RESPONDENT STATE ---
    const respondentAnswers = reactive({});
    const validationErrors = reactive({});
    const isSubmitted = ref(false);
    const isSubmitting = ref(false);

    // --- ANALYTICS STATE ---
    const responses = ref([]);
    const analyticsTab = ref('summary'); // 'summary' | 'individual'
    const selectedResponseIndex = ref(0);
    const audioLimit = ref(20);

    const audioResponsesList = computed(() => {
      if (!responses.value) return [];
      return responses.value.filter(r => r.answers && (r.answers._audioProof || r.answers._aiTranscript));
    });

    const isRespondentOnly = ref(false);
    // Check & Set default Admin PIN to 080905
    const storedPin = localStorage.getItem('formsmobile_admin_pin');
    if (!storedPin || storedPin === '1234') {
      localStorage.setItem('formsmobile_admin_pin', '080905');
    }
    const adminPin = ref(localStorage.getItem('formsmobile_admin_pin') || '080905');
    const adminPinModal = reactive({
      show: false,
      pinInput: '',
      errorMsg: ''
    });

    const requestAdminAccess = () => {
      adminPinModal.pinInput = '';
      adminPinModal.errorMsg = '';
      adminPinModal.show = true;
    };

    const verifyAdminPin = () => {
      if (adminPinModal.pinInput.trim() === adminPin.value.trim()) {
        isRespondentOnly.value = false;
        adminPinModal.show = false;
        showToast('Mở khóa trang quản trị Admin thành công!');
        goHome();
      } else {
        adminPinModal.errorMsg = 'Mật khẩu PIN quản trị không chính xác!';
      }
    };

    // --- INITIAL LOAD ---
    onMounted(async () => {
      try {
        applyTheme(themeMode.value);
        checkSupabaseConnectionStatus();
        await loadSurveys();

        // Check URL parameters for Respondent Link (e.g. ?form=survey-sample-1 or ?fill=survey-sample-1)
        const urlParams = new URLSearchParams(window.location.search);
        const targetFormId = urlParams.get('form') || urlParams.get('fill') || urlParams.get('id');

        if (targetFormId) {
          isRespondentOnly.value = true;
          await openViewer(targetFormId);
        }
      } catch (err) {
        console.error('Lỗi khởi tạo ứng dụng:', err);
        surveys.value = window.surveyStore.getSurveys();
      }
    });

    const checkSupabaseConnectionStatus = () => {
      if (!window.surveyStore) return;
      const cfg = window.surveyStore.getSupabaseConfig();
      supabaseModal.url = cfg ? (cfg.url || '') : '';
      supabaseModal.key = cfg ? (cfg.key || '') : '';
      supabaseModal.isConnected = window.surveyStore.isCloudConnected();
    };

    const applyTheme = (mode) => {
      themeMode.value = mode;
      localStorage.setItem('formsmobile_theme', mode);
      if (mode === 'dark') {
        document.body.classList.remove('theme-light');
        document.body.classList.add('theme-dark', 'dark');
      } else {
        document.body.classList.remove('theme-dark', 'dark');
        document.body.classList.add('theme-light');
      }
    };

    const toggleThemeMode = () => {
      const newMode = themeMode.value === 'light' ? 'dark' : 'light';
      applyTheme(newMode);
      showToast(newMode === 'light' ? 'Đã chuyển sang Giao diện Sáng (Google Forms)' : 'Đã chuyển sang Giao diện Tối (Dark Mode)');
      if (currentView.value === 'analytics') {
        Vue.nextTick(() => renderAnalyticsCharts());
      }
    };

    const loadSurveys = async () => {
      if (window.surveyStore && typeof window.surveyStore.fetchSurveysFromCloud === 'function') {
        surveys.value = await window.surveyStore.fetchSurveysFromCloud();
      } else if (window.surveyStore) {
        surveys.value = window.surveyStore.getSurveys();
      }
    };

    const showToast = (msg, type = 'success') => {
      notification.value = { show: true, message: msg, type };
      setTimeout(() => {
        notification.value.show = false;
      }, 3000);
    };

    // --- SUPABASE CONFIG HANDLERS ---
    const openSupabaseModal = () => {
      checkSupabaseConnectionStatus();
      supabaseModal.show = true;
    };

    const saveSupabaseSettings = () => {
      try {
        const url = (supabaseModal.url || '').trim();
        const key = (supabaseModal.key || '').trim();
        
        if (!url && !key) {
          window.surveyStore.saveSupabaseConfig('', '');
          checkSupabaseConnectionStatus();
          showToast('Đã ngắt kết nối Supabase Cloud', 'warning');
          supabaseModal.show = false;
          return;
        }

        const success = window.surveyStore.saveSupabaseConfig(url, key);
        checkSupabaseConnectionStatus();

        if (success || window.surveyStore.isCloudConnected()) {
          showToast('Lưu & Kết nối Supabase Cloud thành công!');
          supabaseModal.show = false;
          loadSurveys();
        } else {
          showToast('Đã lưu cấu hình, đang khởi tạo kết nối Cloud...', 'warning');
          supabaseModal.show = false;
        }
      } catch(e) {
        console.error('Lỗi lưu cấu hình Supabase:', e);
        showToast('Lỗi: ' + e.message, 'error');
      }
    };

    const copySQLScript = () => {
      const sql = `-- 1. Tạo bảng Surveys
create table public.surveys (
  id text primary key,
  title text not null,
  description text,
  theme_color text default 'purple',
  is_published boolean default true,
  questions jsonb not null default '[]'::jsonb,
  created_at timestamp with time zone default timezone('utc'::text, now()),
  updated_at timestamp with time zone default timezone('utc'::text, now())
);

-- 2. Tạo bảng Responses
create table public.responses (
  id text primary key,
  survey_id text references public.surveys(id) on delete cascade,
  answers jsonb not null default '{}'::jsonb,
  submitted_at timestamp with time zone default timezone('utc'::text, now())
);

-- 3. Bật quyền truy cập công khai (RLS)
alter table public.surveys enable row level security;
alter table public.responses enable row level security;

create policy "Public read surveys" on public.surveys for select using (true);
create policy "Public insert surveys" on public.surveys for insert with check (true);
create policy "Public update surveys" on public.surveys for update using (true);
create policy "Public delete surveys" on public.surveys for delete using (true);

create policy "Public read responses" on public.responses for select using (true);
create policy "Public insert responses" on public.responses for insert with check (true);
create policy "Public delete responses" on public.responses for delete using (true);`;

      navigator.clipboard.writeText(sql).then(() => {
        showToast('Đã copy đoạn mã SQL Supabase vào bộ nhớ tạm!');
      });
    };

    // --- NAVIGATION HELPERS ---
    const goHome = () => {
      if (isRespondentOnly.value) return;
      loadSurveys();
      currentView.value = 'home';
      activeSurveyId.value = null;
    };

    const createNewSurvey = () => {
      const newId = 'survey-' + Date.now();
      currentSurvey.id = newId;
      currentSurvey.title = 'Đăng ký nhận thông tin chương trình MBA/MHA';
      currentSurvey.description = 'Hệ thống sẽ tự động gửi email thông tin tuyển sinh khi có thông báo tuyển sinh mới.';
      currentSurvey.themeColor = 'purple';
      currentSurvey.isPublished = true;
      currentSurvey.questions = [
        {
          id: 'q_' + Date.now(),
          title: 'Họ và Tên',
          type: 'text_short',
          required: true,
          placeholder: 'Câu trả lời của bạn'
        },
        {
          id: 'q_' + (Date.now() + 1),
          title: 'Địa chỉ email',
          type: 'text_short',
          required: true,
          placeholder: 'Câu trả lời của bạn'
        },
        {
          id: 'q_' + (Date.now() + 2),
          title: 'Số điện thoại liên lạc',
          type: 'text_short',
          required: true,
          placeholder: 'Câu trả lời của bạn'
        }
      ];
      activeSurveyId.value = newId;
      currentView.value = 'editor';
    };

    const editSurvey = async (surveyId) => {
      let existing = window.surveyStore ? window.surveyStore.getSurveyById(surveyId) : null;
      if (!existing && window.surveyStore) {
        existing = await window.surveyStore.getSurveyByIdAsync(surveyId);
      }
      if (existing) {
        Object.assign(currentSurvey, JSON.parse(JSON.stringify(existing)));
        activeSurveyId.value = surveyId;
        currentView.value = 'editor';
      }
    };

    const openViewer = async (surveyId) => {
      let existing = window.surveyStore ? window.surveyStore.getSurveyById(surveyId) : null;
      if (!existing && window.surveyStore) {
        existing = await window.surveyStore.getSurveyByIdAsync(surveyId);
      }
      if (existing) {
        Object.assign(currentSurvey, JSON.parse(JSON.stringify(existing)));
        activeSurveyId.value = surveyId;
        // Reset answers, validation & section step
        Object.keys(respondentAnswers).forEach(k => delete respondentAnswers[k]);
        Object.keys(validationErrors).forEach(k => delete validationErrors[k]);
        currentSectionIndex.value = 0;
        isSubmitted.value = false;
        isSubmitting.value = false;
        // Reset AI state để không hiện transcript/audio cũ từ form trước
        aiTranscript.value = '';
        audioBlob.value = null;
        audioUrl.value = null;
        aiStatusMessage.value = '';
        isAiRecording.value = false;
        accumulatedText = '';
        isManualStop = false;
        mediaRecorder = null;
        activeSpeechRecogInstance = null;
        audioChunks = [];
        currentView.value = 'viewer';
        // Auto fetch GPS location for survey submission
        fetchUserLocation();
      }
    };

    const openAnalytics = async (surveyId) => {
      try {
        let existing = window.surveyStore.getSurveyById(surveyId);
        if (!existing) {
          existing = await window.surveyStore.getSurveyByIdAsync(surveyId);
        }
        if (!existing) {
          existing = surveys.value.find(s => s.id === surveyId);
        }
        if (existing) {
          Object.assign(currentSurvey, JSON.parse(JSON.stringify(existing)));
          activeSurveyId.value = surveyId;
          // Reset responses state immediately to prevent showing previous survey's data
          responses.value = [];
          // Switch view IMMEDIATELY so the UI responds to click without delay!
          currentView.value = 'analytics';

          // Fetch responses from Cloud/Local for this specific survey
          responses.value = await window.surveyStore.fetchResponsesForSurvey(surveyId);
          selectedResponseIndex.value = 0;

          // Render charts on next tick
          Vue.nextTick(() => {
            renderAnalyticsCharts();
          });
        }
      } catch (err) {
        console.error("Lỗi khi mở Thống kê:", err);
        showToast("Đã có lỗi xảy ra khi tải trang Thống kê");
      }
    };

    const refreshAnalyticsData = async () => {
      if (!activeSurveyId.value) return;
      showToast('Đang kết nối Cloud kéo dữ liệu phản hồi...');
      responses.value = await window.surveyStore.fetchResponsesForSurvey(activeSurveyId.value);
      selectedResponseIndex.value = 0;
      Vue.nextTick(() => {
        renderAnalyticsCharts();
      });
      showToast(`Đã đồng bộ thành công ${responses.value.length} lượt phản hồi từ Cloud!`);
    };

    // --- EDITOR LOGIC ---
    const addQuestion = (type = 'single_choice', afterIndex = null) => {
      const qCount = currentSurvey.questions.length + 1;
      const q = {
        id: 'q_' + Date.now(),
        title: `Câu hỏi ${qCount}`,
        description: '',
        type: type,
        required: true,
        shuffleOptions: false,
        logicMap: {},
        options: (type === 'single_choice' || type === 'multiple_choice' || type === 'dropdown') ? ['Tùy chọn 1', 'Tùy chọn 2'] : [],
        rows: (type === 'grid_single' || type === 'grid_multiple') ? ['Hàng 1', 'Hàng 2'] : [],
        columns: (type === 'grid_single' || type === 'grid_multiple') ? ['Cột 1', 'Cột 2', 'Cột 3'] : []
      };
      if (afterIndex !== null && afterIndex >= 0) currentSurvey.questions.splice(afterIndex + 1, 0, q);
      else currentSurvey.questions.push(q);
      showToast('Đã thêm câu hỏi mới');
    };

    const addTitleBlock = (afterIndex = null) => {
      const q = {
        id: 'q_' + Date.now(),
        title: 'Tiêu đề phần mới',
        description: 'Nhập nội dung mô tả chi tiết ở đây...',
        type: 'title_block',
        required: false
      };
      if (afterIndex !== null && afterIndex >= 0) currentSurvey.questions.splice(afterIndex + 1, 0, q);
      else currentSurvey.questions.push(q);
      showToast('Đã thêm thẻ Tiêu đề & Mô tả');
    };

    const addImageBlock = (afterIndex = null) => {
      const q = {
        id: 'q_' + Date.now(),
        title: 'Hình ảnh minh họa',
        mediaUrl: 'https://images.unsplash.com/photo-1579546929518-9e396f3cc809?w=800&auto=format&fit=crop&q=80',
        type: 'image_block',
        required: false
      };
      if (afterIndex !== null && afterIndex >= 0) currentSurvey.questions.splice(afterIndex + 1, 0, q);
      else currentSurvey.questions.push(q);
      showToast('Đã thêm hình ảnh minh họa');
    };

    const addVideoBlock = (afterIndex = null) => {
      const q = {
        id: 'q_' + Date.now(),
        title: 'Video minh họa',
        mediaUrl: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        type: 'video_block',
        required: false
      };
      if (afterIndex !== null && afterIndex >= 0) currentSurvey.questions.splice(afterIndex + 1, 0, q);
      else currentSurvey.questions.push(q);
      showToast('Đã thêm video minh họa');
    };

    const addSectionBlock = (afterIndex = null) => {
      const sectionCount = currentSurvey.questions.filter(q => q.type === 'section_break').length + 2;
      const q = {
        id: 'q_' + Date.now(),
        title: `Phần ${sectionCount}: Tiêu đề mục mới`,
        description: 'Mô tả ngắn gọn về mục khảo sát này...',
        type: 'section_break',
        required: false
      };
      if (afterIndex !== null && afterIndex >= 0) currentSurvey.questions.splice(afterIndex + 1, 0, q);
      else currentSurvey.questions.push(q);
      showToast('Đã thêm Ngắt Phần khảo sát');
    };

    // --- MULTI-SECTION NAVIGATION & CONDITIONAL LOGIC ---
    const currentSectionIndex = ref(0);

    const surveySections = computed(() => {
      if (!currentSurvey.questions || currentSurvey.questions.length === 0) return [];
      const sections = [];
      let currentSec = { title: currentSurvey.title, description: currentSurvey.description, questions: [] };
      
      currentSurvey.questions.forEach((q, idx) => {
        if (q.type === 'section_break' && idx > 0) {
          sections.push(currentSec);
          currentSec = { title: q.title, description: q.description, questions: [] };
        } else {
          currentSec.questions.push(q);
        }
      });
      sections.push(currentSec);
      return sections;
    });

    const getRenderedOptions = (question) => {
      if (!question || !question.options) return [];
      if (!question.shuffleOptions) return question.options;
      if (!question._shuffledCache) {
        question._shuffledCache = [...question.options].sort(() => Math.random() - 0.5);
      }
      return question._shuffledCache;
    };

    const nextSection = async () => {
      const activeSec = surveySections.value[currentSectionIndex.value];
      if (!activeSec) return;

      let hasError = false;
      activeSec.questions.forEach(q => {
        if (q.required && q.type !== 'title_block' && q.type !== 'image_block' && q.type !== 'video_block' && q.type !== 'section_break') {
          const val = respondentAnswers[q.id];
          if (val === undefined || val === null || val === '' || (Array.isArray(val) && val.length === 0)) {
            validationErrors[q.id] = 'Vui lòng hoàn thành câu hỏi bắt buộc này';
            hasError = true;
          }
        }
      });

      if (hasError) {
        showToast('Vui lòng hoàn thành các câu hỏi bắt buộc trước khi sang phần tiếp theo', 'warning');
        return;
      }

      // Conditional Logic Skip Routing
      let targetSec = null;
      let shouldSubmit = false;
      for (const q of activeSec.questions) {
        if ((q.type === 'single_choice' || q.type === 'dropdown') && q.logicMap) {
          const selected = respondentAnswers[q.id];
          if (selected && q.logicMap[selected] !== undefined && q.logicMap[selected] !== '') {
            const rule = q.logicMap[selected];
            if (rule === 'submit') {
              shouldSubmit = true;
              break;
            } else {
              targetSec = parseInt(rule, 10);
            }
          }
        }
      }

      if (shouldSubmit) {
        await submitForm();
        return;
      }

      if (targetSec !== null && targetSec >= 0 && targetSec < surveySections.value.length) {
        currentSectionIndex.value = targetSec;
        window.scrollTo({ top: 0, behavior: 'smooth' });
        return;
      }

      if (currentSectionIndex.value < surveySections.value.length - 1) {
        currentSectionIndex.value++;
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    };

    const prevSection = () => {
      if (currentSectionIndex.value > 0) {
        currentSectionIndex.value--;
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    };

    const removeQuestion = (index) => {
      if (currentSurvey.questions.length <= 1) {
        showToast('Khảo sát cần có ít nhất 1 câu hỏi', 'warning');
        return;
      }
      currentSurvey.questions.splice(index, 1);
      showToast('Đã xóa câu hỏi');
    };

    const duplicateQuestion = (index) => {
      const target = currentSurvey.questions[index];
      const dup = JSON.parse(JSON.stringify(target));
      dup.id = 'q_' + Date.now();
      dup.title = target.title + ' (Bản sao)';
      currentSurvey.questions.splice(index + 1, 0, dup);
      showToast('Đã nhân bản câu hỏi');
    };

    const moveQuestion = (index, direction) => {
      const targetIndex = index + direction;
      if (targetIndex < 0 || targetIndex >= currentSurvey.questions.length) return;
      const item = currentSurvey.questions.splice(index, 1)[0];
      currentSurvey.questions.splice(targetIndex, 0, item);
    };

    const addOption = (question) => {
      if (!question.options) question.options = [];
      question.options.push(`Tùy chọn ${question.options.length + 1}`);
    };

    const removeOption = (question, optIndex) => {
      if (question.options.length <= 2) {
        showToast('Cần ít nhất 2 lựa chọn', 'warning');
        return;
      }
      question.options.splice(optIndex, 1);
    };

    const addRow = (question) => {
      if (!question.rows) question.rows = [];
      question.rows.push(`Hàng ${question.rows.length + 1}`);
    };

    const removeRow = (question, rIdx) => {
      if (question.rows.length <= 1) {
        showToast('Cần ít nhất 1 hàng', 'warning');
        return;
      }
      question.rows.splice(rIdx, 1);
    };

    const addColumn = (question) => {
      if (!question.columns) question.columns = [];
      question.columns.push(`Cột ${question.columns.length + 1}`);
    };

    const removeColumn = (question, cIdx) => {
      if (question.columns.length <= 1) {
        showToast('Cần ít nhất 1 cột', 'warning');
        return;
      }
      question.columns.splice(cIdx, 1);
    };

    const handleTypeChange = (question) => {
      if ((question.type === 'single_choice' || question.type === 'multiple_choice' || question.type === 'dropdown') && (!question.options || question.options.length === 0)) {
        question.options = ['Tùy chọn 1', 'Tùy chọn 2'];
      }
      if ((question.type === 'grid_single' || question.type === 'grid_multiple')) {
        if (!question.rows || question.rows.length === 0) question.rows = ['Hàng 1', 'Hàng 2'];
        if (!question.columns || question.columns.length === 0) question.columns = ['Cột 1', 'Cột 2', 'Cột 3'];
      }
    };

    const saveSurveyEditor = async () => {
      if (!currentSurvey.title.trim()) {
        showToast('Vui lòng nhập tiêu đề khảo sát', 'warning');
        return;
      }
      await window.surveyStore.saveSurvey(JSON.parse(JSON.stringify(currentSurvey)));
      showToast('Đã lưu khảo sát thành công!');
      loadSurveys();
    };

    const deleteSurveyConfirm = async (surveyId) => {
      const targetSurvey = surveys.value.find(s => s.id === surveyId);
      const title = targetSurvey ? targetSurvey.title : 'khảo sát này';
      
      if (confirm(`Bạn có chắc chắn muốn xóa bài khảo sát "${title}" không?`)) {
        surveys.value = surveys.value.filter(s => s.id !== surveyId);
        showToast('Đã xóa bài khảo sát!');
        try {
          await window.surveyStore.deleteSurvey(surveyId);
        } catch (err) {
          console.warn('Lỗi xóa khảo sát:', err);
        }
      }
    };

    // --- RESPONDENT LOGIC ---
    const handleSingleChoiceSelect = (qId, option) => {
      respondentAnswers[qId] = option;
      delete validationErrors[qId];
    };

    const handleMultipleChoiceSelect = (qId, option) => {
      if (!respondentAnswers[qId]) {
        respondentAnswers[qId] = [];
      }
      const arr = respondentAnswers[qId];
      const idx = arr.indexOf(option);
      if (idx >= 0) {
        arr.splice(idx, 1);
      } else {
        arr.push(option);
      }
      delete validationErrors[qId];
    };

    const handleRatingSelect = (qId, score) => {
      respondentAnswers[qId] = score;
      delete validationErrors[qId];
    };

    const handleGridSingleSelect = (qId, row, col) => {
      if (!respondentAnswers[qId] || typeof respondentAnswers[qId] !== 'object') {
        respondentAnswers[qId] = {};
      }
      respondentAnswers[qId][row] = col;
      delete validationErrors[qId];
    };

    const handleGridMultipleSelect = (qId, row, col) => {
      if (!respondentAnswers[qId] || typeof respondentAnswers[qId] !== 'object') {
        respondentAnswers[qId] = {};
      }
      if (!Array.isArray(respondentAnswers[qId][row])) {
        respondentAnswers[qId][row] = [];
      }
      const arr = respondentAnswers[qId][row];
      const idx = arr.indexOf(col);
      if (idx >= 0) arr.splice(idx, 1);
      else arr.push(col);
      delete validationErrors[qId];
    };

    const handleFileUpload = (qId, event) => {
      const file = event.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (e) => {
        respondentAnswers[qId] = {
          name: file.name,
          size: (file.size / 1024).toFixed(1) + ' KB',
          dataUrl: e.target.result
        };
        delete validationErrors[qId];
        showToast(`Đã đính kèm tệp: ${file.name}`);
      };
      reader.readAsDataURL(file);
    };

    const completedProgress = computed(() => {
      if (!currentSurvey.questions || currentSurvey.questions.length === 0) return 0;
      let answeredCount = 0;
      currentSurvey.questions.forEach(q => {
        const val = respondentAnswers[q.id];
        if (Array.isArray(val) && val.length > 0) answeredCount++;
        else if (val !== undefined && val !== null && val !== '') answeredCount++;
      });
      return Math.round((answeredCount / currentSurvey.questions.length) * 100);
    });

    // --- AI VOICE RECORDING & AUTO-FILL LOGIC ---
    const isAiRecording = ref(false);
    const aiTranscript = ref('');
    const audioBlob = ref(null);
    const audioUrl = ref(null);
    const aiStatusMessage = ref('');
    let mediaRecorder = null;
    let audioChunks = [];
    let activeSpeechRecogInstance = null;
    let accumulatedText = '';
    let isManualStop = false;

    const blobToBase64 = (blob) => {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => {
          const dataUrl = reader.result;
          const base64 = dataUrl.split(',')[1];
          resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      });
    };

    const createAndStartSpeechRecognition = () => {
      if (!isAiRecording.value || isManualStop) return;

      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) return;

      try {
        if (activeSpeechRecogInstance) {
          try { activeSpeechRecogInstance.stop(); } catch (e) {}
        }

        const recog = new SpeechRecognition();
        activeSpeechRecogInstance = recog;
        recog.continuous = true;
        recog.interimResults = true;
        recog.lang = 'vi-VN';

        recog.onresult = (event) => {
          let currentChunk = '';
          for (let i = 0; i < event.results.length; i++) {
            currentChunk += event.results[i][0].transcript + ' ';
          }
          if (currentChunk.trim()) {
            const fullText = (accumulatedText + ' ' + currentChunk).trim();
            aiTranscript.value = fullText;
            aiStatusMessage.value = '🔴 AI đang nhận diện: "' + currentChunk.trim().substring(0, 60) + '"';
            console.log('[MIC] Recognized:', currentChunk.trim());
          }
        };

        recog.onerror = (e) => {
          console.warn('[MIC] Speech error:', e.error);
          if (e.error === 'not-allowed' || e.error === 'service-not-allowed') {
            aiStatusMessage.value = '⚠️ Vui lòng cấp quyền Micro cho Chrome trong Cài đặt điện thoại';
            isAiRecording.value = false;
          }
        };

        recog.onend = () => {
          if (aiTranscript.value) {
            accumulatedText = aiTranscript.value;
          }
          if (isAiRecording.value && !isManualStop) {
            setTimeout(() => {
              if (isAiRecording.value && !isManualStop) {
                createAndStartSpeechRecognition();
              }
            }, 100);
          }
        };

        recog.start();
        console.log('[MIC] New SpeechRecognition instance started');
      } catch (err) {
        console.warn('[MIC] Speech Recognition init error:', err);
      }
    };

    const startAiRecording = () => {
      aiTranscript.value = '';
      accumulatedText = '';
      audioBlob.value = null;
      audioUrl.value = null;
      isManualStop = false;
      aiStatusMessage.value = '🎙️ AI đang lắng nghe... Hãy nói nội dung phỏng vấn!';
      audioChunks = [];
      isAiRecording.value = true;

      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

      // Bước 1: Lấy quyền Microphone TRƯỚC (getUserMedia)
      // Bước 2: Khởi tạo MediaRecorder với stream đã sẵn sàng
      // Bước 3: SAU KHI mic ổn định → mới start SpeechRecognition
      // → Tránh tranh chấp mic giữa getUserMedia và SpeechRecognition
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ audio: true })
          .then(stream => {
            try {
              mediaRecorder = new MediaRecorder(stream);
              audioChunks = [];
              mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) audioChunks.push(e.data);
              };
              mediaRecorder.onstop = () => {
                if (audioChunks.length > 0) {
                  const blob = new Blob(audioChunks, { type: audioChunks[0]?.type || 'audio/webm' });
                  audioBlob.value = blob;
                  audioUrl.value = URL.createObjectURL(blob);
                  console.log('[MIC] Recorded audio blob size:', blob.size, 'type:', blob.type);
                }
                stream.getTracks().forEach(track => track.stop());
              };
              mediaRecorder.start(1000);
              console.log('[MIC] MediaRecorder started — stream acquired OK');
            } catch (err) {
              console.warn('[MIC] MediaRecorder start error:', err);
            }

            // Mic stream đã ổn định → an toàn để start SpeechRecognition
            if (SpeechRecognition) {
              setTimeout(() => {
                if (isAiRecording.value && !isManualStop) {
                  createAndStartSpeechRecognition();
                }
              }, 300);
            }
          })
          .catch(err => {
            console.warn('[MIC] getUserMedia failed:', err);
            // Fallback: Vẫn thử start SpeechRecognition dù không có MediaRecorder
            if (SpeechRecognition) {
              createAndStartSpeechRecognition();
            } else {
              aiStatusMessage.value = '⚠️ Không thể truy cập microphone. Vui lòng cấp quyền.';
            }
          });
      } else if (SpeechRecognition) {
        // Thiết bị không hỗ trợ getUserMedia → chỉ dùng SpeechRecognition
        createAndStartSpeechRecognition();
      } else {
        aiStatusMessage.value = '⚠️ Trình duyệt không hỗ trợ ghi âm. AI Tito sẽ sử dụng nhập liệu tay.';
      }
    };

    const stopAiRecordingAndFill = () => {
      isManualStop = true;
      isAiRecording.value = false;
      aiStatusMessage.value = '⚙️ AI đang dừng thu âm và bóc tách dữ liệu...';

      if (activeSpeechRecogInstance) {
        try { activeSpeechRecogInstance.stop(); } catch (e) {}
      }

      if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        try { mediaRecorder.stop(); } catch (e) {}
      }

      // 1200ms delay to allow Android MediaRecorder.onstop to finish encoding audio blob
      setTimeout(async () => {
        const fullText = (aiTranscript.value || accumulatedText).trim();
        const currentBlob = audioBlob.value;
        
        let count = 0;
        if (fullText || currentBlob) {
          // Pass both recognized text AND audio blob to Gemini AI
          count = await autoFillWithGeminiAI(fullText, currentBlob);
        }

        if (count > 0) {
          showToast(`🎉 AI đã phân tích & điền xong ${count} câu trả lời!`);
        } else if (fullText) {
          showToast('AI đã ghi nhận văn bản cuộc thoại.', 'info');
          aiStatusMessage.value = '✅ Đã ghi nhận bản ghi cuộc thoại.';
        } else if (currentBlob) {
          showToast('🎙️ Đã lưu file ghi âm bằng chứng!', 'success');
          aiStatusMessage.value = '🎙️ Đã lưu file ghi âm bằng chứng thành công!';
        } else {
          showToast('Vui lòng thử nói lại hoặc cấp quyền Micro.', 'warning');
          aiStatusMessage.value = '⚠️ AI chưa nhận diện được giọng nói. Hãy thử lại.';
        }
      }, 1200);
    };

    const geminiApiKey = ref(localStorage.getItem('gemini_api_key') || '');

    // Danh sách Model AI ưu tiên: 3.7 flash -> 3.5 flash -> 3.5 flash lite -> 3.6 flash
    const GEMINI_MODEL_CASCADE = [
      'gemini-3.7-flash',
      'gemini-3.5-flash',
      'gemini-3.5-flash-lite',
      'gemini-3.6-flash'
    ];

    const autoFillWithGeminiAI = async (text, blob = null) => {
      if (!text && (!blob || blob.size === 0)) return 0;

      const apiKey = geminiApiKey.value || localStorage.getItem('gemini_api_key');

      if (apiKey && apiKey.trim()) {
        try {
          aiStatusMessage.value = '🧠 Dữ liệu đang được gửi tới AI Tito để phân tích...';
          console.log('[AI TITO] Bắt đầu gọi API với key:', apiKey.substring(0, 10) + '...');
          
          const questionsMeta = currentSurvey.questions.map(q => ({
            id: q.id,
            title: q.title,
            type: q.type,
            options: q.options || [],
            rows: q.rows || [],
            columns: q.columns || []
          }));

          const parts = [];

          let promptText = `Bạn là trợ lý AI trích xuất thông tin khảo sát từ cuộc phỏng vấn tiếng Việt.

Danh sách câu hỏi:
${JSON.stringify(questionsMeta, null, 2)}
`;

          if (text && text.trim()) {
            promptText += `\nĐoạn văn bản ghi nhận từ giọng nói:\n"${text}"\n`;
          }

          // Chỉ yêu cầu AI nghe audio khi không có text transcript (tối ưu payload)
          const shouldAttachAudio = blob && blob.size > 0 && (!text || !text.trim());

          if (shouldAttachAudio) {
            promptText += `\nHãy lắng nghe file âm thanh đính kèm để trích xuất thông tin chính xác nhất.\n`;
          }

          promptText += `
Trả về JSON theo định dạng: {"answers": {"id_câu_hỏi": "giá_trị"}}

Quy tắc:
- Họ và Tên: chỉ lấy tên người (VD: "Nguyễn Văn A"), bỏ hết lời chào, lời đệm
- Địa chỉ/Nơi làm việc: chỉ lấy tên địa danh (VD: "Bình Dương")  
- Số điện thoại: chỉ lấy số
- Câu hỏi Ngày (date): bắt buộc quy đổi ra dạng YYYY-MM-DD (VD: "2026-08-04")
- Câu hỏi Giờ (time): bắt buộc quy đổi ra dạng HH:mm 24h (VD: "14:30")
- Câu hỏi Lưới (grid_single / grid_multiple): trả về object cặp {"tên_hàng": "tên_cột"}
- Nếu không tìm thấy thông tin cho câu hỏi nào thì bỏ qua, không điền bừa`;

          parts.push({ text: promptText });

          // Chỉ đính kèm audio khi không có text transcript (giảm latency đáng kể)
          if (shouldAttachAudio) {
            try {
              const base64Data = await blobToBase64(blob);
              const cleanMime = (blob.type || 'audio/webm').split(';')[0];
              parts.push({
                inlineData: {
                  mimeType: cleanMime,
                  data: base64Data
                }
              });
              console.log('[AI TITO] Đã đính kèm Audio Blob Base64 (mime:', cleanMime, 'size:', blob.size, ')');
            } catch (e) {
              console.warn('[AI TITO] Không thể convert audioBlob sang base64:', e);
            }
          }

          console.log('[AI TITO] Sending parts count:', parts.length);

          const requestBody = JSON.stringify({
            contents: [{ parts: parts }],
            generationConfig: {
              responseMimeType: "application/json",
              temperature: 0.1
            }
          });

          // === MULTI-MODEL FALLBACK CASCADE ===
          let lastError = null;
          for (let mIdx = 0; mIdx < GEMINI_MODEL_CASCADE.length; mIdx++) {
            const modelName = GEMINI_MODEL_CASCADE[mIdx];
            const modelUrl = `https://generativelanguage.googleapis.com/v1beta/models/${modelName}:generateContent?key=${apiKey.trim()}`;

            console.log(`[AI TITO] Thử model ${mIdx + 1}/${GEMINI_MODEL_CASCADE.length}: ${modelName}...`);

            // AbortController timeout 10 giây cho mỗi lần thử
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000);

            try {
              const response = await fetch(modelUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: requestBody,
                signal: controller.signal
              });

              clearTimeout(timeoutId);
              console.log(`[AI TITO] ${modelName} → HTTP ${response.status} ${response.statusText}`);

              if (response.ok) {
                const data = await response.json();
                console.log('[AI TITO] Response data:', JSON.stringify(data).substring(0, 500));
                
                const jsonText = data.candidates?.[0]?.content?.parts?.[0]?.text || '';
                console.log('[AI TITO] Extracted text:', jsonText);
                
                const cleanJson = jsonText.replace(/```json/g, '').replace(/```/g, '').trim();
                const parsed = JSON.parse(cleanJson);
                console.log('[AI TITO] Parsed answers:', JSON.stringify(parsed));

                if (parsed && parsed.answers) {
                  let filledCount = 0;
                  Object.keys(parsed.answers).forEach(qId => {
                    const val = parsed.answers[qId];
                    if (val !== null && val !== undefined && val !== '') {
                      respondentAnswers[qId] = val;
                      delete validationErrors[qId];
                      filledCount++;
                      console.log(`[AI TITO] Điền: ${qId} = "${val}"`);
                    }
                  });

                  if (filledCount > 0) {
                    aiStatusMessage.value = `🧠 AI Tito đã phân tích thành công ${filledCount} thông tin.`;
                    return filledCount;
                  }
                }
                // Model trả về OK nhưng không parse được answers → thử model tiếp
                console.warn(`[AI TITO] ${modelName} trả về OK nhưng không có answers hợp lệ, thử model tiếp...`);
                lastError = 'no_answers';
              } else {
                const errBody = await response.text();
                console.warn(`[AI TITO] ${modelName} lỗi HTTP ${response.status}:`, errBody.substring(0, 200));
                lastError = response.status;
                // Tiếp tục thử model tiếp theo trong cascade
              }
            } catch (fetchErr) {
              clearTimeout(timeoutId);
              if (fetchErr.name === 'AbortError') {
                console.warn(`[AI TITO] ${modelName} timeout sau 10 giây, thử model tiếp...`);
                lastError = 'timeout';
              } else {
                console.warn(`[AI TITO] ${modelName} exception:`, fetchErr.message);
                lastError = fetchErr.message;
              }
              // Tiếp tục thử model tiếp theo trong cascade
            }
          }

          // Tất cả model đều thất bại
          console.error('[AI TITO] Tất cả model đều thất bại. Lỗi cuối:', lastError);
          if (lastError === 429) {
            aiStatusMessage.value = '⏳ AI Tito tạm thời hết quota. Đã dùng bộ lọc bóc tách ngay!';
          } else if (lastError === 'timeout') {
            aiStatusMessage.value = '⏳ AI Tito đang bận. Đã dùng bộ lọc dự phòng...';
          } else {
            aiStatusMessage.value = `⚠️ AI Tito đang bận (${lastError}). Dùng bộ lọc dự phòng...`;
          }
        } catch (err) {
          console.error('[AI TITO] Exception:', err);
          aiStatusMessage.value = '⚠️ Lỗi kết nối AI Tito. Dùng bộ lọc dự phòng...';
        }
      }

      // Fallback to regex engine
      console.log('[FALLBACK] Chuyển sang bộ lọc regex dự phòng');
      const fallbackCount = autoFillFormFromTranscript(text);
      if (fallbackCount > 0) {
        aiStatusMessage.value = `⚙️ Bộ lọc dự phòng (không phải AI) đã điền ${fallbackCount} thông tin.`;
      }
      return fallbackCount;
    };

    const autoFillFormFromTranscript = (text) => {
      if (!text || !text.trim()) return 0;
      let count = 0;
      const lower = text.toLowerCase();

      currentSurvey.questions.forEach(q => {
        const qTitleLower = (q.title || '').toLowerCase();

        // 1. Rating Stars (1-5)
        if (q.type === 'rating_5') {
          const starMatch = lower.match(/(\d)\s*(sao|điểm|star)/i) || lower.match(/(cho|đánh giá)\s*(\d)\s*sao/i);
          if (starMatch) {
            const score = parseInt(starMatch[1] || starMatch[2]);
            if (score >= 1 && score <= 5) {
              respondentAnswers[q.id] = score;
              delete validationErrors[q.id];
              count++;
            }
          } else if (lower.includes('xuất sắc') || lower.includes('rất tốt') || lower.includes('tuyệt vời') || lower.includes('5 sao')) {
            respondentAnswers[q.id] = 5;
            delete validationErrors[q.id];
            count++;
          } else if (lower.includes('hài lòng') || lower.includes('tốt') || lower.includes('4 sao')) {
            respondentAnswers[q.id] = 4;
            delete validationErrors[q.id];
            count++;
          } else if (lower.includes('bình thường') || lower.includes('tạm được') || lower.includes('3 sao')) {
            respondentAnswers[q.id] = 3;
            delete validationErrors[q.id];
            count++;
          } else if (lower.includes('2 sao') || lower.includes('tệ')) {
            respondentAnswers[q.id] = 2;
            delete validationErrors[q.id];
            count++;
          } else if (lower.includes('1 sao') || lower.includes('rất tệ')) {
            respondentAnswers[q.id] = 1;
            delete validationErrors[q.id];
            count++;
          }
        }
        // 2. Choice Options (Single / Multiple)
        else if (q.type === 'single_choice' || q.type === 'multiple_choice') {
          if (q.options && q.options.length > 0) {
            q.options.forEach(opt => {
              const optLower = opt.toLowerCase();
              if (lower.includes(optLower)) {
                if (q.type === 'single_choice') {
                  respondentAnswers[q.id] = opt;
                  delete validationErrors[q.id];
                  count++;
                } else {
                  if (!Array.isArray(respondentAnswers[q.id])) respondentAnswers[q.id] = [];
                  if (!respondentAnswers[q.id].includes(opt)) {
                    respondentAnswers[q.id].push(opt);
                    delete validationErrors[q.id];
                    count++;
                  }
                }
              }
            });
          }
        }
        // 3. Text inputs (Short / Long)
        else if (q.type === 'text_short' || q.type === 'text_long') {
          const isNameQuestion = (qTitleLower.includes('họ và tên') || qTitleLower.includes('họ tên') || qTitleLower.includes('tên')) && !qTitleLower.includes('tốt nghiệp') && !qTitleLower.includes('đại học') && !qTitleLower.includes('nơi');
          if (isNameQuestion) {
            const nameMatch = text.match(/(?:tên tôi là|tên là|tôi tên|tôi là|họ và tên|họ tên|tên|anh|chị)\s+([^\d,.:;?!]+)/i);
            if (nameMatch && nameMatch[1]) {
              let cleanName = nameMatch[1].trim();
              cleanName = cleanName.replace(/(tiếp đến|tiếp theo|sau đó|mình sẽ|địa chỉ|nơi|ngành|số điện thoại|sđt|phone|email|đánh giá|tốt nghiệp|đại học).*/i, '').trim();
              if (cleanName) {
                respondentAnswers[q.id] = cleanName;
                delete validationErrors[q.id];
                count++;
              }
            }
          } else if (qTitleLower.includes('email') || qTitleLower.includes('thư')) {
            const emailMatch = text.match(/([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/);
            if (emailMatch) {
              respondentAnswers[q.id] = emailMatch[1];
              delete validationErrors[q.id];
              count++;
            }
          } else if (qTitleLower.includes('thoại') || qTitleLower.includes('sđt') || qTitleLower.includes('phone')) {
            const phoneMatch = text.match(/(0[3|5|7|8|9][0-9]{8})/) || text.match(/(\d{5,11})/);
            if (phoneMatch) {
              respondentAnswers[q.id] = phoneMatch[1];
              delete validationErrors[q.id];
              count++;
            }
          } else if (qTitleLower.includes('nơi làm') || qTitleLower.includes('công ty') || qTitleLower.includes('làm việc')) {
            const workMatch = text.match(/(?:làm việc tại|nơi làm việc|công ty|thì ở|ở)\s+([^\d,.:;?!]+)/i);
            if (workMatch && workMatch[1]) {
              let cleanWork = workMatch[1].replace(/(còn ngành|ngành|tốt nghiệp|email|sđt|số điện thoại).*/i, '').trim();
              if (cleanWork) {
                respondentAnswers[q.id] = cleanWork;
                delete validationErrors[q.id];
                count++;
              }
            }
          } else if (qTitleLower.includes('ngành') || qTitleLower.includes('ngành học') || qTitleLower.includes('tốt nghiệp')) {
            const majorMatch = text.match(/(?:ngành|tốt nghiệp|chuyên ngành|tốt nghiệp thì)\s+([^\d,.:;?!]+)/i);
            if (majorMatch && majorMatch[1]) {
              let cleanMajor = majorMatch[1].replace(/(làm việc|email|sđt).*/i, '').trim();
              if (cleanMajor) {
                respondentAnswers[q.id] = cleanMajor;
                delete validationErrors[q.id];
                count++;
              }
            }
          }
        }
        // 4. Date input (YYYY-MM-DD)
        else if (q.type === 'date') {
          const dateStrMatch = text.match(/(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})/) || text.match(/(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})/);
          const vietDateMatch = text.match(/ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})(?:\s+năm\s+(\d{4}))?/i);
          if (dateStrMatch) {
            let y, m, d;
            if (dateStrMatch[1].length === 4) {
              [_, y, m, d] = dateStrMatch;
            } else {
              [_, d, m, y] = dateStrMatch;
            }
            const formattedDate = `${y}-${m.padStart(2, '0')}-${d.padStart(2, '0')}`;
            respondentAnswers[q.id] = formattedDate;
            delete validationErrors[q.id];
            count++;
          } else if (vietDateMatch) {
            const d = vietDateMatch[1].padStart(2, '0');
            const m = vietDateMatch[2].padStart(2, '0');
            const y = vietDateMatch[3] || new Date().getFullYear();
            respondentAnswers[q.id] = `${y}-${m}-${d}`;
            delete validationErrors[q.id];
            count++;
          }
        }
        // 5. Time input (HH:mm)
        else if (q.type === 'time') {
          const timeMatch = text.match(/(\d{1,2})\s*:\s*(\d{2})/) || text.match(/(\d{1,2})\s*(?:giờ|h)\s*(\d{1,2})?/i);
          if (timeMatch) {
            const hh = timeMatch[1].padStart(2, '0');
            const mm = (timeMatch[2] || '00').padStart(2, '0');
            respondentAnswers[q.id] = `${hh}:${mm}`;
            delete validationErrors[q.id];
            count++;
          }
        }
      });

      return count;
    };

    const recordSingleQuestionVoice = (qId) => {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        const userInput = prompt('🎙️ Đọc câu trả lời của bạn:\n(Bấm nút Micro 🎙️ trên bàn phím điện thoại để đọc tiếng Việt)');
        if (userInput && userInput.trim()) {
          respondentAnswers[qId] = userInput.trim();
          delete validationErrors[qId];
          showToast(`Đã ghi nhận: "${userInput.trim()}"`);
        }
        return;
      }

      try {
        const recog = new SpeechRecognition();
        recog.lang = 'vi-VN';
        showToast('🎙️ Đang lắng nghe... Hãy nói câu trả lời của bạn!');

        let gotResult = false;
        recog.onresult = (e) => {
          gotResult = true;
          const resultText = e.results[0][0].transcript;
          respondentAnswers[qId] = resultText;
          delete validationErrors[qId];
          showToast(`Đã nhận diện: "${resultText}"`);
        };

        recog.onerror = () => {
          if (!gotResult) {
            const userInput = prompt('🎙️ Đọc câu trả lời của bạn:\n(Bấm nút Micro 🎙️ trên bàn phím điện thoại để đọc tiếng Việt)');
            if (userInput && userInput.trim()) {
              respondentAnswers[qId] = userInput.trim();
              delete validationErrors[qId];
              showToast(`Đã ghi nhận: "${userInput.trim()}"`);
            }
          }
        };

        recog.start();
      } catch (err) {
        const userInput = prompt('🎙️ Đọc câu trả lời của bạn:\n(Bấm nút Micro 🎙️ trên bàn phím điện thoại để đọc tiếng Việt)');
        if (userInput && userInput.trim()) {
          respondentAnswers[qId] = userInput.trim();
          delete validationErrors[qId];
          showToast(`Đã ghi nhận: "${userInput.trim()}"`);
        }
      }
    };

    // --- GEOLOCATION LOGIC ---
    const userLocation = ref(null);
    const isGettingLocation = ref(false);
    const locationStatus = ref('');

    const fetchUserLocation = () => {
      if (!navigator.geolocation) {
        locationStatus.value = 'Trình duyệt không hỗ trợ vị trí GPS';
        return;
      }

      isGettingLocation.value = true;
      locationStatus.value = 'Đang xác định tọa độ GPS...';

      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          const mapsUrl = `https://www.google.com/maps?q=${lat},${lng}`;
          
          let addressName = `Tọa độ: ${lat.toFixed(5)}, ${lng.toFixed(5)}`;

          try {
            // Reverse Geocoding via OpenStreetMap Nominatim API
            const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=14`, {
              headers: { 'Accept-Language': 'vi' }
            });
            const data = await res.json();
            if (data && data.display_name) {
              addressName = data.display_name;
            }
          } catch (e) {
            console.warn('Lỗi reverse geocoding:', e);
          }

          userLocation.value = {
            latitude: lat,
            longitude: lng,
            address: addressName,
            mapsUrl: mapsUrl,
            accuracy: position.coords.accuracy
          };

          isGettingLocation.value = false;
          locationStatus.value = `📍 ${addressName}`;
        },
        (error) => {
          isGettingLocation.value = false;
          let msg = 'Không thể lấy vị trí';
          if (error.code === error.PERMISSION_DENIED) msg = 'Người dùng từ chối quyền vị trí (GPS)';
          else if (error.code === error.POSITION_UNAVAILABLE) msg = 'Tín hiệu GPS không khả dụng';
          else if (error.code === error.TIMEOUT) msg = 'Quá thời gian lấy vị trí GPS';
          
          locationStatus.value = msg;
          userLocation.value = { error: msg };
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
      );
    };

    const submitForm = async () => {
      // Chặn gửi đúp khi đang xử lý
      if (isSubmitting.value) return;

      // Validate required questions
      let hasError = false;
      Object.keys(validationErrors).forEach(k => delete validationErrors[k]);

      currentSurvey.questions.forEach(q => {
        if (q.required) {
          const val = respondentAnswers[q.id];
          if (val === undefined || val === null || val === '' || (Array.isArray(val) && val.length === 0)) {
            validationErrors[q.id] = 'Vui lòng hoàn thành câu hỏi bắt buộc này';
            hasError = true;
          }
        }
      });

      if (hasError) {
        showToast('Vui lòng điền đầy đủ các câu hỏi bắt buộc!', 'error');
        // Scroll to first error
        const firstErrEl = document.querySelector('.border-red-500, .border-rose-500');
        if (firstErrEl) {
          firstErrEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        return;
      }

      // Khoá nút submit ngay lập tức
      isSubmitting.value = true;

      try {
        // Attach location info if captured
        const submissionData = JSON.parse(JSON.stringify(respondentAnswers));
        if (userLocation.value) {
          submissionData._location = userLocation.value;
        }

        if (aiTranscript.value) {
          submissionData._aiTranscript = aiTranscript.value;
        }

        // Chuyển FileReader callback thành Promise để await được
        if (audioBlob.value) {
          const base64Audio = await new Promise((resolve) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.readAsDataURL(audioBlob.value);
          });
          submissionData._audioProof = base64Audio;
        }

        await window.surveyStore.submitResponse(currentSurvey.id, submissionData);
        isSubmitted.value = true;
        showToast('Gửi khảo sát thành công! Cảm ơn bạn 🎉');
      } catch (err) {
        console.error('[SUBMIT] Lỗi gửi khảo sát:', err);
        showToast('Có lỗi khi gửi khảo sát. Vui lòng thử lại!', 'error');
        isSubmitting.value = false;
      }
    };

    const resetFormRespondent = () => {
      // Reset câu trả lời & lỗi validation
      Object.keys(respondentAnswers).forEach(k => delete respondentAnswers[k]);
      Object.keys(validationErrors).forEach(k => delete validationErrors[k]);
      isSubmitted.value = false;
      isSubmitting.value = false;

      // Reset toàn bộ AI state để voice AI hoạt động lại từ đầu
      aiTranscript.value = '';
      audioBlob.value = null;
      audioUrl.value = null;
      aiStatusMessage.value = '';
      isAiRecording.value = false;
      accumulatedText = '';
      isManualStop = false;
      mediaRecorder = null;
      activeSpeechRecogInstance = null;
      audioChunks = [];
    };

    // --- SHARE & QR MODAL ---
    const shareLink = computed(() => {
      if (!shareModal.survey || !shareModal.survey.id) return '';
      let baseUrl = window.location.origin + window.location.pathname;
      if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        baseUrl = 'https://khao-sat-2026.netlify.app/';
      }
      return baseUrl + `?form=${shareModal.survey.id}`;
    });

    const openShareModal = (survey) => {
      shareModal.survey = survey;
      let baseUrl = window.location.origin + window.location.pathname;
      if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        baseUrl = 'https://khao-sat-2026.netlify.app/';
      }
      const fullUrl = baseUrl + `?form=${survey.id}`;
      shareModal.qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=${encodeURIComponent(fullUrl)}`;
      shareModal.show = true;
    };

    const copySurveyLink = () => {
      const fullUrl = shareLink.value;
      navigator.clipboard.writeText(fullUrl).then(() => {
        showToast('Đã sao chép liên kết khảo sát!');
      }).catch(() => {
        showToast('Đã copy: ' + fullUrl);
      });
    };

    // --- EXPORT DATA ---
    const exportCSV = () => {
      window.surveyStore.exportToCSV(currentSurvey.id);
      showToast('Đã tải xuống file CSV thành công!');
    };

    // --- ANALYTICS CHARTS RENDER ---
    const chartInstances = [];
    const renderAnalyticsCharts = () => {
      chartInstances.forEach(c => c.destroy());
      chartInstances.length = 0;

      if (responses.value.length === 0) return;

      const isDark = themeMode.value === 'dark';
      const textColor = isDark ? '#94a3b8' : '#475569';
      const gridColor = isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)';

      currentSurvey.questions.forEach(q => {
        if (q.type === 'single_choice' || q.type === 'multiple_choice' || q.type === 'dropdown' || q.type === 'rating_5') {
          const canvasId = `chart_${q.id}`;
          const canvasEl = document.getElementById(canvasId);
          if (!canvasEl) return;

          const ctx = canvasEl.getContext('2d');
          
          let labels = [];
          let counts = [];
          let colors = [
            '#673ab7', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b', 
            '#3b82f6', '#14b8a6', '#f97316', '#a855f7', '#06b6d4'
          ];

          if (q.type === 'single_choice' || q.type === 'multiple_choice' || q.type === 'dropdown') {
            labels = q.options || [];
            counts = labels.map(opt => {
              return responses.value.filter(r => {
                const ans = r && r.answers ? r.answers[q.id] : null;
                if (Array.isArray(ans)) return ans.includes(opt);
                return ans === opt;
              }).length;
            });
          } else if (q.type === 'rating_5') {
            labels = ['1 ⭐', '2 ⭐', '3 ⭐', '4 ⭐', '5 ⭐'];
            counts = [1, 2, 3, 4, 5].map(score => {
              return responses.value.filter(r => r && r.answers && Number(r.answers[q.id]) === score).length;
            });
            colors = ['#ef4444', '#f97316', '#eab308', '#84cc16', '#22c55e'];
          }

          const chartType = (q.type === 'single_choice' || q.type === 'dropdown') ? 'doughnut' : 'bar';
          
          const newChart = new Chart(ctx, {
            type: chartType,
            data: {
              labels: labels,
              datasets: [{
                label: 'Số lượt chọn',
                data: counts,
                backgroundColor: colors,
                borderRadius: 8,
                borderWidth: 0
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: {
                  position: 'bottom',
                  labels: { color: textColor, font: { family: 'Plus Jakarta Sans', weight: '600' } }
                }
              },
              scales: chartType === 'bar' ? {
                y: {
                  ticks: { color: textColor, stepSize: 1 },
                  grid: { color: gridColor }
                },
                x: {
                  ticks: { color: textColor },
                  grid: { display: false }
                }
              } : {}
            }
          });
          chartInstances.push(newChart);
        }
      });
    };

    // Helper for question response stats
    const getChoiceStats = (question) => {
      if (!responses.value || responses.value.length === 0) return [];
      const total = responses.value.length;
      return (question.options || []).map(opt => {
        const count = responses.value.filter(r => {
          const ans = r && r.answers ? r.answers[question.id] : null;
          if (Array.isArray(ans)) return ans.includes(opt);
          return ans === opt;
        }).length;
        const percent = Math.round((count / total) * 100);
        return { option: opt, count, percent };
      });
    };

    const getAverageRating = (qId) => {
      if (!responses.value || responses.value.length === 0) return '0.0';
      const ratings = responses.value
        .map(r => (r && r.answers ? Number(r.answers[qId]) : NaN))
        .filter(score => !isNaN(score) && score > 0);
      if (ratings.length === 0) return '0.0';
      const sum = ratings.reduce((a, b) => a + b, 0);
      return (sum / ratings.length).toFixed(1);
    };

    const getTextAnswers = (qId) => {
      if (!responses.value) return [];
      return responses.value
        .map(r => ({
          answer: r && r.answers ? r.answers[qId] : null,
          submittedAt: r ? r.submittedAt : null
        }))
        .filter(item => item.answer && String(item.answer).trim() !== '');
    };

    const formatDate = (isoString) => {
      if (!isoString) return '';
      const d = new Date(isoString);
      return d.toLocaleDateString('vi-VN', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    };

    const getGridStats = (question) => {
      if (!responses.value || responses.value.length === 0 || !question.rows || !question.columns) return [];
      const total = responses.value.length;
      return question.rows.map(row => {
        const colStats = question.columns.map(col => {
          const count = responses.value.filter(r => {
            const ans = r && r.answers ? r.answers[question.id] : null;
            if (!ans || typeof ans !== 'object') return false;
            const val = ans[row];
            if (Array.isArray(val)) return val.includes(col);
            return val === col;
          }).length;
          const percent = Math.round((count / total) * 100);
          return { col, count, percent };
        });
        return { row, colStats };
      });
    };

    const getFileAnswers = (qId) => {
      if (!responses.value) return [];
      return responses.value
        .map(r => ({
          answer: r && r.answers ? r.answers[qId] : null,
          submittedAt: r ? r.submittedAt : null
        }))
        .filter(item => item.answer && item.answer !== null);
    };

    return {
      currentView,
      surveys,
      currentSurvey,
      respondentAnswers,
      validationErrors,
      isSubmitted,
      responses,
      analyticsTab,
      selectedResponseIndex,
      isMobilePreview,
      themeMode,
      notification,
      shareModal,
      shareLink,
      supabaseModal,
      completedProgress,
      isRespondentOnly,
      adminPinModal,
      requestAdminAccess,
      verifyAdminPin,
      userLocation,
      isGettingLocation,
      locationStatus,
      isAiRecording,
      aiTranscript,
      aiStatusMessage,
      audioUrl,
      audioLimit,
      audioResponsesList,
      currentSectionIndex,
      surveySections,
      nextSection,
      prevSection,

      // Functions
      startAiRecording,
      stopAiRecordingAndFill,
      recordSingleQuestionVoice,
      fetchUserLocation,
      toggleThemeMode,
      openSupabaseModal,
      saveSupabaseSettings,
      copySQLScript,
      goHome,
      createNewSurvey,
      editSurvey,
      openViewer,
      openAnalytics,
      refreshAnalyticsData,
      addQuestion,
      addTitleBlock,
      addImageBlock,
      addVideoBlock,
      addSectionBlock,
      removeQuestion,
      duplicateQuestion,
      moveQuestion,
      addOption,
      removeOption,
      addRow,
      removeRow,
      addColumn,
      removeColumn,
      handleTypeChange,
      saveSurveyEditor,
      deleteSurveyConfirm,
      handleSingleChoiceSelect,
      handleMultipleChoiceSelect,
      handleRatingSelect,
      handleGridSingleSelect,
      handleGridMultipleSelect,
      handleFileUpload,
      submitForm,
      isSubmitting,
      resetFormRespondent,
      openShareModal,
      copySurveyLink,
      exportCSV,
      getChoiceStats,
      getAverageRating,
      getTextAnswers,
      getGridStats,
      getFileAnswers,
      getRenderedOptions,
      formatDate
    };
  }
});

app.mount('#app');
