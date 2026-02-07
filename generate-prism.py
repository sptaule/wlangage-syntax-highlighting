#!/usr/bin/env python3
"""
Générateur Prism.js pour WLangage à partir des fichiers JSON
Gère correctement les accents et caractères Unicode
"""

import json
import re

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
    try:
        with open(filename, 'r', encoding='utf-8') as f:
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
        escaped = escape_for_regex(op)
        # Échappement supplémentaire pour certains caractères en JavaScript
        escaped = escaped.replace('?', '\\?')
        escaped = escaped.replace('+', '\\+')
        escaped = escaped.replace('*', '\\*')
        escaped = escaped.replace('|', '\\|')
        escaped = escaped.replace('/', '\\/')
        operators_escaped.append(escaped)

    # Créer les patterns
    keywords_pattern = '|'.join(keywords_escaped)
    functions_pattern = '|'.join(functions_escaped)
    constants_pattern = '|'.join(constants_escaped)
    types_pattern = '|'.join(types_patterns)
    operators_pattern = '|'.join(operators_escaped)

    # Template JavaScript
    template = f'''/**
 * WLangage syntax highlighting for Prism.js
 * Language: WLangage (WinDev, WebDev, WinDev Mobile)
 *
 * Auto-généré depuis les fichiers JSON
 * Mots-clés: {len(keywords)} | Fonctions: {len(functions)} | Constantes: {len(constants)} | Types: {len(types)}
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
	'keyword': /\\b(?:{keywords_pattern})\\b/i,

	// Déclaration de procédure
	'procedure': {{
		pattern: /procédure(?:\\s+(?:interne|constructeur|destructeur|virtuelle))?\\s+[\\p{{L}}\\p{{N}}_]+/iu,
		inside: {{
			'procedure-keyword': /procédure(?:\\s+(?:interne|constructeur|destructeur|virtuelle))?/i,
			'procedure-name': /\\b[\\p{{L}}\\p{{N}}_]+\\b$/u
		}}
	}},

	// Types de variables
	'type': /\\b(?:{types_pattern})\\b/i,

	// Constantes (doit être avant functions pour avoir la priorité)
	'constant': /\\b(?:{constants_pattern})\\b/i,

	// Fonctions natives (suivies d'une parenthèse ouvrante)
	'function': /\\b(?:{functions_pattern})\\b(?=\\s*\\()/i,

	// Nombres (entiers et décimaux, négatifs inclus)
	'number': /-?\\b\\d+(?:\\.\\d+)?\\b/,

	// Opérateurs
	'operator': /{operators_pattern}/,

	// Ponctuation
	'punctuation': /[(){{}}\\[\\],;:.]/
}};

// Alias pour compatibilité
Prism.languages.wl = Prism.languages.wlangage;

// Injection automatique des styles CSS pour WLangage
(function() {{
    var css = `
        /* Thème clair (par défaut) */
        .language-wlangage .token.keyword {{
            color: #000000;
            text-transform: uppercase;
        }}
        .language-wlangage .token.variable-assignment {{
            color: #555555;
        }}
        .language-wlangage .token.visibility {{
            color: #0066CC;
            font-weight: bold;
        }}
        .language-wlangage .token.procedure .procedure-keyword {{
            color: #000000;
            text-transform: uppercase;
        }}
        .language-wlangage .token.procedure .procedure-name {{
            color: #008080;
            font-weight: 600;
        }}
        .language-wlangage .token.function {{
            color: #0000FF;
        }}
        .language-wlangage .token.constant {{
            color: #0000FF;
            font-style: italic;
        }}
        .language-wlangage .token.type {{
            color: #5D00BA;
        }}
        .language-wlangage .token.operator {{
            color: #000000;
        }}
        .language-wlangage .token.number {{
            color: #800080;
        }}
        .language-wlangage .token.string {{
            color: #800080;
        }}
        .language-wlangage .token.comment {{
            color: #808080;
            font-style: italic;
        }}
        .language-wlangage .token.punctuation {{
            color: #000000;
        }}
        .language-wlangage .token.procedure-name {{
            color: #008080;
            font-weight: 600;
        }}

        /* Thème sombre */
        .dark-theme .language-wlangage .token.keyword {{
            color: #FF8000;
            text-transform: uppercase;
        }}
        .dark-theme .language-wlangage .token.variable-assignment {{
            color: #A6A8AB;
        }}
        .dark-theme .language-wlangage .token.visibility {{
            color: #4FC3F7;
            font-weight: bold;
        }}
        .dark-theme .language-wlangage .token.procedure .procedure-keyword {{
            color: #FF8000;
            text-transform: uppercase;
        }}
        .dark-theme .language-wlangage .token.procedure .procedure-name {{
            color: #009180;
            text-shadow: 0px 0px 4px rgba(0,145,128,0.3);
            font-weight: 600;
        }}
        .dark-theme .language-wlangage .token.function {{
            color: #91B5FE;
            text-shadow: 0px 0px 4px rgba(145,181,254,0.3);
        }}
        .dark-theme .language-wlangage .token.constant {{
            color: #B1C33A;
            font-style: italic;
        }}
        .dark-theme .language-wlangage .token.type {{
            color: #9575CD;
        }}
        .dark-theme .language-wlangage .token.operator {{
            color: #CDD3DE;
        }}
        .dark-theme .language-wlangage .token.number {{
            color: #BA68C8;
        }}
        .dark-theme .language-wlangage .token.string {{
            color: #BA68C8;
        }}
        .dark-theme .language-wlangage .token.comment {{
            color: #808080;
            font-style: italic;
        }}
        .dark-theme .language-wlangage .token.punctuation {{
            color: #CDD3DE;
        }}
        .dark-theme .language-wlangage .token.procedure-name {{
            color: #009180;
            font-weight: 600;
        }}
    `;
    var style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);
}})();
'''

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
        print("Assurez-vous d'avoir les fichiers suivants dans le même dossier:")
        print("   - keywords.json")
        print("   - functions.json")
        print("   - constants.json")
        print("   - operators.json")
        print("   - variable-types.json")
        return

    # Générer le code Prism.js
    print("Génération du fichier Prism.js...")
    prism_code = create_prism_definition(keywords, functions, constants, operators, types)

    # Sauvegarder
    output_file = 'prism-wlangage.js'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(prism_code)

    print(f"Fichier généré : {output_file}")
    print(f"Taille : {len(prism_code):,} caractères")

    # Générer la version minifiée si jsmin est disponible
    if MINIFY_AVAILABLE:
        minified_code = jsmin(prism_code)
        minified_file = 'prism-wlangage.min.js'
        with open(minified_file, 'w', encoding='utf-8') as f:
            f.write(minified_code)
        print(f"Fichier minifié généré : {minified_file}")
        print(f"Taille minifiée : {len(minified_code):,} caractères")
    else:
        print("jsmin non disponible, le fichier minifié n'a pas été généré.")
        print("Installez jsmin avec : pip install jsmin")

if __name__ == '__main__':
    main()
