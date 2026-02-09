#!/usr/bin/env python3
"""
Générateur Prism.js pour WLangage à partir des fichiers JSON (données sources)
"""

from common import (
    CSS_LIGHT, CSS_DARK,
    escape_for_regex, escape_operator_for_regex,
    load_json_safe, sort_and_escape, create_types_pattern,
    write_output
)

def create_prism_definition(keywords, functions, constants, operators, types):
    keywords_pattern = '|'.join(sort_and_escape(keywords))
    functions_pattern = '|'.join(sort_and_escape(functions))
    constants_pattern = '|'.join(sort_and_escape(constants))
    types_pattern = create_types_pattern(types)
    operators_pattern = '|'.join(sort_and_escape(operators, escape_operator_for_regex))

    template = f'''/**
 * WLangage syntax highlighting for Prism.js
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

	// Propriétés (après un nom de variable suivi d'un ou deux points)
	'property': /(?<=\\b[\\p{{L}}\\p{{N}}_]+(?:\\.\\.|\\.))[\\p{{L}}\\p{{N}}_]+/u,

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
    print("Chargement des fichiers JSON...")

    data = {
        'keywords': load_json_safe('keywords.json'),
        'functions': load_json_safe('functions.json'),
        'constants': load_json_safe('constants.json'),
        'operators': load_json_safe('operators.json'),
        'types': load_json_safe('variable-types.json'),
    }

    if not any(data.values()):
        print("Aucun fichier JSON trouvé ou chargé")
        print("Assurez-vous d'avoir les fichiers suivants dans le dossier data/:")
        print("   - keywords.json")
        print("   - functions.json")
        print("   - constants.json")
        print("   - operators.json")
        print("   - variable-types.json")
        return

    print("Génération du fichier Prism.js...")
    prism_code = create_prism_definition(**data)
    write_output(prism_code, 'prism-wlangage.js')


if __name__ == '__main__':
    main()
