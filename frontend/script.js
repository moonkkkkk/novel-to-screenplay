/**
 * 小说转剧本 - 前端交互逻辑
 *
 * 功能：
 * - 双模式输入：手动分章 / 粘贴全文（自动识别章节）
 * - 调用 /convert API 转换小说
 * - Tab 切换查看 YAML / JSON / 章节树 / 分镜表 / 检查报告
 * - 复制、下载输出结果
 */

// file:// 协议下 origin 为 null，回退到 localhost:8000
const API_BASE = window.location.origin && window.location.origin !== 'null'
  ? window.location.origin
  : 'http://localhost:8000';

// ── 输入模式管理 ──────────────────────────────────────────────

let inputMode = 'manual';  // 'manual' | 'raw'

/** 切换输入模式 */
function setInputMode(mode) {
  inputMode = mode;
  document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
  document.querySelector(`.mode-btn[data-mode="${mode}"]`).classList.add('active');

  const chaptersContainer = document.getElementById('chapters-container');
  const rawContainer = document.getElementById('raw-text-container');
  const addBtn = document.querySelector('.button-row');

  if (mode === 'raw') {
    chaptersContainer.style.display = 'none';
    rawContainer.style.display = 'block';
    if (addBtn) addBtn.style.display = 'none';
  } else {
    chaptersContainer.style.display = 'block';
    rawContainer.style.display = 'none';
    if (addBtn) addBtn.style.display = 'flex';
  }
}

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
      <button class="btn-remove" title="删除此章" onclick="removeChapter(this)">x</button>
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

  // 根据输入模式构建请求体
  const body = { title, author, genre };

  if (inputMode === 'raw') {
    const rawText = document.getElementById('raw-text').value.trim();
    if (!rawText) {
      alert('请粘贴整本小说文本');
      return;
    }
    body.raw_text = rawText;
    // 不传 chapters 字段，让 Pydantic 用 default=None
  } else {
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
    body.chapters = chapters;
    // 不传 raw_text 字段
  }

  // 切换 UI 状态
  const btn = document.getElementById('btn-convert');
  btn.disabled = true;
  btn.textContent = '转换中...';

  hideError();
  showProgress('正在连接 LLM 服务...');

  try {
    const response = await fetch(`${API_BASE}/convert`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const err = await response.json();
      // FastAPI 422 返回 detail 数组 [{loc, msg, type}, ...]
      let msg;
      if (Array.isArray(err.detail)) {
        msg = err.detail.map(e => `${e.msg} (${e.loc.join('.')})`).join('; ');
      } else if (typeof err.detail === 'string') {
        msg = err.detail;
      } else {
        msg = JSON.stringify(err);
      }
      throw new Error(msg || `HTTP ${response.status}`);
    }

    const data = await response.json();

    if (!data.success) {
      throw new Error(data.error || '未知错误');
    }

    // 解析 JSON 用于树/表展示
    let scriptData = null;
    try {
      scriptData = JSON.parse(data.script_json);
    } catch (e) {
      console.warn('Failed to parse script_json for tree/table views');
    }

    // 填入输出
    document.getElementById('output-yaml').textContent = data.script_yaml;
    document.getElementById('output-json').textContent = data.script_json;

    // 检查报告
    buildReport(data);

    // 章节树
    if (scriptData) {
      buildChapterTree(scriptData);
      buildShotTable(scriptData);
    }

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
    btn.textContent = '转换为剧本';
  }
}

// ── 进度管理 ──────────────────────────────────────────────────

function showProgress(text) {
  document.getElementById('progress-section').style.display = 'block';
  document.getElementById('progress-text').textContent = text;
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

// ── Tab 切换 ──────────────────────────────────────────────────

function switchTab(name) {
  const tabs = document.querySelectorAll('.output-tabs .tab');
  const tabNames = ['yaml', 'json', 'tree', 'shots', 'report'];
  const idx = tabNames.indexOf(name);

  tabs.forEach(t => t.classList.remove('active'));
  if (idx >= 0 && idx < tabs.length) {
    tabs[idx].classList.add('active');
  }

  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  const panel = document.getElementById(`panel-${name}`);
  if (panel) panel.classList.add('active');
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
      <h4>忠实度评分</h4>
      <p class="score ${scoreClass}">${(score * 100).toFixed(0)}%</p>
      <p style="color: var(--ink-muted);">
        综合评分（硬规则校验 + LLM 软检查）
      </p>
    </div>

    <div class="report-card">
      <h4>统计信息</h4>
      <table class="stats-table">
        <tr><td>章节数</td><td><strong>${data.chapter_count || 0}</strong></td></tr>
        <tr><td>场景数</td><td><strong>${data.scene_count || 0}</strong></td></tr>
        <tr><td>分镜数</td><td><strong>${data.beat_count || 0}</strong></td></tr>
        <tr><td>角色数</td><td><strong>${data.character_count || 0}</strong></td></tr>
      </table>
    </div>

    <div class="report-card">
      <h4>Validation</h4>
      ${data.violations && data.violations.length > 0
        ? '<ul class="violation-list">' + data.violations.map(v => `<li>${v}</li>`).join('') + '</ul>'
        : '<p style="color: var(--success);">No violations detected.</p>'
      }
    </div>
  `;
}

// ── 章节树 ────────────────────────────────────────────────────

function buildChapterTree(scriptData) {
  const container = document.getElementById('tree-content');

  if (!scriptData.chapters || scriptData.chapters.length === 0) {
    container.innerHTML = '<p class="empty-msg">暂无章节树数据</p>';
    return;
  }

  let html = '<div class="tree-root">';

  scriptData.chapters.forEach(ch => {
    html += `
      <div class="tree-chapter">
        <div class="tree-chapter-header">
          <span class="tree-icon">&#x25A0;</span>
          <strong>${escHtml(ch.title || `第${ch.id}章`)}</strong>
          ${ch.summary ? `<span class="tree-desc"> — ${escHtml(ch.summary)}</span>` : ''}
          <span class="tree-count">${(ch.scenes || []).length} 个场景</span>
        </div>`;

    (ch.scenes || []).forEach(sc => {
      const timelineLabel = sc.timeline_type === 'flashback' ? ' [倒叙]' :
                            sc.timeline_type === 'flashforward' ? ' [插叙]' : '';
      html += `
        <div class="tree-scene">
          <div class="tree-scene-header">
            <span class="tree-icon">&#x25B8;</span>
            <span class="scene-slug">${escHtml(sc.slug || `场景 ${sc.id}`)}${timelineLabel}</span>
            ${sc.scene_purpose ? `<span class="scene-purpose">${escHtml(sc.scene_purpose)}</span>` : ''}
            <span class="tree-count">${(sc.beats || []).length} 个分镜</span>
          </div>
          <div class="tree-beats">`;

      (sc.beats || []).forEach(beat => {
        const typeLabel = { narration: 'NAR', action: 'ACT', dialogue: 'DIA', transition: 'TRA' };
        const label = typeLabel[beat.type] || beat.type;
        const charName = beat.character ? ` [${beat.character}]` : '';
        html += `
            <div class="tree-beat">
              <span class="beat-type ${beat.type}">${label}</span>
              <span class="beat-desc">${escHtml(beat.description || '')}${charName}</span>
              ${beat.shot_suggestion ? `
                <span class="beat-meta">
                  ${escHtml(beat.shot_suggestion.camera_hint || '')} / ${escHtml(beat.shot_suggestion.sound_hint || '')} / ${escHtml(beat.shot_suggestion.emotion || '')}
                </span>` : ''}
            </div>`;
      });

      html += `</div></div>`;
    });

    html += '</div>';
  });

  html += '</div>';
  container.innerHTML = html;
}

// ── 分镜表格 ──────────────────────────────────────────────────

function buildShotTable(scriptData) {
  const container = document.getElementById('shots-content');
  const allBeats = [];

  // 收集所有 Beat
  if (scriptData.chapters) {
    scriptData.chapters.forEach(ch => {
      (ch.scenes || []).forEach(sc => {
        (sc.beats || []).forEach(b => {
          allBeats.push({ ...b, _sceneSlug: sc.slug, _chapterTitle: ch.title });
        });
      });
    });
  }

  if (allBeats.length === 0) {
    container.innerHTML = '<p class="empty-msg">暂无分镜数据</p>';
    return;
  }

  const typeLabel = { narration: '旁白', action: '动作', dialogue: '对白', transition: '转场' };

  let html = `<p class="shot-summary">共 <strong>${allBeats.length}</strong> 个分镜</p>
    <div class="shot-table-wrap">
    <table class="shot-table">
      <thead>
        <tr>
          <th>序号</th>
          <th>类型</th>
          <th>描述</th>
          <th>角色</th>
          <th>镜头</th>
          <th>声音</th>
          <th>情绪</th>
        </tr>
      </thead>
      <tbody>`;

  let globalIdx = 0;
  allBeats.forEach(b => {
    globalIdx++;
    const shot = b.shot_suggestion || {};
    html += `
        <tr class="beat-row-${b.type}">
          <td>${globalIdx}</td>
          <td><span class="beat-type-label ${b.type}">${typeLabel[b.type] || b.type}</span></td>
          <td>
            <div class="shot-desc">${escHtml(b.description || '')}</div>
            <div class="shot-context">${escHtml(b._sceneSlug || '')}</div>
          </td>
          <td>${escHtml(b.character || '-')}</td>
          <td>${escHtml(shot.camera_hint || '-')}</td>
          <td>${escHtml(shot.sound_hint || '-')}</td>
          <td>${escHtml(shot.emotion || '-')}</td>
        </tr>`;
  });

  html += '</tbody></table></div>';
  container.innerHTML = html;
}

// ── 辅助函数 ──────────────────────────────────────────────────

function escHtml(str) {
  if (!str) return '';
  str = String(str);
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
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
  // 对于树/表/报告，复制文本内容
  let text;
  if (type === 'tree') {
    text = document.getElementById('tree-content').textContent;
  } else if (type === 'shots') {
    text = document.getElementById('shots-content').textContent;
  } else {
    text = document.getElementById(`output-${type}`).textContent;
  }
  navigator.clipboard.writeText(text).then(() => {
    alert(`已复制内容到剪贴板`);
  }).catch(() => {
    alert('复制失败，请手动选择文本复制');
  });
}

function downloadOutput(type) {
  let text, ext;
  if (type === 'yaml') {
    text = document.getElementById('output-yaml').textContent;
    ext = 'yaml';
  } else if (type === 'json') {
    text = document.getElementById('output-json').textContent;
    ext = 'json';
  } else {
    text = document.getElementById(`panel-${type}`).textContent;
    ext = 'txt';
  }
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `剧本输出.${ext}`;
  a.click();
  URL.revokeObjectURL(url);
}
