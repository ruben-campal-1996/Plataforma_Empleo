# Analisis_mercado/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
from urllib.parse import urljoin

@login_required
def index(request):
    return render(request, 'Usuarios/index.html', {'jobs': [], 'error': None})

@login_required
def buscar_trabajos(request):
    jobs = []
    error = None
    base_url = "https://www.infojobs.net"

    if request.method == 'GET':
        keywords = request.GET.get('q', '')
        province = request.GET.get('provincia', '0')
        print(f"Palabra clave recibida: {keywords}")
        print(f"Provincia recibida: {province}")

        if keywords:
            # Configurar Selenium
            options = Options()
            options.headless = False  # Visible para depurar
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("window-size=1920,1080")
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--disable-gpu")
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
            ]
            options.add_argument(f"user-agent={random.choice(user_agents)}")

            try:
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
                print("Navegador iniciado correctamente")
            except Exception as e:
                error = f"Error al iniciar el navegador: {str(e)}"
                print(error)
                return render(request, 'Usuarios/index.html', {'jobs': jobs, 'error': error})

            try:
                # Simular el formulario
                driver.get("https://www.infojobs.net")
                print("Cargando página inicial...")
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, "palabra"))
                )

                # Manejar el popup de consentimiento
                try:
                    print("Buscando popup de consentimiento...")
                    accept_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
                    )
                    accept_button.click()
                    print("Popup de consentimiento aceptado.")
                    time.sleep(2)
                except Exception as e:
                    print(f"No se encontró popup o no se pudo aceptar: {str(e)}")

                # Llenar palabra clave
                keyword_input = driver.find_element(By.ID, "palabra")
                keyword_input.clear()
                keyword_input.send_keys(keywords)
                print(f"Palabra clave ingresada: {keywords}")

                # Seleccionar provincia con Chosen.js
                if province != '0':
                    province_select = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.ID, "of_provincia"))
                    )
                    driver.execute_script(f"document.getElementById('of_provincia').value = '{province}';")
                    driver.execute_script("jQuery('#of_provincia').trigger('chosen:updated');")
                    print(f"Provincia seleccionada: {province}")
                    time.sleep(1)

                # Hacer clic en buscar
                search_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.ID, "searchOffers"))
                )
                search_button.click()
                print("Botón de búsqueda clicado.")

                # Esperar resultados
                print("Esperando ofertas iniciales...")
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ij-OfferCardContent-description-title-link"))
                )
                print("Ofertas iniciales cargadas. Haciendo scroll...")
                for _ in range(3):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(3)

                # Obtener HTML
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                with open("infojobs_debug.html", "w", encoding="utf-8") as f:
                    f.write(soup.prettify())

                # Extraer hasta 15 ofertas
                job_listings = soup.select("a.ij-OfferCardContent-description-title-link")[:15]
                print(f"Elementos encontrados: {len(job_listings)}")

                for i, job in enumerate(job_listings):
                    print(f"\nProcesando oferta {i+1}...")
                    title = job.text.strip()
                    href = job.get('href', '')
                    print(f"href extraído: {href}")

                    # Construir URL completa
                    link = urljoin(base_url, href)
                    print(f"URL construida: {link}")

                    # Visitar la oferta
                    print(f"Visitando oferta: {link}")
                    driver.get(link)
                    try:
                        # Esperar a que cargue la sección de detalles
                        WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "ij-OfferDetailHeader-detailsList"))
                        )
                        offer_html = driver.page_source
                        offer_soup = BeautifulSoup(offer_html, "html.parser")

                        # Extraer datos de detailsList
                        details_list = offer_soup.select_one(".ij-OfferDetailHeader-detailsList")
                        modality = "No disponible"
                        experience = "No disponible"
                        contract = "No disponible"

                        if details_list:
                            items = details_list.select("div.ij-OfferDetailHeader-detailsList-item p.ij-Text-body1")
                            for item in items:
                                text = item.text.strip()
                                if any(x in text for x in ["Presencial", "Híbrido", "Remoto"]):
                                    modality = text
                                elif "Experiencia mínima" in text:
                                    experience = text
                                elif any(x in text for x in ["Contrato", "Jornada"]):
                                    contract = text

                        # URL limpia para el front-end
                        clean_link = urljoin(base_url, href.split('?')[0])
                        print(f"Enlace almacenado: {clean_link}")
                        print(f"Modalidad: {modality}, Experiencia: {experience}, Contrato: {contract}")
                        jobs.append({
                            "title": title,
                            "link": clean_link,
                            "modality": modality,
                            "experience": experience,
                            "contract": contract
                        })

                    except Exception as e:
                        print(f"Error al procesar {title}: {str(e)}")
                        clean_link = urljoin(base_url, href.split('?')[0])
                        jobs.append({
                            "title": title,
                            "link": clean_link,
                            "modality": "No disponible",
                            "experience": "No disponible",
                            "contract": "No disponible"
                        })

                if not jobs:
                    error = "No se encontraron ofertas."

            except Exception as e:
                error = f"Ocurrió un error en el scraping: {str(e)}"
                print(error)

            finally:
                driver.quit()
                print("Navegador cerrado.")

    print(f"Trabajos encontrados: {len(jobs)}")
    for job in jobs:
        print(f"Oferta final: {job['title']} - {job['link']} - Modalidad: {job['modality']} - Experiencia: {job['experience']} - Contrato: {job['contract']}")
    return render(request, 'Usuarios/index.html', {'jobs': jobs, 'error': error})