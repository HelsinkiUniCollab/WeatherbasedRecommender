const medicalEnum = { 'Mental stress':
['Weightlifting', 'Jogging', 'Skateboarding', 'Cycling', 'Swimming', 'Climbing', 'Football'],
Obesity: ['Weightlifting', 'Jogging', 'Skateboarding', 'Cycling', 'Swimming', 'Climbing', 'Football'],
'Diabetes (Type I)': ['Weightlifting', 'Jogging', 'Skateboarding', 'Cycling', 'Swimming', 'Climbing', 'Football'],
'Diabetes (Type II)': ['Weightlifting', 'Jogging', 'Skateboarding', 'Cycling', 'Swimming', 'Climbing', 'Football'],
Hypertension: ['Weightlifting', 'Jogging', 'Skateboarding', 'Cycling', 'Swimming', 'Climbing', 'Football'],
'Coronary heart disease': ['Jogging', 'Skateboarding', 'Cycling', 'Swimming', 'Football'],
'Bronchial asthma': ['Jogging', 'Skateboarding', 'Cycling', 'Swimming', 'Football'],
Osteoporosis: ['Weightlifting', 'Jogging', 'Skateboarding', 'Cycling', 'Swimming', 'Climbing', 'Football'],
'Back pain': ['Weightlifting', 'Jogging', 'Skateboarding', 'Cycling', 'Swimming', 'Climbing', 'Football'],
Pregnancy: ['Jogging', 'Swimming'] };

const covertMedicalCategories = (medCategories) => {
  let outputCategories = new Set(medicalEnum[medCategories[0]]);
  for (let i = 0; i < medCategories.length; i += 1) {
    console.log(medicalEnum[medCategories[i]]);
    outputCategories = outputCategories.intersection(new Set(medicalEnum[medCategories[i]]));
  }
  const tmp = Array.from(outputCategories);
  return tmp;
};

export default covertMedicalCategories;
