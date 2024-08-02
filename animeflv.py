from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import argparse
import requests
import urllib.parse

# URL de la página web que deseas scrape, AnimeFLV
url_base = 'https://www3.animeflv.net'

# Configura las opciones de Chrome
chrome_options = Options()
chrome_options.add_argument("--disable-javascript")  # Desactiva JavaScript
chrome_options.add_argument("--headless")  # Ejecuta el navegador en modo headless (sin interfaz gráfica)


# Me retorna una lista de animes encontrados
def search_anime(search_text):
    animes_list = []

    # Realiza una solicitud GET a la URL
    response = requests.get(url_base + '/browse', params={'q': urllib.parse.quote(search_text)})

    # Verifica si la solicitud fue exitosa (código de estado 200)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Encuentra elementos específicos, por ejemplo, todos los enlaces
        search_result = soup.find(class_='ListAnimes')

        animes = search_result.find_all(class_='Anime')

        for anime in animes:
            anime_link = anime.find('a')
            anime_name = anime_link.find(class_='Title')

            animes_list.append({'name': anime_name.get_text(), 'link': anime_link.get('href')})
    else:
        print(f'Error accessing page, status code: {response.status_code}')

    return animes_list


def get_downloads_links_episode(episode_link):
    download_list = []

    try:
        # Crea una instancia del navegador Chrome
        browser = webdriver.Chrome(options=chrome_options)

        # Abre la página web
        browser.get(url_base + episode_link)

        # Obtén el contenido de la página
        page_content = browser.page_source        
        soup = BeautifulSoup(page_content, 'html.parser')

        # Obtengo el elemento "tbody" que contiene los enlaces de descarga
        tbody_download_list = soup.find('tbody')

        # Obtengo los elementos "tr" del "tbody"
        if tbody_download_list:
            tr_elements = tbody_download_list.find_all('tr') 

            for tr_element in tr_elements:
                tr_content = tr_element.find_all('td')
                provaider_name = tr_content[0].get_text()
                download_url = tr_content[3].find('a')

                download_list.append({'provaider_name': provaider_name, 'download_url': download_url.get('href')})                
        else: 
            print('Episodes not found.')

    except NoSuchElementException as e:
        print(f'Error finding an element on the page: {e}')
    except Exception as e:
        print(f'Error processing the HTML: {e}')
    finally:
        # Cierra el navegador
        browser.quit()

        return download_list


def get_links_episodes(anime_name, anime_link):
    print(f'Processing: {anime_name}, {anime_link}\n')

    episodes_list = []

    try:
        # Crea una instancia del navegador Chrome
        browser = webdriver.Chrome(options=chrome_options)

        # Abre la página web
        browser.get(url_base + anime_link)

        # Obtén el contenido de la página
        page_content = browser.page_source        
        soup = BeautifulSoup(page_content, 'html.parser')

        # Obtengo el contenedor "ul" de los episodios
        ul_episodes_result = soup.find('ul', class_='ListCaps')

        # Obtengo los elementos "li" de episodios
        if ul_episodes_result:
            li_episodes_result = ul_episodes_result.find_all('li') 

            for li_element in li_episodes_result:
                episode_link = li_element.find('a')
                episode_name = episode_link.find('p')

                episodes_list.append({'name': episode_name.get_text(), 'link': episode_link.get('href')})

            print(f'Total episode available(s): {len(episodes_list)}\n')
        else: 
            print('Episodes not found.')

    except NoSuchElementException as e:
        print(f'Error finding an element on the page: {e}')
    except Exception as e:
        print(f'Error processing the HTML: {e}')
    finally:
        # Cierra el navegador
        browser.quit()

        return episodes_list
    

def process_animes(animes_list):
    # Imprime la lista de animes
    print('List of available animes:\n')

    for i, element in enumerate(animes_list, start=1):
        print(f'{i}.- Anime: {element['name']}, enlace: {element['link']}')

    # Solicitar al usuario que seleccione un anime
    try:
        option = int(input('\nSelect a number to show download links: '))

        # Validar la entrada del usuario
        if 1 <= option <= len(animes_list):
            select_anime = animes_list[option - 1]
            print(f'Selected: {select_anime['name']}, {select_anime['link']}')
            print('\nProcessing...\n')

            episodes_list = get_links_episodes(select_anime['name'], select_anime['link'])

            for episode in episodes_list:
                download_list = get_downloads_links_episode(episode['link'])

                print(f'Episode: {episode["name"]}')

                for download in download_list:
                    print(download['download_url'])
                
                print('')
        else:
            print('Invalid option.')
    except ValueError:
        print('Only numbers are accepted.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="AnimeFLV Downloader")

    # Define un argumento opcional con dos versiones: larga (--search) y corta (-s)
    parser.add_argument('--search', '-s', type=str, help='Name anime to search')

    # Parsea los argumentos de la línea de comandos
    args = parser.parse_args()

    # Usa el valor del argumento si existe para buscar coincidencias
    if args.search:
        animes_list = search_anime(args.search)

        if len(animes_list) != 0:
            process_animes(animes_list)
        else:
            print('Anime not found.')
    else:
        print('No search term provided.')
