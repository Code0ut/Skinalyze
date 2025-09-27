# Model Files

This directory should contain the following model files for the health prediction features:

## Required Files:

1. **maternal_risk_model.joblib** - Trained model for maternal health risk prediction
2. **disease_model.joblib** - Trained model for general disease prediction  
3. **disease_label_encoder.joblib** - Label encoder for disease prediction model

## Model Training:

These models should be trained using appropriate datasets:

- **Maternal Health Risk**: Train on maternal health datasets with features like Age, SystolicBP, DiastolicBP, BS, BodyTemp, HeartRate
- **Disease Prediction**: Train on symptom-disease datasets with binary symptom features

## Note:

Without these model files, the corresponding features will show error messages and won't function. The application will still work for other features like skin analysis and user management.

To add your models:
1. Train your models using scikit-learn or similar
2. Save them using joblib.dump()
3. Place the .joblib files in this directory
4. Restart the application