# FileShare
### Mini-projekt zrealizowany w ramach przedmiotu "Ochrona danych w systemach informatycznych", semestr V na Politechnice Warszawskiej. Celem było napisanie prostej aplikacji internetowej spełniającej wysokie standardy bezpieczeństwa.
***
Wykorzystane techniki zapewniajace odpowiedni poziom bezpieczenstwa:
* walidacja danych wejściowych (z negatywnym nastawieniem)
* limit nieudanych prób logowania (aby utrudnić zdalne zgadywanie i atak brute-force)
* bezpieczne przechowywanie hasła (wykorzystanie kryptograficznych funcji mieszających)
* kontrola siły hasła, aby uświadomić użytkownikowi problem
***
### Podstawowe wymagania zrealizowane w celu zapewnienia bezpieczenstwa:
* **(kluczowe)** restrykcyjna walidacja danych pochodzących z formularza login-hasło,
* **(kluczowe)** przechowywanie hasła chronione funkcją hash z solą,
* **(kluczowe)** możliwość umieszczenia na serwerze obrazków dostępnych prywatnie lub dla określonych użytkowni-
ków,
* **(kluczowe)** weryfikacja bezpieczeństwa przechowywanych plików graficznych,
* **(kluczowe)** zabezpieczenie transmisji poprzez wykorzystanie protokołu https,
* **(kluczowe)** możliwość zmiany hasła,
* **(kluczowe)** możliwość odzyskania dostępu w przypadku utraty hasła,

### Wymagania dodatkowe zrealizowane w celu zapewnienia bezpieczenstwa:
* monitorowanie liczby nieudanych prób logowania,
* informowanie użytnownika o jakości jego hasła (jego entropii),
* kontrola odporności nowego hasła na ataki słownikowe.

***
### Demo

#### Rejestracja
* niepoprawny email

![register_invalid_email](https://github.com/MichalZdanuk/Projekt_OD/assets/76063659/b85aeb14-edd5-4dce-b3b2-1ee18e49e3ce)

* próba wstrzyknięcia kodu (np. XSS injection)

![register_injection](https://github.com/MichalZdanuk/Projekt_OD/assets/76063659/a623c591-7ae6-4c84-ab25-7a93e372cb7b)

* zbyt słabe hasło

![register_too_weak_password](https://github.com/MichalZdanuk/Projekt_OD/assets/76063659/b5fc4696-8007-4747-a54f-b5d058db41aa)

* poprawna rejestracja

![register_success](https://github.com/MichalZdanuk/Projekt_OD/assets/76063659/099cdc43-4f19-4784-b5bf-40989c85c0f1)

#### Logowanie
* poprawne zalogowanie do serwisu

![login](https://github.com/MichalZdanuk/Projekt_OD/assets/76063659/d1ab59b7-899f-4da7-9dca-5f26d240dff6)

#### Uprawnienia prywatności
* dodanie uprawnień do naszych prywatnych zdjęć innemu użytkownikowi

![add_permission](https://github.com/MichalZdanuk/Projekt_OD/assets/76063659/2f60b43e-e4c4-4ae9-9b75-d6ed1e2b674a)

#### Zdjęcia
* dodanie publicznego zdjęcia

  ![add_img](https://github.com/MichalZdanuk/Projekt_OD/assets/76063659/f99fcde7-2c83-480e-935e-1a812f30f095)
