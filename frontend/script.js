// API Configuration
const API_URL = '/api';

// DOM Elements
const messagesDiv = document.getElementById('messages');
const questionInput = document.getElementById('questionInput');
const sendBtn = document.getElementById('sendBtn');
const micBtn = document.getElementById('micButton');
const speakerBtn = document.getElementById('speakerButton');
const voiceModal = document.getElementById('voiceModal');
const speakerModal = document.getElementById('speakerModal');
const closeMicModal = document.getElementById('closeMicModal');
const closeSpeakerModal = document.getElementById('closeSpeakerModal');
const cancelMicBtn = document.getElementById('cancelMicBtn');
const cancelSpeakerBtn = document.getElementById('cancelSpeakerBtn');
const voiceStatusText = document.getElementById('voiceStatusText');
const speakerStatusText = document.getElementById('speakerStatusText');
const typingIndicator = document.getElementById('typingIndicator');
const loadingOverlay = document.getElementById('loadingOverlay');

// State
let lastBotAnswer = '';
let currentUtterance = null;

// ---------- Speech Synthesis (Auto + Manual) ----------
function speakText(text, showModal = true) {
    if (!('speechSynthesis' in window)) return;
    if (currentUtterance) window.speechSynthesis.cancel();

    // Optional: open speaker modal to show visual feedback
    if (showModal) {
        openModal(speakerModal);
        speakerStatusText.textContent = '🔊 बोल रहा हूँ... Speaking...';
        speakerStatusText.style.color = '#ffa000';
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'hi-IN';
    utterance.rate = 0.9;
    utterance.pitch = 1;

    const setVoice = () => {
        const voices = window.speechSynthesis.getVoices();
        const hindiVoice = voices.find(v => v.lang === 'hi-IN');
        if (hindiVoice) utterance.voice = hindiVoice;
        window.speechSynthesis.speak(utterance);
    };

    if (window.speechSynthesis.getVoices().length) setVoice();
    else window.speechSynthesis.onvoiceschanged = setVoice;

    utterance.onstart = () => {
        if (showModal) speakerStatusText.textContent = '🔊 सुनाए जा रहे... Playing...';
    };
    utterance.onend = () => {
        currentUtterance = null;
        if (showModal) closeModal(speakerModal);
    };
    utterance.onerror = (err) => {
        console.error('Speech error:', err);
        if (showModal) {
            speakerStatusText.textContent = '❌ त्रुटि, पुनः प्रयास करें।';
            setTimeout(() => closeModal(speakerModal), 1500);
        }
    };
    currentUtterance = utterance;
}

// ---------- Speech Recognition (Mic) ----------
let recognition = null;
let isListening = false;

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = 'hi-IN';
    recognition.continuous = false;
    recognition.interimResults = false;
    
    recognition.onstart = () => {
        isListening = true;
        voiceStatusText.textContent = '🎤 सुन रहा हूँ... Speak now...';
        voiceStatusText.style.color = '#ffa000';
    };
    recognition.onend = () => { isListening = false; };
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        voiceStatusText.textContent = '✅ सुन लिया! Got it!';
        voiceStatusText.style.color = '#4caf50';
        setTimeout(() => {
            closeModal(voiceModal);
            questionInput.value = transcript;
            sendMessage();
        }, 1000);
    };
    recognition.onerror = (event) => {
        let errorMsg = '❌ त्रुटि! ';
        if (event.error === 'no-speech') errorMsg += 'कुछ नहीं सुना। पुनः प्रयास करें।';
        else if (event.error === 'not-allowed') errorMsg += 'माइक्रोफोन की अनुमति नहीं।';
        else errorMsg += 'पुनः प्रयास करें।';
        voiceStatusText.textContent = errorMsg;
        voiceStatusText.style.color = '#f44336';
        setTimeout(() => closeModal(voiceModal), 2000);
    };
} else {
    micBtn.disabled = true;
    micBtn.title = 'Voice not supported';
}

// ---------- Modal Helpers ----------
function openModal(modal) { modal.classList.remove('hidden'); }
function closeModal(modal) { modal.classList.add('hidden'); }

// ---------- Send Message (Text) ----------
async function sendMessage() {
    const query = questionInput.value.trim();
    if (!query) return;

    addMessage(query, 'user');
    questionInput.value = '';
    showTypingIndicator();

    try {
        const response = await fetch(`${API_URL}/ask-text?query=${encodeURIComponent(query)}`, {
            method: 'POST'
        });
        const data = await response.json();
        hideTypingIndicator();

        if (data.status === 'success') {
            addMessage(data.answer, 'bot');
            lastBotAnswer = data.answer;
            // Automatically speak the answer
            speakText(data.answer);
        } else {
            const errMsg = 'क्षमा करें, कुछ गलत हो गया। कृपया पुनः प्रयास करें।';
            addMessage(errMsg, 'bot');
            lastBotAnswer = errMsg;
            speakText(errMsg);
        }
    } catch (error) {
        console.error('Error:', error);
        hideTypingIndicator();
        const errMsg = 'नेटवर्क त्रुटि। कृपया अपना कनेक्शन जांचें।';
        addMessage(errMsg, 'bot');
        lastBotAnswer = errMsg;
        speakText(errMsg);
    }
}

// Add message to chat
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender} fade-in`;
    const messageBubble = document.createElement('div');
    messageBubble.className = 'message-bubble';
    const iconDiv = document.createElement('div');
    iconDiv.className = 'message-icon';
    iconDiv.textContent = sender === 'user' ? '👤' : '🌾';
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = text.replace(/\n/g, '<br>');
    messageBubble.appendChild(iconDiv);
    messageBubble.appendChild(contentDiv);
    messageDiv.appendChild(messageBubble);
    messagesDiv.appendChild(messageDiv);
    scrollToBottom();
}

function showTypingIndicator() {
    typingIndicator.classList.remove('hidden');
    scrollToBottom();
}
function hideTypingIndicator() { typingIndicator.classList.add('hidden'); }
function scrollToBottom() {
    document.querySelector('.messages-wrapper').scrollTop = document.querySelector('.messages-wrapper').scrollHeight;
}
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// ---------- Event Listeners ----------
// Mic button
micBtn.addEventListener('click', () => {
    if (!recognition) {
        alert('Voice input not supported in this browser');
        return;
    }
    openModal(voiceModal);
    voiceStatusText.textContent = '🎤 बोलिए... Speak now...';
    voiceStatusText.style.color = '#666';
    setTimeout(() => {
        if (recognition && !isListening) recognition.start();
    }, 500);
});

// Speaker button (manual replay)
speakerBtn.addEventListener('click', () => {
    if (!lastBotAnswer) {
        alert('कोई जवाब नहीं है। पहले कोई सवाल पूछें।');
        return;
    }
    // Speak the last answer without opening a modal (or you can open it – your choice)
    speakText(lastBotAnswer, true);
});

// Close modals
closeMicModal.addEventListener('click', () => closeModal(voiceModal));
cancelMicBtn.addEventListener('click', () => closeModal(voiceModal));
closeSpeakerModal.addEventListener('click', () => {
    if (currentUtterance) window.speechSynthesis.cancel();
    closeModal(speakerModal);
});
cancelSpeakerBtn.addEventListener('click', () => {
    if (currentUtterance) window.speechSynthesis.cancel();
    closeModal(speakerModal);
});

sendBtn.addEventListener('click', sendMessage);
questionInput.addEventListener('keypress', handleKeyPress);

// Backdrop clicks
voiceModal.addEventListener('click', (e) => { if (e.target === voiceModal) closeModal(voiceModal); });
speakerModal.addEventListener('click', (e) => { if (e.target === speakerModal) closeModal(speakerModal); });

// Initial focus
questionInput.focus();
scrollToBottom();

// Health check
async function healthCheck() {
    try {
        const response = await fetch(`${API_URL}/health`);
        if (response.ok) console.log('✅ KrishiBot API ready');
    } catch (error) {
        console.error('⚠️ API not responding');
        addMessage('⚠️ सर्वर कनेक्ट नहीं हो पाया। कृपया सुनिश्चित करें कि API चल रहा है।', 'bot');
    }
}
healthCheck();

// Preload voices
if ('speechSynthesis' in window) window.speechSynthesis.getVoices();