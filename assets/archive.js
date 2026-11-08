/**
 * 归档页面逻辑：渲染年/月/日树形结构
 */

(function() {
  'use strict';

  const CONFIG = {
    contentUrl: '../data/content.json',
  };

  const els = {
    archiveTree: document.getElementById('archiveTree'),
    currentDate: document.getElementById('currentDate'),
    bgImage: document.getElementById('bgImage'),
    bgParticles: document.getElementById('bgParticles'),
  };

  let state = {
    allContent: [],
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
    updateDateDisplay();
    initBackgrounds();
    loadContent();
  }

  function updateDateDisplay() {
    const today = new Date();
    const todayStr = today.toISOString().split('T')[0];
    els.currentDate.textContent = formatDate(todayStr, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
  }

  function formatDate(dateStr, options = {}) {
    const defaultOpts = { year: 'numeric', month: 'long', day: 'numeric', ...options };
    return new Date(dateStr + 'T00:00:00').toLocaleDateString('zh-CN', defaultOpts);
  }

  function initBackgrounds() {
    // 预加载第一张
    preloadImage(state.backgrounds[0]).then(() => {
      setBackground(0);
    });

    // 定时切换
    setInterval(() => {
      state.currentBgIndex = (state.currentBgIndex + 1) % state.backgrounds.length;
      preloadImage(state.backgrounds[state.currentBgIndex]).then(() => {
        setBackground(state.currentBgIndex);
      });
    }, 300000); // 5分钟

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
      renderArchiveTree();
    } catch (err) {
      console.error('Load content failed:', err);
      els.archiveTree.innerHTML = '<div class="empty-state"><p>加载失败，请刷新重试</p></div>';
    }
  }

  function renderArchiveTree() {
    // 按年份分组
    const byYear = {};
    state.allContent.forEach(item => {
      const year = item.date.split('-')[0];
      if (!byYear[year]) byYear[year] = {};
      const month = item.date.split('-')[1];
      if (!byYear[year][month]) byYear[year][month] = [];
      byYear[year][month].push(item);
    });

    // 年份倒序排列
    const years = Object.keys(byYear).sort((a, b) => b - a);

    const fragment = document.createDocumentFragment();

    years.forEach(year => {
      const yearEl = createYearNode(year, byYear[year]);
      fragment.appendChild(yearEl);
    });

    els.archiveTree.appendChild(fragment);
  }

  function createYearNode(year, months) {
    const yearDiv = document.createElement('div');
    yearDiv.className = 'archive-year';

    const yearHeader = document.createElement('div');
    yearHeader.className = 'archive-year-header';
    yearHeader.innerHTML = `
      <span class="archive-year-toggle" aria-expanded="true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="6 9 12 15 18 9"/>
        </svg>
      </span>
      <span class="archive-year-label">${year}年</span>
      <span class="archive-year-count">${countItemsInYear(months)} 篇</span>
    `;

    const yearContent = document.createElement('div');
    yearContent.className = 'archive-year-content';

    const monthKeys = Object.keys(months).sort((a, b) => b - a);
    monthKeys.forEach(month => {
      const monthEl = createMonthNode(year, month, months[month]);
      yearContent.appendChild(monthEl);
    });

    yearDiv.appendChild(yearHeader);
    yearDiv.appendChild(yearContent);

    // 点击展开/折叠
    yearHeader.addEventListener('click', () => {
      const isCollapsed = yearContent.style.display === 'none';
      yearContent.style.display = isCollapsed ? 'block' : 'none';
      yearHeader.querySelector('.archive-year-toggle').style.transform = isCollapsed ? 'rotate(0deg)' : 'rotate(-90deg)';
      yearHeader.querySelector('.archive-year-toggle').setAttribute('aria-expanded', isCollapsed);
    });

    return yearDiv;
  }

  function countItemsInYear(months) {
    let count = 0;
    Object.values(months).forEach(days => { count += days.length; });
    return count;
  }

  function createMonthNode(year, month, days) {
    const monthDiv = document.createElement('div');
    monthDiv.className = 'archive-month';

    const monthHeader = document.createElement('div');
    monthHeader.className = 'archive-month-header';
    const monthLabel = formatMonthLabel(month);
    monthHeader.innerHTML = `
      <span class="archive-month-toggle" aria-expanded="true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="6 9 12 15 18 9"/>
        </svg>
      </span>
      <span class="archive-month-label">${monthLabel}</span>
      <span class="archive-month-count">${days.length} 篇</span>
    `;

    const monthContent = document.createElement('div');
    monthContent.className = 'archive-month-content';

    // 日期倒序
    const sortedDays = [...days].sort((a, b) => b.date.localeCompare(a.date));
    sortedDays.forEach(item => {
      const dayEl = createDayNode(item);
      monthContent.appendChild(dayEl);
    });

    monthDiv.appendChild(monthHeader);
    monthDiv.appendChild(monthContent);

    monthHeader.addEventListener('click', () => {
      const isCollapsed = monthContent.style.display === 'none';
      monthContent.style.display = isCollapsed ? 'block' : 'none';
      monthHeader.querySelector('.archive-month-toggle').style.transform = isCollapsed ? 'rotate(0deg)' : 'rotate(-90deg)';
      monthHeader.querySelector('.archive-month-toggle').setAttribute('aria-expanded', isCollapsed);
    });

    return monthDiv;
  }

  function formatMonthLabel(month) {
    const date = new Date(2000, parseInt(month) - 1, 1);
    return date.toLocaleDateString('zh-CN', { month: 'long' });
  }

  function createDayNode(item) {
    const dayDiv = document.createElement('a');
    dayDiv.className = 'archive-day';
    dayDiv.href = `../${item.date}/`; // 链接到当天的详情页
    dayDiv.innerHTML = `
      <span class="archive-day-date">${formatDayLabel(item.date)}</span>
      <span class="archive-day-title">${escapeHtml(item.title)}</span>
      <span class="archive-day-category">${escapeHtml(item.category)}</span>
      <svg class="archive-day-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M5 12h14M12 5l7 7-7 7"/>
      </svg>
    `;
    return dayDiv;
  }

  function formatDayLabel(dateStr) {
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', weekday: 'short' });
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // 启动
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();