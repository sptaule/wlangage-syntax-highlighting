/**
 * WLangage syntax highlighting for Prism.js - Version Light
 * Note: Ce fichier ne contient pas de CSS. Les couleurs sont gérées par les thèmes Prism.js.
 */

Prism.languages.wlangage = {
	// Commentaires
	'comment': [
		{
			pattern: /\/\/.*$/m,
			greedy: true
		},
		{
			pattern: /\/\*[\s\S]*?\*\//,
			greedy: true
		}
	],

	// Chaînes de caractères (guillemets doubles)
	'string': {
		pattern: /"(?:[^"\\]|\\.)*"/,
		greedy: true
	},

	// Assignation de variables (avec détection du type)
	'variable-assignment': {
		pattern: /\b(?:est un|est une|sont des)\s+[\p{L}\p{N}_]+/iu,
		inside: {
			'assignment-keyword': /\b(?:est un|est une|sont des)\b/i,
			'type': /\b[\p{L}\p{N}_]+\b$/u
		}
	},

	// Mots de visibilité (public, privé, protégé, hérite de)
	'visibility': /(?:^|\s)(?:public|priv[eé]|prot[eé]g[eé]|h[eé]rite de)(?:$|\s)/i,

	// Mots-clés du langage
	'keyword': /\b(?:POUR\ TOUTE\ LIGNE\ SÉLECTIONNÉE|POUR\ TOUTE\ POSITION|POUR\ TOUTE\ CHAINE|POUR\ TOUTE\ LIGNE|COMPILE\ SI|CONTINUER|POUR\ TOUT|POUR\ TOUS|RENVOYER|UTILISER|TANTQUE|AUTRES|BOUCLE|CLASSE|RETOUR|ALORS|APRES|AUTRE|FAIRE|LOCAL|SELON|SINON|AVEC|DANS|GOTO|POUR|SOIT|CAS|FIN|PAS|DE|SI)\b/i,

	// Déclaration de procédure
	'procedure': {
		pattern: /procédure(?:\s+(?:interne|constructeur|destructeur|virtuelle))?\s+[\p{L}\p{N}_]+/iu,
		inside: {
			'important': /procédure(?:\s+(?:interne|constructeur|destructeur|virtuelle))?/i,
			'procedure-name': /\b[\p{L}\p{N}_]+\b$/u
		}
	},

	// Éléments importants (procédures, types, visibilité)
	'important': [
		/\b(?:est un|est une|sont des)\s+[\p{L}\p{N}_]+/iu,
		/(?:^|\s)(?:public|priv[eé]|prot[eé]g[eé]|h[eé]rite de)(?:$|\s)/i
	],

	// Fonctions (détectées automatiquement par la parenthèse ouvrante)
	'function': /\b[\p{L}\p{N}_]+\b(?=\s*\()/iu,

	// Propriétés (après un nom de variable suivi d'un ou deux points)
	'property': /(?<=\b[\p{L}\p{N}_]+(?:\.\.|\.))[\p{L}\p{N}_]+/u,

	// Nombres (entiers et décimaux, négatifs inclus)
	'number': /-?\b\d+(?:\.\d+)?\b/,

	// Opérateurs
	'operator': /(?:\?\?=\*|<=>|\?\?\*|\?\?=|\+\+|--|\+=|-=|\|\||~=|<>|<=|>=|<-|\?!|\?\?|=|\+|\*|\/|-|%|\^|&|\||>|<)/,

	// Ponctuation
	'punctuation': /[(){}\[\],;:.]/
};

// Alias pour compatibilité
Prism.languages.wl = Prism.languages.wlangage;
