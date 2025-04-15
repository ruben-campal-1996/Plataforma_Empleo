import threading
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
from urllib.parse import urljoin
from math import ceil  # Para calcular el número de páginas

@login_required
def index(request):
    context = {
        'jobs': [],
        'total_pages': 1,
        'current_page': 1,
        'keywords': '',
        'province': '0',
        'scraped': False,
    }
    return render(request, 'Usuarios/index.html', context)

def scrape_infojobs(keywords, province):
    print(f"DEBUG: scrape_infojobs iniciado con keywords='{keywords}', province='{province}'")
    jobs = []
    base_url = "https://www.infojobs.net"
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
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        print("Cargando página inicial de InfoJobs...")
        driver.get(base_url)
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
                company = "No disponible"
                description = "No disponible"
                technologies = ["No disponible"]

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

                # Extraer descripción y compañía
                description_elem = offer_soup.select_one(".ij-OfferDetailDescription-content")
                description = description_elem.text.strip() if description_elem else "No disponible"
                company_elem = offer_soup.select_one(".ij-OfferDetailHeader-companyName")
                company = company_elem.text.strip() if company_elem else "No disponible"

                clean_link = urljoin(base_url, href.split('?')[0])
                jobs.append({
                    "title": title,
                    "link": clean_link,
                    "location": location,
                    "modality": modality,
                    "salary": salary,
                    "experience": experience,
                    "contract": contract,
                    "source": "InfoJobs",
                    "company": company,
                    "description": description,
                    "technologies": technologies
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
                    "contract": "No disponible",
                    "source": "InfoJobs",
                    "company": "No disponible",
                    "description": "No disponible",
                    "technologies": ["No disponible"]
                })

        print(f"Total de ofertas recolectadas de InfoJobs: {len(jobs)}")
        return jobs

    except Exception as e:
        print(f"Error en scrape_infojobs: {str(e)}")
        return jobs

    finally:
        driver.quit()
        print("Navegador cerrado (InfoJobs).")

def scrape_tecnoempleo(keywords, province):
    print(f"DEBUG: scrape_tecnoempleo iniciado con keywords='{keywords}', province='{province}'")
    jobs = []
    base_url = "https://www.tecnoempleo.com"
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
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    province_mapping = {
        "28": "231",  # A Coruña
        "2": "232",   # Álava/Araba
        "3": "233",   # Albacete
        "4": "234",   # Alicante/Alacant
        "5": "235",   # Almería
        "6": "236",   # Asturias
        "7": "237",   # Ávila
        "8": "238",   # Badajoz
        "9": "240",   # Barcelona
        "10": "242",  # Burgos
        "11": "243",  # Cáceres
        "12": "244",  # Cádiz
        "13": "245",  # Cantabria
        "14": "246",  # Castellón/Castelló
        "15": "247",  # Ceuta
        "16": "248",  # Ciudad Real
        "17": "249",  # Córdoba
        "18": "250",  # Cuenca
        "19": "252",  # Girona
        "20": "259",  # Las Palmas -> Las Palmas de Gran Canaria
        "21": "253",  # Granada
        "22": "254",  # Guadalajara
        "23": "251",  # Guipúzcoa/Gipuzkoa -> Gipuzkoa
        "24": "255",  # Huelva
        "25": "256",  # Huesca
        "26": "239",  # Islas Baleares/Illes Balears -> Baleares
        "27": "257",  # Jaén
        "29": "258",  # La Rioja
        "30": "260",  # León
        "31": "262",  # Lleida
        "32": "261",  # Lugo
        "33": "263",  # Madrid
        "34": "264",  # Málaga
        "35": "265",  # Melilla
        "36": "266",  # Murcia
        "37": "267",  # Navarra
        "38": "268",  # Ourense
        "39": "269",  # Palencia
        "40": "270",  # Pontevedra
        "41": "271",  # Salamanca
        "42": "273",  # Segovia
        "43": "274",  # Sevilla
        "44": "275",  # Soria
        "45": "276",  # Tarragona
        "46": "272",  # Santa Cruz de Tenerife -> Sta. Cruz de Tenerife
        "47": "277",  # Teruel
        "48": "278",  # Toledo
        "49": "279",  # Valencia/València -> Valencia
        "50": "280",  # Valladolid
        "51": "241",  # Vizcaya/Bizkaia -> Bizkaia
        "52": "281",  # Zamora
        "53": "282",  # Zaragoza
    }

    def scrape_page():
        try:
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.col-10.col-md-9.col-lg-7")))
            print("Resultados cargados. Procesando ofertas...")
        except Exception as e:
            print(f"Error al esperar resultados: {str(e)}")
            return

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

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        all_job_listings = soup.select("div.col-10.col-md-9.col-lg-7")

        for job in all_job_listings:
            title_elem = job.select_one("h3.fs-5 a")
            title = title_elem.text.strip() if title_elem else "No disponible"
            href = title_elem.get('href', '') if title_elem else ''
            link = urljoin(base_url, href) if href else "No disponible"

            company_elem = job.select_one("a.text-primary")
            company = company_elem.text.strip() if company_elem else "No disponible"

            # Extraer modalidad
            modality_elem = job.select_one("span.d-block.d-lg-none.text-gray-800")
            modality = modality_elem.text.strip() if modality_elem else "No disponible"
            if modality != "No disponible":
                modality = modality.split(" - ")[0].strip()

            tech_elems = job.select("span.badge")
            technologies = [tech.text.strip() for tech in tech_elems] if tech_elems else ["No disponible"]

            location = "No disponible"
            location_elem = job.select_one("span.location, span.text-gray-800")
            if location_elem:
                location_text = location_elem.text.strip().lower()
                if "españa" in location_text or "remoto" in location_text:
                    location = "España (Remoto)" if "remoto" in location_text else "España"
                else:
                    location = location_text.capitalize()

            jobs.append({
                "title": title,
                "link": link,
                "location": location,
                "modality": modality,
                "experience": "No disponible",
                "contract": "No disponible",
                "source": "Tecnoempleo",
                "company": company,
                "technologies": technologies
            })
            print(f"Oferta añadida de Tecnoempleo: {title}")

    try:
        print("Iniciando scraping de Tecnoempleo...")
        driver.get(base_url)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "te")))
        print("Página de Tecnoempleo cargada.")

        keyword_input = driver.find_element(By.ID, "te")
        keyword_input.clear()
        keyword_input.send_keys(keywords)
        print(f"Palabra clave ingresada: {keywords}")

        if province != '0':
            tecno_province = province_mapping.get(province, province)
            print(f"Provincia recibida (InfoJobs ID): {province}")
            print(f"Provincia mapeada para Tecnoempleo: {tecno_province}")
            select = Select(WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "pr"))
            ))
            select.select_by_value(tecno_province)
            print(f"Provincia seleccionada en Tecnoempleo: {tecno_province}")
            time.sleep(1)

        search_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-warning[type='submit']"))
        )
        driver.execute_script("arguments[0].click();", search_button)
        print("Búsqueda iniciada en Tecnoempleo.")

        print("Procesando página 1...")
        scrape_page()

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        try:
            print("Buscando enlace a la página 2...")
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "nav[aria-label='pagination']"))
            )
            page_2_link = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//li[@class='page-item']/a[@class='page-link' and contains(@href, 'pagina=2') and text()='2']"))
            )
            page_2_url = page_2_link.get_attribute("href")
            print(f"Enlace a la página 2 encontrado: {page_2_url}")
            driver.get(page_2_url)
            time.sleep(3)

            print("Procesando página 2...")
            scrape_page()

        except Exception as e:
            print(f"No se pudo navegar a la página 2: {str(e)}")
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            pagination = soup.select("li.page-item a.page-link[href*='pagina=2']")
            if not pagination:
                print("No se encontró enlace a la página 2 en el HTML. Es posible que no haya más páginas.")
            else:
                print("El enlace a la página 2 está presente en el HTML, pero no se pudo acceder con Selenium.")
                print(f"HTML encontrado: {pagination}")
            with open("tecnoempleo_pagination_error.html", "w", encoding="utf-8") as f:
                f.write(html)

        print(f"Total de ofertas recolectadas de Tecnoempleo: {len(jobs)}")
        return jobs

    except Exception as e:
        print(f"Error en scrape_tecnoempleo: {str(e)}")
        return jobs

    finally:
        driver.quit()
        print("Navegador cerrado (Tecnoempleo).")

@login_required
def buscar_trabajos(request):
    jobs = []
    error = None

    if request.method == 'GET':
        keywords = request.GET.get('q', '')
        province = request.GET.get('provincia', '0')
        page = int(request.GET.get('page', 1))
        scraped = request.GET.get('scraped', 'False') == 'True'
        print(f"Palabra clave recibida: {keywords}")
        print(f"Provincia recibida: {province}")
        print(f"Página solicitada: {page}")
        print(f"Scraped: {scraped}")

        if keywords and not scraped:
            infojobs_jobs = []
            tecnoempleo_jobs = []

            def scrape_infojobs_thread():
                nonlocal infojobs_jobs
                try:
                    infojobs_jobs = scrape_infojobs(keywords, province)
                    print(f"DEBUG: InfoJobs recolectó {len(infojobs_jobs)} ofertas")
                except Exception as e:
                    print(f"Error en hilo de InfoJobs: {str(e)}")
                    infojobs_jobs = []

            def scrape_tecnoempleo_thread():
                nonlocal tecnoempleo_jobs
                try:
                    tecnoempleo_jobs = scrape_tecnoempleo(keywords, province)
                    print(f"DEBUG: Tecnoempleo recolectó {len(tecnoempleo_jobs)} ofertas")
                except Exception as e:
                    print(f"Error en hilo de Tecnoempleo: {str(e)}")
                    tecnoempleo_jobs = []

            infojobs_thread = threading.Thread(target=scrape_infojobs_thread)
            tecnoempleo_thread = threading.Thread(target=scrape_tecnoempleo_thread)
            print("Iniciando hilos para InfoJobs y Tecnoempleo...")
            infojobs_thread.start()
            tecnoempleo_thread.start()

            infojobs_thread.join()
            tecnoempleo_thread.join()
            print("Ambos hilos han finalizado.")

            jobs = infojobs_jobs + tecnoempleo_jobs
            if not jobs:
                error = "No se encontraron ofertas en ninguno de los sitios."
                print(error)

            request.session['jobs'] = jobs
            request.session['scraped'] = True
            request.session['keywords'] = keywords
            request.session['province'] = province

        else:
            if 'jobs' in request.session:
                jobs = request.session['jobs']
                keywords = request.session.get('keywords', keywords)
                province = request.session.get('province', province)
            else:
                error = "No hay ofertas almacenadas. Realiza una búsqueda primero."
                print(error)

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
        'scraped': scraped or ('jobs' in request.session),
    }
    return render(request, 'Usuarios/index.html', context)