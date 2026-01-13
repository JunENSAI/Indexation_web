import os
from src.utils import load_jsonl, save_json, extract_product_info
from src.indexer import positional_index, index_features, index_reviews

def main():
    input_file = "../Index/Input/products.jsonl"
    output_dir = "Output"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Lecture de {input_file}...")
    documents = load_jsonl(input_file)

    if documents:
        info = extract_product_info(documents[1]['url'])
        print(f"Test Extraction URL: {info}")

    title_index = positional_index(documents, "title")
    save_json(title_index, os.path.join(output_dir, "title_index.json"))

    description_index = positional_index(documents, "description")
    save_json(description_index, os.path.join(output_dir, "description_index.json"))

    brand_index = index_features(documents, "brand")
    save_json(brand_index, os.path.join(output_dir, "brand_index.json"))

    origin_index = index_features(documents, "made in")
    save_json(origin_index, os.path.join(output_dir, "origin_index.json"))

    reviews_index = index_reviews(documents)
    save_json(reviews_index, os.path.join(output_dir, "reviews_index.json"))

if __name__ == "__main__":
    main()