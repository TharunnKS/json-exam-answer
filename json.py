import json
import hashlib
import csv
import pandas as pd
import matplotlib.pyplot as plt

with open('/content/drive/MyDrive/ML/DataEngineeringQ2.json') as f:
    data = json.load(f)

print(data)
df = pd.DataFrame(data)
print(df['patientDetails'][1]['gender'])
df = df[['appointmentId', 'phoneNumber', 'patientDetails', 'consultationData']]
print(df)
l=0
for i in df['patientDetails']:
  df['patientDetails'][l]['gender'] = (lambda x: 'male' if x['gender'] == 'M' else ('female' if x['gender'] == 'F' else 'others'))
  l=l+1
  df['DOB'] = (lambda x: x['birthDate'])
  df = df.rename(columns={'DOB': 'Age'})

df['fullName'] = df['patientDetails'].apply(lambda x: x['firstName'] + ' ' + x['lastName'])

def is_valid_mobile(number):
    if number.startswith('+91') or number.startswith('91'):
        number = number[-10:]
    return number.isdigit() and 6000000000 <= int(number) <= 9999999999

df['isValidMobile'] = df['phoneNumber'].apply(is_valid_mobile)

def get_hash(number):
    if number.startswith('+91') or number.startswith('91'):
        number = number[-10:]
    if is_valid_mobile(number):
        return hashlib.sha256(number.encode()).hexdigest()
    else:
        return None

df['phoneNumberHash'] = df['phoneNumber'].apply(get_hash)

df['Age'] = pd.to_datetime(df['Age']).apply(lambda x: (pd.to_datetime('today').year - x.year) if pd.notnull(x) else None)


grouped = df.groupby('appointmentId')['consultationData']
df['noOfMedicines'] = grouped.transform('size')
df['noOfActiveMedicines'] = grouped.apply(lambda x: sum(x['IsActive']))
df['noOfInActiveMedicines'] = grouped.apply(lambda x: sum(~x['IsActive']))

df['medicineNames'] = grouped.apply(lambda x: ','.join(x[x['IsActive']]['medicines']))

final_df = df[['appointmentId', 'fullName', 'phoneNumber', 'isValidMobile', 'phoneNumberHash',
               'gender', 'DOB', 'Age', 'noOfMedicines', 'noOfActiveMedicines',
               'noOfInActiveMedicines', 'medicineNames']]

final_df.to_csv('output.csv', index=False, sep='~', quoting=csv.QUOTE_NONNUMERIC)

aggregated_data = {
    'Age': df['Age'].count(),
    'gender': df['gender'].value_counts().to_dict(),
    'validPhoneNumbers': df['isValidMobile'].sum(),
    'appointments': df['appointmentId'].nunique(),
    'medicines': df['noOfMedicines'].sum(),
    'activeMedicines': df['noOfActiveMedicines'].sum()
}

with open('aggregated_data.json', 'w') as f:
    json.dump(aggregated_data, f)

# Plot pie chart
gender_counts = df['gender'].value_counts()
plt.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%')
plt.title('Number of Appointments by Gender')
plt.show()