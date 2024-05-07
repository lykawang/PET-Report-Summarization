import pandas as pd
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load the pre-generated Excel file
df = pd.read_excel('output.xlsx')

# Specify the model to be used
finetuned_model = "xtie/PEGASUS-PET-impression"
tokenizer = AutoTokenizer.from_pretrained(finetuned_model)
model = AutoModelForSeq2SeqLM.from_pretrained(finetuned_model, ignore_mismatched_sizes=True).eval()

# Prepare a new column for generated impressions
df['Generated Impression'] = ""

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    # Construct the input text by concatenating specific fields
    fields = ['Procedure', 'Referring Physician', 'Clinical History', 'Clinical Information', 'History', 'Technique', 'Comparison', 'Findings or PET Findings']
    # findings_info = "PET SCAN REPORT " + " ".join([str(row[field]) for field in fields if field in row and pd.notna(row[field])])
    findings_info = "PET SCAN REPORT " + " ".join([f"{field}: {str(row[field])}" for field in fields if field in row and pd.notna(row[field])])
    
     # Add findings_info to the DataFrame
    df.at[index, 'Findings Info'] = findings_info
    
    # Prepare the input for the model
    inputs = tokenizer(findings_info.replace('\n', ' '),
                       padding="max_length",
                       truncation=True,
                       max_length=1024,
                       return_tensors="pt")
    input_ids = inputs.input_ids.to("cpu")
    attention_mask = inputs.attention_mask.to("cpu")

    # Generate output using the model
    outputs = model.generate(input_ids,
                             attention_mask=attention_mask,
                             max_new_tokens=512, 
                             num_beam_groups=1,
                             num_beams=4, 
                             do_sample=False,
                             diversity_penalty=0.0,
                             num_return_sequences=1, 
                             length_penalty=2.0,
                             no_repeat_ngram_size=3,
                             early_stopping=True,
                             )

    # Decode the generated text
    output_str = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Store the generated impression in the DataFrame
    df.at[index, 'Generated Impression'] = output_str
    
    # Print a dot to indicate progress
    print('.', end='', flush=True)

# Save the DataFrame to a new Excel file with the generated impressions
df.to_excel('output_with_impressions.xlsx', index=False)

print("Data processing and impression generation complete. Output saved to 'output_with_impressions.xlsx'.")
