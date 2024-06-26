const medicalEnum = { 'Mental stress':
['Weightlifting', 'Jogging', 'Skateboarding', 'Cycling', 'Swimming', 'Climbing', 'Football', 'Walking'],
Obesity: ['Weightlifting', 'Jogging', 'Skateboarding', 'Cycling', 'Swimming', 'Climbing', 'Football', 'Walking'],
'Diabetes (Type I)': ['Weightlifting', 'Jogging', 'Skateboarding', 'Cycling', 'Swimming', 'Climbing', 'Football', 'Walking'],
'Diabetes (Type II)': ['Weightlifting', 'Jogging', 'Skateboarding', 'Cycling', 'Swimming', 'Climbing', 'Football', 'Walking'],
Hypertension: ['Weightlifting', 'Jogging', 'Skateboarding', 'Cycling', 'Swimming', 'Climbing', 'Football', 'Walking'],
'Coronary heart disease': ['Jogging', 'Skateboarding', 'Cycling', 'Swimming', 'Football', 'Walking'],
Asthma: ['Jogging', 'Skateboarding', 'Cycling', 'Swimming', 'Football', 'Walking'],
Osteoporosis: ['Weightlifting', 'Jogging', 'Skateboarding', 'Cycling', 'Swimming', 'Climbing', 'Football', 'Walking'],
'Back pain': ['Weightlifting', 'Jogging', 'Skateboarding', 'Cycling', 'Swimming', 'Climbing', 'Football', 'Walking'],
Pregnancy: ['Jogging', 'Swimming', 'Walking'] };

const covertMedicalCategories = (medCategories) => {
  let outputCategories = new Set(medicalEnum[medCategories[0]]);
  for (let i = 0; i < medCategories.length; i += 1) {
    outputCategories = outputCategories.intersection(new Set(medicalEnum[medCategories[i]]));
  }
  const tmp = Array.from(outputCategories);
  return tmp;
};

export default covertMedicalCategories;
