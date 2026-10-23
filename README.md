# 🛡️ Phishing Email Detection

A Python desktop app that classifies pasted email text as **likely safe** or **possible phishing** using TF-IDF features and a Multinomial Naive Bayes model. It also flags selected suspicious keywords and URLs to help with manual review.

> **Educational prototype:** The bundled dataset contains only 10 short examples. The displayed evaluation scores are based on a tiny holdout set and should not be treated as evidence of real-world accuracy.

## ✨ Features

- TF-IDF + Multinomial Naive Bayes text classification
- Holdout accuracy, precision, recall, and F1 metrics
- Estimated phishing probability (not a guarantee)
- Flags for selected urgency, credential, reward, and URL indicators
- Input validation and clear error messages
- Tkinter desktop interface with Analyze and Clear actions
- Local analysis; the app does not upload email text to a server

## 🖼️ Application Demo

### 1. Safe email example

The meeting reminder below was classified as **LIKELY SAFE**, with a model-estimated phishing probability of 12.5%.

![Safe email test screenshot](safe-email-test.png)

### 2. Phishing email example

The urgent message asking for a password and promising a reward was classified as **POSSIBLE PHISHING**, with a model-estimated phishing probability of 75.9%.

![Phishing email test screenshot](phishing-email-test.png)

**Screenshot setup:** Upload the two PNG screenshots to the repository root using these exact filenames: `safe-email-test.png` and `phishing-email-test.png`. The images will display in this section once the files exist in the repository.

> Predictions and probabilities are only triage hints. Verify sender addresses, links, and requests independently.

## 🧰 Built With

- Python 3.10+
- pandas
- scikit-learn
- Tkinter

## 📁 Project Structure

```text
Phishing-Email-Detection/
├── emails.csv                 # Small example dataset (text,label)
├── phishing_detector.py       # Model training and GUI
├── requirements.txt           # Python dependencies
├── safe-email-test.png        # Safe email demo screenshot (upload required)
├── phishing-email-test.png    # Phishing email demo screenshot (upload required)
├── README.md
├── LICENSE
└── .gitignore
```

## 🚀 Installation and Run

1. Install Python 3.10 or newer.
2. Clone the repository:

   ```powershell
   git clone https://github.com/shivarjunchaturvedi/Phishing-Email-Detection.git
   cd Phishing-Email-Detection
   ```

3. Install the dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Run the application:

   ```powershell
   python phishing_detector.py
   ```

On Windows, you can also use `py phishing_detector.py`.

## 🧠 How It Works

1. Loads the `text,label` columns from `emails.csv`.
2. Splits the dataset into training and holdout sets.
3. Fits TF-IDF features and a Multinomial Naive Bayes classifier using the training data.
4. Displays holdout metrics.
5. Predicts the pasted email text and shows selected keyword/URL review flags.

## ⚠️ Limitations

- The dataset contains only 10 short examples, so holdout metrics are highly unstable.
- The model may miss phishing messages or flag legitimate messages incorrectly.
- Keywords and URLs alone do not prove an email is malicious.
- The displayed probability is model-estimated and is not calibrated as a real-world risk score.
- Do not use this prototype as the sole basis for security decisions.

For meaningful evaluation, use a much larger, diverse, correctly labelled dataset and assess false positives and false negatives on data kept separate from training.

## 👨‍💻 Author

**Shivarjun Chaturvedi**

- GitHub: [@shivarjunchaturvedi](https://github.com/shivarjunchaturvedi)
- LinkedIn: [Shivarjun Chaturvedi](https://www.linkedin.com/in/shivarjun-chaturvedi)
