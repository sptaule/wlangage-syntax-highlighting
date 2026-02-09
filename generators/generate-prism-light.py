#!/usr/bin/env python3
"""
Générateur Prism.js pour WLangage - Version Light
"""

from common import (
    escape_for_regex, escape_operator_for_regex,
    load_json_safe, sort_and_escape, write_output
)

def create_prism_definition(keywords, operators):
    keywords_pattern = '|'.join(sort_and_escape(keywords))
    operators_pattern = '|'.join(sort_and_escape(operators, escape_operator_for_regex))

    template = f'''/**
 * WLangage syntax highlighting for Prism.js - Version Light
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
	'keyword': /\\b(?:{keywords_pattern})\\b/i,

	// Déclaration de procédure
	'procedure': {{
		pattern: /procédure(?:\\s+(?:interne|constructeur|destructeur|virtuelle))?\\s+[\\p{{L}}\\p{{N}}_]+/iu,
		inside: {{
			'important': /procédure(?:\\s+(?:interne|constructeur|destructeur|virtuelle))?/i,
			'procedure-name': /\\b[\\p{{L}}\\p{{N}}_]+\\b$/u
		}}
	}},

	// Éléments importants (procédures, types, visibilité)
	'important': [
		/\\b(?:est un|est une|sont des)\\s+[\\p{{L}}\\p{{N}}_]+/iu,
		/(?:^|\\s)(?:public|priv[eé]|prot[eé]g[eé]|h[eé]rite de)(?:$|\\s)/i
	],

	// Fonctions (détectées automatiquement par la parenthèse ouvrante)
	'function': /\\b[\\p{{L}}\\p{{N}}_]+\\b(?=\\s*\\()/iu,

	// Propriétés (après un accès membre '.' ou '..', y compris après des indexations [...] )
	// Note: on n'utilise pas \\b car il n'est pas Unicode-aware (ex: mots finissant par 'é').
	'property': /(?<=\\.\\.|\\.)[\\p{{L}}\\p{{N}}_]+(?![\\p{{L}}\\p{{N}}_])/u,

	// Nombres (entiers et décimaux, négatifs inclus)
	'number': /-?\\b\\d+(?:\\.\\d+)?\\b/,

	// Opérateurs
	'operator': /(?:{operators_pattern})/,

	// Ponctuation
	'punctuation': /[(){{}}\\[\\],;:.]/
}};

// Alias pour compatibilité
Prism.languages.wl = Prism.languages.wlangage;
'''

    return template

def main():
    print("Chargement des fichiers JSON (version light)...")

    data = {
        'keywords': load_json_safe('keywords.json'),
        'operators': load_json_safe('operators.json'),
    }

    if not any(data.values()):
        print("Aucun fichier JSON trouvé ou chargé")
        print("Assurez-vous d'avoir les fichiers suivants dans le dossier data/:")
        print("   - keywords.json")
        print("   - operators.json")
        print("\nNote: functions.json, constants.json et variable-types.json ne sont pas utilisés dans cette version light.")
        return

    print("Génération du fichier Prism.js (version light)...")
    prism_code = create_prism_definition(**data)
    write_output(prism_code, 'prism-wlangage-light.js')


if __name__ == '__main__':
    main()
