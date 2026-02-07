import google.generativeai as genai
import os
from dotenv import load_dotenv

# Tenta carregar do .env, senão espera a variável do sistema
load_dotenv()

# --- CONFIGURAÇÃO DA API KEY ---
# Você precisará pegar uma chave gratuita no Google AI Studio
# Coloque no arquivo .env como: GOOGLE_API_KEY=sua_chave_aqui
API_KEY = os.getenv("GOOGLE_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

def processar_redacao(caminho_imagem):
    print(f"🤖 [OCR AI] Iniciando análise de redação: {caminho_imagem}")
    
    if not API_KEY:
        return "ERRO: Chave de API do Google não configurada no backend."

    try:
        # Usa o modelo Flash que é mais rápido e barato
        model = genai.GenerativeModel ('gemini-1.5-flash')

        # Carrega a imagem
        with open(caminho_imagem, "rb") as f:
            imagem_bytes = f.read()

        image_parts = [
            {
                "mime_type": "image/jpeg", 
                "data": imagem_bytes
            }
        ]

        prompt = """
        Atue como um transcritor de provas escolares.
        Analise esta imagem de uma redação manuscrita.
        Sua tarefa é transcrever o texto EXATAMENTE como foi escrito pelo aluno.
        
        Regras:
        1. Respeite a pontuação e ortografia do aluno (mesmo se estiver errada).
        2. Se houver palavras riscadas (rasuras), ignore-as.
        3. Não adicione comentários seus, retorne APENAS o texto da redação.
        4. Separe os parágrafos corretamente.
        """

        response = model.generate_content([prompt, image_parts[0]])
        
        print("✅ [OCR AI] Transcrição concluída com sucesso.")
        return response.text

    except Exception as e:
        print(f"❌ [OCR AI] Erro na API: {e}")
        return f"Erro ao processar redação: {str(e)}"