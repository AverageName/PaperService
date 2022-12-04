from topic_modeling.mapping import mapping_class, mapping_multi_class
from sentence_transformers import SentenceTransformer

import pickle

import nltk
from nltk.corpus import stopwords
import re

nltk.download("stopwords")
sno = nltk.stem.SnowballStemmer("english")
stop = set(stopwords.words("english"))


def get_multiclass(x: int):
    return mapping_multi_class[x]


def get_class(x: int):
    return mapping_class[x]


def get_model(path: str):
    with open(path, "rb") as file:
        model = pickle.load(file)
    return model


def get_cleaned_sents(sent: str):
    def cleanpunc(sentence):
        cleaned = re.sub(r'[?|!|\'|"|#]', r"", sentence)
        cleaned = re.sub(r"[.|,|)|(|\|/-]", r" ", cleaned)
        return cleaned

    sent = str(sent)
    filtered_sentence = []
    for word in sent.split():
        for cleaned_words in cleanpunc(word).split():
            if (cleaned_words.isalpha()) & (len(cleaned_words) > 2):
                if cleaned_words.lower() not in stop:
                    s = sno.stem(cleaned_words.lower())
                    filtered_sentence.append(s)
    return " ".join(filtered_sentence)


def get_topic(title: str, transformer: object, model: object):
    embeddings = transformer.encode(title).reshape(1, -1)
    pred = model.predict(embeddings)[0]
    topic, multi_topic = get_class(pred), get_multiclass(pred)
    return topic, multi_topic


def predict_topic(title: list):
    transformer = SentenceTransformer("distilbert-base-nli-mean-tokens")
    model = get_model("./topic_modeling/model_logreg.pkl")
    title = get_cleaned_sents(title)

    topic, multi_topic = get_topic(title, transformer, model)
    return topic, multi_topic


# def test_sample():
#     df = pd.read_csv("df_clean.csv")
#     test_sample = df["title"][0]
#
#     output = predict_topic(test_sample)
#
#     print("=" * 50)
#     print(test_sample)
#     print(output)
#
#
# if __name__ == "__main__":
#     test_sample()
