from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}. "
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
    "5. **Format:** Present the extracted information in a clean, structured format."
)

# Model configuration with memory optimization
def create_optimized_model(model_name="gpt-oss:20b"):
    """Create an optimized model instance with memory constraints."""
    config = {
        "gpt-oss:20b": {
            "temperature": 0.1,
            "num_predict": 400,  # Reduced for memory efficiency
            "num_ctx": 2048,     # Reduced context window
            "repeat_penalty": 1.1,
            "top_k": 20,
            "top_p": 0.9,
        },
        "llama3.1:8b": {
            "temperature": 0.1,
            "num_predict": 600,
            "num_ctx": 3072,
        },
        "llama3.1": {
            "temperature": 0.1,
            "num_predict": 600,
            "num_ctx": 3072,
        }
    }
    
    model_config = config.get(model_name, config["gpt-oss:20b"])
    
    try:
        return OllamaLLM(model=model_name, **model_config)
    except Exception as e:
        logger.error(f"Failed to create model {model_name}: {e}")
        # Fallback to a smaller model
        if model_name != "llama3.1:8b":
            logger.info("Falling back to llama3.1:8b model")
            return OllamaLLM(model="llama3.1:8b", **config["llama3.1:8b"])
        raise

# Try to create the model with fallback
try:
    model = create_optimized_model("gpt-oss:20b")
    current_model_name = "gpt-oss:20b"
    logger.info("Successfully loaded gpt-oss:20b model")
except Exception as e:
    logger.warning(f"Failed to load gpt-oss:20b: {e}")
    try:
        model = create_optimized_model("llama3.1:8b") 
        current_model_name = "llama3.1:8b"
        logger.info("Fallback to llama3.1:8b model")
    except Exception as e2:
        logger.error(f"Failed to load fallback model: {e2}")
        raise Exception("No suitable models available")


def parse_with_ollama(dom_chunks, parse_description):
    """
    Parse DOM content chunks using Ollama LLM to extract specific information.
    
    Args:
        dom_chunks (list): List of DOM content chunks to parse
        parse_description (str): Description of what information to extract
        
    Returns:
        str: Parsed and extracted information from all chunks
    """
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    parsed_results = []
    total_chunks = len(dom_chunks)
    failed_chunks = 0
    
    logger.info(f"Starting to parse {total_chunks} chunks with gpt-oss:20b model")
    
    for i, chunk in enumerate(dom_chunks, start=1):
        try:
            logger.info(f"Processing chunk {i}/{total_chunks}")
            
            # Add retry mechanism for memory issues
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = chain.invoke({
                        "dom_content": chunk,
                        "parse_description": parse_description
                    })
                    
                    # Only add non-empty responses
                    if response and response.strip():
                        parsed_results.append(response.strip())
                    break  # Success, exit retry loop
                    
                except Exception as retry_error:
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed for chunk {i}, retrying in 2 seconds...")
                        import time
                        time.sleep(2)  # Wait before retry
                    else:
                        raise retry_error
                        
        except Exception as e:
            error_msg = str(e)
            failed_chunks += 1
            
            # Handle specific memory/resource errors
            if "status code: 500" in error_msg or "terminated" in error_msg or "killed" in error_msg:
                logger.error(f"Memory/resource error on chunk {i}: {error_msg}")
                logger.info("Waiting 5 seconds before continuing...")
                import time
                time.sleep(5)
                
                # If too many chunks fail due to memory, suggest switching models
                if failed_chunks > total_chunks * 0.3:  # More than 30% failed
                    logger.error("Too many memory failures detected. Consider using a smaller model.")
                    break
            else:
                logger.error(f"Error parsing chunk {i}: {error_msg}")
            continue
    
    # Report results
    success_rate = ((total_chunks - failed_chunks) / total_chunks) * 100 if total_chunks > 0 else 0
    logger.info(f"Parsing completed: {total_chunks - failed_chunks}/{total_chunks} chunks successful ({success_rate:.1f}%)")
    
    # Join results with proper formatting
    if parsed_results:
        result = "\n\n".join(parsed_results)
        if failed_chunks > 0:
            result += f"\n\n⚠️ Note: {failed_chunks} chunks failed due to memory limitations."
        return result
    else:
        if failed_chunks > 0:
            return f"❌ Parsing failed due to memory limitations. {failed_chunks}/{total_chunks} chunks failed. Consider using a smaller model or reducing chunk size."
        return "No relevant information found matching your description."