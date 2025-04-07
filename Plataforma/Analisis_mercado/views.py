# Analisis_mercado/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

@login_required
def index(request):
    return render(request, 'Usuarios/index.html', {'jobs': [], 'error': None})

@login_required
def buscar_trabajos(request):
    jobs = []
    error = None

    if request.method == 'GET':
        keywords = request.GET.get('q', '')
        print(f"Palabra clave recibida: {keywords}")

        if keywords:
            # Configura Selenium en modo headless
            options = Options()
            options.headless = True
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
            ]
            options.add_argument(f"user-agent={random.choice(user_agents)}")

            # Inicializar el navegador
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
                driver.get(search_url)
                print("Página solicitada:", search_url)

                # Detectar CAPTCHA (usar iframe como indicador común)
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.TAG_NAME, "iframe"))  # reCAPTCHA suele estar en un iframe
                    )
                    print("CAPTCHA detectado. Abriendo ventana para resolverlo...")
                    driver.quit()
                    options.headless = False
                    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
                    driver.get(search_url)
                    print("Por favor, resuelve el CAPTCHA en la ventana emergente.")
                    WebDriverWait(driver, 60).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "ij-OfferCardContent-description-title-link"))
                    )
                    print("CAPTCHA resuelto y ofertas cargadas.")
                except:
                    print("No se detectó CAPTCHA. Continuando en modo headless...")
                    # Esperar las ofertas dinámicamente
                    try:
                        WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "ij-OfferCardContent-description-title-link"))
                        )
                        print("Ofertas cargadas en modo headless.")
                    except:
                        error = "No se cargaron las ofertas en modo headless. Revisa infojobs_debug.html."
                        print(error)

                # Obtener el HTML
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")

                # Guardar HTML para depuración
                with open("infojobs_debug.html", "w", encoding="utf-8") as f:
                    f.write(soup.prettify())

                # Depuración
                print("HTML recibido (primeros 500 caracteres):", soup.prettify()[:500])

                # Buscar trabajos
                job_listings = soup.find_all("a", class_="ij-OfferCardContent-description-title-link")
                print(f"Elementos encontrados con 'ij-OfferCardContent-description-title-link': {len(job_listings)}")

                for job in job_listings:
                    title = job.text.strip()
                    if title:
                        jobs.append({"title": title})

                if not jobs and not error:
                    error = "No se encontraron ofertas con el selector actual. Revisa infojobs_debug.html."

            except Exception as e:
                error = f"Ocurrió un error al obtener los resultados: {str(e)}"
                print(error)

            finally:
                driver.quit()

    print(f"Trabajos encontrados: {jobs}")
    return render(request, 'Usuarios/index.html', {'jobs': jobs, 'error': error})