import json
import os

def parse_cookies(cookie_str):
    cookies = {}
    parts = cookie_str.split(';')
    for part in parts:
        part = part.strip()
        if not part or '=' not in part:
            continue
        key, val = part.split('=', 1)
        cookies[key.strip()] = val.strip()
    return cookies

def main():
    env_path = os.path.join(os.getcwd(), '.env')
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    linkedin_line = next((l for l in lines if l.startswith('LINKEDIN_COOKIES=')), None)
    indeed_line = next((l for l in lines if l.startswith('INDEED_COOKIES=')), None)
    
    if linkedin_line:
        linkedin_raw = linkedin_line.partition('=')[2].strip().strip('"')
        linkedin_cookies = parse_cookies(linkedin_raw)
        with open('linkedin_cookies.json', 'w') as f:
            json.dump(linkedin_cookies, f, indent=2)
    
    if indeed_line:
        indeed_raw = indeed_line.partition('=')[2].strip().strip('"')
        indeed_cookies = parse_cookies(indeed_raw)
        with open('indeed_cookies.json', 'w') as f:
            json.dump(indeed_cookies, f, indent=2)

if __name__ == '__main__':
    main()
