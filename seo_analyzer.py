import re
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import logging
from ai_integration import analyze_content_semantics # Importation ajoutée

logger = logging.getLogger(__name__)

# Définir des exceptions personnalisées pour une meilleure gestion des erreurs
class SeoAnalysisError(Exception):
    """Classe de base pour les erreurs d'analyse SEO."""
    pass

class ContentFetchError(SeoAnalysisError):
    """Erreur lors de la récupération du contenu de l'URL."""
    pass

class HtmlParsingError(SeoAnalysisError):
    """Erreur lors du parsing du HTML."""
    pass

def analyze_url(url, analysis_type='meta'):
    """
    Analyze a URL for SEO performance.
    """
    logger.info(f"Starting analysis for {url}, type: {analysis_type}")
    try:
        # Get URL content with a common User-Agent and error handling
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1', 
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        try:
            response = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
            response.raise_for_status() 
            logger.debug(f"Successfully fetched content for {url}, status: {response.status_code}")
        except requests.exceptions.Timeout:
            logger.error(f"Timeout while trying to fetch {url}")
            raise ContentFetchError(f"Timeout: The request to {url} timed out after 20 seconds.")
        except requests.exceptions.TooManyRedirects:
            logger.error(f"Too many redirects for {url}")
            raise ContentFetchError(f"RedirectError: Too many redirects for {url}.")
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred for {url}: {http_err}")
            raise ContentFetchError(f"HTTPError: Failed to fetch content from {url}. Status: {response.status_code}. Error: {http_err}")
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Request failed for {url}: {str(req_err)}")
            raise ContentFetchError(f"RequestError: Failed to fetch content from {url}. Error: {str(req_err)}")

        # Parse HTML
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            logger.debug(f"Successfully parsed HTML for {url}")
        except Exception as parse_err: # Attraper des erreurs plus larges de BeautifulSoup si nécessaire
            logger.error(f"Failed to parse HTML for {url}: {str(parse_err)}")
            raise HtmlParsingError(f"ParsingError: Could not parse HTML content from {url}. Error: {str(parse_err)}")
        
        results = {
            'url': url, 'analysis_type': analysis_type,
            'scores': {'meta': 0, 'content': 0, 'technical': 0, 'overall': 0}, # Initialiser tous les scores
            'details': {'meta': {}, 'content': {}, 'technical': {}} # Initialiser toutes les sections de détails
        }
        
        analyze_meta_tags(soup, results)
        
        if analysis_type in ['partial', 'complete', 'deep']:
            analyze_content(soup, results)
            
        if analysis_type in ['complete', 'deep']:
            analyze_technical(soup, url, results)
            
        # Calculate overall score
        scores_to_average = [results['scores']['meta']]
        if analysis_type in ['partial', 'complete', 'deep']:
            scores_to_average.append(results['scores']['content'])
        if analysis_type in ['complete', 'deep']:
            scores_to_average.append(results['scores']['technical'])
        
        # Semantic analysis for 'deep' type
        if analysis_type == 'deep':
            logger.info(f"Extracting text for semantic analysis from {url}")
            paragraphs = soup.find_all('p')
            extracted_text_for_semantic_analysis = " ".join(p.get_text(separator=' ', strip=True) for p in paragraphs if p.get_text(strip=True))
            
            if extracted_text_for_semantic_analysis.strip():
                try:
                    logger.info(f"Performing semantic analysis for {url} (type: deep)")
                    semantic_results = analyze_content_semantics(extracted_text_for_semantic_analysis)
                    logger.debug(f"Semantic analysis results for {url}: {semantic_results}")

                    if 'semantic' not in results['details']:
                        results['details']['semantic'] = {}
                    
                    results['details']['semantic']['relevance'] = {
                        'status': 'info', 
                        'score': semantic_results.get('relevance_score', 0), 
                        'description': f"AI Semantic Relevance Score: {semantic_results.get('relevance_score', 'N/A')}/100.",
                        'recommendation': semantic_results.get('depth_assessment', 'No specific depth assessment provided.')
                    }
                    # Potentially add other semantic details if returned by analyze_content_semantics
                except Exception as sem_err:
                    logger.error(f"Error during semantic analysis for {url}: {str(sem_err)}", exc_info=True)
                    if 'semantic' not in results['details']:
                        results['details']['semantic'] = {}
                    results['details']['semantic']['error'] = {
                        'status': 'error', 
                        'score': 0, 
                        'description': "Semantic analysis could not be performed.",
                        'recommendation': str(sem_err)
                    }
            else:
                logger.warning(f"No significant text extracted from <p> tags for semantic analysis of {url}")
                if 'semantic' not in results['details']:
                    results['details']['semantic'] = {}
                results['details']['semantic']['no_text'] = {
                    'status': 'warning',
                    'score': 0, # Or a neutral score
                    'description': "No significant text content found in <p> tags for semantic analysis.",
                    'recommendation': "Ensure the page has substantial textual content in paragraph tags for semantic analysis."
                }

        # Calculate overall score
        scores_to_average = [results['scores']['meta']]
        if analysis_type in ['partial', 'complete', 'deep']:
            scores_to_average.append(results['scores']['content'])
        if analysis_type in ['complete', 'deep']:
            scores_to_average.append(results['scores']['technical'])
        
        if scores_to_average:
            results['scores']['overall'] = sum(scores_to_average) // len(scores_to_average)
        else:
            results['scores']['overall'] = 0 # Should always have at least meta score

        logger.info(f"Analysis for {url} completed. Overall score: {results['scores']['overall']}")
        return results
        
    except ContentFetchError as e: 
        logger.error(f"ContentFetchError during analysis of {url}: {str(e)}")
        raise # Remonter l'erreur pour que la route principale puisse l'afficher
    except HtmlParsingError as e:
        logger.error(f"HtmlParsingError during analysis of {url}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error analyzing URL {url}: {str(e)}", exc_info=True)
        raise SeoAnalysisError(f"An unexpected error occurred during analysis of {url}: {str(e)}")

# Les fonctions analyze_meta_tags, analyze_content, analyze_technical restent inchangées pour l'instant
# ... (coller ici le reste des fonctions analyze_meta_tags, analyze_content, analyze_technical)
# ... (Assurez-vous que ces fonctions utilisent logger.debug ou logger.info pour les messages internes si besoin)

def analyze_meta_tags(soup, results):
    """Analyze meta tags for SEO"""
    meta_score = 0
    meta_items = 0
    
    # Title analysis
    title_tag = soup.title
    title_text = title_tag.string if title_tag else None
    if title_text:
        title_length = len(title_text.strip())
        if 10 <= title_length <= 60: status, score, recommendation = 'good', 100, "Optimal title length."
        elif title_length < 10: status, score, recommendation = 'error', 30, "Title too short. Make it more descriptive."
        else: status, score, recommendation = 'warning', 70, "Title too long. Keep under 60 characters."
        results['details']['meta']['title'] = {'status': status, 'score': score, 'description': f"Title: {title_text.strip()} ({title_length} chars)", 'recommendation': recommendation, 'value': title_text.strip()}
        meta_score += score; meta_items += 1
    else:
        results['details']['meta']['title'] = {'status': 'error', 'score': 0, 'description': "Missing page title.", 'recommendation': "Add a descriptive title tag."}
        meta_items += 1
    
    # Meta description
    meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
    meta_desc_content = meta_desc_tag['content'].strip() if meta_desc_tag and meta_desc_tag.get('content') else None
    if meta_desc_content:
        desc_length = len(meta_desc_content)
        if 50 <= desc_length <= 160: status, score, recommendation = 'good', 100, "Optimal meta description length."
        elif desc_length < 50: status, score, recommendation = 'warning', 50, "Meta description too short (aim 50-160 chars)."
        else: status, score, recommendation = 'warning', 70, "Meta description too long (under 160 chars)."
        results['details']['meta']['description'] = {'status': status, 'score': score, 'description': f"Length: {desc_length} chars", 'recommendation': recommendation, 'value': meta_desc_content[:200] + "..."}
        meta_score += score; meta_items += 1
    else:
        results['details']['meta']['description'] = {'status': 'error', 'score': 0, 'description': "Missing meta description.", 'recommendation': "Add a meta description."}
        meta_items += 1
        
    # Meta keywords (moins important mais vérifié)
    meta_kw_tag = soup.find('meta', attrs={'name': 'keywords'})
    meta_kw_content = meta_kw_tag['content'].strip() if meta_kw_tag and meta_kw_tag.get('content') else None
    if meta_kw_content:
        kw_count = len(meta_kw_content.split(','))
        status, score, recommendation = 'info', 70, "Meta keywords are less impactful now but can be used."
        results['details']['meta']['keywords'] = {'status': status, 'score': score, 'description': f"{kw_count} keywords found.", 'recommendation': recommendation, 'value': meta_kw_content[:200] + "..."}
    else:
        status, score, recommendation = 'info', 50, "No meta keywords tag found."
        results['details']['meta']['keywords'] = {'status': status, 'score': score, 'description': "Missing meta keywords.", 'recommendation': recommendation}
    meta_score += score; meta_items += 1

    # OG tags
    og_title = soup.find('meta', property='og:title')
    og_desc = soup.find('meta', property='og:description')
    og_image = soup.find('meta', property='og:image')
    og_tags_found = sum(1 for tag in [og_title, og_desc, og_image] if tag and tag.get('content'))
    if og_tags_found == 3: status, score, recommendation = 'good', 100, "All key Open Graph tags present."
    elif og_tags_found > 0: status, score, recommendation = 'warning', 60, f"{3-og_tags_found} Open Graph tags missing."
    else: status, score, recommendation = 'error', 20, "Open Graph tags missing."
    results['details']['meta']['og_tags'] = {'status': status, 'score': score, 'description': f"{og_tags_found}/3 OG tags found.", 'recommendation': recommendation}
    meta_score += score; meta_items += 1
    
    results['scores']['meta'] = meta_score // meta_items if meta_items > 0 else 0

def analyze_content(soup, results):
    content_score = 0; content_items = 0
    
    h1_tags = soup.find_all('h1')
    h1_count = len(h1_tags)
    if h1_count == 1: status, score, recommendation = 'good', 100, "One H1 tag found."
    elif h1_count == 0: status, score, recommendation = 'error', 0, "Missing H1 tag."
    else: status, score, recommendation = 'warning', 50, f"{h1_count} H1 tags found. Aim for one."
    results['details']['content']['h1_tag'] = {'status': status, 'score': score, 'description': f"{h1_count} H1 tags.", 'recommendation': recommendation}
    content_score += score; content_items += 1

    headings = {f'h{i}': len(soup.find_all(f'h{i}')) for i in range(1, 7)}
    if headings['h1'] == 1 and headings['h2'] >= 1: status, score, recommendation = 'good', 100, "Good heading structure."
    else: status, score, recommendation = 'warning', 60, "Suboptimal heading structure. Ensure H1 is followed by H2s etc."
    desc_str = ", ".join([f"{count} H{i}" for i, count in headings.items()])
    results['details']['content']['heading_structure'] = {'status': status, 'score': score, 'description': desc_str, 'recommendation': recommendation}
    content_score += score; content_items += 1

    text_content = ' '.join(p.get_text(separator=' ', strip=True) for p in soup.find_all('p'))
    word_count = len(text_content.split())
    if word_count >= 300: status, score, recommendation = 'good', 100, "Good content length."
    elif word_count >= 100: status, score, recommendation = 'warning', 70, "Content a bit short (aim 300+ words)."
    else: status, score, recommendation = 'error', 30, "Content too short."
    results['details']['content']['content_length'] = {'status': status, 'score': score, 'description': f"{word_count} words.", 'recommendation': recommendation}
    content_score += score; content_items += 1

    images = soup.find_all('img')
    img_alts = sum(1 for img in images if img.get('alt', '').strip())
    if not images: status, score, recommendation = 'info', 70, "No images found. Consider adding relevant images."
    elif img_alts == len(images): status, score, recommendation = 'good', 100, "All images have alt text."
    else: status, score, recommendation = 'warning', 60, f"{len(images) - img_alts} images missing alt text."
    results['details']['content']['image_alt'] = {'status': status, 'score': score, 'description': f"{img_alts}/{len(images)} images with alt text.", 'recommendation': recommendation}
    content_score += score; content_items += 1
    
    results['scores']['content'] = content_score // content_items if content_items > 0 else 0

def analyze_technical(soup, url, results):
    technical_score = 0; technical_items = 0
    
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    if viewport and 'width=device-width' in viewport.get('content', ''): status, score, recommendation = 'good', 100, "Viewport meta tag present."
    else: status, score, recommendation = 'error', 20, "Missing viewport meta tag."
    results['details']['technical']['viewport'] = {'status': status, 'score': score, 'description': "Viewport " + ("present" if viewport else "missing"), 'recommendation': recommendation}
    technical_score += score; technical_items += 1

    if url.startswith('https://'): status, score, recommendation = 'good', 100, "Site uses HTTPS."
    else: status, score, recommendation = 'error', 0, "Site does not use HTTPS."
    results['details']['technical']['https'] = {'status': status, 'score': score, 'description': "HTTPS " + ("enabled" if url.startswith('https') else "disabled"), 'recommendation': recommendation}
    technical_score += score; technical_items += 1

    canonical = soup.find('link', rel='canonical')
    if canonical and canonical.get('href'): status, score, recommendation = 'good', 100, "Canonical URL tag present."
    else: status, score, recommendation = 'warning', 60, "No canonical URL tag. Consider adding one."
    results['details']['technical']['canonical'] = {'status': status, 'score': score, 'description': "Canonical URL " + (canonical.get('href') if canonical else "missing"), 'recommendation': recommendation}
    technical_score += score; technical_items += 1
    
    # Placeholders pour des analyses plus poussées
    results['details']['technical']['robots_txt'] = {'status': 'info', 'score': 50, 'description': "robots.txt check: Not implemented.", 'recommendation': "Ensure robots.txt is configured."}
    technical_score += 50; technical_items += 1
    results['details']['technical']['sitemap'] = {'status': 'info', 'score': 50, 'description': "Sitemap check: Not implemented.", 'recommendation': "Ensure a sitemap exists."}
    technical_score += 50; technical_items += 1
    
    results['scores']['technical'] = technical_score // technical_items if technical_items > 0 else 0
