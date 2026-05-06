import asyncio
import pandas as pd
import os
import requests
from google import genai
from playwright.async_api import async_playwright
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

# === 1. CONFIGURACIÓN DE LLAVES ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# El resto de tu código se mantiene igual...
client = genai.Client(api_key=GOOGLE_API_KEY)

# === 2. DICCIONARIO DE TALENTOS (SCORING) ===
SCORING_SISTEMA = {
    "TECH_IA": {"python": 8, "automation": 7, "scraping": 6, "ai": 5, "ia": 5},
    "ACADEMIC": {"apa": 15, "vancouver": 15, "thesis": 10, "academic": 10, "redacción": 8},
    "HEALTH": {"medical": 12, "neuroscience": 15, "salud": 7, "emt": 10},
    "PROYECTOS": {"project": 8, "management": 7, "prefactibilidad": 10, "factibilidad": 10, "liderazgo": 5}
}

# === 3. LÓGICA DE ROTACIÓN DIARIA (BILINGÜE) ===
def obtener_config_dia():
    # 0=Lun, 1=Mar, 2=Mié, 3=Jue, 4=Vie
    dia = datetime.now().weekday()
    
    # Hemos optimizado las keywords para que busquen en inglés y español
    config = {
        0: {"kw": 'Medical Interpreter OR "Traductor Médico"', "modo": "Salud/Neuro"},
        1: {"kw": 'Python Automation OR "Desarrollador Python"', "modo": "Tech/IA"},
        2: {"kw": 'Project Coordinator OR "Gestión de Proyectos" OR "Prefactibilidad"', "modo": "Gestión/Factibilidad"},
        3: {"kw": 'Academic Editor OR "Normas APA" OR "Revisión de Tesis"', "modo": "Académico/Edición"}, 
        4: {"kw": 'Video Editor OR "Editor de Video" OR "TikTok Content"', "modo": "Creativo/Video"},
    }
    return config.get(dia, {"kw": "Remote Assistant", "modo": "General"})

# === 4. EL CEREBRO (IA + FALLBACK) ===
async def obtener_analisis_hibrido(titulo, descripcion):
    try:
        contexto = (
            "Candidato: Lexan. Perfil: Bilingüe (Inglés/Español), experto en Normas APA/Vancouver, "
            "Editor de video, Neurociencia (Duke), Proyectos (UC Irvine), Liderazgo (Los Andes). "
            "Experiencia real en estudios de prefactibilidad para el Jardín Botánico de Tuluá."
        )
        prompt = f"{contexto}\nOferta: {titulo}. Escribe un pitch de 3 líneas resaltando el talento que más encaje."
        
        response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
        return response.text, "GEMINI_IA"
    except Exception:
        desc_l = descripcion.lower()
        score = sum(pts for cat in SCORING_SISTEMA.values() for word, pts in cat.items() if word in desc_l)
        if score >= 6:
            return f"Match Manual (Score: {score}).", "MANUAL"
        return None, None

# === 5. PERSISTENCIA Y NOTIFICACIÓN ===
async def guardar_excel(datos):
    try:
        ruta = "mis_ofertas_ia.xlsx"
        df_nueva = pd.DataFrame([datos])
        if os.path.exists(ruta):
            df_final = pd.concat([pd.read_excel(ruta), df_nueva], ignore_index=True).drop_duplicates(subset=['Link'])
        else:
            df_final = df_nueva
        df_final.to_excel(ruta, index=False, engine='openpyxl')
        return True
    except: return False

async def analizar():
    config = obtener_config_dia()
    print(f"🚀 Iniciando Modo: {config['modo']} | Buscando: {config['kw']}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir="./user_data", 
            headless=False,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        page = browser.pages[0] if browser.pages else await browser.new_page()
        
        try:
            # URL optimizada para búsqueda global y remota
            url_busqueda = f"https://www.linkedin.com/jobs/search/?keywords={config['kw']}&f_WT=2"
            await page.goto(url_busqueda, timeout=60000, wait_until="commit")
            await page.wait_for_timeout(5000) # Espera extra para renderizado de tarjetas
        except Exception as e:
            print(f"⚠️ Error de carga: {e}")
            await browser.close()
            return

        ofertas = await page.query_selector_all('.job-card-container')
        
        for oferta in ofertas[:8]:
            try:
                await oferta.click()
                await page.wait_for_timeout(4000)
                
                titulo = await page.locator('.job-details-jobs-unified-top-card__job-title').first.inner_text()
                empresa = await page.locator('.job-details-jobs-unified-top-card__company-name').first.inner_text()
                desc = await page.locator('#job-details').first.inner_text()
                
                pitch, fuente = await obtener_analisis_hibrido(titulo, desc)
                
                if pitch:
                    print(f"✅ Match: {titulo}")
                    datos = {"Fecha": datetime.now(), "Título": titulo, "Empresa": empresa, "Pitch": pitch, "Link": page.url}
                    await guardar_excel(datos)
                    
                    msg = f"✨ NUEVA CHAMBA ({config['modo']})\n📌 {titulo}\n🏢 {empresa}\n💡 {pitch}\n🔗 {page.url}"
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                                  data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
            except: continue
            
        await browser.close()
        print("🏁 Proceso terminado.")

if __name__ == "__main__":
    asyncio.run(analizar())