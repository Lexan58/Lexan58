import asyncio
import pandas as pd
import os
import requests
from playwright.async_api import async_playwright
from datetime import datetime

# === CONFIGURACIÓN ===
TELEGRAM_TOKEN = "8549182157:AAHyAK3C2iFmNsCtsQo5998V9uDR1gSD0Kc"
TELEGRAM_CHAT_ID = "7011782289"
PALABRAS_CLAVE_EXITO = ["python", "video", "remoto", "remote", "edit", "asistente", "junior", "datos", "desarrollador", "ia", "ai"]

def enviar_telegram(mensaje):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}
        requests.post(url, data=payload)
    except Exception as e:
        print(f"❌ Error Telegram: {e}")

async def guardar_en_excel(nueva_oferta):
    ruta_excel = os.path.join(os.getcwd(), "mis_ofertas.xlsx")
    try:
        df_nueva = pd.DataFrame([nueva_oferta])
        if os.path.exists(ruta_excel):
            df_existente = pd.read_excel(ruta_excel)
            df_final = pd.concat([df_existente, df_nueva], ignore_index=True)
        else:
            df_final = df_nueva
        df_final.drop_duplicates(subset=['Link'], keep='first', inplace=True)
        df_final.to_excel(ruta_excel, index=False)
        return True
    except Exception as e:
        print(f"❌ Error al escribir en Excel: {e}")
        return False

async def analizar_ofertas(keyword):
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir="./user_data", 
            headless=False,
            args=["--start-maximized"]
        )
        page = browser.pages[0]

        url_chamba = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&location=Bogota%2C%20Colombia&f_WT=2&f_JT=P"
        print(f"🚀 Iniciando búsqueda: {url_chamba}")
        await page.goto(url_chamba)
        
        # Espera para que cargue la lista
        await page.wait_for_timeout(10000)

        # Seleccionamos las tarjetas
        ofertas = await page.query_selector_all('.job-card-container, [data-occludable-job-id]')
        total = len(ofertas)
        print(f"✅ Se encontraron {total} ofertas. Analizando...")

        for i, oferta in enumerate(ofertas):
            try:
                # 1. Scroll y Clic
                await oferta.scroll_into_view_if_needed()
                await page.wait_for_timeout(1000)
                await oferta.click(force=True)
                print(f"🧐 [{i+1}/{total}] Analizando...")

                # 2. Espera a que el panel derecho cargue algo de texto
                # Esperamos 6 segundos para dar tiempo al internet
                await page.wait_for_timeout(6000) 

                # 3. EXTRACCIÓN DETECTIVE (Buscamos por múltiples vías)
                try:
                    # Título: El h2 más grande del panel derecho
                    titulo = await page.locator('.job-details-jobs-unified-top-card__job-title, h2.t-24').first.inner_text(timeout=5000)
                    
                    # Empresa: El nombre que está cerca del título
                    empresa = await page.locator('.job-details-jobs-unified-top-card__company-name, .jobs-unified-top-card__company-name').first.inner_text(timeout=5000)
                    
                    # Descripción: El bloque grande de texto
                    # Si el selector de clase falla, tomamos el ID job-details
                    descripcion = await page.locator('#job-details, .jobs-description-content__text').first.inner_text(timeout=5000)
                
                except Exception as e_info:
                    print(f"⚠️ Error de lectura en oferta {i+1}: No se encontró el texto (posible bloqueo de LinkedIn)")
                    continue

                link_actual = page.url
                # Limpiamos el texto para el match
                desc_clean = descripcion.lower()
                match_si = any(word in desc_clean for word in PALABRAS_CLAVE_EXITO)
                
                datos = {
                    "Fecha": datetime.now().strftime("%Y-%m-%d"),
                    "Título": titulo.strip(),
                    "Empresa": empresa.strip(),
                    "Match": "SÍ" if match_si else "NO",
                    "Link": link_actual
                }

                # Guardamos SIEMPRE para verificar que está leyendo
                if await guardar_en_excel(datos):
                    if match_si:
                        print(f"✨ ¡MATCH! {titulo.strip()}")
                        enviar_telegram(f"🚀 ¡NUEVA CHAMBA!\n\n📌 {titulo.strip()}\n🏢 {empresa.strip()}\n🔗 {link_actual}")
                    else:
                        print(f"☁️  Guardada (Sin Match): {titulo.strip()}")

            except Exception as e:
                print(f"⚠️ Salto inesperado en oferta {i+1}")
                continue

        await browser.close()
        print("\n🏁 ¡Proceso finalizado! Revisa el Excel.")

if __name__ == "__main__":
    # Mensaje de inicio para Telegram
    enviar_telegram("🤖 Bot activo: Iniciando búsqueda en Bogotá...")
    asyncio.run(analizar_ofertas("Python"))