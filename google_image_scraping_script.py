from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import requests
import base64
import cv2

def chrome_driver():
    driver_path = f'{os.path.join(os.path.dirname(__file__), "chromedriver")}'
    service = Service(executable_path=driver_path)
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('headless')
    options.add_argument('--disable-gpu')
    options.add_argument('window-size=1920x1080')
    options.add_argument(
        'User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
    return webdriver.Chrome(service=service, options=options)


def search_images(driver, query):
    """
    Google 이미지 검색 실행
    """
    driver.get("https://www.google.com/imghp?hl=ko")
    (WebDriverWait(driver, 5)
     .until(EC.visibility_of_element_located((By.XPATH, '//*[@id="APjFqb"]'))))
    search_box = driver.find_element(By.XPATH,'//*[@id="APjFqb"]')
    search_box.send_keys(query)
    search_box.send_keys(Keys.ENTER)

def scroll_page(driver, scrolls=5, delay=2):
    """
    페이지를 스크롤 다운하여 더 많은 이미지 로드
    """
    for _ in range(scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay)


def collect_image_urls(driver, num_images):
    """
    수집된 이미지 URL 또는 Base64 데이터 추출
    """
    images = driver.find_elements(By.XPATH,'//*[@id="islrg"]/div[1]/div/a[1]/div[1]/img')
    image_urls = []
    for image in images:
        if len(image_urls) < num_images:
            image_url = image.get_attribute('src')
            if image_url and 'http' in image_url:
                image_urls.append(image_url)
            elif image_url and 'data:image' in image_url:
                header, encoded = image_url.split(",", 1)
                image_urls.append((header, encoded))
    return image_urls


def download_images(image_urls, folder_path='images'):
    """
    이미지 URL 또는 Base64 데이터를 파일로 다운로드
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    for i, url in enumerate(image_urls):
        try:
            if isinstance(url, tuple):
                # Base64로 인코딩된 이미지 처리
                header, encoded = url
                image_data = base64.b64decode(encoded)
                file_path = f"{folder_path}/image_{i + 1}.jpg"
                with open(file_path, "wb") as file:
                    file.write(image_data)
            else:
                # 일반 이미지 URL 처리
                response = requests.get(url)
                file_path = f"{folder_path}/image_{i + 1}.jpg"
                with open(file_path, "wb") as file:
                    file.write(response.content)
        except Exception as e:
            print(f"Error downloading {url}: {e}")



import os


def improve_image_quality(image_path, output_path, target_size=(640, 480)):
    """
    이미지의 해상도를 target_size로 변경하고 이미지의 품질을 개선합니다.
    """
    # 이미지를 읽고 지정된 해상도로 크기 조정
    img = cv2.imread(image_path)
    resized_img = cv2.resize(img, target_size, interpolation=cv2.INTER_LINEAR)

    # 선명도 개선을 위한 가우시안 블러 적용
    gaussian_blur = cv2.GaussianBlur(resized_img, (0, 0), 3)

    # cv2.addWeighted를 사용하여 원본 이미지와 가우시안 블러 이미지를 혼합
    sharpened_img = cv2.addWeighted(resized_img, 1.5, gaussian_blur, -0.5, 0)

    # 개선된 이미지 저장
    cv2.imwrite(output_path, sharpened_img)


def process_images(folder_path, output_folder, target_size=(640, 480)):
    """
    지정된 폴더 내의 모든 이미지에 대해 해상도 조정 및 품질 개선을 수행합니다.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('jpg', 'jpeg', 'png')):
            image_path = os.path.join(folder_path, filename)
            output_path = os.path.join(output_folder, f"improved_{filename}")
            improve_image_quality(image_path, output_path, target_size)






def main():
    search_query = "시드니"
    num_images = 100

    driver = chrome_driver()
    search_images(driver, search_query)
    scroll_page(driver)
    image_urls = collect_image_urls(driver, num_images)
    download_images(image_urls)
    driver.quit()
    # 예제 실행
    folder_path = './images'  # 원본 이미지가 위치한 폴더 경로
    output_folder = './process_images'  # 개선된 이미지를 저장할 폴더 경로
    process_images(folder_path, output_folder)

    print(f"{len(image_urls)} 다운로드 완료.")


if __name__ == "__main__":
    main()


