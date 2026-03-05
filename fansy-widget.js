/**
 * Виджет чата Fansy для сайта fancy-group.pro
 * Обычный режим: FansyWidget.init({ apiUrl: '...' }) — создаёт свою кнопку «Чат».
 * Режим «уже есть кнопка»: FansyWidget.init({ apiUrl: '...', attachTo: '#ваша-кнопка-чата' }) — открывает панель по клику на вашу кнопку.
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'fansy_session_id';
  var DEFAULT_API = '/chat';

  function getSessionId() {
    try {
      var id = sessionStorage.getItem(STORAGE_KEY);
      if (id) return id;
      id = 'fansy-' + Math.random().toString(36).slice(2) + '-' + Date.now();
      sessionStorage.setItem(STORAGE_KEY, id);
      return id;
    } catch (e) {
      return 'fansy-' + Date.now();
    }
  }

  window.FansyWidget = {
    config: {
      apiUrl: DEFAULT_API,
      title: 'Fansy',
      subtitle: 'Помогу с подбором сувениров',
      placeholder: 'Напишите сообщение...',
      sendLabel: 'Отправить',
      openLabel: 'Чат',
      errorMessage: 'Не удалось отправить. Попробуйте позже.',
    },

    init: function (options) {
      var self = this;
      if (options && options.apiUrl) self.config.apiUrl = options.apiUrl.replace(/\/+$/, '');
      if (options && options.title) self.config.title = options.title;
      if (options && options.subtitle) self.config.subtitle = options.subtitle;
      if (options && options.placeholder) self.config.placeholder = options.placeholder;
      if (options && options.sendLabel) self.config.sendLabel = options.sendLabel;
      if (options && options.openLabel) self.config.openLabel = options.openLabel;
      if (options && options.errorMessage) self.config.errorMessage = options.errorMessage;
      var attachTo = options && options.attachTo; // селектор существующей кнопки «Чат»

      var apiBase = self.config.apiUrl.replace(/\/chat\/?$/, '');
      var chatUrl = apiBase + (apiBase.endsWith('/') ? 'chat' : '/chat');

      var container = document.createElement('div');
      container.className = 'fansy-widget';
      if (attachTo) {
        container.classList.add('fansy-widget-attached');
      }
      container.innerHTML =
        (attachTo ? '' : ('<div class="fansy-widget-button" role="button" aria-label="' +
        self.config.openLabel +
        '">' +
        '<span class="fansy-widget-button-text">' +
        self.config.openLabel +
        '</span></div>')) +
        '<div class="fansy-widget-panel" aria-hidden="true">' +
        '<div class="fansy-widget-header">' +
        '<span class="fansy-widget-title">' +
        self.config.title +
        '</span>' +
        '<span class="fansy-widget-subtitle">' +
        self.config.subtitle +
        '</span>' +
        '<button type="button" class="fansy-widget-close" aria-label="Закрыть">&times;</button>' +
        '</div>' +
        '<div class="fansy-widget-messages"></div>' +
        '<div class="fansy-widget-form">' +
        '<input type="text" class="fansy-widget-input" placeholder="' +
        self.config.placeholder +
        '" autocomplete="off">' +
        '<button type="button" class="fansy-widget-send">' +
        self.config.sendLabel +
        '</button>' +
        '</div>' +
        '</div>';

      var style = document.createElement('style');
      style.textContent =
        '.fansy-widget{position:fixed;bottom:20px;right:20px;z-index:99999;font-family:system-ui,-apple-system,sans-serif;font-size:14px;}' +
        '.fansy-widget-attached .fansy-widget-panel{bottom:20px;}' +
        '.fansy-widget-button{width:56px;height:56px;border-radius:50%;background:#1a5f4a;color:#fff;display:flex;align-items:center;justify-content:center;cursor:pointer;box-shadow:0 4px 12px rgba(0,0,0,.2);}' +
        '.fansy-widget-button-text{display:none;}@media(min-width:360px){.fansy-widget-button{width:auto;padding:0 18px;border-radius:28px;}.fansy-widget-button-text{display:inline;}}' +
        '.fansy-widget-panel{display:none;position:absolute;bottom:70px;right:0;width:360px;max-width:calc(100vw - 40px);height:480px;max-height:70vh;background:#fff;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,.15);flex-direction:column;overflow:hidden;}' +
        '.fansy-widget-panel.open{display:flex;}' +
        '.fansy-widget-header{background:#1a5f4a;color:#fff;padding:14px 16px;display:flex;flex-wrap:wrap;align-items:center;gap:8px;}' +
        '.fansy-widget-title{font-weight:700;} .fansy-widget-subtitle{font-size:12px;opacity:.9;}' +
        '.fansy-widget-close{margin-left:auto;background:0;border:0;color:inherit;font-size:24px;cursor:pointer;line-height:1;padding:0 4px;}' +
        '.fansy-widget-messages{flex:1;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:10px;}' +
        '.fansy-widget-msg{max-width:85%;padding:10px 12px;border-radius:12px;line-height:1.4;}' +
        '.fansy-widget-msg.user{align-self:flex-end;background:#e8f5e9;}' +
        '.fansy-widget-msg.bot{align-self:flex-start;background:#f5f5f5;}' +
        '.fansy-widget-msg.error{background:#ffebee;}' +
        '.fansy-widget-form{display:flex;gap:8px;padding:12px;border-top:1px solid #eee;}' +
        '.fansy-widget-input{flex:1;padding:10px 12px;border:1px solid #ccc;border-radius:8px;outline:0;}' +
        '.fansy-widget-send{padding:10px 16px;background:#1a5f4a;color:#fff;border:0;border-radius:8px;cursor:pointer;}' +
        '.fansy-widget-send:disabled{opacity:.6;cursor:not-allowed;}';
      document.head.appendChild(style);

      document.body.appendChild(container);

      var btn = container.querySelector('.fansy-widget-button');
      var panel = container.querySelector('.fansy-widget-panel');
      var closeBtn = container.querySelector('.fansy-widget-close');
      var messagesEl = container.querySelector('.fansy-widget-messages');
      var inputEl = container.querySelector('.fansy-widget-input');
      var sendBtn = container.querySelector('.fansy-widget-send');

      function openPanel() {
        panel.classList.add('open');
        panel.setAttribute('aria-hidden', 'false');
        if (inputEl) inputEl.focus();
      }
      function closePanel() {
        panel.classList.remove('open');
        panel.setAttribute('aria-hidden', 'true');
      }
      function togglePanel() {
        panel.classList.toggle('open');
        panel.setAttribute('aria-hidden', panel.classList.contains('open') ? 'false' : 'true');
        if (panel.classList.contains('open')) inputEl.focus();
      }

      function addMessage(text, role, isError) {
        var div = document.createElement('div');
        div.className = 'fansy-widget-msg ' + (role === 'user' ? 'user' : isError ? 'error' : 'bot');
        div.textContent = text;
        messagesEl.appendChild(div);
        messagesEl.scrollTop = messagesEl.scrollHeight;
      }

      function setLoading(loading) {
        sendBtn.disabled = loading;
        inputEl.disabled = loading;
      }

      function send() {
        var text = inputEl.value.trim();
        if (!text) return;
        inputEl.value = '';
        addMessage(text, 'user');
        setLoading(true);

        var sessionId = getSessionId();
        fetch(chatUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text, session_id: sessionId }),
        })
          .then(function (res) {
            return res.json().then(function (data) {
              if (!res.ok) throw new Error(data.detail || self.config.errorMessage);
              return data;
            });
          })
          .then(function (data) {
            addMessage(data.reply || '', 'bot');
          })
          .catch(function () {
            addMessage(self.config.errorMessage, 'bot', true);
          })
          .finally(function () {
            setLoading(false);
          });
      }

      if (attachTo) {
        var existingBtn = document.querySelector(attachTo);
        if (existingBtn) {
          existingBtn.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            togglePanel();
          });
        }
      } else if (btn) {
        btn.addEventListener('click', togglePanel);
      }
      closeBtn.addEventListener('click', closePanel);
      sendBtn.addEventListener('click', send);
      inputEl.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') send();
      });
    },
  };
})();
