#!/bin/bash

# Vérifier si le fichier config.json existe
if [ ! -f "config.json" ]; then
    echo "Erreur: config.json non trouvé. Veuillez monter le fichier config.json dans le conteneur."
    exit 1
fi

# Initialiser le module d'indexation si la base de données n'existe pas
if [ ! -f "YAM_events.db" ]; then
    echo "Initialisation du module d'indexation..."
    python3 -m yam_indexing_module.initialize_indexing_module
fi

# Démarrer le service d'indexation en arrière-plan
echo "Démarrage du service d'indexation..."
python3 -m yam_indexing_module.main_indexing &

# Démarrer l'API
echo "Démarrage de l'API..."
python3 pdf_generator_module/start_api.py