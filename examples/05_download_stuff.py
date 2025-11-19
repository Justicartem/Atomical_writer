import requests
from atomic_writer import SimpleWriter


url = "https://fsn1-speed.hetzner.com/100MB.bin"
with requests.get(url, stream=True) as r:
	r.raise_for_status()
	with SimpleWriter("examples_out/1MB.bin", mode="wb") as f:
		for chunk in r.iter_content(1024*64):
			if chunk:
				f.write(chunk)