const API = '';
let toastTimer;

function toast(msg) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('show'), 2000);
}

function updateCounts(total) {
  document.getElementById('total-count').textContent = String(total);
  document.getElementById('today-count').textContent = String(total);
  document.getElementById('links-counter').textContent = `${total} lien${total > 1 ? 's' : ''}`;
}

function showError(msg) {
  const el = document.getElementById('error-box');
  el.textContent = msg;
  el.classList.add('show');
}

function hideError() {
  document.getElementById('error-box').classList.remove('show');
}

async function loadLinks() {
  const res = await fetch(`${API}/links`);
  const links = await res.json();
  renderLinks(links);
}

function renderLinks(links) {
  const container = document.getElementById('links-list');
  updateCounts(links.length);

  if (!links.length) {
    container.innerHTML = '<div class="empty">Aucun lien pour l\'instant</div>';
    return;
  }

  container.innerHTML = links.map((l, index) => `
    <div class="link-item" id="item-${l.slug}" style="animation-delay:${index * 45}ms;">
      <a class="link-slug" href="${l.short_url}" target="_blank" rel="noopener noreferrer">/${l.slug}</a>
      <span class="link-original" title="${l.original_url}">${l.original_url}</span>
      <button class="delete-btn" onclick="deleteLink('${l.slug}')" title="Supprimer">X</button>
    </div>
  `).join('');
}

document.getElementById('submit-btn').addEventListener('click', createLink);
document.getElementById('url-input').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') createLink();
});

async function createLink() {
  const input = document.getElementById('url-input');
  const url = input.value.trim();
  if (!url) return;

  hideError();
  document.getElementById('result').classList.add('hidden');
  document.getElementById('submit-btn').disabled = true;

  try {
    const res = await fetch(`${API}/links`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    const data = await res.json();

    if (!res.ok) {
      showError(data.detail || 'Erreur lors de la création.');
      return;
    }

    document.getElementById('result-url').textContent = data.short_url;
    document.getElementById('result').classList.remove('hidden');
    input.value = '';
    loadLinks();
  } catch {
    showError('Impossible de joindre le serveur.');
  } finally {
    document.getElementById('submit-btn').disabled = false;
  }
}

document.getElementById('copy-btn').addEventListener('click', () => {
  const url = document.getElementById('result-url').textContent;
  navigator.clipboard.writeText(url).then(() => toast('Lien copie'));
});

async function deleteLink(slug) {
  const item = document.getElementById(`item-${slug}`);
  item.style.opacity = '0.35';

  try {
    await fetch(`${API}/links/${slug}`, { method: 'DELETE' });
    item.remove();
    toast('Lien supprime');
    loadLinks();
  } catch {
    item.style.opacity = '1';
    toast('Erreur lors de la suppression');
  }
}

loadLinks();
