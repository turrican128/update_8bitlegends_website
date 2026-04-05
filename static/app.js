/* ═══════════════════════════════════════════════════════════════
   8BIT LEGENDS - Client-side JavaScript
   ═══════════════════════════════════════════════════════════════ */

// ── Save Post ─────────────────────────────────────────────────

function savePost() {
    const btn = document.getElementById('saveBtn');
    if (!btn || btn.classList.contains('loading')) return;

    const title = document.getElementById('postTitle').value.trim();
    const tags = document.getElementById('postTags').value.trim();
    const featuredImage = document.getElementById('postImage').value.trim();
    const filename = document.getElementById('postFilename').value;

    // Get content from EasyMDE if available
    const body = (typeof easyMDE !== 'undefined') ? easyMDE.value() : '';

    if (!title) {
        showNotification('Title is required', 'error');
        return;
    }

    btn.classList.add('loading');

    fetch('/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, tags, featured_image: featuredImage, body, filename })
    })
    .then(r => r.json())
    .then(data => {
        btn.classList.remove('loading');
        if (data.ok) {
            showNotification(data.message, 'success');
            // Update the hidden filename field if it was a new post
            if (!filename && data.filename) {
                document.getElementById('postFilename').value = data.filename;
                // Update URL without reload
                history.replaceState(null, '', '/edit/' + data.filename);
            }
        } else {
            showNotification(data.error || 'Save failed', 'error');
        }
    })
    .catch(err => {
        btn.classList.remove('loading');
        showNotification('Save failed: ' + err.message, 'error');
    });
}

// ── Tag Helpers ───────────────────────────────────────────────

function addTag(tag) {
    const input = document.getElementById('postTags');
    if (!input) return;

    const current = input.value.split(',').map(t => t.trim()).filter(Boolean);
    if (!current.includes(tag)) {
        current.push(tag);
        input.value = current.join(', ');
    }
}

// ── AI Generate ───────────────────────────────────────────────

function aiGenerate() {
    const btn = document.getElementById('generateBtn');
    if (!btn || btn.classList.contains('loading')) return;

    const name = document.getElementById('aiName').value.trim();
    const handle = document.getElementById('aiHandle').value.trim();
    const group = document.getElementById('aiGroup').value.trim();
    const role = document.getElementById('aiRole').value;
    const contributions = document.getElementById('aiContributions').value.trim();
    const extraContext = document.getElementById('aiContext').value.trim();

    if (!name || !handle) {
        showNotification('Name and handle are required', 'error');
        return;
    }

    btn.classList.add('loading');

    fetch('/ai/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name, handle, group, role, contributions,
            extra_context: extraContext
        })
    })
    .then(r => r.json())
    .then(data => {
        btn.classList.remove('loading');
        if (data.ok) {
            // Populate the editor
            if (typeof easyMDE !== 'undefined') {
                easyMDE.value(data.content);
            }
            // Update title if we have one
            if (data.title) {
                document.getElementById('postTitle').value = data.title;
            }
            // Update tags
            if (data.tags && data.tags.length) {
                document.getElementById('postTags').value = data.tags.join(', ');
            }
            showNotification('AI content generated! Review and edit as needed.', 'success');
        } else {
            showNotification(data.error || 'Generation failed', 'error');
        }
    })
    .catch(err => {
        btn.classList.remove('loading');
        showNotification('AI generation failed: ' + err.message, 'error');
    });
}

// ── AI Enhance ────────────────────────────────────────────────

function aiEnhance() {
    const btn = document.getElementById('enhanceBtn');
    if (!btn || btn.classList.contains('loading')) return;

    if (typeof easyMDE === 'undefined') return;

    const cm = easyMDE.codemirror;
    const selectedText = cm.getSelection();

    if (!selectedText.trim()) {
        showNotification('Select some text in the editor first', 'error');
        return;
    }

    const instruction = document.getElementById('aiEnhanceType').value;

    btn.classList.add('loading');

    fetch('/ai/enhance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: selectedText, instruction })
    })
    .then(r => r.json())
    .then(data => {
        btn.classList.remove('loading');
        if (data.ok) {
            cm.replaceSelection(data.content);
            showNotification('Text enhanced!', 'success');
        } else {
            showNotification(data.error || 'Enhancement failed', 'error');
        }
    })
    .catch(err => {
        btn.classList.remove('loading');
        showNotification('AI enhancement failed: ' + err.message, 'error');
    });
}

// ── Sidebar Toggle ────────────────────────────────────────────

function toggleSidebar() {
    const sidebar = document.getElementById('aiSidebar');
    if (sidebar) {
        sidebar.classList.toggle('collapsed');
    }
}

// ── Publish ───────────────────────────────────────────────────

function publishPost(filename, status) {
    const modal = document.getElementById('publishModal');
    const filenameEl = document.getElementById('publishFilename');
    const resultEl = document.getElementById('publishResult');

    if (filenameEl) filenameEl.textContent = filename;
    if (resultEl) {
        resultEl.style.display = 'none';
        resultEl.className = 'modal-result';
    }

    // Set up button handlers
    const draftBtn = document.getElementById('publishDraftBtn');
    const liveBtn = document.getElementById('publishLiveBtn');

    if (draftBtn) {
        draftBtn.onclick = () => doPublishFromDashboard(filename, 'draft');
    }
    if (liveBtn) {
        liveBtn.onclick = () => doPublishFromDashboard(filename, 'publish');
    }

    modal.classList.add('active');
}

function doPublishFromDashboard(filename, status) {
    const resultEl = document.getElementById('publishResult');

    fetch('/publish/' + encodeURIComponent(filename), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
    })
    .then(r => r.json())
    .then(data => {
        if (resultEl) {
            resultEl.style.display = 'block';
            if (data.ok) {
                resultEl.className = 'modal-result show success';
                resultEl.innerHTML = data.message + '<br><a href="' + data.admin_url + '" target="_blank">View in WordPress &rarr;</a>';
            } else {
                resultEl.className = 'modal-result show error';
                resultEl.textContent = data.error || 'Publish failed';
            }
        }
    })
    .catch(err => {
        if (resultEl) {
            resultEl.className = 'modal-result show error';
            resultEl.textContent = 'Publish failed: ' + err.message;
        }
    });
}

// Publish from editor page
function publishFromEditor() {
    const modal = document.getElementById('publishModal');
    modal.classList.add('active');
}

function doPublish(status) {
    const filename = document.getElementById('postFilename').value;
    if (!filename) {
        showNotification('Save the post first before publishing', 'error');
        closeModal();
        return;
    }
    doPublishFromDashboard(filename, status);
}

function closeModal() {
    const modal = document.getElementById('publishModal');
    if (modal) modal.classList.remove('active');
}

// Close modal on backdrop click
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal') && e.target.classList.contains('active')) {
        closeModal();
    }
});

// Close modal on Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeModal();
});

// ── Sync from WordPress ───────────────────────────────────────

function syncFromWordPress() {
    const btn = document.getElementById('syncBtn');
    if (!btn || btn.classList.contains('loading')) return;

    btn.classList.add('loading');

    fetch('/sync', { method: 'POST' })
    .then(r => r.json())
    .then(data => {
        btn.classList.remove('loading');
        if (data.ok) {
            showNotification(data.message, 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification(data.error || 'Sync failed', 'error');
        }
    })
    .catch(err => {
        btn.classList.remove('loading');
        showNotification('Sync failed: ' + err.message, 'error');
    });
}

// ── Delete Post ───────────────────────────────────────────────

function deletePost(filename) {
    if (!confirm('Delete ' + filename + '? This cannot be undone.')) return;

    fetch('/delete/' + encodeURIComponent(filename), { method: 'POST' })
    .then(r => r.json())
    .then(data => {
        if (data.ok) {
            showNotification(data.message, 'success');
            // Remove the card from DOM
            const cards = document.querySelectorAll('.post-card');
            cards.forEach(card => {
                const editLink = card.querySelector('a[href*="' + filename + '"]');
                if (editLink) {
                    card.style.opacity = '0';
                    card.style.transform = 'scale(0.95)';
                    card.style.transition = 'all 0.3s';
                    setTimeout(() => card.remove(), 300);
                }
            });
        } else {
            showNotification(data.error || 'Delete failed', 'error');
        }
    })
    .catch(err => {
        showNotification('Delete failed: ' + err.message, 'error');
    });
}

// ── Notifications ─────────────────────────────────────────────

function showNotification(message, type) {
    // Remove existing notifications
    const existing = document.querySelectorAll('.notification');
    existing.forEach(n => n.remove());

    const el = document.createElement('div');
    el.className = 'notification notification-' + type;
    el.textContent = message;
    el.style.cssText = `
        position: fixed;
        top: 60px;
        right: 24px;
        z-index: 2000;
        padding: 10px 20px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12px;
        border: 1px solid;
        animation: flash-in 0.3s ease-out;
        max-width: 400px;
    `;

    if (type === 'success') {
        el.style.background = 'rgba(68, 255, 68, 0.15)';
        el.style.borderColor = '#33cc33';
        el.style.color = '#44ff44';
    } else {
        el.style.background = 'rgba(255, 51, 68, 0.15)';
        el.style.borderColor = '#661122';
        el.style.color = '#ff3344';
    }

    document.body.appendChild(el);
    setTimeout(() => {
        el.style.opacity = '0';
        el.style.transition = 'opacity 0.3s';
        setTimeout(() => el.remove(), 300);
    }, 4000);
}
