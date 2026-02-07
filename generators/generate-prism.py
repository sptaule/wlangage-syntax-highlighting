#!/usr/bin/env python3
"""
Générateur Prism.js pour WLangage à partir des fichiers JSON (données sources)
"""

import json
import os
import re

# ============================================================================
# CONSTANTES DE STYLE CSS - Thème clair
# ============================================================================
CSS_LIGHT = {
    'code_color': '#008000',
    'keyword_color': '#000000',
    'variable_assignment_color': '#555555',
    'visibility_color': '#0066CC',
    'procedure_name_color': '#008080',
    'function_color': '#0000FF',
    'function_shadow': 'rgba(0,0,255,0.15)',
    'property_color': '#000000',
    'constant_color': '#0000FF',
    'type_color': '#5D00BA',
    'operator_color': '#000000',
    'number_color': '#800080',
    'string_color': '#800080',
    'comment_color': '#808080',
    'punctuation_color': '#000000',
}

# ============================================================================
# CONSTANTES DE STYLE CSS - Thème sombre
# ============================================================================
CSS_DARK = {
    'code_color': '#4CAF50',
    'keyword_color': '#FF8000',
    'variable_assignment_color': '#A6A8AB',
    'visibility_color': '#4FC3F7',
    'procedure_name_color': '#009180',
    'procedure_name_shadow': 'rgba(0,145,128,0.3)',
    'function_color': '#91B5FE',
    'function_shadow': 'rgba(145,181,254,0.3)',
    'property_color': '#CDD3DE',
    'constant_color': '#B1C33A',
    'type_color': '#9575CD',
    'operator_color': '#CDD3DE',
    'number_color': '#BA68C8',
    'string_color': '#BA68C8',
    'comment_color': '#808080',
    'punctuation_color': '#CDD3DE',
}

try:
    from jsmin import jsmin
    MINIFY_AVAILABLE = True
except ImportError:
    MINIFY_AVAILABLE = False

def escape_for_regex(text):
    """Échappe les caractères spéciaux pour une regex JavaScript"""
    # Caractères à échapper dans une regex
    special = r'\.^$*+?{}[]()|\\'
    result = ''
    for char in text:
        if char in special:
            result += '\\' + char
        else:
            result += char
    return result

def escape_operator_for_regex(op):
    """Échappe les caractères spéciaux pour un opérateur dans une regex JavaScript"""
    # Pour les opérateurs, on échappe tous les caractères spéciaux
    special = r'\.^$*+?{}[]()|\\/'
    result = ''
    for char in op:
        if char in special:
            result += '\\' + char
        else:
            result += char
    return result

def make_accent_insensitive(text):
    """Crée une regex insensible aux accents et à la casse"""
    mapping = {
        'a': '[aàâä]', 'à': '[aàâä]', 'â': '[aàâä]', 'ä': '[aàâä]',
        'e': '[eèéêë]', 'è': '[eèéêë]', 'é': '[eèéêë]', 'ê': '[eèéêë]', 'ë': '[eèéêë]',
        'i': '[iìíîï]', 'ì': '[iìíîï]', 'í': '[iìíîï]', 'î': '[iìíîï]', 'ï': '[iìíîï]',
        'o': '[oòóôö]', 'ò': '[oòóôö]', 'ó': '[oòóôö]', 'ô': '[oòóôö]', 'ö': '[oòóôö]',
        'u': '[uùúûü]', 'ù': '[uùúûü]', 'ú': '[uùúûü]', 'û': '[uùúûü]', 'ü': '[uùúûü]',
        'c': '[cç]', 'ç': '[cç]',
        'n': '[nñ]', 'ñ': '[nñ]',
        'y': '[yÿ]', 'ÿ': '[yÿ]',
        'A': '[AÀÂÄ]', 'À': '[AÀÂÄ]', 'Â': '[AÀÂÄ]', 'Ä': '[AÀÂÄ]',
        'E': '[EÈÉÊË]', 'È': '[EÈÉÊË]', 'É': '[EÈÉÊË]', 'Ê': '[EÈÉÊË]', 'Ë': '[EÈÉÊË]',
        'I': '[IÌÍÎÏ]', 'Ì': '[IÌÍÎÏ]', 'Í': '[IÌÍÎÏ]', 'Î': '[IÌÍÎÏ]', 'Ï': '[IÌÍÎÏ]',
        'O': '[OÒÓÔÖ]', 'Ò': '[OÒÓÔÖ]', 'Ó': '[OÒÓÔÖ]', 'Ô': '[OÒÓÔÖ]', 'Ö': '[OÒÓÔÖ]',
        'U': '[UÙÚÛÜ]', 'Ù': '[UÙÚÛÜ]', 'Ú': '[UÙÚÛÜ]', 'Û': '[UÙÚÛÜ]', 'Ü': '[UÙÚÛÜ]',
        'C': '[CÇ]', 'Ç': '[CÇ]',
        'N': '[NÑ]', 'Ñ': '[NÑ]',
        'Y': '[YŸ]', 'Ÿ': '[YŸ]',
    }
    result = ''
    for char in text:
        if char in mapping:
            result += mapping[char]
        else:
            result += re.escape(char)
    return result

def load_json_safe(filename):
    """Charge un fichier JSON de manière sécurisée"""
    # Construire le chemin vers le dossier data
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), 'data')
    filepath = os.path.join(data_dir, filename)

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

def create_prism_definition(keywords, functions, constants, operators, types):
    """Crée la définition Prism.js complète"""

    # Trier par longueur décroissante pour éviter les conflits
    keywords_sorted = sorted(keywords, key=len, reverse=True)
    functions_sorted = sorted(functions, key=len, reverse=True)
    constants_sorted = sorted(constants, key=len, reverse=True)
    types_sorted = sorted(types, key=len, reverse=True)

    # Échapper pour regex
    keywords_escaped = [escape_for_regex(k) for k in keywords_sorted]
    functions_escaped = [escape_for_regex(f) for f in functions_sorted]
    constants_escaped = [escape_for_regex(c) for c in constants_sorted]

    # Pour les types, on crée un pattern qui gère singulier/pluriel
    types_patterns = []
    processed_types = set()

    for t in types_sorted:
        # Éviter les doublons (singulier/pluriel)
        base = re.sub(r's$', '', t)
        if base not in processed_types:
            processed_types.add(base)
            # Créer un pattern avec s optionnel, insensible aux accents
            pattern = escape_for_regex(base) + 's?'
            types_patterns.append(pattern)

    # Opérateurs : trier par longueur et échapper
    operators_sorted = sorted(operators, key=len, reverse=True)
    operators_escaped = []
    for op in operators_sorted:
        # Utiliser la fonction spécifique pour les opérateurs
        escaped = escape_operator_for_regex(op)
        operators_escaped.append(escaped)

    # Créer les patterns
    keywords_pattern = '|'.join(keywords_escaped)
    functions_pattern = '|'.join(functions_escaped)
    constants_pattern = '|'.join(constants_escaped)
    types_pattern = '|'.join(types_patterns)
    # Pour les opérateurs, on ne les joint pas ici car on va les insérer directement
    operators_pattern = '|'.join(operators_escaped)

    # Template JavaScript - on utilise .format() pour éviter les problèmes d'échappement
    template = '''/**
 * WLangage syntax highlighting for Prism.js
 * Language: WLangage (WinDev, WebDev, WinDev Mobile)
 *
 * Auto-généré depuis les fichiers JSON
 * Mots-clés: {0} | Fonctions: {1} | Constantes: {2} | Types: {3}
 */

Prism.languages.wlangage = {{
	// Commentaires
	'comment': [
		{{
			pattern: /\\/\\/.*$/m,
			greedy: true
		}},
		{{
			pattern: /\\/\\*[\\s\\S]*?\\*\\//,
			greedy: true
		}}
	],

	// Chaînes de caractères (guillemets doubles)
	'string': {{
		pattern: /"(?:[^"\\\\]|\\\\.)*"/,
		greedy: true
	}},

	// Assignation de variables
	'variable-assignment': /\\b(?:est un|est une|sont des)\\b/i,

	// Mots de visibilité (public, privé, protégé, hérite de)
	'visibility': /(?:^|\\s)(?:public|priv[eé]|prot[eé]g[eé]|h[eé]rite de)(?:$|\\s)/i,

	// Mots-clés du langage
	'keyword': /\\b(?:{4})\\b/i,

	// Déclaration de procédure
	'procedure': {{
		pattern: /procédure(?:\\s+(?:interne|constructeur|destructeur|virtuelle))?\\s+[\\p{{L}}\\p{{N}}_]+/iu,
		inside: {{
			'procedure-keyword': /procédure(?:\\s+(?:interne|constructeur|destructeur|virtuelle))?/i,
			'procedure-name': /\\b[\\p{{L}}\\p{{N}}_]+\\b$/u
		}}
	}},

	// Types de variables
	'type': /\\b(?:{5})\\b/i,

	// Constantes (doit être avant functions pour avoir la priorité)
	'constant': /\\b(?:{6})\\b/i,

	// Fonctions natives (suivies d'une parenthèse ouvrante)
	'function': /\\b(?:{7})\\b(?=\\s*\\()/i,

	// Propriétés (après un nom de variable suivi d'un ou deux points)
	'property': /(?<=\\b[\\p{{L}}\\p{{N}}_]+(?:\\.\\.|\\.))[\\p{{L}}\\p{{N}}_]+/u,

	// Nombres (entiers et décimaux, négatifs inclus)
	'number': /-?\\b\\d+(?:\\.\\d+)?\\b/,

	// Opérateurs
	'operator': /(?:{8})/,

	// Ponctuation
	'punctuation': /[(){{}}\\[\\],;:.]/
}};

// Alias pour compatibilité
Prism.languages.wl = Prism.languages.wlangage;

// Injection automatique des styles CSS pour WLangage
(function() {{
    var style = document.createElement('style');
    style.textContent = `
        /* Thème clair (par défaut) */
        .light-theme code.language-wlangage {{ color: {9} !important; }}
        .language-wlangage .token.keyword,
        .language-wlangage .token.procedure .procedure-keyword {{
            color: {10};
            text-transform: uppercase;
        }}
        .language-wlangage .token.variable-assignment {{ color: {11}; }}
        .language-wlangage .token.visibility {{ color: {12}; font-weight: bold; }}
        .language-wlangage .token.procedure-name,
        .language-wlangage .token.procedure .procedure-name {{
            color: {13};
            font-weight: 600;
        }}
        .language-wlangage .token.function {{
            color: {14};
            text-shadow: 0px 0px 4px {15};
        }}
        .language-wlangage .token.property {{ color: {16}; }}
        .language-wlangage .token.constant {{ color: {17}; font-style: italic; }}
        .language-wlangage .token.type {{ color: {18}; }}
        .language-wlangage .token.operator {{ color: {19}; background-color: transparent; }}
        .language-wlangage .token.number,
        .language-wlangage .token.string {{ color: {20}; }}
        .language-wlangage .token.comment {{ color: {21}; font-style: italic; }}
        .language-wlangage .token.punctuation {{ color: {22}; }}

        /* Thème sombre */
        .dark-theme code.language-wlangage {{ color: {23} !important; }}
        .dark-theme .language-wlangage .token.keyword,
        .dark-theme .language-wlangage .token.procedure .procedure-keyword {{
            color: {24};
            text-transform: uppercase;
        }}
        .dark-theme .language-wlangage .token.variable-assignment {{ color: {25}; }}
        .dark-theme .language-wlangage .token.visibility {{ color: {26}; font-weight: bold; }}
        .dark-theme .language-wlangage .token.procedure-name,
        .dark-theme .language-wlangage .token.procedure .procedure-name {{
            color: {27};
            text-shadow: 0px 0px 4px {28};
            font-weight: 600;
        }}
        .dark-theme .language-wlangage .token.function {{
            color: {29};
            text-shadow: 0px 0px 4px {30};
        }}
        .dark-theme .language-wlangage .token.property {{ color: {31}; }}
        .dark-theme .language-wlangage .token.constant {{ color: {32}; font-style: italic; }}
        .dark-theme .language-wlangage .token.type {{ color: {33}; }}
        .dark-theme .language-wlangage .token.operator {{ color: {34}; background-color: transparent; }}
        .dark-theme .language-wlangage .token.number,
        .dark-theme .language-wlangage .token.string {{ color: {35}; }}
        .dark-theme .language-wlangage .token.comment {{ color: {36}; font-style: italic; }}
        .dark-theme .language-wlangage .token.punctuation {{ color: {37}; }}
    `;
    document.head.appendChild(style);
}})();
'''.format(
    len(keywords),
    len(functions),
    len(constants),
    len(types),
    keywords_pattern,
    types_pattern,
    constants_pattern,
    functions_pattern,
    operators_pattern,
    # Thème clair
    CSS_LIGHT['code_color'],
    CSS_LIGHT['keyword_color'],
    CSS_LIGHT['variable_assignment_color'],
    CSS_LIGHT['visibility_color'],
    CSS_LIGHT['procedure_name_color'],
    CSS_LIGHT['function_color'],
    CSS_LIGHT['function_shadow'],
    CSS_LIGHT['property_color'],
    CSS_LIGHT['constant_color'],
    CSS_LIGHT['type_color'],
    CSS_LIGHT['operator_color'],
    CSS_LIGHT['number_color'],
    CSS_LIGHT['comment_color'],
    CSS_LIGHT['punctuation_color'],
    # Thème sombre
    CSS_DARK['code_color'],
    CSS_DARK['keyword_color'],
    CSS_DARK['variable_assignment_color'],
    CSS_DARK['visibility_color'],
    CSS_DARK['procedure_name_color'],
    CSS_DARK['procedure_name_shadow'],
    CSS_DARK['function_color'],
    CSS_DARK['function_shadow'],
    CSS_DARK['property_color'],
    CSS_DARK['constant_color'],
    CSS_DARK['type_color'],
    CSS_DARK['operator_color'],
    CSS_DARK['number_color'],
    CSS_DARK['comment_color'],
    CSS_DARK['punctuation_color']
)

    return template

def main():
    """Fonction principale"""
    # Charger les fichiers JSON
    print("Chargement des fichiers JSON...")
    keywords = load_json_safe('keywords.json')
    functions = load_json_safe('functions.json')
    constants = load_json_safe('constants.json')
    operators = load_json_safe('operators.json')
    types = load_json_safe('variable-types.json')

    if not any([keywords, functions, constants, operators, types]):
        print("Aucun fichier JSON trouvé ou chargé")
        print("Assurez-vous d'avoir les fichiers suivants dans le dossier data/:")
        print("   - keywords.json")
        print("   - functions.json")
        print("   - constants.json")
        print("   - operators.json")
        print("   - variable-types.json")
        return

    # Générer le code Prism.js
    print("Génération du fichier Prism.js...")
    prism_code = create_prism_definition(keywords, functions, constants, operators, types)

    # Créer le dossier dist s'il n'existe pas
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(os.path.dirname(script_dir), 'dist')
    os.makedirs(dist_dir, exist_ok=True)

    # Sauvegarder dans le dossier dist
    output_file = os.path.join(dist_dir, 'prism-wlangage.js')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(prism_code)

    print(f"Fichier généré : {output_file}")
    print(f"Taille : {len(prism_code):,} caractères")

    # Générer la version minifiée si jsmin est disponible
    if MINIFY_AVAILABLE:
        minified_code = jsmin(prism_code)
        minified_file = os.path.join(dist_dir, 'prism-wlangage.min.js')
        with open(minified_file, 'w', encoding='utf-8') as f:
            f.write(minified_code)
        print(f"Fichier minifié généré : {minified_file}")
        print(f"Taille minifiée : {len(minified_code):,} caractères")
    else:
        print("jsmin non disponible, le fichier minifié n'a pas été généré.")
        print("Installez jsmin avec : pip install jsmin")

if __name__ == '__main__':
    main()
