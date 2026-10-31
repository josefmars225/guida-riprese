# guida-riprese

La guida alle riprese: la web app con cui i clienti filmano la propria casa dal telefono, passo dopo passo, per il video dell'immobile. I video arrivano da soli nel tuo Google Drive.

**La guida:** https://foretaste-riprese.github.io/

Per ogni cliente, aggiungi l'indirizzo dell'immobile al link, così i suoi video finiscono nella sua cartella:
`https://foretaste-riprese.github.io/?casa=Via Roma 12, Bologna`

## Come funziona

1. Il cliente apre il link dal telefono e segue la guida: setup, scelta dello spazio, un passo alla volta con pianta e vista in prima persona.
2. Ogni passo lo gira con l'app Fotocamera (4K, lente 0,5×), poi nella guida tocca **Scegli il video**.
3. La guida manda il video a pezzi direttamente nel tuo Drive mentre lui passa al passo successivo; se cade la connessione riprende da sola.

## Cosa c'è

- `index.html`: la guida, costruita da `tools/build.py`. Non va modificata a mano.
- `design/Main.dc.html`: la guida disegnata nel canvas di Claude, fonte di schermate, testi e animazioni.
- `src/`: il motore che fa girare il disegno come pagina (`shell.html`), l'adattamento allo schermo (`fit.js`) e l'invio dei video (`app.js`).
- `config.js`: l'indirizzo dello script Google che riceve i video.
- `apps-script/`: lo script da installare nel tuo account Google, con le istruzioni in [`apps-script/LEGGIMI.md`](apps-script/LEGGIMI.md).
- `media/`: prato, musica e mappe per l'effetto vetro.
- `prova-fotocamera/`: pagina di prova della fotocamera nel browser.

## Aggiornare la guida

Dopo aver cambiato `design/Main.dc.html` o `src/`:

```bash
python3 tools/build.py
```
