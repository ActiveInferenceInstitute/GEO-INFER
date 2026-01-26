import os
import re

def reformat_markdown(content):
    # If file is mostly one huge line, naive check
    if len(content.splitlines()) < 10 and len(content) > 500:
        # It's likely minified.
        # Insert newlines before headers
        content = re.sub(r'(?<!\n)(#+ )', r'\n\n\1', content)
        # Insert newlines before list items if they are stuck
        content = re.sub(r'(?<!\n)(- \*\*)', r'\n\1', content)
        # Fix the "## Scope" that might be stuck
        content = re.sub(r'(?<!\n)(## Scope)', r'\n\n\1', content)
        # Clean up double newlines
        content = re.sub(r'\n{3,}', r'\n\n', content)
        return content, True
    return content, False

count = 0
for root, dirs, files in os.walk("."):
    for file in files:
        if file == "AGENTS.md":
            path = os.path.join(root, file)
            with open(path, 'r') as f:
                original = f.read()
            
            rewritten, changed = reformat_markdown(original)
            
            if changed:
                print(f"Refomatting {path}")
                with open(path, 'w') as f:
                    f.write(rewritten)
                count += 1

print(f"Reformatted {count} files.")
