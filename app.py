import streamlit as st
import pandas as pd
import json
import joblib
import os
import base64
from datetime import datetime

# Importações oficiais da SDK atualizada do Google Gemini
from google import genai
from google.genai import types

# Importações do ReportLab para confecção de laudos em papel timbrado
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ==============================================================================
# 1. CARREGAMENTO DOS COMPONENTES E SISTEMA DE DADOS (BASE DE CONHECIMENTO)
# ==============================================================================
def carregar_sistema_producao():
    """
    Carrega o modelo do XGBoost e arquivos JSON com tolerância estrita a falhas.
    """
    caminho_modelo = 'modelos/pipeline_antifraude_calibrado.joblib'
    os.makedirs('data', exist_ok=True)
    os.makedirs('modelos', exist_ok=True)
   
    # 1. Proteção do modelo preditivo
    if os.path.exists(caminho_modelo):
        modelo = joblib.load(caminho_modelo)
    else:
        st.sidebar.warning("⚠️ Arquivo .joblib não encontrado. Usando modelo simulado.")
        class ModeloSimulado:
            def predict_proba(self, X):
                import numpy as np
                valor = float(X["Amount"].iloc[0]) if "Amount" in X.columns else 100.0
                prob_fraude = 0.95 if valor > 5000 else 0.05
                return np.array([[1 - prob_fraude, prob_fraude]])
        modelo = ModeloSimulado()
   
    # 2. Proteção do JSON de perfis
    perfil_json = {}
    if os.path.exists('data/perfil_investidor.json'):
        try:
            with open('data/perfil_investidor.json', 'r', encoding='utf-8') as f:
                conteudo = f.read().strip()
                if conteudo:
                    perfil_json = json.loads(conteudo)
        except Exception:
            perfil_json = {}
           
    # 3. Proteção do JSON de produtos
    produtos_json = []
    if os.path.exists('data/produtos_financeiros.json'):
        try:
            with open('data/produtos_financeiros.json', 'r', encoding='utf-8') as f:
                conteudo = f.read().strip()
                if conteudo:
                    produtos_json = json.loads(conteudo)
        except Exception:
            produtos_json = []
           
    if not produtos_json:
        produtos_json = [
            {"nome_produto": "Crédito Pessoal Automático", "taxa_juros": "2.99% a.m.", "limite_maximo": 15000},
            {"nome_produto": "Consignado Privado", "taxa_juros": "1.89% a.m.", "limite_maximo": 50000}
        ]
       
    # 4. Carregamento do histórico CSV
    if os.path.exists('data/historico_atendimento.csv'):
        try:
            df_historico = pd.read_csv('data/historico_atendimento.csv')
        except Exception:
            df_historico = pd.DataFrame(columns=['id_cliente', 'data', 'categoria', 'status_resolucao'])
    else:
        df_historico = pd.DataFrame(columns=['id_cliente', 'data', 'categoria', 'status_resolucao'])
   
    return modelo, perfil_json, produtos_json, df_historico

def carregar_normativas_bacen():
    caminho = "data/normativas_bacen.json"
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"resolucoes_bcb": []}

modelo_calibrado, perfil_dados, produtos_dados, df_historico = carregar_sistema_producao()
normativas_bacen = carregar_normativas_bacen()

# ==============================================================================
# 2. SISTEMA DE AUTENTICAÇÃO E CONTROLE DE SESSÃO OPERACIONAL
# ==============================================================================
st.set_page_config(page_title="Levi - Analista Consultivo de Crédito", layout="wide")

if "historico_chat" not in st.session_state:
    st.session_state["historico_chat"] = [
        {"role": "assistant", "content": "Olá, Operador. Sou o Levi, seu consultor sênior de crédito e conformidade regulatória BACEN. Como posso auxiliar na análise desta ou de outras operações?"}
    ]

if "ultimo_contexto_auditoria" not in st.session_state:
    st.session_state["ultimo_contexto_auditoria"] = "Nenhuma auditoria executada na sessão atual."

if "usuario_ativo" not in st.session_state:
    st.session_state["usuario_ativo"] = None

# Bloqueio de segurança: Se nenhum operador estiver logado
if st.session_state["usuario_ativo"] is None:
    st.title("🏛️ Autenticação Institucional - Plataforma Levi")
    st.caption("Insira suas credenciais corporativas para habilitar os módulos de crédito.")
   
    with st.form("form_login"):
        nome_usuario = st.text_input("Nome do Operador ou Matrícula (Ex: Ana Silva - M-402):")
        senha_simples = st.text_input("Senha de Acesso:", type="password")
        botao_entrar = st.form_submit_button("Habilitar Chaves de Consulta")
       
        if botao_entrar:
            if nome_usuario.strip() == "":
                st.error("Identificação inválida. O campo do operador não pode ser enviado vazio.")
            else:
                st.session_state["usuario_ativo"] = nome_usuario.strip()
                st.rerun()
    st.stop()

# Painel de controle de sessão no menu lateral
st.sidebar.markdown(f"👤 **Operador Ativo:** `{st.session_state['usuario_ativo']}`")
if st.sidebar.button("Encerrar Sessão (Logout)"):
    st.session_state["usuario_ativo"] = None
    st.rerun()

# ==============================================================================
# 3. ESTILIZAÇÃO E IDENTIDADE VISUAL PREMIUM VIA CSS
# ==============================================================================
estilo_premium_levi = """
<meta name="google" content="notranslate">
<meta name="googlebot" content="notranslate">
<style translate="no">
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
   
    html, body, [class*="css"], [data-testid="stAppViewContainer"], div {
        font-family: 'Inter', sans-serif !important;
        translate: no !important;
    }
   
    code, pre, .stCodeBlock {
        font-family: 'JetBrains Mono', monospace !important;
        background-color: #6F553F !important; color: #D2C4AE !important; border: 1px solid #D4AF37 !important;
    }
    button[data-baseweb="tab"] {
        color: #A99C91 !important; background-color: #1A1D24 !important;
        font-weight: 600 !important; padding: 10px 20px !important; margin-right: 4px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #D4AF37 !important; background-color: #0A192F !important; border-top: 2px solid #D4AF37 !important;
    }
   
    div.stButton > button {
        background-color: #0A192F !important; color: #D4AF37 !important; border: 1px solid #D4AF37 !important;
        font-weight: 700 !important; border-radius: 6px !important; padding: 12px 24px !important; width: 100% !important;
    }
    div.stButton > button:hover { background-color: #D4AF37 !important; color: #0B0C10 !important; }
    .zona-verde-box { background-color: #4E6952 !important; color: #D2C4AE !important; padding: 15px; border-radius: 6px; margin-bottom: 15px; }
    .zona-amarela-box { background-color: #C5A059 !important; color: #0B0C10 !important; padding: 15px; border-radius: 6px; margin-bottom: 15px; }
    .zona-vermelha-box { background-color: #8F5E4E !important; color: #D2C4AE !important; padding: 15px; border-radius: 6px; margin-bottom: 15px; }
</style>
"""
st.markdown(estilo_premium_levi, unsafe_allow_html=True)

# ==============================================================================
# 4. ENGENHARIA DE PROMPT INTEGRADA AO GOOGLE GEMINI / SABIÁ GROUNDING
# ==============================================================================
def chamar_agente_levi(contexto_operacional, pergunta_usuario):
    """
    Emite parecer consultivo via Google GenAI SDK com contingência determinística.
    """
    api_key_gemini = st.secrets.get("GEMINI_API_KEY", "")
   
    prompt_completo = f"""Você é o Levi, um analista financeiro sênior eloquente, altamente consultivo e formal.
Sua missão é emitir pareceres de viabilidade de crédito baseando-se estritamente na ESTRUTURA DE PROCESSAMENTO DO CÓDIGO fornecida e nas normas do BACEN.
Como profundo conhecedor das regras do Banco Central do Brasil, use terminologias corporativas adequadas.

REGRAS CRÍTICAS DE SEGURANÇA:
- ZONA VERDE: Aprove proativamente e indique o melhor produto mapeado no portfólio.
- ZONA AMARELA: Retenha a operação para checagem complementar de MFA ou análise humana.
- ZONA VERMELHA: Recuse sumariamente devido a riscos cibernéticos ou de fraude. Proibido aprovar crédito.

=== ESTRUTURA DE PROCESSAMENTO DO CÓDIGO DE ANÁLISE ===
{contexto_operacional}

=== SOLICITAÇÃO / PERGUNTA ===
{pergunta_usuario}

Parecer Analítico Formal do Agente Levi:"""

    if api_key_gemini:
        try:
            client = genai.Client(api_key=api_key_gemini)
            for modelo in ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]:
                try:
                    resposta = client.models.generate_content(
                        model=modelo,
                        contents=prompt_completo
                    )
                    if resposta and resposta.text:
                        return resposta.text
                except Exception:
                    continue
        except Exception:
            pass

    # Motor de Contingência Analítica Local
    parecer_contingencia = [
        "### PARECER TÉCNICO DE ADMISSIBILIDADE E GOVERNANÇA DE CRÉDITO",
        "**Analista Consultivo Sênior:** Levi AI | **Marco Regulatório:** Resoluções BACEN / Compliance",
        "\n**1. DIAGNÓSTICO MATRICIAL DE RISCO:**"
    ]
   
    if "VERMELHA" in contexto_operacional:
        parecer_contingencia.extend([
            "- **Veredito:** INDEFERIMENTO TÉCNICO SUMÁRIO.",
            "- **Fundamentação:** Operação enquadrada em ZONA VERMELHA com probabilidade crítica de fraude. Identificou-se anomalia nos padrões transacionais e risco elevado no score de rede.",
            "- **Ação Mandatória:** Bloqueio cautelar preventivo (conforme Res. BCB nº 147/2021) e comunicação aos canais de compliance (Circ. BACEN nº 3.978/2020)."
        ])
    elif "AMARELA" in contexto_operacional:
        parecer_contingencia.extend([
            "- **Veredito:** RETENÇÃO PREVENTIVA PARA VALIDAÇÃO (MFA).",
            "- **Fundamentação:** Operação alocada em ZONA AMARELA (risco moderado). Exige autenticação multifatorial prévia à liberação de valores.",
            "- **Ação Mandatória:** Solicitar validação biométrica/token e revisão de histórico cadastral."
        ])
    else:
        parecer_contingencia.extend([
            "- **Veredito:** OPERAÇÃO HOMOLOGADA COM SUCESSO (ZONA VERDE).",
            "- **Fundamentação:** Risco estatístico reduzido, compatível com a capacidade financeira (Res. CMN nº 4.949/2021) e histórico cadastral do proponente.",
            "- **Recomendação Consultiva:** Concessão prioritária das linhas de crédito com taxas bonificadas do portfólio disponível."
        ])
       
    parecer_contingencia.append("\n*Documento emitido eletronicamente e validado pelo Sistema de Governança Levi.*")
    return "\n".join(parecer_contingencia)

def responder_chat_levi(contexto_operacional, pergunta_usuario, normativas, historico_conversa):
    """
    Conexão direta com o Google GenAI SDK utilizando System Instructions
    e histórico conversacional para respostas orgânicas e contextuais.
    """
    api_key_gemini = st.secrets.get("GEMINI_API_KEY", "")
    contexto_normativo = json.dumps(normativas, ensure_ascii=False, indent=2)
    
    # Instrução de Sistema: Define a persona e limites em segundo plano
    system_prompt = f"""Você é o Levi, um analista financeiro sênior, consultivo, altamente formal e profundo conhecedor das normas do Banco Central do Brasil (BACEN), COAF e LGPD.

SUAS DIRETRIZES FUNDAMENTAIS:
1. POSTURA E ELOQUÊNCIA: Responda de maneira analítica, corporativa, elegante e concisa. Utilize terminologia bancária adequada.
2. PERGUNTAS FORA DO ESCOPO BANCÁRIO/CRÉDITO (ex: receitas, esportes, clima, curiosidades gerais, entretenimento):
   - Não atenda a solicitações fora do domínio de crédito, risco e governança bancária.
   - Recuse com polidez e formalidade institucional, reforçando que suas atribuições limitam-se à esteira de concessão e conformidade regulatória.
3. DADOS SENSÍVEIS E LEGISLAÇÃO (LGPD - Lei nº 13.709/2018):
   - Se o operador solicitar ou mencionar informações de cunho religioso, político, médico/saúde, orientação sexual, senhas ou biometria bruta, recuse expressamente a ponderação desses dados com base nos princípios de não discriminação e privacidade da LGPD e Resolução CMN nº 4.949/2021.
4. ANÁLISE TÉCNICA E CRÉDITO:
   - ZONA VERDE: Fundamente em higidez financeira, ausência de anomalias no score e Resolução CMN nº 4.949/2021.
   - ZONA AMARELA: Indique necessidade de MFA ou validação biométrica antes da liberação.
   - ZONA VERMELHA: Fundamente o bloqueio preventivo estritamente na Resolução BCB nº 147/2021 (bloqueio cautelar) e Circular BACEN nº 3.978/2020 (PLD/FT).

=== DADOS ATUAIS DA OPERAÇÃO AUDITADA ===
{contexto_operacional}

=== BASE DE CONHECIMENTO REGULATÓRIO BACEN ===
{contexto_normativo}
"""

    if api_key_gemini:
        try:
            client = genai.Client(api_key=api_key_gemini)
            
            # Monta o histórico estruturado da conversa para o modelo
            conteudos = []
            for msg in historico_conversa[-6:]:  # Mantém as últimas 6 interações para contexto
                role = "user" if msg["role"] == "user" else "model"
                conteudos.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg["content"])]
                    )
                )
            
            # Adiciona a pergunta atual
            conteudos.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=pergunta_usuario)]
                )
            )

            # Executa a chamada com System Instruction
            resposta = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=conteudos,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.3,
                )
            )
            
            if resposta and resposta.text:
                return resposta.text
        except Exception as e:
            # Fallback flexível com indicação técnica
            pass

    # Motor de contingência flexível caso a API remota oscile
    p_lower = pergunta_usuario.lower()
    
    if any(k in p_lower for k in ["receita", "tempo", "jogo", "filme", "música", "conte", "crie", "poema"]):
        return (
            "**Comunicação Institucional de Escopo:**\n\n"
            "Na qualidade de Analista Sênior de Crédito e Governança Regulatória, minhas atribuições restringem-se "
            "à deliberação sobre riscos financeiros, parametrização preditiva e conformidade com as diretrizes do Banco Central do Brasil. "
            "Solicitações de natureza recreativa ou externa ao processo de crédito não são atendidas por esta mesa."
        )
    elif any(k in p_lower for k in ["saúde", "religião", "política", "senha", "biometria", "partido"]):
        return (
            "**Parecer de Governança LGPD (Lei nº 13.709/2018):**\n\n"
            "Em consonância com a regulação do BACEN e a Lei Geral de Proteção de Dados, é expressamente vedada "
            "a utilização de atributos sensíveis (como filiação política, credo ou dados médicos) para precificação de risco ou concessão de crédito."
        )
    else:
        return (
            f"**Parecer Técnico Consultivo:**\n\n"
            f"Analisando os metadados da operação ({'ZONA VERMELHA' if 'VERMELHA' in contexto_operacional else 'ZONA VERDE'}), "
            f"a deliberação foi estabelecida com base nos índices de regularidade de rede, compatibilidade de renda cadastrada e diretrizes de crédito do BACEN."
        )
# ==============================================================================
# 5. GERADORES DE LAUDOS PDF TIMBRADOS E EVENTOS DE ALERTA
# ==============================================================================
def desenhar_papel_timbrado(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#0A192F"))
    canvas.rect(0, doc.height + doc.topMargin + 10, doc.width + doc.leftMargin + doc.rightMargin, 30, stroke=0, fill=1)
    canvas.setFillColor(colors.HexColor("#D4AF37"))
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawString(doc.leftMargin, doc.height + doc.topMargin + 20, "PARECER OPERACIONAL INSTITUCIONAL - AGENTE LEVI")
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.setFont('Helvetica', 8)
    canvas.drawString(doc.leftMargin, 30, f"Documento Restrito Confidencial | Rastreabilidade por Operador | Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    canvas.drawRightString(doc.width + doc.leftMargin, 30, f"Pág. {doc.page}")
    canvas.restoreState()

def gerar_pdf_auditoria_timbrado(id_cliente, contexto_codigo, parecer_ia, operador):
    pasta_local_pdfs = "auditoria_pdfs"
    os.makedirs(pasta_local_pdfs, exist_ok=True)
    nome_arquivo = f"PARECER_{id_cliente}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    caminho_completo = os.path.join(pasta_local_pdfs, nome_arquivo)
   
    doc = SimpleDocTemplate(caminho_completo, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=72, bottomMargin=72)
    estilos = getSampleStyleSheet()
   
    estilo_titulo = ParagraphStyle('T', fontName='Helvetica-Bold', fontSize=16, textColor=colors.HexColor("#0A192F"), spaceAfter=15)
    estilo_sub = ParagraphStyle('S', fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor("#6F553F"), spaceBefore=12, spaceAfter=6)
    estilo_corpo = ParagraphStyle('C', fontName='Helvetica', fontSize=10, textColor=colors.HexColor("#333333"), leading=13, spaceAfter=8)
    estilo_cod = ParagraphStyle('D', fontName='Courier', fontSize=8.5, backColor=colors.HexColor("#F4F4F4"), borderPadding=6, spaceAfter=8)
    
    story = [
        Paragraph("LAUDO TÉCNICO DE ADMISSIBILIDADE DE CRÉDITO", estilo_titulo),
        Paragraph(f"<b>ID do Proponente:</b> {id_cliente} | <b>Analista Responsável:</b> {operador}", estilo_corpo),
        Spacer(1, 10),
        Paragraph("1. MÉTRICAS DA ESTRUTURA DE PROCESSAMENTO DO CÓDIGO (XGBOOST)", estilo_sub),
        Paragraph(contexto_codigo.replace('\n', '<br/>'), estilo_cod),
        Paragraph("2. CONFORMIDADE, REGULAÇÃO E VEREDITO CONSULTIVO (GEMINI)", estilo_sub),
        Paragraph(parecer_ia.replace('\n', '<br/>'), estilo_corpo),
        Spacer(1, 20),
        Paragraph("________________________________________________________", estilo_corpo),
        Paragraph("<b>SISTEMA DE GOVERNANÇA DE COMPLIANCE LEVI</b>", estilo_corpo)
    ]
    doc.build(story, onFirstPage=desenhar_papel_timbrado, onLaterPages=desenhar_papel_timbrado)
    return caminho_completo

def disparar_alerta_diretoria(id_cliente, probabilidade, valor, ip_freq, operador):
    pasta_logs = "auditoria_logs"
    os.makedirs(pasta_logs, exist_ok=True)
    caminho_alertas = os.path.join(pasta_logs, "ALERTAS_DIRETORIA.txt")
   
    corpo_alerta = f"""
🚨 [ALERTA DE SEGURANÇA CRÍTICO - AGENTE LEVI]
--------------------------------------------------------------------------------
DATA/HORA: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
OPERADOR AUTENTICADO: {operador}
CLIENTE ALVO SENSÍVEL: {id_cliente}
STATUS: OPERAÇÃO BLOQUEADA (ZONA VERMELHA) - RISCO DE FRAUDE ELEVADO
MÉTRICAS DO DISPARO:
• Probabilidade de Fraude Computada: {probabilidade * 100:.2f}%
• Valor da Operação Solicitada: R$ {valor:.2f}
• Reputação de Rede (IP Freq): {ip_freq}
--------------------------------------------------------------------------------
\n"""
    with open(caminho_alertas, "a", encoding="utf-8") as f:
        f.write(corpo_alerta)

# ==============================================================================
# 6. RENDERIZAÇÃO DAS ABAS DA INTERFACE GRÁFICA (TABS MANAGEMENT)
# ==============================================================================
st.title("🏛️ Sistema Analítico de Concessão de Crédito - Levi")
st.caption("Core: XGBoost Pipeline Otimizado & ribbons de Inteligência Artificial Explicável (XAI)")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Executar Auditoria de Crédito",
    "➕ Inserir Novos Dados (Simplificado)",
    "🔒 Painel Administrativo de Logs",
    "💬 Chat Consultivo Levi (BACEN / Sabiá Grounding)"
])

# ------------------------------------------------------------------------------
# ABA 1: MOTOR DE INFERÊNCIA OPERACIONAL
# ------------------------------------------------------------------------------
with tab1:
    id_cliente_busca = st.text_input("Insira o identificador cadastral do cliente cadastrado:", "CLIENTE_8942")
    col1, col2, col3 = st.columns(3)
    with col1: valor_transacao = col1.number_input("Valor da Transação (R$):", min_value=0.0, value=149.62)
    with col2: tempo_decorrido = col2.number_input("Tempo de Execução (Segundos):", min_value=0.0, value=0.0)
    with col3: freq_ip = col3.number_input("Frequência Reputacional de IP:", min_value=1, value=1)
    
    if st.button("Executar Auditoria de Viabilidade Completa"):
        dados_input = pd.DataFrame([{"Time": tempo_decorrido, "Amount": valor_transacao, "IP_Frequencia_Score": freq_ip, "Previous_Action": "Autenticação MFA", "Connection_Type": "Fibra residencial"}])
        for i in range(1, 29): dados_input[f"V{i}"] = 0.00
           
        pred_resultado = modelo_calibrado.predict_proba(dados_input)
       
        if hasattr(pred_resultado, "shape") and len(pred_resultado.shape) > 1:
            probabilidade_fraude = float(pred_resultado[0, 1])
        else:
            probabilidade_fraude = float(pred_resultado[0][1]) if isinstance(pred_resultado, list) else 0.05
       
        if probabilidade_fraude <= 0.15:
            zona_risco = "VERDE (BAIXO RISCO)"
            st.markdown(f'<div class="zona-verde-box"><b>📊 PIPELINE:</b> Operação alocada na ZONA VERDE. Risco computado de {probabilidade_fraude*100:.2f}%. Concessão viável.</div>', unsafe_allow_html=True)
        elif probabilidade_fraude <= 0.70:
            zona_risco = "AMARELA (RISCO MÉDIO)"
            st.markdown(f'<div class="zona-amarela-box"><b>⚠️ PIPELINE:</b> Operação alocada na ZONA AMARELA. Risco computado de {probabilidade_fraude*100:.2f}%. Requer barreiras extras.</div>', unsafe_allow_html=True)
        else:
            zona_risco = "VERMELHA (ALTO RISCO)"
            st.markdown(f'<div class="zona-vermelha-box"><b>🚨 GATILHO DE ALERTA:</b> Operação bloqueada na ZONA VERMELHA. Risco de {probabilidade_fraude*100:.2f}%. Notificação enviada.</div>', unsafe_allow_html=True)
            disparar_alerta_diretoria(id_cliente_busca, probabilidade_fraude, valor_transacao, freq_ip, st.session_state["usuario_ativo"])
            st.toast("🚨 Alerta de Alto Risco despachado para a diretoria!", icon="⚠️")
        
        dados_cadastro = perfil_dados.get(id_cliente_busca, {"Idade": 69, "Renda Mensal": 6202.93, "Tempo de Relacionamento": 123})
       
        texto_produtos = ""
        if isinstance(produtos_dados, list):
            for prod in produtos_dados: 
                texto_produtos += f"- {prod.get('nome_produto')}: Taxa {prod.get('taxa_juros')} | Limite: R$ {prod.get('limite_maximo')}\n"
       
        historico_filtrado = df_historico[df_historico['id_cliente'] == id_cliente_busca]
        texto_historico = "\n".join([f"- Data: {l['data']} | Setor: {l['categoria']} | Status: {l['status_resolucao']}" for _, l in historico_filtrado.tail(2).iterrows()]) if not historico_filtrado.empty else "- Sem histórico prévio."
        
        contexto_operacional_texto = f"--- PARAMETRIZAÇÃO DO CODIGO ---\n- Risco Computado: {probabilidade_fraude*100:.2f}%\n- Auditoria: ZONA {zona_risco}\n- IP Freq: {freq_ip}\n\n--- PERFIL CADASTRAIS (JSON) ---\n- Idade: {dados_cadastro['Idade']} anos\n- Renda: R$ {dados_cadastro['Renda Mensal']}\n- Vínculo: {dados_cadastro['Tempo de Relacionamento']} meses\n\n--- PRODUTOS DISPONÍVEIS ---\n{texto_produtos}\n--- COMPLIANCE ANTERIOR (CSV) ---\n{texto_historico}"
       
        # Salva o contexto para o Chat
        st.session_state["ultimo_contexto_auditoria"] = contexto_operacional_texto
       
        with st.expander("Auditar Estrutura de Processamento do Código (XAI)"):
            st.code(contexto_operacional_texto, language="text")
        
        st.subheader("🎙️ Parecer Técnico Consultivo do Gemini")
        parecer_final = chamar_agente_levi(contexto_operacional_texto, "Emita a análise técnica institucional e decida formalmente sobre a concessão do limite de crédito.")
        st.markdown(parecer_final)
       
        caminho_pdf = gerar_pdf_auditoria_timbrado(id_cliente_busca, contexto_operacional_texto, parecer_final, st.session_state["usuario_ativo"])
        with open(caminho_pdf, "rb") as f:
            st.download_button(label="📥 Baixar Parecer Oficial em PDF Timbrado", data=f, file_name=os.path.basename(caminho_pdf), mime="application/pdf")

# ------------------------------------------------------------------------------
# ABA 2: CADASTRO DINÂMICO E PERSISTÊNCIA SIMPLIFICADA
# ------------------------------------------------------------------------------
with tab2:
    st.subheader("Módulo de Inserção Simplificada de Dados")
    with st.form("form_novos_dados", clear_on_submit=True):
        novo_id = st.text_input("ID ou CPF do Novo Proponente:")
        c_1, c_2, c_3 = st.columns(3)
        with c_1: nova_idade = c_1.number_input("Idade:", min_value=18, value=35)
        with c_2: nova_renda = c_2.number_input("Renda Declarada (R$):", min_value=0.0, value=3000.0)
        with c_3: novo_tempo = c_3.number_input("Tempo de Vínculo (Meses):", min_value=0, value=24)
       
        if st.form_submit_button("Indexar no Banco de Conhecimento"):
            if novo_id:
                perfil_dados[novo_id] = {"Idade": int(nova_idade), "Renda Mensal": float(nova_renda), "Tempo de Relacionamento": int(novo_tempo)}
                with open('data/perfil_investidor.json', 'w', encoding='utf-8') as f:
                    json.dump(perfil_dados, f, indent=4, ensure_ascii=False)
                st.success(f"Cadastro do cliente {novo_id} acoplado com sucesso às matrizes de memória.")
                modelo_calibrado, perfil_dados, produtos_dados, df_historico = carregar_sistema_producao()
            else: 
                st.error("O campo ID é mandatório para indexação.")

# ------------------------------------------------------------------------------
# ABA 3: PAINEL ADMINISTRATIVO DE LAUDOS E LOGS (VIEWER DE PDF EMBUTIDO)
# ------------------------------------------------------------------------------
with tab3:
    st.subheader("Visualizador de Conformidade e Governança")
    pasta_pdfs = "auditoria_pdfs"
   
    if not os.path.exists(pasta_pdfs) or not [f for f in os.listdir(pasta_pdfs) if f.endswith('.pdf')]:
        st.warning("Nenhum laudo formal em PDF foi gerado até o momento.")
    else:
        arquivos_pdf = sorted([f for f in os.listdir(pasta_pdfs) if f.endswith('.pdf')], reverse=True)
        pdf_selecionado = st.selectbox("Selecione o parecer para auditoria em tela:", arquivos_pdf)
       
        with open(os.path.join(pasta_pdfs, pdf_selecionado), "rb") as f: 
            dados_pdf = f.read()
        pdf_base64 = base64.b64encode(dados_pdf).decode('utf-8')
       
        pdf_display = f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="100%" height="600px" style="border:1px solid #D4AF37; border-radius:5px;"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# ABA 4: CHAT CONSULTIVO LEVI (BACEN / SABIÁ GROUNDING)
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ABA 4: CHAT CONSULTIVO LEVI (BACEN / SABIÁ GROUNDING)
# ------------------------------------------------------------------------------
with tab4:
    st.markdown("### 💬 Mesa de Consulta Regulatória & Análise de Crédito")
    st.caption("Agente Levi alimentado com matrizes de risco XGBoost e diretrizes do Banco Central do Brasil (BACEN / COAF / LGPD).")
   
    with st.expander("📚 Consultar Dicionário de Normativas BACEN Ativas"):
        for norma in normativas_bacen.get("resolucoes_bcb", []):
            st.markdown(f"**{norma['codigo']}** - *{norma['tema']}*")
            st.markdown(f"- **Diretriz:** {norma['diretriz']}")
            st.markdown(f"- **Aplicação:** `{norma['aplicacao_risco']}`")
            st.markdown("---")
            
    # 1. Renderiza o histórico de mensagens salvas na sessão
    for msg in st.session_state["historico_chat"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # 2. Captura a entrada do operador e processa a resposta DENTRO do if
    if prompt_usuario := st.chat_input("Pergunte sobre o enquadramento BACEN, justificativa de risco ou produto..."):
        # Exibe e grava a pergunta do operador
        st.session_state["historico_chat"].append({"role": "user", "content": prompt_usuario})
        with st.chat_message("user"):
            st.markdown(prompt_usuario)
            
        # Gera, exibe e grava a resposta do Levi
        with st.chat_message("assistant"):
            resposta_texto = responder_chat_levi(
                st.session_state['ultimo_contexto_auditoria'],
                prompt_usuario,
                normativas_bacen,
                st.session_state["historico_chat"]
            )
            st.markdown(resposta_texto)
            st.session_state["historico_chat"].append({"role": "assistant", "content": resposta_texto})