import re
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

def analyze_url(url, analysis_type='meta'):
    """
    Analyze a URL for SEO performance
    
    Parameters:
    - url: URL to analyze
    - analysis_type: Type of analysis (meta, partial, complete, deep)
    
    Returns:
    - Dictionary with analysis results
    """
    try:
        # Get URL content
        headers = {
            'User-Agent': 'Opt-AI SEO Analyzer/1.0',
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Prepare result structure
        results = {
            'url': url,
            'analysis_type': analysis_type,
            'scores': {
                'meta': 0,
                'overall': 0
            },
            'details': {
                'meta': {}
            }
        }
        
        # Analyze meta tags
        analyze_meta_tags(soup, results)
        
        # Additional analysis based on type
        if analysis_type in ['partial', 'complete', 'deep']:
            results['scores']['content'] = 0
            results['details']['content'] = {}
            analyze_content(soup, results)
            
        if analysis_type in ['complete', 'deep']:
            results['scores']['technical'] = 0
            results['details']['technical'] = {}
            analyze_technical(soup, url, results)
            
        # Calculate overall score
        if analysis_type == 'meta':
            results['scores']['overall'] = results['scores']['meta']
        elif analysis_type == 'partial':
            results['scores']['overall'] = (results['scores']['meta'] + results['scores']['content']) // 2
        else:
            results['scores']['overall'] = (results['scores']['meta'] + results['scores']['content'] + results['scores']['technical']) // 3
        
        return results
        
    except Exception as e:
        logger.error(f"Error analyzing URL {url}: {str(e)}")
        raise Exception(f"Failed to analyze URL: {str(e)}")

def analyze_meta_tags(soup, results):
    """Analyze meta tags for SEO"""
    meta_score = 0
    meta_items = 0
    
    # Title analysis
    title = soup.title.string if soup.title else None
    if title:
        title_length = len(title)
        if 10 <= title_length <= 60:
            status = 'good'
            score = 100
            recommendation = "Your title is the optimal length."
        elif title_length < 10:
            status = 'error'
            score = 30
            recommendation = "Your title is too short. Make it more descriptive."
        else:
            status = 'warning'
            score = 70
            recommendation = "Your title is too long. Keep it under 60 characters for better visibility in search results."
            
        results['details']['meta']['title'] = {
            'status': status,
            'score': score,
            'description': f"Title: {title} ({title_length} characters)",
            'recommendation': recommendation
        }
        meta_score += score
        meta_items += 1
    else:
        results['details']['meta']['title'] = {
            'status': 'error',
            'score': 0,
            'description': "Missing page title",
            'recommendation': "Add a descriptive title tag to your page. This is crucial for SEO."
        }
        meta_items += 1
    
    # Meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        desc_content = meta_desc['content']
        desc_length = len(desc_content)
        
        if 50 <= desc_length <= 160:
            status = 'good'
            score = 100
            recommendation = "Your meta description is the optimal length."
        elif desc_length < 50:
            status = 'warning'
            score = 50
            recommendation = "Your meta description is too short. Aim for 50-160 characters."
        else:
            status = 'warning'
            score = 70
            recommendation = "Your meta description is too long. Keep it under 160 characters."
            
        results['details']['meta']['description'] = {
            'status': status,
            'score': score,
            'description': f"Description: {desc_content[:100]}... ({desc_length} characters)",
            'recommendation': recommendation
        }
        meta_score += score
        meta_items += 1
    else:
        results['details']['meta']['description'] = {
            'status': 'error',
            'score': 0,
            'description': "Missing meta description",
            'recommendation': "Add a meta description tag to improve CTR from search results."
        }
        meta_items += 1
    
    # Meta keywords
    meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
    if meta_keywords and meta_keywords.get('content'):
        keywords = meta_keywords['content']
        keyword_count = len(keywords.split(','))
        
        if 3 <= keyword_count <= 10:
            status = 'good'
            score = 80
            recommendation = "Your keyword count is good, though search engines give less weight to the keywords meta tag now."
        elif keyword_count < 3:
            status = 'warning'
            score = 50
            recommendation = "Consider adding more keywords, although this tag has diminished SEO value."
        else:
            status = 'warning'
            score = 60
            recommendation = "Too many keywords may appear as keyword stuffing."
            
        results['details']['meta']['keywords'] = {
            'status': status,
            'score': score,
            'description': f"Keywords: {keywords[:100]}... ({keyword_count} keywords)",
            'recommendation': recommendation
        }
        meta_score += score
        meta_items += 1
    else:
        results['details']['meta']['keywords'] = {
            'status': 'warning',
            'score': 50,
            'description': "Missing meta keywords",
            'recommendation': "While not critical for SEO, meta keywords can still help with site organization."
        }
        meta_score += 50
        meta_items += 1
    
    # OG tags (Open Graph)
    og_title = soup.find('meta', attrs={'property': 'og:title'})
    og_desc = soup.find('meta', attrs={'property': 'og:description'})
    og_image = soup.find('meta', attrs={'property': 'og:image'})
    
    if og_title and og_desc and og_image:
        status = 'good'
        score = 100
        recommendation = "Your Open Graph tags are complete, good for social sharing."
    elif og_title or og_desc or og_image:
        status = 'warning'
        score = 60
        recommendation = "Some Open Graph tags are missing. Complete them for better social media sharing."
    else:
        status = 'error'
        score = 20
        recommendation = "Missing Open Graph tags. Add them to improve appearance when shared on social media."
        
    results['details']['meta']['og_tags'] = {
        'status': status,
        'score': score,
        'description': f"Open Graph tags: {1 if og_title else 0}/1 title, {1 if og_desc else 0}/1 description, {1 if og_image else 0}/1 image",
        'recommendation': recommendation
    }
    meta_score += score
    meta_items += 1
    
    # Calculate average meta score
    results['scores']['meta'] = meta_score // meta_items if meta_items > 0 else 0

def analyze_content(soup, results):
    """Analyze page content for SEO"""
    content_score = 0
    content_items = 0
    
    # Headings analysis
    h1_tags = soup.find_all('h1')
    h1_count = len(h1_tags)
    
    if h1_count == 1:
        status = 'good'
        score = 100
        recommendation = "Perfect! Your page has exactly one H1 tag."
    elif h1_count == 0:
        status = 'error'
        score = 0
        recommendation = "Your page is missing an H1 tag. Add one that includes your primary keyword."
    else:
        status = 'warning'
        score = 50
        recommendation = f"Your page has {h1_count} H1 tags. It's best to have exactly one H1 tag."
        
    results['details']['content']['h1_tag'] = {
        'status': status,
        'score': score,
        'description': f"H1 tags: {h1_count}",
        'recommendation': recommendation
    }
    content_score += score
    content_items += 1
    
    # Heading structure
    headings = {
        'h1': len(soup.find_all('h1')),
        'h2': len(soup.find_all('h2')),
        'h3': len(soup.find_all('h3')),
        'h4': len(soup.find_all('h4')),
        'h5': len(soup.find_all('h5')),
        'h6': len(soup.find_all('h6'))
    }
    
    if headings['h1'] == 1 and headings['h2'] >= 1:
        status = 'good'
        score = 100
        recommendation = "Your heading structure follows best practices."
    elif headings['h1'] == 1 and headings['h2'] == 0:
        status = 'warning'
        score = 70
        recommendation = "Your page has an H1 but no H2 tags. Consider adding H2 tags to structure your content."
    else:
        status = 'warning'
        score = 50
        recommendation = "Your heading structure is not optimal. Ensure you have one H1 followed by H2 and H3 tags."
        
    results['details']['content']['heading_structure'] = {
        'status': status,
        'score': score,
        'description': f"Headings: {headings['h1']} H1, {headings['h2']} H2, {headings['h3']} H3, {headings['h4']} H4, {headings['h5']} H5, {headings['h6']} H6",
        'recommendation': recommendation
    }
    content_score += score
    content_items += 1
    
    # Content length
    paragraphs = soup.find_all('p')
    text_content = ' '.join([p.get_text() for p in paragraphs])
    word_count = len(text_content.split())
    
    if word_count >= 300:
        status = 'good'
        score = 100
        recommendation = "Your content length is good for SEO."
    elif word_count >= 100:
        status = 'warning'
        score = 70
        recommendation = "Your content is a bit short. Aim for at least 300 words for better SEO performance."
    else:
        status = 'error'
        score = 30
        recommendation = "Your content is too short. Create more comprehensive content with at least 300 words."
        
    results['details']['content']['content_length'] = {
        'status': status,
        'score': score,
        'description': f"Content: {word_count} words",
        'recommendation': recommendation
    }
    content_score += score
    content_items += 1
    
    # Image alt text
    images = soup.find_all('img')
    images_with_alt = [img for img in images if img.get('alt')]
    img_count = len(images)
    img_with_alt_count = len(images_with_alt)
    
    if img_count == 0:
        status = 'warning'
        score = 70
        recommendation = "Your page has no images. Consider adding relevant images with alt text to improve engagement."
    elif img_with_alt_count == img_count:
        status = 'good'
        score = 100
        recommendation = "All images have alt text. Great job!"
    elif img_with_alt_count >= img_count * 0.8:
        status = 'warning'
        score = 80
        recommendation = "Most images have alt text, but some are missing. Add alt text to all images for better accessibility and SEO."
    else:
        status = 'error'
        score = 40
        recommendation = "Many images are missing alt text. Add descriptive alt text to all images."
        
    results['details']['content']['image_alt'] = {
        'status': status,
        'score': score,
        'description': f"Images: {img_with_alt_count}/{img_count} have alt text",
        'recommendation': recommendation
    }
    content_score += score
    content_items += 1
    
    # Internal links
    internal_links = [a for a in soup.find_all('a', href=True) if not (a['href'].startswith('http') or a['href'].startswith('//')) and not a['href'].startswith('#')]
    internal_link_count = len(internal_links)
    
    if internal_link_count >= 3:
        status = 'good'
        score = 100
        recommendation = "Good number of internal links for user navigation and SEO."
    elif internal_link_count > 0:
        status = 'warning'
        score = 70
        recommendation = "Your page has few internal links. Add more to improve site structure and SEO."
    else:
        status = 'error'
        score = 30
        recommendation = "No internal links found. Add links to other relevant pages on your site."
        
    results['details']['content']['internal_links'] = {
        'status': status,
        'score': score,
        'description': f"Internal links: {internal_link_count}",
        'recommendation': recommendation
    }
    content_score += score
    content_items += 1
    
    # Calculate average content score
    results['scores']['content'] = content_score // content_items if content_items > 0 else 0

def analyze_technical(soup, url, results):
    """Analyze technical aspects for SEO"""
    technical_score = 0
    technical_items = 0
    
    # Mobile responsiveness check (simple viewport check)
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    if viewport and 'width=device-width' in viewport.get('content', ''):
        status = 'good'
        score = 100
        recommendation = "Your page has a proper viewport meta tag for mobile responsiveness."
    else:
        status = 'error'
        score = 20
        recommendation = "No viewport meta tag found. Add one to ensure mobile-friendliness."
        
    results['details']['technical']['viewport'] = {
        'status': status,
        'score': score,
        'description': "Viewport meta tag: " + ("Present" if viewport else "Missing"),
        'recommendation': recommendation
    }
    technical_score += score
    technical_items += 1
    
    # HTTPS check
    if url.startswith('https'):
        status = 'good'
        score = 100
        recommendation = "Your site is secure with HTTPS."
    else:
        status = 'error'
        score = 0
        recommendation = "Your site is not using HTTPS. Switch to HTTPS for better security and SEO."
        
    results['details']['technical']['https'] = {
        'status': status,
        'score': score,
        'description': "HTTPS: " + ("Yes" if url.startswith('https') else "No"),
        'recommendation': recommendation
    }
    technical_score += score
    technical_items += 1
    
    # Canonical URL
    canonical = soup.find('link', attrs={'rel': 'canonical'})
    if canonical and canonical.get('href'):
        status = 'good'
        score = 100
        recommendation = "Your page has a canonical URL tag."
    else:
        status = 'warning'
        score = 60
        recommendation = "No canonical URL tag found. Consider adding one to prevent duplicate content issues."
        
    results['details']['technical']['canonical'] = {
        'status': status,
        'score': score,
        'description': "Canonical URL: " + (canonical.get('href', '') if canonical else "Missing"),
        'recommendation': recommendation
    }
    technical_score += score
    technical_items += 1
    
    # robots.txt and sitemap.xml checks could be added here for a more complete analysis
    # For the MVP, we'll use placeholders
    
    results['details']['technical']['robots_txt'] = {
        'status': 'info',
        'score': 50,
        'description': "robots.txt check: Not implemented in MVP",
        'recommendation': "Ensure you have a robots.txt file that doesn't block important content."
    }
    technical_score += 50
    technical_items += 1
    
    results['details']['technical']['sitemap'] = {
        'status': 'info',
        'score': 50,
        'description': "sitemap.xml check: Not implemented in MVP",
        'recommendation': "Ensure you have a sitemap.xml file submitted to search engines."
    }
    technical_score += 50
    technical_items += 1
    
    # Page loading speed (placeholder - would need frontend timing data for accurate measurement)
    results['details']['technical']['page_speed'] = {
        'status': 'info',
        'score': 50,
        'description': "Page speed check: Not implemented in MVP",
        'recommendation': "Ensure your page loads quickly for better user experience and SEO."
    }
    technical_score += 50
    technical_items += 1
    
    # Calculate average technical score
    results['scores']['technical'] = technical_score // technical_items if technical_items > 0 else 0
