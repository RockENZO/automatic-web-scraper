import streamlit as st
import time
from scrape import (
    scrape_website,
    split_dom_content,
    extract_body_content,
    clean_body_content,
)
from parse import parse_with_ollama

# Configure Streamlit page
st.set_page_config(
    page_title="Automatic Web Scraper",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Automatic Web Scraper")
st.markdown("*Powered by Ollama gpt-oss:20b model*")

# Add sidebar with information
with st.sidebar:
    st.header("📋 How to use")
    st.markdown("""
    1. Enter a valid URL
    2. Click 'Scrape' to extract content
    3. Describe what you want to parse
    4. Click 'Parse Content' to get results
    """)
    
    st.header("⚙️ Settings")
    chunk_size = st.slider("Chunk size for processing", 2000, 10000, 6000, 500)

url = st.text_input("🌐 Enter the URL of the website you want to scrape", placeholder="https://example.com")

if st.button("🤳 Scrape Website", type="primary"):
    if not url:
        st.error("Please enter a valid URL")
    elif not url.startswith(('http://', 'https://')):
        st.error("Please enter a valid URL starting with http:// or https://")
    else:
        with st.spinner(f"Scraping {url}..."):
            try:
                start_time = time.time()
                result = scrape_website(url)
                body_content = extract_body_content(result)
                cleaned_content = clean_body_content(body_content)
                
                # Store in session state
                st.session_state.dom_content = cleaned_content
                st.session_state.original_url = url
                
                scrape_time = time.time() - start_time
                st.success(f"✅ Successfully scraped {url} in {scrape_time:.2f} seconds")
                
                # Show content stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Content Length", f"{len(cleaned_content):,} chars")
                with col2:
                    st.metric("Word Count", f"{len(cleaned_content.split()):,}")
                with col3:
                    estimated_chunks = len(cleaned_content) // chunk_size + 1
                    st.metric("Estimated Chunks", estimated_chunks)
                
            except Exception as e:
                st.error(f"❌ Error scraping website: {str(e)}")

# Show DOM content if available
if "dom_content" in st.session_state:
    with st.expander("👁️ View DOM Content", expanded=False):
        st.text_area(
            "Scraped Content", 
            st.session_state.dom_content, 
            height=300,
            help="This is the cleaned content extracted from the website"
        )

    # Parsing section
    st.divider()
    st.subheader("🔍 Parse Content")
    
    parse_description = st.text_area(
        "Describe what you want to extract from the content:",
        placeholder="e.g., Extract all email addresses, phone numbers, product prices, etc.",
        help="Be specific about what information you want to extract"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        parse_button = st.button("🚀 Parse Content", type="primary")
    with col2:
        if "original_url" in st.session_state:
            st.info(f"Parsing content from: {st.session_state.original_url}")
    
    if parse_button:
        if not parse_description:
            st.error("Please describe what you want to parse")
        else:
            with st.spinner("🔍 Parsing content with gpt-oss:20b..."):
                try:
                    start_time = time.time()
                    dom_chunks = split_dom_content(st.session_state.dom_content, chunk_size)
                    
                    # Show progress
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    results = parse_with_ollama(dom_chunks, parse_description)
                    
                    parse_time = time.time() - start_time
                    progress_bar.progress(100)
                    status_text.success(f"✅ Parsing completed in {parse_time:.2f} seconds")
                    
                    st.subheader("📊 Parsing Results")
                    if results and results != "No relevant information found matching your description.":
                        st.markdown("### Extracted Information:")
                        st.write(results)
                        
                        # Add download button for results
                        st.download_button(
                            label="💾 Download Results",
                            data=results,
                            file_name=f"parsed_results_{int(time.time())}.txt",
                            mime="text/plain"
                        )
                    else:
                        st.warning("⚠️ No relevant information found matching your description. Try being more specific or check if the content contains what you're looking for.")
                        
                except Exception as e:
                    st.error(f"❌ Error during parsing: {str(e)}")
else:
    st.info("👆 Please scrape a website first to begin parsing content")
