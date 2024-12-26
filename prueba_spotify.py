import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time


class TestSpotify(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Configuración inicial
        chrome_options = Options()
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument('--start-maximized')
        service = Service(executable_path="chromedriver.exe")
        cls.driver = webdriver.Chrome(service=service, options=chrome_options)



    def test_01_iniciar_sesion_spotify(self):
        # URL de la página
        url_spotify = "https://www.spotify.com/"
        correo = "prueba001mat@gmail.com"
        contrasena = "Matias_2003"

        
        inicio_carga = time.time()
        # Abrir la página
        self.driver.get(url_spotify)
        
        
        try:
            # Esperar a que la página esté completamente cargada
            WebDriverWait(self.driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            pagina_tiempo_fin = time.time()
            carga_pagina = pagina_tiempo_fin - inicio_carga
            print(f"El tiempo de carga de la pagina es de: {carga_pagina:.2f}")
        except Exception as e:
            print(f"Error al cargar la página {e}")
        
            time.sleep(5)

        # Quitar el mensaje de cookies
        try:
            quitar_mensaje_cookies = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Cerrar']"))
            )
            quitar_mensaje_cookies.click()
            print("Se ha quitado el mensaje de cookies")
        except Exception as e:
            print(f"Error al quitar el mensaje de cookies: {e}")

            time.sleep(3)


        # Hacer click en el botón iniciar sesión para acceder al formulario
        try:
            boton_inicio = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "Button-sc-qlcn5g-0"))
            )
            boton_inicio.click()
            print("Clic en el botón inicial exitoso.")
        except Exception as e:
            self.fail(f"Error al hacer clic en el botón inicial: {e}")


        # Esperar a que cargue el formulario y rellenar el correo
        try:
            correo_input = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, "login-username"))  # ID del campo de correo
            )
            correo_input.send_keys(correo)
            correo_input.send_keys(Keys.TAB)
            print("Correo ingresado exitosamente.")
        except Exception as e:
            self.fail(f"Error al ingresar el correo: {e}")

        # Esperar a que cargue el campo de contraseña
        try:
            contrasena_input = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "login-password"))  # ID del campo de contraseña
            )
            contrasena_input.send_keys(contrasena)
            print("Contraseña ingresada exitosamente.")
        except Exception as e:
            self.fail(f"Error al ingresar la contraseña: {e}")

        try:
            boton_inicio_sesion = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.ID, "login-button"))
            )
            boton_inicio_sesion.click()
            print("Clic en el botón iniciar sesión exitoso.")
        except Exception as e:
            self.fail(f"Error al hacer clic en el botón iniciar sesión: {e}")

        # Medir el tiempo de carga después de presionar presionar el botón de iniciar sesión
        inicio_ejecucion = time.time()

        # Esperar a que se cargue la página después de iniciar sesión (usando un elemento específico de la nueva página)
        try:
            # Aquí esperamos un elemento de la página de inicio de Spotify
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jEMA2gVoLgPQqAFrPhFw"))  # Usamos el div que contiene las canciones el cual es el que se demora más 
            )
            print("Página cargada después del inicio de sesión.")
        except Exception as e:
            self.fail(f"Error al esperar la carga completa de la página: {e}")
        
        fin_carga = time.time()
        carga_tiempo = fin_carga - inicio_ejecucion

        # Imprimir el tiempo de carga
        print(f"El tiempo de carga desde el clic en 'Iniciar sesión' es de: {carga_tiempo:.2f} segundos.")
        time.sleep(2)


    # Testeo para utilizar la barra de búsqueda

    def test_02_buscar_musica(self):
        url = "https://open.spotify.com/"
        self.driver.get(url)

        inicio = time.time()
        try:
            ingresar_cancion = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "Input-sc-1gbx9xe-0"))
            )

            ingresar_cancion.send_keys("Aunque no me creas kidd voodoo")
            ingresar_cancion.send_keys(Keys.ENTER)
        except Exception as e:
            self.fail(f"Error al ingresar el nombre de la canción: {e}")


        fin = time.time()
        carga = fin - inicio
        print(f"El tiempo de carga para buscar una canción es de: {carga:.2f} segundos")

        time.sleep(5)


        # Reproducir canción haciendo doble click al div que contiene la canción que quiero
        try:
            reproducir_cancion = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "w46g_LQVSLE9xK399VYf"))
            )
        # Utilizamos ActionChains para realizar la acción de doble click
            accion = ActionChains(self.driver)
            accion.double_click(reproducir_cancion).perform()
             
            print("Se hizo click en la canción")
        except Exception as e:
            self.fail(f"Error al reproducir la canción: {e}")


        time.sleep(20)


    # Testeo para pausar canción
    
    def test_03_pausar_cancion(self):

        try:
            pausar = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="control-button-playpause"]'))
            )
            pausar.click()
            print("Se pausó la canción")
        except Exception as e:
            self.fail(f"Error al pausar la canción: {e}")

        time.sleep(3)
            

    @classmethod
    def tearDownClass(cls):
        # Cerrar el navegador después de las pruebas
        cls.driver.quit()


if __name__ == "__main__":
    unittest.main()

