import sys
from sentence_transformers import SentenceTransformer

def main():
    # Read input from stdin if available, else from command-line argument
    if not sys.stdin.isatty():
        input_text = sys.stdin.read().strip()
    elif len(sys.argv) >= 2:
        input_text = sys.argv[1]
    else:
        print("No text provided")
        sys.exit(1)

    # If the input contains the separator, assume batch processing.
    if "<SEP>" in input_text:
        texts = input_text.split("<SEP>")
    else:
        texts = [input_text]

    model = SentenceTransformer('all-MiniLM-L6-v2')  # Adjust model as needed
    embeddings = model.encode(texts)  # returns an array with shape (batch, dimension)
    
    # Output each embedding on a new line, space-separated.
    for emb in embeddings:
        print(" ".join(str(f) for f in emb))

if __name__ == "__main__":
    main()

