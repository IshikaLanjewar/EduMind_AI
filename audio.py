"""Browser-side Text-to-Speech and Voice Input via Streamlit HTML."""

import re
import streamlit as st
import streamlit.components.v1 as components


def _sanitise(text: str) -> str:
    text = re.sub(r"[#*_`>~\[\]]+", "", text)
    text = text.replace("\\", "")
    text = text.replace("'", " ")
    text = text.replace('"', " ")
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text[:2000]


def render_tts_player(text: str) -> None:
    rate = st.session_state.get("voice_rate", 150)
    api_rate = round(rate / 150, 2)
    safe = _sanitise(text)

    html = f"""
<div style="display:flex;align-items:center;gap:8px;padding:8px 12px;
     background:#f0eeff;border-radius:10px;border:1px solid #d0c8ff;margin:4px 0;
     font-family:sans-serif">
  <button id="playBtn" onclick="doSpeak()"
    style="background:#6c63ff;color:#fff;border:none;border-radius:8px;
           padding:5px 14px;cursor:pointer;font-size:13px;white-space:nowrap">
    ▶ Listen
  </button>
  <button onclick="window.speechSynthesis.cancel();
                  document.getElementById('playBtn').textContent='▶ Listen';"
    style="background:#ff6584;color:#fff;border:none;border-radius:8px;
           padding:5px 10px;cursor:pointer;font-size:13px">
    ■
  </button>
  <span style="font-size:11px;color:#7c7ca0;overflow:hidden;
               text-overflow:ellipsis;white-space:nowrap;flex:1">
    AI audio response
  </span>
</div>
<script>
(function(){{
  var spoken = false;
  function doSpeak(){{
    window.speechSynthesis.cancel();
    var utt = new SpeechSynthesisUtterance('{safe}');
    utt.rate  = {api_rate};
    utt.pitch = 1.0;
    var btn = document.getElementById('playBtn');
    btn.textContent = '🔊 Speaking…';
    utt.onend  = function(){{ btn.textContent = '▶ Listen'; }};
    utt.onerror = function(){{ btn.textContent = '▶ Listen'; }};
    window.speechSynthesis.speak(utt);
  }}
  function tryAuto(){{
    if(spoken) return;
    var voices = window.speechSynthesis.getVoices();
    if(voices.length > 0){{ spoken=true; doSpeak(); }}
    else {{ setTimeout(tryAuto, 300); }}
  }}
  window.speechSynthesis.onvoiceschanged = tryAuto;
  setTimeout(tryAuto, 500);
  window.doSpeak = doSpeak;
}})();
</script>
"""
    components.html(html, height=56, scrolling=False)


def render_voice_input() -> None:
    components.html(
        """
<div style="font-family:sans-serif;padding:6px 0">
  <button id="micBtn" onclick="toggleRec()"
    style="background:#6c63ff;color:#fff;border:none;border-radius:10px;
           padding:9px 18px;font-size:13px;cursor:pointer;margin-bottom:6px">
    🎙 Click to Speak
  </button>
  <div id="status" style="font-size:11px;color:#7c7ca0;margin-bottom:4px;min-height:16px"></div>
  <div id="transcript" style="font-size:13px;font-weight:500;color:#1a1a2e;
       background:#f3f1ff;border-radius:8px;padding:6px 10px;min-height:32px;
       word-break:break-word;white-space:pre-wrap">(transcript appears here)</div>
  <div style="font-size:11px;color:#aaa;margin-top:4px">Copy the transcript above → paste into the chat box below</div>
</div>
<script>
(function(){{
  var recognition = null;
  var recording = false;

  function getSR(){{
    return window.SpeechRecognition || window.webkitSpeechRecognition || null;
  }}

  window.toggleRec = function(){{
    var SR = getSR();
    if(!SR){{
      document.getElementById('status').textContent =
        '⚠ Speech recognition not supported. Use Google Chrome or Edge.';
      return;
    }}
    if(recording){{
      if(recognition) recognition.stop();
      return;
    }}
    recognition = new SR();
    recognition.lang = 'en-US';
    recognition.interimResults = true;
    recognition.continuous = false;

    recognition.onstart = function(){{
      recording = true;
      document.getElementById('micBtn').textContent = '🔴 Stop Recording';
      document.getElementById('micBtn').style.background = '#ff6584';
      document.getElementById('status').textContent = 'Listening… speak now';
      document.getElementById('transcript').textContent = '';
    }};

    recognition.onresult = function(e){{
      var t = '';
      for(var i = 0; i < e.results.length; i++) t += e.results[i][0].transcript;
      document.getElementById('transcript').textContent = t;
    }};

    recognition.onend = function(){{
      recording = false;
      document.getElementById('micBtn').textContent = '🎙 Click to Speak';
      document.getElementById('micBtn').style.background = '#6c63ff';
      document.getElementById('status').textContent = '✅ Done — copy the transcript above into the chat box';
    }};

    recognition.onerror = function(e){{
      recording = false;
      document.getElementById('micBtn').textContent = '🎙 Click to Speak';
      document.getElementById('micBtn').style.background = '#6c63ff';
      document.getElementById('status').textContent = '⚠ Error: ' + e.error + '. Make sure microphone is allowed.';
    }};

    recognition.start();
  }};
}})();
</script>
""",
        height=170,
        scrolling=False,
    )
