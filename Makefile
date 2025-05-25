# Makefile (루트 디렉토리)
run-ui:
	PYTHONPATH=. streamlit run app/frontend/ui.py

run-api:
	PYTHONPATH=. uvicorn app.main:app --reload

export-env:
	conda env export --from-history > environment.yml

clean-pyc:
	find . -name "*.pyc" -delete

# make run-ui     # Streamlit UI 실행
# make run-api    # FastAPI 실행
