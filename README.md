# Projekt_OchronaDanych
### Mini-projekt zrealizowany w ramach przedmiotu "Ochrona danych w systemach informatycznych".

### Celem jest napisanie prostej aplikacji internetowej spełniającej wysokie standardy bezpieczeństwa.
***
Wykorzystane techniki zapewniajace odpowiedni poziom bezpieczenstwa:
* walidacja danych wejściowych (z negatywnym nastawieniem)
* limit nieudanych prób logowania (aby utrudnić zdalne zgadywanie i atak brute-force)
* bezpieczne przechowywanie hasła (wykorzystanie kryptograficznych funcji mieszających)
* kontrola siły hasła, aby uświadomić użytkownikowi problem
***
### Podstawowe wymagania zrealizowane w celu zapewnienia bezpieczenstwa:
* **(kluczowe)** restrykcyjna walidacja danych pochodzących z formularza login-hasło,
* **(kluczowe)** przechowywanie hasła chronione funkcją hash,
* **(kluczowe)** możliwość zmiany hasła,
* **(kluczowe)** możliwość odzyskania dostępu w przypadku utraty hasła,
* monitorowanie liczby nieudanych prób logowania,
* informowanie użytnownika o jakości jego hasła (jego entropii),
* kontrola odporności nowego hasła na ataki słownikowe.
