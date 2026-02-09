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
	'keyword': /\b(?:POUR\ TOUTE\ LIGNE\ SÉLECTIONNÉE|POUR\ TOUTE\ POSITION|POUR\ TOUTE\ CHAÎNE|SANSSAUVEPOSITION|POUR\ TOUTE\ LIGNE|EN\ PROFONDEUR|ALLOUER\ UNE|POUR\ CHAQUE|SÉPARÉE\ PAR|ALLOUER\ UN|COMPILE\ SI|ABSTRAITE|CONSTANTE|CONTINUER|DEPUISFIN|HÉRITE\ DE|POUR\ TOUT|POUR\ TOUS|sérialise|SÉRIALISE|VIRTUELLE|CONSTANT|CONTINUE|IMMUABLE|RENVOYER|UTILISER|LIBÉRER|TANTQUE|AUTRES|BOUCLE|CLASSE|Classe|_DANS_|GLOBAL|RETOUR|SORTIR|ALORS|APRES|AUTRE|FAIRE|LOCAL|SELON|SINON|AVEC|DANS|_ET_|GOTO|_OU_|POUR|SOIT|CAS|FIN|PAS|SUR|DE|ET|OU|SI|À)\b/i,

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

	// Propriétés (après un accès membre '.' ou '..', y compris après des indexations [...] )
	// Note: on n'utilise pas \b car il n'est pas Unicode-aware (ex: mots finissant par 'é').
	'property': /(?<=\.\.|\.)[\p{L}\p{N}_]+(?![\p{L}\p{N}_])/u,

	// Nombres (entiers et décimaux, négatifs inclus)
	'number': /-?\b\d+(?:\.\d+)?\b/,

	// Opérateurs
	'operator': /(?:\?\?=\*|<=>|\?\?\*|\?\?=|\+\+|--|\+=|-=|\|\||~=|<>|<=|>=|<-|\?!|\?\?|=|\+|\*|\/|-|%|\^|&|\||>|<)/,

	// Ponctuation
	'punctuation': /[(){}\[\],;:.]/
};

// Alias pour compatibilité
Prism.languages.wl = Prism.languages.wlangage;
