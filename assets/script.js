/**
 * 每日资源导航 - 前端逻辑
 * 加载每日内容、历史归档、背景图片轮换
 */

(function() {
  'use strict';

  // ========================================
  // 配置常量
  // ========================================
  const CONFIG = {
    contentUrl: 'data/content.json',
    backgrounds: [
      'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1920&q=80', // 星空
      'https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=1920&q=80', // 星系
      'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=1920&q=80', // 极光
      'https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=1920&q=80', // 星空山脉
      'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=1920&q=80', // 星空树
      'https://images.unsplash.com/photo-1507582354351-3921a86d8e32?w=1920&q=80', // 夜空
      'https://images.unsplash.com/photo-1465101162946-4377e57745c3?w=1920&q=80', // 深空
      'https://images.unsplash.com/photo-1472214103451-9374bd1c798e?w=1920&q=80', // 宇宙
    ],
    bgChangeInterval: 300000, // 5分钟换一次背景
    archivePerPage: 6,
    startDate: '2025-01-01', // 项目启动日期
  };

  // ========================================
  // DOM 元素缓存
  // ========================================
  const els = {
    bgImage: document.getElementById('bgImage'),
    bgParticles: document.getElementById('bgParticles'),
    currentDate: document.getElementById('currentDate'),
    dayCount: document.getElementById('dayCount'),
    totalDays: document.getElementById('totalDays'),
    heroTitle: document.getElementById('heroTitle'),
    heroDesc: document.getElementById('heroDesc'),
    heroCategory: document.getElementById('heroCategory'),
    heroReadTime: document.getElementById('heroReadTime'),
    heroCta: document.getElementById('heroCta'),
    archiveGrid: document.getElementById('archiveGrid'),
    loadMoreBtn: document.getElementById('loadMoreBtn'),
  };

  // ========================================
  // 状态
  // ========================================
  let state = {
    allContent: [],
    displayedArchiveCount: 0,
    currentBgIndex: 0,
    bgInterval: null,
    particleInterval: null,
  };

  // ========================================
  // 工具函数
  // ========================================
  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

  function formatDate(dateStr, options = {}) {
    const defaultOpts = { year: 'numeric', month: 'long', day: 'numeric', ...options };
    return new Date(dateStr + 'T00:00:00').toLocaleDateString('zh-CN', defaultOpts);
  }

  function daysBetween(start, end) {
    const s = new Date(start + 'T00:00:00');
    const e = new Date(end + 'T00:00:00');
    return Math.floor((e - s) / (1000 * 60 * 60 * 24)) + 1;
  }

  function clamp(num, min, max) {
    return Math.min(Math.max(num, min), max);
  }

  function debounce(fn, delay) {
    let t;
    return (...args) => {
      clearTimeout(t);
      t = setTimeout(() => fn(...args), delay);
    };
  }

  // ========================================
  // 背景图片管理
  // ========================================
  function initBackgrounds() {
    // 预加载第一张
    preloadImage(CONFIG.backgrounds[0]).then(() => {
      setBackground(0);
    });

    // 启动定时切换
    state.bgInterval = setInterval(() => {
      state.currentBgIndex = (state.currentBgIndex + 1) % CONFIG.backgrounds.length;
      preloadImage(CONFIG.backgrounds[state.currentBgIndex]).then(() => {
        setBackground(state.currentBgIndex);
      });
    }, CONFIG.bgChangeInterval);

    // 创建粒子
    createParticles();
  }

  function preloadImage(url) {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = resolve;
      img.onerror = resolve; // 失败也继续
      img.src = url;
    });
  }

  function setBackground(index) {
    const url = CONFIG.backgrounds[index];
    els.bgImage.style.opacity = '0';
    setTimeout(() => {
      els.bgImage.style.backgroundImage = `url("${url}")`;
      els.bgImage.style.opacity = '1';
    }, 500);
  }

  function createParticles() {
    const count = 20;
    for (let i = 0; i < count; i++) {
      const particle = document.createElement('div');
      particle.className = 'bg-particle';
      particle.style.left = Math.random() * 100 + '%';
      particle.style.animationDelay = Math.random() * 15 + 's';
      particle.style.animationDuration = (15 + Math.random() * 10) + 's';
      const size = Math.random() * 2 + 1;
      particle.style.width = size + 'px';
      particle.style.height = size + 'px';
      particle.style.opacity = Math.random() * 0.5 + 0.1;
      els.bgParticles.appendChild(particle);
    }
  }

  // ========================================
  // 日期与天数显示
  // ========================================
  function updateDateDisplay() {
    const today = new Date();
    const todayStr = today.toISOString().split('T')[0];

    els.currentDate.textContent = formatDate(todayStr, { weekday: 'long' });

    const dayNum = daysBetween(CONFIG.startDate, todayStr);
    els.dayCount.innerHTML = `第 <strong>${dayNum}</strong> 天`;
    els.totalDays.textContent = dayNum;
  }

  // ========================================
  // 内容加载与渲染
  // ========================================
  async function loadContent() {
    try {
      const res = await fetch(CONFIG.contentUrl, { cache: 'no-cache' });
      if (!res.ok) throw new Error('Failed to load content');
      const data = await res.json();
      state.allContent = data.items || [];
      renderHero();
      renderArchive(true);
    } catch (err) {
      console.error('Load content failed:', err);
      renderFallback();
    }
  }

  function renderHero() {
    const today = new Date().toISOString().split('T')[0];
    const todayItem = state.allContent.find(item => item.date === today);
    const item = todayItem || state.allContent[0]; // 兜底显示第一条

    if (!item) {
      renderFallback();
      return;
    }

    els.heroTitle.textContent = item.title;
    els.heroDesc.textContent = item.description;
    els.heroCategory.textContent = item.category;
    els.heroReadTime.textContent = `${item.readTime} 分钟阅读`;
    els.heroCta.href = item.url;
    els.heroCta.setAttribute('aria-label', `查看资源：${item.title}`);
  }

  function renderFallback() {
    els.heroTitle.textContent = '暂无今日内容';
    els.heroDesc.textContent = '内容正在准备中，请稍后再来';
    els.heroCategory.textContent = '—';
    els.heroReadTime.textContent = '—';
    els.heroCta.href = '#';
    els.heroCta.style.pointerEvents = 'none';
    els.heroCta.style.opacity = '0.5';
  }

  function renderArchive(reset = false) {
    if (reset) {
      state.displayedArchiveCount = 0;
      els.archiveGrid.innerHTML = '';
    }

    const today = new Date().toISOString().split('T')[0];
    const historyItems = state.allContent
      .filter(item => item.date !== today)
      .sort((a, b) => b.date.localeCompare(a.date));

    const nextItems = historyItems.slice(
      state.displayedArchiveCount,
      state.displayedArchiveCount + CONFIG.archivePerPage
    );

    if (nextItems.length === 0) {
      els.loadMoreBtn.style.display = 'none';
      if (state.displayedArchiveCount === 0) {
        els.archiveGrid.innerHTML = `
          <div class="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M12 8v4M12 16h.01M21 12c0 4.97-4.03 9-9 9S3 16.97 3 12 7.03 3 12 3s9 4.03 9 9z"/>
            </svg>
            <p>暂无历史内容</p>
          </div>
        `;
      }
      return;
    }

    const fragment = document.createDocumentFragment();
    nextItems.forEach(item => {
      fragment.appendChild(createArchiveCard(item));
    });
    els.archiveGrid.appendChild(fragment);

    state.displayedArchiveCount += nextItems.length;

    if (state.displayedArchiveCount >= historyItems.length) {
      els.loadMoreBtn.style.display = 'none';
    } else {
      els.loadMoreBtn.style.display = 'block';
    }
  }

  function createArchiveCard(item) {
    const card = document.createElement('article');
    card.className = 'archive-card';
    card.innerHTML = `
      <div class="archive-card-date">${formatDate(item.date)}</div>
      <h3 class="archive-card-title">${escapeHtml(item.title)}</h3>
      <p class="archive-card-desc">${escapeHtml(item.description)}</p>
      <div class="archive-card-footer">
        <span class="archive-card-category">${escapeHtml(item.category)}</span>
        <a href="${escapeHtml(item.url)}" class="archive-card-link" target="_blank" rel="noopener noreferrer">
          阅读全文
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </a>
      </div>
    `;
    return card;
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // ========================================
  // 事件绑定
  // ========================================
  function bindEvents() {
    els.loadMoreBtn.addEventListener('click', () => renderArchive(false));

    // 键盘快捷键：空格键加载更多
    document.addEventListener('keydown', (e) => {
      if (e.code === 'Space' && document.activeElement === document.body) {
        e.preventDefault();
        if (els.loadMoreBtn.style.display !== 'none') {
          renderArchive(false);
        }
      }
    });

    // 页面可见性变化时暂停/恢复背景切换
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        clearInterval(state.bgInterval);
        clearInterval(state.particleInterval);
      } else {
        state.bgInterval = setInterval(() => {
          state.currentBgIndex = (state.currentBgIndex + 1) % CONFIG.backgrounds.length;
          preloadImage(CONFIG.backgrounds[state.currentBgIndex]).then(() => {
            setBackground(state.currentBgIndex);
          });
        }, CONFIG.bgChangeInterval);
      }
    });
  }

  // ========================================
  // 初始化
  // ========================================
  function init() {
    updateDateDisplay();
    initBackgrounds();
    bindEvents();
    loadContent();

    // 暴露调试接口
    window.__DAILY_NAV__ = {
      state,
      CONFIG,
      refresh: loadContent,
      nextBg: () => {
        state.currentBgIndex = (state.currentBgIndex + 1) % CONFIG.backgrounds.length;
        preloadImage(CONFIG.backgrounds[state.currentBgIndex]).then(() => setBackground(state.currentBgIndex));
      },
    };
  }

  // 启动
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();