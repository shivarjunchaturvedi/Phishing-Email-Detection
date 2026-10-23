"""Phishing Email Detection — educational local text classifier.

Trains a TF-IDF + Multinomial Naive Bayes model from emails.csv.
Email text is analyzed locally; no email is sent or uploaded.
The bundled dataset is tiny and illustrative, not suitable for production decisions.
"""
from __future__ import annotations

import re
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "emails.csv"

SUSPICIOUS_KEYWORDS = (
    "urgent", "verify", "free", "winner", "click", "reward",
    "suspended", "password", "login", "limited time", "confirm",
    "bank account", "payment", "gift card",
)
URL_PATTERN = re.compile(r"\b(?:https?://|www\.)\S+", re.IGNORECASE)


def load_dataset(path: Path = DATASET_PATH) -> pd.DataFrame:
    """Load and validate the training CSV."""
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}\nKeep emails.csv in the same folder as this script."
        )

    data = pd.read_csv(path)
    required = {"text", "label"}
    if not required.issubset(data.columns):
        raise ValueError("emails.csv must contain columns named 'text' and 'label'.")

    data = data[["text", "label"]].dropna().copy()
    data["text"] = data["text"].astype(str).str.strip()
    data["label"] = data["label"].astype(str).str.strip().str.lower()
    data = data[data["text"] != ""]
    data["label"] = data["label"].replace({
        "legitimate": "safe",
        "ham": "safe",
        "not phishing": "safe",
        "phishing email": "phishing",
    })

    valid_labels = {"safe", "phishing"}
    unexpected = set(data["label"].unique()) - valid_labels
    if unexpected:
        raise ValueError(
            "Unsupported labels in emails.csv: "
            + ", ".join(sorted(unexpected))
            + ". Use 'safe' or 'phishing'."
        )
    if data["label"].nunique() != 2:
        raise ValueError("The dataset must include both 'safe' and 'phishing' examples.")
    if data["label"].value_counts().min() < 2:
        raise ValueError("Add at least two examples for each class before training.")
    return data


def train_model(data: pd.DataFrame) -> tuple[Pipeline, dict[str, float], str, str]:
    """Split before vectorization to avoid fitting TF-IDF on held-out texts."""
    X_train, X_test, y_train, y_test = train_test_split(
        data["text"],
        data["label"],
        test_size=0.2,
        random_state=42,
        stratify=data["label"],
    )

    model = Pipeline([
        ("tfidf", TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            ngram_range=(1, 2),
            max_features=10000,
            sublinear_tf=True,
        )),
        ("classifier", MultinomialNB(alpha=0.5)),
    ])
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(y_test, predictions, pos_label="phishing", zero_division=0),
        "recall": recall_score(y_test, predictions, pos_label="phishing", zero_division=0),
        "f1": f1_score(y_test, predictions, pos_label="phishing", zero_division=0),
    }
    report = classification_report(y_test, predictions, labels=["phishing", "safe"], zero_division=0)
    matrix = confusion_matrix(y_test, predictions, labels=["phishing", "safe"])
    matrix_text = (
        "Rows = actual; columns = predicted; label order = phishing, safe\n"
        f"{matrix}"
    )
    return model, metrics, report, matrix_text


def inspect_email(text: str, model: Pipeline) -> tuple[str, list[str], float | None]:
    """Classify text and return transparent heuristic flags (not proof of phishing)."""
    prediction = str(model.predict([text])[0])
    reasons: list[str] = []

    matches = [word for word in SUSPICIOUS_KEYWORDS if re.search(
        rf"(?<!\w){re.escape(word)}(?!\w)", text, flags=re.IGNORECASE
    )]
    if matches:
        reasons.append("Urgency/credential/reward keywords: " + ", ".join(matches))
    if URL_PATTERN.search(text):
        reasons.append("Contains a URL — inspect its real destination before opening.")

    phishing_probability: float | None = None
    try:
        classes = list(model.named_steps["classifier"].classes_)
        if "phishing" in classes:
            phishing_probability = float(model.predict_proba([text])[0][classes.index("phishing")])
    except (AttributeError, ValueError, IndexError):
        pass
    return prediction, reasons, phishing_probability


class PhishingDetectorApp:
    def __init__(self, root: tk.Tk, model: Pipeline, metrics: dict[str, float]) -> None:
        self.root = root
        self.model = model
        root.title("Phishing Email Detection")
        root.geometry("850x690")
        root.minsize(720, 600)
        root.configure(bg="#101827")

        tk.Label(
            root, text="Phishing Email Detection",
            font=("Segoe UI", 22, "bold"), fg="#f8fafc", bg="#101827",
        ).pack(pady=(18, 4))
        tk.Label(
            root, text="Local ML analysis • TF-IDF + Naive Bayes",
            font=("Segoe UI", 10), fg="#a8b3c7", bg="#101827",
        ).pack(pady=(0, 12))

        metrics_text = (
            f"Holdout accuracy: {metrics['accuracy']:.0%}   |   "
            f"Precision: {metrics['precision']:.0%}   |   "
            f"Recall: {metrics['recall']:.0%}   |   F1: {metrics['f1']:.0%}"
        )
        tk.Label(
            root, text=metrics_text, font=("Segoe UI", 10, "bold"),
            fg="#93c5fd", bg="#101827",
        ).pack(pady=(0, 10))

        panel = tk.Frame(root, bg="#1b2638", padx=18, pady=15)
        panel.pack(fill="both", expand=True, padx=20, pady=(0, 18))
        tk.Label(
            panel, text="Paste email subject and body",
            font=("Segoe UI", 11, "bold"), fg="#e5e7eb", bg="#1b2638",
        ).pack(anchor="w", pady=(0, 8))

        self.email_box = tk.Text(
            panel, height=11, wrap="word", font=("Consolas", 11),
            bg="#0f1724", fg="#f8fafc", insertbackground="white",
            relief="flat", padx=10, pady=10,
        )
        self.email_box.pack(fill="both", expand=True)

        controls = tk.Frame(panel, bg="#1b2638")
        controls.pack(fill="x", pady=(10, 10))
        tk.Button(
            controls, text="Analyze Email", command=self.analyze,
            font=("Segoe UI", 10, "bold"), bg="#1677ff", fg="white",
            activebackground="#0b5ed7", activeforeground="white",
            relief="flat", cursor="hand2", padx=18, pady=8,
        ).pack(side="left")
        tk.Button(
            controls, text="Clear", command=self.clear,
            font=("Segoe UI", 10), bg="#334155", fg="white",
            activebackground="#475569", activeforeground="white",
            relief="flat", cursor="hand2", padx=18, pady=8,
        ).pack(side="left", padx=8)

        self.result_title = tk.Label(
            panel, text="Result: Waiting for email text",
            font=("Segoe UI", 14, "bold"), fg="#cbd5e1", bg="#1b2638",
        )
        self.result_title.pack(anchor="w", pady=(3, 7))
        self.result_body = tk.Text(
            panel, height=7, wrap="word", font=("Segoe UI", 10),
            bg="#111c2c", fg="#dbeafe", relief="flat",
            state="disabled", padx=10, pady=8,
        )
        self.result_body.pack(fill="x")

        tk.Label(
            root,
            text="Educational prototype only. Always verify sender, links and requests independently.",
            font=("Segoe UI", 9), fg="#fbbf24", bg="#101827",
        ).pack(pady=(0, 10))

    def analyze(self) -> None:
        email_text = self.email_box.get("1.0", "end").strip()
        if not email_text:
            messagebox.showwarning("Email required", "Paste email subject or body first.", parent=self.root)
            return

        prediction, reasons, probability = inspect_email(email_text, self.model)
        if prediction == "phishing":
            self.result_title.configure(text="Prediction: POSSIBLE PHISHING", fg="#f87171")
        else:
            self.result_title.configure(text="Prediction: LIKELY SAFE", fg="#4ade80")

        lines = []
        if probability is not None:
            lines.append(f"Model phishing probability: {probability:.1%} (not a guarantee)")
        if reasons:
            lines.append("Review flags:")
            lines.extend(f"• {reason}" for reason in reasons)
        else:
            lines.append("No keyword/URL heuristic flags found.")
        lines.extend([
            "",
            "Do not treat this prediction as proof. Check the sender address, destination URL, and requests independently.",
        ])

        self.result_body.configure(state="normal")
        self.result_body.delete("1.0", "end")
        self.result_body.insert("end", "\n".join(lines))
        self.result_body.configure(state="disabled")

    def clear(self) -> None:
        self.email_box.delete("1.0", "end")
        self.result_title.configure(text="Result: Waiting for email text", fg="#cbd5e1")
        self.result_body.configure(state="normal")
        self.result_body.delete("1.0", "end")
        self.result_body.configure(state="disabled")


def main() -> None:
    try:
        data = load_dataset()
        model, metrics, report, matrix_text = train_model(data)
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Could not load model", str(exc), parent=root)
        root.destroy()
        raise SystemExit(1) from exc

    print("Dataset rows:", len(data))
    print("Class distribution:\n", data["label"].value_counts().to_string())
    print("Holdout metrics:", {key: round(value, 3) for key, value in metrics.items()})
    print("Classification report (small holdout set; interpret cautiously):\n", report)
    print("Confusion matrix:\n", matrix_text)

    root = tk.Tk()
    PhishingDetectorApp(root, model, metrics)
    root.mainloop()


if __name__ == "__main__":
    main()
