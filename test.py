from html_transfer_md import html_converter


if __name__ == '__main__':
    html = "<table><tr><th>Header</th></tr><tr><td>Data</td></tr></table>"
    text_md = html_converter(html, verbose=True)
    print(text_md)