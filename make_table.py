import json

def generate_markdown_table(json_file_path, output_markdown_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        widgets = json.load(f)
    header = "| Category | Widget name (trame.widget.{name}) | Package name (pip install {name}) | Vue version | Number of components |\n"
    separator = "| --- | --- | --- | --- | --- |\n"
    markdown_table = header + separator
    current_category = None
    for widget in widgets:
        category = widget['Category']
        widget_name = widget['Widget name']
        summary = widget['Summary']
        package_name = widget['Package name']
        vue_version = widget['Vue version']
        num_components = widget['Number of components']
        status = widget['Status']
        if category != current_category:
            markdown_table += f"| **{category}** |\n"
            # markdown_table += "| --- | --- | --- | --- | --- |\n"
            current_category = category
        
        formatted_widget_name = widget_name
        if status and status != '⚠️':
            emojis = ''.join([char for char in status if not char.isalnum() and char != ' '])
            if emojis:
                formatted_widget_name = f"{emojis} {formatted_widget_name}"
        
        if summary:
            formatted_widget_name = f"[{formatted_widget_name}](# \"{summary}\")"
        
        row = f"| | {formatted_widget_name} | {package_name} | {vue_version} | {num_components} |\n"
        markdown_table += row
    
    with open(output_markdown_path, 'w', encoding='utf-8') as f:
        f.write(markdown_table)
    
    print(f"Markdown table generated successfully at: {output_markdown_path}")


if __name__ == "__main__":
    json_file = "trame_widgets.json"
    output_markdown = "trame_widgets.md"
    
    generate_markdown_table(json_file, output_markdown)