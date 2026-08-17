# treinar_modelo.py
import os
import json
import logging
import pandas as pd
import xgboost as xgb
import joblib

from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import precision_recall_curve, auc, make_scorer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
os.makedirs('modelos', exist_ok=True)

logging.info("Iniciando processamento e unificação da base de dados...")
partes = []
for i in range(1, 11):
    caminho = f'data/cartao_de_credito_sintetico_parte_{i:02d}.csv'
    if os.path.exists(caminho) and os.path.getsize(caminho) > 0:
        try:
            df_temp = pd.read_csv(caminho)
            if not df_temp.empty:
                partes.append(df_temp)
        except Exception as e:
            logging.warning(f"Não foi possível ler {caminho}: {e}")

if not partes:
    raise ValueError("Nenhum arquivo CSV com dados válidos foi encontrado na pasta data/!")

df_completo = pd.concat(partes, ignore_index=True).dropna(subset=["Class"])

if 'Device_IP' in df_completo.columns:
    ip_frequencia = df_completo['Device_IP'].value_counts().to_dict()
    df_completo['IP_Frequencia_Score'] = df_completo['Device_IP'].map(ip_frequencia)
else:
    df_completo['IP_Frequencia_Score'] = 1

colunas_v = [f"V{i}" for i in range(1, 29)]
features_numericas = ["Time", "Amount", "IP_Frequencia_Score"] + colunas_v
features_categoricas = [col for col in ["Previous_Action", "Connection_Type"] if col in df_completo.columns]

X = df_completo[features_numericas + features_categoricas].copy()
y = df_completo["Class"].astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), ["Time", "Amount"]),
        ('cat', OneHotEncoder(handle_unknown='ignore'), features_categoricas)
    ], remainder='passthrough'
)

fator_peso = (len(y_train) - sum(y_train)) / sum(y_train) if sum(y_train) > 0 else 1
modelo_xgb = xgb.XGBClassifier(objective="binary:logistic", eval_metric="logloss", scale_pos_weight=fator_peso, random_state=42, n_jobs=-1)

pipeline_antifraude = Pipeline(steps=[('preprocessor', preprocessor), ('classifier', modelo_xgb)])

param_grid = {
    'classifier__max_depth': [3, 5],
    'classifier__learning_rate': [0.1],
    'classifier__n_estimators': [100]
}

def calcular_auprc(y_true, y_pred_proba):
    p, r, _ = precision_recall_curve(y_true, y_pred_proba)
    return auc(r, p)

auprc_scorer = make_scorer(calcular_auprc, response_method='predict_proba')
cv_estratificado = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)

grid = GridSearchCV(estimator=pipeline_antifraude, param_grid=param_grid, scoring=auprc_scorer, cv=cv_estratificado, n_jobs=-1)
grid.fit(X_train, y_train)

modelo_calibrado = CalibratedClassifierCV(estimator=grid.best_estimator_, method='isotonic', cv=3)
modelo_calibrado.fit(X_train, y_train)

joblib.dump(modelo_calibrado, 'modelos/pipeline_antifraude_calibrado.joblib')
logging.info("🧠 Modelo preditivo acoplado e exportado com absoluto sucesso.")