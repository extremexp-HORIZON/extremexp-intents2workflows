# Get the absolute path to the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Launch each process in a new GNOME Terminal tab
gnome-terminal -- bash -c "cd '$SCRIPT_DIR/backend/api' && uvicorn main:app --port=9001; exec bash" \
--tab -- bash -c "cd '$SCRIPT_DIR/backend/modules/IntentSpecification2WorkflowGenerator' && flask --app api/api_main.py run --port=9002; exec bash" \
--tab -- bash -c "cd '$SCRIPT_DIR/backend/modules/IntentAnticipation' && flask --app ./llm/api_llm_interaction.py run --host 0.0.0.0 --port 9003; exec bash" \
--tab -- bash -c "cd '$SCRIPT_DIR/backend/modules/IntentAnticipation' && flask --app ./kge-recommendation/api_kge_recommendation.py run --host 0.0.0.0 --port 9004; exec bash" \
--tab -- bash -c "cd '$SCRIPT_DIR/frontend' && quasar dev; exec bash"