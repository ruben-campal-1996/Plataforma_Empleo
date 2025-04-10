# Analisis_mercado/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
from urllib.parse import urljoin
from math import ceil  # Para calcular el número de páginas

@login_required
def index(request):
    # Caso inicial: sin búsqueda realizada
    context = {
        'jobs': [],  # Lista vacía si no hay búsqueda
        'total_pages': 1,  # Valor por defecto para evitar None
        'current_page': 1,  # Página inicial
        'keywords': '',  # Sin palabras clave aún
        'province': '0',  # Valor por defecto para provincia
        'scraped': False,  # No se ha hecho scraping
    }
    return render(request, 'usuarios/index.html', context)

@login_required
def buscar_trabajos(request):
    jobs = []
    error = None
    base_url = "https://www.infojobs.net"

    if request.method == 'GET':
        keywords = request.GET.get('q', '')
        province = request.GET.get('provincia', '0')
        page = int(request.GET.get('page', 1))
        scraped = request.GET.get('scraped', 'False') == 'True'  # Indicador de si ya se hizo scraping
        print(f"Palabra clave recibida: {keywords}")
        print(f"Provincia recibida: {province}")
        print(f"Página solicitada: {page}")
        print(f"Scraped: {scraped}")

        if keywords and not scraped:
            options = Options()
            options.headless = True
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("window-size=1920,1080")
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--disable-gpu")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
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
                print("Cargando página inicial...")
                driver.get("https://www.infojobs.net")
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.ID, "palabra"))
                )
                print("Página inicial cargada.")

                try:
                    print("Buscando popup de consentimiento...")
                    accept_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
                    )
                    accept_button.click()
                    print("Popup de consentimiento aceptado.")
                    time.sleep(1)
                except Exception as e:
                    print(f"No se encontró popup o no se pudo aceptar: {str(e)}")

                keyword_input = driver.find_element(By.ID, "palabra")
                keyword_input.clear()
                keyword_input.send_keys(keywords)
                print(f"Palabra clave ingresada: {keywords}")

                if province != '0':
                    province_select = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.ID, "of_provincia"))
                    )
                    driver.execute_script(f"document.getElementById('of_provincia').value = '{province}';")
                    driver.execute_script("jQuery('#of_provincia').trigger('chosen:updated');")
                    print(f"Provincia seleccionada: {province}")
                    time.sleep(1)

                search_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.ID, "searchOffers"))
                )
                search_button.click()
                print("Botón de búsqueda clicado.")

                # Procesar solo la página 1 de InfoJobs
                print("\nProcesando página 1 de InfoJobs...")
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ij-OfferCardContent-description-title-link"))
                )
                print("Ofertas cargadas. Haciendo scroll gradual...")

                total_height = driver.execute_script("return document.body.scrollHeight")
                current_position = 0
                step = 500
                while current_position < total_height:
                    driver.execute_script(f"window.scrollTo(0, {current_position});")
                    current_position += step
                    time.sleep(0.5)
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height > total_height:
                        total_height = new_height
                    print(f"Scroll - Posición: {current_position}, Altura total: {total_height}")

                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                all_job_listings = soup.select("a.ij-OfferCardContent-description-title-link")
                print(f"Ofertas detectadas en página 1: {len(all_job_listings)}")

                # Procesar todas las ofertas de la página 1
                for i, job in enumerate(all_job_listings):
                    print(f"\nProcesando oferta {len(jobs)+1}...")
                    title = job.text.strip()
                    href = job.get('href', '')
                    link = urljoin(base_url, href)
                    print(f"URL construida: {link}")

                    for attempt in range(2):
                        try:
                            driver.get(link)
                            WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.CLASS_NAME, "ij-OfferDetailHeader-detailsList"))
                            )
                            break
                        except Exception as e:
                            if attempt == 0:
                                print(f"Fallo al cargar oferta (intento 1/2), reintentando...")
                                time.sleep(2)
                            else:
                                print(f"Error persistente al cargar oferta: {str(e)}")

                    try:
                        offer_html = driver.page_source
                        offer_soup = BeautifulSoup(offer_html, "html.parser")
                        details_list = offer_soup.select_one(".ij-OfferDetailHeader-detailsList")
                        location = "No disponible"
                        modality = "No disponible"
                        salary = "No disponible"
                        experience = "No disponible"
                        contract = "No disponible"

                        if details_list:
                            items = details_list.select(".ij-OfferDetailHeader-detailsList-item p.ij-Text-body1")
                            for item in items:
                                text = item.text.strip()
                                if "(" in text and ")" in text:
                                    location = text
                                elif any(x in text for x in ["Presencial", "Híbrido", "Remoto"]):
                                    modality = text
                                elif "€" in text or "Bruto" in text or "Neto" in text:
                                    salary = text
                                elif "Experiencia mínima" in text:
                                    experience = text
                                elif any(x in text for x in ["Contrato", "Jornada"]):
                                    contract = text

                        clean_link = urljoin(base_url, href.split('?')[0])
                        jobs.append({
                            "title": title,
                            "link": clean_link,
                            "location": location,
                            "modality": modality,
                            "salary": salary,
                            "experience": experience,
                            "contract": contract
                        })
                        print(f"Oferta {len(jobs)} almacenada: {title}")

                    except Exception as e:
                        print(f"Error al procesar {title}: {str(e)}")
                        clean_link = urljoin(base_url, href.split('?')[0])
                        jobs.append({
                            "title": title,
                            "link": clean_link,
                            "location": "No disponible",
                            "modality": "No disponible",
                            "salary": "No disponible",
                            "experience": "No disponible",
                            "contract": "No disponible"
                        })

                if not jobs:
                    error = "No se encontraron ofertas."
                    print(error)

                # Guardar las ofertas en la sesión
                request.session['jobs'] = jobs
                request.session['scraped'] = True
                request.session['keywords'] = keywords
                request.session['province'] = province

            except Exception as e:
                error = f"Ocurrió un error en el scraping: {str(e)}"
                print(error)

            finally:
                driver.quit()
                print("Navegador cerrado.")

        else:
            # Recuperar las ofertas de la sesión si ya se scrapearon
            if 'jobs' in request.session:
                jobs = request.session['jobs']
                keywords = request.session.get('keywords', keywords)
                province = request.session.get('province', province)
            else:
                error = "No hay ofertas almacenadas. Realiza una búsqueda primero."
                print(error)

        # Paginación en el servidor para el front-end
        items_per_page = 10
        total_jobs = len(jobs)
        total_pages = ceil(total_jobs / items_per_page)
        start_index = (page - 1) * items_per_page
        end_index = start_index + items_per_page
        paginated_jobs = jobs[start_index:end_index]

        print(f"Total de trabajos recolectados: {total_jobs}")
        print(f"Total de páginas: {total_pages}")
        print(f"Ofertas enviadas para página {page}: {len(paginated_jobs)}")

    context = {
        'jobs': paginated_jobs if 'paginated_jobs' in locals() else jobs,
        'error': error,
        'total_pages': total_pages if 'total_pages' in locals() else 1,
        'current_page': page,
        'keywords': keywords,
        'province': province,
        'scraped': scraped or ('jobs' in request.session),  # Indica si las ofertas ya están en la sesión
    }
    return render(request, 'Usuarios/index.html', context)