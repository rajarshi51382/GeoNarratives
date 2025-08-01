
import json
import pandas as pd
import nltk
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline

# Download necessary NLTK data
nltk.download('punkt')

def load_data(templates_path, locations_path):
    """Loads the headline templates and locations from JSON files."""
    with open(templates_path, 'r') as f:
        templates = json.load(f)['templates']
    with open(locations_path, 'r') as f:
        locations = json.load(f)
    return templates, locations

def generate_headlines(templates, locations):
    """Generates all headline variations."""
    headlines = []
    for template in templates:
        for location in locations:
            headlines.append({
                'template_id': template['id'],
                'template_category': template['category'],
                'template_text': template['text'],
                'location_name': location['name'],
                'location_country': location['country'],
                'location_region': location['region'],
                'location_population': location['population'],
                'location_development_level': location['development_level'],
                'headline': template['text'].format(location=location['name'])
            })
    return pd.DataFrame(headlines)

def analyze_sentiment(headlines_df):
    """Performs sentiment analysis on the headlines using VADER, DistilBERT, and RoBERTa."""
    # VADER
    analyzer = SentimentIntensityAnalyzer()
    headlines_df['vader_sentiment'] = headlines_df['headline'].apply(lambda x: analyzer.polarity_scores(x)['compound'])

    # DistilBERT
    distilbert_pipeline = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')
    distilbert_results = distilbert_pipeline(headlines_df['headline'].tolist())
    headlines_df['distilbert_sentiment'] = [result['label'] for result in distilbert_results]
    headlines_df['distilbert_score'] = [result['score'] for result in distilbert_results]

    # RoBERTa
    roberta_pipeline = pipeline('sentiment-analysis', model='cardiffnlp/twitter-roberta-base-sentiment')
    roberta_results = roberta_pipeline(headlines_df['headline'].tolist())
    headlines_df['roberta_sentiment'] = [result['label'] for result in roberta_results]
    headlines_df['roberta_score'] = [result['score'] for result in roberta_results]

    return headlines_df

def main():
    """Main function to run the experiments."""
    templates, locations = load_data('headline_templates.json', 'locations.json')
    headlines_df = generate_headlines(templates, locations)
    results_df = analyze_sentiment(headlines_df)
    results_df.to_csv('sentiment_analysis_results.csv', index=False)
    print("Successfully ran sentiment analysis and saved results to sentiment_analysis_results.csv")

if __name__ == "__main__":
    main()
