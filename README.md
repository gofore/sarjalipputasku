# sarjalipputasku
Matkalipputasku VR:n sarjalipuille

# Dev-ympäristö
- Docker
  - Aja juuresta löytyvä docker-compose.yml (docker-compose up)

- Dev server
  - backend-hakemistosta löytyvällä manage.py -scriptillä, suositeltavaa käyttää
    virtuaalista ympäristöä (virtualenv)
    - apt-get install -y libldap2-dev libsasl2-dev poppler-utils
    - pip install requirements.txt (backend-hakemistossa)
    - export SARJALIPPUTASKU_CONFIGFILE=/path/to/sarjalipputasku/config/app.cfg (edit path)
    - python manage.py runserver
# Ominaisuukset
- Sarjalipun upload
  - Pyynnön käsittely
  - Lipun parsinta
    - Määränpäät
    - Luokka
    - Vanheneminen
- Lippujen haku
    - Lähtö- ja kohdeasemilla
    - Myöhempiin versioihin: voimassaoloajalla, lipputyypillä (eko/ekstra)
    - Haku palauttaa yhden hakuehtoihin sopivan lipun
- Lipun varaaminen
    - Lippu merkitään varatuksi, kun haku palauttaa sen
- Lipun käyttäminen
    - Käyttäjä voi merkitä lipun käytetyksi
- Myöhempiin versioihin: 
    - varauksen peruuttaminen
    - Älykäs haku
