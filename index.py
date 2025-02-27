import whois
from datetime import datetime
from termcolor import colored
import os
import time
import google.generativeai as genai

# Funkcja do zczytywania tokena z pliku key.conf
def get_api_key(config_file="key.conf"):
    try:
        with open(config_file, "r") as file:
            for line in file:
                if line.strip().startswith("api_key="):  # Przykład - zakładając, że linia z tokenem zaczyna się od 'api_key='
                    return line.split("=")[1].strip()  # Zwracamy token, usuwając białe znaki
    except FileNotFoundError:
        print(f"Błąd: Plik {config_file} nie został znaleziony.")
        return None
    except Exception as e:
        print(f"Błąd: {e}")
        return None

# Wczytanie klucza API z pliku konfiguracyjnego
api_key = get_api_key("key.conf")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("Unable to configure API - no token")
    exit(1)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def parse_config(file_path):
    domains, tlds = [], []
    with open(file_path, "r") as file:
        section = None
        for line in file:
            line = line.strip()
            if line == "[d]":
                section = "domains"
            elif line == "[tld]":
                section = "tlds"
            elif line and section:
                if section == "domains":
                    domains.append(line)
                elif section == "tlds":
                    tlds.append(line)
    return domains, tlds

def generate_domains(keywords, tlds):
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"Generate a list of 10 creative domain names based on these keywords: {', '.join(keywords)}. Exclude spaces and special characters. Write only domains without anything else. Split domains with next line. Dont generate too long names"

    response = model.generate_content(prompt)

    # Debugowanie - wyświetlanie odpowiedzi
    print("Response from API:", response)

    if response and hasattr(response, 'candidates') and len(response.candidates) > 0:
        # Zmiana na odpowiednią strukturę
        content = response.candidates[0].content
        if hasattr(content, 'parts') and len(content.parts) > 0:
            # Pobranie tekstu z pierwszego elementu 'parts'
            generated_domains = content.parts[0].text.split("\n")

            # Usuwamy TLD (jeśli istnieje) z generowanych domen
            domains_without_tld = [domain.split(".")[0].strip().lower() for domain in generated_domains if domain.strip()]
            return domains_without_tld
        else:
            print("Cannot find 'parts' field in response")
            return []
    else:
        print("Error during generating domains")
        return []


def check_domain_availability(domains, tlds):
    available, unavailable = [], []
    expiration_dates = {}

    clear_screen()
    print("Checking domains...\n")

    for domain in domains:
        for tld in tlds:
            full_domain = f"{domain}.{tld}"
            try:
                domain_info = whois.whois(full_domain)
                registrar = domain_info.registrar

                if registrar is None:
                    available.append(full_domain)
                    print(colored(f"{full_domain} - available - N/A", "green"))
                    continue

                if isinstance(domain_info.expiration_date, list):
                    expiration_date = max(domain_info.expiration_date) if domain_info.expiration_date else None
                else:
                    expiration_date = domain_info.expiration_date if domain_info.expiration_date else None

                if expiration_date:
                    unavailable.append(full_domain)
                    expiration_dates[full_domain] = expiration_date
                    print(colored(f"{full_domain} - unavailable - {expiration_date.strftime('%Y-%m-%d')}", "red"))
                else:
                    unavailable.append(full_domain)
                    expiration_dates[full_domain] = "N/A"
                    print(colored(f"{full_domain} - unavailable - N/A", "red"))
            except whois.parser.PywhoisError:
                available.append(full_domain)
                print(colored(f"{full_domain} - available - N/A", "green"))

    unavailable.sort(key=lambda d: expiration_dates.get(d, datetime.max) if isinstance(expiration_dates.get(d), datetime) else datetime.max)
    return available, unavailable, expiration_dates

def main():
    clear_screen()
    print("1. Sprawdzenie domen z domains.conf")
    print("2. Generowanie domen i ich sprawdzenie")
    choice = input("Wybierz opcję (1/2): ")

    domains, tlds = parse_config("domains.conf")

    if choice == "2":
        keywords = input("Podaj słowa kluczowe oddzielone przecinkami: ").split(",")
        domains = generate_domains(keywords, tlds)

    available, unavailable, expiration_dates = check_domain_availability(domains, tlds)

    print("\nPreparing summary...")
    time.sleep(5)
    clear_screen()

    print("Summary:")
    print("Available domains:")
    for domain in available:
        print(colored(f" - {domain}", "green"))

    print("\nUnavaiable domains (sorted by expiration date):")
    for domain in unavailable:
        print(colored(f" - {domain} - {expiration_dates.get(domain, 'N/A')}", "red"))

if __name__ == "__main__":
    main()
