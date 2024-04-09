from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

finetuned_model = "xtie/PEGASUS-PET-impression"
tokenizer = AutoTokenizer.from_pretrained(finetuned_model) 
model = AutoModelForSeq2SeqLM.from_pretrained(finetuned_model, ignore_mismatched_sizes=True).eval()

findings_info = """
Description: PET CT WHOLE BODY
Radiologist: James
Findings:
Head/Neck: xxx Chest: xxx Abdomen/Pelvis: xxx Extremities/Musculoskeletal: xxx
Indication:
The patient is a 60-year old male with a history of xxx
"""

inputs = tokenizer(findings_info.replace('\n', ' '),
                  padding="max_length",
                  truncation=True,
                  max_length=1024,
                  return_tensors="pt")
input_ids = inputs.input_ids.to("cpu")
attention_mask = inputs.attention_mask.to("cpu")
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
# get the generated impressions
output_str = tokenizer.decode(outputs[0],
                              skip_special_tokens=True)
print(output_str)
