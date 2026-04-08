/* ═══════════════════════════════════════════════════════════════
   8BIT LEGENDS v2.0 - Client-side JavaScript
   TinyMCE WYSIWYG editor + AI panel
   ═══════════════════════════════════════════════════════════════ */

// ── TinyMCE Helpers ──────────────────────────────────────────

function getEditorContent() {
    if (window.tinyEditor) {
        return window.tinyEditor.getContent();
    }
    const el = document.getElementById('htmlEditor');
    return el ? el.value : '';
}

function setEditorContent(html, raw) {
    if (window.tinyEditor) {
        window.tinyEditor.undoManager.add();   // snapshot current state for Ctrl+Z
        if (raw) {
            // Bypass TinyMCE's HTML parser — preserves WP classes and structure
            window.tinyEditor.setContent(html, {format: 'raw'});
        } else {
            window.tinyEditor.setContent(html);
        }
        window.tinyEditor.undoManager.add();   // snapshot new state
    }
}

function insertAtCursor(html) {
    if (window.tinyEditor) {
        window.tinyEditor.execCommand('mceInsertContent', false, html);
    }
}

function getSelectedText() {
    if (window.tinyEditor) {
        return window.tinyEditor.selection.getContent();
    }
    return '';
}

function replaceSelection(html) {
    if (window.tinyEditor) {
        window.tinyEditor.selection.setContent(html);
    }
}

// ── Save Post ────────────────────────────────────────────────

function savePost() {
    const btn = document.getElementById('saveBtn');
    if (!btn || btn.classList.contains('loading')) return;

    const title = document.getElementById('postTitle').value.trim();
    const tags = document.getElementById('postTags').value.trim();
    const featuredImage = document.getElementById('postImage').value.trim();
    const realName = (document.getElementById('postRealName') || {}).value || '';
    const filename = document.getElementById('postFilename').value;
    const body = getEditorContent();

    if (!title) {
        showNotification('Title is required', 'error');
        return;
    }

    btn.classList.add('loading');

    fetch('/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            title, tags, featured_image: featuredImage,
            real_name: realName.trim(),
            body, filename, format: 'html'
        })
    })
    .then(r => r.json())
    .then(data => {
        btn.classList.remove('loading');
        if (data.ok) {
            showNotification(data.message, 'success');
            if (!filename && data.filename) {
                document.getElementById('postFilename').value = data.filename;
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

// ── Tag Helpers ──────────────────────────────────────────────

function addTag(tag) {
    const input = document.getElementById('postTags');
    if (!input) return;

    const current = input.value.split(',').map(t => t.trim()).filter(Boolean);
    if (!current.includes(tag)) {
        current.push(tag);
        input.value = current.join(', ');
    }
}

// ── AI Create Post (one-shot) ────────────────────────────────

function aiCreatePost() {
    const btn = document.getElementById('createPostBtn');
    if (!btn || btn.classList.contains('loading')) return;

    const rawInput = document.getElementById('aiSourceUrl').value.trim();
    if (!rawInput) {
        showNotification('Paste one or more URLs or type a scene handle', 'error');
        return;
    }

    // Split by newlines, filter empty lines
    const sources = rawInput.split('\n').map(s => s.trim()).filter(Boolean);

    btn.classList.add('loading');

    // Show status area with progress
    const statusArea = document.getElementById('aiStatus');
    const statusBody = document.getElementById('aiStatusBody');
    if (statusArea) statusArea.style.display = 'block';
    const sourceCount = sources.length;
    if (statusBody) statusBody.innerHTML = '<span class="ai-progress">Scraping ' + sourceCount + ' source' + (sourceCount > 1 ? 's' : '') + ' and generating memorial post...</span>';

    fetch('/ai/create-post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sources: sources })
    })
    .then(r => r.json())
    .then(data => {
        btn.classList.remove('loading');
        if (data.ok) {
            // Fill the entire editor with generated content
            if (data.content) {
                setEditorContent(data.content);
            }
            // Set title
            if (data.title) {
                document.getElementById('postTitle').value = data.title;
            }
            // Set tags
            if (data.tags && data.tags.length) {
                document.getElementById('postTags').value = data.tags.join(', ');
            }
            // Set real name if found
            if (data.real_name) {
                var rnEl = document.getElementById('postRealName');
                if (rnEl) rnEl.value = data.real_name;
            }

            // Show what was found in the status area
            if (statusBody) {
                let statusHtml = '<span class="ai-status-success">Post generated!</span>';
                if (data.profile_info) {
                    statusHtml += '<span class="ai-status-info"> Found: ' + data.profile_info + '</span>';
                }
                statusHtml += '<span class="ai-status-hint"> Edit the content above, then save when ready.</span>';
                statusBody.innerHTML = statusHtml;
            }

            showNotification('Memorial post created! Edit it above.', 'success');
        } else {
            showNotification(data.error || 'Generation failed', 'error');
            if (statusBody) {
                statusBody.innerHTML = '<span class="ai-status-error">' + (data.error || 'Generation failed') + '</span>';
            }
        }
    })
    .catch(err => {
        btn.classList.remove('loading');
        showNotification('Failed: ' + err.message, 'error');
        if (statusBody) {
            statusBody.innerHTML = '<span class="ai-status-error">Failed: ' + err.message + '</span>';
        }
    });
}

// ── AI Research & Create ────────────────────────────────────

function aiResearchCreate() {
    const btn = document.getElementById('researchCreateBtn');
    if (!btn || btn.classList.contains('loading')) return;

    const rawInput = document.getElementById('aiSourceUrl').value.trim();
    if (!rawInput) {
        showNotification('Type a scene handle or name to search for', 'error');
        return;
    }

    // Send full input — backend detects URLs vs handle names
    const handle = rawInput;

    btn.classList.add('loading');

    const statusArea = document.getElementById('aiStatus');
    const statusBody = document.getElementById('aiStatusBody');
    if (statusArea) statusArea.style.display = 'block';
    if (statusBody) statusBody.innerHTML = '<span class="ai-progress">Searching CSDB, Pouet for "' + handle + '"...</span>';

    fetch('/ai/research-create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ handle: handle })
    })
    .then(r => r.json())
    .then(data => {
        btn.classList.remove('loading');
        if (data.ok) {
            if (data.content) {
                setEditorContent(data.content);
            }
            if (data.title) {
                document.getElementById('postTitle').value = data.title;
            }
            if (data.tags && data.tags.length) {
                document.getElementById('postTags').value = data.tags.join(', ');
            }
            if (data.real_name) {
                var rnEl = document.getElementById('postRealName');
                if (rnEl) rnEl.value = data.real_name;
            }

            if (statusBody) {
                let statusHtml = '<span class="ai-status-success">Post generated!</span>';
                if (data.search_info) {
                    statusHtml += '<span class="ai-status-info"> ' + data.search_info + '</span>';
                }
                if (data.found_urls) {
                    statusHtml += '<br><span class="ai-status-hint">Sources: ' + data.found_urls.join(', ') + '</span>';
                }
                statusHtml += '<br><span class="ai-status-hint">Edit the content above, then save when ready.</span>';
                statusBody.innerHTML = statusHtml;
            }

            showNotification('Memorial post created from research!', 'success');
        } else {
            showNotification(data.error || 'Research failed', 'error');
            if (statusBody) {
                statusBody.innerHTML = '<span class="ai-status-error">' + (data.error || 'Research failed') + '</span>';
            }
        }
    })
    .catch(err => {
        btn.classList.remove('loading');
        showNotification('Failed: ' + err.message, 'error');
        if (statusBody) {
            statusBody.innerHTML = '<span class="ai-status-error">Failed: ' + err.message + '</span>';
        }
    });
}

// ── AI Restyle Post ─────────────────────────────────────────

function aiRestylePost() {
    const btn = document.getElementById('restylePostBtn');
    if (!btn || btn.classList.contains('loading')) return;

    const content = getEditorContent();
    if (!content || content.trim().length < 50) {
        showNotification('Post content is too short to restyle', 'error');
        return;
    }

    // Optional supplementary sources
    const rawInput = (document.getElementById('aiSourceUrl').value || '').trim();
    const sources = rawInput ? rawInput.split('\n').map(s => s.trim()).filter(Boolean) : [];

    // Get metadata from editor fields
    const realName = (document.getElementById('postRealName').value || '').trim();
    const title = (document.getElementById('postTitle').value || '').trim();
    const preset = (document.getElementById('restylePreset') || {}).value || 'default';
    const presetNames = { default: 'Dark Cinematic', c64: 'C64 Retro', amiga: 'Amiga Demo' };

    btn.classList.add('loading');

    const statusArea = document.getElementById('aiStatus');
    const statusBody = document.getElementById('aiStatusBody');
    if (statusArea) statusArea.style.display = 'block';
    if (statusBody) statusBody.innerHTML = '<span class="ai-progress">Restyling post with ' + (presetNames[preset] || preset) + ' theme...</span>';

    fetch('/ai/restyle-post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: content, sources: sources, real_name: realName, title: title, preset: preset })
    })
    .then(r => r.json())
    .then(data => {
        btn.classList.remove('loading');
        if (data.ok) {
            if (data.content) {
                setEditorContent(data.content);
            }
            if (data.title) {
                document.getElementById('postTitle').value = data.title;
            }
            if (statusBody) {
                statusBody.innerHTML = '<span class="ai-status-success">Post restyled!</span><span class="ai-status-hint"> Review the content above, then save when ready.</span>';
            }
            showNotification('Post restyled! Review and save.', 'success');
        } else {
            showNotification(data.error || 'Restyle failed', 'error');
            if (statusBody) {
                statusBody.innerHTML = '<span class="ai-status-error">' + (data.error || 'Restyle failed') + '</span>';
            }
        }
    })
    .catch(err => {
        btn.classList.remove('loading');
        showNotification('Failed: ' + err.message, 'error');
        if (statusBody) {
            statusBody.innerHTML = '<span class="ai-status-error">Failed: ' + err.message + '</span>';
        }
    });
}

// ── AI Enhance Selection ─────────────────────────────────────

function aiEnhance() {
    const btn = document.getElementById('enhanceBtn');
    if (!btn || btn.classList.contains('loading')) return;

    const selectedText = getSelectedText();
    if (!selectedText.trim()) {
        showNotification('Select some text in the editor first, then click Enhance', 'error');
        return;
    }

    btn.classList.add('loading');

    fetch('/ai/enhance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            text: selectedText,
            instruction: 'Make this more detailed and heartfelt, using demoscene vocabulary naturally'
        })
    })
    .then(r => r.json())
    .then(data => {
        btn.classList.remove('loading');
        if (data.ok) {
            replaceSelection(data.content);
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

// ── Publish ──────────────────────────────────────────────────

function publishPost(filename, status) {
    const modal = document.getElementById('publishModal');
    const resultEl = document.getElementById('publishResult');

    if (resultEl) {
        resultEl.style.display = 'none';
        resultEl.className = 'modal-result';
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

// ── Fetch single post from WordPress ─────────────────────────

function fetchFromWordPress() {
    const btn = document.getElementById('fetchWpBtn');
    const wpId = document.getElementById('wpPostId')?.value;
    if (!btn || !wpId) return;
    if (btn.classList.contains('loading')) return;

    if (!confirm('Fetch the latest version from WordPress? Your unsaved editor changes will be replaced (Ctrl+Z to undo).')) return;

    btn.classList.add('loading');
    btn.textContent = 'FETCHING...';

    fetch('/fetch-wp/' + wpId, { method: 'POST' })
    .then(r => r.json())
    .then(data => {
        btn.classList.remove('loading');
        btn.innerHTML = '<span class="btn-icon">&darr;</span> FETCH WP';
        if (data.ok) {
            // Update editor fields with fetched data
            document.getElementById('postTitle').value = data.title || '';
            document.getElementById('postTags').value = data.tags || '';
            document.getElementById('postImage').value = data.featured_image || '';
            setEditorContent(data.body || '', true);
            showNotification('Fetched latest from WordPress — review and save when ready', 'success');
        } else {
            showNotification(data.error || 'Fetch failed', 'error');
        }
    })
    .catch(err => {
        btn.classList.remove('loading');
        btn.innerHTML = '<span class="btn-icon">&darr;</span> FETCH WP';
        showNotification('Fetch failed: ' + err.message, 'error');
    });
}

// ── Delete Post ──────────────────────────────────────────────

function deletePost(filename) {
    if (!confirm('Delete ' + filename + '? This cannot be undone.')) return;

    fetch('/delete/' + encodeURIComponent(filename), { method: 'POST' })
    .then(r => r.json())
    .then(data => {
        if (data.ok) {
            showNotification(data.message, 'success');
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

// ── Logo Generator ──────────────────────────────────────────

// Load available fonts on page load
(function loadLogoFonts() {
    const select = document.getElementById('logoFont');
    if (!select) return;
    fetch('/logo/fonts')
        .then(r => r.json())
        .then(data => {
            if (data.ok && data.fonts) {
                data.fonts.forEach(f => {
                    const opt = document.createElement('option');
                    opt.value = f.name;
                    opt.textContent = f.name + ' (' + f.height + 'px, ' + (f.year || '?') + ' by ' + (f.maker || '?') + ')';
                    select.appendChild(opt);
                });
            }
        })
        .catch(() => {});
})();

var _lastLogoDataUri = null;

// Wire up scale slider label
(function() {
    const slider = document.getElementById('logoScale');
    const label = document.getElementById('logoScaleValue');
    if (slider && label) {
        slider.addEventListener('input', function() {
            label.textContent = this.value + '%';
        });
    }
})();

function _getLogoMaxWidth() {
    const slider = document.getElementById('logoScale');
    const pct = slider ? parseInt(slider.value) : 60;
    return Math.round(880 * pct / 100);
}

function previewLogo() {
    const handle = document.getElementById('logoHandle').value.trim();
    if (!handle) {
        showNotification('Type a handle name first', 'error');
        return;
    }

    const font = document.getElementById('logoFont').value;
    const area = document.getElementById('logoPreviewArea');
    const btn = document.getElementById('logoPreviewBtn');
    if (btn) btn.classList.add('loading');

    const maxW = _getLogoMaxWidth();
    let url = '/logo/' + encodeURIComponent(handle) + '?max_width=' + maxW;
    if (font) url += '&font=' + encodeURIComponent(font);

    // Fetch as blob to show preview, then also get base64 for insertion
    fetch(url)
        .then(r => {
            if (!r.ok) throw new Error('Logo generation failed');
            return r.blob();
        })
        .then(blob => {
            if (btn) btn.classList.remove('loading');
            const imgUrl = URL.createObjectURL(blob);
            area.innerHTML = '<img src="' + imgUrl + '" alt="' + handle + ' logo">';
            area.classList.add('has-preview');

            // Also convert to data URI for insertion
            const reader = new FileReader();
            reader.onload = function() {
                _lastLogoDataUri = reader.result;
            };
            reader.readAsDataURL(blob);
        })
        .catch(err => {
            if (btn) btn.classList.remove('loading');
            showNotification('Logo preview failed: ' + err.message, 'error');
        });
}

function insertLogo() {
    const handle = document.getElementById('logoHandle').value.trim();
    if (!handle) {
        showNotification('Type a handle name and preview first', 'error');
        return;
    }

    if (!_lastLogoDataUri) {
        // Auto-preview then insert
        const font = document.getElementById('logoFont').value;
        const btn = document.getElementById('logoInsertBtn');
        if (btn) btn.classList.add('loading');

        const maxW = _getLogoMaxWidth();
        let url = '/logo/' + encodeURIComponent(handle) + '?max_width=' + maxW;
        if (font) url += '&font=' + encodeURIComponent(font);
        fetch(url)
            .then(r => r.blob())
            .then(blob => {
                const reader = new FileReader();
                reader.onload = function() {
                    _lastLogoDataUri = reader.result;
                    _doInsertLogo(handle);
                    if (btn) btn.classList.remove('loading');
                };
                reader.readAsDataURL(blob);
            })
            .catch(err => {
                if (btn) btn.classList.remove('loading');
                showNotification('Failed: ' + err.message, 'error');
            });
        return;
    }

    _doInsertLogo(handle);
}

function _doInsertLogo(handle) {
    const logoHtml = '<div style="text-align:center;margin:0 0 1.5rem;padding:0">' +
        '<img src="' + _lastLogoDataUri + '" alt="' + handle + '" ' +
        'style="display:inline-block;max-width:100%;height:auto;image-rendering:pixelated;border-radius:8px;box-shadow:0 4px 16px rgba(0,0,0,0.6)">' +
        '</div>';

    // Insert at the very top of the editor content
    const current = getEditorContent();
    if (current.trim()) {
        setEditorContent(logoHtml + '\n' + current);
    } else {
        setEditorContent(logoHtml);
    }
    showNotification('Logo inserted at top of post!', 'success');
    _lastLogoDataUri = null;
}

// ── AI Chat Assistant ────────────────────────────────────────

function aiChat() {
    const input = document.getElementById('aiChatInput');
    const btn = document.getElementById('aiChatBtn');
    const instruction = input.value.trim();
    if (!instruction || (btn && btn.classList.contains('loading'))) return;

    const currentContent = getEditorContent();
    if (!currentContent.trim()) {
        showNotification('No content in editor to modify', 'error');
        return;
    }

    // Show user message
    appendChatMessage('user', instruction);
    input.value = '';
    if (btn) btn.classList.add('loading');

    fetch('/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ instruction, content: currentContent })
    })
    .then(r => r.json())
    .then(data => {
        if (btn) btn.classList.remove('loading');
        if (data.ok) {
            setEditorContent(data.content);
            appendChatMessage('ai', data.summary || 'Done! Content updated.');
        } else {
            appendChatMessage('ai', 'Error: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(err => {
        if (btn) btn.classList.remove('loading');
        appendChatMessage('ai', 'Error: ' + err.message);
    });
}

function appendChatMessage(role, text) {
    const container = document.getElementById('aiChatMessages');
    if (!container) return;

    // Remove welcome message on first use
    const welcome = container.querySelector('.ai-chat-welcome');
    if (welcome) welcome.remove();

    const msg = document.createElement('div');
    msg.className = 'ai-chat-msg ai-chat-' + role;
    msg.textContent = text;
    container.appendChild(msg);
    container.scrollTop = container.scrollHeight;
}

// ── Notifications ────────────────────────────────────────────

function showNotification(message, type) {
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
