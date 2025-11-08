#!/bin/bash
# Script pour télécharger les données NIST directement

# Créer le répertoire de sortie
mkdir -p nist_data_raw

echo "=== Téléchargement des données NIST ==="
echo ""

# Liste des éléments (Z=1 à Z=92)
declare -A ELEMENTS=(
    [1]="H" [2]="He" [3]="Li" [4]="Be" [5]="B" [6]="C" [7]="N" [8]="O" [9]="F" [10]="Ne"
    [11]="Na" [12]="Mg" [13]="Al" [14]="Si" [15]="P" [16]="S" [17]="Cl" [18]="Ar" [19]="K" [20]="Ca"
    [21]="Sc" [22]="Ti" [23]="V" [24]="Cr" [25]="Mn" [26]="Fe" [27]="Co" [28]="Ni" [29]="Cu" [30]="Zn"
    [31]="Ga" [32]="Ge" [33]="As" [34]="Se" [35]="Br" [36]="Kr" [37]="Rb" [38]="Sr" [39]="Y" [40]="Zr"
    [41]="Nb" [42]="Mo" [43]="Tc" [44]="Ru" [45]="Rh" [46]="Pd" [47]="Ag" [48]="Cd" [49]="In" [50]="Sn"
    [51]="Sb" [52]="Te" [53]="I" [54]="Xe" [55]="Cs" [56]="Ba" [57]="La" [58]="Ce" [59]="Pr" [60]="Nd"
    [61]="Pm" [62]="Sm" [63]="Eu" [64]="Gd" [65]="Tb" [66]="Dy" [67]="Ho" [68]="Er" [69]="Tm" [70]="Yb"
    [71]="Lu" [72]="Hf" [73]="Ta" [74]="W" [75]="Re" [76]="Os" [77]="Ir" [78]="Pt" [79]="Au" [80]="Hg"
    [81]="Tl" [82]="Pb" [83]="Bi" [84]="Po" [85]="At" [86]="Rn" [87]="Fr" [88]="Ra" [89]="Ac" [90]="Th"
    [91]="Pa" [92]="U"
)

success=0
fail=0

# Essayer plusieurs patterns d'URL
for z in {1..92}; do
    z_padded=$(printf "%02d" $z)
    element="${ELEMENTS[$z]}"

    echo "Téléchargement des données pour $element (Z=$z)..."

    # Essayer différentes URLs possibles
    urls=(
        "https://physics.nist.gov/PhysRefData/XrayMassCoef/ElemTab/z${z_padded}.html"
        "https://physics.nist.gov/cgi-bin/XrayMassCoef/ElemTab/z${z_padded}"
        "https://www.nist.gov/pml/x-ray-mass-attenuation-coefficients/z${z_padded}"
    )

    downloaded=false
    for url in "${urls[@]}"; do
        wget -q --user-agent="Mozilla/5.0" -O "nist_data_raw/${element}_z${z_padded}.html" "$url" 2>/dev/null

        if [ $? -eq 0 ] && [ -s "nist_data_raw/${element}_z${z_padded}.html" ]; then
            echo "  ✓ Téléchargé depuis $url"
            ((success++))
            downloaded=true
            break
        fi
    done

    if [ "$downloaded" = false ]; then
        echo "  ✗ Échec du téléchargement"
        ((fail++))
        rm -f "nist_data_raw/${element}_z${z_padded}.html"
    fi

    sleep 0.5
done

echo ""
echo "=== Résumé ==="
echo "Succès: $success"
echo "Échecs: $fail"
echo "Total: 92"
