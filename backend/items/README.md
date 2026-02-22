# Minecraft Recipe Lookup (sample)

Simple Python CLI to lookup sample Minecraft crafting recipes.

Usage:

1. List available items:

```
python recipes.py list
```

2. Get a recipe:

```
python recipes.py get torch
```

3. Search partial names or display names:

```
python recipes.py search plank
```

The included `recipes.json` is a small sample. You can expand it with more items using the same structure.

File: `recipes.json` contains objects keyed by lowercase item ids. Each recipe supports `type` (shaped|shapeless), `pattern` and `key` for shaped recipes, or `ingredients` for shapeless recipes.
