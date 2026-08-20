# meu_projeto_levi_AI
# 🏛️ Levi AI — Sistema Preditivo Antifraude & Governança de Crédito

Solução analítica de esteira bancária voltada para avaliação de risco transacional, classificação antifraude via **Machine Learning (XGBoost)**, emissão automatizada de laudos em PDF timbrado e auditoria conversacional especializada em conformidade com as diretrizes do **Banco Central do Brasil (BACEN)**.

---

## 📌 Origem e Linhagem do Projeto

Este repositório representa o estágio corporativo e aprimorado de uma esteira analítica desenvolvida em ciclos evolutivos:

1. **Base Educacional:** Desenvolvido originalmente no laboratório [dio-lab-bia-do-futuro](https://github.com/digitalinnovationone/dio-lab-bia-do-futuro) da Digital Innovation One (DIO).
2. **Fork Intermediário:** Estruturado e adaptado em [dio-lab-levi-AI](https://github.com/engsoftweduardooeiras/dio-lab-levi-AI).
3. **Versão Final de Produção:** Aprimorado integralmente em [Projeto_levi_AI_deteccao_de_fraudes](https://github.com/engsoftweduardooeiras/Projeto_levi_AI_deteccao_de_fraudes), implementando governança regulatória, motor híbrido de contingência analítica, visualizador PDF embutido e mesa de chat com grounding normativo nacional.

---

## ⚙️ Arquitetura do Sistema

* **Motor Preditivo (XGBoost):** Classificação probabilística em Zonas de Risco (*Verde*, *Amarela* e *Vermelha*) com disparo automatizado de alertas de segurança para a diretoria.
* **Laudos em PDF Timbrado (ReportLab):** Geração dinâmica de pareceres técnicos com trilha de auditoria (XAI), identificador de operador e visualizador em tela.
* **Auditoria Massiva & Exportação (OpenPyXL / Pandas):** Processamento em lote de intervalos de transações com parametrização dinâmica de rede, autenticação, faixas de valores e geração de planilhas formatadas (.xlsx).
* **Base Regulatória BACEN / LGPD:** Grounding local de normativas federais (Resolução BCB nº 147/2021, Resolução CMN nº 4.949/2021, Circular BACEN nº 3.978/2020 e Lei nº 13.709/2018).
* **Mesa Consultiva (Chat com Analista Levi):** Assistente conversacional multi-turno via **Google GenAI SDK**, com controle estrito de persona corporativa, barreira contra dados sensíveis e rejeição de solicitações fora do domínio de crédito.

---

## 🖥️ Módulos da Interface (Streamlit)

| Aba | Funcionalidade | Tecnologia |
| :--- | :--- | :--- |
| **1. 📊 Auditoria de Crédito** | Inferência de risco, exibição de XAI e emissão de laudo timbrado | XGBoost + ReportLab |
| **2. ➕ Novos Dados** | Cadastro e indexação dinâmica de proponentes em disco | JSON / Pandas |
| **3. 🔒 Painel de Logs** | Visualização em tempo real dos PDFs gerados | Base64 PDF Viewer |
| **4. 💬 Chat Levi** | Consulta e deliberação técnica com grounding regulatório BACEN | Google Gemini 2.0 Flash |
| **5. 📑 Auditoria em Lote** | Análise massiva por intervalos/upload com parametrização completa e exportação | Pandas + OpenPyXL |

---

## 🚀 Como Executar Localmente

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/engsoftweduardooeiras/Projeto_levi_AI_deteccao_de_fraudes.git](https://github.com/engsoftweduardooeiras/Projeto_levi_AI_deteccao_de_fraudes.git)
   cd Projeto_levi_AI_deteccao_de_fraudes

* **Instale as dependências:**
**Bash**
pip install streamlit pandas joblib xgboost reportlab google-genai openpyxl

* **Configure as credenciais (opcional para IA externa):**
**Crie o arquivo**``.streamlit/secrets.toml``:
*Ini, TOML*
GEMINI_API_KEY = "SUA_CHAVE_AQUI"

* **Inicie a aplicação:**
**Bash**
streamlit run app.py

🛠️ **Tecnologias Utilizadas**
* **Linguagem:** Python 3.12+
* **Interface:** Streamlit
* **Machine Learning:** XGBoost & Scikit-Learn & Joblib
* **Documentação & Relatórios:** ReportLab
* **LLM & Governança:** Google GenAI SDK (Gemini 2.0 Flash) & Grounding em Normativas BACEN
* **Manipulacao_e_Exportacao:** Pandas & OpenPyXL
