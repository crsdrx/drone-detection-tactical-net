let notes = JSON.parse(localStorage.getItem('notes')) || [];
let research = JSON.parse(localStorage.getItem('research')) || [];

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', (e) => {
    const tab = e.target.dataset.tab;
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    e.target.classList.add('active');
    document.getElementById(tab).classList.add('active');
  });
});

function addNote() {
  const title = document.getElementById('note-title').value;
  const content = document.getElementById('note-content').value;
  const tags = document.getElementById('note-tags').value.split(',').map(t => t.trim()).filter(t => t);
  
  if (!title || !content) { alert('Title and content required'); return; }
  
  notes.push({
    id: Date.now(),
    title, content, tags,
    created: new Date().toLocaleString()
  });
  
  localStorage.setItem('notes', JSON.stringify(notes));
  document.getElementById('note-title').value = '';
  document.getElementById('note-content').value = '';
  document.getElementById('note-tags').value = '';
  renderNotes();
}

function addResource() {
  const url = document.getElementById('res-url').value;
  const title = document.getElementById('res-title').value;
  const type = document.getElementById('res-type').value;
  const topic = document.getElementById('res-topic').value;
  const notes_text = document.getElementById('res-notes').value;
  
  if (!url || !title) { alert('URL and title required'); return; }
  
  research.push({
    id: Date.now(),
    url, title, type, topic, notes: notes_text,
    saved: new Date().toLocaleString()
  });
  
  localStorage.setItem('research', JSON.stringify(research));
  document.getElementById('res-url').value = '';
  document.getElementById('res-title').value = '';
  document.getElementById('res-topic').value = '';
  document.getElementById('res-notes').value = '';
  renderResearch();
}

function renderNotes() {
  const html = notes.map(n => `
    <div style="background: #1a1a1a; padding: 10px; margin: 10px 0; border-left: 3px solid #4dd0e1;">
      <strong>${n.title}</strong>
      <p style="font-size: 0.9em; color: #888;">${n.created}</p>
      <p>${n.content.substring(0, 100)}...</p>
      <small>${n.tags.join(', ')}</small>
      <button onclick="deleteNote(${n.id})" style="margin-top: 5px; background: #ff6b6b;">Delete</button>
    </div>
  `).join('');
  document.getElementById('notes-list').innerHTML = html || '<p>No notes yet</p>';
}

function renderResearch() {
  const byTopic = {};
  research.forEach(r => {
    if (!byTopic[r.topic]) byTopic[r.topic] = [];
    byTopic[r.topic].push(r);
  });
  
  const html = Object.entries(byTopic).map(([topic, items]) => `
    <h3 style="color: #4dd0e1; margin-top: 20px;">${topic || 'Untagged'} (${items.length})</h3>
    ${items.map(r => `
      <div style="background: #1a1a1a; padding: 10px; margin: 10px 0; border-left: 3px solid #4dd0e1;">
        <a href="${r.url}" target="_blank" style="color: #4dd0e1; text-decoration: none;"><strong>${r.title}</strong></a>
        <p style="font-size: 0.9em; color: #888;">${r.type} • ${r.saved}</p>
        ${r.notes ? '<p>' + r.notes + '</p>' : ''}
        <button onclick="deleteResource(${r.id})" style="margin-top: 5px; background: #ff6b6b;">Delete</button>
      </div>
    `).join('')}
  `).join('');
  
  document.getElementById('research-list').innerHTML = html || '<p>No resources yet</p>';
}

function deleteNote(id) {
  notes = notes.filter(n => n.id !== id);
  localStorage.setItem('notes', JSON.stringify(notes));
  renderNotes();
}

function deleteResource(id) {
  research = research.filter(r => r.id !== id);
  localStorage.setItem('research', JSON.stringify(research));
  renderResearch();
}

renderNotes();
renderResearch();
