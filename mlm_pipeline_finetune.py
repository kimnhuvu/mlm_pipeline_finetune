#!/usr/bin/env python
# coding: utf-8

# In[13]:


get_ipython().system('pip install transformers datasets torch pdfplumber huggingface-hub')


# In[14]:


from huggingface_hub import login

# Đăng nhập vào Hugging Face Hub bằng token API của bạn
login("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")


# In[4]:


get_ipython().system('pip install python-docx')


# In[8]:


import os
import comtypes.client

def convert_doc_to_docx(doc_folder):
    """
    Chuyển tất cả các file .doc trong thư mục thành .docx.
    Args:
        doc_folder: Đường dẫn chứa file .doc.
    """
    word = comtypes.client.CreateObject("Word.Application")
    word.Visible = False

    for filename in os.listdir(doc_folder):
        if filename.endswith(".DOC"):
            doc_path = os.path.abspath(os.path.join(doc_folder, filename))
            docx_path = os.path.abspath(os.path.join(doc_folder, filename + "x"))
            print(f"Chuyển đổi file: {doc_path} -> {docx_path}")
            doc = word.Documents.Open(doc_path)
            doc.SaveAs(docx_path, FileFormat=16)  # FileFormat=16 là .docx
            doc.Close()

    word.Quit()
    print("Chuyển đổi hoàn tất!")

# Chạy chuyển đổi
convert_doc_to_docx("E:\\CaoHoc\\Luan Van\\Data")


# In[9]:


import os
from docx import Document

def extract_text_from_docx(docx_folder):
    """
    Trích xuất văn bản từ tất cả các file .docx trong một thư mục.
    Args:
        docx_folder: Đường dẫn đến thư mục chứa các file .docx.
    Returns:
        text_data: Chuỗi văn bản được trích xuất từ các file .docx.
    """
    text_data = ""
    for filename in os.listdir(docx_folder):
        if filename.endswith(".docx"):
            docx_path = os.path.join(docx_folder, filename)
            print(f"Đang xử lý file: {docx_path}")
            document = Document(docx_path)
            for para in document.paragraphs:
                text_data += para.text + "\n"
    return text_data

# Đường dẫn tới thư mục chứa các file .docx
docx_folder = "E:\CaoHoc\Luan Van\Data"  # Thay đường dẫn với thư mục của bạn
raw_text = extract_text_from_docx(docx_folder)

# Lưu văn bản trích xuất vào file
with open("combined_text_docx.txt", "w", encoding="utf-8") as f:
    f.write(raw_text)

print("Dữ liệu văn bản đã được trích xuất và lưu vào 'combined_text_docx.txt'")


# In[11]:


import re

def clean_text(text):
    """
    Làm sạch văn bản: loại bỏ ký tự đặc biệt và khoảng trắng thừa.
    """ # Loại bỏ ký tự không cần thiết
    text = re.sub(r"\s+", " ", text).strip()  # Xóa khoảng trắng thừa
    return text

# Làm sạch văn bản
with open("combined_text.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

cleaned_text = clean_text(raw_text)

# Lưu văn bản sạch vào file
with open("cleaned_text.txt", "w", encoding="utf-8") as f:
    f.write(cleaned_text)

print("Văn bản đã được làm sạch và lưu vào 'cleaned_text.txt'")


# In[16]:


pip install --upgrade pyOpenSSL cryptography urllib3


# In[17]:


from datasets import Dataset
from transformers import AutoTokenizer

# Load tokenizer của mDeBERTa-v3
model_checkpoint = "microsoft/mdeberta-v3-base"
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)

# Chia văn bản thành đoạn nhỏ
def split_into_paragraphs(text, max_length=512):
    paragraphs = text.split(". ")  # Tách thành các câu hoặc đoạn
    return [{"text": para} for para in paragraphs if len(para) > 50]

# Tạo dataset từ văn bản đã làm sạch
paragraphs = split_into_paragraphs(cleaned_text)
dataset = Dataset.from_list(paragraphs)

# Tokenize dữ liệu
def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=512)

tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=["text"])

print("Dataset đã được tokenize thành công!")


# In[ ]:


from transformers import AutoModelForMaskedLM, DataCollatorForLanguageModeling, Trainer, TrainingArguments

# Load mô hình Masked Language Model
model = AutoModelForMaskedLM.from_pretrained(model_checkpoint)

# Data collator tự động che token (MLM)
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer, mlm=True, mlm_probability=0.15
)

# Training arguments
training_args = TrainingArguments(
    output_dir="./mlm_results",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01,
    save_steps=500,
    save_total_limit=2,
    logging_dir="./logs",
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator,
    tokenizer=tokenizer,
)

# Huấn luyện mô hình
trainer.train()

# Lưu mô hình đã fine-tune
model.save_pretrained("./mlm_finetuned")
tokenizer.save_pretrained("./mlm_finetuned")

print("Huấn luyện MLM hoàn thành và mô hình đã được lưu.")


# In[ ]:


# Đặt tên repo trên Hugging Face Hub
repo_name = "mdeberta-v3-mlm-finetuned"

# Lưu mô hình và tokenizer lên Hugging Face Hub
model.push_to_hub(repo_name)
tokenizer.push_to_hub(repo_name)

print(f"Mô hình đã được lưu lên Hugging Face tại: https://huggingface.co/kimnhuvu276/{repo_name}")


# In[ ]:


from transformers import pipeline

# Load mô hình đã fine-tune từ Hugging Face Hub
fill_mask = pipeline("fill-mask", model=f"<your_username>/{repo_name}")

# Kiểm tra khả năng điền từ bị che
input_text = "Bộ luật Lao động năm [MASK] có hiệu lực vào ngày 1/1/2021."
results = fill_mask(input_text)

for result in results:
    print(f"Điền từ: {result['token_str']}, Xác suất: {result['score']:.4f}")

