/**
 * 每日详情页逻辑：从 URL 解析日期，加载对应内容
 */

(function() {
  'use strict';

  const CONFIG = {
    contentUrl: '../../data/content.json',
  };

  const els = {
    pageTitle: document.getElementById('pageTitle'),
    pageDescription: document.getElementById('pageDescription'),
    breadcrumb: document.getElementById('breadcrumb'),
    dayBadge: document.getElementById('dayBadge'),
    dayTitle: document.getElementById('dayTitle'),
    dayDesc: document.getElementById('dayDesc'),
    dayCategory: document.getElementById('dayCategory'),
    dayReadTime: document.getElementById('dayReadTime'),
    dayCta: document.getElementById('dayCta'),
    prevLink: document.getElementById('prevLink'),
    nextLink: document.getElementById('nextLink'),
    currentDate: document.getElementById('currentDate'),
    bgImage: document.getElementById('bgImage'),
    bgParticles: document.getElementById('bgParticles'),
  };

  let state = {
    allContent: [],
    currentItem: null,
    currentIndex: -1,
    backgrounds: [
      'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1920&q=80',
      'https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=1920&q=80',
      'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=1920&q=80',
      'https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=1920&q=80',
      'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=1920&q=80',
      'https://images.unsplash.com/photo-1507582354351-3921a86d8e32?w=1920&q=80',
      'https://images.unsplash.com/photo-1465101162946-4377e57745c3?w=1920&q=80',
      'https://images.unsplash.com/photo-1472214103451-9374bd1c798e?w=1920&q=80',
    ],
    currentBgIndex: 0,
  };

  function init() {
    // 从 URL 解析日期
    const pathParts = window.location.pathname.split('/').filter(Boolean);
    const dateStr = pathParts[pathParts.length - 1]; // 最后一段是日期
    
    if (!dateStr || !/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
      showError('无效的日期格式');
      return;
    }

    state.targetDate = dateStr;
    
    updateDateDisplay();
    initBackgrounds();
    loadContent();
  }

  function updateDateDisplay() {
    const today = new Date();
    // 使用 Asia/Shanghai 时区，手动格式化为 YYYY-MM-DD (零填充)
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    const localTodayStr = `${year}-${month}-${day}`;
    els.currentDate.textContent = formatDate(localTodayStr, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
  }

  function formatDate(dateStr, options = {}) {
    const defaultOpts = { year: 'numeric', month: 'long', day: 'numeric', ...options };
    return new Date(dateStr + 'T00:00:00').toLocaleDateString('zh-CN', defaultOpts);
  }

  function initBackgrounds() {
    preloadImage(state.backgrounds[0]).then(() => {
      setBackground(0);
    });

    setInterval(() => {
      state.currentBgIndex = (state.currentBgIndex + 1) % state.backgrounds.length;
      preloadImage(state.backgrounds[state.currentBgIndex]).then(() => {
        setBackground(state.currentBgIndex);
      });
    }, 300000);

    createParticles();
  }

  function preloadImage(url) {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = resolve;
      img.onerror = resolve;
      img.src = url;
    });
  }

  function setBackground(index) {
    const url = state.backgrounds[index];
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

  async function loadContent() {
    try {
      const res = await fetch(CONFIG.contentUrl, { cache: 'no-cache' });
      if (!res.ok) throw new Error('Failed to load content');
      const data = await res.json();
      state.allContent = data.items || [];
      
      // 按日期倒序排序
      state.allContent.sort((a, b) => b.date.localeCompare(a.date));
      
      // 找到目标日期的内容
      state.currentIndex = state.allContent.findIndex(item => item.date === state.targetDate);
      
      if (state.currentIndex === -1) {
        showError(`未找到 ${state.targetDate} 的内容`);
        return;
      }

      state.currentItem = state.allContent[state.currentIndex];
      renderPage();
      renderBreadcrumb();
      renderNavigation();
    } catch (err) {
      console.error('Load content failed:', err);
      showError('加载失败，请刷新重试');
    }
  }

  function renderPage() {
    const item = state.currentItem;
    
    // 更新页面标题和描述
    document.title = `${item.title} | 每日资源导航`;
    els.pageDescription.content = item.description;
    
    // 更新面包屑
    renderBreadcrumb();
    
    // 更新徽章
    els.dayBadge.textContent = formatDate(item.date, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    
    // 更新标题
    els.dayTitle.textContent = item.title;
    
    // 更新描述
    els.dayDesc.textContent = item.description;
    
    // 更新分类和阅读时间
    els.dayCategory.textContent = item.category;
    els.dayReadTime.textContent = `${item.readTime} 分钟阅读`;
    
    // 更新 CTA 链接
    els.dayCta.href = item.url;
    els.dayCta.setAttribute('aria-label', `查看资源：${item.title}`);
  }

  function renderBreadcrumb() {
    const item = state.currentItem;
    if (!item) return;
    
    els.breadcrumb.innerHTML = `
      <a href="../../">首页</a>
      <svg class="breadcrumb-sep" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
      <a href="../../archive/">历史归档</a>
      <svg class="breadcrumb-sep" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
      <a href="../${item.date.split('-')[0]}/">${item.date.split('-')[0]}年</a>
      <svg class="breadcrumb-sep" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
      <a href="../${item.date.split('-')[0]}/${item.date.split('-')[1]}/">${formatMonthLabel(item.date.split('-')[1])}</a>
      <svg class="breadcrumb-sep" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
      <span class="breadcrumb-current">${formatDayLabel(item.date)}</span>
    `;
  }

  function formatMonthLabel(month) {
    const date = new Date(2000, parseInt(month) - 1, 1);
    return date.toLocaleDateString('zh-CN', { month: 'long' });
  }

  function formatDayLabel(dateStr) {
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', weekday: 'short' });
  }

  function renderNavigation() {
    // 上一日（按时间倒序，所以索引+1是更早的日期）
    if (state.currentIndex + 1 < state.allContent.length) {
      const prevItem = state.allContent[state.currentIndex + 1];
      els.prevLink.href = `../${prevItem.date}/`;
      els.prevLink.querySelector('span').textContent = `${formatDayLabel(prevItem.date)} · ${prevItem.title}`;
      els.prevLink.style.display = 'flex';
    }
    
    // 下一日（索引-1是更新的日期）
    if (state.currentIndex - 1 >= 0) {
      const nextItem = state.allContent[state.currentIndex - 1];
      els.nextLink.href = `../${nextItem.date}/`;
      els.nextLink.querySelector('span').textContent = `${formatDayLabel(nextItem.date)} · ${nextItem.title}`;
      els.nextLink.style.display = 'flex';
    }
  }

  function showError(message) {
    document.title = '页面不存在 | 每日资源导航';
    els.dayHero.innerHTML = `
      <div class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"/>
          <line x1="15" y1="9" x2="9" y2="15"/>
          <line x1="9" y1="9" x2="15" y2="15"/>
        </svg>
        <h2>页面不存在</h2>
        <p>${message}</p>
        <a href="../../" class="hero-cta" style="margin-top: 24px; display: inline-flex;">
          <span>返回首页</span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        </a>
      </div>
    `;
  }

  // 启动
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();