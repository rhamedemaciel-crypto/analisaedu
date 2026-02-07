import google.generativeai as genai
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configura a API Key
API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

def encontrar_modelo_disponivel():
    """
    Função que busca automaticamente qual modelo sua chave tem permissão para usar.
    """
    print("🔍 [IA] Buscando modelo Gemini compatível com sua chave...")
    
    try:
        modelos = list(genai.list_models())
        
        # 1. Tenta achar o Flash (mais rápido e barato)
        for m in modelos:
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini-1.5-flash' in m.name:
                    return m.name 

        # 2. Se não achar Flash, tenta o Pro
        for m in modelos:
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini-1.5-pro' in m.name:
                    return m.name

        # 3. Se não achar nenhum específico, pega o primeiro que for "Gemini"
        for m in modelos:
            if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name:
                return m.name

    except Exception as e:
        print(f"⚠️ [IA] Erro ao listar modelos: {e}")

    # Chute final se tudo falhar (o padrão mais comum)
    return 'models/gemini-1.5-flash'

def processar_redacao(caminho_imagem):
    print(f"🤖 [IA] Iniciando análise de redação: {caminho_imagem}")
    
    if not API_KEY:
        return "ERRO: Chave de API do Google não configurada no backend (.env)."

    try:
        # Descobre o nome correto do modelo para VOCÊ
        nome_modelo = encontrar_modelo_disponivel()
        print(f"🚀 [IA] Usando modelo: {nome_modelo}")

        model = genai.GenerativeModel(nome_modelo)

        # Prepara a imagem
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
        Sua tarefa é transcrever o texto manuscrito desta imagem.
        Retorne APENAS o texto, sem comentários.
        Se não houver texto legível, diga "Texto ilegível".
        """

        # Envia para o Google
        response = model.generate_content([prompt, image_parts[0]])
        
        texto_final = response.text
        print("✅ [IA] Transcrição concluída com sucesso.")
        return texto_final

    except Exception as e:
        print(f"❌ [IA] Falha fatal: {e}")
        return f"Erro técnico na IA: {str(e)}"