#!/bin/bash

# URL pour les données en temps réel
URL_REALTIME="https://fr.investing.com/indices/france-40"
USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
DATA_FILE="cac40_data.txt"

# === Scraping des données en temps réel ===
# Récupérer le HTML de la page en temps réel
html_realtime=$(curl -sL -H "User-Agent: $USER_AGENT" "$URL_REALTIME")

# Extraction du prix actuel et de la variation
# Supprimer les points (séparateurs de milliers) et remplacer la virgule décimale par un point
prix=$(echo "$html_realtime" | pup 'div[data-test="instrument-price-last"] text{}' | tr -d '\n' | sed 's/\.//g' | tr ',' '.')

# Extraction de la variation
var_abs=$(echo "$html_realtime" | pup 'span[data-test="instrument-price-change-value"] text{}' | tr -d '\n' | sed 's/\.//g' | tr ',' '.')
var_pct=$(echo "$html_realtime" | pup 'span[data-test="instrument-price-change-percent"] text{}' | tr -d '\n' | tr ',' '.')
if [ -n "$var_abs" ] && [ -n "$var_pct" ]; then
    variation="${var_abs} (${var_pct})"
else
    variation="$var_abs$var_pct"
fi

# Clôture précédente
cloture=$(echo "$html_realtime" | pup 'dd[data-test="prevClose"] span.key-info_dd-numeric__ZQFIs span text{}' | grep -E '[0-9]' | head -n1 | tr -d '\n' | sed 's/\.//g' | tr ',' '.')

# Ouverture
ouverture=$(echo "$html_realtime" | pup 'dd[data-test="open"] span.key-info_dd-numeric__ZQFIs span text{}' | grep -E '[0-9]' | head -n1 | tr -d '\n' | sed 's/\.//g' | tr ',' '.')

# Variation sur 1 an
variation1an=$(echo "$html_realtime" | pup 'dd[data-test="oneYearReturn"] span.key-info_dd-numeric__ZQFIs span text{}' | grep -E '[0-9,%.-]' | paste -sd "" - | tr -d '\n')

# Volume
volume=$(echo "$html_realtime" | pup 'dd[data-test="volume"] span.key-info_dd-numeric__ZQFIs span text{}' | grep -E '[0-9]' | head -n1 | tr -d '\n')

# Volume moyen (3m)
volumemoyen=$(echo "$html_realtime" | pup 'dd[data-test="avgVolume"] span.key-info_dd-numeric__ZQFIs span text{}' | grep -E '[0-9]' | head -n1 | tr -d '\n')

# Écart journalier
ecartjour=$(echo "$html_realtime" | pup 'dd[data-test="dailyRange"] span.key-info_dd-numeric__ZQFIs span text{}' | grep -E '[0-9,]' | paste -sd "-" - | tr -d '\n' | sed 's/\.//g' | tr ',' '.')

# Écart 52 semaines
ecart52=$(echo "$html_realtime" | pup 'dd[data-test="weekRange"] span.key-info_dd-numeric__ZQFIs span text{}' | grep -E '[0-9,]' | paste -sd "-" - | tr -d '\n' | sed 's/\.//g' | tr ',' '.')

# Sentiment technique
sentiment=$(echo "$html_realtime" | pup 'div.rounded-full.text-center.font-semibold text{}' | tr -d '\n')
if [ -z "$sentiment" ]; then
    sentiment="N/A"
fi

# Timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Valeurs par défaut si vide
[ -z "$prix" ] && prix="N/A"
[ -z "$variation" ] && variation="N/A"
[ -z "$cloture" ] && cloture="N/A"
[ -z "$ouverture" ] && ouverture="N/A"
[ -z "$variation1an" ] && variation1an="N/A"
[ -z "$volume" ] && volume="N/A"
[ -z "$volumemoyen" ] && volumemoyen="N/A"
[ -z "$ecartjour" ] && ecartjour="N/A"
[ -z "$ecart52" ] && ecart52="N/A"
[ -z "$sentiment" ] && sentiment="N/A"

# Enregistrer les données en temps réel dans cac40_data.txt (append)
echo "$TIMESTAMP,$prix,$variation,$cloture,$ouverture,$variation1an,$volume,$volumemoyen,$ecartjour,$ecart52,$sentiment" >> "$DATA_FILE"

# Affichage final des données en temps réel
echo "═══════════════════════════════════════"
echo "📊 Données CAC 40 - Investing.com"
echo "═══════════════════════════════════════"
echo "Prix actuel           : $prix"
echo "Variation             : $variation"
echo "Clôture précédente    : $cloture"
echo "Ouverture             : $ouverture"
echo "Variation sur 1 an    : $variation1an"
echo "Volume                : $volume"
echo "Volume moyen (3m)     : $volumemoyen"
echo "Écart journalier      : $ecartjour"
echo "Écart 52 sem.         : $ecart52"
echo "Sentiment technique   : $sentiment"
echo "═══════════════════════════════════════"
echo "Données en temps réel scrapées et sauvegardées dans $DATA_FILE"