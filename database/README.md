# Database Files

This directory should contain the training data for the health prediction models.

## Required Files:

1. **Training.csv** - Dataset containing symptom-disease mappings for disease prediction

## Training.csv Format:

The CSV should have:
- Columns for each symptom (binary 0/1 values)
- Final column named 'prognosis' with disease names
- Each row represents a patient case

Example structure:
```csv
itching,skin_rash,continuous_sneezing,shivering,chills,joint_pain,stomach_pain,...,prognosis
1,1,0,0,0,0,0,...,Fungal infection
0,0,1,1,1,0,0,...,Common Cold
...
```

## Note:

Without the Training.csv file, the application will use a default symptom list but disease prediction may not work optimally.

To add your data:
1. Prepare your symptom-disease dataset in the required format
2. Save as Training.csv in this directory
3. Restart the application