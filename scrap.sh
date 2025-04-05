URL="https://fr.investing.com/indices/france-40"

# Télécharge le contenu de la page en suivant les redirections
html=$(curl -sL "$URL")


prix=$(echo "$html" | pup 'div[data-test="instrument-price-last"] text{}' | tr -d '\n')
variation=$(echo "$html" | pup 'span[data-test="instrument-price-change-percent"] text{}' | tr -d '\n')
volume=$(echo "$html" | pup 'div[data-test="instrument-volume"] text{}' | tr -d '\n')

echo "Prix actuel : $prix"
echo "Variation  : $variation"
echo "Volume     : $volume"

