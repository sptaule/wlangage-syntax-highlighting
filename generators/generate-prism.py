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
    """Crée la définition Prism.js complète"""

    # Préparer les patterns
    keywords_pattern = '|'.join(sort_and_escape(keywords))
    functions_pattern = '|'.join(sort_and_escape(functions))
    constants_pattern = '|'.join(sort_and_escape(constants))
    types_pattern = create_types_pattern(types)
    operators_pattern = '|'.join(sort_and_escape(operators, escape_operator_for_regex))

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
    print("Chargement des fichiers JSON...")

    # Charger tous les fichiers JSON
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

    # Générer et sauvegarder le code Prism.js
    print("Génération du fichier Prism.js...")
    prism_code = create_prism_definition(**data)
    write_output(prism_code, 'prism-wlangage.js')


if __name__ == '__main__':
    main()
