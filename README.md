# Unofficial SchoolMouv
Get schoolmouv's premium pdfs and videos with **python**, no account required🔥

⚠️ This tool isn't affiliated to SchoolMouv in any way, make sure you've read their privacy policy before use⚠️

## Prerequisites

Modules : `BeautifulSoup` and `requests`

Python version : 3.6 and above

Run:
`pip install bs4 requests` or `pip install -r requirements.txt`

## Usage

```python
import schoolmouv

# Videos
my_video = schoolmouv.video('https://www.schoolmouv.fr/cours/la-liberte-politique/cours-video')
my_video.run()
results = my_video.result # result found (list) (direct urls to mp4s)
my_video.download(results[0],'/path/to/folder',save_as='myvideo.mp4') # Default filename here is 'La liberte politique.mp4' (in this case)
my_video.see(results[0]) # Open in default browser

# PDFs
my_pdf = schoolmouv.pdf('https://www.schoolmouv.fr/cours/echantillonnage2/fiche-de-revision')
my_pdf.run()
result = my_pdf.result # result found (str) (direct url to pdf)
my_pdf.download(result,'/path/to/folder',save_as='mypdf.pdf') # Default filename is 'Echantillonage 2.pdf' (in this case)
my_pdf.see(result)
```
