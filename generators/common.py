#!/usr/bin/env python3
"""
Module commun pour les générateurs Prism.js
"""

import json
import os
import re

try:
    from jsmin import jsmin
    MINIFY_AVAILABLE = True
except ImportError:
    MINIFY_AVAILABLE = False


# ============================================================================
# CONSTANTES DE STYLE CSS
# ============================================================================
CSS_LIGHT = {
    'code_color': '#008000',
    'keyword_color': '#000000',
    'variable_assignment_color': '#555555',
    'visibility_color': '#0066CC',
    'procedure_name_color': '#008080',
    'function_color': '#0000FF',
    'function_shadow': 'rgba(0,0,255,0.15)',
    'user_function_color': '#FF6600',
    'user_function_shadow': 'rgba(255,102,0,0.15)',
    'property_color': '#000000',
    'constant_color': '#0000FF',
    'type_color': '#5D00BA',
    'operator_color': '#000000',
    'number_color': '#800080',
    'string_color': '#800080',
    'comment_color': '#808080',
    'punctuation_color': '#000000',
}

CSS_DARK = {
    'code_color': '#4CAF50',
    'keyword_color': '#FF8000',
    'variable_assignment_color': '#A6A8AB',
    'visibility_color': '#4FC3F7',
    'procedure_name_color': '#009180',
    'procedure_name_shadow': 'rgba(0,145,128,0.3)',
    'function_color': '#91B5FE',
    'function_shadow': 'rgba(145,181,254,0.3)',
    'user_function_color': '#FFB74D',
    'user_function_shadow': 'rgba(255,183,77,0.3)',
    'property_color': '#CDD3DE',
    'constant_color': '#B1C33A',
    'type_color': '#9575CD',
    'operator_color': '#CDD3DE',
    'number_color': '#BA68C8',
    'string_color': '#BA68C8',
    'comment_color': '#808080',
    'punctuation_color': '#CDD3DE',
}


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================
def escape_for_regex(text):
    """Échappe les caractères spéciaux pour une regex JavaScript"""
    return re.escape(text)


# =========================================================================
# NORMALISATION DES ACCENTS ("accent folding")
# =========================================================================
# Objectif: rendre la tokenisation insensible aux accents SANS générer des
# patterns énormes du type [eéèêë] pour chaque lettre.
#
# On fait un mapping 1:1 (un caractère -> un caractère) pour garantir que la
# longueur du code reste identique, ce qui permet de restaurer le texte original
# après la tokenisation côté JS.
_ACCENT_FOLD_MAP = {
    # a
    **{ord(c): 'a' for c in 'àâäáãå'},
    **{ord(c): 'A' for c in 'ÀÂÄÁÃÅ'},
    # e
    **{ord(c): 'e' for c in 'éèêë'},
    **{ord(c): 'E' for c in 'ÉÈÊË'},
    # i
    **{ord(c): 'i' for c in 'îïíì'},
    **{ord(c): 'I' for c in 'ÎÏÍÌ'},
    # o
    **{ord(c): 'o' for c in 'ôöóòõ'},
    **{ord(c): 'O' for c in 'ÔÖÓÒÕ'},
    # u
    **{ord(c): 'u' for c in 'ùûüú'},
    **{ord(c): 'U' for c in 'ÙÛÜÚ'},
    # y
    **{ord(c): 'y' for c in 'ÿý'},
    **{ord(c): 'Y' for c in 'ŸÝ'},
    # c
    ord('ç'): 'c',
    ord('Ç'): 'C',
}


def fold_accents(text: str) -> str:
    """Supprime les accents via un mapping 1:1 (préserve la longueur)."""
    return text.translate(_ACCENT_FOLD_MAP)


def normalize_accents_for_regex(text):
    """
    Normalise les accents dans un texte pour créer un pattern regex qui matche
    les variantes avec et sans accents.

    Exemple: "Chaine" -> "Ch[aeî]n[eé]"
    """
    # Mapping des caractères avec leurs variantes accentuées
    accent_map = {
        'a': 'aàâä',
        'e': 'eéèêë',
        'i': 'iîï',
        'o': 'oôö',
        'u': 'uùûü',
        'c': 'cç',
        'y': 'yÿ',
    }

    result = []
    i = 0
    while i < len(text):
        char = text[i].lower()
        if char in accent_map:
            # Créer une classe de caractères [variantes]
            # On garde la casse originale pour le premier caractère
            variants = accent_map[char]
            if text[i].isupper():
                # Si le caractère original est majuscule, on met les variantes en majuscule aussi
                variants = ''.join(v.upper() for v in variants)
            result.append(f'[{variants}]')
        else:
            # Échapper les caractères spéciaux regex
            result.append(re.escape(text[i]))
        i += 1

    return ''.join(result)


def escape_operator_for_regex(op):
    """Échappe les caractères spéciaux pour un opérateur dans une regex JavaScript"""
    return ''.join('\\' + char if char in r'\.^$*+?{}[]()|\\/' else char for char in op)


def load_json_safe(filename):
    """Charge un fichier JSON de manière sécurisée"""
    filepath = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'data',
        filename
    )

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"{filename}: {len(data)} éléments chargés")
            return data
    except FileNotFoundError:
        print(f"{filename} non trouvé")
        return []
    except Exception as e:
        print(f"Erreur avec {filename}: {e}")
        return []


def sort_and_escape(items, escape_func=escape_for_regex, normalize_accents=False, fold_accents_items=False):
    """
    Trie les éléments par longueur décroissante et les échappe pour regex

    Args:
        items: Liste des éléments à traiter
        escape_func: Fonction d'échappement à utiliser
        normalize_accents: Si True, normalise les accents pour matcher les variantes
        fold_accents_items: Si True, remplace les caractères accentués par leur
            version non accentuée (1:1), pour générer des patterns plus compacts.
    """
    processed_items = items
    if fold_accents_items:
        # Dédoublonnage après folding (sinon patterns inutiles)
        processed_items = list({fold_accents(item) for item in items})

    sorted_items = sorted(processed_items, key=len, reverse=True)

    if normalize_accents:
        return [normalize_accents_for_regex(item) for item in sorted_items]
    return [escape_func(item) for item in sorted_items]


def create_types_pattern(types, normalize_accents=False):
    """Crée un pattern regex pour les types avec gestion du singulier/pluriel"""
    processed = set()
    patterns = []

    for t in sorted(types, key=len, reverse=True):
        base = re.sub(r's$', '', t)
        if base not in processed:
            processed.add(base)
            if normalize_accents:
                patterns.append(normalize_accents_for_regex(base) + 's?')
            else:
                patterns.append(escape_for_regex(base) + 's?')

    return '|'.join(patterns)


def get_output_path(filename):
    """Retourne le chemin complet du fichier de sortie dans le dossier dist"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(os.path.dirname(script_dir), 'dist')
    os.makedirs(dist_dir, exist_ok=True)
    return os.path.join(dist_dir, filename)


def write_output(content, filename):
    """Écrit le contenu dans un fichier et affiche des informations"""
    filepath = get_output_path(filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Fichier généré : {filepath}")
    print(f"Taille : {len(content):,} caractères")

    # Générer la version minifiée si jsmin est disponible
    if MINIFY_AVAILABLE:
        minified_code = jsmin(content)
        minified_path = get_output_path(filename.replace('.js', '.min.js'))
        with open(minified_path, 'w', encoding='utf-8') as f:
            f.write(minified_code)
        print(f"Fichier minifié généré : {minified_path}")
        print(f"Taille minifiée : {len(minified_code):,} caractères")
    else:
        print("jsmin non disponible, le fichier minifié n'a pas été généré.")
        print("Installez jsmin avec : pip install jsmin")
