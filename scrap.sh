URL="https://fr.investing.com/indices/france-40"
html=$(curl -sL "$URL")

# Extraction du prix actuel et de la variation (déjà fonctionnels)
prix=$(echo "$html" | pup 'div[data-test="instrument-price-last"] text{}' | tr -d '\n')
var_abs=$(echo "$html" | pup 'span[data-test="instrument-price-change-value"] text{}' | tr -d '\n')
var_pct=$(echo "$html" | pup 'span[data-test="instrument-price-change-percent"] text{}' | tr -d '\n')
if [ -n "$var_abs" ] && [ -n "$var_pct" ]; then
    variation="${var_abs} (${var_pct})"
else
    variation="$var_abs$var_pct"
fi

# Clôture précédente (data-test="prevClose")
cloture=$(echo "$html" | pup 'dd[data-test="prevClose"] span.key-info_dd-numeric__ZQFIs span text{}' | grep -E '[0-9]' | head -n1 | tr -d '\n')

# Ouverture (data-test="open")
ouverture=$(echo "$html" | pup 'dd[data-test="open"] span.key-info_dd-numeric__ZQFIs span text{}' | grep -E '[0-9]' | head -n1 | tr -d '\n')

# Variation sur 1 an (data-test="oneYearReturn")
# On récupère les spans contenant le nombre et le symbole %, puis on les joint
variation1an=$(echo "$html" | pup 'dd[data-test="oneYearReturn"] span.key-info_dd-numeric__ZQFIs span text{}' | grep -E '[0-9,%.-]' | paste -sd "" - | tr -d '\n')

# Volume (data-test="volume")
volume=$(echo "$html" | pup 'dd[data-test="volume"] span.key-info_dd-numeric__ZQFIs span text{}' | grep -E '[0-9]' | head -n1 | tr -d '\n')

# Volume moyen (3m) (data-test="avgVolume")
volumemoyen=$(echo "$html" | pup 'dd[data-test="avgVolume"] span.key-info_dd-numeric__ZQFIs span text{}' | grep -E '[0-9]' | head -n1 | tr -d '\n')

# Écart journalier (data-test="dailyRange")
# Deux valeurs séparées par un tiret (on joint les lignes récupérées)
ecartjour=$(echo "$html" | pup 'dd[data-test="dailyRange"] span.key-info_dd-numeric__ZQFIs span text{}' | grep -E '[0-9,]' | paste -sd "-" - | tr -d '\n')

# Écart 52 sem
ecart52=$(echo "$html" | pup 'dd[data-test="weekRange"] span.key-info_dd-numeric__ZQFIs span text{}' | grep -E '[0-9,]' | paste -sd "-" - | tr -d '\n')

# Sentiment technique
sentiment=$(echo "$html" | pup 'div.rounded-full.text-center.font-semibold text{}' | tr -d '\n')

# Affichage final
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
