from transformers import pipeline

# Load the pre-trained NLP model for text2text generation (T5 model for SQL generation)
nlp_model = pipeline('text2text-generation', model="t5-small")

def generate_sql(natural_language_query, schema_metadata):
    """
    Convert a natural language query into SQL using a pre-trained NLP model.
    
    Args:
        natural_language_query (str): The query provided by the user.
        schema_metadata (dict): Database schema details for context.
        
    Returns:
        str: Generated SQL query.
    """
    try:
        # Prepare the schema context in the format the model can understand
        schema_context = "\n".join(
            f"Table: {table}, Columns: {', '.join(details['columns'])}"
            for table, details in schema_metadata.items()
        )
        
        # Construct the prompt with schema context and the natural language query
        prompt = f"Schema:\n{schema_context}\n\nQuery: {natural_language_query}\n\nSQL:"
        
        # Generate the SQL using the NLP model
        result = nlp_model(prompt, max_length=150, num_return_sequences=1)
        return result[0]['generated_text'].strip()
    except Exception as e:
        print(f"Error in SQL generation: {e}")
        return None
