#!/usr/bin/env python3
"""
Générateur Prism.js pour WLangage à partir des fichiers JSON (données sources)
"""

import re

from common import (
    CSS_LIGHT, CSS_DARK,
    escape_for_regex, escape_operator_for_regex,
    load_json_safe, sort_and_escape, create_types_pattern,
    fold_accents,
    write_output
)

def create_prism_definition(keywords, functions, constants, operators, types, properties):
    # NOTE PERF / TAILLE - OPTIMISATION 1:
    # On utilise maintenant des patterns simples (sans classes de caractères [eéèêë])
    # et on applique le folding d'accents côté JavaScript via un hook.
    # Cela réduit considérablement la taille du fichier généré (~250 Ko de gain).

    # Keywords, constants, types, properties: patterns simples sans accents
    keywords_pattern = '|'.join(sort_and_escape(keywords))
    constants_pattern = '|'.join(sort_and_escape(constants))

    # Créer les maps pour le folding d'accents côté JS
    folded_keywords = sorted({fold_accents(kw) for kw in keywords})
    keywords_map_entries = ','.join(f'"{kw}":1' for kw in folded_keywords)

    folded_constants = sorted({fold_accents(c) for c in constants})
    constants_map_entries = ','.join(f'"{c}":1' for c in folded_constants)

    # Fonctions: on tokenise tous les appels avec 'user-function',
    # puis on requalifie ceux dont le nom (fold accents + lower) est présent dans
    # functions.json en 'function' via un hook Prism.
    folded_functions = sorted({fold_accents(fn).lower() for fn in functions})
    functions_map_entries = ','.join(f'"{fn}":1' for fn in folded_functions)

    # Types: pattern simple sans accents (le folding sera fait côté JS)
    types_pattern = create_types_pattern(types, normalize_accents=False)
    folded_types = sorted({fold_accents(re.sub(r's$', '', t)) for t in types})
    types_map_entries = ','.join(f'"{t}":1' for t in folded_types)

    operators_pattern = '|'.join(sort_and_escape(operators, escape_operator_for_regex))
    properties_pattern = '|'.join(sort_and_escape(properties))

    template = f'''/**
 * WLangage syntax highlighting for Prism.js
 * Mots-clés: {len(keywords)} | Fonctions: {len(functions)} | Constantes: {len(constants)} | Types: {len(types)} | Propriétés: {len(properties)}
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

	// Mots de visibilité (public, privé, protégé)
	'visibility': /(?:^|\\s)(?:public|priv[eé]|prot[eé]g[eé])(?:$|\\s)/i,

	// Lettre "à" ou "À" isolée (sera requalifiée en 'keyword' par le hook)
	'keyword-a': /(?<![\\p{{L}}\\p{{N}}_])[àÀ](?![\\p{{L}}\\p{{N}}_])/u,

	// Mots-clés du langage (case-sensitive, accent-insensitive via hook)
	'keyword': /\\b(?:{keywords_pattern})\\b/,

	// Déclaration de procédure
	'procedure': {{
		pattern: /procédure(?:\\s+(?:interne|constructeur|destructeur|virtuelle))?\\s+[\\p{{L}}\\p{{N}}_]+/iu,
		inside: {{
			'procedure-keyword': /procédure(?:\\s+(?:interne|constructeur|destructeur|virtuelle))?/i,
			'procedure-name': /\\b[\\p{{L}}\\p{{N}}_]+\\b$/u
		}}
	}},

	// Types de variables (case-sensitive, accent-insensitive via hook)
	'type': /\\b(?:{types_pattern})\\b/,

	// Constantes (case-sensitive, accent-insensitive via hook, doit être avant functions pour avoir la priorité)
	'constant': /\\b(?:{constants_pattern})\\b/,

	// Fonctions utilisateur (custom, commencent par une majuscule et ne sont pas dans functions.json)
	'user-function': /\\b[\\p{{Lu}}_][\\p{{L}}\\p{{N}}_]*\\b(?=\\s*\\()/iu,

	// Propriétés (après un accès membre '.' ou '..', y compris après des indexations [...] )
	// Note: on n'utilise pas \\b car il n'est pas Unicode-aware (ex: mots finissant par 'é').
	'property': /(?<=\\.\\.|\\.)(?:{properties_pattern})(?![\\p{{L}}\\p{{N}}_])/u,

	// Nombres (entiers et décimaux, négatifs inclus)
	'number': /-?\\b\\d+(?:\\.\\d+)?\\b/,

	// Opérateurs
	'operator': /(?:{operators_pattern})/,

	// Ponctuation
	'punctuation': /[(){{}}\\[\\],;:.]/
}};

// ---------------------------------------------------------------------------
// Accent-insensitive built-in elements (compact)
// ---------------------------------------------------------------------------
// Mots-clés, constantes, types et fonctions WL en version "sans accents".
// Exemple: "Chaîne" et "Chaine" => "chaine".
var WL_BUILTIN_KEYWORDS = {{{keywords_map_entries}}};
var WL_BUILTIN_CONSTANTS = {{{constants_map_entries}}};
var WL_BUILTIN_TYPES = {{{types_map_entries}}};
var WL_BUILTIN_FUNCTIONS = {{{functions_map_entries}}};

function wlFoldAccents(str) {{
	// mapping 1:1 (préserve la longueur)
	return str
		.replace(/[\u00E0\u00E2\u00E4\u00E1\u00E3\u00E5]/g, 'a')
		.replace(/[\u00C0\u00C2\u00C4\u00C1\u00C3\u00C5]/g, 'A')
		.replace(/[\u00E9\u00E8\u00EA\u00EB]/g, 'e')
		.replace(/[\u00C9\u00C8\u00CA\u00CB]/g, 'E')
		.replace(/[\u00EE\u00EF\u00ED\u00EC]/g, 'i')
		.replace(/[\u00CE\u00CF\u00CD\u00CC]/g, 'I')
		.replace(/[\u00F4\u00F6\u00F3\u00F2\u00F5]/g, 'o')
		.replace(/[\u00D4\u00D6\u00D3\u00D2\u00D5]/g, 'O')
		.replace(/[\u00F9\u00FB\u00FC\u00FA]/g, 'u')
		.replace(/[\u00D9\u00DB\u00DC\u00DA]/g, 'U')
		.replace(/[\u00FF\u00FD]/g, 'y')
		.replace(/[\u0178\u00DD]/g, 'Y')
		.replace(/\u00E7/g, 'c')
		.replace(/\u00C7/g, 'C');
}}

(function () {{
	if (typeof Prism === 'undefined' || !Prism.hooks) return;

	function transformToken(token) {{
		if (!token) return;
		if (Array.isArray(token)) {{
			for (var i = 0; i < token.length; i++) transformToken(token[i]);
			return;
		}}
		if (typeof token === 'object') {{
			var content = token.content;
			if (typeof content === 'string') {{
				var folded = wlFoldAccents(content);

				// Requalifier les types (avec gestion du singulier/pluriel)
				if (token.type === 'type') {{
					var typeBase = folded.replace(/s$/, '');
					if (WL_BUILTIN_TYPES[typeBase]) {{
						// Garder le type 'type' car c'est correct
					}} else {{
						// Ce n'est pas un type connu, le requalifier en texte normal
						token.type = undefined;
					}}
				}}
				// Requalifier les constantes
				else if (token.type === 'constant') {{
					if (!WL_BUILTIN_CONSTANTS[folded]) {{
						token.type = undefined;
					}}
				}}
				// Requalifier les mots-clés
				else if (token.type === 'keyword') {{
					if (!WL_BUILTIN_KEYWORDS[folded]) {{
						token.type = undefined;
					}}
				}}
				// Requalifier les fonctions utilisateur
				else if (token.type === 'user-function') {{
					var foldedLower = folded.toLowerCase();
					if (WL_BUILTIN_FUNCTIONS[foldedLower]) {{
						token.type = 'function';
					}}
				}}
				// Requalifier la lettre "à" isolée
				else if (token.type === 'keyword-a') {{
					token.type = 'keyword';
				}}
			}}
			transformToken(token.content);
		}}
	}}

	Prism.hooks.add('after-tokenize', function (env) {{
		if (!env || (env.language !== 'wlangage' && env.language !== 'wl')) return;
		transformToken(env.tokens);
	}});
}})();

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
        'properties': load_json_safe('properties.json'),
    }

    if not any(data.values()):
        print("Aucun fichier JSON trouvé ou chargé")
        print("Assurez-vous d'avoir les fichiers suivants dans le dossier data/:")
        print("   - keywords.json")
        print("   - functions.json")
        print("   - constants.json")
        print("   - operators.json")
        print("   - variable-types.json")
        print("   - properties.json")
        return

    print("Génération du fichier Prism.js...")
    prism_code = create_prism_definition(**data)
    write_output(prism_code, 'prism-wlangage.js')


if __name__ == '__main__':
    main()
