// ─── Pandimedic Frontend — API Integration ─────────────────────────────────
const API = '';  // same origin
let authToken = localStorage.getItem('pandi_token');
let currentUser = null;
let quizData = null;
let currentQuestionIdx = 0;

// ─── UTILS ──────────────────────────────────────────────────────────────────
function showToast(msg, type = 'success') {
    const c = document.getElementById('toast-container');
    const t = document.createElement('div');
    t.className = `toast toast-${type}`;
    t.textContent = msg;
    c.appendChild(t);
    setTimeout(() => t.remove(), 3000);
}

function apiHeaders() {
    const h = { 'Content-Type': 'application/json' };
    if (authToken) h['Authorization'] = `Bearer ${authToken}`;
    return h;
}

async function apiFetch(url, opts = {}) {
    opts.headers = { ...apiHeaders(), ...(opts.headers || {}) };
    const res = await fetch(API + url, opts);
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Bir hata oluştu' }));
        throw new Error(err.detail || 'Bir hata oluştu');
    }
    return res.json();
}

// ─── NAV & PAGES ────────────────────────────────────────────────────────────
const menu = document.getElementById('side-menu');
document.getElementById('menu-toggle').onclick = () => menu.style.transform = 'translateX(0)';
document.getElementById('menu-close').onclick = () => menu.style.transform = 'translateX(100%)';

function showPage(pageId) {
    document.querySelectorAll('.page-section').forEach(s => s.classList.remove('active'));
    document.getElementById(pageId).classList.add('active');
    menu.style.transform = 'translateX(100%)';
    window.scrollTo({ top: 0, behavior: 'smooth' });
    const decoration = document.querySelector('.side-decoration');
    decoration.style.opacity = pageId !== 'home-page' ? '0.3' : '1';
    if (pageId === 'ansiklopedi-page') loadArticles();
    if (pageId === 'leaderboard-page') loadLeaderboard();
}

// ─── AUTH ────────────────────────────────────────────────────────────────────
function updateUIForAuth() {
    const loginBtn = document.getElementById('login-btn');
    const userBadge = document.getElementById('user-badge');
    if (currentUser) {
        loginBtn.classList.add('hidden');
        userBadge.classList.remove('hidden');
        userBadge.classList.add('flex');
        document.getElementById('user-name-display').textContent = currentUser.full_name;
        document.getElementById('user-name-display').classList.remove('hidden');
        if (currentUser.current_streak > 0) {
            document.getElementById('streak-display').classList.remove('hidden');
            document.getElementById('streak-count').textContent = currentUser.current_streak;
        } else {
            document.getElementById('streak-display').classList.add('hidden');
        }
        document.getElementById('score-display').classList.remove('hidden');
        document.getElementById('score-count').textContent = currentUser.total_score;
    } else {
        loginBtn.classList.remove('hidden');
        userBadge.classList.add('hidden');
        userBadge.classList.remove('flex');
    }
}

async function loadProfile() {
    if (!authToken) return;
    try {
        currentUser = await apiFetch('/api/auth/me');
        updateUIForAuth();
    } catch (e) {
        authToken = null;
        localStorage.removeItem('pandi_token');
        currentUser = null;
        updateUIForAuth();
    }
}

async function loginUser() {
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;
    if (!email || !password) return showToast('Lütfen tüm alanları doldurun', 'error');
    try {
        const data = await apiFetch('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
        authToken = data.access_token;
        localStorage.setItem('pandi_token', authToken);
        await loadProfile();
        showToast(`Hoş geldin, ${currentUser.full_name}! 🐼`);
        showPage('home-page');
        loadDailyQuiz();
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function registerUser() {
    const full_name = document.getElementById('reg-name').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;
    const password2 = document.getElementById('reg-password2').value;
    if (!full_name || !email || !password) return showToast('Lütfen tüm alanları doldurun', 'error');
    if (password !== password2) return showToast('Şifreler eşleşmiyor', 'error');
    if (password.length < 6) return showToast('Şifre en az 6 karakter olmalı', 'error');
    try {
        const data = await apiFetch('/api/auth/register', {
            method: 'POST',
            body: JSON.stringify({ email, password, full_name }),
        });
        authToken = data.access_token;
        localStorage.setItem('pandi_token', authToken);
        await loadProfile();
        showToast(`Hoş geldin, ${currentUser.full_name}! 🎉`);
        showPage('home-page');
        loadDailyQuiz();
    } catch (e) {
        showToast(e.message, 'error');
    }
}

function logout() {
    authToken = null;
    localStorage.removeItem('pandi_token');
    currentUser = null;
    updateUIForAuth();
    showToast('Çıkış yapıldı');
    loadDailyQuiz();
}

// ─── QUIZ ───────────────────────────────────────────────────────────────────
async function loadDailyQuiz() {
    const qEl = document.getElementById('quiz-question');
    const oEl = document.getElementById('quiz-options');
    const msgEl = document.getElementById('quiz-message');
    msgEl.classList.add('hidden');
    try {
        quizData = await apiFetch('/api/quiz/daily');
        currentQuestionIdx = 0;
        renderQuizQuestion();
    } catch (e) {
        qEl.textContent = e.message || 'Quiz yüklenemedi';
        oEl.innerHTML = '';
    }
}

function renderQuizQuestion() {
    const qEl = document.getElementById('quiz-question');
    const oEl = document.getElementById('quiz-options');
    const msgEl = document.getElementById('quiz-message');
    msgEl.classList.add('hidden');
    if (!quizData || !quizData.questions || currentQuestionIdx >= quizData.questions.length) {
        if (!authToken) {
            document.getElementById('quiz-content').innerHTML = `
                <div class='text-center py-4'>
                    <i class='fas fa-lock text-3xl text-slate-300 mb-3'></i>
                    <p class='font-bold text-slate-500 italic'>Quiz'i göndermek için giriş yapın</p>
                    <button onclick="showPage('login-page')" class='mt-3 bg-blue-600 text-white px-6 py-2 rounded-xl font-bold text-sm'>Giriş Yap</button>
                </div>`;
            return;
        }
        submitQuiz();
        return;
    }
    const q = quizData.questions[currentQuestionIdx];
    qEl.textContent = `"${q.question_text}"`;
    oEl.innerHTML = '';
    q.options.forEach(opt => {
        const b = document.createElement('button');
        b.className = "w-full py-3 px-4 bg-white/80 border-2 border-slate-100 rounded-xl font-bold text-left hover:border-blue-400 transition-all shadow-sm";
        b.textContent = `${opt.label}) ${opt.option_text}`;
        b.onclick = () => {
            q._selected = opt.id;
            currentQuestionIdx++;
            renderQuizQuestion();
        };
        oEl.appendChild(b);
    });
}

async function submitQuiz() {
    if (!authToken) {
        document.getElementById('quiz-content').innerHTML = `
            <div class='text-center py-4'>
                <i class='fas fa-lock text-3xl text-slate-300 mb-3'></i>
                <p class='font-bold text-slate-500 italic'>Sonuçları görmek için giriş yapın</p>
                <button onclick="showPage('login-page')" class='mt-3 bg-blue-600 text-white px-6 py-2 rounded-xl font-bold text-sm'>Giriş Yap</button>
            </div>`;
        return;
    }
    const answers = quizData.questions.map(q => ({
        question_id: q.id,
        selected_option_id: q._selected || '',
    }));
    try {
        const result = await apiFetch('/api/quiz/submit', {
            method: 'POST',
            body: JSON.stringify({ quiz_id: quizData.id, answers }),
        });
        await loadProfile();
        document.getElementById('quiz-content').innerHTML = `
            <div class='text-center py-4'>
                <i class='fas fa-medal text-4xl text-yellow-500 mb-2'></i>
                <p class='font-black uppercase italic text-2xl'>${result.score}%</p>
                <p class='text-slate-500 font-bold'>${result.correct_count}/${result.total_questions} doğru</p>
                <p class='text-orange-500 font-black mt-2'><i class="fas fa-fire"></i> Seri: ${result.new_streak} gün</p>
            </div>`;
        showToast(`Quiz tamamlandı! Skor: ${result.score}%`);
    } catch (e) {
        showToast(e.message, 'error');
        document.getElementById('quiz-content').innerHTML = `
            <div class='text-center py-4'>
                <i class='fas fa-check-circle text-4xl text-emerald-500 mb-2'></i>
                <p class='font-black uppercase italic'>Bu quiz'i zaten çözdünüz!</p>
            </div>`;
    }
}

// ─── SYMPTOM ANALYSIS ───────────────────────────────────────────────────────
async function analyzeSymptoms() {
    const input = document.getElementById('complaint-input').value.trim();
    if (!input) return showToast('Lütfen önce şikayetinizi yazın', 'error');
    if (!authToken) return showToast('Analiz için giriş yapmanız gerekiyor', 'error');
    const symptoms = input.split(/[,\n]+/).map(s => s.trim()).filter(s => s.length > 0);
    try {
        const result = await apiFetch('/api/symptoms/analyze', {
            method: 'POST',
            body: JSON.stringify({ symptoms }),
        });
        showAnalysisResult(result);
    } catch (e) {
        showToast(e.message, 'error');
    }
}

function showAnalysisResult(result) {
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };
    let recsHTML = result.recommendations.map(r => `
        <div class="p-4 rounded-2xl border-l-4 ${r.warning ? 'border-red-500 bg-red-50' : 'border-blue-500 bg-blue-50'} mb-3">
            <div class="flex justify-between items-start">
                <h4 class="font-black text-lg">${r.department}</h4>
                <span class="text-xs font-bold px-2 py-1 rounded-full ${r.confidence === 'yüksek' ? 'bg-emerald-100 text-emerald-700' : r.confidence === 'orta' ? 'bg-yellow-100 text-yellow-700' : 'bg-slate-100 text-slate-600'}">${r.confidence}</span>
            </div>
            <p class="text-slate-600 text-sm mt-2">${r.description}</p>
            ${r.warning ? `<p class="text-red-600 font-bold text-sm mt-2">${r.warning}</p>` : ''}
            <a href="${r.enabiz_url}" target="_blank" class="text-blue-600 text-sm font-bold mt-2 inline-block hover:underline"><i class="fas fa-external-link-alt"></i> E-Nabız Randevu</a>
        </div>
    `).join('');
    overlay.innerHTML = `
        <div class="modal-content">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-2xl font-black uppercase">Analiz Sonucu</h3>
                <button onclick="this.closest('.modal-overlay').remove()" class="text-3xl text-slate-400 hover:text-red-500">&times;</button>
            </div>
            <p class="text-slate-500 text-sm mb-4"><strong>Belirtiler:</strong> ${result.input_symptoms.join(', ')}</p>
            ${recsHTML}
            <p class="text-xs text-slate-400 italic mt-4 p-3 bg-yellow-50 rounded-xl">${result.disclaimer}</p>
        </div>`;
    document.body.appendChild(overlay);
}

// ─── VOICE ASSISTANT ────────────────────────────────────────────────────────
function startVoiceAssistant() {
    const mascot = document.getElementById('mascot-trigger');
    const textarea = document.getElementById('complaint-input');
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SR();
        recognition.lang = 'tr-TR';
        recognition.continuous = false;
        mascot.classList.add('listening');
        textarea.placeholder = "Pandi dinliyor... Lütfen konuşun.";
        recognition.onresult = (e) => {
            textarea.value = e.results[0][0].transcript;
            mascot.classList.remove('listening');
            textarea.placeholder = "Şikayetinizi buraya yazın...";
        };
        recognition.onerror = () => {
            mascot.classList.remove('listening');
            textarea.placeholder = "Şikayetinizi buraya yazın...";
            showToast('Ses algılanamadı, lütfen tekrar deneyin', 'error');
        };
        recognition.onend = () => {
            mascot.classList.remove('listening');
            textarea.placeholder = "Şikayetinizi buraya yazın...";
        };
        recognition.start();
    } else {
        mascot.classList.add('listening');
        textarea.placeholder = "Pandi dinliyor... Lütfen konuşun.";
        setTimeout(() => {
            mascot.classList.remove('listening');
            textarea.value = "baş ağrısı, ateş, halsizlik";
            textarea.placeholder = "Şikayetinizi buraya yazın...";
        }, 3000);
    }
}

// ─── ARTICLES ───────────────────────────────────────────────────────────────
let articlesCache = [];
async function loadArticles(search = '') {
    const container = document.getElementById('articles-container');
    try {
        const url = search ? `/api/articles?search=${encodeURIComponent(search)}` : '/api/articles';
        const articles = await apiFetch(url);
        articlesCache = articles;
        if (articles.length === 0) {
            container.innerHTML = '<p class="text-slate-500 italic col-span-2">Makale bulunamadı.</p>';
            return;
        }
        const colors = { 'ilaç': 'blue', 'hastalık': 'emerald', 'terim': 'purple', 'genel': 'orange' };
        container.innerHTML = articles.map(a => {
            const c = colors[a.category] || 'slate';
            return `<div class="card-style p-8 rounded-3xl border-l-8 border-${c}-500 cursor-pointer hover:shadow-lg transition-all" onclick="showArticle('${a.slug}')">
                <span class="text-xs font-black uppercase bg-${c}-100 text-${c}-700 px-3 py-1 rounded-full">${a.category}</span>
                <h3 class="text-xl font-black text-slate-800 mt-3">${a.title}</h3>
                <p class="text-sm text-slate-400 mt-2">${new Date(a.created_at).toLocaleDateString('tr-TR')}</p>
            </div>`;
        }).join('');
    } catch (e) {
        container.innerHTML = '<p class="text-red-500 italic">Makaleler yüklenirken hata oluştu.</p>';
    }
}

function searchArticles() {
    const q = document.getElementById('article-search').value.trim();
    loadArticles(q);
}

async function showArticle(slug) {
    try {
        const article = await apiFetch(`/api/articles/${slug}`);
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };
        overlay.innerHTML = `
            <div class="modal-content">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-2xl font-black">${article.title}</h3>
                    <button onclick="this.closest('.modal-overlay').remove()" class="text-3xl text-slate-400 hover:text-red-500">&times;</button>
                </div>
                <div class="prose prose-slate max-w-none text-slate-700 leading-relaxed" style="white-space: pre-line;">${article.content}</div>
            </div>`;
        document.body.appendChild(overlay);
    } catch (e) {
        showToast(e.message, 'error');
    }
}

// ─── LEADERBOARD ────────────────────────────────────────────────────────────
async function loadLeaderboard() {
    const container = document.getElementById('leaderboard-container');
    try {
        const entries = await apiFetch('/api/quiz/leaderboard');
        if (entries.length === 0) {
            container.innerHTML = '<p class="text-slate-500 italic text-center">Henüz skor tablosunda kimse yok.</p>';
            return;
        }
        container.innerHTML = entries.map((e, i) => {
            const medal = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `${i + 1}.`;
            return `<div class="card-style p-5 rounded-2xl mb-3 flex items-center justify-between ${i < 3 ? 'border-l-4 border-yellow-400' : ''}">
                <div class="flex items-center gap-4">
                    <span class="text-2xl font-black w-10 text-center">${medal}</span>
                    <div>
                        <p class="font-black text-slate-800">${e.full_name}</p>
                        <p class="text-sm text-slate-400"><i class="fas fa-fire text-orange-400"></i> ${e.current_streak} gün seri</p>
                    </div>
                </div>
                <div class="text-right">
                    <p class="font-black text-2xl text-blue-600">${e.total_score}</p>
                    <p class="text-xs text-slate-400">puan</p>
                </div>
            </div>`;
        }).join('');
    } catch (e) {
        container.innerHTML = '<p class="text-red-500 italic">Yüklenirken hata oluştu.</p>';
    }
}

// ─── INIT ───────────────────────────────────────────────────────────────────
window.onload = async () => {
    await loadProfile();
    loadDailyQuiz();
};
