<template>
  <div class="landing-root">
    <!-- Ambient background -->
    <div class="bg-ambient">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3"></div>
      <div class="grid-overlay"></div>
    </div>

    <!-- ── NAVBAR (sticky) ─────────────────────────────────────────────── -->
    <nav class="navbar" :class="{ scrolled: navScrolled }">
      <div class="nav-inner">
        <div class="nav-brand">
          <img src="/logo.png" height="36" class="nav-logo" alt="JayPolyMind">
          <span class="brand-name">Jay<span class="brand-poly">Poly</span>Mind</span>
        </div>
        <div class="nav-links">
          <a href="#how-it-works" class="nav-link" @click.prevent="scrollTo('how-it-works')">Как работает</a>
          <a href="#technology" class="nav-link" @click.prevent="scrollTo('technology')">Технология</a>
          <a href="#pricing" class="nav-link" @click.prevent="scrollTo('pricing')">Цены</a>
        </div>
        <div class="nav-right">
          <button class="nav-login-btn" @click="goToApp">Войти &rarr;</button>
        </div>
        <button class="nav-burger" @click="mobileMenu = !mobileMenu" aria-label="Menu">
          <span></span><span></span><span></span>
        </button>
      </div>
      <!-- Mobile menu -->
      <div v-if="mobileMenu" class="mobile-menu">
        <a href="#how-it-works" @click.prevent="scrollTo('how-it-works'); mobileMenu = false">Как работает</a>
        <a href="#technology" @click.prevent="scrollTo('technology'); mobileMenu = false">Технология</a>
        <a href="#pricing" @click.prevent="scrollTo('pricing'); mobileMenu = false">Цены</a>
        <button class="nav-login-btn mobile" @click="goToApp">Войти &rarr;</button>
      </div>
    </nav>

    <!-- ── 1. HERO ─────────────────────────────────────────────────────── -->
    <section class="hero">
      <div class="hero-left">
        <div class="hero-inner">
          <div class="hero-tag">
            <span class="tag-dot"></span>
            Предиктивная аналитика поведения аудитории
          </div>
          <h1 class="hero-title">
            Узнайте реакцию рынка &mdash;<br>
            <span class="hero-accent">до того, как решение принято.</span>
          </h1>
          <p class="hero-desc">
            <strong>JayPolyMind</strong> моделирует поведение вашей аудитории на основе
            загруженной документации. Платформа создаёт сотни
            <span class="hl-blue">AI-агентов</span> &mdash; каждый с уникальным профилем,
            убеждениями и логикой поведения &mdash; и запускает полноценную симуляцию
            социальных реакций.
          </p>
          <div class="hero-ctas">
            <button class="btn-primary" @click="goToApp">
              <span>Начать симуляцию</span>
              <span class="btn-arrow">&rarr;</span>
            </button>
            <a href="#how-it-works" class="btn-ghost" @click.prevent="scrollTo('how-it-works')">
              Смотреть демо &darr;
            </a>
          </div>
          <div class="hero-kpi">
            <div class="kpi-item">
              <span class="kpi-val">x10</span>
              <span class="kpi-lbl">быстрее традиционных исследований</span>
            </div>
            <div class="kpi-sep"></div>
            <div class="kpi-item">
              <span class="kpi-val">1000+</span>
              <span class="kpi-lbl">агентов в одной симуляции</span>
            </div>
            <div class="kpi-sep"></div>
            <div class="kpi-item">
              <span class="kpi-val">Часы</span>
              <span class="kpi-lbl">от документа до отчёта</span>
            </div>
          </div>
        </div>
      </div>
      <div class="hero-right">
        <div class="hero-orb hero-orb-1"></div>
        <div class="hero-orb hero-orb-2"></div>
        <div class="logo-showcase">
          <div class="logo-glow"></div>
          <img src="/logo.png" class="logo-img" alt="JayPolyMind">
        </div>
      </div>
    </section>

    <main class="main-wrap">

      <!-- ── 2. PROBLEM ──────────────────────────────────────────────────── -->
      <section class="section pain-section" v-observe>
        <div class="section-head">
          <span class="section-eyebrow">Проблема</span>
          <h2 class="section-title">Решения принимаются вслепую</h2>
          <p class="section-sub">Традиционные методы тестирования реакций дороги, медленны и ненадёжны</p>
        </div>
        <div class="pain-grid">
          <div class="pain-card" v-for="(p, i) in pains" :key="i">
            <div class="pain-icon">{{ p.icon }}</div>
            <h3 class="pain-title">{{ p.title }}</h3>
            <p class="pain-desc">{{ p.desc }}</p>
            <div class="pain-stat">{{ p.stat }}</div>
          </div>
        </div>
      </section>

      <!-- ── 3. USE CASES ────────────────────────────────────────────────── -->
      <section class="section" v-observe>
        <div class="section-head">
          <span class="section-eyebrow">Применение</span>
          <h2 class="section-title">Где работает JayPolyMind</h2>
        </div>
        <div class="cases-grid">
          <div v-for="(uc, i) in useCases" :key="i" class="case-card">
            <div class="case-num">{{ String(i + 1).padStart(2, '0') }}</div>
            <h3 class="case-title">{{ uc.title }}</h3>
            <p class="case-desc">{{ uc.desc }}</p>
          </div>
        </div>
      </section>

      <!-- ── 4. HOW IT WORKS ─────────────────────────────────────────────── -->
      <section id="how-it-works" class="section" v-observe>
        <div class="section-head">
          <span class="section-eyebrow">Процесс</span>
          <h2 class="section-title">Пять шагов от документа до прогноза</h2>
        </div>
        <div class="steps-timeline">
          <div class="timeline-line"></div>
          <div v-for="(step, i) in steps" :key="i" class="step-item" :class="{ reverse: i % 2 === 1 }">
            <div class="step-content">
              <div class="step-num-badge">{{ step.num }}</div>
              <h4 class="step-name">{{ step.title }}</h4>
              <p class="step-detail">{{ step.desc }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- ── 5. METRICS ──────────────────────────────────────────────────── -->
      <section class="section metrics-section" v-observe>
        <div class="section-head">
          <span class="section-eyebrow">Эффективность</span>
          <h2 class="section-title">Цифры говорят сами</h2>
        </div>
        <div class="metrics-grid">
          <div class="metric-card" v-for="(m, i) in metrics" :key="i">
            <div class="metric-val">{{ m.val }}</div>
            <div class="metric-lbl">{{ m.label }}</div>
          </div>
        </div>
        <div class="compare-table-wrap">
          <table class="compare-table">
            <thead>
              <tr>
                <th>Критерий</th>
                <th>Фокус-группы</th>
                <th>Опросы</th>
                <th>ChatGPT</th>
                <th class="highlight-col">JayPolyMind</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, i) in compareRows" :key="i">
                <td class="compare-label">{{ row.label }}</td>
                <td>{{ row.focus }}</td>
                <td>{{ row.survey }}</td>
                <td>{{ row.chatgpt }}</td>
                <td class="highlight-col">{{ row.jpm }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ── 6. TECHNOLOGY ───────────────────────────────────────────────── -->
      <section id="technology" class="section" v-observe>
        <div class="section-head">
          <span class="section-eyebrow">Технология</span>
          <h2 class="section-title">Не просто чат-бот</h2>
          <p class="section-sub">Многослойная архитектура для реалистичной симуляции</p>
        </div>
        <div class="tech-grid">
          <div class="tech-card" v-for="(t, i) in techFeatures" :key="i">
            <div class="tech-icon">{{ t.icon }}</div>
            <h3 class="tech-title">{{ t.title }}</h3>
            <p class="tech-desc">{{ t.desc }}</p>
          </div>
        </div>
      </section>

      <!-- ── 7. DEMO CASES ───────────────────────────────────────────────── -->
      <section class="section" v-observe>
        <div class="section-head">
          <span class="section-eyebrow">Кейсы</span>
          <h2 class="section-title">Посмотрите в действии</h2>
        </div>
        <div class="demo-grid">
          <div v-for="(d, i) in demoCases" :key="i" class="demo-card">
            <div class="demo-badge">{{ d.tag }}</div>
            <h3 class="demo-title">{{ d.title }}</h3>
            <p class="demo-desc">{{ d.desc }}</p>
            <button class="demo-btn" @click="goToApp">Запустить демо &rarr;</button>
          </div>
        </div>
      </section>

      <!-- ── 8. PRICING (Pay-as-you-go) ──────────────────────────────────── -->
      <section id="pricing" class="section pricing-section" v-observe>
        <div class="section-head">
          <span class="section-eyebrow">Тарификация</span>
          <h2 class="section-title">Платите только за то, что используете</h2>
          <p class="section-sub">Без подписок. Пополните баланс &mdash; запускайте симуляции. Платите за токены.</p>
        </div>

        <div class="pricing-layout">
          <!-- Calculator -->
          <div class="calc-card">
            <h3 class="calc-title">Калькулятор стоимости</h3>
            <div class="calc-row">
              <label class="calc-label">Агентов: <strong>{{ agents }}</strong></label>
              <input type="range" v-model.number="agents" min="10" max="100" step="5" class="calc-slider">
              <div class="calc-range"><span>10</span><span>100</span></div>
            </div>
            <div class="calc-row">
              <label class="calc-label">Раундов: <strong>{{ rounds }}</strong></label>
              <input type="range" v-model.number="rounds" min="3" max="10" step="1" class="calc-slider">
              <div class="calc-range"><span>3</span><span>10</span></div>
            </div>
            <div class="calc-result">
              <div class="calc-result-row">
                <span>Симуляция</span>
                <span class="calc-price">${{ simPrice }}</span>
              </div>
              <div class="calc-result-row sub">
                <span>+ Отчёт</span>
                <span>~$2.00</span>
              </div>
              <div class="calc-result-row sub">
                <span>+ Интервью (10 агентов)</span>
                <span>~$1.00</span>
              </div>
              <div class="calc-divider"></div>
              <div class="calc-result-row total">
                <span>Итого</span>
                <span class="calc-total">${{ totalPrice }}</span>
              </div>
            </div>
            <button class="btn-primary calc-cta" @click="goToApp">Пополнить баланс &rarr;</button>
          </div>

          <!-- Presets -->
          <div class="presets">
            <div v-for="(pr, i) in presets" :key="i" class="preset-card" @click="agents = pr.agents; rounds = pr.rounds">
              <div class="preset-name">{{ pr.name }}</div>
              <div class="preset-config">{{ pr.agents }} агентов &middot; {{ pr.rounds }} раундов</div>
              <div class="preset-price">~${{ pr.price }}</div>
            </div>
            <div class="bonus-card">
              <div class="bonus-title">Бонусы при пополнении</div>
              <div class="bonus-row"><span>от $50</span><span class="bonus-val">+10%</span></div>
              <div class="bonus-row"><span>от $200</span><span class="bonus-val">+20%</span></div>
            </div>
          </div>
        </div>
      </section>

      <!-- ── 9. STACK + ROADMAP ──────────────────────────────────────────── -->
      <section class="section" v-observe>
        <div class="section-head">
          <span class="section-eyebrow">Фундамент</span>
          <h2 class="section-title">Построено на надёжном стеке</h2>
        </div>
        <div class="stack-bar">
          <div v-for="(s, i) in stack" :key="i" class="stack-item">
            <span class="stack-name">{{ s.name }}</span>
            <span class="stack-role">{{ s.role }}</span>
          </div>
        </div>

        <div class="roadmap-head">
          <span class="section-eyebrow">Roadmap</span>
          <h2 class="section-title">Что дальше</h2>
        </div>
        <div class="roadmap-grid">
          <div v-for="(r, i) in roadmap" :key="i" class="roadmap-card">
            <div class="roadmap-period">{{ r.period }}</div>
            <ul class="roadmap-list">
              <li v-for="(item, j) in r.items" :key="j">{{ item }}</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- ── 10. FOOTER CTA ──────────────────────────────────────────────── -->
      <section class="cta-section" v-observe>
        <div class="cta-inner">
          <span class="section-eyebrow">Готовы к запуску?</span>
          <h2 class="cta-title">Протестируйте реакцию на ваш документ</h2>
          <p class="cta-desc">Загрузите документ, настройте агентов и получите прогноз за минуты.</p>
          <div class="cta-buttons">
            <button class="btn-primary" @click="goToApp">
              <span>Начать бесплатно</span>
              <span class="btn-arrow">&rarr;</span>
            </button>
          </div>
        </div>
      </section>

      <!-- ── FOOTER ──────────────────────────────────────────────────────── -->
      <footer class="footer">
        <div class="footer-inner">
          <div class="footer-brand">
            <img src="/logo.png" height="28" alt="JayPolyMind">
            <span class="brand-name sm">Jay<span class="brand-poly">Poly</span>Mind</span>
          </div>
          <div class="footer-links">
            <a href="#how-it-works" @click.prevent="scrollTo('how-it-works')">Как работает</a>
            <a href="#technology" @click.prevent="scrollTo('technology')">Технология</a>
            <a href="#pricing" @click.prevent="scrollTo('pricing')">Цены</a>
          </div>
          <div class="footer-copy">&copy; 2026 JayPolyMind. All rights reserved.</div>
        </div>
      </footer>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { isAuthenticated } from '../store/auth.js'

// ── Navigation ─────────────────────────────────────────────────────────────
const router = useRouter()
const navScrolled = ref(false)
const mobileMenu = ref(false)

function goToApp() {
  router.push(isAuthenticated() ? { name: 'App' } : { name: 'Login' })
}

function scrollTo(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}

function onScroll() {
  navScrolled.value = window.scrollY > 40
}

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))

// ── Scroll-reveal directive ────────────────────────────────────────────────
const vObserve = {
  mounted(el) {
    el.classList.add('reveal')
    const obs = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        el.classList.add('visible')
        obs.disconnect()
      }
    }, { threshold: 0.12 })
    obs.observe(el)
  }
}

// ── Pricing calculator ─────────────────────────────────────────────────────
const agents = ref(50)
const rounds = ref(5)

const simPrice = computed(() => {
  const tokens = agents.value * rounds.value * 40000
  const cost = (tokens / 1000000) * 4.50
  return cost.toFixed(2)
})

const totalPrice = computed(() => {
  return (parseFloat(simPrice.value) + 3.00).toFixed(2)
})

const presets = [
  { name: 'Быстрый тест', agents: 20, rounds: 3, price: '2' },
  { name: 'Стандарт', agents: 50, rounds: 5, price: '8' },
  { name: 'Глубокий анализ', agents: 100, rounds: 10, price: '30' },
]

// ── Static data ────────────────────────────────────────────────────────────
const pains = [
  {
    icon: '\u{1F4B8}',
    title: 'Фокус-группы',
    desc: 'Дорого, долго и мало участников. Нерепрезентативная выборка из 8-15 человек.',
    stat: '$5K - $50K за сессию'
  },
  {
    icon: '\u{1F50D}',
    title: 'Опросы',
    desc: 'Респонденты отвечают "как надо", а не как думают. Социальная желательность искажает данные.',
    stat: '2-4 недели на результат'
  },
  {
    icon: '\u{26A0}\u{FE0F}',
    title: 'Публикация вслепую',
    desc: 'Без предварительного теста ошибка сразу на виду у аудитории. PR-кризис может стоить миллионы.',
    stat: '$1M+ потенциальных потерь'
  }
]

const useCases = [
  { title: 'Регуляторные изменения', desc: 'Оцените восприятие новых норм до их введения по каждому сегменту аудитории' },
  { title: 'Внутренние трансформации', desc: 'Смоделируйте реакцию команды на реструктуризацию, слияние или смену стратегии' },
  { title: 'Запуск коммуникаций', desc: 'Протестируйте месседжи и позиционирование до публичного выхода' },
  { title: 'Вывод продукта на рынок', desc: 'Предскажите поведение сегментов и выявите точки сопротивления заранее' },
]

const steps = [
  { num: '01', title: 'Граф знаний', desc: 'Платформа анализирует документ, выделяет сущности, факты и связи между ними' },
  { num: '02', title: 'Профили агентов', desc: 'LLM создаёт психологические портреты: MBTI, возраст, профессия, предубеждения' },
  { num: '03', title: 'Симуляция', desc: 'Агенты обсуждают на Twitter и Reddit, публикуют, комментируют, меняют мнения' },
  { num: '04', title: 'Аналитический отчёт', desc: 'ReportAgent синтезирует итоги: сентимент, ключевые инсайты, зоны риска' },
  { num: '05', title: 'Углублённый диалог', desc: 'Задавайте вопросы любому агенту: "Почему ты так отреагировал?"' },
]

const metrics = [
  { val: 'x200', label: 'быстрее фокус-групп' },
  { val: 'x100', label: 'дешевле традиционных исследований' },
  { val: '100+', label: 'AI-агентов за один запуск' },
  { val: '5', label: 'архетипов личностей' },
]

const compareRows = [
  { label: 'Время', focus: '2-4 недели', survey: '1-4 недели', chatgpt: '5 минут', jpm: '10-15 минут' },
  { label: 'Стоимость', focus: '$5K-50K', survey: '$10K-100K', chatgpt: '~$0.10', jpm: '$2-30' },
  { label: 'Респонденты', focus: '8-15', survey: '100-1000', chatgpt: '1', jpm: '50-100+' },
  { label: 'Динамика', focus: 'Есть', survey: 'Нет', chatgpt: 'Нет', jpm: 'Есть' },
  { label: 'Воспроизводимость', focus: 'Нет', survey: 'Частичная', chatgpt: 'Нет', jpm: '100%' },
]

const techFeatures = [
  { icon: '\u{1F578}\u{FE0F}', title: 'Граф знаний', desc: 'Документ разбирается в структурированный граф сущностей в Neo4j, а не просто передаётся как текст' },
  { icon: '\u{1F9E0}', title: 'Психопрофили', desc: 'Каждый агент имеет MBTI-тип, возраст, профессию и уникальные предубеждения' },
  { icon: '\u{1F4F1}', title: 'Dual-platform', desc: 'Одновременная симуляция на Twitter (быстрые реакции) и Reddit (глубокие дискуссии)' },
  { icon: '\u{1F504}', title: 'Эволюция мнений', desc: 'Агенты меняют позицию под влиянием аргументов других участников, как реальные люди' },
]

const demoCases = [
  { tag: 'Продукт', title: 'Запуск нового продукта', desc: 'Как отреагирует рынок на ваш анонс? Агенты-скептики, эксперты и энтузиасты покажут реальную картину.' },
  { tag: 'Регуляторика', title: 'Регуляторный анализ', desc: 'Оцените реакцию стейкхолдеров на новые нормы и требования до их официального введения.' },
  { tag: 'HR', title: 'Корпоративная трансформация', desc: 'Протестируйте внутренние коммуникации о реструктуризации, слиянии или смене стратегии.' },
]

const stack = [
  { name: 'Vue 3', role: 'Frontend' },
  { name: 'Flask', role: 'Backend' },
  { name: 'Neo4j', role: 'Graph DB' },
  { name: 'CAMEL-AI', role: 'Agents' },
  { name: 'OASIS', role: 'Simulation' },
  { name: 'OpenRouter', role: 'LLM API' },
  { name: 'Docker', role: 'Deploy' },
]

const roadmap = [
  { period: 'Сейчас', items: ['MVP + демо-кейсы', 'Лендинг-презентация', 'Pay-as-you-go биллинг'] },
  { period: 'Q3 2026', items: ['Multi-language (RU/EN)', 'A/B симуляции', 'Slack-интеграция'] },
  { period: 'Q4 2026', items: ['REST API для партнёров', 'Отраслевые шаблоны агентов', 'Расширенная аналитика'] },
  { period: '2027', items: ['On-premise (Ollama)', 'Плагин Google Docs / Notion', 'Предиктивная модель'] },
]
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Unbounded:wght@400;700;900&family=Onest:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Tokens ──────────────────────────────────────────────────────────────── */
:root {
  --bg:       #060814;
  --bg2:      #0A0F1E;
  --bg3:      #0F1625;
  --acc1:     #3B82F6;
  --acc2:     #38BDF8;
  --txt:      #EFF6FF;
  --txt2:     #7FA4C4;
  --txt3:     #3A5570;
  --border:   rgba(59,130,246,0.15);
  --border-h: rgba(59,130,246,0.4);
  --mono:     'JetBrains Mono', monospace;
  --display:  'Unbounded', sans-serif;
  --body:     'Onest', sans-serif;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

.landing-root {
  min-height: 100vh;
  background: var(--bg);
  color: var(--txt);
  font-family: var(--body);
  overflow-x: hidden;
}

/* ── Scroll reveal ───────────────────────────────────────────────────────── */
.reveal {
  opacity: 0;
  transform: translateY(32px);
  transition: opacity 0.7s ease, transform 0.7s ease;
}
.reveal.visible {
  opacity: 1;
  transform: translateY(0);
}

/* ── Ambient bg ──────────────────────────────────────────────────────────── */
.bg-ambient { position: fixed; inset: 0; z-index: 0; pointer-events: none; }
.orb {
  position: absolute; border-radius: 50%;
  filter: blur(130px); opacity: 0.10;
}
.orb-1 { width: 800px; height: 800px; background: #3B82F6; top: -300px; left: -200px; }
.orb-2 { width: 600px; height: 600px; background: #0EA5E9; bottom: -100px; right: -150px; }
.orb-3 { width: 400px; height: 400px; background: #6366F1; top: 50%; left: 50%; transform: translate(-50%, -50%); opacity: 0.05; }
.grid-overlay {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(59,130,246,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59,130,246,0.04) 1px, transparent 1px);
  background-size: 64px 64px;
}

/* ── Navbar ──────────────────────────────────────────────────────────────── */
.navbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid #EAEAEA;
  transition: box-shadow 0.3s;
}
.navbar.scrolled {
  box-shadow: 0 2px 20px rgba(0,0,0,0.08);
}
.nav-inner {
  max-width: 1400px; margin: 0 auto;
  height: 68px;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 52px;
}
.nav-brand { display: flex; align-items: center; gap: 12px; }
.nav-logo { object-fit: contain; }
.brand-name {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.05rem; font-weight: 800;
  letter-spacing: 0.5px; color: #111111;
}
.brand-name.sm { font-size: 0.9rem; color: #EFF6FF; }
.brand-poly { color: #38BDF8; }
.nav-links { display: flex; gap: 36px; margin-left: 64px; flex-shrink: 0; }
.nav-link {
  font-family: var(--mono);
  font-size: 0.78rem; color: #64748B;
  text-decoration: none; font-weight: 500;
  transition: color 0.2s;
}
.nav-link:hover { color: #1D4ED8; }
.nav-right { display: flex; align-items: center; gap: 20px; }
.nav-login-btn {
  font-family: var(--mono); font-size: 0.8rem;
  color: #1D4ED8; background: rgba(29,78,216,0.06);
  border: 1px solid rgba(29,78,216,0.25);
  border-radius: 6px; padding: 7px 18px; cursor: pointer;
  transition: all .2s; font-weight: 600;
}
.nav-login-btn:hover { background: rgba(29,78,216,0.12); border-color: #1D4ED8; }
.nav-burger { display: none; background: none; border: none; cursor: pointer; padding: 4px; flex-direction: column; gap: 5px; }
.nav-burger span { display: block; width: 22px; height: 2px; background: #111; border-radius: 1px; }
.mobile-menu {
  display: none;
  flex-direction: column; gap: 16px;
  padding: 20px 52px 24px;
  border-top: 1px solid #EAEAEA;
}
.mobile-menu a {
  font-family: var(--mono); font-size: 0.85rem;
  color: #374151; text-decoration: none; font-weight: 500;
}

/* ── HERO ────────────────────────────────────────────────────────────────── */
.hero {
  display: flex;
  min-height: 100vh;
  position: relative;
  z-index: 1;
  margin-top: 68px;
}
.hero-left {
  flex: 1;
  background: #F8FAFF;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 88px 80px 88px max(52px, calc(50vw - 720px));
}
.hero-inner { max-width: 600px; width: 100%; }
.hero-right {
  flex: 0 0 44%;
  background: #060E1C;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}
.hero-orb {
  position: absolute; border-radius: 50%;
  filter: blur(100px); pointer-events: none;
}
.hero-orb-1 {
  width: 520px; height: 520px;
  background: #1D4ED8; opacity: 0.45;
  top: -160px; left: -120px;
}
.hero-orb-2 {
  width: 380px; height: 380px;
  background: #0EA5E9; opacity: 0.3;
  bottom: -80px; right: -80px;
}
.hero-tag {
  display: inline-flex; align-items: center; gap: 9px;
  font-family: var(--mono); font-size: 0.72rem;
  color: #2563EB;
  border: 1px solid rgba(37,99,235,0.25);
  padding: 5px 16px; border-radius: 20px;
  margin-bottom: 32px;
  background: rgba(37,99,235,0.05);
}
.tag-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: #3B82F6;
  animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
.hero-title {
  font-family: var(--display);
  font-size: clamp(2rem, 3.2vw, 3rem);
  font-weight: 700; line-height: 1.15;
  letter-spacing: -1.5px;
  color: #0F172A;
  margin-bottom: 24px;
}
.hero-accent { color: #1E40AF; display: block; }
.hero-desc {
  font-size: 1rem; line-height: 1.8;
  color: #475569; max-width: 560px;
  margin-bottom: 28px;
}
.hero-desc strong { color: #0F172A; font-weight: 600; }
.hl-blue { color: #2563EB; font-weight: 500; }
.hero-ctas {
  display: flex; gap: 16px; align-items: center;
  margin-bottom: 44px;
}
.btn-primary {
  display: inline-flex; align-items: center; gap: 10px;
  background: linear-gradient(135deg, #1D4ED8 0%, #3B82F6 50%, #0EA5E9 100%);
  color: #fff; border: none;
  border-radius: 8px; padding: 14px 28px;
  font-family: var(--display);
  font-size: 0.88rem; font-weight: 700;
  cursor: pointer;
  transition: opacity .2s, transform .15s;
  box-shadow: 0 4px 24px rgba(59,130,246,0.35);
}
.btn-primary:hover { opacity: 0.9; transform: translateY(-2px); }
.btn-arrow { font-size: 1.1rem; }
.btn-ghost {
  font-family: var(--mono); font-size: 0.82rem;
  color: #2563EB; text-decoration: none;
  border: 1px solid rgba(37,99,235,0.3);
  padding: 12px 24px; border-radius: 8px;
  transition: all 0.2s; font-weight: 500;
}
.btn-ghost:hover { background: rgba(37,99,235,0.06); border-color: #2563EB; }
.hero-kpi { display: flex; align-items: center; gap: 32px; }
.kpi-item { display: flex; flex-direction: column; gap: 4px; }
.kpi-val {
  font-family: var(--display);
  font-size: 1.4rem; font-weight: 700; color: #0F172A;
}
.kpi-lbl { font-size: 0.78rem; color: #94A3B8; max-width: 120px; line-height: 1.4; }
.kpi-sep { width: 1px; height: 36px; background: rgba(0,0,0,0.1); }
.logo-showcase {
  position: relative;
  width: 420px; height: 420px;
  display: flex; align-items: center; justify-content: center;
  z-index: 1;
}
.logo-glow {
  position: absolute; inset: -40px;
  background: radial-gradient(circle at 50% 50%,
    rgba(59,130,246,0.55) 0%,
    rgba(14,165,233,0.25) 45%,
    transparent 70%
  );
  border-radius: 50%;
  animation: glowPulse 4s ease-in-out infinite;
}
@keyframes glowPulse {
  0%,100% { opacity: 0.75; transform: scale(1); }
  50%     { opacity: 1;    transform: scale(1.08); }
}
.logo-img {
  width: 420px; height: 420px;
  object-fit: contain;
  animation: float 6s ease-in-out infinite;
  filter:
    drop-shadow(0 0 40px rgba(59,130,246,0.75))
    drop-shadow(0 0 80px rgba(14,165,233,0.4));
}
@keyframes float {
  0%,100% { transform: translateY(0); }
  50%     { transform: translateY(-14px); }
}

/* ── Main wrap ───────────────────────────────────────────────────────────── */
.main-wrap {
  position: relative; z-index: 1;
  max-width: 1360px; margin: 0 auto;
  padding: 0 52px 0;
}

/* ── Section (shared) ────────────────────────────────────────────────────── */
.section {
  padding: 100px 0;
  border-top: 1px solid rgba(59,130,246,0.08);
}
.section-head { margin-bottom: 56px; }
.section-eyebrow {
  font-family: var(--mono);
  font-size: 0.7rem; color: var(--acc1);
  letter-spacing: 2px; text-transform: uppercase;
  display: block; margin-bottom: 12px;
}
.section-title {
  font-family: var(--display);
  font-size: clamp(1.5rem, 2.5vw, 2.2rem);
  font-weight: 700; color: var(--txt);
  letter-spacing: -0.5px;
}
.section-sub {
  font-size: 1rem; color: var(--txt2);
  margin-top: 12px; max-width: 560px; line-height: 1.6;
}

/* ── PAIN SECTION ────────────────────────────────────────────────────────── */
.pain-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}
.pain-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 32px 28px;
  transition: border-color 0.3s, transform 0.2s;
  position: relative;
  overflow: hidden;
}
.pain-card::after {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, #F59E0B, #EF4444);
  opacity: 0; transition: opacity 0.3s;
}
.pain-card:hover { border-color: rgba(245,158,11,0.3); transform: translateY(-4px); }
.pain-card:hover::after { opacity: 1; }
.pain-icon { font-size: 2rem; margin-bottom: 16px; }
.pain-title {
  font-family: var(--display);
  font-size: 1rem; font-weight: 700;
  color: var(--txt); margin-bottom: 10px;
}
.pain-desc { font-size: 0.88rem; color: var(--txt2); line-height: 1.65; margin-bottom: 16px; }
.pain-stat {
  font-family: var(--mono); font-size: 0.75rem;
  color: #F59E0B; font-weight: 600;
  padding: 6px 12px;
  background: rgba(245,158,11,0.08);
  border: 1px solid rgba(245,158,11,0.2);
  border-radius: 6px;
  display: inline-block;
}

/* ── USE CASES ───────────────────────────────────────────────────────────── */
.cases-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}
.case-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 28px 24px;
  position: relative;
  overflow: hidden;
  transition: border-color .25s, transform .2s;
}
.case-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, var(--acc1), var(--acc2));
  opacity: 0; transition: opacity .25s;
}
.case-card:hover { border-color: var(--border-h); transform: translateY(-3px); }
.case-card:hover::before { opacity: 1; }
.case-num {
  font-family: var(--mono); font-size: 0.7rem;
  color: var(--acc1); margin-bottom: 16px; font-weight: 600;
}
.case-title {
  font-family: var(--display);
  font-size: 0.92rem; font-weight: 700;
  color: var(--txt); margin-bottom: 10px; line-height: 1.3;
}
.case-desc { font-size: 0.85rem; color: var(--txt2); line-height: 1.6; }

/* ── HOW IT WORKS (timeline) ─────────────────────────────────────────────── */
.steps-timeline {
  position: relative;
  max-width: 800px;
  margin: 0 auto;
}
.timeline-line {
  position: absolute;
  left: 19px; top: 0; bottom: 0;
  width: 2px;
  background: linear-gradient(180deg, var(--acc1), var(--acc2), transparent);
}
.step-item {
  display: flex;
  padding: 0 0 48px 0;
  position: relative;
}
.step-item:last-child { padding-bottom: 0; }
.step-content {
  margin-left: 52px;
  padding: 24px 28px;
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 12px;
  flex: 1;
  transition: border-color 0.3s, transform 0.2s;
}
.step-content:hover { border-color: var(--border-h); transform: translateX(4px); }
.step-num-badge {
  position: absolute;
  left: 0; top: 24px;
  width: 40px; height: 40px;
  border-radius: 50%;
  background: var(--bg);
  border: 2px solid var(--acc1);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--mono); font-size: 0.72rem; font-weight: 600;
  color: var(--acc1);
  z-index: 2;
}
.step-name {
  font-family: var(--display);
  font-size: 0.95rem; font-weight: 700;
  color: var(--txt); margin-bottom: 8px;
}
.step-detail { font-size: 0.85rem; color: var(--txt2); line-height: 1.6; }

/* ── METRICS ─────────────────────────────────────────────────────────────── */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 56px;
}
.metric-card {
  text-align: center;
  padding: 36px 20px;
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 16px;
  transition: border-color 0.3s;
}
.metric-card:hover { border-color: var(--border-h); }
.metric-val {
  font-family: var(--display);
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 900;
  background: linear-gradient(135deg, var(--acc1), var(--acc2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
}
.metric-lbl { font-size: 0.85rem; color: var(--txt2); }

/* Compare table */
.compare-table-wrap {
  overflow-x: auto;
  border-radius: 12px;
  border: 1px solid var(--border);
}
.compare-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}
.compare-table th {
  font-family: var(--mono);
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--txt3);
  padding: 16px 20px;
  text-align: left;
  background: var(--bg2);
  border-bottom: 1px solid var(--border);
  font-weight: 600;
}
.compare-table td {
  padding: 14px 20px;
  color: var(--txt2);
  border-bottom: 1px solid rgba(59,130,246,0.06);
}
.compare-label { color: var(--txt); font-weight: 500; }
.highlight-col {
  color: var(--acc2) !important;
  font-weight: 600 !important;
  background: rgba(56,189,248,0.04);
}

/* ── TECHNOLOGY ──────────────────────────────────────────────────────────── */
.tech-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}
.tech-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 36px 32px;
  transition: border-color 0.3s, transform 0.2s;
}
.tech-card:hover { border-color: var(--border-h); transform: translateY(-4px); }
.tech-icon { font-size: 2rem; margin-bottom: 16px; }
.tech-title {
  font-family: var(--display);
  font-size: 1rem; font-weight: 700;
  color: var(--txt); margin-bottom: 10px;
}
.tech-desc { font-size: 0.88rem; color: var(--txt2); line-height: 1.65; }

/* ── DEMO CASES ──────────────────────────────────────────────────────────── */
.demo-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}
.demo-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 32px 28px;
  display: flex; flex-direction: column;
  transition: border-color 0.3s, transform 0.2s;
}
.demo-card:hover { border-color: var(--border-h); transform: translateY(-4px); }
.demo-badge {
  font-family: var(--mono); font-size: 0.68rem;
  color: var(--acc2); font-weight: 600;
  text-transform: uppercase; letter-spacing: 1.5px;
  margin-bottom: 16px;
}
.demo-title {
  font-family: var(--display);
  font-size: 1rem; font-weight: 700;
  color: var(--txt); margin-bottom: 10px;
}
.demo-desc {
  font-size: 0.85rem; color: var(--txt2); line-height: 1.6;
  flex: 1; margin-bottom: 20px;
}
.demo-btn {
  font-family: var(--mono); font-size: 0.78rem;
  color: var(--acc1); background: transparent;
  border: 1px solid rgba(59,130,246,0.3);
  border-radius: 8px; padding: 10px 16px;
  cursor: pointer; transition: all 0.2s;
  font-weight: 600; text-align: center;
}
.demo-btn:hover { background: rgba(59,130,246,0.08); border-color: var(--acc1); }

/* ── PRICING ─────────────────────────────────────────────────────────────── */
.pricing-layout {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 32px;
  align-items: start;
}
.calc-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 40px 36px;
}
.calc-title {
  font-family: var(--display);
  font-size: 1.1rem; font-weight: 700;
  color: var(--txt); margin-bottom: 32px;
}
.calc-row { margin-bottom: 28px; }
.calc-label {
  font-size: 0.88rem; color: var(--txt2);
  display: block; margin-bottom: 10px;
}
.calc-label strong { color: var(--acc2); font-weight: 700; }
.calc-slider {
  width: 100%;
  -webkit-appearance: none;
  appearance: none;
  height: 6px;
  border-radius: 3px;
  background: linear-gradient(90deg, var(--acc1), var(--acc2));
  outline: none;
  cursor: pointer;
}
.calc-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 22px; height: 22px;
  border-radius: 50%;
  background: #fff;
  border: 3px solid var(--acc1);
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(59,130,246,0.3);
}
.calc-slider::-moz-range-thumb {
  width: 22px; height: 22px;
  border-radius: 50%;
  background: #fff;
  border: 3px solid var(--acc1);
  cursor: pointer;
}
.calc-range {
  display: flex; justify-content: space-between;
  font-family: var(--mono); font-size: 0.68rem;
  color: var(--txt3); margin-top: 6px;
}
.calc-result {
  background: rgba(59,130,246,0.05);
  border: 1px solid rgba(59,130,246,0.15);
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 24px;
}
.calc-result-row {
  display: flex; justify-content: space-between;
  font-size: 0.9rem; color: var(--txt2);
  padding: 6px 0;
}
.calc-result-row.sub { font-size: 0.8rem; color: var(--txt3); }
.calc-result-row.total {
  font-size: 1.1rem; font-weight: 700; color: var(--txt);
  padding-top: 12px;
}
.calc-price { color: var(--acc2); font-weight: 600; font-family: var(--mono); }
.calc-total {
  font-family: var(--display); font-size: 1.3rem;
  background: linear-gradient(135deg, var(--acc1), var(--acc2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.calc-divider { height: 1px; background: var(--border); margin: 8px 0; }
.calc-cta { width: 100%; justify-content: center; }

/* Presets */
.presets { display: flex; flex-direction: column; gap: 16px; }
.preset-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px 24px;
  cursor: pointer;
  transition: border-color 0.3s, transform 0.2s;
}
.preset-card:hover { border-color: var(--border-h); transform: translateX(4px); }
.preset-name {
  font-family: var(--display);
  font-size: 0.9rem; font-weight: 700;
  color: var(--txt); margin-bottom: 4px;
}
.preset-config { font-size: 0.78rem; color: var(--txt3); margin-bottom: 8px; }
.preset-price {
  font-family: var(--mono); font-size: 1.1rem;
  color: var(--acc2); font-weight: 700;
}
.bonus-card {
  background: linear-gradient(135deg, rgba(29,78,216,0.12), rgba(14,165,233,0.08));
  border: 1px solid rgba(59,130,246,0.25);
  border-radius: 12px;
  padding: 20px 24px;
}
.bonus-title {
  font-family: var(--display);
  font-size: 0.82rem; font-weight: 700;
  color: var(--txt); margin-bottom: 12px;
}
.bonus-row {
  display: flex; justify-content: space-between;
  font-size: 0.85rem; color: var(--txt2);
  padding: 4px 0;
}
.bonus-val { color: #34D399; font-weight: 700; font-family: var(--mono); }

/* ── STACK ────────────────────────────────────────────────────────────────── */
.stack-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 80px;
}
.stack-item {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px 22px;
  display: flex; flex-direction: column; gap: 4px;
  transition: border-color 0.3s;
}
.stack-item:hover { border-color: var(--border-h); }
.stack-name {
  font-family: var(--mono); font-size: 0.82rem;
  color: var(--txt); font-weight: 600;
}
.stack-role {
  font-size: 0.7rem; color: var(--txt3);
  text-transform: uppercase; letter-spacing: 1px;
}

/* Roadmap */
.roadmap-head { margin-bottom: 48px; margin-top: 20px; }
.roadmap-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}
.roadmap-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
  transition: border-color 0.3s;
}
.roadmap-card:hover { border-color: var(--border-h); }
.roadmap-period {
  font-family: var(--display);
  font-size: 0.88rem; font-weight: 700;
  color: var(--acc2); margin-bottom: 16px;
}
.roadmap-list {
  list-style: none; padding: 0;
}
.roadmap-list li {
  font-size: 0.82rem; color: var(--txt2);
  line-height: 1.5;
  padding: 6px 0 6px 16px;
  position: relative;
}
.roadmap-list li::before {
  content: '';
  position: absolute; left: 0; top: 13px;
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--acc1);
}

/* ── CTA SECTION ─────────────────────────────────────────────────────────── */
.cta-section {
  padding: 100px 0 60px;
  border-top: 1px solid rgba(59,130,246,0.08);
}
.cta-inner {
  background: linear-gradient(135deg, rgba(29,78,216,0.15) 0%, rgba(14,165,233,0.1) 100%);
  border: 1px solid rgba(59,130,246,0.25);
  border-radius: 24px;
  padding: 72px 52px;
  text-align: center;
}
.cta-title {
  font-family: var(--display);
  font-size: clamp(1.6rem, 2.8vw, 2.2rem);
  font-weight: 700; color: var(--txt);
  letter-spacing: -0.5px; margin-bottom: 16px;
}
.cta-desc {
  font-size: 1rem; color: var(--txt2);
  margin-bottom: 36px; line-height: 1.6;
}
.cta-buttons { display: flex; justify-content: center; gap: 16px; }

/* ── FOOTER ──────────────────────────────────────────────────────────────── */
.footer {
  border-top: 1px solid rgba(59,130,246,0.08);
  padding: 40px 0;
}
.footer-inner {
  display: flex; align-items: center; justify-content: space-between;
  flex-wrap: wrap; gap: 20px;
}
.footer-brand { display: flex; align-items: center; gap: 10px; }
.footer-brand img {
  filter: brightness(0) invert(1);
}
.footer-links { display: flex; gap: 24px; }
.footer-links a {
  font-family: var(--mono); font-size: 0.75rem;
  color: var(--txt3); text-decoration: none;
  transition: color 0.2s;
}
.footer-links a:hover { color: var(--acc1); }
.footer-copy { font-size: 0.72rem; color: var(--txt3); }

/* ── Responsive ──────────────────────────────────────────────────────────── */
@media (max-width: 1200px) {
  .cases-grid { grid-template-columns: repeat(2, 1fr); }
  .metrics-grid { grid-template-columns: repeat(2, 1fr); }
  .roadmap-grid { grid-template-columns: repeat(2, 1fr); }
  .pricing-layout { grid-template-columns: 1fr; }
}
@media (max-width: 1024px) {
  .hero { flex-direction: column; min-height: auto; }
  .hero-left { padding: 60px 40px; justify-content: flex-start; }
  .hero-right { flex: none; width: 100%; min-height: 320px; }
  .logo-img { width: 280px; height: 280px; }
  .logo-showcase { width: 280px; height: 280px; }
  .pain-grid { grid-template-columns: 1fr; }
  .tech-grid { grid-template-columns: 1fr; }
  .demo-grid { grid-template-columns: 1fr; }
  .nav-links { display: none; }
  .nav-burger { display: flex; }
  .mobile-menu { display: flex; }
}
@media (max-width: 640px) {
  .main-wrap { padding: 0 20px; }
  .nav-inner { padding: 0 20px; }
  .mobile-menu { padding: 16px 20px 20px; }
  .hero-left { padding: 48px 20px; }
  .hero-title { font-size: 1.8rem; }
  .cases-grid { grid-template-columns: 1fr; }
  .hero-kpi { flex-wrap: wrap; gap: 20px; }
  .hero-ctas { flex-direction: column; align-items: stretch; }
  .btn-ghost { text-align: center; }
  .section { padding: 64px 0; }
  .cta-inner { padding: 48px 24px; }
  .calc-card { padding: 28px 20px; }
  .compare-table { font-size: 0.75rem; }
  .compare-table th, .compare-table td { padding: 10px 12px; }
  .roadmap-grid { grid-template-columns: 1fr; }
  .metrics-grid { grid-template-columns: 1fr 1fr; }
  .footer-inner { flex-direction: column; align-items: flex-start; }
}
</style>
