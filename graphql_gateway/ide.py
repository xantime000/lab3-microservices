# -*- coding: utf-8 -*-
"""
Встроенный автономный GraphQL Playground / IDE.
Работает 100% локально и мгновенно, без зависимости от внешних CDN (unpkg.com / jsdelivr),
что исключает зависание на 'Loading...' при закрытом или медленном доступе в интернет.
"""

def get_ide_html(default_query: str = None) -> str:
    if not default_query:
        default_query = """query GetUserOrders($userId: ID!) {
  ordersByUserId(userId: $userId) {
    id
    createdAt
    items {
      quantity
      product {
        id
        name
        price
      }
    }
  }
}"""

    default_variables = '{\n  "userId": "123"\n}'

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GraphQL Gateway Playground — Strawberry & DataLoader</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2280%22>⚡</text></svg>">
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    :root {{
      --bg-main: #0d1117;
      --bg-panel: #161b22;
      --bg-panel-header: #21262d;
      --border: #30363d;
      --text-main: #c9d1d9;
      --text-muted: #8b949e;
      --accent: #58a6ff;
      --accent-hover: #79c0ff;
      --success: #238636;
      --success-hover: #2ea043;
      --danger: #da3633;
      --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
    }}
    body {{
      background: var(--bg-main);
      color: var(--text-main);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }}
    /* Header */
    header {{
      background: var(--bg-panel);
      border-bottom: 1px solid var(--border);
      padding: 10px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .brand-icon {{
      background: #e10098;
      color: white;
      width: 28px;
      height: 28px;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      font-size: 15px;
    }}
    .brand-title {{
      font-size: 15px;
      font-weight: 600;
      color: #fff;
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 3px 8px;
      border-radius: 12px;
      font-size: 11px;
      font-weight: 500;
    }}
    .badge-endpoint {{
      background: #1f6feb26;
      color: #58a6ff;
      border: 1px solid #1f6feb66;
      font-family: var(--font-mono);
    }}
    .badge-dataloader {{
      background: #23863626;
      color: #3fb950;
      border: 1px solid #23863666;
    }}
    .header-actions {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    button {{
      cursor: pointer;
      border: 1px solid var(--border);
      background: var(--bg-panel-header);
      color: var(--text-main);
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 500;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
    }}
    button:hover {{
      background: #30363d;
      border-color: #8b949e;
    }}
    button.btn-run {{
      background: var(--success);
      border-color: rgba(240, 246, 252, 0.1);
      color: #ffffff;
      font-weight: 600;
    }}
    button.btn-run:hover {{
      background: var(--success-hover);
    }}
    button.btn-active {{
      background: #1f6feb;
      border-color: #58a6ff;
      color: #fff;
    }}
    /* Main Layout */
    .workspace {{
      flex: 1;
      display: flex;
      overflow: hidden;
    }}
    .panel {{
      flex: 1;
      display: flex;
      flex-direction: column;
      border-right: 1px solid var(--border);
      overflow: hidden;
      min-width: 300px;
    }}
    .panel:last-child {{
      border-right: none;
    }}
    .panel-header {{
      background: var(--bg-panel-header);
      padding: 8px 14px;
      font-size: 12px;
      font-weight: 600;
      color: var(--text-muted);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .panel-header .title {{
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--text-main);
    }}
    .status-badge {{
      font-family: var(--font-mono);
      font-size: 11px;
      padding: 2px 6px;
      border-radius: 4px;
    }}
    .status-200 {{
      background: #23863633;
      color: #3fb950;
      border: 1px solid #238636;
    }}
    .status-err {{
      background: #da363333;
      color: #f85149;
      border: 1px solid #da3633;
    }}
    /* Editor */
    .editor-container {{
      flex: 1;
      position: relative;
      display: flex;
      flex-direction: column;
    }}
    textarea.code-editor {{
      flex: 1;
      width: 100%;
      background: var(--bg-main);
      color: #e6edf3;
      border: none;
      outline: none;
      padding: 14px 16px;
      font-family: var(--font-mono);
      font-size: 13.5px;
      line-height: 1.5;
      resize: none;
      tab-size: 2;
    }}
    /* Variables drawer */
    .variables-drawer {{
      border-top: 1px solid var(--border);
      background: var(--bg-panel);
      display: flex;
      flex-direction: column;
      height: 140px;
      transition: height 0.2s ease;
    }}
    .variables-drawer.collapsed {{
      height: 32px;
    }}
    .variables-header {{
      background: var(--bg-panel-header);
      padding: 6px 14px;
      font-size: 11px;
      font-weight: 600;
      color: var(--text-muted);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      user-select: none;
    }}
    .variables-header:hover {{
      color: var(--text-main);
    }}
    textarea.var-editor {{
      flex: 1;
      background: var(--bg-main);
      color: #e6edf3;
      border: none;
      outline: none;
      padding: 8px 14px;
      font-family: var(--font-mono);
      font-size: 12.5px;
      line-height: 1.4;
      resize: none;
    }}
    /* Response viewer */
    .response-container {{
      flex: 1;
      overflow: auto;
      background: var(--bg-main);
      padding: 14px 16px;
    }}
    pre.response-output {{
      margin: 0;
      font-family: var(--font-mono);
      font-size: 13px;
      line-height: 1.5;
      color: #79c0ff;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    /* Documentation Sidebar */
    .docs-sidebar {{
      width: 380px;
      background: var(--bg-panel);
      border-left: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      transition: margin-right 0.2s ease;
    }}
    .docs-sidebar.hidden {{
      margin-right: -380px;
    }}
    .docs-content {{
      flex: 1;
      overflow-y: auto;
      padding: 16px;
    }}
    .doc-section {{
      margin-bottom: 20px;
    }}
    .doc-section h3 {{
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-muted);
      margin-bottom: 10px;
      padding-bottom: 4px;
      border-bottom: 1px solid var(--border);
    }}
    .type-card {{
      background: var(--bg-main);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 12px;
      margin-bottom: 10px;
    }}
    .type-name {{
      font-family: var(--font-mono);
      font-size: 14px;
      font-weight: 600;
      color: #ff7b72;
      margin-bottom: 4px;
    }}
    .type-desc {{
      font-size: 12px;
      color: var(--text-muted);
      margin-bottom: 8px;
    }}
    .field-row {{
      font-family: var(--font-mono);
      font-size: 12px;
      padding: 4px 0;
      border-top: 1px dashed #21262d;
    }}
    .field-name {{
      color: #79c0ff;
    }}
    .field-type {{
      color: #d2a8ff;
    }}
    .field-desc {{
      font-family: -apple-system, sans-serif;
      font-size: 11px;
      color: #8b949e;
      margin-top: 2px;
      padding-left: 8px;
    }}
    .callout {{
      background: #1f6feb15;
      border: 1px solid #1f6feb55;
      border-radius: 6px;
      padding: 10px;
      font-size: 12px;
      line-height: 1.4;
      color: #79c0ff;
      margin-bottom: 14px;
    }}
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <div class="brand-icon">G</div>
      <div>
        <div class="brand-title">GraphQL Gateway Playground</div>
      </div>
      <span class="badge badge-endpoint">POST /graphql</span>
      <span class="badge badge-dataloader">DataLoader: N+1 Solved</span>
    </div>

    <div class="header-actions">
      <button class="btn-run" id="btn-run" title="Выполнить запрос (Ctrl+Enter)">
        <span>▶</span> Выполнить
      </button>
      <button id="btn-preset-orders" title="Загрузить запрос из ТЗ">
        Запрос из ТЗ
      </button>
      <button id="btn-preset-intro" title="Интроспекция схемы">
        Интроспекция
      </button>
      <button id="btn-toggle-docs" class="btn-active" title="Открыть документацию схемы">
        Docs (Схема)
      </button>
    </div>
  </header>

  <div class="workspace">
    <!-- Левая панель: Редактор запроса -->
    <div class="panel">
      <div class="panel-header">
        <div class="title">
          <span>GraphQL Query</span>
          <span style="font-size: 11px; color: var(--text-muted);">(Ctrl+Enter для запуска)</span>
        </div>
      </div>

      <div class="editor-container">
        <textarea id="query-editor" class="code-editor" spellcheck="false">{default_query}</textarea>
        
        <div class="variables-drawer" id="var-drawer">
          <div class="variables-header" id="var-header">
            <span>Query Variables (JSON)</span>
            <span id="var-toggle-icon">▼</span>
          </div>
          <textarea id="var-editor" class="var-editor" spellcheck="false">{default_variables}</textarea>
        </div>
      </div>
    </div>

    <!-- Правая панель: Результат JSON -->
    <div class="panel">
      <div class="panel-header">
        <div class="title">
          <span>Ответ сервера (JSON)</span>
          <span id="status-pill" class="status-badge status-200">200 OK</span>
          <span id="time-pill" style="font-family: var(--font-mono); font-size: 11px; color: var(--text-muted);">0 ms</span>
        </div>
        <button id="btn-copy" style="padding: 2px 8px; font-size: 11px;">Копировать</button>
      </div>

      <div class="response-container">
        <pre id="response-output" class="response-output">Выполняется запрос к шлюзу...</pre>
      </div>
    </div>

    <!-- Боковая панель документации (Docs) -->
    <div class="docs-sidebar" id="docs-sidebar">
      <div class="panel-header">
        <span class="title">Документация GraphQL SDL</span>
        <span style="font-size: 11px; color: var(--text-muted);">Интроспекция включена</span>
      </div>

      <div class="docs-content">
        <div class="callout">
          <strong>Паттерн DataLoader активен:</strong> При вызове <code>ordersByUserId</code> резолвер позиций батчит все ID товаров и отправляет <strong>ровно один</strong> запрос к Catalog Service <code>GET /api/catalog/products?ids=...</code>, устраняя проблему N+1.
        </div>

        <div class="doc-section">
          <h3>Точка входа (Query)</h3>
          <div class="type-card">
            <div class="type-name">Query</div>
            <div class="field-row">
              <span class="field-name">ordersByUserId</span>(<span class="field-name">userId</span>: <span class="field-type">ID!</span>): <span class="field-type">[Order!]!</span>
              <div class="field-desc">Получить список всех заказов конкретного пользователя по его userId</div>
            </div>
          </div>
        </div>

        <div class="doc-section">
          <h3>Сущности схемы (Types)</h3>

          <div class="type-card">
            <div class="type-name">Order</div>
            <div class="type-desc">Сущность заказа пользователя</div>
            <div class="field-row"><span class="field-name">id</span>: <span class="field-type">ID!</span><div class="field-desc">Уникальный идентификатор заказа</div></div>
            <div class="field-row"><span class="field-name">userId</span>: <span class="field-type">ID!</span><div class="field-desc">Идентификатор пользователя, оформившего заказ</div></div>
            <div class="field-row"><span class="field-name">createdAt</span>: <span class="field-type">String!</span><div class="field-desc">Дата и время создания заказа в формате ISO 8601</div></div>
            <div class="field-row"><span class="field-name">items</span>: <span class="field-type">[OrderItem!]!</span><div class="field-desc">Список позиций (товаров) в заказе</div></div>
          </div>

          <div class="type-card">
            <div class="type-name">OrderItem</div>
            <div class="type-desc">Элемент заказа, связывающий товар и его количество</div>
            <div class="field-row"><span class="field-name">quantity</span>: <span class="field-type">Int!</span><div class="field-desc">Количество единиц товара в заказе</div></div>
            <div class="field-row"><span class="field-name">product</span>: <span class="field-type">Product!</span><div class="field-desc">Информация о товаре, загружаемая через DataLoader без проблемы N+1</div></div>
          </div>

          <div class="type-card">
            <div class="type-name">Product</div>
            <div class="type-desc">Сущность товара из сервиса каталога</div>
            <div class="field-row"><span class="field-name">id</span>: <span class="field-type">ID!</span><div class="field-desc">Уникальный идентификатор товара</div></div>
            <div class="field-row"><span class="field-name">name</span>: <span class="field-type">String!</span><div class="field-desc">Наименование товара</div></div>
            <div class="field-row"><span class="field-name">price</span>: <span class="field-type">Float!</span><div class="field-desc">Стоимость товара в рублях</div></div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    const queryEditor = document.getElementById("query-editor");
    const varEditor = document.getElementById("var-editor");
    const responseOutput = document.getElementById("response-output");
    const statusPill = document.getElementById("status-pill");
    const timePill = document.getElementById("time-pill");
    const btnRun = document.getElementById("btn-run");
    const btnCopy = document.getElementById("btn-copy");
    const btnPresetOrders = document.getElementById("btn-preset-orders");
    const btnPresetIntro = document.getElementById("btn-preset-intro");
    const btnToggleDocs = document.getElementById("btn-toggle-docs");
    const docsSidebar = document.getElementById("docs-sidebar");
    const varHeader = document.getElementById("var-header");
    const varDrawer = document.getElementById("var-drawer");
    const varToggleIcon = document.getElementById("var-toggle-icon");

    // Поддержка табуляции в текстовых полях
    function enableTabIndent(textarea) {{
      textarea.addEventListener("keydown", function(e) {{
        if (e.key === "Tab") {{
          e.preventDefault();
          const start = this.selectionStart;
          const end = this.selectionEnd;
          this.value = this.value.substring(0, start) + "  " + this.value.substring(end);
          this.selectionStart = this.selectionEnd = start + 2;
        }} else if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {{
          e.preventDefault();
          executeQuery();
        }}
      }});
    }}
    enableTabIndent(queryEditor);
    enableTabIndent(varEditor);

    // Сворачивание панели переменных
    varHeader.addEventListener("click", () => {{
      varDrawer.classList.toggle("collapsed");
      varToggleIcon.textContent = varDrawer.classList.contains("collapsed") ? "▲" : "▼";
    }});

    // Переключение боковой панели документации
    btnToggleDocs.addEventListener("click", () => {{
      docsSidebar.classList.toggle("hidden");
      btnToggleDocs.classList.toggle("btn-active", !docsSidebar.classList.contains("hidden"));
    }});

    // Подсветка синтаксиса JSON
    function syntaxHighlightJson(jsonObj) {{
      const jsonStr = JSON.stringify(jsonObj, null, 2);
      return jsonStr.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
        .replace(/("(\\\\u[a-zA-Z0-9]{{4}}|\\\\[^u]|[^\\\\"])*"(\\s*:)?|\\b(true|false|null)\\b|-?\\d+(?:\\.\\d*)?(?:[eE][+\\-]?\\d+)?)/g, function(match) {{
          let cls = "color: #79c0ff;";
          if (/^"/.test(match)) {{
            if (/:$/.test(match)) {{
              cls = "color: #ff7b72; font-weight: 600;";
            }} else {{
              cls = "color: #a5d6ff;";
            }}
          }} else if (/true|false/.test(match)) {{
            cls = "color: #56d364;";
          }} else if (/null/.test(match)) {{
            cls = "color: #ffa657;";
          }}
          return '<span style="' + cls + '">' + match + "</span>";
        }});
    }}

    // Выполнение GraphQL-запроса
    async function executeQuery() {{
      const query = queryEditor.value.trim();
      let variables = {{}};
      const varText = varEditor.value.trim();

      if (varText) {{
        try {{
          variables = JSON.parse(varText);
        }} catch (err) {{
          statusPill.className = "status-badge status-err";
          statusPill.textContent = "JSON Error";
          responseOutput.innerHTML = '<span style="color: #f85149;">Ошибка синтаксиса в Query Variables (невалидный JSON):</span>\\n' + err.message;
          return;
        }}
      }}

      statusPill.className = "status-badge";
      statusPill.textContent = "Loading...";
      btnRun.disabled = true;

      // Нормализация пути к /graphql независимо от того, открыт ли URL со слэшем на конце
      let endpoint = window.location.pathname;
      if (endpoint.endsWith("/")) {{
        endpoint = endpoint.slice(0, -1);
      }}
      if (!endpoint.endsWith("/graphql")) {{
        endpoint = "/graphql";
      }}

      const startTime = performance.now();

      try {{
        const res = await fetch(endpoint, {{
          method: "POST",
          headers: {{
            "Content-Type": "application/json",
            "Accept": "application/json"
          }},
          body: JSON.stringify({{ query, variables }})
        }});

        const duration = Math.round(performance.now() - startTime);
        timePill.textContent = duration + " ms";

        const data = await res.json();
        btnRun.disabled = false;

        if (res.ok && !data.errors) {{
          statusPill.className = "status-badge status-200";
          statusPill.textContent = res.status + " OK";
        }} else {{
          statusPill.className = "status-badge status-err";
          statusPill.textContent = res.status + (data.errors ? " Errors" : " Error");
        }}

        responseOutput.innerHTML = syntaxHighlightJson(data);

      }} catch (err) {{
        btnRun.disabled = false;
        const duration = Math.round(performance.now() - startTime);
        timePill.textContent = duration + " ms";
        statusPill.className = "status-badge status-err";
        statusPill.textContent = "Network Error";
        responseOutput.innerHTML = '<span style="color: #f85149;">Ошибка выполнения сетевого запроса:</span>\\n' + err.message;
      }}
    }}

    btnRun.addEventListener("click", executeQuery);

    // Копирование ответа
    btnCopy.addEventListener("click", () => {{
      const text = responseOutput.innerText;
      navigator.clipboard.writeText(text).then(() => {{
        const orig = btnCopy.textContent;
        btnCopy.textContent = "Скопировано!";
        setTimeout(() => btnCopy.textContent = orig, 1500);
      }});
    }});

    // Пресеты запросов
    btnPresetOrders.addEventListener("click", () => {{
      queryEditor.value = `query GetUserOrders($userId: ID!) {{
  ordersByUserId(userId: $userId) {{
    id
    createdAt
    items {{
      quantity
      product {{
        id
        name
        price
      }}
    }}
  }}
}}`;
      varEditor.value = `{{\\n  "userId": "123"\\n}}`;
      executeQuery();
    }});

    btnPresetIntro.addEventListener("click", () => {{
      queryEditor.value = `query IntrospectionQuery {{
  __schema {{
    types {{
      name
      description
      fields {{
        name
        description
      }}
    }}
  }}
}}`;
      varEditor.value = "{{}}";
      executeQuery();
    }});

    // Автоматический запуск при первой загрузке страницы
    window.addEventListener("DOMContentLoaded", () => {{
      executeQuery();
    }});
  </script>
</body>
</html>
"""
