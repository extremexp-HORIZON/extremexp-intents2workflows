@echo off
start cmd /k "cd /d %~dp0backend/api && uvicorn main:app --port=9001"
start cmd /k "cd /d %~dp0backend/modules/IntentSpecification2WorkflowGenerator && flask --app api\api_main.py run --port=9002"
start cmd /k "cd /d %~dp0backend/modules/IntentAnticipation && flask --app ./llm/api_llm_interaction.py run --host 0.0.0.0 --port 9003"
start cmd /k "cd /d %~dp0backend/modules/IntentAnticipation && flask --app ./kge-recommendation/api_kge_recommendation.py run --host 0.0.0.0 --port 9004"
start cmd /k "cd /d %~dp0frontend && quasar dev"



