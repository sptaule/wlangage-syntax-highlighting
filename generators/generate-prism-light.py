#!/usr/bin/env python3
"""
Générateur Prism.js pour WLangage - Version Light
"""

import json
import os
import re

try:
    from jsmin import jsmin
    MINIFY_AVAILABLE = True
except ImportError:
    MINIFY_AVAILABLE = False

def escape_for_regex(text):
    """Échappe les caractères spéciaux pour une regex JavaScript"""
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
    special = r'\.^$*+?{}[]()|\\/'
    result = ''
    for char in op:
        if char in special:
            result += '\\' + char
        else:
            result += char
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

def create_prism_definition(keywords, operators):
    """Crée la définition Prism.js complète (version light)"""

    # Trier par longueur décroissante pour éviter les conflits
    keywords_sorted = sorted(keywords, key=len, reverse=True)

    # Échapper pour regex
    keywords_escaped = [escape_for_regex(k) for k in keywords_sorted]

    # Opérateurs : trier par longueur et échapper
    operators_sorted = sorted(operators, key=len, reverse=True)
    operators_escaped = []
    for op in operators_sorted:
        escaped = escape_operator_for_regex(op)
        operators_escaped.append(escaped)

    # Créer les patterns
    keywords_pattern = '|'.join(keywords_escaped)
    operators_pattern = '|'.join(operators_escaped)

    # Template JavaScript - version light (sans CSS)
    template = '''/**
 * WLangage syntax highlighting for Prism.js - Version Light
 * Language: WLangage (WinDev, WebDev, WinDev Mobile)
 *
 * Auto-généré depuis les fichiers JSON (sans functions.json, constants.json ni variable-types.json)
 * Mots-clés: {0}
 * Les fonctions sont détectées automatiquement par la présence d'une parenthèse ouvrante
 * Les types sont détectés automatiquement par les mots-clés "est un", "est une" ou "sont des"
 *
 * Note: Ce fichier ne contient pas de CSS. Les couleurs sont gérées par les thèmes Prism.js.
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

	// Assignation de variables (avec détection du type)
	'variable-assignment': {{
		pattern: /\\b(?:est un|est une|sont des)\\s+[\\p{{L}}\\p{{N}}_]+/iu,
		inside: {{
			'assignment-keyword': /\\b(?:est un|est une|sont des)\\b/i,
			'type': /\\b[\\p{{L}}\\p{{N}}_]+\\b$/u
		}}
	}},

	// Mots de visibilité (public, privé, protégé, hérite de)
	'visibility': /(?:^|\\s)(?:public|priv[eé]|prot[eé]g[eé]|h[eé]rite de)(?:$|\\s)/i,

	// Mots-clés du langage
	'keyword': /\\b(?:{1})\\b/i,

	// Déclaration de procédure
	'procedure': {{
		pattern: /procédure(?:\\s+(?:interne|constructeur|destructeur|virtuelle))?\\s+[\\p{{L}}\\p{{N}}_]+/iu,
		inside: {{
			'procedure-keyword': /procédure(?:\\s+(?:interne|constructeur|destructeur|virtuelle))?/i,
			'procedure-name': /\\b[\\p{{L}}\\p{{N}}_]+\\b$/u
		}}
	}},

	// Fonctions (détectées automatiquement par la parenthèse ouvrante)
	'function': /\\b[\\p{{L}}\\p{{N}}_]+\\b(?=\\s*\\()/iu,

	// Propriétés (après un nom de variable suivi d'un ou deux points)
	'property': /(?<=\\b[\\p{{L}}\\p{{N}}_]+(?:\\.\\.|\\.))[\\p{{L}}\\p{{N}}_]+/u,

	// Nombres (entiers et décimaux, négatifs inclus)
	'number': /-?\\b\\d+(?:\\.\\d+)?\\b/,

	// Opérateurs
	'operator': /(?:{2})/,

	// Ponctuation
	'punctuation': /[(){{}}\\[\\],;:.]/
}};

// Alias pour compatibilité
Prism.languages.wl = Prism.languages.wlangage;
'''.format(
    len(keywords),
    keywords_pattern,
    operators_pattern
)

    return template

def main():
    """Fonction principale"""
    # Charger les fichiers JSON (sans functions.json, constants.json ni variable-types.json)
    print("Chargement des fichiers JSON (version light)...")
    keywords = load_json_safe('keywords.json')
    operators = load_json_safe('operators.json')

    if not any([keywords, operators]):
        print("Aucun fichier JSON trouvé ou chargé")
        print("Assurez-vous d'avoir les fichiers suivants dans le dossier data/:")
        print("   - keywords.json")
        print("   - operators.json")
        print("\nNote: functions.json, constants.json et variable-types.json ne sont pas utilisés dans cette version light.")
        return

    # Générer le code Prism.js
    print("Génération du fichier Prism.js (version light)...")
    prism_code = create_prism_definition(keywords, operators)

    # Créer le dossier dist s'il n'existe pas
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(os.path.dirname(script_dir), 'dist')
    os.makedirs(dist_dir, exist_ok=True)

    # Sauvegarder dans le dossier dist
    output_file = os.path.join(dist_dir, 'prism-wlangage-light.js')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(prism_code)

    print(f"Fichier généré : {output_file}")
    print(f"Taille : {len(prism_code):,} caractères")

    # Générer la version minifiée si jsmin est disponible
    if MINIFY_AVAILABLE:
        minified_code = jsmin(prism_code)
        minified_file = os.path.join(dist_dir, 'prism-wlangage-light.min.js')
        with open(minified_file, 'w', encoding='utf-8') as f:
            f.write(minified_code)
        print(f"Fichier minifié généré : {minified_file}")
        print(f"Taille minifiée : {len(minified_code):,} caractères")
    else:
        print("jsmin non disponible, le fichier minifié n'a pas été généré.")
        print("Installez jsmin avec : pip install jsmin")

if __name__ == '__main__':
    main()
