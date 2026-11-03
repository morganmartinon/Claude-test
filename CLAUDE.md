# Chaîne de production de reels

Projet d'automatisation du montage de reels verticaux (1080x1920, 30 fps, MP4) à partir de rushes bruts.

## Dossiers
- `input/` : rushes, musique, modèles de référence (originaux, ne jamais modifier)
- `work/` : fichiers intermédiaires (brief, plans découpés, montage brut)
- `output/` : reel final
- `docs/` : références de style

## Agents (dans `.claude/agents/`)
| Agent | Modèle | Rôle |
|---|---|---|
| `chef-de-projet` | Opus | Écrit le brief, délègue, contrôle la qualité |
| `decoupeur` | Sonnet | Choisit et découpe les plans |
| `assembleur` | Sonnet | Monte les plans, musique, coupes sur le rythme |
| `motion` | Sonnet | Étalonnage, effets, textes animés, export |

## Flux
`input/` → chef-de-projet (brief) → decoupeur → assembleur → motion → `output/reel_final.mp4`

## Outils
Tout se fait avec `ffmpeg` et `ffprobe` en ligne de commande. Pour des animations plus avancées, on pourra ajouter plus tard une brique dédiée (par exemple Remotion).

## Lancer une production
Demande : « Utilise l'agent chef-de-projet pour faire un reel avec les rushes de `input/`, en suivant le style de `docs/style-reference.md` ».
