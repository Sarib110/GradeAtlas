const STORAGE_KEY = 'student-planner-state-v1';

const state = {
  subjects: [],
  timetable: [],
  settings: {
    currentGPA: null,
    totalSubjects: 0
  }
};

const elements = {};

function generateId() {
  if (window.crypto && window.crypto.randomUUID) return window.crypto.randomUUID();
  return `id-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function loadState() {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (!saved) return;
  try {
    const parsed = JSON.parse(saved);
    state.subjects = Array.isArray(parsed.subjects) ? parsed.subjects : [];
    state.timetable = Array.isArray(parsed.timetable) ? parsed.timetable : [];
    state.settings = { ...state.settings, ...parsed.settings };
  } catch (error) {
    console.error('Unable to parse saved data', error);
  }
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function formatDuration(start, end) {
  const [h1, m1] = start.split(':').map(Number);
  const [h2, m2] = end.split(':').map(Number);
  const startMinutes = h1 * 60 + m1;
  const endMinutes = h2 * 60 + m2;
  return Math.max(0, (endMinutes - startMinutes) / 60);
}

function getGradeLabel(value) {
  if (value === null || value === undefined || value === '') return 'N/A';
  const num = Number(value);
  if (Number.isNaN(num)) return 'N/A';
  return `${Math.min(100, Math.max(0, num))}%`;
}

function renderDashboard() {
  const totalSubjects = state.subjects.length;
  const totalHours = state.timetable.reduce((sum, row) => sum + Number(row.duration || 0), 0);
  const completed = totalSubjects && state.settings.totalSubjects ? Math.min(100, Math.round((totalSubjects / state.settings.totalSubjects) * 100)) : 0;

  if (elements.cardTotalSubjects) elements.cardTotalSubjects.textContent = String(totalSubjects);
  if (elements.cardCurrentGPA) elements.cardCurrentGPA.textContent = state.settings.currentGPA !== null ? state.settings.currentGPA.toFixed(2) : '—';
  if (elements.cardStudyHours) elements.cardStudyHours.textContent = `${totalHours.toFixed(1)}`;
  if (elements.cardProgressFill) elements.cardProgressFill.style.width = `${completed}%`;
  if (elements.cardProgressLabel) elements.cardProgressLabel.textContent = `${completed}% complete`;
}

function createFieldBlock(index) {
  const wrapper = document.createElement('div');
  wrapper.className = 'subject-item';

  const fields = document.createElement('div');
  fields.className = 'subject-entry';
  fields.innerHTML = `
    <label>Subject name</label>
    <input type="text" class="field-name" placeholder="Subject ${index + 1} name">
    <label>Current grade (%) <span class="hint">optional</span></label>
    <input type="number" min="0" max="100" class="field-grade" placeholder="Optional grade">
  `;

  const remove = document.createElement('button');
  remove.type = 'button';
  remove.className = 'btn small-btn';
  remove.textContent = 'Remove';
  remove.addEventListener('click', () => {
    wrapper.remove();
    updateSubjectCountInput();
  });

  wrapper.appendChild(fields);
  wrapper.appendChild(remove);
  return wrapper;
}

function renderDynamicFields(count) {
  elements.dynamicFields.innerHTML = '';
  const currentCount = Math.max(0, Math.min(20, count));
  for (let i = 0; i < currentCount; i += 1) {
    elements.dynamicFields.appendChild(createFieldBlock(i));
  }
}

function updateSubjectCountInput() {
  const fields = elements.dynamicFields.querySelectorAll('.subject-item');
  elements.subjectCountInput.value = fields.length > 0 ? String(fields.length) : '';
}

function renderSubjectList() {
  elements.subjectList.innerHTML = '';
  if (!state.subjects.length) {
    elements.subjectList.innerHTML = '<div class="empty-state">No subjects added yet. Use the forms above to save your first subject.</div>';
    return;
  }

  state.subjects.forEach((subject) => {
    const subjectCard = document.createElement('div');
    subjectCard.className = 'subject-item';
    subjectCard.innerHTML = `
      <div class="subject-entry">
        <span class="subject-name">${subject.name}</span>
        <span class="subject-meta">Grade: ${getGradeLabel(subject.grade)} • Created: ${new Date(subject.addedAt).toLocaleDateString()}</span>
      </div>
      <div class="subject-actions">
        <button class="small-btn" type="button" data-action="delete" data-id="${subject.id}">Delete</button>
      </div>
    `;

    subjectCard.querySelector('[data-action="delete"]').addEventListener('click', () => {
      removeSubject(subject.id);
    });

    elements.subjectList.appendChild(subjectCard);
  });
}

function renderSubjectOptions() {
  const select = elements.entrySubject;
  select.innerHTML = '';
  if (!state.subjects.length) {
    const option = document.createElement('option');
    option.value = '';
    option.textContent = 'No subjects available';
    select.appendChild(option);
    select.disabled = true;
    return;
  }

  select.disabled = false;
  state.subjects.forEach((subject) => {
    const option = document.createElement('option');
    option.value = subject.id;
    option.textContent = subject.name;
    select.appendChild(option);
  });
}

function renderSchedule() {
  elements.scheduleBody.innerHTML = '';
  if (!state.timetable.length) {
    elements.scheduleBody.innerHTML = '<tr><td colspan="6" class="empty-state">Your timetable is empty. Add a new schedule entry to begin.</td></tr>';
    elements.timetableSummary.innerHTML = '<p class="empty-state">Track your weekly schedule here once you add entries.</p>';
    return;
  }

  const sorted = [...state.timetable].sort((a, b) => {
    const days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
    const dayA = days.indexOf(a.day);
    const dayB = days.indexOf(b.day);
    if (dayA !== dayB) return dayA - dayB;
    return a.start.localeCompare(b.start);
  });

  sorted.forEach((entry) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${entry.subject}</td>
      <td>${entry.day}</td>
      <td>${entry.start}</td>
      <td>${entry.end}</td>
      <td>${entry.duration.toFixed(1)}h</td>
      <td>
        <div class="action-buttons">
          <button class="small-btn" type="button" data-action="edit" data-id="${entry.id}">Edit</button>
          <button class="small-btn" type="button" data-action="delete" data-id="${entry.id}">Delete</button>
        </div>
      </td>
    `;

    row.querySelector('[data-action="edit"]').addEventListener('click', () => openEditModal(entry.id));
    row.querySelector('[data-action="delete"]').addEventListener('click', () => deleteTimetableEntry(entry.id));
    elements.scheduleBody.appendChild(row);
  });

  renderScheduleSummary();
}

function renderScheduleSummary() {
  const totalHours = state.timetable.reduce((sum, row) => sum + Number(row.duration || 0), 0);
  const subjectCount = state.subjects.length;
  elements.timetableSummary.innerHTML = `
    <div class="summary-card">
      <span class="card-title">Entries</span>
      <strong>${state.timetable.length}</strong>
      <p class="subject-meta">Sessions currently planned.</p>
    </div>
    <div class="summary-card">
      <span class="card-title">Hours planned</span>
      <strong>${totalHours.toFixed(1)}h</strong>
      <p class="subject-meta">Total session time for this week.</p>
    </div>
    <div class="summary-card">
      <span class="card-title">Subjects used</span>
      <strong>${subjectCount}</strong>
      <p class="subject-meta">Available subjects for scheduling.</p>
    </div>
  `;
}

function showModal(type, title, message) {
  const overlay = document.getElementById('modal-overlay');
  const icon = document.getElementById('modal-icon');
  const titleEl = document.getElementById('modal-title');
  const messageEl = document.getElementById('modal-message');

  const typeMap = {
    success: { icon: '✔', color: 'var(--success)' },
    warning: { icon: '⚠', color: 'var(--warning)' },
    error: { icon: '✖', color: 'var(--danger)' }
  };

  const meta = typeMap[type] || typeMap.success;
  icon.textContent = meta.icon;
  icon.style.background = meta.color;
  titleEl.textContent = title;
  messageEl.textContent = message;
  overlay.hidden = false;
}

function hideModal() {
  document.getElementById('modal-overlay').hidden = true;
}

function showConfirm() {
  document.getElementById('confirm-overlay').hidden = false;
}

function hideConfirm() {
  document.getElementById('confirm-overlay').hidden = true;
}

function removeSubject(id) {
  state.subjects = state.subjects.filter((subject) => subject.id !== id);
  state.timetable = state.timetable.filter((entry) => entry.subjectId !== id);
  state.settings.totalSubjects = state.subjects.length;
  saveState();
  renderSubjectList();
  renderSubjectOptions();
  renderSchedule();
  renderDashboard();
  showModal('success', 'Removed', 'Subject and related timetable entries were deleted.');
}

function clearAllData() {
  state.subjects = [];
  state.timetable = [];
  state.settings = { currentGPA: null, totalSubjects: 0 };
  localStorage.removeItem(STORAGE_KEY);
  renderSubjectList();
  renderSubjectOptions();
  renderSchedule();
  renderDashboard();
  hideConfirm();
  showModal('success', 'Cleared', 'All planner data has been removed.');
}

function addSubjectFromFields() {
  const blocks = [...elements.dynamicFields.querySelectorAll('.subject-item')];
  if (!blocks.length) {
    showModal('warning', 'No fields', 'Create subject fields first before saving items.');
    return;
  }

  let added = 0;
  blocks.forEach((block) => {
    const nameInput = block.querySelector('.field-name');
    const gradeInput = block.querySelector('.field-grade');
    const name = nameInput?.value.trim();
    const grade = gradeInput?.value.trim();
    if (!name) return;
    state.subjects.push({ id: generateId(), name, grade: grade === '' ? null : Number(grade), addedAt: Date.now() });
    added += 1;
  });

  if (!added) {
    showModal('warning', 'No subjects added', 'Please fill at least one subject name before saving.');
    return;
  }

  state.settings.totalSubjects = state.subjects.length;
  saveState();
  renderSubjectList();
  renderSubjectOptions();
  renderDashboard();
  showModal('success', 'Subjects saved', `Added ${added} subject${added > 1 ? 's' : ''} successfully.`);
}

function addQuickSubject() {
  const name = elements.quickName.value.trim();
  const gradeValue = elements.quickGrade.value.trim();
  if (!name) {
    showModal('error', 'Missing name', 'Please enter a subject name before adding.');
    return;
  }

  state.subjects.push({ id: generateId(), name, grade: gradeValue === '' ? null : Number(gradeValue), addedAt: Date.now() });
  elements.quickName.value = '';
  elements.quickGrade.value = '';
  state.settings.totalSubjects = state.subjects.length;
  saveState();
  renderSubjectList();
  renderSubjectOptions();
  renderDashboard();
  showModal('success', 'Subject added', `${name} is now available in your planner.`);
}

function savePlannerGPA() {
  const value = elements.plannerGPAInput.value.trim();
  if (value === '') {
    state.settings.currentGPA = null;
  } else {
    const gpa = Number(value);
    if (Number.isNaN(gpa) || gpa < 0 || gpa > 4) {
      showModal('error', 'Invalid GPA', 'Enter a GPA between 0.00 and 4.00, or leave blank.');
      return;
    }
    state.settings.currentGPA = Math.round(gpa * 100) / 100;
  }
  saveState();
  renderDashboard();
  showModal('success', 'GPA saved', 'Your current GPA has been updated.');
}

function validateTimetableEntry(subjectId, day, start, end, ignoreId = null) {
  if (!subjectId || !day || !start || !end) {
    return { valid: false, message: 'Please select a subject, day, and start/end times.' };
  }

  if (end <= start) {
    return { valid: false, message: 'End time must be later than start time.' };
  }

  const duration = formatDuration(start, end);
  if (duration < 0.5) {
    return { valid: false, message: '⚠ This time slot is too short for effective study' };
  }

  const conflict = state.timetable.some((entry) => {
    if (entry.day !== day) return false;
    if (ignoreId && entry.id === ignoreId) return false;
    return entry.start < end && start < entry.end;
  });

  if (conflict) {
    return { valid: false, message: '⚠ Time conflict detected! Please choose a different time.' };
  }

  return { valid: true, duration };
}

function addTimetableEntry() {
  const subjectId = elements.entrySubject.value;
  const day = elements.entryDay.value;
  const start = elements.entryStart.value;
  const end = elements.entryEnd.value;

  const validation = validateTimetableEntry(subjectId, day, start, end);
  if (!validation.valid) {
    showModal(validation.message.startsWith('⚠') ? 'warning' : 'error', 'Unable to add entry', validation.message);
    return;
  }

  const subject = state.subjects.find((item) => item.id === subjectId);
  state.timetable.push({ id: generateId(), subjectId, subject: subject?.name || 'Unknown', day, start, end, duration: validation.duration });
  saveState();
  renderSchedule();
  renderDashboard();
  showModal('success', 'Entry added', 'Your timetable entry has been saved.');
  elements.entryStart.value = '';
  elements.entryEnd.value = '';
}

function deleteTimetableEntry(id) {
  state.timetable = state.timetable.filter((entry) => entry.id !== id);
  saveState();
  renderSchedule();
  renderDashboard();
  showModal('success', 'Entry removed', 'The timetable entry was deleted.');
}

function openEditModal(entryId) {
  const entry = state.timetable.find((item) => item.id === entryId);
  if (!entry) return;
  const subjectOptions = state.subjects.map((subject) => `<option value="${subject.id}" ${subject.id === entry.subjectId ? 'selected' : ''}>${subject.name}</option>`).join('');

  const overlay = document.getElementById('modal-overlay');
  overlay.hidden = false;
  overlay.innerHTML = `
    <div class="modal-card">
      <div class="modal-icon" style="background: var(--accent);">✎</div>
      <h3>Edit entry</h3>
      <div class="field-row">
        <label>Subject</label>
        <select id="edit-entry-subject">${subjectOptions}</select>
      </div>
      <div class="field-row-grid">
        <div>
          <label>Day</label>
          <select id="edit-entry-day">
            <option value="Monday">Monday</option>
            <option value="Tuesday">Tuesday</option>
            <option value="Wednesday">Wednesday</option>
            <option value="Thursday">Thursday</option>
            <option value="Friday">Friday</option>
            <option value="Saturday">Saturday</option>
            <option value="Sunday">Sunday</option>
          </select>
        </div>
        <div>
          <label>Start</label>
          <input type="time" id="edit-entry-start" value="${entry.start}">
        </div>
        <div>
          <label>End</label>
          <input type="time" id="edit-entry-end" value="${entry.end}">
        </div>
      </div>
      <div class="modal-actions">
        <button class="btn btn-secondary" id="edit-cancel-btn" type="button">Cancel</button>
        <button class="btn btn-primary" id="edit-save-btn" type="button">Save changes</button>
      </div>
    </div>
  `;

  document.getElementById('edit-entry-day').value = entry.day;
  document.getElementById('edit-cancel-btn').addEventListener('click', () => {
    overlay.hidden = true;
    initModalMarkup();
  });
  document.getElementById('edit-save-btn').addEventListener('click', () => saveEditedEntry(entryId));
}

function saveEditedEntry(entryId) {
  const subjectId = document.getElementById('edit-entry-subject')?.value;
  const day = document.getElementById('edit-entry-day')?.value;
  const start = document.getElementById('edit-entry-start')?.value;
  const end = document.getElementById('edit-entry-end')?.value;

  const validation = validateTimetableEntry(subjectId, day, start, end, entryId);
  if (!validation.valid) {
    showModal(validation.message.startsWith('⚠') ? 'warning' : 'error', 'Unable to save', validation.message);
    return;
  }

  const entry = state.timetable.find((item) => item.id === entryId);
  if (!entry) return;
  const subject = state.subjects.find((item) => item.id === subjectId);

  entry.subjectId = subjectId;
  entry.subject = subject?.name || entry.subject;
  entry.day = day;
  entry.start = start;
  entry.end = end;
  entry.duration = validation.duration;

  saveState();
  renderSchedule();
  renderDashboard();
  initModalMarkup();
  showModal('success', 'Updated', 'Timetable entry has been updated.');
}

function initModalMarkup() {
  const overlay = document.getElementById('modal-overlay');
  if (!overlay) return;
  overlay.innerHTML = `
    <div class="modal-card" id="modal-card">
      <div class="modal-icon" id="modal-icon">✓</div>
      <h3 id="modal-title">Success</h3>
      <p id="modal-message">Your action was successful.</p>
      <div class="modal-actions">
        <button class="btn btn-primary" id="modal-ok-btn">OK</button>
      </div>
    </div>
  `;
  overlay.hidden = true;
  const okBtn = document.getElementById('modal-ok-btn');
  if (okBtn) okBtn.addEventListener('click', hideModal);
}

/* Compatibility wrapper functions (do not replace existing logic) */
function addSubject() {
  // Prefer quick add if a name is present, otherwise use dynamic fields
  try {
    if (elements && elements.quickName && elements.quickName.value.trim()) {
      addQuickSubject();
      return;
    }
    addSubjectFromFields();
  } catch (e) {
    console.error('addSubject wrapper error', e);
    showModal('error', 'Error', 'Unable to add subject.');
  }
}

function deleteSubject(id) {
  try {
    removeSubject(id);
  } catch (e) {
    console.error('deleteSubject wrapper error', e);
    showModal('error', 'Error', 'Unable to delete subject.');
  }
}

function editTimetableEntry(id) {
  try {
    openEditModal(id);
  } catch (e) {
    console.error('editTimetableEntry wrapper error', e);
    showModal('error', 'Error', 'Unable to open edit modal.');
  }
}

function saveToLocalStorage() {
  try {
    saveState();
  } catch (e) {
    console.error('saveToLocalStorage error', e);
  }
}

function loadFromLocalStorage() {
  try {
    loadState();
    renderSubjectList();
    renderSubjectOptions();
    renderSchedule();
    renderDashboard();
  } catch (e) {
    console.error('loadFromLocalStorage error', e);
  }
}

function validateTimeSlots(subjectId, day, start, end, ignoreId = null) {
  return validateTimetableEntry(subjectId, day, start, end, ignoreId);
}

function showPopup(type, message) {
  const title = type && typeof type === 'string' ? type.charAt(0).toUpperCase() + type.slice(1) : 'Notice';
  showModal(type, title, message);
}

function updateDashboard() {
  try {
    renderDashboard();
  } catch (e) {
    console.error('updateDashboard error', e);
  }
}

function bindEvents() {
  if (elements.createFieldsBtn) {
    elements.createFieldsBtn.addEventListener('click', () => {
      const value = Number(elements.subjectCountInput.value);
      if (!Number.isInteger(value) || value < 1) {
        showModal('error', 'Invalid number', 'Enter a positive subject count.');
        return;
      }
      renderDynamicFields(value);
    });
  }

  if (elements.saveFieldsBtn) elements.saveFieldsBtn.addEventListener('click', addSubjectFromFields);
  if (elements.addSubjectBtn) elements.addSubjectBtn.addEventListener('click', addQuickSubject);
  if (elements.saveGpaBtn) elements.saveGpaBtn.addEventListener('click', savePlannerGPA);
  if (elements.addEntryBtn) elements.addEntryBtn.addEventListener('click', addTimetableEntry);
  if (elements.clearDataBtn) elements.clearDataBtn.addEventListener('click', showConfirm);

  const confirmYes = document.getElementById('confirm-yes-btn');
  const confirmCancel = document.getElementById('confirm-cancel-btn');
  const modalOverlayEl = document.getElementById('modal-overlay');
  if (confirmYes) confirmYes.addEventListener('click', clearAllData);
  if (confirmCancel) confirmCancel.addEventListener('click', hideConfirm);
  if (modalOverlayEl) modalOverlayEl.addEventListener('click', (event) => {
    if (event.target === modalOverlayEl) hideModal();
  });
}

function initElements() {
  elements.subjectCountInput = document.getElementById('subject-count');
  elements.createFieldsBtn = document.getElementById('create-fields-btn');
  elements.dynamicFields = document.getElementById('dynamic-fields');
  elements.saveFieldsBtn = document.getElementById('save-fields-btn');
  elements.quickName = document.getElementById('quick-name');
  elements.quickGrade = document.getElementById('quick-grade');
  elements.addSubjectBtn = document.getElementById('add-subject-btn');
  elements.plannerGPAInput = document.getElementById('planner-gpa-input');
  elements.saveGpaBtn = document.getElementById('save-gpa-btn');
  elements.subjectList = document.getElementById('subject-list');
  elements.entrySubject = document.getElementById('entry-subject');
  elements.entryDay = document.getElementById('entry-day');
  elements.entryStart = document.getElementById('entry-start');
  elements.entryEnd = document.getElementById('entry-end');
  elements.addEntryBtn = document.getElementById('add-entry-btn');
  elements.scheduleBody = document.getElementById('schedule-body');
  elements.timetableSummary = document.getElementById('timetable-summary');
  elements.cardTotalSubjects = document.getElementById('card-total-subjects');
  elements.cardCurrentGPA = document.getElementById('card-current-gpa');
  elements.cardStudyHours = document.getElementById('card-study-hours');
  elements.cardProgressFill = document.getElementById('card-progress-fill');
  elements.cardProgressLabel = document.getElementById('card-progress-label');
  elements.clearDataBtn = document.getElementById('clear-data-btn');
}

function initialize() {
  initElements();
  bindEvents();
  loadState();
  renderSubjectList();
  renderSubjectOptions();
  renderSchedule();
  renderDashboard();
  initModalMarkup();
}

document.addEventListener('DOMContentLoaded', initialize);
