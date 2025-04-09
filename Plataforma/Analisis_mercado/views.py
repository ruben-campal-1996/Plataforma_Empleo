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
    return render(request, 'Usuarios/index.html', {'jobs': [], 'error': None})

@login_required
def buscar_trabajos(request):
    jobs = []
    error = None
    base_url = "https://www.infojobs.net"

    if request.method == 'GET':
        keywords = request.GET.get('q', '')
        province = request.GET.get('provincia', '0')
        page = int(request.GET.get('page', 1))  # Página actual, por defecto 1
        print(f"Palabra clave recibida: {keywords}")
        print(f"Provincia recibida: {province}")
        print(f"Página solicitada: {page}")

        if keywords:
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
                for attempt in range(2):
                    try:
                        driver.get("https://www.infojobs.net")
                        WebDriverWait(driver, 30).until(
                            EC.presence_of_element_located((By.ID, "palabra"))
                        )
                        print("Página inicial cargada.")
                        break
                    except TimeoutException:
                        print(f"Timeout al cargar la página inicial (intento {attempt + 1}/2)")
                        if attempt == 1:
                            raise Exception("No se pudo cargar la página inicial tras 2 intentos")
                        time.sleep(5)

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

                print("\nProcesando página 1 de InfoJobs...")
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ij-OfferCardContent-description-title-link"))
                )
                print("Ofertas cargadas. Haciendo scroll para recolectar todas las ofertas de la página 1...")

                previous_height = driver.execute_script("return document.body.scrollHeight")
                for i in range(10):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    print(f"Scroll {i+1}/10 - Altura de página: {new_height}")
                    if new_height == previous_height:
                        print("No se cargaron más ofertas tras el scroll.")
                        break
                    previous_height = new_height

                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                with open("infojobs_debug_page1.html", "w", encoding="utf-8") as f:
                    f.write(soup.prettify())

                all_job_listings = soup.select("a.ij-OfferCardContent-description-title-link")
                print(f"Ofertas detectadas en página 1 de InfoJobs: {len(all_job_listings)}")

                # Procesar todas las ofertas recolectadas
                for i, job in enumerate(all_job_listings):
                    print(f"\nProcesando oferta {i+1}...")
                    title = job.text.strip()
                    href = job.get('href', '')
                    print(f"href extraído: {href}")

                    link = urljoin(base_url, href)
                    print(f"URL construida: {link}")

                    print(f"Visitando oferta: {link}")
                    for attempt in range(2):
                        try:
                            driver.get(link)
                            print(f"Esperando detalles para oferta {i+1}...")
                            WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.CLASS_NAME, "ij-OfferDetailHeader-detailsList"))
                            )
                            break
                        except Exception as e:
                            if attempt == 0:
                                print(f"Fallo al cargar oferta {i+1} (intento 1/2), reintentando...")
                                time.sleep(2)
                            else:
                                print(f"Error persistente al cargar oferta {i+1}: {str(e)}")

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
                        print(f"Enlace almacenado: {clean_link}")
                        print(f"Ubicación: {location}, Modalidad: {modality}, Sueldo: {salary}, Experiencia: {experience}, Contrato: {contract}")
                        jobs.append({
                            "title": title,
                            "link": clean_link,
                            "location": location,
                            "modality": modality,
                            "salary": salary,
                            "experience": experience,
                            "contract": contract
                        })

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
                    error = "No se encontraron ofertas en la página 1."
                    print(error)

                # Paginación en el servidor
                items_per_page = 10
                total_jobs = len(jobs)
                total_pages = ceil(total_jobs / items_per_page)  # Número total de páginas
                start_index = (page - 1) * items_per_page
                end_index = start_index + items_per_page
                paginated_jobs = jobs[start_index:end_index]  # Solo las ofertas de la página actual

                print(f"Total de trabajos recolectados: {total_jobs}")
                print(f"Total de páginas: {total_pages}")
                print(f"Ofertas enviadas para página {page}: {len(paginated_jobs)}")

            except Exception as e:
                error = f"Ocurrió un error en el scraping: {str(e)}"
                print(error)

            finally:
                driver.quit()
                print("Navegador cerrado.")

    # Contexto para el template
    context = {
        'jobs': paginated_jobs if 'paginated_jobs' in locals() else jobs,
        'error': error,
        'total_pages': total_pages if 'total_pages' in locals() else 1,
        'current_page': page,
        'keywords': keywords,
        'province': province,
    }
    return render(request, 'Usuarios/index.html', context)