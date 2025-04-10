#!/usr/bin/env bash

# URL de la page à scraper
URL="https://fr.investing.com/indices/france-40"
html=$(curl -sL "$URL")

# Extraction du prix actuel
prix=$(echo "$html" | pup 'div[data-test="instrument-price-last"] text{}' | tr -d '\n')

# Extraction de la variation absolue et du pourcentage
var_abs=$(echo "$html" | pup 'span[data-test="instrument-price-change-value"] text{}' | tr -d '\n')
var_pct=$(echo "$html" | pup 'span[data-test="instrument-price-change-percent"] text{}' | tr -d '\n')

if [ -n "$var_abs" ] && [ -n "$var_pct" ]; then
    variation="${var_abs} (${var_pct})"
else
    variation="$var_abs$var_pct"
fi

# Extraction de la clôture précédente
cloture=$(echo "$html" \
  | pup 'dd[data-test="prevClose"] span.key-info_dd-numeric__ZQFIs span text{}' \
  | grep -E '[0-9]' \
  | head -n1 \
  | tr -d '\n')

# Extraction de l'ouverture
ouverture=$(echo "$html" \
  | pup 'dd[data-test="open"] span.key-info_dd-numeric__ZQFIs span text{}' \
  | grep -E '[0-9]' \
  | head -n1 \
  | tr -d '\n')

# Extraction de la variation sur 1 an (fusion des lignes récupérées)
variation1an=$(echo "$html" \
  | pup 'dd[data-test="oneYearReturn"] span.key-info_dd-numeric__ZQFIs span text{}' \
  | grep -E '[0-9,%.-]' \
  | paste -sd "" - \
  | tr -d '\n')

# Extraction du volume
volume=$(echo "$html" \
  | pup 'dd[data-test="volume"] span.key-info_dd-numeric__ZQFIs span text{}' \
  | grep -E '[0-9]' \
  | head -n1 \
  | tr -d '\n')

# Extraction du volume moyen (3m)
volumemoyen=$(echo "$html" \
  | pup 'dd[data-test="avgVolume"] span.key-info_dd-numeric__ZQFIs span text{}' \
  | grep -E '[0-9]' \
  | head -n1 \
  | tr -d '\n')

# Extraction de l'écart journalier (les valeurs jointes par un tiret)
ecartjour=$(echo "$html" \
  | pup 'dd[data-test="dailyRange"] span.key-info_dd-numeric__ZQFIs span text{}' \
  | grep -E '[0-9,]' \
  | paste -sd "-" - \
  | tr -d '\n')

# Extraction de l'écart sur 52 semaines
ecart52=$(echo "$html" \
  | pup 'dd[data-test="weekRange"] span.key-info_dd-numeric__ZQFIs span text{}' \
  | grep -E '[0-9,]' \
  | paste -sd "-" - \
  | tr -d '\n')

# Extraction du sentiment technique
sentiment=$(echo "$html" \
  | pup 'div.rounded-full.text-center.font-semibold text{}' \
  | tr -d '\n')

# Générer un timestamp (date et heure actuelles)
timestamp=$(date '+%Y-%m-%d %H:%M:%S')

# Création de la ligne CSV (séparateur ;)
csv_line="${timestamp};${prix};${variation};${cloture};${ouverture};${variation1an};${volume};${volumemoyen};${ecartjour};${ecart52};${sentiment}"

# Affichage détaillé dans la console
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

# Enregistrement dans un fichier CSV en insérant la nouvelle ligne en première position
temp_file=$(mktemp)
# On écrit la nouvelle ligne dans le fichier temporaire
echo "$csv_line" > "$temp_file"
# Si le fichier CSV existe déjà, on ajoute son contenu après la nouvelle ligne
if [ -f cac40_data.txt ]; then
    cat cac40_data.txt >> "$temp_file"
fi
# On remplace l'ancien fichier par le fichier temporaire
mv "$temp_file" cac40_data.txt
