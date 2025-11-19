from flask import Flask, request
import tempfile, os
from atomic_writer import write_from_file


app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
	f = request.files['file']
	tmp = tempfile.NamedTemporaryFile(delete=False)
	try:
		f.save(tmp.name)
		tmp.close()
		write_from_file(os.path.join('uploads', f.filename), tmp.name)
	finally:
		try:
			os.unlink(tmp.name)
		except Exception:
			pass
	return 'ok'


if __name__ == '__main__':
	app.run(port=5000)