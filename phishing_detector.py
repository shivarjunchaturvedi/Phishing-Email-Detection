import pandas as pd
import re
import tkinter as tk
from tkinter import messagebox
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, confusion_matrix

# Load dataset
data = pd.read_csv("emails.csv")

X = data["text"]
y = data["label"]

# Feature extraction
vectorizer = TfidfVectorizer()
X_vectorized = vectorizer.fit_transform(X)

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X_vectorized,
    y,
    test_size=0.2,
    random_state=42
)

# Train Model
model = MultinomialNB()
model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)
cm = confusion_matrix(y_test, predictions)

print("Accuracy:", round(accuracy * 100, 2), "%")
print("Confusion Matrix:")
print(cm)

# Suspicious keywords
keywords = [
    "urgent",
    "verify",
    "free",
    "winner",
    "click",
    "reward",
    "account",
    "bank"
]

def analyze_email():
    email_text = email_box.get("1.0", tk.END)

    if not email_text.strip():
        messagebox.showwarning(
            "Warning",
            "Please enter email text."
        )
        return

    email_vector = vectorizer.transform([email_text])
    prediction = model.predict(email_vector)[0]

    reasons = []

    # URL Detection
    if re.search(r"http[s]?://", email_text):
        reasons.append("Suspicious URL Found")

    # Keyword Detection
    for word in keywords:
        if word.lower() in email_text.lower():
            reasons.append(f"Keyword Detected: {word}")

    result = f"Prediction: {prediction.upper()}\n\n"

    if reasons:
        result += "Reasons:\n"
        for r in reasons:
            result += f"• {r}\n"

    output_label.config(text=result)

# GUI
root = tk.Tk()
root.title("Phishing Email Detection Model")
root.geometry("700x500")

title = tk.Label(
    root,
    text="Phishing Email Detection",
    font=("Arial", 18, "bold")
)
title.pack(pady=10)

accuracy_label = tk.Label(
    root,
    text=f"Model Accuracy: {round(accuracy*100,2)}%"
)
accuracy_label.pack()

email_box = tk.Text(
    root,
    height=10,
    width=70
)
email_box.pack(pady=10)

check_btn = tk.Button(
    root,
    text="Analyze Email",
    command=analyze_email
)
check_btn.pack()

output_label = tk.Label(
    root,
    text="",
    justify="left",
    font=("Arial", 11)
)
output_label.pack(pady=20)

root.mainloop()