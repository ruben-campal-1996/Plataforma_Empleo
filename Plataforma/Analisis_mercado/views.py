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
from urllib.parse import urljoin  # Para manejar URLs de forma más segura

@login_required
def index(request):
    return render(request, 'Usuarios/index.html', {'jobs': [], 'error': None})

@login_required
def buscar_trabajos(request):
    jobs = []
    error = None
    base_url = "https://www.infojobs.net"  # Definir base URL

    if request.method == 'GET':
        keywords = request.GET.get('q', '')
        print(f"Palabra clave recibida: {keywords}")

        if keywords:
            # Configurar Selenium
            options = Options()
            options.headless = True
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
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
                # URL de búsqueda
                search_url = f"https://www.infojobs.net/jobsearch/search-results/list.xhtml?keyword={keywords}"
                print("Solicitando página:", search_url)
                driver.get(search_url)

                # Esperar y hacer scroll
                print("Esperando ofertas iniciales...")
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ij-OfferCardContent-description-title-link"))
                )
                print("Ofertas iniciales cargadas. Haciendo scroll...")
                last_height = driver.execute_script("return document.body.scrollHeight")
                while len(jobs) < 15:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height

                # Obtener HTML
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")

                # Guardar para depuración
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

                    # Construir URL de forma segura con urljoin
                    link = urljoin(base_url, href)
                    print(f"URL construida: {link}")

                    # Visitar la oferta
                    print(f"Visitando oferta: {link}")
                    driver.get(link)
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "ij-Description-content"))
                        )
                        offer_html = driver.page_source
                        offer_soup = BeautifulSoup(offer_html, "html.parser")

                        # Verificar si la página tiene contenido
                        if not offer_soup.select_one(".ij-Description-content"):
                            print(f"Advertencia: Página en blanco o sin contenido para {title}")

                        # Extraer datos
                        description_elem = offer_soup.select_one(".ij-Description-content")
                        description = (description_elem.text.strip()[:200] + "..." 
                                     if description_elem and len(description_elem.text) > 200 
                                     else description_elem.text.strip() if description_elem else "No disponible")

                        location_elem = offer_soup.select_one("span[data-test='job-location']")
                        location = location_elem.text.strip() if location_elem else "No disponible"

                        salary_elem = offer_soup.select_one("span[data-test='job-salary']")
                        salary = salary_elem.text.strip() if salary_elem else "No especificado"

                        print(f"Enlace almacenado para front-end: {link}")
                        jobs.append({
                            "title": title,
                            "link": link,
                            "description": description,
                            "location": location,
                            "salary": salary
                        })
                    except Exception as e:
                        print(f"Error al procesar {title}: {str(e)}")
                        jobs.append({
                            "title": title,
                            "link": link,
                            "description": "No disponible",
                            "location": "No disponible",
                            "salary": "No especificado"
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
        print(f"Oferta final: {job['title']} - {job['link']}")
    return render(request, 'Usuarios/index.html', {'jobs': jobs, 'error': error})