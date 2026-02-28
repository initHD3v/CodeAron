import re

def robust_parse_shell(text: str):
    # Mencari tag <shell>...</shell> atau <shell>... hingga akhir/tag lain
    pattern = r'<shell>(.*?)(?=</shell>|<file|<shell|$)'
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
    
    results = []
    for match in matches:
        cmd = match.strip()
        cmd = re.sub(r'</shell>', '', cmd, flags=re.IGNORECASE).strip()
        if cmd:
            results.append(cmd)
    return results

def robust_parse_file(text: str):
    # Mencari tag <file path="...">...</file> atau hingga akhir/tag lain
    # Menggunakan regex yang lebih aman untuk tanda kutip
    pattern = r'<file\s+path=["\'](.*?)["\']>(.*?)(?=</file>|<file|<shell|$)'
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
    
    results = []
    for path, content in matches:
        path = path.strip()
        content = content.strip()
        content = re.sub(r'</file>', '', content, flags=re.IGNORECASE).strip()
        if path and content:
            results.append((path, content))
    return results

# Test cases
test_outputs = [
    "Jalankan ini: <shell>ls -la</shell> oke?",
    "Tanpa tag tutup: <shell>npm install",
    "Dua tag: <shell>git status</shell> lalu <shell>git add .",
    "Tag file dan shell: <file path=\"test.txt\">halo</file> kemudian <shell>cat test.txt",
    "Hallucinated tag inside: <shell>echo 'done' </shell> sisa teks",
    "Nested-like (error case): <shell>ls <file path='err'>content</file></shell>"
]

print("--- Testing Shell Parsing ---")
for out in test_outputs:
    cmds = robust_parse_shell(out)
    print(f"Input: {out[:40]}...")
    print(f"Extracted: {cmds}")

print("\n--- Testing File Parsing ---")
for out in test_outputs:
    files = robust_parse_file(out)
    print(f"Input: {out[:40]}...")
    print(f"Extracted: {files}")
