from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)

# Define directories for uploading files and for the HEC requirements CSV files
UPLOAD_FOLDER = 'uploads/'
HEC_REQUIREMENTS_FOLDER = 'hec_requirements/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to check passed courses and calculate total credit hours
def is_pass(data):
    credit_hour_gained = 0
    for index, row in data.iterrows():
        if row['points'] > 0.0:  # points is for passed courses
            credit_hour_gained += row['creditHour']
    return credit_hour_gained

# Function to generate validation results based on total credits
def result(total_general_education, total_university_electives, total_math_science_foundation,
           total_computing_core, total_domain_cs_core, total_domain_cs_electives, total_domain_cs_supporting):
    validation_result = []
    Total_credits= (
        total_general_education+
        total_university_electives+
        total_math_science_foundation+
        total_computing_core+
        total_domain_cs_core+
        total_domain_cs_electives+
        total_domain_cs_supporting
    )
    if total_general_education-22 < 0:
        validation_result.append(f"You need to take  more credits in General Education.")

    if total_university_electives-12 < 0:
        validation_result.append(f"You need to take  more credits in University Elective.")

    if total_math_science_foundation-12 < 0:
        validation_result.append(f"You need to take  more credits  in Math and Science Foundation.")

    if total_computing_core-39 < 0:
        validation_result.append(f"You need to take  more credits in Computing Core.")

    if total_domain_cs_core-24 < 0:
        validation_result.append(f"You need to take  more credits in Domain Computer Science Core.")

    if total_domain_cs_electives-15 < 0:
        validation_result.append(f"You need to take  more credits in Computer Science Electives.")

    if total_domain_cs_supporting-9 < 0:
        validation_result.append(f"You need to take  more credits in Computer Science Supporting.")

    # Uncomment if extra courses need to be validated
    #if total_general_education-22 > 0:
    #     validation_result.append(f"You have taken {abs(total_general_education)} extra credits in General Education.")

    #if total_university_electives-12 > 0:
    #     validation_result.append(f"You have taken {abs(total_university_electives)} extra credits in University Elective courses.")

    #if total_math_science_foundation-12 > 0:
    #     validation_result.append(f"You have taken {abs(total_math_science_foundation)} extra credits in Math and Science Foundation.")

    #if total_computing_core-39 > 0:
     #    validation_result.append(f"You have taken {abs(total_computing_core)} extra credits in Computing Core.")

    #if total_domain_cs_core-24 > 0:
    #     validation_result.append(f"You have taken {abs(total_domain_cs_core)} extra credits in Computer Science Core.")

   # if total_domain_cs_electives-25 > 0:
      #   validation_result.append(f"You have taken {abs(total_domain_cs_electives)} extra credits in Computer Science Electives.")

   # if total_domain_cs_supporting-9 > 0:
     #    validation_result.append(f"You have taken {abs(total_domain_cs_supporting)} extra credits in Computer Science Supporting.")

    if (
        total_general_education >= 0 and total_university_electives >= 0
        and total_math_science_foundation >= 0 and total_computing_core >= 0
        and total_domain_cs_core >= 0 and total_domain_cs_electives >= 0
        and total_domain_cs_supporting >= 0) and (Total_credits==133):
        validation_result.append("--------------Degree Validated Successfully---------------")
        #validation_result.append(f"Total credits: {Total_credits}")
        return "\n".join(validation_result)
    else:
        validation_result.append("--------------Degree Validation Failed---------------")
        #validation_result.append(f"Total credits: {Total_credits}")
        return "\n".join(validation_result)


# Function to validate degree by merging transcript with HEC requirements
def validate_degree(transcript_path):
    # Read the uploaded transcript
    file = pd.read_csv(transcript_path)
    file1 = file.drop(columns='rmk', axis=1)  # Assuming 'rmk' is the column to be dropped

    # Read the required CSV files dynamically from the 'hec_requirements' folder
    cs_core = pd.merge(file1, pd.read_csv(os.path.join(HEC_REQUIREMENTS_FOLDER, 'cscore.csv')), on='courseName', how='left').dropna()
    cs_general = pd.merge(file1, pd.read_csv(os.path.join(HEC_REQUIREMENTS_FOLDER, 'csgeneral.csv')), on='courseName', how='left').dropna()
    cs_generalelective = pd.merge(file1, pd.read_csv(os.path.join(HEC_REQUIREMENTS_FOLDER, 'csgeneralelective.csv')), on='courseName', how='left').dropna()
    cs_maths = pd.merge(file1, pd.read_csv(os.path.join(HEC_REQUIREMENTS_FOLDER, 'csmaths.csv')), on='courseName', how='left').dropna()
    cs_compulsory = pd.merge(file1, pd.read_csv(os.path.join(HEC_REQUIREMENTS_FOLDER, 'cscompulsory.csv')), on='courseName', how='left').dropna()
    cs_supporting = pd.merge(file1, pd.read_csv(os.path.join(HEC_REQUIREMENTS_FOLDER, 'cssupporting.csv')), on='courseName', how='left').dropna()
    cs_elective = pd.merge(file1, pd.read_csv(os.path.join(HEC_REQUIREMENTS_FOLDER, 'cselective.csv')), on='courseName', how='left').dropna()

    # Calculate the total credits for each course category
    total_general_education = is_pass(cs_general)  #19 in areas covered section
    total_university_electives = is_pass(cs_generalelective) 
    total_math_science_foundation = is_pass(cs_maths) 
    total_computing_core = is_pass(cs_core) 
    total_domain_cs_core = is_pass(cs_compulsory) 
    total_domain_cs_electives = is_pass(cs_elective) 
    total_domain_cs_supporting = is_pass(cs_supporting) 

    # Get validation result
    validation_text = result(
        total_general_education,
        total_university_electives,
        total_math_science_foundation,
        total_computing_core,
        total_domain_cs_core,
        total_domain_cs_electives,
        total_domain_cs_supporting
    )
    return validation_text

# Route for handling form submission and file upload
@app.route('/', methods=['GET', 'POST'])
def index():
    validation_result = None
    if request.method == 'POST':
        file = request.files['transcript']
        if file:
            # Save the uploaded file
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)

            # Call the degree validation function here
            validation_result = validate_degree(file_path)
    
    return render_template('index.html', validation_result=validation_result)

if __name__ == "__main__":
    app.run(debug=True)
