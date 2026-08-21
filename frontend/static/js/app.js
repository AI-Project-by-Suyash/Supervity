// State management
let allExceptions = [];
let selectedExceptionId = null;
let currentExceptionDetail = null;
let selectedDecision = 'APPROVE';

// DOM Elements
const queueContainer = document.getElementById('queue-container');
const detailContent = document.getElementById('detail-content');
const searchInput = document.getElementById('search-input');
const filterStatus = document.getElementById('filter-status');
const filterSeverity = document.getElementById('filter-severity');
const filterType = document.getElementById('filter-type');

const btnExplain = document.getElementById('btn-explain');
const btnSuggest = document.getElementById('btn-suggest');
const btnAutoResolve = document.getElementById('btn-auto-resolve');
const btnHumanReview = document.getElementById('btn-human-review');
const btnResetSeed = document.getElementById('btn-reset-seed');

const explanationBox = document.getElementById('ai-explanation-box');
const explanationText = document.getElementById('explanation-text');
const explanationTags = document.getElementById('explanation-tags');
const explanationProvider = document.getElementById('explanation-provider');

const suggestionBox = document.getElementById('ai-suggestion-box');
const suggestedActionBadge = document.getElementById('suggested-action-badge');
const suggestionDecision = document.getElementById('suggestion-decision');
const confidenceScore = document.getElementById('confidence-score');
const confidenceBar = document.getElementById('confidence-bar');
const suggestionReason = document.getElementById('suggestion-reason');
const scoreBreakdownGrid = document.getElementById('score-breakdown-grid');
const safetyGateBanner = document.getElementById('safety-gate-banner');

const reviewModal = document.getElementById('review-modal');
const btnCloseModal = document.getElementById('btn-close-modal');
const btnCancelModal = document.getElementById('btn-cancel-modal');
const btnSubmitDecision = document.getElementById('btn-submit-decision');
const reviewerNotes = document.getElementById('reviewer-notes');
const auditTimeline = document.getElementById('audit-timeline');
const auditCount = document.getElementById('audit-count');

let currentView = 'workbench';
let chartTypesInstance = null;
let chartStatusInstance = null;
let chartSeverityInstance = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
  fetchExceptions();
  setupEventListeners();
});

function setupEventListeners() {
  // Navigation Tabs
  const tabWorkbench = document.getElementById('tab-workbench');
  const tabAnalytics = document.getElementById('tab-analytics');
  const btnRefreshAnalytics = document.getElementById('btn-refresh-analytics');

  if (tabWorkbench && tabAnalytics) {
    tabWorkbench.addEventListener('click', () => switchView('workbench'));
    tabAnalytics.addEventListener('click', () => switchView('analytics'));
  }
  if (btnRefreshAnalytics) {
    btnRefreshAnalytics.addEventListener('click', fetchAnalytics);
  }

  searchInput.addEventListener('input', renderQueue);
  filterStatus.addEventListener('change', renderQueue);
  filterSeverity.addEventListener('change', renderQueue);
  filterType.addEventListener('change', renderQueue);

  btnResetSeed.addEventListener('click', async () => {
    if (confirm('Reset dataset back to initial 12 seed exceptions?')) {
      const res = await fetch('/api/seed/reset', { method: 'POST' });
      if (res.ok) {
        showToast('Dataset reset successfully', 'success');
        await fetchExceptions();
        if (selectedExceptionId) selectException(selectedExceptionId);
        if (currentView === 'analytics') fetchAnalytics();
      }
    }
  });

  btnExplain.addEventListener('click', handleExplain);
  btnSuggest.addEventListener('click', handleSuggest);
  btnAutoResolve.addEventListener('click', async () => {
    await handleAutoResolve();
    if (currentView === 'analytics') fetchAnalytics();
  });
  btnHumanReview.addEventListener('click', () => {
    reviewerNotes.value = '';
    reviewModal.classList.remove('hidden');
  });

  btnCloseModal.addEventListener('click', () => reviewModal.classList.add('hidden'));
  btnCancelModal.addEventListener('click', () => reviewModal.classList.add('hidden'));

  document.querySelectorAll('.decision-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.decision-btn').forEach(b => b.classList.remove('ring-2', 'ring-indigo-500'));
      const target = e.currentTarget;
      target.classList.add('ring-2', 'ring-indigo-500');
      selectedDecision = target.dataset.decision;
    });
  });

  btnSubmitDecision.addEventListener('click', async () => {
    await handleHumanDecisionSubmit();
    if (currentView === 'analytics') fetchAnalytics();
  });
}

function switchView(viewName) {
  currentView = viewName;
  const viewWorkbench = document.getElementById('view-workbench');
  const viewAnalytics = document.getElementById('view-analytics');
  const tabWorkbench = document.getElementById('tab-workbench');
  const tabAnalytics = document.getElementById('tab-analytics');

  if (viewName === 'workbench') {
    viewWorkbench.classList.remove('hidden');
    viewAnalytics.classList.add('hidden');
    tabWorkbench.className = 'view-tab-btn px-3 py-1.5 rounded text-xs font-semibold bg-emerald-600 text-white transition flex items-center gap-1.5 shadow-sm';
    tabAnalytics.className = 'view-tab-btn px-3 py-1.5 rounded text-xs font-semibold text-slate-400 hover:text-white transition flex items-center gap-1.5';
  } else {
    viewWorkbench.classList.add('hidden');
    viewAnalytics.classList.remove('hidden');
    tabWorkbench.className = 'view-tab-btn px-3 py-1.5 rounded text-xs font-semibold text-slate-400 hover:text-white transition flex items-center gap-1.5';
    tabAnalytics.className = 'view-tab-btn px-3 py-1.5 rounded text-xs font-semibold bg-emerald-600 text-white transition flex items-center gap-1.5 shadow-sm';
    fetchAnalytics();
  }
}


async function fetchExceptions() {
  try {
    const res = await fetch('/api/exceptions');
    const data = await res.json();
    allExceptions = data.items || [];
    updateMetrics();
    renderQueue();
    if (allExceptions.length > 0 && !selectedExceptionId) {
      selectException(allExceptions[0].id);
    }
  } catch (err) {
    console.error('Failed to fetch exceptions', err);
    showToast('Failed to load exceptions queue', 'error');
  }
}

function updateMetrics() {
  document.getElementById('metric-total').textContent = allExceptions.length;
  document.getElementById('metric-high').textContent = allExceptions.filter(e => e.severity === 'HIGH' && e.status !== 'RESOLVED').length;
  document.getElementById('metric-med').textContent = allExceptions.filter(e => e.severity === 'MEDIUM' && e.status !== 'RESOLVED').length;
  document.getElementById('metric-low').textContent = allExceptions.filter(e => e.severity === 'LOW' && e.status !== 'RESOLVED').length;
  document.getElementById('metric-resolved').textContent = allExceptions.filter(e => e.status === 'RESOLVED').length;
}

function renderQueue() {
  const query = searchInput.value.toLowerCase();
  const statusVal = filterStatus.value;
  const sevVal = filterSeverity.value;
  const typeVal = filterType.value;

  const filtered = allExceptions.filter(item => {
    const matchesSearch = !query || 
      item.reference_number.toLowerCase().includes(query) || 
      item.vendor.toLowerCase().includes(query) || 
      item.title.toLowerCase().includes(query);
    const matchesStatus = !statusVal || item.status === statusVal;
    const matchesSeverity = !sevVal || item.severity === sevVal;
    const matchesType = !typeVal || item.type === typeVal;
    return matchesSearch && matchesStatus && matchesSeverity && matchesType;
  });

  if (filtered.length === 0) {
    queueContainer.innerHTML = '<div class="text-center py-10 text-slate-500 text-xs">No exceptions match active filters.</div>';
    return;
  }

  queueContainer.innerHTML = filtered.map(item => {
    const isActive = item.id === selectedExceptionId ? 'active' : '';
    const sevClass = item.severity === 'HIGH' ? 'badge-high' : item.severity === 'MEDIUM' ? 'badge-medium' : 'badge-low';
    const statusClass = item.status === 'RESOLVED' ? 'badge-status-resolved' : item.status === 'ESCALATED' ? 'badge-status-escalated' : item.status === 'PENDING_HUMAN' ? 'badge-status-pending' : 'badge-status-open';

    return `
      <div onclick="selectException('${item.id}')" 
        class="queue-item ${isActive} p-3 rounded-lg hover:bg-slate-800/60 cursor-pointer transition border border-slate-800/80 space-y-1.5">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-1.5">
            <span class="text-[10px] font-bold px-1.5 py-0.5 rounded ${sevClass}">${item.severity}</span>
            <span class="text-xs font-mono font-bold text-white">${item.reference_number}</span>
          </div>
          <span class="text-[10px] font-mono px-1.5 py-0.5 rounded ${statusClass}">${item.status}</span>
        </div>
        <p class="text-xs font-medium text-slate-200 truncate">${item.vendor}</p>
        <div class="flex justify-between items-center text-[11px] text-slate-400">
          <span>${item.type.replace('_', ' ')}</span>
          <span class="font-mono text-emerald-400 font-semibold">${item.difference || ''}</span>
        </div>
      </div>
    `;
  }).join('');
}

async function selectException(id) {
  selectedExceptionId = id;
  renderQueue();

  // Enable action buttons
  btnExplain.disabled = false;
  btnSuggest.disabled = false;

  // Reset AI Panels
  explanationBox.classList.add('hidden');
  suggestionBox.classList.add('hidden');

  detailContent.innerHTML = '<div class="text-center py-10 text-slate-400 text-xs"><i class="fa-solid fa-circle-notch fa-spin text-emerald-400 text-lg mb-2"></i><p>Loading ground-truth evidence...</p></div>';

  try {
    const res = await fetch(`/api/exceptions/${id}`);
    if (!res.ok) throw new Error('Exception not found');
    currentExceptionDetail = await res.json();
    renderDetail(currentExceptionDetail);
    fetchAuditTrail(id);
  } catch (err) {
    detailContent.innerHTML = '<div class="text-center py-10 text-rose-400 text-xs">Failed to load exception details.</div>';
  }
}

function renderDetail(exc) {
  document.getElementById('detail-status-badge').textContent = `${exc.type} | ${exc.status}`;
  
  const txn = exc.transaction || {};
  const evidence = exc.evidence || { fields: [] };

  detailContent.innerHTML = `
    <div class="rounded-lg bg-slate-900 border border-slate-800 p-3.5 space-y-3">
      <div class="flex justify-between items-start">
        <div>
          <span class="text-[10px] font-mono uppercase tracking-wider text-slate-400">Transaction #${txn.reference_number || 'N/A'}</span>
          <h3 class="text-sm font-bold text-white">${txn.vendor || 'Unknown Vendor'}</h3>
        </div>
        <span class="text-xs font-mono font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300">${txn.transaction_type || 'TXN'}</span>
      </div>
      <p class="text-xs text-slate-300 leading-relaxed">${exc.description}</p>
    </div>

    <!-- Discrepancy Overview Metrics -->
    <div class="grid grid-cols-2 gap-2.5">
      <div class="bg-slate-900/90 border border-slate-800 p-2.5 rounded-lg space-y-1">
        <span class="text-[10px] uppercase text-slate-400 font-semibold">Expected Value</span>
        <div class="text-xs font-mono font-bold text-slate-200">${exc.expected_value || 'N/A'}</div>
      </div>
      <div class="bg-slate-900/90 border border-slate-800 p-2.5 rounded-lg space-y-1">
        <span class="text-[10px] uppercase text-slate-400 font-semibold">Actual / Received</span>
        <div class="text-xs font-mono font-bold text-rose-400">${exc.actual_value || 'N/A'}</div>
      </div>
      <div class="bg-slate-900/90 border border-slate-800 p-2.5 rounded-lg space-y-1">
        <span class="text-[10px] uppercase text-slate-400 font-semibold">Calculated Discrepancy</span>
        <div class="text-xs font-mono font-bold text-emerald-400">${exc.difference || 'N/A'}</div>
      </div>
      <div class="bg-slate-900/90 border border-slate-800 p-2.5 rounded-lg space-y-1">
        <span class="text-[10px] uppercase text-slate-400 font-semibold">Policy Threshold</span>
        <div class="text-xs font-mono font-bold text-slate-300">${exc.threshold || 'N/A'}</div>
      </div>
    </div>

    <!-- Structured Ground-Truth Evidence Table -->
    <div class="rounded-lg bg-slate-900 border border-slate-800 p-3.5 space-y-2.5">
      <div class="flex justify-between items-center border-b border-slate-800 pb-2">
        <span class="text-[11px] font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
          <i class="fa-solid fa-table-list text-emerald-400"></i> Structured Evidence Fields
        </span>
        <span class="text-[10px] font-mono px-2 py-0.5 rounded ${evidence.completeness_score >= 0.8 ? 'bg-emerald-950 text-emerald-400' : 'bg-rose-950 text-rose-400'}">
          ${Math.round((evidence.completeness_score || 1) * 100)}% Complete
        </span>
      </div>
      <div class="space-y-1.5">
        ${(evidence.fields || []).map(f => `
          <div class="flex items-center justify-between text-xs p-1.5 rounded bg-slate-950 border border-slate-800/80 font-mono">
            <div class="flex flex-col">
              <span class="text-slate-300 font-sans font-medium text-[11px]">${f.label || f.name}</span>
              <span class="text-[9px] text-slate-500">${f.name} &bull; src: ${f.source}</span>
            </div>
            <span class="text-slate-200 font-bold">${f.value !== null ? f.value : '<span class="text-rose-400 italic">null (missing)</span>'}</span>
          </div>
        `).join('')}
      </div>
    </div>
  `;

  // If already resolved, update state
  if (exc.status === 'RESOLVED') {
    btnAutoResolve.disabled = true;
    btnHumanReview.disabled = true;
  } else {
    btnAutoResolve.disabled = false;
    btnHumanReview.disabled = false;
  }
}

async function handleExplain() {
  if (!selectedExceptionId) return;
  btnExplain.disabled = true;
  btnExplain.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Explaining...';

  try {
    const res = await fetch(`/api/exceptions/${selectedExceptionId}/explain`, { method: 'POST' });
    const data = await res.json();
    
    explanationText.textContent = data.explanation;
    explanationProvider.textContent = `Engine: ${data.provider_used}`;
    explanationTags.innerHTML = (data.evidence_fields || []).map(tag => `
      <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-950 text-emerald-400 border border-emerald-900/60">#${tag}</span>
    `).join('');

    explanationBox.classList.remove('hidden');
    fetchAuditTrail(selectedExceptionId);
  } catch (err) {
    showToast('Failed to generate AI explanation', 'error');
  } finally {
    btnExplain.disabled = false;
    btnExplain.innerHTML = '<i class="fa-regular fa-comment-dots text-emerald-400"></i> Explain';
  }
}

async function handleSuggest() {
  if (!selectedExceptionId) return;
  btnSuggest.disabled = true;
  btnSuggest.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Reasoning...';

  try {
    const res = await fetch(`/api/exceptions/${selectedExceptionId}/suggest`, { method: 'POST' });
    const data = await res.json();

    suggestedActionBadge.textContent = data.suggested_action;
    suggestionReason.textContent = data.reason;
    
    const pct = Math.round(data.confidence * 100);
    confidenceScore.textContent = `${pct}%`;
    confidenceBar.style.width = `${pct}%`;

    // Decision badge style
    suggestionDecision.textContent = data.recommended_decision;
    if (data.recommended_decision === 'AUTO_RESOLVE') {
      suggestionDecision.className = 'text-[10px] font-mono px-2 py-0.5 rounded font-bold bg-emerald-950 text-emerald-400 border border-emerald-800';
      confidenceBar.className = 'bg-emerald-500 h-2 rounded-full transition-all duration-500';
    } else if (data.recommended_decision === 'HUMAN_REVIEW') {
      suggestionDecision.className = 'text-[10px] font-mono px-2 py-0.5 rounded font-bold bg-amber-950 text-amber-400 border border-amber-800';
      confidenceBar.className = 'bg-amber-500 h-2 rounded-full transition-all duration-500';
    } else {
      suggestionDecision.className = 'text-[10px] font-mono px-2 py-0.5 rounded font-bold bg-rose-950 text-rose-400 border border-rose-800';
      confidenceBar.className = 'bg-rose-500 h-2 rounded-full transition-all duration-500';
    }

    // Safety Gate status
    if (data.safety_gates_passed) {
      safetyGateBanner.className = 'text-xs p-2 rounded border bg-emerald-950/60 border-emerald-800 text-emerald-300 flex items-center gap-2';
      safetyGateBanner.innerHTML = '<i class="fa-solid fa-circle-check text-emerald-400"></i> Safety gates verified &amp; passed.';
    } else {
      safetyGateBanner.className = 'text-xs p-2 rounded border bg-rose-950/60 border-rose-800 text-rose-300 flex items-center gap-2';
      safetyGateBanner.innerHTML = '<i class="fa-solid fa-triangle-exclamation text-rose-400"></i> Safety gate alert: Incomplete evidence or policy block.';
    }

    // Score breakdown
    const b = data.score_breakdown || {};
    scoreBreakdownGrid.innerHTML = `
      <div>Evidence: <span class="text-white">${Math.round((b.evidence_score||0)*100)}%</span></div>
      <div>Rule: <span class="text-white">${Math.round((b.rule_certainty||0)*100)}%</span></div>
      <div>Classification: <span class="text-white">${Math.round((b.classification_score||0)*100)}%</span></div>
      <div>AI Score: <span class="text-white">${Math.round((b.ai_score||0)*100)}%</span></div>
    `;

    suggestionBox.classList.remove('hidden');
    fetchAuditTrail(selectedExceptionId);
  } catch (err) {
    showToast('Failed to generate resolution suggestion', 'error');
  } finally {
    btnSuggest.disabled = false;
    btnSuggest.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles text-white"></i> Suggest Resolution';
  }
}

async function handleAutoResolve() {
  if (!selectedExceptionId) return;
  btnAutoResolve.disabled = true;

  try {
    const res = await fetch(`/api/exceptions/${selectedExceptionId}/resolve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode: 'AUTO' })
    });

    const data = await res.json();
    if (!res.ok) {
      showToast(data.detail || 'Auto-resolution blocked by policy', 'error');
    } else {
      showToast('Exception auto-resolved successfully!', 'success');
    }
    await fetchExceptions();
    selectException(selectedExceptionId);
  } catch (err) {
    showToast('Failed to execute auto-resolve', 'error');
  } finally {
    btnAutoResolve.disabled = false;
  }
}

async function handleHumanDecisionSubmit() {
  if (!selectedExceptionId) return;
  const notes = reviewerNotes.value.trim();
  if (!notes) {
    alert('Please enter mandatory verification rationale for audit compliance.');
    return;
  }

  btnSubmitDecision.disabled = true;
  try {
    const res = await fetch(`/api/exceptions/${selectedExceptionId}/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ decision: selectedDecision, reason: notes })
    });

    if (res.ok) {
      showToast(`Review decision ${selectedDecision} recorded!`, 'success');
      reviewModal.classList.add('hidden');
      await fetchExceptions();
      selectException(selectedExceptionId);
    } else {
      const err = await res.json();
      showToast(err.detail || 'Review submission failed', 'error');
    }
  } catch (err) {
    showToast('Error submitting decision', 'error');
  } finally {
    btnSubmitDecision.disabled = false;
  }
}

async function fetchAuditTrail(id) {
  try {
    const res = await fetch(`/api/exceptions/${id}/audit`);
    const events = await res.json();
    auditCount.textContent = `${events.length} events`;
    
    if (events.length === 0) {
      auditTimeline.innerHTML = '<p class="text-slate-500 text-center py-3 text-[11px]">No audit records found.</p>';
      return;
    }

    auditTimeline.innerHTML = events.map(ev => {
      const actorColor = ev.actor === 'SYSTEM' ? 'text-emerald-400' : ev.actor === 'AI_EMPLOYEE' ? 'text-cyan-400' : 'text-indigo-400';
      const timeStr = new Date(ev.timestamp).toLocaleTimeString();
      return `
        <div class="p-2 rounded bg-slate-950 border border-slate-800/80 space-y-1 text-[11px]">
          <div class="flex justify-between items-center">
            <span class="font-bold ${actorColor} font-mono">${ev.actor}</span>
            <span class="text-slate-500 font-mono text-[10px]">${timeStr}</span>
          </div>
          <div class="font-medium text-slate-200 font-mono text-[10px]">${ev.action}</div>
          ${ev.reason ? `<p class="text-slate-400 text-[10px]">${ev.reason}</p>` : ''}
        </div>
      `;
    }).join('');
  } catch (err) {
    console.error('Audit trail error', err);
  }
}

function showToast(message, type = 'info') {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.className = `fixed bottom-5 right-5 text-xs px-4 py-2.5 rounded-lg shadow-xl transition-all duration-300 flex items-center gap-2 z-50 ${type === 'success' ? 'bg-emerald-950 border border-emerald-700 text-emerald-200' : type === 'error' ? 'bg-rose-950 border border-rose-700 text-rose-200' : 'bg-slate-900 border border-slate-700 text-white'}`;
  toast.classList.remove('hidden');
  setTimeout(() => toast.classList.add('hidden'), 3500);
}

async function fetchAnalytics() {
  try {
    const res = await fetch('/api/analytics/metrics');
    if (!res.ok) return;
    const data = await res.json();

    // 1. Update KPI Cards
    const kpiTotal = document.getElementById('dash-kpi-total');
    const kpiExposure = document.getElementById('dash-kpi-exposure');
    const kpiAutoRate = document.getElementById('dash-kpi-auto-rate');
    const kpiConfidence = document.getElementById('dash-kpi-confidence');

    if (kpiTotal) kpiTotal.textContent = data.summary.total_exceptions;
    if (kpiExposure) kpiExposure.textContent = `$${data.summary.total_financial_exposure.toLocaleString()}`;
    if (kpiAutoRate) kpiAutoRate.textContent = `${data.summary.auto_resolution_rate}%`;
    if (kpiConfidence) kpiConfidence.textContent = `${data.summary.avg_confidence}%`;

    // 2. Render Charts
    renderAnalyticsCharts(data);

    // 3. Render Recent Resolutions Table
    renderResolutionsLedger(data.recent_resolutions);
  } catch (err) {
    console.error('Failed to fetch analytics metrics', err);
  }
}

function renderAnalyticsCharts(data) {
  // Chart 1: Exception Types (Doughnut)
  const ctxTypes = document.getElementById('chart-types');
  if (ctxTypes && typeof Chart !== 'undefined') {
    if (chartTypesInstance) chartTypesInstance.destroy();
    chartTypesInstance = new Chart(ctxTypes, {
      type: 'doughnut',
      data: {
        labels: ['Amount Mismatch', 'Quantity Mismatch', 'Payment Overdue'],
        datasets: [{
          data: [
            data.type_distribution.AMOUNT_MISMATCH || 0,
            data.type_distribution.QUANTITY_MISMATCH || 0,
            data.type_distribution.PAYMENT_OVERDUE || 0
          ],
          backgroundColor: ['#10b981', '#3b82f6', '#f59e0b'],
          borderColor: '#0f172a',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 10 } } }
        }
      }
    });
  }

  // Chart 2: Resolution Status Funnel (Bar)
  const ctxStatus = document.getElementById('chart-status');
  if (ctxStatus && typeof Chart !== 'undefined') {
    if (chartStatusInstance) chartStatusInstance.destroy();
    chartStatusInstance = new Chart(ctxStatus, {
      type: 'bar',
      data: {
        labels: ['Open', 'Recommended', 'Pending Review', 'Resolved', 'Escalated', 'Rejected'],
        datasets: [{
          label: 'Exceptions',
          data: [
            data.status_distribution.OPEN || 0,
            data.status_distribution.RECOMMENDED || 0,
            data.status_distribution.PENDING_HUMAN || 0,
            data.status_distribution.RESOLVED || 0,
            data.status_distribution.ESCALATED || 0,
            data.status_distribution.REJECTED || 0
          ],
          backgroundColor: ['#64748b', '#06b6d4', '#f59e0b', '#10b981', '#ef4444', '#f43f5e'],
          borderRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true, grid: { color: '#1e293b' }, ticks: { color: '#94a3b8', stepSize: 1 } },
          x: { grid: { display: false }, ticks: { color: '#94a3b8', font: { size: 9 } } }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }

  // Chart 3: Severity & Risk Levels (Pie/Doughnut)
  const ctxSeverity = document.getElementById('chart-severity');
  if (ctxSeverity && typeof Chart !== 'undefined') {
    if (chartSeverityInstance) chartSeverityInstance.destroy();
    chartSeverityInstance = new Chart(ctxSeverity, {
      type: 'pie',
      data: {
        labels: ['High Severity', 'Medium Severity', 'Low Severity'],
        datasets: [{
          data: [
            data.severity_distribution.HIGH || 0,
            data.severity_distribution.MEDIUM || 0,
            data.severity_distribution.LOW || 0
          ],
          backgroundColor: ['#ef4444', '#f59e0b', '#3b82f6'],
          borderColor: '#0f172a',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 10 } } }
        }
      }
    });
  }
}

function renderResolutionsLedger(stream) {
  const tbody = document.getElementById('dash-resolutions-tbody');
  if (!tbody) return;

  if (!stream || stream.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" class="py-6 text-center text-slate-500 text-xs">No resolution records recorded yet. Resolve exceptions in Workbench to populate ledger.</td></tr>';
    return;
  }

  tbody.innerHTML = stream.map(item => {
    const isAuto = item.resolution_type === 'AUTO_RESOLVE';
    const actorBadge = isAuto 
      ? '<span class="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950 text-emerald-400 border border-emerald-800">AI Employee</span>'
      : '<span class="px-2 py-0.5 rounded text-[10px] font-mono bg-indigo-950 text-indigo-400 border border-indigo-800">Reviewer Lead</span>';
    
    const actionBadge = `<span class="font-mono text-[11px] text-slate-200">${item.action}</span>`;
    const timeStr = item.resolved_at ? new Date(item.resolved_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '--';

    return `
      <tr class="hover:bg-slate-900/60 transition">
        <td class="py-3 px-3 font-mono font-bold text-emerald-400">${item.exception_id}</td>
        <td class="py-3 px-3 font-medium text-slate-200">${item.title}</td>
        <td class="py-3 px-3 text-[11px] text-slate-400 font-mono">${item.type}</td>
        <td class="py-3 px-3">${actionBadge}</td>
        <td class="py-3 px-3 font-mono font-bold ${item.confidence >= 90 ? 'text-emerald-400' : 'text-amber-400'}">${item.confidence}%</td>
        <td class="py-3 px-3">${actorBadge}</td>
        <td class="py-3 px-3 text-slate-400 font-mono text-[11px]">${timeStr}</td>
      </tr>
    `;
  }).join('');
}

