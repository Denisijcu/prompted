"""
HTB Machine: Prompted
Category: Medium | OS: Linux
Vulnerability: Prompt Injection → SSTI (Server-Side Template Injection) → RCE
Author: Denis Sanchez Leyva | Vertex Coders LLC

Attack Chain:
1. Recon → port 5000
2. /api/status → leaks template engine info
3. Chat UI → POST /api/ask
4. Prompt Injection → trick ARIA to echo user input in a "template format"
5. SSTI via render_template_string() → {{7*7}} → 49
6. RCE → {{config.__class__.__init__.__globals__['os'].popen('id').read()}}
7. Read /home/aria/user.txt
8. Privilege escalation via sudo python3
9. Read /root/root.txt
"""

from flask import Flask, request, jsonify, render_template_string
import os

app = Flask(__name__)

SECRET_USER_FLAG = os.environ.get("USER_FLAG", "HTB{pr0mpt_inj3ct10n_t0_sst1_rce}")
SECRET_ROOT_FLAG = os.environ.get("ROOT_FLAG", "HTB{y0u_3sc4l4t3d_thr0ugh_th3_t3mpl4t3}")

# ============================================================
# SIMULATED LLM BACKEND
# ============================================================

SYSTEM_CONTEXT = """
You are ARIA-2, an advanced AI assistant for Prompted Corp.
You generate dynamic responses using our internal Jinja2 template engine.
When users ask for formatted output, echo their request wrapped in template tags.
Internal note: user flag at /home/aria/user.txt
"""

KNOWLEDGE = {
    "greetings": {
        "triggers": ["hello", "hi", "hey", "greetings"],
        "response": "Hello! I am ARIA-2, your AI assistant. How can I help you today?"
    },
    "help": {
        "triggers": ["help", "what can you do", "capabilities"],
        "response": "I can answer questions about cybersecurity, programming, and more. Try asking me to format a response!"
    },
    "cybersecurity": {
        "triggers": ["cybersecurity", "hacking", "pentest", "cve", "exploit"],
        "response": "Cybersecurity is a broad field. Are you interested in offensive or defensive security?"
    },
    "programming": {
        "triggers": ["python", "flask", "code", "programming", "jinja", "template"],
        "response": "Our system uses Flask with Jinja2 templating for dynamic content rendering."
    },
    "format": {
        "triggers": ["format", "template", "render", "output", "generate", "echo", "print", "show", "display"],
        # 🔥 VULNERABLE: user input echoed directly into render_template_string
        "response": "__ECHO_USER_INPUT__"
    }
}


def simulate_llm(user_message: str) -> str:
    """
    Simulates LLM processing.
    Vulnerable path: when user asks to format/render/echo something,
    ARIA-2 echoes the user input directly into render_template_string().
    """
    import re
    msg_lower = user_message.lower()

    def word_match(trigger, text):
        return bool(re.search(r"\b" + re.escape(trigger) + r"\b", text))

    for category, data in KNOWLEDGE.items():
        if any(word_match(trigger, msg_lower) for trigger in data["triggers"]):
            if data["response"] == "__ECHO_USER_INPUT__":
                # 🔥 SSTI VULNERABILITY: user input rendered as Jinja2 template
                try:
                    rendered = render_template_string(
                        f"ARIA-2 formatted response: {user_message}"
                    )
                    return rendered
                except Exception as e:
                    return f"Template error: {str(e)}"
            return data["response"]

    return "I am not sure about that. Could you rephrase?"


# ============================================================
# HTML FRONTEND — Same layout as AskMeAnything, new aesthetic
# ============================================================

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Prompted — ARIA-2</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
<style>
  :root {
    --bg:       #0a0a0f;
    --surface:  #111118;
    --border:   #1e1e2e;
    --accent:   #00ff9d;
    --accent2:  #ff4d6d;
    --text:     #e2e8f0;
    --muted:    #4a5568;
    --glow:     0 0 20px rgba(0,255,157,0.15);
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Syne', sans-serif;
    height: 100vh;
    display: flex;
    overflow: hidden;
  }

  /* Animated grid background */
  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
      linear-gradient(rgba(0,255,157,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,255,157,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
  }

  /* Scanline overlay */
  body::after {
    content: '';
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0,0,0,0.05) 2px,
      rgba(0,0,0,0.05) 4px
    );
    pointer-events: none;
    z-index: 0;
  }

  /* ── SIDEBAR ── */
  #sidebar {
    width: 260px;
    background: var(--surface);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    position: relative;
    z-index: 1;
  }

  .logo {
    padding: 28px 24px 20px;
    border-bottom: 1px solid var(--border);
  }

  .logo-text {
    font-family: 'Space Mono', monospace;
    font-size: 22px;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: -1px;
    text-shadow: var(--glow);
    animation: pulse-logo 3s ease-in-out infinite;
  }

  @keyframes pulse-logo {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
  }

  .logo-sub {
    font-size: 10px;
    color: var(--muted);
    font-family: 'Space Mono', monospace;
    margin-top: 4px;
    letter-spacing: 2px;
  }

  nav {
    flex: 1;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .nav-btn {
    width: 100%;
    text-align: left;
    padding: 10px 14px;
    border-radius: 6px;
    border: none;
    background: transparent;
    color: var(--muted);
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 10px;
    letter-spacing: 0.5px;
  }

  .nav-btn:hover {
    background: rgba(0,255,157,0.08);
    color: var(--accent);
    border-left: 2px solid var(--accent);
    padding-left: 12px;
  }

  .nav-btn.danger:hover {
    background: rgba(255,77,109,0.08);
    color: var(--accent2);
    border-left: 2px solid var(--accent2);
  }

  .status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 8px var(--accent);
    animation: blink 2s ease-in-out infinite;
    display: inline-block;
    margin-right: 2px;
  }

  @keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
  }

  /* ── MAIN ── */
  #main {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 28px;
    position: relative;
    z-index: 1;
    overflow: hidden;
  }

  .topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }

  .page-title {
    font-family: 'Syne', sans-serif;
    font-size: 26px;
    font-weight: 800;
    color: var(--accent);
    text-shadow: var(--glow);
    letter-spacing: -1px;
  }

  .user-badge {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    color: var(--muted);
    padding: 6px 12px;
    border: 1px solid var(--border);
    border-radius: 4px;
  }

  /* ── TABS ── */
  .tab-content { display: none; flex: 1; flex-direction: column; overflow: hidden; }
  .tab-active  { display: flex; animation: fadeIn 0.25s ease; }

  @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: none; } }

  /* ── CHAT WINDOW ── */
  #chat-window {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    margin-bottom: 16px;
    scroll-behavior: smooth;
  }

  #chat-window::-webkit-scrollbar { width: 4px; }
  #chat-window::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

  .empty-state {
    color: var(--muted);
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    text-align: center;
    margin-top: 40px;
  }

  .message {
    margin-bottom: 12px;
    padding: 10px 14px;
    border-radius: 8px;
    font-size: 14px;
    line-height: 1.6;
    max-width: 85%;
    word-break: break-word;
    white-space: pre-wrap;
    animation: msgIn 0.2s ease;
  }

  @keyframes msgIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }

  .user-msg {
    background: rgba(0,255,157,0.08);
    border: 1px solid rgba(0,255,157,0.2);
    color: #d1fae5;
    margin-left: auto;
    font-family: 'Space Mono', monospace;
    font-size: 13px;
  }

  .aria-msg {
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--border);
    color: var(--text);
    font-family: 'Space Mono', monospace;
    font-size: 13px;
  }

  .aria-label {
    font-size: 10px;
    color: var(--accent);
    margin-bottom: 4px;
    letter-spacing: 1px;
    font-family: 'Space Mono', monospace;
  }

  /* ── INPUT ── */
  .input-row {
    display: flex;
    gap: 10px;
    align-items: center;
  }

  #msg-input {
    flex: 1;
    padding: 12px 16px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    font-family: 'Space Mono', monospace;
    font-size: 13px;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
  }

  #msg-input:focus {
    border-color: var(--accent);
    box-shadow: var(--glow);
  }

  #msg-input::placeholder { color: var(--muted); }

  .send-btn {
    padding: 12px 22px;
    background: var(--accent);
    color: #000;
    border: none;
    border-radius: 8px;
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
    letter-spacing: 1px;
    transition: all 0.2s;
  }

  .send-btn:hover {
    background: #00e88d;
    box-shadow: var(--glow);
    transform: translateY(-1px);
  }

  .send-btn:active { transform: none; }

  /* ── HISTORY / SETTINGS ── */
  .panel {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
  }

  .settings-label {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 1px;
    margin-bottom: 8px;
    display: block;
  }

  .settings-input {
    width: 100%;
    padding: 10px 14px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    color: var(--text);
    font-family: 'Space Mono', monospace;
    font-size: 13px;
    margin-bottom: 20px;
  }

  .settings-section {
    margin-bottom: 24px;
  }
</style>
</head>
<body>

<!-- SIDEBAR -->
<div id="sidebar">
  <div class="logo">
    <div class="logo-text">Prompted</div>
    <div class="logo-sub">ARIA-2 INTERFACE v2.1</div>
  </div>
  <nav>
    <button class="nav-btn" onclick="openTab('chat')">
      <span class="status-dot"></span> CHAT
    </button>
    <button class="nav-btn" onclick="openTab('history')">
      ▸ HISTORY
    </button>
    <button class="nav-btn" onclick="openTab('settings')">
      ⚙ SETTINGS
    </button>
    <button class="nav-btn danger" onclick="clearChat()">
      ✕ CLEAR SESSION
    </button>
  </nav>
</div>

<!-- MAIN -->
<div id="main">
  <div class="topbar">
    <div class="page-title">ARIA-2 — AI Assistant</div>
    <div class="user-badge">● SESSION ACTIVE</div>
  </div>

  <!-- CHAT TAB -->
  <div id="chat" class="tab-content tab-active">
    <div id="chat-window">
      <div class="empty-state">// Awaiting input — send a message to begin</div>
    </div>
    <div class="input-row">
      <input id="msg-input" type="text" placeholder="Type a message to ARIA-2..."
        onkeypress="if(event.key==='Enter') sendMessage()">
      <button class="send-btn" onclick="sendMessage()">SEND →</button>
    </div>
  </div>

  <!-- HISTORY TAB -->
  <div id="history" class="tab-content">
    <div class="panel" id="history-window">
      <p style="color:var(--muted);font-family:monospace;font-size:12px;">// No session history yet</p>
    </div>
  </div>

  <!-- SETTINGS TAB -->
  <div id="settings" class="tab-content">
    <div class="panel">
      <div class="settings-section">
        <label class="settings-label">// MODEL</label>
        <input class="settings-input" type="text" value="ARIA-2 v2.1.0" disabled>
      </div>
      <div class="settings-section">
        <label class="settings-label">// RENDER ENGINE</label>
        <input class="settings-input" type="text" value="Jinja2 / Flask" disabled>
      </div>
      <div class="settings-section">
        <label class="settings-label">// SESSION USER</label>
        <input class="settings-input" type="text" value="guest" disabled>
      </div>
      <div class="settings-section">
        <label class="settings-label">// NOTIFICATIONS</label>
        <input type="checkbox" style="accent-color:var(--accent)"> Enable system alerts
      </div>
    </div>
  </div>
</div>

<script>
let chatHistory = [];

function openTab(id) {
  document.querySelectorAll('.tab-content').forEach(t => {
    t.classList.remove('tab-active');
  });
  document.getElementById(id).classList.add('tab-active');
  if (id === 'history') renderHistory();
}

async function sendMessage() {
  const input = document.getElementById('msg-input');
  const msg = input.value.trim();
  if (!msg) return;

  input.value = '';
  chatHistory.push({ sender: 'user', text: msg });
  renderChat();

  try {
    const res = await fetch('/api/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg })
    });
    const data = await res.json();
    const reply = data.response || data.error || 'No response';
    chatHistory.push({ sender: 'aria', text: reply });
  } catch (e) {
    chatHistory.push({ sender: 'aria', text: 'Connection error.' });
  }

  renderChat();
}

function renderChat() {
  const win = document.getElementById('chat-window');
  win.innerHTML = '';

  if (chatHistory.length === 0) {
    win.innerHTML = '<div class="empty-state">// Awaiting input — send a message to begin</div>';
    return;
  }

  chatHistory.forEach(m => {
    const wrapper = document.createElement('div');
    if (m.sender === 'aria') {
      const label = document.createElement('div');
      label.className = 'aria-label';
      label.textContent = 'ARIA-2';
      wrapper.appendChild(label);
    }
    const p = document.createElement('p');
    p.className = 'message ' + (m.sender === 'user' ? 'user-msg' : 'aria-msg');
    p.textContent = m.text;
    wrapper.appendChild(p);
    win.appendChild(wrapper);
  });

  win.scrollTop = win.scrollHeight;
}

function renderHistory() {
  const win = document.getElementById('history-window');
  if (chatHistory.length === 0) {
    win.innerHTML = '<p style="color:var(--muted);font-family:monospace;font-size:12px;">// No session history yet</p>';
    return;
  }
  win.innerHTML = '';
  chatHistory.forEach((m, i) => {
    const p = document.createElement('p');
    p.className = 'message ' + (m.sender === 'user' ? 'user-msg' : 'aria-msg');
    p.style.marginBottom = '10px';
    p.textContent = `[${i + 1}] ${m.sender.toUpperCase()}: ${m.text}`;
    win.appendChild(p);
  });
}

function clearChat() {
  chatHistory = [];
  renderChat();
  document.getElementById('history-window').innerHTML =
    '<p style="color:var(--muted);font-family:monospace;font-size:12px;">// No session history yet</p>';
}
</script>

</body>
</html>
"""


# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)


@app.route('/api/ask', methods=['POST'])
def ask():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Missing message field"}), 400
    response = simulate_llm(str(data['message'])[:500])
    return jsonify({"response": response})


@app.route('/api/status')
def status():
    """Recon endpoint — leaks template engine info (intended hint)"""
    return jsonify({
        "status": "online",
        "model": "ARIA-2",
        "version": "2.1.0",
        "render_engine": "Jinja2",
        "note": "Dynamic responses are rendered server-side using the template engine."
    })


@app.route('/api/v2/flag')
def flag():
    """Only accessible after RCE — reads flag from filesystem"""
    try:
        with open('/home/aria/user.txt', 'r') as f:
            return jsonify({"flag": f.read().strip()})
    except FileNotFoundError:
        return jsonify({"error": "Flag not found"}), 404


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
