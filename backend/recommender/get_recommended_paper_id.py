from sentence_transformers import SentenceTransformer, util
import torch
import pandas as pd
import typing

def get_recommended_paper_id(last_liked_paper: typing.Optional[dict], readed_papers: list):
    top_5k_papers = pd.read_csv("/data/recommender_data/top_5k_papers.csv")
    if last_liked_paper is None:
        candidate_paper_ids = top_5k_papers._id.tolist()
    else:
        top_5k_papers_embeddings = torch.load("/data/recommender_data/top_5k_papers_embeddings.pt",
                                              map_location=torch.device('cpu'))
        model = SentenceTransformer(
            "/data/recommender_data/allenai-specter/content/model/sentence-transformers_allenai-specter")
        query = last_liked_paper["title"] + '[SEP]' + last_liked_paper["abstract"]
        query_embedding = model.encode(query, convert_to_tensor=True)
        search_hits = util.semantic_search(query_embedding, top_5k_papers_embeddings, top_k=100)[0]
        candidate_paper_ids = top_5k_papers.iloc[[search_hits[i]["corpus_id"] for i in range(100)]]._id.tolist()
    recommended_paper_ids = list()
    for recommended_paper_id in candidate_paper_ids:
        if recommended_paper_id not in readed_papers:
            recommended_paper_ids.append(recommended_paper_id)
        if len(recommended_paper_ids) >= 5:
            return recommended_paper_ids
    return recommended_paper_ids

