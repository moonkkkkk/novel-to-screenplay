/**
 * 小说转剧本 - 前端交互逻辑
 *
 * 功能：
 * - 动态添加/删除章节输入框
 * - 调用 /convert API 转换小说
 * - Tab 切换查看 YAML / JSON / 检查报告
 * - 复制、下载输出结果
 */

// file:// 协议下 origin 为 null，回退到 localhost:8000
const API_BASE = window.location.origin && window.location.origin !== 'null'
  ? window.location.origin
  : 'http://localhost:8000';

// ── 章节管理 ──────────────────────────────────────────────────

let chapterCount = 3;

/** 添加新章节输入块 */
function addChapter() {
  chapterCount++;
  const container = document.getElementById('chapters-container');
  const block = document.createElement('div');
  block.className = 'chapter-block';
  block.innerHTML = `
    <div class="chapter-header">
      <span>第 ${chapterCount} 章</span>
      <button class="btn-remove-chapter" title="删除此章" onclick="removeChapter(this)">✕</button>
    </div>
    <textarea class="chapter-text" placeholder="在此粘贴第 ${chapterCount} 章小说内容..." rows="6"></textarea>
  `;
  container.appendChild(block);
}

/** 删除章节输入块（至少保留 3 个） */
function removeChapter(btn) {
  const blocks = document.querySelectorAll('.chapter-block');
  if (blocks.length <= 3) {
    alert('至少需要 3 个章节');
    return;
  }
  btn.closest('.chapter-block').remove();
  // 重新编号
  document.querySelectorAll('.chapter-block .chapter-header span').forEach((span, i) => {
    span.textContent = `第 ${i + 1} 章`;
  });
  chapterCount = blocks.length - 1;
}

// ── 转换主流程 ────────────────────────────────────────────────

async function convertNovel() {
  const title = document.getElementById('title').value.trim() || '未命名剧本';
  const author = document.getElementById('author').value.trim() || '未知';
  const genre = document.getElementById('genre').value;

  // 收集所有章节
  const textareas = document.querySelectorAll('.chapter-text');
  const chapters = [];
  textareas.forEach(ta => {
    const text = ta.value.trim();
    if (text) chapters.push(text);
  });

  if (chapters.length < 3) {
    alert('请至少填写 3 个章节的内容');
    return;
  }

  // 切换 UI 状态
  const btn = document.getElementById('btn-convert');
  btn.disabled = true;
  btn.textContent = '⏳ 转换中...';

  hideError();
  showProgress('正在连接 LLM 服务...');

  try {
    const response = await fetch(`${API_BASE}/convert`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chapters: chapters,
        title: title,
        author: author,
        genre: genre,
      }),
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || `HTTP ${response.status}`);
    }

    const data = await response.json();

    if (!data.success) {
      throw new Error(data.error || '未知错误');
    }

    // 填入输出
    document.getElementById('output-yaml').textContent = data.script_yaml;
    document.getElementById('output-json').textContent = data.script_json;

    // 检查报告
    buildReport(data);

    // 显示输出区
    hideProgress();
    showOutput();
    switchTab('yaml');

  } catch (err) {
    hideProgress();
    showError(err.message);
    console.error('Convert error:', err);
  } finally {
    btn.disabled = false;
    btn.textContent = '🎬 转换为剧本';
  }
}

// ── 进度管理 ──────────────────────────────────────────────────

function showProgress(text) {
  document.getElementById('progress-section').style.display = 'block';
  document.getElementById('progress-text').textContent = text;
  // 模拟进度动画
  const fill = document.getElementById('progress-fill');
  fill.style.width = '0%';
  setTimeout(() => { fill.style.width = '30%'; }, 200);
  setTimeout(() => { fill.style.width = '70%'; }, 5000);
  setTimeout(() => { fill.style.width = '90%'; }, 15000);
}

function hideProgress() {
  document.getElementById('progress-section').style.display = 'none';
  document.getElementById('progress-fill').style.width = '0%';
}

// ── 输出展示 ──────────────────────────────────────────────────

function showOutput() {
  document.getElementById('output-section').style.display = 'block';
  document.getElementById('output-section').scrollIntoView({ behavior: 'smooth' });
}

function hideOutput() {
  document.getElementById('output-section').style.display = 'none';
}

// ── Tab 切换 ──────────────────────────────────────────────────

function switchTab(name) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));

  document.querySelector(`.tab:nth-child(${
    name === 'yaml' ? 1 : name === 'json' ? 2 : 3
  })`).classList.add('active');
  document.getElementById(`panel-${name}`).classList.add('active');
}

// ── 检查报告 ──────────────────────────────────────────────────

function buildReport(data) {
  const score = data.faithfulness_score;
  const badge = document.getElementById('score-badge');

  let scoreClass = score >= 0.8 ? 'good' : score >= 0.5 ? 'warn' : 'bad';
  badge.textContent = (score * 100).toFixed(0) + '%';
  badge.className = 'score-badge ' + scoreClass;

  const container = document.getElementById('report-content');
  container.innerHTML = `
    <div class="report-card">
      <h4>📊 忠实度评分</h4>
      <p class="score ${scoreClass}">${(score * 100).toFixed(0)}%</p>
      <p style="color: var(--text-muted);">
        综合评分（硬规则校验 + LLM 软检查）
      </p>
    </div>

    <div class="report-card">
      <h4>📋 统计信息</h4>
      <p>场景数：<strong>${data.scene_count}</strong></p>
      <p>角色数：<strong>${data.character_count}</strong></p>
    </div>

    <div class="report-card">
      <h4>🔍 硬规则违规</h4>
      ${data.violations && data.violations.length > 0
        ? '<ul class="violation-list">' + data.violations.map(v => `<li>${v}</li>`).join('') + '</ul>'
        : '<p style="color: var(--success);">✅ 全部通过，无硬规则违规</p>'
      }
    </div>
  `;
}

// ── 错误展示 ──────────────────────────────────────────────────

function showError(msg) {
  document.getElementById('error-section').style.display = 'block';
  document.getElementById('error-message').textContent = msg;
  document.getElementById('error-section').scrollIntoView({ behavior: 'smooth' });
}

function hideError() {
  document.getElementById('error-section').style.display = 'none';
}

// ── 复制和下载 ────────────────────────────────────────────────

function copyOutput(type) {
  const el = document.getElementById(`output-${type}`);
  const text = el.textContent;
  navigator.clipboard.writeText(text).then(() => {
    alert(`已复制 ${type.toUpperCase()} 内容到剪贴板`);
  }).catch(() => {
    alert('复制失败，请手动选择文本复制');
  });
}

function downloadOutput(type) {
  const text = document.getElementById(`output-${type}`).textContent;
  const ext = type === 'yaml' ? 'yaml' : 'json';
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `剧本输出.${ext}`;
  a.click();
  URL.revokeObjectURL(url);
}
