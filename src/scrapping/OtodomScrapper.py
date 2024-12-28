from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from datetime import datetime

from ..files.FileAppender import FileAppender

import time

class OtoDomScrapper:
    """
    Handles all operation for scrapping 'otodom.pl' website.
    """
    __webdriver: WebDriver
    __file_name = "test_data"
    __apartments_list = []
    __lp = 1
    __last_page_number = 0
    __file_date = datetime.now()

    def execute(self):
        try:
            self.__initialize_driver()

            self.__go_to_website(1)
            time.sleep(3)
            self.__accept_cookies()
            self.__set_last_page_number()
            self.__apartments_list.extend(self.__get_data_from_site())

            for i in range(2, self.__last_page_number + 1):
                self.__go_to_website(i)
                self.__apartments_list.extend(self.__get_data_from_site())

        finally:
            self.__webdriver.quit()

    def __initialize_driver(self):
        """
        Initializes the webdriver.
        """
        download_service = Service()
        self.__webdriver = webdriver.Chrome(service=download_service)

    def __go_to_website(self, page: int):
        """
        Goes to the website.
        :param page: Number of page to go.
        """
        print(f"Going to page {page}")
        self.__webdriver.get(f"https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/mazowieckie/warszawa/warszawa/warszawa?viewType=listing&page={page}")

    def __accept_cookies(self):
        """
        Finds the accept button on the website.
        Clicks on the accept button to accept cookies.
        """
        accept_button = self.__webdriver.find_element(By.ID, "onetrust-accept-btn-handler")
        accept_button.click()

    def __set_last_page_number(self):
        """
        Sets the last page number as global variable.
        """
        pagination_items = self.__webdriver.find_elements(By.CSS_SELECTOR, 'ul[data-cy="frontend.search.base-pagination.nexus-pagination"] li')

        last_page_number = max(
            int(item.text) for item in pagination_items if item.text.isdigit()
        )

        print(f"Last page number: {last_page_number}")
        self.__last_page_number = last_page_number

    def __get_data_from_site(self):
        """
        Gets data about apartments from the website.
        """
        advertisements = self.__webdriver.find_elements(By.CSS_SELECTOR, 'article[data-cy="listing-item"]')
        apartments_list = []

        for advertisement in advertisements:
            try:
                # 'Title' probably will be not necessary
                title = advertisement.find_element(By.CSS_SELECTOR, '[data-cy="listing-item-title"]').text
                print(f"Gets data from advertisement: {self.__lp}. {title}")
                price = advertisement.find_element(By.CSS_SELECTOR, '.css-2bt9f1').text
                localization = advertisement.find_element(By.CSS_SELECTOR, '.css-42r2ms').text
                link = advertisement.find_element(By.CSS_SELECTOR, 'a[data-cy="listing-item-link"]').get_attribute('href')

                # Gets details about rooms, area, floor
                details = advertisement.find_elements(By.CSS_SELECTOR, '.css-12dsp7a dt')
                value = advertisement.find_elements(By.CSS_SELECTOR, '.css-12dsp7a dd')

                details_dict = {details.text: value.text for details, value in zip(details, value)}

                rooms_number = details_dict.get("Liczba pokoi", "Brak informacji")
                area = details_dict.get("Powierzchnia", "Brak informacji")
                floor = details_dict.get("Piętro", "Brak informacji")

                apartment = {
                    "lp": self.__lp,
                    "title": title,
                    "link": link,
                    "localization": localization,
                    "price": price,
                    "rooms_number": rooms_number,
                    "area": area,
                    "floor": floor,
                }

                self.__lp += 1
                apartments_list.append(apartment)

            except Exception as e:
                print(f"Błąd podczas przetwarzania ogłoszenia: {e}")

        FileAppender.append_data_as_csv(apartments_list, "apartments", self.__file_date)
        return apartments_list

    def get_list(self):
        """
        Returns apartments list.
        :return: Apartments list.
        """
        return self.__apartments_list