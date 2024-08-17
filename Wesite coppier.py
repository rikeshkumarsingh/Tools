import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote

def save_file(content, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(content)

def get_all_links(soup, base_url):
    tags = soup.find_all(['a', 'link', 'img', 'script', 'source', 'video', 'iframe', 'style'])
    links = []
    for tag in tags:
        if tag.name == 'a' and 'href' in tag.attrs:
            link = tag.attrs['href']
        elif tag.name == 'link' and 'href' in tag.attrs:
            link = tag.attrs['href']
        elif tag.name in ['img', 'script', 'source', 'video', 'iframe'] and 'src' in tag.attrs:
            link = tag.attrs['src']
        elif tag.name in ['style']:
            css_urls = extract_urls_from_css(tag.string, base_url)
            links.extend(css_urls)
        elif tag.name == 'source' and 'srcset' in tag.attrs:
            link = tag.attrs['srcset']
        else:
            continue
        full_url = urljoin(base_url, link)
        links.append(full_url)
    return links

def extract_urls_from_css(css_text, base_url):
    urls = []
    if css_text:
        for part in css_text.split('url(')[1:]:
            url = part.split(')')[0].strip('"\' ')
            full_url = urljoin(base_url, url)
            urls.append(full_url)
    return urls

def update_links(soup, base_url, output_dir):
    tags = soup.find_all(['a', 'link', 'img', 'script', 'source', 'video', 'iframe', 'style'])
    for tag in tags:
        if tag.name == 'a' and 'href' in tag.attrs:
            attr = 'href'
        elif tag.name in ['link', 'img', 'script', 'source', 'video', 'iframe'] and 'src' in tag.attrs:
            attr = 'src'
        elif tag.name == 'style':
            tag.string = update_urls_in_css(tag.string, base_url, output_dir)
            continue
        else:
            continue
        link = tag.attrs[attr]
        full_url = urljoin(base_url, link)
        parsed_url = urlparse(full_url)
        local_path = os.path.join(output_dir, parsed_url.netloc, parsed_url.path.lstrip('/'))
        relative_path = os.path.relpath(local_path, start=os.path.join(output_dir, parsed_url.netloc))
        tag.attrs[attr] = relative_path

def update_urls_in_css(css_text, base_url, output_dir):
    if not css_text:
        return ''
    updated_css = ''
    parts = css_text.split('url(')
    updated_css += parts[0]
    for part in parts[1:]:
        url = part.split(')')[0].strip('"\' ')
        full_url = urljoin(base_url, url)
        parsed_url = urlparse(full_url)
        local_path = os.path.join(output_dir, parsed_url.netloc, parsed_url.path.lstrip('/'))
        relative_path = os.path.relpath(local_path, start=os.path.join(output_dir, parsed_url.netloc))
        updated_css += f'url({relative_path})'
        updated_css += part[len(url)+1:]
    return updated_css

def ensure_path_has_filename(path, default_filename):
    if not os.path.basename(path):
        path = os.path.join(path, default_filename)
    return path

def scrape_resource(url, output_dir):
    resource_url = urlparse(url)
    resource_path = os.path.join(output_dir, resource_url.netloc, unquote(resource_url.path.lstrip('/')))
    resource_path = ensure_path_has_filename(resource_path, 'index.html')

    if os.path.exists(resource_path):
        return

    try:
        resource_response = requests.get(url, allow_redirects=True, timeout=10)
        resource_response.raise_for_status()
        save_file(resource_response.content, resource_path)

        # If the resource is CSS, also parse and download any URLs within it
        if resource_path.endswith('.css'):
            css_content = resource_response.text
            css_urls = extract_urls_from_css(css_content, url)
            for css_url in css_urls:
                scrape_resource(css_url, output_dir)
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")

def scrape_website(url, output_dir):
    response = requests.get(url, allow_redirects=True, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    parsed_url = urlparse(url)
    base_path = os.path.join(output_dir, parsed_url.netloc)

    # Download and save all linked resources
    for link in get_all_links(soup, url):
        scrape_resource(link, output_dir)

    # Update the HTML to point to local resources
    update_links(soup, url, output_dir)

    # Save the main HTML file
    main_html_path = os.path.join(base_path, 'index.html')
    save_file(soup.prettify('utf-8'), main_html_path)

if __name__ == "__main__":
    website_url = "https://www.instagram.com/_rikesh_singh/"  # Replace with the target website URL
    output_directory = "../copied_website"  # Replace with the desired output directory
    scrape_website(website_url, output_directory)
    print("Website copy completed.")


    #import this library first
    # "pip install requests beautifulsoup4"

